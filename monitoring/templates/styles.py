DASHBOARD_STYLES = """
            :root {
                --bg-charcoal: #181514;
                --gold-seam: #cfa73e;
                --verdigris-green: #5b8266;
                --rust-terracotta: #ad4d37;
                --parchment-white: #ebdcc5;
                --dust-grey: #8d8073;
                --border-ledger: #2e2825;
                --kintsugi-ease: cubic-bezier(0.16, 1, 0.3, 1);
                --kintsugi-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);
            }
            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }
            body {
                font-family: system-ui, -apple-system, sans-serif;
                background-color: var(--bg-charcoal);
                color: var(--parchment-white);
                min-height: 100vh;
                line-height: 1.6;
                padding: 40px 20px;
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            
            /* Ledger Container */
            .ledger-container {
                width: 100%;
                max-width: 1050px;
                background-color: #1a1716;
                border: 4px double var(--border-ledger);
                border-radius: 2px;
                padding: 40px;
                box-shadow: 0 12px 40px rgba(0, 0, 0, 0.6);
            }
            
            /* Header Section */
            .ledger-header {
                border-bottom: 1px solid var(--border-ledger);
                padding-bottom: 24px;
                margin-bottom: 40px;
            }
            .ledger-meta {
                display: flex;
                justify-content: space-between;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.8rem;
                color: var(--dust-grey);
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 12px;
            }
            .ledger-title {
                font-family: 'Newsreader', serif;
                font-weight: 500;
                font-size: 2.6rem;
                font-style: italic;
                line-height: 1.2;
                color: var(--parchment-white);
                margin-bottom: 8px;
            }
            .ledger-subtitle {
                font-family: system-ui, -apple-system, sans-serif;
                font-size: 0.95rem;
                color: var(--dust-grey);
                text-transform: uppercase;
                letter-spacing: 0.08em;
            }
            
            /* Sticky Navigation and Controls wrapping */
            .sticky-header-container {
                position: sticky;
                top: 0;
                z-index: 100;
                background-color: rgba(26, 23, 22, 0.9);
                backdrop-filter: blur(10px);
                will-change: transform, backdrop-filter;
                transform: translateZ(0);
                padding-top: 10px;
                margin-bottom: 30px;
                border-bottom: 1px solid var(--border-ledger);
            }
            
            /* Tabs Navigation */
            .ledger-tabs {
                display: flex;
                gap: 10px;
                padding-bottom: 1px;
            }
            
            /* On-Demand Bar */
            .ondemand-bar {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px 0 8px 0;
            }
            .ondemand-input {
                flex: 1;
                background: #12100f;
                border: 1px solid var(--border-ledger);
                color: var(--parchment-white);
                padding: 10px 16px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.88rem;
                border-radius: 2px;
                outline: none;
                transition: border-color 0.25s var(--kintsugi-ease);
            }
            .ondemand-input:focus {
                border-color: var(--gold-seam);
                box-shadow: 0 0 0 2px rgba(207, 167, 62, 0.2);
            }
            .ondemand-btn {
                background: var(--gold-seam);
                color: #12100f;
                border: none;
                padding: 10px 20px;
                font-family: system-ui, -apple-system, sans-serif;
                font-weight: 600;
                font-size: 0.9rem;
                cursor: pointer;
                border-radius: 2px;
                transition: background-color 0.2s var(--kintsugi-ease), transform 0.2s var(--kintsugi-ease);
            }
            .ondemand-btn:hover {
                background-color: #dfb84f;
                transform: scale(1.02);
            }
            .ondemand-btn:active {
                transform: scale(0.97);
            }
            .ondemand-btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }
            .ondemand-badge {
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.8rem;
                padding: 6px 12px;
                border-radius: 2px;
                background: #25201d;
                border: 1px solid var(--gold-seam);
                color: var(--gold-seam);
            }
            .tab-button {
                background: none;
                border: 1px solid transparent;
                border-bottom: none;
                color: var(--dust-grey);
                padding: 12px 24px;
                font-family: 'Newsreader', serif;
                font-size: 1.15rem;
                font-style: italic;
                cursor: pointer;
                border-radius: 2px 2px 0 0;
                position: relative;
                transition: color 0.25s var(--kintsugi-ease), transform 0.2s var(--kintsugi-ease);
                will-change: transform;
            }
            .tab-button:hover {
                color: var(--parchment-white);
                transform: scale(1.02);
            }
            .tab-button:active {
                transform: scale(0.97) !important;
            }
            .tab-button.active {
                color: var(--parchment-white);
                border-color: var(--border-ledger);
                background-color: #1a1716;
                margin-bottom: -2px;
                font-weight: 500;
            }
            .tab-button.active::after {
                content: "";
                position: absolute;
                bottom: -2px;
                left: 0;
                right: 0;
                height: 3px;
                background-color: var(--gold-seam);
            }
            
            /* Mending Summary Banner */
            .yield-box {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 20px;
                border: 1px solid var(--border-ledger);
                background-color: #151211;
                padding: 24px;
                margin-bottom: 40px;
                border-radius: 2px;
            }
            .yield-item {
                border-right: 1px solid var(--border-ledger);
                padding-right: 16px;
            }
            .yield-item:last-child {
                border-right: none;
            }
            .yield-label {
                font-family: system-ui, -apple-system, sans-serif;
                font-size: 0.75rem;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                color: var(--dust-grey);
                margin-bottom: 6px;
            }
            .yield-value {
                font-family: 'JetBrains Mono', monospace;
                font-size: 1.6rem;
                font-weight: 600;
                color: var(--parchment-white);
            }
            
            /* Tab content management & animations */
            .tab-content {
                display: none;
                opacity: 0;
                transform: translateY(12px);
                will-change: opacity, transform;
            }
            .tab-content.active {
                display: block;
                animation: tabFadeIn 0.35s var(--kintsugi-ease) forwards;
            }
            
            @keyframes tabFadeIn {
                from {
                    opacity: 0;
                    transform: translateY(12px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            /* View 1: Ledger of Scraper Records */
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
            
            /* Inspection / Restoration Modal */
            .modal-overlay {
                display: none;
                position: fixed;
                inset: 0;
                background-color: rgba(24, 21, 20, 0.95);
                z-index: 1000;
                align-items: center;
                justify-content: center;
                opacity: 0;
                transition: opacity 0.3s var(--kintsugi-ease);
                will-change: opacity;
            }
            .modal-overlay.active {
                display: flex;
                opacity: 1;
            }
            .modal-content {
                background-color: #1a1716;
                border: 2px solid var(--border-ledger);
                width: 90vw;
                max-width: 1100px;
                max-height: 88vh;
                display: flex;
                flex-direction: column;
                box-shadow: 0 20px 50px rgba(0, 0, 0, 0.8);
                border-radius: 2px;
                transform: translateY(20px) scale(0.97);
                transition: transform 0.3s var(--kintsugi-ease);
                will-change: transform;
            }
            .modal-overlay.active .modal-content {
                transform: translateY(0) scale(1);
            }
            .modal-header {
                padding: 24px;
                border-bottom: 1px solid var(--border-ledger);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .modal-title-serif {
                font-family: 'Newsreader', serif;
                font-size: 1.5rem;
                font-style: italic;
                color: var(--parchment-white);
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                max-width: 90%;
            }
            .modal-close {
                background: none;
                border: none;
                color: var(--dust-grey);
                font-size: 2rem;
                cursor: pointer;
                padding: 0 8px;
                line-height: 1;
                transition: color 0.25s var(--kintsugi-ease), transform 0.25s var(--kintsugi-ease);
            }
            .modal-close:hover {
                color: var(--parchment-white);
                transform: scale(1.1);
            }
            .modal-close:active {
                transform: scale(0.95);
            }
            .modal-body {
                padding: 30px;
                overflow-y: auto;
                flex: 1;
            }
            
            /* Ledger Indicators for Scores */
            .metrics-panel {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 16px;
                margin-bottom: 30px;
            }
            .metric-bar-container {
                background-color: #151211;
                border: 1px solid var(--border-ledger);
                padding: 14px;
                border-radius: 2px;
            }
            .metric-bar-header {
                display: flex;
                justify-content: space-between;
                font-family: system-ui, -apple-system, sans-serif;
                font-size: 0.75rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                color: var(--dust-grey);
                margin-bottom: 8px;
            }
            .metric-bar-bg {
                background-color: var(--border-ledger);
                height: 4px;
                overflow: hidden;
            }
            .metric-bar-fill {
                height: 100%;
                background-color: var(--gold-seam);
                transition: width 1s ease-out;
            }
            
            /* Kintsugi Restoration Diff layout */
            .diff-panel {
                display: grid;
                grid-template-columns: 1fr 12px 1fr;
                gap: 10px;
                height: 420px;
            }
            .diff-column {
                display: flex;
                flex-direction: column;
                height: 100%;
                min-width: 0;
            }
            .diff-title {
                font-family: 'Newsreader', serif;
                font-style: italic;
                font-size: 1rem;
                margin-bottom: 12px;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
            .diff-box {
                background-color: #151211;
                border: 1px solid var(--border-ledger);
                padding: 20px;
                flex: 1;
                overflow-y: auto;
                border-radius: 2px;
            }
            .diff-box.raw {
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.8rem;
                color: var(--dust-grey);
                opacity: 0.8;
                border-color: var(--border-ledger);
            }
            .diff-box.clean {
                font-family: 'Newsreader', serif;
                font-size: 1.15rem;
                color: var(--parchment-white);
                line-height: 1.6;
            }
            
            /* Gold Seam Divider in Modal */
            .kintsugi-vertical-divider {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100%;
            }
            .vertical-seam-svg {
                width: 100%;
                height: 100%;
            }
            
            /* Highlighting elements */
            .highlight-ad {
                background-color: rgba(173, 77, 55, 0.15);
                border: 1px dashed var(--rust-terracotta);
                color: var(--rust-terracotta);
                padding: 2px 4px;
            }
            
            /* Keyboard Focus Accessibility with gold seams */
            .tab-button:focus-visible, 
            .catalog-search:focus-visible,
            .catalog-select:focus-visible,
            .modal-close:focus-visible,
            .heal-trigger-btn:focus-visible,
            .heal-approve-btn:focus-visible,
            .demo-btn:focus-visible,
            .sort-btn:focus-visible {
                outline: 2px solid var(--gold-seam) !important;
                outline-offset: 2px !important;
            }
            
            /* Heal trigger & approval UI */
            .heal-trigger-btn {
                background: none;
                border: 1px solid var(--gold-seam);
                color: var(--gold-seam);
                font-family: 'Newsreader', serif;
                font-style: italic;
                font-size: 1rem;
                padding: 10px 20px;
                cursor: pointer;
                border-radius: 2px;
                transition: background-color 0.25s var(--kintsugi-ease), transform 0.2s var(--kintsugi-ease);
                will-change: transform;
            }
            .heal-trigger-btn:hover {
                background-color: rgba(207, 167, 62, 0.08);
                transform: scale(1.02);
            }
            .heal-trigger-btn:active {
                transform: scale(0.97) !important;
            }
            .demo-btn {
                background-color: var(--border-ledger);
                border: 1px solid var(--dust-grey);
                color: var(--parchment-white);
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.75rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                padding: 6px 12px;
                cursor: pointer;
                border-radius: 2px;
                transition: border-color 0.25s var(--kintsugi-ease), transform 0.2s var(--kintsugi-ease);
                will-change: transform;
            }
            .demo-btn:hover {
                border-color: var(--parchment-white);
                transform: scale(1.02);
            }
            .demo-btn:active {
                transform: scale(0.97) !important;
            }
            .heal-preview-panel {
                margin-top: 20px;
                border: 1px solid var(--gold-seam);
                background-color: rgba(207, 167, 62, 0.04);
                padding: 20px;
                border-radius: 2px;
                display: none;
            }
            .heal-preview-panel.visible { display: block; }
            .heal-preview-title {
                font-family: 'Newsreader', serif;
                font-style: italic;
                font-size: 1.15rem;
                color: var(--gold-seam);
                margin-bottom: 12px;
            }
            .heal-diff-summary {
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.8rem;
                color: var(--parchment-white);
                white-space: pre-wrap;
                background-color: #151211;
                border: 1px solid var(--border-ledger);
                padding: 14px;
                margin-bottom: 16px;
                border-left: 3px solid var(--gold-seam);
            }
            .heal-preview-result {
                font-family: 'Newsreader', serif;
                font-size: 1.05rem;
                color: var(--parchment-white);
                margin-bottom: 16px;
                line-height: 1.6;
            }
            .heal-approve-btn {
                background-color: var(--verdigris-green);
                border: none;
                color: var(--parchment-white);
                font-family: 'Newsreader', serif;
                font-style: italic;
                font-size: 1rem;
                padding: 10px 24px;
                cursor: pointer;
                border-radius: 2px;
                transition: transform 0.2s var(--kintsugi-ease), opacity 0.2s var(--kintsugi-ease);
                will-change: transform;
            }
            .heal-approve-btn:hover {
                opacity: 0.85;
                transform: scale(1.02);
            }
            .heal-approve-btn:active {
                transform: scale(0.97) !important;
            }
            .heal-status-msg {
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.85rem;
                margin-top: 10px;
                color: var(--dust-grey);
            }
            
            @keyframes spin { 100% { transform: rotate(360deg); } }
            button:disabled { opacity: 0.6; cursor: not-allowed; pointer-events: none; }

            /* Button Loading state indicator overlay spinner */
            .button-loading {
                position: relative;
                color: transparent !important;
                pointer-events: none;
            }
            .button-loading::after {
                content: "";
                position: absolute;
                width: 16px;
                height: 16px;
                top: 0; left: 0; right: 0; bottom: 0;
                margin: auto;
                border: 2px solid transparent;
                border-top-color: currentColor;
                border-radius: 50%;
                animation: button-spin 0.6s linear infinite;
            }
            @keyframes button-spin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }

            /* Toast Notification System */
            #toast-container {
                position: fixed;
                bottom: 24px;
                right: 24px;
                z-index: 9999;
                display: flex;
                flex-direction: column;
                gap: 10px;
                max-width: 400px;
                width: calc(100vw - 48px);
                pointer-events: none;
            }
            .toast-msg {
                pointer-events: auto;
                background-color: #1a1614;
                border: 1px solid var(--border-ledger);
                padding: 14px 18px;
                border-radius: 2px;
                box-shadow: 0 12px 36px rgba(0,0,0,0.8);
                display: flex;
                align-items: flex-start;
                gap: 12px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.82rem;
                color: var(--parchment-white);
                animation: toastIn 0.4s var(--kintsugi-bounce) forwards;
                transition: opacity 0.3s var(--kintsugi-ease), transform 0.3s var(--kintsugi-ease);
                will-change: transform, opacity;
            }
            .toast-msg.error { border-left: 4px solid var(--rust-terracotta); }
            .toast-msg.success { border-left: 4px solid var(--verdigris-green); }
            .toast-msg.info { border-left: 4px solid var(--gold-seam); }
            .toast-icon { font-size: 1.1rem; line-height: 1; }
            .toast-content { flex: 1; line-height: 1.4; word-break: break-word; }
            .toast-close {
                cursor: pointer;
                color: var(--dust-grey);
                font-size: 1.1rem;
                line-height: 1;
                background: none;
                border: none;
                padding: 0;
                transition: color 0.2s var(--kintsugi-ease);
            }
            .toast-close:hover { color: var(--parchment-white); }
            @keyframes toastIn {
                0% { opacity: 0; transform: translateY(20px) scale(0.95); }
                70% { transform: translateY(-2px) scale(1.02); }
                100% { opacity: 1; transform: translateY(0) scale(1); }
            }
            
            /* Skeleton shimmers */
            .skeleton-card {
                border: 1px solid var(--border-ledger);
                background: #151211;
                padding: 24px;
                border-radius: 2px;
                display: flex;
                align-items: center;
                height: 98px;
                position: relative;
                overflow: hidden;
                margin-bottom: 1px;
            }
            .skeleton-card::before {
                content: '';
                position: absolute;
                inset: 0;
                background: linear-gradient(
                    90deg,
                    rgba(255,255,255,0) 0%,
                    rgba(255,255,255,0.04) 50%,
                    rgba(255,255,255,0) 100%
                );
                animation: shimmer 1.5s infinite var(--kintsugi-ease);
                will-change: transform;
            }
            @keyframes shimmer {
                0% { transform: translateX(-100%); }
                100% { transform: translateX(100%); }
            }
            .skeleton-stamp {
                width: 140px;
                height: 38px;
                background-color: var(--border-ledger);
                margin-right: 24px;
                border-radius: 2px;
                flex-shrink: 0;
            }
            .skeleton-info {
                flex: 1;
                display: flex;
                flex-direction: column;
                gap: 8px;
            }
            .skeleton-title {
                width: 60%;
                height: 18px;
                background-color: var(--border-ledger);
                border-radius: 2px;
            }
            .skeleton-text {
                width: 30%;
                height: 12px;
                background-color: var(--border-ledger);
                border-radius: 2px;
            }
            .skeleton-meta {
                width: 180px;
                height: 14px;
                background-color: var(--border-ledger);
                border-radius: 2px;
                margin-left: 24px;
            }

            /* Beautiful Empty search states styling */
            .empty-state-panel {
                text-align: center;
                padding: 60px 40px;
                border: 1px dashed var(--border-ledger);
                background-color: #151211;
                border-radius: 2px;
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 16px;
            }
            .empty-state-icon {
                font-size: 3rem;
                color: var(--dust-grey);
            }
            .empty-state-title {
                font-family: 'Newsreader', serif;
                font-style: italic;
                font-size: 1.45rem;
                color: var(--parchment-white);
            }
            .empty-state-text {
                font-size: 0.92rem;
                color: var(--dust-grey);
                max-width: 440px;
                line-height: 1.5;
            }
            .empty-state-reset-btn {
                background: none;
                border: 1px solid var(--gold-seam);
                color: var(--gold-seam);
                font-family: 'Newsreader', serif;
                font-style: italic;
                font-size: 0.95rem;
                padding: 6px 16px;
                cursor: pointer;
                border-radius: 2px;
                transition: background-color 0.25s var(--kintsugi-ease), transform 0.2s var(--kintsugi-ease);
            }
            .empty-state-reset-btn:hover {
                background-color: rgba(207, 167, 62, 0.08);
                transform: scale(1.02);
            }
            .empty-state-reset-btn:active {
                transform: scale(0.97);
            }
            
            /* Media Queries for Mobile & Tablet Responsiveness */
            @media (max-width: 850px) {
                .yield-box {
                    grid-template-columns: repeat(2, 1fr);
                    gap: 15px;
                }
                .yield-item {
                    border-right: none;
                    border-bottom: 1px solid var(--border-ledger);
                    padding-bottom: 10px;
                }
                .yield-item:nth-child(even) {
                    border-bottom: none;
                }
                .catalog-row {
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 12px;
                }
                .provenance-stamp {
                    width: 100%;
                    margin-right: 0;
                }
                .specimen-meta {
                    margin-left: 0;
                    width: 100%;
                    justify-content: space-between;
                    border-top: 1px dashed var(--border-ledger);
                    padding-top: 8px;
                }
            }
            
            @media (max-width: 640px) {
                .modal-content {
                    width: 95vw;
                    max-height: 92vh;
                    margin: 10px;
                }
                .modal-header {
                    padding: 16px 18px;
                }
                .modal-body {
                    padding: 16px 12px;
                }
                .diff-panel {
                    grid-template-columns: 1fr;
                    grid-template-rows: auto auto auto;
                    height: auto;
                    gap: 12px;
                }
                .diff-box {
                    height: 180px;
                    max-height: 180px;
                    flex: none;
                }
                .kintsugi-vertical-divider {
                    height: 12px;
                    width: 100%;
                    transform: none;
                }
                .specimen-reasoning-trail {
                    flex-wrap: wrap;
                }
                .ledger-container {
                    padding: 16px 12px;
                }
                .ledger-header {
                    margin-bottom: 24px;
                }
                .ledger-meta {
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 12px;
                }
                .ledger-meta > div {
                    flex-direction: column;
                    align-items: flex-start;
                    width: 100%;
                    gap: 10px;
                }
                .ledger-title {
                    font-size: 1.8rem;
                }
                .ledger-tabs {
                    overflow-x: auto;
                    white-space: nowrap;
                    -webkit-overflow-scrolling: touch;
                    gap: 4px;
                }
                .tab-button {
                    padding: 10px 14px;
                    font-size: 0.85rem;
                }
                .yield-box {
                    grid-template-columns: 1fr;
                }
                .catalog-controls {
                    flex-direction: column;
                    gap: 10px;
                    position: static;
                    backdrop-filter: none;
                }
                .ops-filter-bar {
                    flex-direction: column;
                    align-items: stretch;
                    position: static;
                    backdrop-filter: none;
                }
                .catalog-search, .catalog-select {
                    width: 100%;
                }
                .metrics-panel {
                    grid-template-columns: 1fr;
                }
                .modal-content {
                    width: 96vw;
                    max-height: 94vh;
                }
                .modal-body {
                    padding: 16px;
                }
                #toast-container {
                    right: 12px;
                    bottom: 12px;
                    width: calc(100vw - 24px);
                }
                .sticky-header-container {
                    position: static;
                    backdrop-filter: none;
                    background-color: transparent;
                    padding-top: 0;
                    margin-bottom: 20px;
                }
            }
            
            /* Reduced Motion Media Query */
            @media (prefers-reduced-motion: reduce) {
                .seam-path, .modal-seam-path.animate {
                    animation: none !important;
                    stroke-dashoffset: 0 !important;
                }
                .skeleton-card::before {
                    animation: none !important;
                }
                .refresh-dot.pulsing {
                    animation: none !important;
                }
                * {
                    transition: none !important;
                    animation: none !important;
                    scroll-behavior: auto !important;
                }
                .sticky-header-container, .ops-filter-bar, .catalog-controls {
                    backdrop-filter: none !important;
                    background: rgba(26, 23, 22, 0.98) !important;
                }
            }
        """
