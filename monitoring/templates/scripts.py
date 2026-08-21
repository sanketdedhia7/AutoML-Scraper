def get_dashboard_scripts(articles_json: str, quality_stats_json: str, threshold: int) -> str:
    return f"""
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

            // ─── Quality Chart ─────────────────────────────────────────────────

            function renderQualityChart() {{
                const container = document.getElementById('quality-chart-container');
                if (!qualityStats || qualityStats.length === 0) {{
                    container.innerHTML = '<p style="color:var(--dust-grey); font-style:italic; padding:20px 0;">No scored data available yet.</p>';
                    return;
                }}
                container.innerHTML = '';
                
                // Append the legend once before the loop
                const legend = document.createElement('div');
                legend.style.cssText = 'display:flex;gap:18px;margin-bottom:18px;margin-top:6px;';
                legend.innerHTML = `
                    <span style="font-family:JetBrains Mono,monospace;font-size:0.68rem;color:var(--verdigris-green);">&#9632; Accepted</span>
                    <span style="font-family:JetBrains Mono,monospace;font-size:0.68rem;color:var(--rust-terracotta);">&#9632; Rejected</span>
                    <span style="font-family:JetBrains Mono,monospace;font-size:0.68rem;color:var(--gold-seam);">&#9632; Avg score</span>
                `;
                container.appendChild(legend);

                qualityStats.forEach(s => {{
                    const total = s.count || 1;
                    const accPct = (s.accepted / total * 100).toFixed(1);
                    const rejPct = (s.rejected / total * 100).toFixed(1);
                    const row = document.createElement('div');
                    row.className = 'qchart-row';
                    row.innerHTML = `
                        <span class="qchart-label" title="${{escapeHTML(s.source)}}">${{escapeHTML(s.source)}}</span>
                        <div class="qchart-bars">
                            <div class="qchart-bar-accepted" style="width:${{accPct}}%" title="${{s.accepted}} accepted"></div>
                            <div class="qchart-bar-rejected" style="width:${{rejPct}}%" title="${{s.rejected}} rejected"></div>
                        </div>
                        <span class="qchart-avg">${{s.avg_score}}/100</span>
                    `;
                    container.appendChild(row);
                }});
            }}

            // ─── Repair History ────────────────────────────────────────────────

            async function loadRepairHistory() {{
                const container = document.getElementById('repair-history-container');
                try {{
                    const data = await (await fetch('/api/repairs')).json();
                    if (!data || data.length === 0) {{
                        container.innerHTML = `
                            <div class="empty-state-panel">
                                <span class="empty-state-icon">🩹</span>
                                <h3 class="empty-state-title">No Repairs Recorded</h3>
                                <p class="empty-state-text">No self-healing operations have been triggered or recorded in the registry yet. Active scrapers are currently operating within nominal parameters.</p>
                            </div>
                        `;
                        return;
                    }}
                    container.innerHTML = '';
                    data.forEach(entry => {{
                        const res = entry.result || {{}};
                        const status = res.status || entry.status || (entry.success ? 'success' : 'error');
                        let ts = entry.timestamp || '';
                        if (ts) {{
                            let normalized = ts;
                            if (!normalized.includes('T')) {{
                                normalized = normalized.replace(' ', 'T');
                            }}
                            if (!normalized.endsWith('Z') && !normalized.includes('+') && !normalized.includes('-') && normalized.split('-').length === 3) {{
                                normalized += 'Z';
                            }}
                            const d = new Date(normalized);
                            if (!isNaN(d.getTime())) {{
                                const pad = (n) => String(n).padStart(2, '0');
                                ts = `${{d.getFullYear()}}-${{pad(d.getMonth() + 1)}}-${{pad(d.getDate())}} ${{pad(d.getHours())}}:${{pad(d.getMinutes())}}:${{pad(d.getSeconds())}}`;
                            }}
                        }}
                        const card = document.createElement('div');
                        card.className = 'repair-card';
                        if (entry.collector_id) {{
                            card.id = `record-${{entry.collector_id}}`;
                        }}
                        const extMethod = entry.extraction_method || res.extraction_method || '';
                        const methodBadge = extMethod ? `<span class="trail-badge" style="background:#1a1919;border:1px solid var(--border-ledger);color:var(--parchment-white);font-family:JetBrains Mono,monospace;font-size:0.65rem;margin-left:8px;padding:2px 6px;text-transform:uppercase;">⚙ ${{escapeHTML(extMethod.replace(/_/g, ' '))}}</span>` : '';
                        card.innerHTML = `
                            <div class="repair-card-header" style="display:flex;align-items:center;">
                                <span class="repair-status-pill ${{escapeHTML(status)}}">${{escapeHTML(status.replace('_', ' '))}}</span>
                                ${{methodBadge}}
                                <span class="repair-card-meta" style="margin-left:auto;">${{escapeHTML(ts)}} &mdash; ${{escapeHTML(entry.collector_id || '')}}</span>
                            </div>
                            <div class="repair-card-issue">${{escapeHTML(entry.issue || 'No issue description')}}</div>
                            ${{res.diff_summary ? `<div class="repair-diff-block">${{escapeHTML(res.diff_summary)}}</div>` : ''}}
                            ${{entry.prompt ? `<div class="repair-prompt-snippet">Prompt: ${{escapeHTML((entry.prompt || '').slice(0, 120))}}${{(entry.prompt || '').length > 120 ? '\u2026' : ''}}</div>` : ''}}
                            ${{entry.is_pending ? `
                                <div style="margin-top: 15px;">
                                    <button class="heal-approve-btn" data-action="approve-heal" data-collector="${{escapeHTML(entry.collector_id || '')}}">
                                        <svg style='width:1.2em;height:1.2em;vertical-align:-0.2em;display:inline-block;' fill='none' stroke='currentColor' viewBox='0 0 24 24'><path stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M5 13l4 4L19 7'></path></svg> <span class="btn-text">Approve & Commit Repair</span>
                                    </button>
                                </div>
                            ` : ''}}
                        `;
                        container.appendChild(card);
                    }});
                }} catch(err) {{
                    const errStr = String(err);
                    showToast('Error loading repairs: ' + errStr, 'error');
                    container.innerHTML = `<p style="color:var(--rust-terracotta);">Error loading repairs: ${{escapeHTML(errStr)}}</p>`;
                }}
            }}

            // ─── Auto-refresh (45s countdown, pauses on hover) ─────────────────

            let refreshTotal = 45;
            let refreshRemaining = refreshTotal;
            let refreshPaused = false;

            // Pause refresh only when hovering the header area, not the whole container
            const headerEl = document.querySelector('.ledger-header');
            if (headerEl) {{
                headerEl.addEventListener('mouseenter', () => {{ refreshPaused = true; }});
                headerEl.addEventListener('mouseleave', () => {{ refreshPaused = false; }});
            }}

            setInterval(async () => {{
                if (refreshPaused) return;
                refreshRemaining--;
                const countdown = document.getElementById('refresh-countdown');
                const dot = document.getElementById('refresh-dot');
                if (countdown) countdown.textContent = `Auto-refresh in ${{refreshRemaining}}s`;
                if (refreshRemaining <= 0) {{
                    refreshRemaining = refreshTotal;
                    if (dot) dot.classList.remove('pulsing');
                    await refreshDashboardDOM();
                    // Also refresh chart/repair data if those tabs are active
                    const activeTab = ALL_TABS.find(t => document.getElementById(`content-${{t}}`).classList.contains('active'));
                    if (activeTab === 'quality') renderQualityChart();
                    if (activeTab === 'repairs') loadRepairHistory();
                    if (dot) {{ dot.classList.add('pulsing'); }}
                }}
            }}, 1000);

            
            function renderArticleCards(filteredList = currentFilteredArticles, page = 1) {{
                const container = document.getElementById('article-cards-container');
                if (page === 1) container.innerHTML = "";
                
                if (filteredList.length === 0) {{
                    container.innerHTML = `
                        <div class="empty-state-panel">
                            <span class="empty-state-icon">📭</span>
                            <h3 class="empty-state-title">No Specimens Registered</h3>
                            <p class="empty-state-text">No specimens could be found matching the search query or active filter settings. Try resetting your search term or selecting another quality status.</p>
                            <button class="empty-state-reset-btn" onclick="resetSearchFilters()">Reset Catalog Filters</button>
                        </div>
                    `;
                    return;
                }}
                
                const startIndex = (page - 1) * PAGE_SIZE;
                const endIndex = startIndex + PAGE_SIZE;
                const pageList = filteredList.slice(startIndex, endIndex);
                
                pageList.forEach((a, index) => {{
                    const isAccepted = a.quality_score >= {threshold};
                    const badgeClass = isAccepted ? 'excellent' : 'rejected';
                    const statusText = isAccepted ? 'PROVEN' : 'REJECTED';
                    
                    let stampLabel = `№ ${{a.quality_score}}/100 - ${{statusText}}`;
                    
                    let trailBadges = `<span class="trail-badge lang">🌐 ${{escapeHTML((a.language || 'en').toUpperCase())}}</span>`;
                    if (a.has_email_redacted) {{
                        trailBadges += `<span class="trail-badge pii">🔒 Email Redacted</span>`;
                    }}
                    if (a.has_phone_redacted) {{
                        trailBadges += `<span class="trail-badge pii">📞 Phone Redacted</span>`;
                    }}
                    if (a.duplicate_of || a.dedup_info || a.similarity_score) {{
                        const simText = a.similarity_score ? ` (Sim: ${{escapeHTML(String(a.similarity_score))}}%)` : '';
                        const targetText = a.duplicate_of ? ` &rarr; ${{escapeHTML(String(a.duplicate_of))}}` : '';
                        trailBadges += `<span class="trail-badge dedup" title="Merged into master item">🔗 Near-Duplicate${{simText}}${{~targetText ? "" : targetText}}</span>`;
                    }}
                    if (!isAccepted) {{
                        const reasonText = escapeHTML(String(a.rejection_reason || 'Low Readability Score'));
                        trailBadges += `<span class="trail-badge reason" title="Reason for removal">⚠️ Rejection: ${{reasonText}}</span>`;
                    }}

                    const row = document.createElement('div');
                    row.className = "catalog-row";
                    row.tabIndex = 0;
                    row.onclick = () => inspectArticle(a, row);
                    row.onkeydown = (e) => {{
                        if (e.key === 'Enter' || e.key === ' ') {{
                            e.preventDefault();
                            inspectArticle(a, row);
                        }}
                    }};
                    row.innerHTML = `
                        <div class="provenance-stamp ${{badgeClass}}">
                            ${{escapeHTML(stampLabel)}}
                        </div>
                        <div class="specimen-info">
                            <h3 class="specimen-title">${{escapeHTML(a.title)}}</h3>
                            <p class="specimen-author">BY: ${{escapeHTML(a.author || 'Unknown Author')}}</p>
                            <div class="specimen-reasoning-trail">
                                ${{trailBadges}}
                            </div>
                        </div>
                        <div class="specimen-meta">
                            <span class="specimen-source">${{escapeHTML((a.source || 'unknown').toUpperCase())}}</span>
                            <span>DATE: ${{escapeHTML(a.publication_date || 'N/A')}}</span>
                            <span class="specimen-link">Inspect Reconstruction →</span>
                        </div>
                    `;
                    container.appendChild(row);
                }});
                renderPagination(filteredList, page);
            }}

            function renderPagination(filteredList, currentPage) {{
                const container = document.getElementById('pagination-controls');
                container.innerHTML = "";
                const totalPages = Math.ceil(filteredList.length / PAGE_SIZE);
                if (totalPages <= 1) return;
                
                for(let i = 1; i <= totalPages; i++) {{
                    const btn = document.createElement('button');
                    btn.textContent = i;
                    btn.style.cssText = "margin: 0 4px; padding: 4px 8px; cursor: pointer; background: #151211; border: 1px solid var(--border-ledger); color: var(--parchment-white); transition: border-color 0.2s var(--kintsugi-ease);";
                    if (i === currentPage) btn.style.borderColor = "var(--gold-seam)";
                    btn.onclick = () => {{
                        renderSkeletons('article-cards-container', 4);
                        setTimeout(() => renderArticleCards(filteredList, i), 120);
                    }};
                    container.appendChild(btn);
                }}
            }}
            
            let debounceTimer = null;
            function debouncedFilter() {{
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {{
                    filterArticles();
                }}, 150);
            }}

            function filterArticles() {{
                renderSkeletons('article-cards-container', 4);
                
                // Defer slightly to show skeleton animation and smooth card refresh
                setTimeout(() => {{
                    const searchVal = document.getElementById('search-box').value.toLowerCase();
                    const statusVal = document.getElementById('filter-status').value;
                    const sourceVal = document.getElementById('filter-source') ? document.getElementById('filter-source').value : 'all';
                    const minScore = parseInt(document.getElementById('filter-score') ? document.getElementById('filter-score').value : '0', 10) || 0;
                    const sortVal = document.getElementById('sort-articles') ? document.getElementById('sort-articles').value : 'date-desc';
                    
                    const filtered = articles.filter(a => {{
                        const titleMatch = (a.title || '').toLowerCase().includes(searchVal);
                        const authorMatch = (a.author || '').toLowerCase().includes(searchVal);
                        
                        const matchesSearch = titleMatch || authorMatch;
                        if (!matchesSearch) return false;
                        
                        if (statusVal === 'accepted' && a.quality_score < {threshold}) return false;
                        if (statusVal === 'rejected' && a.quality_score >= {threshold}) return false;
                        
                        if (sourceVal !== 'all' && (a.source || '').toLowerCase() !== sourceVal.toLowerCase()) return false;
                        if (a.quality_score < minScore) return false;
                        
                        return true;
                    }});

                    filtered.sort((a, b) => {{
                        if (sortVal === 'date-desc') return new Date(b.publication_date || 0) - new Date(a.publication_date || 0);
                        if (sortVal === 'date-asc') return new Date(a.publication_date || 0) - new Date(b.publication_date || 0);
                        if (sortVal === 'score-desc') return (b.quality_score || 0) - (a.quality_score || 0);
                        if (sortVal === 'score-asc') return (a.quality_score || 0) - (b.quality_score || 0);
                        if (sortVal === 'title-asc') return (a.title || '').localeCompare(b.title || '');
                        return 0;
                    }});
                    
                    currentFilteredArticles = filtered;
                    renderArticleCards(currentFilteredArticles, 1);
                }}, 120);
            }}
            
            function inspectArticle(a, triggeringElement) {{
                currentlyInspectedArticle = a;
                lastFocusedElement = triggeringElement;
                document.getElementById('modal-title').textContent = `Specimen Reconstruction: № ${{a.quality_score}}/100`;
                
                const wordCount = a.content ? a.content.trim().split(/\s+/).length : 0;
                document.getElementById('val-length').textContent = `${{wordCount}} words`;
                document.getElementById('bar-length').style.width = `${{Math.min(wordCount / 10, 100)}}%`;
                
                document.getElementById('val-readability').textContent = `${{a.quality_breakdown?.readability || 0}} pts`;
                document.getElementById('bar-readability').style.width = `${{Math.min(a.quality_breakdown?.readability || 0, 100)}}%`;
                
                document.getElementById('val-structure').textContent = `${{a.quality_breakdown?.structure || 0}} pts`;
                document.getElementById('bar-structure').style.width = `${{a.quality_breakdown?.structure || 0}}%`;
                
                document.getElementById('val-authority').textContent = `${{a.quality_breakdown?.authority || 0}} pts`;
                document.getElementById('bar-authority').style.width = `${{a.quality_breakdown?.authority || 0}}%`;
                
                const rawBox = document.getElementById('diff-raw');
                const cleanBox = document.getElementById('diff-clean');
                
                // Fetch raw article content from the stored raw map
                const rawContent = a.raw_content || 'No raw content stored';
                
                rawBox.innerHTML = `<pre>${{escapeHTML(rawContent)}}</pre>`;
                cleanBox.innerHTML = `<div class="serif-content">${{escapeHTML(a.content)}}</div>`;
                
                // Trigger gold seam drawing animation inside the modal
                const verticalSeam = document.querySelector('.modal-seam-path');
                if (verticalSeam) {{
                    verticalSeam.classList.remove('animate');
                    verticalSeam.offsetHeight; /* Trigger reflow to restart animation */
                    verticalSeam.classList.add('animate');
                }}
                
                toggleModal(true);
            }}
            
            function toggleModal(open) {{
                const overlay = document.getElementById('modal-overlay');
                overlay.classList.toggle('active', open);
                if (open) {{
                    const content = overlay.querySelector('.modal-content');
                    if (content) {{
                        content.tabIndex = -1;
                        content.focus();
                    }}
                }} else {{
                    if (lastFocusedElement) {{
                        lastFocusedElement.focus();
                    }}
                }}
            }}
            
            function closeModal(e) {{
                toggleModal(false);
            }}
            
            document.addEventListener('keydown', (e) => {{
                if (e.key === 'Escape') {{
                    const overlay = document.getElementById('modal-overlay');
                    if (overlay && overlay.classList.contains('active')) {{
                        toggleModal(false);
                    }}
                }}
            }});

            function escapeHTML(str) {{
                return str.replace(/[&<>'"]/g, 
                    tag => ({{
                        '&': '&amp;',
                        '<': '&lt;',
                        '>': '&gt;',
                        "'": '&#39;',
                        '"': '&quot;'
                     }}[tag] || tag)
                );
            }}

            async function refreshDashboardDOM() {{
                try {{
                    const resp = await fetch('/api/dashboard-data');
                    const data = await resp.json();
                    
                    // Update stats dynamically from the backend data
                    document.getElementById('stat-yield').textContent = data.accepted_articles;
                    document.getElementById('stat-discarded').textContent = data.rejected_articles;
                    document.getElementById('stat-dedup').textContent = data.dedup_saved;
                    document.getElementById('stat-avg').textContent = data.avg_score;
                    
                    // Update scrapers list
                    document.querySelector('#ops-list').innerHTML = data.scrapers_html;
                    // Re-apply filter after refresh
                    applyOpsFilter();
                    
                    // Update articles and quality stats
                    articles = data.articles;
                    if (data.quality_stats) qualityStats = data.quality_stats;
                    
                    // Re-render catalog and quality chart
                    filterArticles();
                    renderQualityChart();
                    
                    // Reset sessionStats since the data has been committed to backend
                    sessionStats = {{
                        yield: 0,
                        discarded: 0,
                        dedup: 0,
                        totalScore: 0.0,
                        countScore: 0
                    }};
                    
                    // Refresh repair history to sync approval states immediately
                    loadRepairHistory();
                }} catch (err) {{
                    console.error("Error refreshing dashboard data:", err);
                }}
            }}

            async function triggerHeal(collectorId) {{
                const record = document.getElementById(`record-${{collectorId}}`);
                const btn = record ? record.querySelector('button[data-action="trigger-heal"]') : null;
                const textSpan = btn ? btn.querySelector('.btn-text') : null;
                
                if (record) {{
                    record.querySelectorAll('button').forEach(b => b.disabled = true);
                }}
                if (btn) {{
                    btn.classList.add('button-loading');
                }}
                if (textSpan) {{ textSpan.textContent = 'Contacting Scraper Studio...'; }}
                
                // Immediately transition stepper to step 2 (Healing)
                const stepper = document.getElementById(`stepper-${{collectorId}}`);
                if (stepper) {{
                    const segments = stepper.querySelectorAll('.step-segment');
                    if (segments.length >= 2) {{
                        segments[1].classList.add('active');
                    }}
                }}

                try {{
                    const resp = await fetch('/api/trigger-heal', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{ collector_id: collectorId }})
                    }});
                    const data = await resp.json();
                    if (btn) {{
                        btn.classList.remove('button-loading');
                    }}
                    if (data.status === 'error') {{
                        showToast(data.message || 'Heal operation returned error.', 'error');
                        renderHealPreview(collectorId, data);
                        if (record) {{
                            record.querySelectorAll('button').forEach(b => b.disabled = false);
                        }}
                        if (textSpan) {{ textSpan.textContent = 'Trigger Self-Heal & Review Preview'; }}
                    }} else {{
                        showToast('Self-heal initiated successfully.', 'info');
                        await refreshDashboardDOM();
                    }}
                }} catch(err) {{
                    if (btn) {{
                        btn.classList.remove('button-loading');
                    }}
                    if (record) {{
                        record.querySelectorAll('button').forEach(b => b.disabled = false);
                    }}
                    if (textSpan) {{ textSpan.textContent = 'Trigger Self-Heal & Review Preview'; }}
                    const msg = 'Error contacting heal API: ' + err;
                    showToast(msg, 'error');
                    renderHealPreview(collectorId, {{status: 'error', message: msg}});
                }}
            }}

            async function healNow(collectorId) {{
                const record = document.getElementById(`record-${{collectorId}}`);
                const btn = record ? record.querySelector('button[data-action="heal-now"]') : null;
                const textSpan = btn ? btn.querySelector('.btn-text') : null;
                
                if (record) {{
                    record.querySelectorAll('button').forEach(b => b.disabled = true);
                }}
                if (btn) {{
                    btn.classList.add('button-loading');
                }}
                if (textSpan) {{ textSpan.textContent = 'Running Cycle...'; }}
                
                // Immediately transition stepper to step 2 (Healing)
                const stepper = document.getElementById(`stepper-${{collectorId}}`);
                if (stepper) {{
                    const segments = stepper.querySelectorAll('.step-segment');
                    if (segments.length >= 2) {{
                        segments[1].classList.add('active');
                    }}
                }}

                try {{
                    const resp = await fetch('/api/heal-now', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{ collector_id: collectorId }})
                    }});
                    const data = await resp.json();
                    if (btn) {{
                        btn.classList.remove('button-loading');
                    }}
                    if (data.status === 'error') {{
                        showToast(data.message || 'Heal now cycle failed.', 'error');
                        renderGlobalError(data.message);
                        if (record) {{
                            record.querySelectorAll('button').forEach(b => b.disabled = false);
                        }}
                        if (textSpan) {{ textSpan.textContent = 'Auto-Heal Now (Full Cycle)'; }}
                    }} else {{
                        showToast('Full auto-heal cycle completed.', 'success');
                        setTimeout(refreshDashboardDOM, 1000);
                    }}
                }} catch(err) {{
                    if (btn) {{
                        btn.classList.remove('button-loading');
                    }}
                    if (record) {{
                        record.querySelectorAll('button').forEach(b => b.disabled = false);
                    }}
                    if (textSpan) {{ textSpan.textContent = 'Auto-Heal Now (Full Cycle)'; }}
                    const msg = 'Error triggering heal now: ' + err;
                    showToast(msg, 'error');
                    renderGlobalError(msg);
                }}
            }}

            function renderHealPreview(collectorId, data) {{
                const record = document.getElementById(`record-${{collectorId}}`);
                if (!record) return;

                // Remove old preview if any
                const old = record.querySelector('.heal-preview-panel');
                if (old) old.remove();

                const panel = document.createElement('div');
                panel.className = 'heal-preview-panel visible';

                const isAwaiting = data.status === 'awaiting_approval';
                const isSuccess  = data.status === 'success';

                panel.innerHTML = `
                    <div class="heal-preview-title">
                        ${{isAwaiting ? '&#9875; Awaiting Approval &mdash; Review the proposed repair below' : isSuccess ? '&#10004; Heal Committed' : '&#9888; Heal Result'}}
                    </div>
                    ${{data.diff_summary ? `<div class="heal-diff-summary">${{escapeHTML(data.diff_summary)}}</div>` : ''}}
                    ${{data.preview_result ? `<div class="heal-preview-result">${{escapeHTML(data.preview_result)}}</div>` : ''}}
                    ${{data.message && !data.preview_result ? `<div class="heal-preview-result">${{escapeHTML(data.message)}}</div>` : ''}}
                    ${{isAwaiting ? `
                        <button class="heal-approve-btn" data-action="approve-heal" data-collector="${{escapeHTML(collectorId)}}">
                            <span class="btn-text">&#10003; Approve &amp; Commit Repair</span>
                        </button>
                        <div class="heal-status-msg">Heal will not take effect until approved.</div>
                    ` : ''}}
                `;
                record.appendChild(panel);

                // If auto-success (demo/mock), also draw the gold seam
                if (isSuccess) {{
                    const existingSeam = record.querySelector('.kintsugi-horizontal-seam');
                    if (!existingSeam) {{
                        const seam = document.createElement('div');
                        seam.className = 'kintsugi-horizontal-seam';
                        seam.innerHTML = `<svg class="seam-svg" viewBox="0 0 100 10" preserveAspectRatio="none"><path d="M0,5 L12,2 L23,8 L35,3 L48,7 L60,4 L72,8 L85,2 L100,5" stroke="var(--gold-seam)" stroke-width="1.5" fill="none" class="seam-path" /></svg>`;
                        record.insertBefore(seam, panel);
                    }}
                }}
            }}

            async function approveHeal(collectorId, btn) {{
                btn.disabled = true;
                btn.classList.add('button-loading');
                const textSpan = btn.querySelector('.btn-text');
                if (textSpan) {{ textSpan.textContent = 'Committing repair...'; }}
                
                try {{
                    const resp = await fetch('/api/approve-heal', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{ collector_id: collectorId }})
                    }});
                    const data = await resp.json();
                    
                    btn.classList.remove('button-loading');
                    
                    if (data.status === 'success') {{
                        showToast('Repair approved and committed successfully!', 'success');
                        
                        // Play micro-bounce animation on approved card container
                        const record = document.getElementById(`record-${{collectorId}}`);
                        if (record) {{
                            record.classList.remove('newly-healed');
                            record.offsetHeight; // force reflow
                            record.classList.add('newly-healed');
                        }}
                        
                        // Defer DOM refresh slightly to let bounce animation finish
                        setTimeout(async () => {{
                            await refreshDashboardDOM();
                        }}, 600);
                    }} else {{
                        btn.disabled = false;
                        if (textSpan) {{ textSpan.textContent = 'Approve & Commit Repair'; }}
                        const msg = 'Approval failed: ' + (data.message || 'Unknown Error');
                        showToast(msg, 'error');
                        const record = document.getElementById(`record-${{collectorId}}`);
                        if (record) {{
                            const statusMsg = record.querySelector('.heal-status-msg');
                            if (statusMsg) {{
                                statusMsg.textContent = msg;
                                statusMsg.style.color = 'var(--rust-terracotta)';
                            }}
                        }}
                    }}
                }} catch(err) {{
                    btn.classList.remove('button-loading');
                    btn.disabled = false;
                    if (textSpan) {{ textSpan.textContent = 'Approve & Commit Repair'; }}
                    const msg = 'Error calling approve API: ' + err;
                    showToast(msg, 'error');
                    const record = document.getElementById(`record-${{collectorId}}`);
                    if (record) {{
                        const statusMsg = record.querySelector('.heal-status-msg');
                        if (statusMsg) {{
                            statusMsg.textContent = msg;
                            statusMsg.style.color = 'var(--rust-terracotta)';
                        }}
                    }}
                }}
            }}

            function renderGlobalError(message) {{
                const header = document.querySelector('.ledger-header');
                const old = document.getElementById('global-error-panel');
                if (old) old.remove();
                
                const panel = document.createElement('div');
                panel.id = 'global-error-panel';
                panel.className = 'heal-preview-panel visible';
                panel.style.margin = '20px 0';
                
                panel.innerHTML = `
                    <div class="heal-preview-title"><svg style='width:1.2em;height:1.2em;vertical-align:-0.2em;display:inline-block;' fill='none' stroke='currentColor' viewBox='0 0 24 24'><path stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z'></path></svg> Action Failed</div>
                    <div class="heal-preview-result" style="color: var(--rust); border-color: var(--rust);">${{escapeHTML(message)}}</div>
                `;
                header.insertAdjacentElement('afterend', panel);
            }}

            async function runDemo(btn) {{
                btn.disabled = true;
                btn.classList.add('button-loading');
                const textSpan = btn.querySelector('.btn-text');
                if (textSpan) {{ textSpan.textContent = 'Running Demo Cycle...'; }}
                try {{
                    const resp = await fetch('/api/run-demo', {{ method: 'POST' }});
                    const data = await resp.json();

                    btn.classList.remove('button-loading');

                    if (data.status === 'success') {{
                        showToast('Live demo cycle completed!', 'success');
                        await refreshDashboardDOM();
                        btn.disabled = false;
                        if (textSpan) {{ textSpan.textContent = 'Run Live Demo Cycle'; }}
                    }} else {{
                        const msg = 'Demo failed: ' + data.message;
                        showToast(msg, 'error');
                        renderGlobalError(msg);
                        btn.disabled = false;
                        if (textSpan) {{ textSpan.textContent = 'Run Live Demo Cycle'; }}
                    }}
                }} catch(err) {{
                    btn.classList.remove('button-loading');
                    const msg = 'Error triggering demo: ' + err;
                    showToast(msg, 'error');
                    renderGlobalError(msg);
                    btn.disabled = false;
                    btn.innerHTML = `&#9654; <span class="btn-text">Run Live Demo Cycle</span>`;
                }}
            }}

            function downloadCSV(text, filename) {{
                const lines = text.split('\\n');
                const books = [];
                let currentBook = null;

                for (let line of lines) {{
                    line = line.trim();
                    const titleMatch = line.match(/^\\d+\\.\\s+\\*\\*(.+?)\\*\\*/);
                    if (titleMatch) {{
                        if (currentBook) books.push(currentBook);
                        currentBook = {{
                            title: titleMatch[1],
                            price: '',
                            availability: '',
                            rating: '',
                            thumbnail: '',
                            detail_page: ''
                        }};
                        continue;
                    }}

                    if (currentBook) {{
                        if (line.includes('**Price**')) {{
                            currentBook.price = line.split('**Price**:')[1]?.trim() || '';
                        }} else if (line.includes('**Availability**')) {{
                            currentBook.availability = line.split('**Availability**:')[1]?.trim() || '';
                        }} else if (line.includes('**Rating**')) {{
                            currentBook.rating = line.split('**Rating**:')[1]?.trim() || '';
                        }} else if (line.includes('**Thumbnail**')) {{
                            currentBook.thumbnail = line.split('**Thumbnail**:')[1]?.trim() || '';
                        }} else if (line.includes('**Detail Page**')) {{
                            currentBook.detail_page = line.split('**Detail Page**:')[1]?.trim() || '';
                        }}
                    }}
                }}
                if (currentBook) books.push(currentBook);

                let csvContent = "";
                if (books.length > 0) {{
                    const headers = ["Title", "Price", "Availability", "Rating", "Thumbnail", "Detail Page"];
                    csvContent = headers.map(h => `"${{h.replace(/"/g, '""')}}"`).join(",") + "\\n";
                    books.forEach(b => {{
                        const row = [b.title, b.price, b.availability, b.rating, b.thumbnail, b.detail_page];
                        csvContent += row.map(v => `"${{(v || '').replace(/"/g, '""')}}"`).join(",") + "\\n";
                    }});
                }} else {{
                    csvContent = `"Content"\\n"${{text.replace(/"/g, '""')}}"\\n`;
                }}

                const blob = new Blob([csvContent], {{ type: 'text/csv;charset=utf-8;' }});
                const url = URL.createObjectURL(blob);
                const link = document.createElement("a");
                link.setAttribute("href", url);
                link.setAttribute("download", filename);
                link.style.visibility = 'hidden';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                showToast('CSV export downloaded successfully!', 'success');
            }}

            function downloadDOC(text, filename) {{
                const htmlContent = text
                    .replace(/\\n/g, '<br>')
                    .replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>')
                    .replace(/#(.*)/g, '<h2>$1</h2>');

                const documentHtml = `
                    <html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
                    <head>
                        <title>Scraped Data Export</title>
                        <!--[if gte mso 9]>
                        <xml>
                            <w:WordDocument>
                                <w:View>Print</w:View>
                                <w:Zoom>100</w:Zoom>
                                <w:DoNotOptimizeForBrowser/>
                            </w:WordDocument>
                        </xml>
                        <![endif]-->
                        <style>
                            body {{ font-family: 'Calibri', 'Arial', sans-serif; font-size: 11pt; line-height: 1.5; color: #333333; }}
                            h2 {{ font-family: 'Georgia', serif; color: #8B5A2B; border-bottom: 1px solid #CCCCCC; padding-bottom: 5px; }}
                            strong {{ color: #000000; }}
                        </style>
                    </head>
                    <body>
                        ${{htmlContent}}
                    </body>
                    </html>
                `;

                const blob = new Blob(['\\ufeff' + documentHtml], {{ type: 'application/msword' }});
                const url = URL.createObjectURL(blob);
                const link = document.createElement("a");
                link.setAttribute("href", url);
                link.setAttribute("download", filename);
                link.style.visibility = 'hidden';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                showToast('Word DOC export downloaded successfully!', 'success');
            }}
            
            // Global Event Delegation for CSP Compliance (No Inline Event Handlers)
            document.addEventListener('DOMContentLoaded', () => {{
                updateStatsDOM();
                const opsFilterSelect = document.getElementById('ops-status-filter');
                if (opsFilterSelect) opsFilterSelect.addEventListener('change', applyOpsFilter);

                const opsSearchInput = document.getElementById('ops-search');
                if (opsSearchInput) opsSearchInput.addEventListener('input', applyOpsFilter);

                const catalogSearchInput = document.getElementById('search-box');
                if (catalogSearchInput) catalogSearchInput.addEventListener('input', debouncedFilter);

                const catalogStatusSelect = document.getElementById('filter-status');
                if (catalogStatusSelect) catalogStatusSelect.addEventListener('change', filterArticles);

                const catalogSourceSelect = document.getElementById('filter-source');
                if (catalogSourceSelect) catalogSourceSelect.addEventListener('change', filterArticles);

                const catalogScoreSelect = document.getElementById('filter-score');
                if (catalogScoreSelect) catalogScoreSelect.addEventListener('change', filterArticles);

                const catalogSortSelect = document.getElementById('sort-articles');
                if (catalogSortSelect) catalogSortSelect.addEventListener('change', filterArticles);
                
                // Export actions listeners
                const btnCopyClean = document.getElementById('btn-copy-clean');
                if (btnCopyClean) {{
                    btnCopyClean.addEventListener('click', () => {{
                        if (!currentlyInspectedArticle || !currentlyInspectedArticle.content) {{
                            showToast('No structured content to copy.', 'warning');
                            return;
                        }}
                        navigator.clipboard.writeText(currentlyInspectedArticle.content)
                            .then(() => showToast('Specimen data copied to clipboard!', 'success'))
                            .catch(err => {{
                                console.error('Copy failed: ', err);
                                showToast('Failed to copy to clipboard.', 'error');
                            }});
                    }});
                }}

                const btnDownloadCsv = document.getElementById('btn-download-csv');
                if (btnDownloadCsv) {{
                    btnDownloadCsv.addEventListener('click', () => {{
                        if (!currentlyInspectedArticle || !currentlyInspectedArticle.content) {{
                            showToast('No structured content to export.', 'warning');
                            return;
                        }}
                        const cleanTitle = (currentlyInspectedArticle.title || 'scraped_data').replace(/[^a-z0-9]/gi, '_').toLowerCase();
                        downloadCSV(currentlyInspectedArticle.content, cleanTitle + '.csv');
                    }});
                }}

                const btnDownloadDocx = document.getElementById('btn-download-docx');
                if (btnDownloadDocx) {{
                    btnDownloadDocx.addEventListener('click', () => {{
                        if (!currentlyInspectedArticle || !currentlyInspectedArticle.content) {{
                            showToast('No structured content to export.', 'warning');
                            return;
                        }}
                        const cleanTitle = (currentlyInspectedArticle.title || 'scraped_data').replace(/[^a-z0-9]/gi, '_').toLowerCase();
                        downloadDOC(currentlyInspectedArticle.content, cleanTitle + '.doc');
                    }});
                }}
                
                populateSourceFilter();
            }});

            document.addEventListener('click', (e) => {{
                const actionBtn = e.target.closest('[data-action]');
                if (actionBtn) {{
                    const action = actionBtn.dataset.action;
                    const colId = actionBtn.dataset.collector;
                    if (action === 'trigger-heal') triggerHeal(colId);
                    else if (action === 'heal-now') healNow(colId);
                    else if (action === 'approve-heal') approveHeal(colId, actionBtn);
                    return;
                }}

                const tabBtn = e.target.closest('[data-tab]');
                if (tabBtn) {{
                    switchTab(tabBtn.dataset.tab);
                    return;
                }}

                const sortBtn = e.target.closest('[data-sort]');
                if (sortBtn) {{
                    sortOps(sortBtn.dataset.sort);
                    return;
                }}

                const demoBtn = e.target.closest('#run-demo-btn');
                if (demoBtn) {{
                    runDemo(demoBtn);
                    return;
                }}

                const modalCloseBtn = e.target.closest('#modal-close-btn');
                if (modalCloseBtn) {{
                    toggleModal(false);
                    return;
                }}

                const modalOverlay = e.target.closest('#modal-overlay');
                if (modalOverlay && e.target === modalOverlay) {{
                    toggleModal(false);
                    return;
                }}
            }});

        async function triggerOnDemandScrape() {{
            const inputEl = document.getElementById('ondemand-url-input');
            const btnEl = document.getElementById('ondemand-submit-btn');
            const badgeEl = document.getElementById('ondemand-status-badge');
            
            if (!inputEl || !inputEl.value.trim()) {{
                showToast("Please enter a valid website URL to scrape.", "warning");
                return;
            }}
            
            const targetUrl = inputEl.value.trim();
            btnEl.disabled = true;
            btnEl.innerHTML = `<svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' style='vertical-align: text-bottom; margin-right: 6px;'><path d='M5 22h14'></path><path d='M5 2h14'></path><path d='M17 22v-4.172a2 2 0 0 0-.586-1.414L12 12l-4.414 4.414A2 2 0 0 0 7 17.828V22'></path><path d='M7 2v4.172a2 2 0 0 0 .586 1.414L12 12l4.414-4.414A2 2 0 0 0 17 6.172V2'></path></svg> Submitting...`;
            badgeEl.style.display = "inline-block";
            badgeEl.innerText = "Queuing job...";
            
            // Clean up any existing active polling interval before starting a new one
            if (window.activeOndemandPollInterval) {{
                clearInterval(window.activeOndemandPollInterval);
                window.activeOndemandPollInterval = null;
            }}
            
            try {{
                const res = await fetch('/api/scrape-url', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ url: targetUrl }})
                }});
                
                const data = await res.json();
                if (res.status !== 200 || data.status !== "success") {{
                    showToast(data.message || "Failed to submit scrape job.", "error");
                    btnEl.disabled = false;
                    btnEl.innerHTML = `<svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' style='vertical-align: text-bottom; margin-right: 6px;'><polygon points='13 2 3 14 12 14 11 22 21 10 12 10 13 2'></polygon></svg> Scrape On-Demand`;
                    badgeEl.style.display = "none";
                    return;
                }}
                
                const jobId = data.job_id;
                showToast("Scrape job queued! Polling live progress...", "info");
                
                let pollAttempts = 0;
                const maxPollAttempts = 300; // 300 * 2000ms = 600s = 10 minutes timeout
                let consecutiveErrors = 0;
                
                // Start polling and keep track of it globally
                window.activeOndemandPollInterval = setInterval(async () => {{
                    pollAttempts++;
                    if (pollAttempts > maxPollAttempts) {{
                        clearInterval(window.activeOndemandPollInterval);
                        window.activeOndemandPollInterval = null;
                        showToast("Scrape job timed out after 10 minutes.", "error");
                        btnEl.disabled = false;
                        btnEl.innerHTML = `<svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' style='vertical-align: text-bottom; margin-right: 6px;'><polygon points='13 2 3 14 12 14 11 22 21 10 12 10 13 2'></polygon></svg> Scrape On-Demand`;
                        badgeEl.style.display = "none";
                        return;
                    }}
                    
                    try {{
                        const pollRes = await fetch('/api/scrape-url/' + jobId);
                        if (!pollRes.ok) {{
                            throw new Error(`HTTP error! status: ${{pollRes.status}}`);
                        }}
                        const pollData = await pollRes.json();
                        
                        // Reset consecutive error count on successful fetch
                        consecutiveErrors = 0;
                        
                        if (!pollData || !pollData.status) {{
                            throw new Error("Invalid response schema from backend job status endpoint");
                        }}
                        
                        if (pollData.step_message) {{
                            badgeEl.innerText = pollData.step_message;
                        }}
                        
                        if (pollData.status === "completed") {{
                            clearInterval(window.activeOndemandPollInterval);
                            window.activeOndemandPollInterval = null;
                            showToast("Scrape complete! Item placed in Repair History (Pending Review).", "success");
                            inputEl.value = "";
                            btnEl.disabled = false;
                            btnEl.innerHTML = `<svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' style='vertical-align: text-bottom; margin-right: 6px;'><polygon points='13 2 3 14 12 14 11 22 21 10 12 10 13 2'></polygon></svg> Scrape On-Demand`;
                            badgeEl.style.display = "none";
                            
                            // Update client-side session stats based on this scrape's articles
                            if (pollData.result) {{
                                const res = pollData.result;
                                const scrapedArticles = res.articles || [];
                                let newYield = 0;
                                let newDiscarded = 0;
                                let newDedup = res.duplicates_removed || 0;
                                let newTotalScore = 0.0;
                                let newCountScore = 0;

                                scrapedArticles.forEach(art => {{
                                    const score = art.quality_score || 0;
                                    if (score >= 50) {{
                                        newYield++;
                                    }} else {{
                                        newDiscarded++;
                                    }}
                                    newTotalScore += score;
                                    newCountScore++;
                                }});

                                sessionStats.yield += newYield;
                                sessionStats.discarded += newDiscarded;
                                sessionStats.dedup += newDedup;
                                sessionStats.totalScore += newTotalScore;
                                sessionStats.countScore += newCountScore;

                                updateStatsDOM();
                            }}

                            // Re-fetch data and switch to repairs tab to show quarantine
                            await refreshDashboardDOM();
                            switchTab('repairs');
                        }} else if (pollData.status === "failed") {{
                            clearInterval(window.activeOndemandPollInterval);
                            window.activeOndemandPollInterval = null;
                            showToast(pollData.error || "On-demand scrape failed.", "error");
                            btnEl.disabled = false;
                            btnEl.innerHTML = `<svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' style='vertical-align: text-bottom; margin-right: 6px;'><polygon points='13 2 3 14 12 14 11 22 21 10 12 10 13 2'></polygon></svg> Scrape On-Demand`;
                            badgeEl.style.display = "none";
                        }}
                    }} catch (err) {{
                        consecutiveErrors++;
                        console.error("Polling error:", err);
                        
                        if (consecutiveErrors >= 5) {{
                            clearInterval(window.activeOndemandPollInterval);
                            window.activeOndemandPollInterval = null;
                            showToast("Network issues detected. Stopped polling live progress.", "error");
                            btnEl.disabled = false;
                            btnEl.innerHTML = `<svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' style='vertical-align: text-bottom; margin-right: 6px;'><polygon points='13 2 3 14 12 14 11 22 21 10 12 10 13 2'></polygon></svg> Scrape On-Demand`;
                            badgeEl.style.display = "none";
                        }}
                    }}
                }}, 2000);
                
            }} catch (err) {{
                showToast("Network error initiating scrape.", "error");
                btnEl.disabled = false;
                btnEl.innerHTML = `<svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' style='vertical-align: text-bottom; margin-right: 6px;'><polygon points='13 2 3 14 12 14 11 22 21 10 12 10 13 2'></polygon></svg> Scrape On-Demand`;
                badgeEl.style.display = "none";
            }}
        }}
        
        // Ensure active poll intervals are cleaned up when the page unloads
        window.addEventListener('beforeunload', () => {{
            if (window.activeOndemandPollInterval) {{
                clearInterval(window.activeOndemandPollInterval);
                window.activeOndemandPollInterval = null;
            }}
        }});
        """
