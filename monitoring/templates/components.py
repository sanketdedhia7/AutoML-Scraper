def get_dashboard_body(curated_date: str, accepted_articles: int, rejected_articles: int, dedup_saved: int, avg_score: float, threshold: int, scrapers_html: str) -> str:
    return f"""
        <div class="ledger-container">
            <!-- Header Section -->
            <header class="ledger-header">
                <div class="ledger-meta">
                    <span>VOLUME 01</span>
                    <div style="display: flex; gap: 16px; align-items: center;">
                        <button class="demo-btn" id="run-demo-btn">&#9654; <span class="btn-text">Run Live Demo Cycle</span></button>
                        <span>LEDGER REGISTRY: {curated_date}</span>
                        <div class="auto-refresh-bar" id="refresh-bar">
                            <div class="refresh-dot pulsing" id="refresh-dot"></div>
                            <span id="refresh-countdown">Auto-refresh in 45s</span>
                        </div>
                    </div>
                </div>
                <h1 class="ledger-title">Conservator's Workshop Ledger</h1>
                <p class="ledger-subtitle">Self-Healing Web Scraping & Specimen Curation Registry</p>
            </header>
            
            <!-- Dynamic Yield/Summary Banner with Trend Sparklines & Balance Bars -->
            <div class="yield-box">
                <div class="yield-item">
                    <div class="yield-label">Yield (Total Curated)</div>
                    <div class="yield-value" id="stat-yield">{accepted_articles}</div>
                    <div class="yield-sparkline-container" title="Pipeline output growth trend">
                        <svg class="yield-sparkline" viewBox="0 0 100 24" preserveAspectRatio="none">
                            <path d="M0,20 Q25,18 50,12 T100,4" fill="none" stroke="var(--verdigris-green)" stroke-width="2.5"/>
                        </svg>
                        <span class="sparkline-trend-text green">&uarr; +14% run growth</span>
                    </div>
                </div>
                <div class="yield-item">
                    <div class="yield-label">Discarded (Rejected)</div>
                    <div class="yield-value" id="stat-discarded">{rejected_articles}</div>
                    <div class="yield-sparkline-container" title="Before/after raw vs clean balance">
                        <div class="mini-balance-bar">
                            <div class="bar-segment raw" style="width: 100%" title="Raw ingested"></div>
                            <div class="bar-segment clean" style="width: 65%" title="Clean retained"></div>
                        </div>
                        <span class="sparkline-trend-text rust">Filter &amp; PII Scrubbed</span>
                    </div>
                </div>
                <div class="yield-item">
                    <div class="yield-label">Duplicates Removed</div>
                    <div class="yield-value" id="stat-dedup">{dedup_saved}</div>
                    <div class="yield-sparkline-container" title="Semantic LSH dedup volume">
                        <svg class="yield-sparkline" viewBox="0 0 100 24" preserveAspectRatio="none">
                            <path d="M0,22 L25,16 L50,18 L75,8 L100,3" fill="none" stroke="var(--gold-seam)" stroke-width="2.5"/>
                        </svg>
                        <span class="sparkline-trend-text gold">LSH + Sim Hash</span>
                    </div>
                </div>
                <div class="yield-item">
                    <div class="yield-label">Avg Quality Score</div>
                    <div class="yield-value" id="stat-avg">{avg_score}</div>
                    <div class="yield-sparkline-container" title="Mean article score trend">
                        <svg class="yield-sparkline" viewBox="0 0 100 24" preserveAspectRatio="none">
                            <path d="M0,18 L30,14 L60,10 L100,4" fill="none" stroke="var(--parchment-white)" stroke-width="2.5"/>
                        </svg>
                        <span class="sparkline-trend-text">&ge; {int(threshold)} Threshold</span>
                    </div>
                </div>
            </div>
            
            <!-- Sticky Bookmarks Tabs Navigation -->
            <div class="sticky-header-container">
                <div class="sticky-header-top">
                    <nav class="ledger-tabs">
                        <button id="nav-ops" class="tab-button active" data-tab="ops">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: text-bottom; margin-right: 6px;"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"></path></svg>
                            Ledger of Scraper Records
                        </button>
                        <button id="nav-data" class="tab-button" data-tab="data">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: text-bottom; margin-right: 6px;"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg>
                            Specimen Catalog
                        </button>
                        <button id="nav-quality" class="tab-button" data-tab="quality">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: text-bottom; margin-right: 6px;"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>
                            Quality Stats
                        </button>
                        <button id="nav-repairs" class="tab-button" data-tab="repairs">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: text-bottom; margin-right: 6px;"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path></svg>
                            Repair History
                        </button>
                    </nav>
                </div>
                <div class="ondemand-bar">
                    <input type="url" id="ondemand-url-input" placeholder="Paste target website URL (e.g. https://news.ycombinator.com)..." class="ondemand-input">
                    <button id="ondemand-submit-btn" class="ondemand-btn" onclick="triggerOnDemandScrape()">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: text-bottom; margin-right: 6px;"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
                        Scrape On-Demand
                    </button>
                    <span id="ondemand-status-badge" class="ondemand-badge" style="display:none;"></span>
                </div>
            </div>
            
            <!-- VIEW 1: Ops Health Ledger -->
            <div id="content-ops" class="tab-content active">
                <!-- Ops filter bar -->
                <div class="ops-filter-bar">
                    <select id="ops-status-filter">
                        <option value="all">All Status</option>
                        <option value="healthy">Healthy Only</option>
                        <option value="unhealthy">Unhealthy Only</option>
                        <option value="error">Error Only</option>
                    </select>
                    <input type="text" id="ops-search" placeholder="Filter by collector ID..." style="flex:1;">
                    <button class="sort-btn" id="sort-articles-btn" data-sort="articles" title="Sort by article count">
                        <span class="sort-arrow">&#8597;</span> Articles
                    </button>
                    <button class="sort-btn" id="sort-status-btn" data-sort="status" title="Sort by status">
                        <span class="sort-arrow">&#8597;</span> Status
                    </button>
                </div>
                <div class="ledger-records-list" id="ops-list">
                    {scrapers_html}
                </div>
            </div>
            
            <!-- VIEW 2: Specimen Catalog -->
            <div id="content-data" class="tab-content">
                <div class="catalog-controls">
                    <input type="text" class="catalog-search" id="search-box" placeholder="Search specimens by title or author...">
                    <select class="catalog-select" id="filter-status">
                        <option value="all">All Statuses</option>
                        <option value="accepted">Accepted (Score &gt;= {int(threshold)})</option>
                        <option value="rejected">Rejected (Score &lt; {int(threshold)})</option>
                    </select>
                    <select class="catalog-select" id="filter-source">
                        <option value="all">All Sources</option>
                    </select>
                    <select class="catalog-select" id="filter-score">
                        <option value="0">All Scores</option>
                        <option value="50">Min Score 50</option>
                        <option value="70">Min Score 70</option>
                        <option value="80">Min Score 80</option>
                        <option value="90">Min Score 90</option>
                    </select>
                    <select class="catalog-select" id="sort-articles">
                        <option value="date-desc">Newest First</option>
                        <option value="date-asc">Oldest First</option>
                        <option value="score-desc">Score (High &rarr; Low)</option>
                        <option value="score-asc">Score (Low &rarr; High)</option>
                        <option value="title-asc">Title (A &rarr; Z)</option>
                    </select>
                </div>
                
                <div class="catalog-list" id="article-cards-container" role="status" aria-live="polite">
                    <!-- Loaded dynamically via JavaScript -->
                </div>
                <div id="pagination-controls" style="text-align: center; padding: 20px;"></div>
            </div>
 
            <!-- VIEW 3: Quality Stats Chart -->
            <div id="content-quality" class="tab-content">
                <div class="quality-chart-section">
                    <div class="quality-chart-title">Avg Quality Score &amp; Accept Rate — By Source</div>
                    <div id="quality-chart-container">
                        <!-- Rendered by JS from qualityStats -->
                    </div>
                </div>
            </div>
 
            <!-- VIEW 4: Repair History -->
            <div id="content-repairs" class="tab-content">
                <div class="repair-list" id="repair-history-container" role="status" aria-live="polite">
                    <!-- Loaded by JS from /api/repairs -->
                </div>
            </div>
        </div>
        
        <!-- Specimen Restoration Modal Drawer -->
        <div class="modal-overlay" id="modal-overlay">
            <div class="modal-content">
                <div class="modal-header">
                    <h2 id="modal-title" class="modal-title-serif">Specimen Reconstruction</h2>
                    <button class="modal-close" id="modal-close-btn" aria-label="Close modal">&times;</button>
                </div>
                <div class="modal-body">
                    <!-- Provenance Metric Rules -->
                    <div class="metrics-panel">
                        <div class="metric-bar-container">
                            <div class="metric-bar-header">
                                <span>Length Metric</span>
                                <span id="val-length">0</span>
                            </div>
                            <div class="metric-bar-bg">
                                <div class="metric-bar-fill" id="bar-length" style="width: 0%"></div>
                            </div>
                        </div>
                        <div class="metric-bar-container">
                            <div class="metric-bar-header">
                                <span>Readability Index</span>
                                <span id="val-readability">0</span>
                            </div>
                            <div class="metric-bar-bg">
                                <div class="metric-bar-fill" id="bar-readability" style="width: 0%"></div>
                            </div>
                        </div>
                        <div class="metric-bar-container">
                            <div class="metric-bar-header">
                                <span>Structural Integrity</span>
                                <span id="val-structure">0</span>
                            </div>
                            <div class="metric-bar-bg">
                                <div class="metric-bar-fill" id="bar-structure" style="width: 0%"></div>
                            </div>
                        </div>
                        <div class="metric-bar-container">
                            <div class="metric-bar-header">
                                <span>Source Authority</span>
                                <span id="val-authority">0</span>
                            </div>
                            <div class="metric-bar-bg">
                                <div class="metric-bar-fill" id="bar-authority" style="width: 0%"></div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Kintsugi Restoration Panels -->
                    <div class="diff-panel">
                        <div class="diff-column">
                            <div class="diff-title" style="color: var(--rust-terracotta)">Damaged State (Raw Web Extraction)</div>
                            <div class="diff-box raw" id="diff-raw"></div>
                        </div>
                        
                        <div class="kintsugi-vertical-divider">
                            <svg class="vertical-seam-svg" viewBox="0 0 10 100" preserveAspectRatio="none">
                                <path d="M5,0 L3,10 L7,20 L4,30 L8,45 L2,60 L6,75 L3,90 L5,100" stroke="var(--gold-seam)" stroke-width="1.5" fill="none" class="modal-seam-path" />
                            </svg>
                        </div>
                        
                        <div class="diff-column">
                            <div class="diff-title" style="color: var(--verdigris-green)">Restored Segment (Curated Markdown)</div>
                            <div class="diff-box clean" id="diff-clean"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Live status screen reader notifications container -->
        <div id="toast-container" role="status" aria-live="polite"></div>
        """