NAVIGATION_STYLES = r"""            /* Sticky Navigation and Controls wrapping */
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
            
"""
