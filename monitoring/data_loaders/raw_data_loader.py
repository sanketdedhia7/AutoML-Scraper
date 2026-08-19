import json
import logging
from typing import Dict, List, Any
from pipeline.utils import PROJECT_ROOT

def load_preloaded_raw_data() -> Dict[str, List[Dict[str, Any]]]:
    """Pre-load raw JSON output files to avoid duplicate disk I/O per request."""
    raw_dir = PROJECT_ROOT / "data" / "raw"
    preloaded_raw = {}
    
    if raw_dir.exists():
        for file in raw_dir.glob("*.json"):
            collector_id = file.stem
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    preloaded_raw[collector_id] = json.load(f)
            except Exception as e:
                logging.warning(f"Error pre-loading raw JSON file {file}: {e}")
                
    # Handle deterministic demo scraper raw data
    if "demo_scraper" not in preloaded_raw:
        from scrapers.scraper_manager import ScraperManager
        try:
            demo_raw = ScraperManager()._run_demo_scraper_parser()
            preloaded_raw["demo_scraper"] = demo_raw
        except Exception as e:
            logging.warning(f"Error generating demo scraper raw content: {e}")

    return preloaded_raw

def build_raw_content_map(preloaded_raw: Dict[str, List[Dict[str, Any]]]) -> Dict[str, str]:
    """Index raw items by their clean title to map them to text contents."""
    raw_map = {}
    for collector_id, raws in preloaded_raw.items():
        for r in raws:
            title = r.get("title", "")
            if title:
                title = title.strip()
            raw_map[title] = r.get("content", "")
    return raw_map
