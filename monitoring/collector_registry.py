import json
from pipeline.utils import PROJECT_ROOT
from monitoring.data_loaders import get_scraper_meta

def validate_collector_id(collector_id: str) -> bool:
    """Validate that collector_id exists in active scrapers or scraper metadata."""
    if not collector_id or not isinstance(collector_id, str):
        return False
    if collector_id == "demo_scraper" or collector_id.startswith("col_demo"):
        return True
    if collector_id.startswith("ondemand_"):
        return True
    known_scrapers = get_scraper_meta()
    if collector_id in known_scrapers:
        return True
    mapping_path = PROJECT_ROOT / "scrapers" / "active_scrapers.json"
    if mapping_path.exists():
        try:
            with open(mapping_path, 'r', encoding='utf-8') as f:
                active_scrapers = json.load(f)
                if collector_id in active_scrapers or collector_id in active_scrapers.values():
                    return True
        except Exception:
            pass
    return False
