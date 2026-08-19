import json
import glob
import logging
from typing import Set, Dict, Any
from pipeline.utils import PROJECT_ROOT

def get_healed_collectors() -> Set[str]:
    """Read logs/pipeline.jsonl to find scrapers that have completed self-healing."""
    healed_scrapers = set()
    log_file = PROJECT_ROOT / "logs" / "pipeline.jsonl"
    if log_file.exists():
        try:
            import monitoring.data_loaders
            with monitoring.data_loaders.open(log_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        data = json.loads(line)
                        if data.get("event") == "Self-heal completed":
                            healed_scrapers.add(data.get("scraper_id"))
                    except Exception as e:
                        logging.warning(f"Error parsing log line {line_num} in {log_file}: {e}")
        except Exception as e:
            logging.error(f"Error reading log file {log_file}: {e}")
    return healed_scrapers

def get_pending_heals() -> Dict[str, Dict[str, Any]]:
    """Determine currently active pending approvals from repairs jsonl logs."""
    pending_heals = {}
    repair_files = glob.glob(str(PROJECT_ROOT / "data" / "repairs" / "*.jsonl"))
    repair_files.sort()
    for file in repair_files:
        try:
            import monitoring.data_loaders
            with monitoring.data_loaders.open(file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        data = json.loads(line)
                        cid = data.get("collector_id")
                        if not cid:
                            continue
                        status = data.get("result", {}).get("status")
                        if status == "awaiting_approval":
                            pending_heals[cid] = data.get("result")
                        elif status == "success":
                            if cid in pending_heals:
                                del pending_heals[cid]
                    except Exception as e:
                        logging.warning(f"Error parsing repair line {line_num} in {file}: {e}")
        except Exception as e:
            logging.error(f"Error reading repairs file {file} for pending checks: {e}")
    return pending_heals
