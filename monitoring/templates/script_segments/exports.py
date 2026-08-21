EXPORTS_JS = r"""            function downloadCSV(text, filename) {{
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

"""
