# Project Demo Walkthrough Script

This script outlines the step-by-step sequence to showcase the AutoML Data Curator's main capabilities.

## Setup Phase
1. Show structure: `tree /F` or equivalent listing commands.
2. Verify `.env` config credentials are correct.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Demonstration Step 1: Initializing Scrapers
- Command:
  ```bash
  python scripts/setup_scrapers.py
  ```
- Output to Highlight: Output showing configs `legal_blog_scraper`, `medical_journal_scraper`, and `arxiv_scraper` being read and created with new collector IDs.

## Demonstration Step 2: Running the Pipeline & Validation Failures
- Command:
  ```bash
  python scripts/run_pipeline.py
  ```
- Behaviors to Highlight:
  - Triggering scraper runs.
  - Mock validators logging validation results.
  - Logging of healing actions to `data/repairs/` and mock self-healing trigger.
  - Writing raw, cleaned, deduplicated, and scored intermediate JSON files to their directories.
  - Writing LLM training JSONL files to `data/exports/`.

## Demonstration Step 3: Combined Training Data Export
- Command:
  ```bash
  python scripts/export_training_data.py
  ```
- Output to Highlight: Merged and filtered output showing items exceeding the quality score threshold written into `data/exports/combined_training_data.jsonl`.

## Demonstration Step 4: Health Check & Web Dashboard
- Command:
  ```bash
  uvicorn monitoring.dashboard:app --host 127.0.0.1 --port 8000
  ```
- Browser Navigation: Open `http://127.0.0.1:8000` in the browser to view the dark-mode dashboard showing statuses, counts of extracted articles, and validation reports.
