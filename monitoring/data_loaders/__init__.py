open = open  # Re-exported for mock patching in tests

from .scraper_meta import get_scraper_meta
from .article_loader import get_quality_stats_per_source, load_all_articles
from .repairs_loader import get_repairs_data
from .metrics_loader import get_impact_metrics
from .dashboard_builder import get_dashboard_data_dict

__all__ = [
    "open",
    "get_scraper_meta",
    "get_quality_stats_per_source",
    "load_all_articles",
    "get_repairs_data",
    "get_impact_metrics",
    "get_dashboard_data_dict",
]
