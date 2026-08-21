UTILITY_STYLES = r"""            /* Media Queries for Mobile & Tablet Responsiveness */
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
