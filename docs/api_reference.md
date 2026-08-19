# API Reference Guide

This document lists classes and methods across modules in the AutoML Data Curator.

## 1. Scraper Management (`scrapers`)

### `ScraperManager`
- `create_scraper(config_path: str) -> dict`: Reads collector configurations and initializes collectors on Bright Data.
- `list_scrapers() -> list`: Returns active collectors list.
- `get_scraper_output(collector_id: str) -> list`: Retrieves latest raw JSON arrays.

---

## 2. ETL Processing (`pipeline`)

### `ScraperRunner`
- `trigger_scraper(collector_id: str) -> dict`: Triggers run execution command.
- `wait_for_completion(collector_id: str, timeout: int = 300) -> list`: Blocks and polls status until completion or timeout.

### `Validator`
- `validate(data: list) -> dict`: Inspects keys, empty datasets, and minimum thresholds.

### `Cleaner`
- `clean_article(article: dict) -> dict`: Iterates article keys to clean titles and convert HTML body to Markdown text.
- `clean_text(text: str) -> str`: Regular expression filters for common web page navigation footer links, cookie text, and headers.

### `Deduplicator`
- `deduplicate(articles: list) -> list`: Checks for exact matching URLs and runs cosine similarity comparison over text embeddings.

### `QualityScorer`
- `score_article(article: dict) -> dict`: Computes structural completeness, sentence readability averages, and source domain reputation.

### `Exporter`
- `export_to_jsonl(articles: list, filename: str) -> Path`: Serializes list items into valid `.jsonl` files formatted for LLM training inputs.

---

## 3. Healing API (`healing`)

### `Healer`
- `trigger_self_healing(collector_id: str, issue_description: str) -> dict`: Instructs Scraper Studio to self-correct selector mappings.

---

## 4. Monitoring (`monitoring`)

### `HealthChecker`
- `check_scraper_health(collector_id: str) -> dict`: Performs dry validation runs over collector outputs.
- `check_all_scrapers(collector_ids: list) -> dict`: Iterates and aggregates status report dictionary.
