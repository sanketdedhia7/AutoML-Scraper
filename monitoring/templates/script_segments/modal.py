MODAL_JS = r"""            function inspectArticle(a, triggeringElement) {{
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

"""
