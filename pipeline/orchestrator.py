import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, List

from pipeline.cleaner import Cleaner
from pipeline.deduplicator import Deduplicator
from pipeline.quality_scorer import QualityScorer
from pipeline.exporter import Exporter
from pipeline.utils import ensure_directories, PROJECT_ROOT
from monitoring.logger import StructuredLogger
from monitoring.telemetry import ARTICLES_EXTRACTED_TOTAL

def run_etl_stage(
    collector_id: str,
    raw_data: List[Dict[str, Any]],
    cleaner: Cleaner,
    deduplicator: Deduplicator,
    scorer: QualityScorer,
    exporter: Exporter,
    logger: StructuredLogger,
    persist_intermediate: bool = True
) -> Dict[str, Any]:
    """
    Orchestrates the pipeline processing flow for a batch of raw articles:
    Clean -> Deduplicate -> Quality Score -> Filter -> Export -> Log.
    
    Optionally persists intermediate JSON artifacts to data/ directories.
    Returns a dictionary of the scoring and processing outcomes.
    """
    ensure_directories()
    
    t_clean_start = time.perf_counter()
    # 1. Clean
    logger.log("INFO", "Cleaning articles (boilerplate & html removal)...")
    cleaned_data: List[Dict[str, Any]] = []
    for article in raw_data:
        try:
            cleaned_data.append(cleaner.clean_article(article))
        except Exception as exc:
            title_summary = article.get("title", "Unknown") if isinstance(article, dict) else "Unknown"
            logger.log("WARNING", f"Skipping article due to cleaning error: {exc}", article_title=str(title_summary)[:40])

    if persist_intermediate:
        cleaned_path = PROJECT_ROOT / "data/cleaned" / f"{collector_id}.json"
        with open(cleaned_path, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, indent=2)
        logger.log("INFO", f"Saved cleaned data ({len(cleaned_data)} articles) to {cleaned_path}")
    t_clean_dur = round(time.perf_counter() - t_clean_start, 4)
        
    t_dedup_start = time.perf_counter()
    # 2. Deduplicate
    logger.log("INFO", "Performing exact & near-duplicate deduplication...")
    deduped_data, dedup_stats = deduplicator.deduplicate(cleaned_data)
    if persist_intermediate:
        deduped_path = PROJECT_ROOT / "data/deduplicated" / f"{collector_id}.json"
        with open(deduped_path, 'w', encoding='utf-8') as f:
            json.dump(deduped_data, f, indent=2)
        logger.log("INFO", f"Saved deduplicated data ({len(deduped_data)} articles) to {deduped_path}")
    t_dedup_dur = round(time.perf_counter() - t_dedup_start, 4)
        
    t_score_start = time.perf_counter()
    # 3. Score Quality
    logger.log("INFO", "Performing quality scoring...")
    scored_data, quality_stats = scorer.score_batch(deduped_data)
    if persist_intermediate:
        scored_path = PROJECT_ROOT / "data/scored" / f"{collector_id}.json"
        with open(scored_path, 'w', encoding='utf-8') as f:
            json.dump(scored_data, f, indent=2)
        logger.log("INFO", f"Saved scored data to {scored_path}")
    t_score_dur = round(time.perf_counter() - t_score_start, 4)
        
    t_export_start = time.perf_counter()
    # 4. Filter and Export
    logger.log("INFO", "Filtering articles by quality score and exporting...")
    # Use QualityScorer.ACCEPT_THRESHOLD for filtering
    threshold = getattr(QualityScorer, "ACCEPT_THRESHOLD", 50.0)
    accepted_data: List[Dict[str, Any]] = [a for a in scored_data if a.get("quality_score", 0) >= threshold]
    rejected_data: List[Dict[str, Any]] = [a for a in scored_data if a.get("quality_score", 0) < threshold]
    
    export_filename = f"{collector_id}_training.jsonl"
    exporter.export_to_jsonl(accepted_data, export_filename)
    logger.log("INFO", f"ETL stage completed. Exported {len(accepted_data)} items.")
    ARTICLES_EXTRACTED_TOTAL.labels(collector_id=collector_id).inc(len(accepted_data))
    t_export_dur = round(time.perf_counter() - t_export_start, 4)
    
    # 5. Log metrics
    logger.log("INFO", "Export accepted", scraper_id=collector_id, count=len(accepted_data), filename=export_filename)
    logger.log("INFO", "Export rejected", scraper_id=collector_id, count=len(rejected_data))
    
    logger.log("INFO", "Pipeline completed", scraper_id=collector_id,
               input_rows=dedup_stats["input"],
               exact_removed=dedup_stats["exact_removed"],
               semantic_removed=dedup_stats["semantic_removed"],
               rows_after_dedup=dedup_stats["output"],
               total_scored=quality_stats["total"],
               rejection_rate_pct=quality_stats["rejection_rate_pct"],
               total_clean_exported=len(accepted_data),
               duration_clean_sec=t_clean_dur,
               duration_dedup_sec=t_dedup_dur,
               duration_score_sec=t_score_dur,
               duration_export_sec=t_export_dur)
               
    return {
        "raw_data": raw_data,
        "cleaned_data": cleaned_data,
        "deduped_data": deduped_data,
        "scored_data": scored_data,
        "accepted_data": accepted_data,
        "rejected_data": rejected_data,
        "quality_stats": quality_stats,
        "dedup_stats": dedup_stats
    }
