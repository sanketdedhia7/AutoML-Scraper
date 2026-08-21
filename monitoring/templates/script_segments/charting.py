CHARTING_JS = r"""            // ─── Quality Chart ─────────────────────────────────────────────────

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
            
"""
