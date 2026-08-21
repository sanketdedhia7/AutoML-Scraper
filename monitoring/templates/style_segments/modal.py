MODAL_STYLES = r"""            /* Inspection / Restoration Modal */
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
                white-space: pre-wrap; /* Preserve newlines and markdown list structures */
            }
            .export-btn {
                background-color: var(--border-ledger);
                border: 1px solid var(--dust-grey);
                color: var(--parchment-white);
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.65rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                padding: 4px 8px;
                cursor: pointer;
                border-radius: 2px;
                transition: border-color 0.25s var(--kintsugi-ease), transform 0.2s var(--kintsugi-ease);
            }
            .export-btn:hover {
                border-color: var(--parchment-white);
                transform: scale(1.03);
            }
            .export-btn:active {
                transform: scale(0.97);
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
            
"""
