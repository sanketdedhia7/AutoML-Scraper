HEALING_STYLES = r"""            /* View 1: Ledger of Scraper Records */
            .ledger-records-list {
                display: flex;
                flex-direction: column;
                gap: 30px;
            }
            .ledger-record {
                border: 1px solid var(--border-ledger);
                background-color: #151211;
                padding: 24px;
                border-radius: 2px;
                position: relative;
                transition: transform 0.45s var(--kintsugi-ease), box-shadow 0.45s var(--kintsugi-ease);
            }
            .ledger-record.newly-healed {
                animation: micro-bounce 550ms var(--kintsugi-ease);
            }
            
            @keyframes micro-bounce {
                0%, 100% { transform: scale(1); }
                40% { transform: scale(1.035); }
                70% { transform: scale(0.985); }
            }
            
            .record-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 1px dashed var(--border-ledger);
                padding-bottom: 12px;
                margin-bottom: 16px;
            }
            .record-title-group {
                display: flex;
                align-items: center;
                gap: 12px;
            }
            .record-num {
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.95rem;
                color: var(--parchment-white);
            }
            .record-narrative-status {
                font-family: 'Newsreader', serif;
                font-style: italic;
                font-size: 0.95rem;
                font-weight: 600;
            }
            .record-narrative-status.healthy { color: var(--verdigris-green); }
            .record-narrative-status.unhealthy { color: var(--rust-terracotta); }
            .record-narrative-status.error { color: var(--rust-terracotta); }
            .record-narrative-status.healing { color: var(--gold-seam); }
            
            .record-meta-group {
                display: flex;
                gap: 20px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.75rem;
                color: var(--dust-grey);
            }
            .record-body {
                font-family: 'Newsreader', serif;
                font-size: 1.15rem;
                color: var(--parchment-white);
            }
            
            /* Status Badge */
            .status-badge {
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.75rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.06em;
                padding: 4px 10px;
                border-radius: 2px;
                flex-shrink: 0;
            }
            .status-badge.healthy  { background: rgba(91,130,102,0.18); color: var(--verdigris-green); border: 1px solid var(--verdigris-green); }
            .status-badge.unhealthy{ background: rgba(173,77,55,0.18); color: var(--rust-terracotta); border: 1px solid var(--rust-terracotta); }
            .status-badge.error    { background: rgba(173,77,55,0.12); color: var(--rust-terracotta); border: 1px dashed var(--rust-terracotta); }
            .status-badge.healing  { background: rgba(207,167,62,0.18); color: var(--gold-seam); border: 1px solid var(--gold-seam); }

            .record-id-group {
                display: flex;
                flex-direction: column;
                gap: 2px;
            }
            .record-display-name {
                font-family: 'Newsreader', serif;
                font-size: 1.05rem;
                font-weight: 500;
                color: var(--parchment-white);
            }
            .record-num {
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.75rem;
                color: var(--dust-grey);
            }
            
            /* Meta pills */
            .meta-pill {
                background: #1e1b1a;
                border: 1px solid var(--border-ledger);
                border-radius: 2px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.72rem;
                padding: 3px 8px;
                color: var(--dust-grey);
                white-space: nowrap;
            }
            .url-pill {
                max-width: 200px;
                overflow: hidden;
                text-overflow: ellipsis;
                display: inline-block;
            }
            
            /* Ops filter bar */
            .ops-filter-bar {
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
                flex-wrap: wrap;
                background-color: #1a1716;
                padding: 4px 0 10px 0;
            }
            .ops-filter-bar select, .ops-filter-bar input {
                background-color: #151211;
                border: 1px solid var(--border-ledger);
                color: var(--parchment-white);
                padding: 8px 14px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.8rem;
                border-radius: 2px;
                cursor: pointer;
                transition: border-color 0.2s var(--kintsugi-ease), transform 0.2s var(--kintsugi-ease);
            }
            .ops-filter-bar select:focus, .ops-filter-bar input:focus {
                outline: none; border-color: var(--gold-seam);
            }
            .sort-btn {
                background: none;
                border: 1px solid var(--border-ledger);
                color: var(--dust-grey);
                padding: 8px 14px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.8rem;
                border-radius: 2px;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 6px;
                transition: border-color 0.2s var(--kintsugi-ease), color 0.2s var(--kintsugi-ease), transform 0.2s var(--kintsugi-ease);
                will-change: transform;
            }
            .sort-btn:hover, .sort-btn.active {
                border-color: var(--gold-seam);
                color: var(--parchment-white);
                transform: scale(1.02);
            }
            .sort-btn:active {
                transform: scale(0.97) !important;
            }
            .sort-arrow { font-size: 0.9rem; }

            /* Auto-refresh indicator */
            .auto-refresh-bar {
                display: flex;
                align-items: center;
                gap: 8px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.7rem;
                color: var(--dust-grey);
                margin-left: auto;
            }
            .refresh-dot {
                width: 7px;
                height: 7px;
                border-radius: 50%;
                background: var(--verdigris-green);
                opacity: 0.7;
            }
            @keyframes pulse {
                0%, 100% { opacity: 0.4; }
                50% { opacity: 1; }
            }
            .refresh-dot.pulsing { animation: pulse 1.8s ease-in-out infinite; }

            /* Quality chart */
            .quality-chart-section {
                margin-bottom: 28px;
            }
            .quality-chart-title {
                font-family: 'Newsreader', serif;
                font-style: italic;
                font-size: 1.1rem;
                color: var(--dust-grey);
                text-transform: uppercase;
                letter-spacing: 0.06em;
                margin-bottom: 16px;
            }
            .qchart-row {
                display: flex;
                align-items: center;
                gap: 14px;
                margin-bottom: 14px;
            }
            .qchart-label {
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.75rem;
                color: var(--dust-grey);
                width: 160px;
                flex-shrink: 0;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
            .qchart-bars {
                flex: 1;
                display: flex;
                height: 18px;
                border-radius: 2px;
                overflow: hidden;
                background: var(--border-ledger);
            }
            .qchart-bar-accepted {
                background: var(--verdigris-green);
                height: 100%;
                transition: width 1s ease-out;
            }
            .qchart-bar-rejected {
                background: var(--rust-terracotta);
                opacity: 0.6;
                height: 100%;
                transition: width 1s ease-out;
            }
            .qchart-avg {
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.75rem;
                color: var(--gold-seam);
                width: 60px;
                flex-shrink: 0;
                text-align: right;
            }

            /* Repair history */
            .repair-list {
                display: flex;
                flex-direction: column;
                gap: 16px;
            }
            .repair-card {
                border: 1px solid var(--border-ledger);
                background: #151211;
                padding: 20px 24px;
                border-radius: 2px;
                transition: transform 0.25s var(--kintsugi-ease);
            }
            .repair-card:hover {
                transform: translateY(-2px);
            }
            .repair-card-header {
                display: flex;
                align-items: center;
                gap: 12px;
                margin-bottom: 12px;
            }
            .repair-status-pill {
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.72rem;
                padding: 3px 9px;
                border-radius: 2px;
                font-weight: 700;
                text-transform: uppercase;
                flex-shrink: 0;
            }
            .repair-status-pill.success  { background: rgba(91,130,102,0.2);  color: var(--verdigris-green); border: 1px solid var(--verdigris-green); }
            .repair-status-pill.awaiting_approval { background: rgba(207,167,62,0.12); color: var(--gold-seam); border: 1px solid var(--gold-seam); }
            .repair-status-pill.error    { background: rgba(173,77,55,0.15); color: var(--rust-terracotta); border: 1px solid var(--rust-terracotta); }
            .repair-card-meta {
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.72rem;
                color: var(--dust-grey);
            }
            .repair-card-issue {
                font-family: 'Newsreader', serif;
                font-size: 1.05rem;
                color: var(--parchment-white);
                margin-bottom: 10px;
                font-style: italic;
            }
            .repair-diff-block {
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.78rem;
                background: #0f0d0c;
                border: 1px solid var(--border-ledger);
                border-left: 3px solid var(--gold-seam);
                padding: 12px 16px;
                white-space: pre-wrap;
                color: var(--dust-grey);
                max-height: 160px;
                overflow-y: auto;
                border-radius: 1px;
                margin-top: 8px;
            }
            .repair-prompt-snippet {
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.72rem;
                color: var(--dust-grey);
                margin-top: 8px;
                opacity: 0.7;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            
            .record-error-box {
                margin-top: 16px;
                padding: 12px;
                background-color: rgba(173, 77, 55, 0.05);
                border-left: 2px solid var(--rust-terracotta);
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.8rem;
                list-style: none;
                color: var(--parchment-white);
            }
            .kintsugi-stepper {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin: 16px 0;
                padding: 10px 16px;
                background-color: rgba(255, 255, 255, 0.01);
                border: 1px solid var(--border-ledger);
                position: relative;
            }
            .kintsugi-stepper::before {
                content: '';
                position: absolute;
                top: 21px; /* aligns with center of step dots */
                left: 40px;
                right: 40px;
                height: 1px;
                background-color: var(--border-ledger);
                z-index: 1;
            }
            .step-segment {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 6px;
                z-index: 2;
                position: relative;
                flex: 1;
            }
            .step-dot {
                width: 12px;
                height: 12px;
                border-radius: 50%;
                background-color: #181514;
                border: 2px solid var(--border-ledger);
                transition: all 0.3s ease;
            }
            .step-label {
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.65rem;
                color: var(--dust-grey);
                text-transform: uppercase;
                letter-spacing: 0.05em;
                transition: all 0.3s ease;
            }
            .step-segment.active .step-dot {
                background-color: var(--gold-seam);
                border-color: var(--gold-seam);
                box-shadow: 0 0 6px rgba(207, 167, 62, 0.5);
            }
            .step-segment.active .step-label {
                color: var(--parchment-white);
                font-weight: 600;
            }
            
            /* Custom Kintsugi SVG Seams */
            .kintsugi-horizontal-seam {
                margin: 20px 0 10px 0;
                height: 16px;
                width: 100%;
                overflow: hidden;
            }
            .seam-svg {
                width: 100%;
                height: 100%;
            }
            @keyframes drawSeam {
                from { stroke-dashoffset: 200; }
                to { stroke-dashoffset: 0; }
            }
            .seam-path {
                stroke-dasharray: 200;
                stroke-dashoffset: 200;
                animation: drawSeam 2.5s var(--kintsugi-ease) forwards;
            }
            .modal-seam-path {
                stroke-dasharray: 200;
                stroke-dashoffset: 200;
                will-change: stroke-dashoffset;
            }
            .modal-seam-path.animate {
                animation: drawSeam 450ms var(--kintsugi-ease) forwards;
            }
            
            /* View 2: Specimen Catalog */
            .catalog-controls {
                display: flex;
                gap: 16px;
                margin-bottom: 24px;
                background-color: #1a1716;
                padding: 4px 0 10px 0;
                flex-wrap: wrap;
            }
            .catalog-search {
                flex: 2;
                min-width: 250px;
                background-color: #151211;
                border: 1px solid var(--border-ledger);
                color: var(--parchment-white);
                padding: 12px 18px;
                font-family: inherit;
                font-size: 0.95rem;
                border-radius: 2px;
                transition: border-color 0.25s var(--kintsugi-ease), transform 0.2s var(--kintsugi-ease);
            }
            .catalog-search:focus {
                outline: none;
                border-color: var(--gold-seam);
            }
            .catalog-select {
                flex: 1;
                min-width: 140px;
                background-color: #151211;
                border: 1px solid var(--border-ledger);
                color: var(--parchment-white);
                padding: 12px 18px;
                font-family: inherit;
                font-size: 0.95rem;
                border-radius: 2px;
                cursor: pointer;
                transition: border-color 0.25s var(--kintsugi-ease), transform 0.2s var(--kintsugi-ease);
            }
            .catalog-select:focus {
                outline: none;
                border-color: var(--gold-seam);
            }
            
            .catalog-list {
                display: flex;
                flex-direction: column;
                border: 1px solid var(--border-ledger);
                background-color: #151211;
                border-radius: 2px;
            }
            .catalog-row {
                display: flex;
                align-items: center;
                border-bottom: 1px solid var(--border-ledger);
                padding: 18px 24px;
                cursor: pointer;
                transition: background-color 0.25s var(--kintsugi-ease), transform 0.25s var(--kintsugi-ease), box-shadow 0.25s var(--kintsugi-ease);
                will-change: transform, box-shadow;
            }
            .catalog-row:last-child {
                border-bottom: none;
            }
            .catalog-row:hover {
                background-color: #1e1a19;
                transform: scale(1.015);
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
            }
            .catalog-row:active {
                transform: scale(0.99);
            }
            
            /* Provenance Stamp styling */
            .provenance-stamp {
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.8rem;
                border: 1px solid var(--border-ledger);
                padding: 6px 12px;
                border-radius: 2px;
                text-align: center;
                width: 140px;
                margin-right: 24px;
                flex-shrink: 0;
                transition: border-color 0.2s var(--kintsugi-ease);
            }
            .provenance-stamp.excellent {
                border-color: var(--verdigris-green);
                color: var(--verdigris-green);
            }
            .provenance-stamp.rejected {
                border-color: var(--rust-terracotta);
                color: var(--rust-terracotta);
            }
            
            .specimen-info {
                flex: 1;
                min-width: 0;
            }
            .specimen-title {
                font-family: 'Newsreader', serif;
                font-size: 1.25rem;
                color: var(--parchment-white);
                margin-bottom: 4px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            .specimen-author {
                font-size: 0.85rem;
                color: var(--dust-grey);
            }
            .specimen-reasoning-trail {
                display: flex;
                align-items: center;
                gap: 6px;
                flex-wrap: wrap;
                margin-top: 6px;
            }
            .trail-badge {
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.68rem;
                padding: 2px 7px;
                border-radius: 2px;
                border: 1px solid var(--border-ledger);
                background-color: rgba(255, 255, 255, 0.02);
                color: var(--dust-grey);
            }
            .trail-badge.lang {
                border-color: rgba(207, 167, 62, 0.3);
                color: var(--gold-seam);
            }
            .trail-badge.pii {
                border-color: rgba(91, 130, 102, 0.4);
                color: var(--verdigris-green);
                background: rgba(91, 130, 102, 0.08);
            }
            .trail-badge.dedup {
                border-color: rgba(207, 167, 62, 0.4);
                color: var(--gold-seam);
                background: rgba(207, 167, 62, 0.08);
            }
            .trail-badge.reason {
                border-color: rgba(173, 77, 55, 0.4);
                color: var(--rust-terracotta);
                background: rgba(173, 77, 55, 0.08);
            }
            
            /* Metric Card Sparkline & Trend Styling */
            .yield-sparkline-container {
                margin-top: 8px;
                display: flex;
                flex-direction: column;
                gap: 4px;
            }
            .yield-sparkline {
                width: 100%;
                height: 22px;
                overflow: visible;
            }
            .mini-balance-bar {
                width: 100%;
                height: 6px;
                background-color: rgba(173, 77, 55, 0.2);
                border-radius: 1px;
                overflow: hidden;
                position: relative;
            }
            .bar-segment.clean {
                height: 100%;
                background-color: var(--verdigris-green);
            }
            .sparkline-trend-text {
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.68rem;
                color: var(--dust-grey);
                text-transform: uppercase;
                letter-spacing: 0.04em;
            }
            .sparkline-trend-text.green { color: var(--verdigris-green); }
            .sparkline-trend-text.gold { color: var(--gold-seam); }
            .sparkline-trend-text.rust { color: var(--rust-terracotta); }
            .stepper-latency-badge {
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.7rem;
                padding: 3px 8px;
                border-radius: 2px;
                border: 1px solid var(--gold-seam);
                background: rgba(207, 167, 62, 0.1);
                color: var(--gold-seam);
                margin-left: 8px;
                white-space: nowrap;
            }
            
            .specimen-meta {
                display: flex;
                align-items: center;
                gap: 24px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.8rem;
                color: var(--dust-grey);
                margin-left: 24px;
            }
            .specimen-source {
                border: 1px solid var(--border-ledger);
                padding: 2px 8px;
                font-size: 0.7rem;
            }
            .specimen-link {
                font-family: 'Newsreader', serif;
                font-style: italic;
                color: var(--gold-seam);
                text-decoration: none;
            }
            
"""
