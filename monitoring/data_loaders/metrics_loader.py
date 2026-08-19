import json
import logging
from pipeline.utils import PROJECT_ROOT
import monitoring.data_loaders

def _open(*args, **kwargs):
    return monitoring.data_loaders.open(*args, **kwargs)

def get_impact_metrics() -> dict:
    """Read pipeline logs to compute deduplication savings, rejection rate, latency, and export count."""
    log_file = PROJECT_ROOT / "logs" / "pipeline.jsonl"
    metrics = {
        "dedup_saved": 0,
        "rejection_rate": "0%",
        "heal_latency": "N/A",
        "total_exported": 0
    }
    
    if not log_file.exists():
        return metrics
        
    try:
        with _open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        latest_pipeline = None
        latest_heal = None
        
        for line in reversed(lines):
            try:
                data = json.loads(line)
                if not latest_pipeline and data.get("event") == "Pipeline completed":
                    latest_pipeline = data
                if not latest_heal and data.get("event") == "Self-heal completed":
                    latest_heal = data
                if latest_pipeline and latest_heal:
                    break
            except Exception as e:
                logging.warning(f"Error parsing log line in {log_file}: {e}")
                
        if latest_pipeline:
            exact = latest_pipeline.get("exact_removed", 0)
            semantic = latest_pipeline.get("semantic_removed", 0)
            metrics["dedup_saved"] = exact + semantic
            metrics["rejection_rate"] = f"{latest_pipeline.get('rejection_rate_pct', 0)}%"
            metrics["total_exported"] = latest_pipeline.get("total_clean_exported", 0)
            
        if latest_heal:
            metrics["heal_latency"] = f"{latest_heal.get('latency_seconds', 0)}s"
            
    except Exception as e:
        logging.error(f"Error reading logs file {log_file}: {e}")
        
    return metrics
