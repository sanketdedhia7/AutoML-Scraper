# AutoML Data Curator

An automated data curation pipeline for LLM training that scrapes domain-specific websites using Bright Data Scraper Studio, validates inputs, cleans boilerplate, deduplicates (exact + near-duplicate semantic check), scores content quality, self-heals layouts, and exports to JSONL format.

## Features
- **Scraper Studio Integration**: Managed scrapers for legal, medical, and scientific resources.
- **Validation & Self-Healing**: Automated health status check, self-healing prompt generation, and repair logs.
- **ETL Pipeline**: Boilerplate removal, exact & near-duplicate detection via embeddings, heuristic quality scoring.
- **Monitoring Dashboard**: FastAPI web dashboard displaying health, last runs, articles count, validation warnings, and Discord notifications.

## Installation

1. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Or venv\Scripts\activate on Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables in `.env`:
   - `BRIGHT_DATA_API_KEY`
   - `BRIGHT_DATA_ORG_ID`
   - `DISCORD_WEBHOOK_URL` (optional)

## Usage

- **Initialize scrapers**: `python scripts/setup_scrapers.py`
- **Run the pipeline**: `python scripts/run_pipeline.py`
- **Export training data**: `python scripts/export_training_data.py`
- **Run the dashboard**: `python run_server.py` (Recommended entrypoint, handles port cleanup)
  - *Alternative backward-compat shim*: `uvicorn monitoring.dashboard:app --host 0.0.0.0 --port 8000`

## Scraper Studio Self-Healing Demo

We have built a layout break-and-heal simulation to verify how our system triggers Scraper Studio's self-healing.

### Keyword-Based Simulated Failure (Controlled Demo)
For demonstration and testing purposes when operating in Mock Mode, the scraper utilizes keyword-based simulated breaks. Submitting target URLs containing any of the keywords `"fail"`, `"drift"`, `"error"`, or `"unhealthy"` will force a simulated extraction failure, dynamically routing the workflow through the healer and fallback pathways. In production and under live mode, breaks are detected organically via strict validation safeguards checking field missing rates.

To run the script-driven break-and-heal demo:
```bash
python scripts/demo_break_heal.py
```

### How Self-Healing Works

This project separates concerns between our validator and Scraper Studio's platform features:
1. **Scraper Studio platform handles**: Code updates and selector generation in the cloud using the real `brightdata scraper heal <id> "<prompt>"` CLI command.
2. **Our Pipeline handles**:
   - **Validation Checks**: Catching *when* to heal by checking for empty outputs or high missing field rates (>30%).
   - **Diagnostic Generation**: Translating validation issues (e.g. empty fields) into descriptive plain-English prompts.
   - **Automated Commit**: Executing `brightdata scraper approve <id>` to commit selector repairs.
   - **Discord Notification**: Sending alerts through the entire heal lifecycle (Break detected → Repair triggered → Approved → Pipeline resumed).
