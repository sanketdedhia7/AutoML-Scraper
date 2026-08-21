CORE_JS = r"""
            // Store articles data directly in JS
            let articles = {articles_json};
            let qualityStats = {quality_stats_json};
            
            // Client-side session stats (only updated by on-demand scraping)
            let sessionStats = {{
                yield: 0,
                discarded: 0,
                dedup: 0,
                totalScore: 0.0,
                countScore: 0
            }};
            
            function updateStatsDOM() {{
                document.getElementById('stat-yield').textContent = sessionStats.yield;
                document.getElementById('stat-discarded').textContent = sessionStats.discarded;
                document.getElementById('stat-dedup').textContent = sessionStats.dedup;
                const avg = sessionStats.countScore > 0 ? (sessionStats.totalScore / sessionStats.countScore).toFixed(1) : "0";
                document.getElementById('stat-avg').textContent = avg;
            }}
            let lastFocusedElement = null;
            let currentlyInspectedArticle = null;
            let currentSortKey = null;
            let currentSortDir = 1; // 1 = asc, -1 = desc
            const SPINNER_SVG = `<svg style="width:1.2em;height:1.2em;vertical-align:-0.2em;display:inline-block;animation:spin 1s linear infinite;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>`;
            
            let currentFilteredArticles = articles;
            const PAGE_SIZE = 30;
            const ALL_TABS = ['ops', 'data', 'quality', 'repairs'];
            
            function showToast(message, type = 'error', duration = 4500) {{
                let container = document.getElementById('toast-container');
                if (!container) {{
                    container = document.createElement('div');
                    container.id = 'toast-container';
                    container.setAttribute('role', 'status');
                    container.setAttribute('aria-live', 'polite');
                    document.body.appendChild(container);
                }}
                const toast = document.createElement('div');
                toast.className = `toast-msg ${{type}}`;
                const icon = type === 'error' ? '&#9888;' : type === 'success' ? '&#10004;' : '&#8505;';
                toast.innerHTML = `
                    <span class="toast-icon">${{icon}}</span>
                    <div class="toast-content">${{escapeHTML(message)}}</div>
                    <button class="toast-close" aria-label="Close notification">&times;</button>
                `;
                
                const closeAction = () => {{
                    toast.style.opacity = '0';
                    toast.style.transform = 'translateY(12px) scale(0.95)';
                    setTimeout(() => toast.remove(), 400);
                }};
                
                const closeBtn = toast.querySelector('.toast-close');
                closeBtn.addEventListener('click', closeAction);
                container.appendChild(toast);
                
                if (duration > 0) {{
                    setTimeout(() => {{
                        if (toast.parentNode) {{
                            closeAction();
                        }}
                    }}, duration);
                }}
            }}

            function renderSkeletons(containerId, count = 3) {{
                const container = document.getElementById(containerId);
                if (!container) return;
                let html = '';
                for (let i = 0; i < count; i++) {{
                    html += `
                        <div class="skeleton-card" aria-hidden="true">
                            <div class="skeleton-stamp"></div>
                            <div class="skeleton-info">
                                <div class="skeleton-title"></div>
                                <div class="skeleton-text"></div>
                            </div>
                            <div class="skeleton-meta"></div>
                        </div>
                    `;
                }}
                container.innerHTML = html;
            }}

            function resetSearchFilters() {{
                const searchBox = document.getElementById('search-box');
                const filterStatus = document.getElementById('filter-status');
                const filterSource = document.getElementById('filter-source');
                const filterScore = document.getElementById('filter-score');
                const sortArticles = document.getElementById('sort-articles');
                
                if (searchBox) searchBox.value = '';
                if (filterStatus) filterStatus.value = 'all';
                if (filterSource) filterSource.value = 'all';
                if (filterScore) filterScore.value = '0';
                if (sortArticles) sortArticles.value = 'date-desc';
                
                filterArticles();
            }}

            function populateSourceFilter() {{
                const select = document.getElementById('filter-source');
                if (!select || !articles) return;
                const current = select.value;
                const sources = Array.from(new Set(articles.map(a => a.source).filter(Boolean)));
                select.innerHTML = '<option value="all">All Sources</option>';
                sources.forEach(src => {{
                    const opt = document.createElement('option');
                    opt.value = src;
                    opt.textContent = src.toUpperCase();
                    if (src === current) opt.selected = true;
                    select.appendChild(opt);
                }});
            }}

            function switchTab(tab) {{
                // 1. Instantly trigger skeleton loaders for data fetching tabs
                if (tab === 'data') {{
                    renderSkeletons('article-cards-container', 4);
                }} else if (tab === 'repairs') {{
                    renderSkeletons('repair-history-container', 3);
                }}
                
                // 2. Batch layout modifications in requestAnimationFrame to prevent scroll jank
                requestAnimationFrame(() => {{
                    ALL_TABS.forEach(t => {{
                        document.getElementById(`nav-${{t}}`).classList.toggle('active', t === tab);
                        document.getElementById(`content-${{t}}`).classList.toggle('active', t === tab);
                    }});
                    
                    // 3. Defer loading actual data slightly to allow tab switch animation to render
                    setTimeout(() => {{
                        if (tab === 'data') {{
                            populateSourceFilter();
                            filterArticles();
                        }}
                        if (tab === 'quality') renderQualityChart();
                        if (tab === 'repairs') loadRepairHistory();
                    }}, 40);
                }});
            }}

            // ─── Ops filter + sort ─────────────────────────────────────────────
            
            function applyOpsFilter() {{
                const statusVal = document.getElementById('ops-status-filter').value;
                const searchVal = (document.getElementById('ops-search').value || '').toLowerCase();
                const records = document.querySelectorAll('#ops-list .ledger-record');
                records.forEach(r => {{
                    const status = r.dataset.status || '';
                    const collector = r.dataset.collector || '';
                    const statusOk = statusVal === 'all' || status === statusVal;
                    const searchOk = !searchVal || collector.includes(searchVal);
                    r.style.display = (statusOk && searchOk) ? '' : 'none';
                }});
            }}

            function sortOps(key) {{
                const list = document.getElementById('ops-list');
                const records = Array.from(list.querySelectorAll('.ledger-record'));
                if (currentSortKey === key) currentSortDir *= -1;
                else {{ currentSortKey = key; currentSortDir = 1; }}

                records.sort((a, b) => {{
                    let va, vb;
                    if (key === 'articles') {{
                        va = parseInt(a.dataset.articles || '0');
                        vb = parseInt(b.dataset.articles || '0');
                    }} else if (key === 'status') {{
                        const order = {{ healthy: 0, unhealthy: 1, error: 2 }};
                        va = order[a.dataset.status] ?? 3;
                        vb = order[b.dataset.status] ?? 3;
                    }}
                    return (va - vb) * currentSortDir;
                }});
                
                requestAnimationFrame(() => {{
                    records.forEach(r => list.appendChild(r));
                    // Update button active states
                    ['articles', 'status'].forEach(k => {{
                        document.getElementById(`sort-${{k}}-btn`).classList.toggle('active', k === key);
                    }});
                }});
            }}

"""
