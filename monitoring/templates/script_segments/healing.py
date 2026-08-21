HEALING_JS = r"""            async function triggerHeal(collectorId) {{
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

"""
