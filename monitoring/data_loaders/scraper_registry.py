import json
import logging
from typing import List
from pipeline.utils import PROJECT_ROOT

def list_active_scrapers() -> List[str]:
    """Finds all active scrapers in active_scrapers.json, json configs, and data/scored."""
    scrapers_list = []
    scrapers_dir = PROJECT_ROOT / "scrapers"
    
    if scrapers_dir.exists():
        mapping_path = scrapers_dir / "active_scrapers.json"
        if mapping_path.exists():
            try:
                import monitoring.data_loaders
                with monitoring.data_loaders.open(mapping_path, 'r', encoding='utf-8') as f:
                    scrapers_list = list(json.load(f).keys())
            except Exception as e:
                logging.error(f"Error reading active_scrapers.json: {e}")
        
        # Include other json config filenames (except active_scrapers and demo_selectors)
        for p in scrapers_dir.glob("*.json"):
            if p.stem not in ("active_scrapers", "demo_selectors") and p.stem not in scrapers_list:
                scrapers_list.append(p.stem)
                
    if not scrapers_list:
        scrapers_list = ["legal_blog_scraper", "medical_journal_scraper", "arxiv_scraper", "demo_scraper"]
        
    # Include approved on-demand scrapers dynamically
    scored_dir = PROJECT_ROOT / "data" / "scored"
    if scored_dir.exists():
        for fp in scored_dir.glob("ondemand_*.json"):
            if fp.stem not in scrapers_list:
                scrapers_list.append(fp.stem)

    return scrapers_list
