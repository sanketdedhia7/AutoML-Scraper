import json
from typing import Dict, Any

from pipeline.utils import PROJECT_ROOT
from monitoring.health_checker import HealthChecker
from monitoring.data_loaders.scraper_meta import get_scraper_meta
from monitoring.data_loaders.article_loader import get_quality_stats_per_source, load_all_articles
from monitoring.data_loaders.scraper_registry import list_active_scrapers
from monitoring.data_loaders.raw_data_loader import load_preloaded_raw_data, build_raw_content_map
from monitoring.data_loaders.repair_state_loader import get_healed_collectors, get_pending_heals
from monitoring.data_loaders.dashboard_metrics import calculate_dashboard_metrics
from monitoring.presenters.scraper_card import render_scraper_card

def get_dashboard_data_dict() -> Dict[str, Any]:
    """Fetch health, log entries, and pending repairs to build dashboard status dictionary."""
    health_checker = HealthChecker()
    scraper_meta = get_scraper_meta()
    
    # 1. Load active scrapers
    scrapers_list = list_active_scrapers()
        
    # 2. Pre-load raw datasets
    preloaded_raw = load_preloaded_raw_data()
    raw_map = build_raw_content_map(preloaded_raw)
        
    # 3. Check health and load processed articles
    health = health_checker.check_all_scrapers(scrapers_list, preloaded_raw=preloaded_raw)
    articles = load_all_articles(raw_map)
    
    # 4. Calculate key metrics
    metrics = calculate_dashboard_metrics(articles)
    
    # 5. Check healed and pending repairs states
    healed_scrapers = get_healed_collectors()
    pending_heals = get_pending_heals()

    # 6. Quality stats
    quality_stats = get_quality_stats_per_source()
    quality_stats_json = json.dumps(quality_stats)

    # 7. Render dynamic HTML scraper narrative blocks via presenter cards
    scrapers_html = ""
    for collector_id, details in health['details'].items():
        smeta = scraper_meta.get(collector_id, {})
        scrapers_html += render_scraper_card(
            collector_id=collector_id,
            details=details,
            meta=smeta,
            pending_heals=pending_heals,
            healed_scrapers=healed_scrapers
        )
        
    # Return structured view model dictionary
    return {
        "scrapers_html": scrapers_html,
        "accepted_articles": metrics["accepted_articles"],
        "rejected_articles": metrics["rejected_articles"],
        "dedup_saved": metrics["dedup_saved"],
        "avg_score": metrics["avg_score"],
        "articles": articles,
        "quality_stats": quality_stats,
        "quality_stats_json": quality_stats_json,
    }
