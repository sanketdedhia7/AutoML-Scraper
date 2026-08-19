import json
import logging
from pipeline.utils import PROJECT_ROOT
import monitoring.data_loaders

def _open(*args, **kwargs):
    return monitoring.data_loaders.open(*args, **kwargs)

def get_scraper_meta() -> dict:
    """Return {collector_id: {display_name, url, schedule}} from scrapers/*.json."""
    meta = {}
    scrapers_dir = PROJECT_ROOT / "scrapers"
    for fp in scrapers_dir.glob("*.json"):
        if fp.stem in ("active_scrapers", "demo_selectors"):
            continue
        try:
            with _open(fp, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
            meta[fp.stem] = {
                "display_name": cfg.get("name", fp.stem).replace("_", " ").title(),
                "url": cfg.get("url", ""),
                "schedule": cfg.get("schedule", ""),
            }
        except Exception as e:
            logging.warning(f"Error loading scraper meta for {fp}: {e}")
    # Add demo scraper fallback
    meta.setdefault("demo_scraper", {"display_name": "Demo Scraper", "url": "", "schedule": ""})
    
    # Add approved on-demand scrapers
    scored_dir = PROJECT_ROOT / "data" / "scored"
    if scored_dir.exists():
        for fp in scored_dir.glob("ondemand_*.json"):
            meta.setdefault(fp.stem, {
                "display_name": f"On-Demand Scraper ({fp.stem.split('_')[-1]})",
                "url": "",
                "schedule": "On-Demand"
            })
    return meta
