ONDEMAND_JS = r"""        async function triggerOnDemandScrape() {{
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
