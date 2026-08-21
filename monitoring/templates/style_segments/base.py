BASE_STYLES = r"""
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
            
"""
