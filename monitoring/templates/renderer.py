import datetime
import json
from pipeline.quality_scorer import QualityScorer
from .base import get_html_head
from .styles import DASHBOARD_STYLES
from .components import get_dashboard_body
from .scripts import get_dashboard_scripts

def render_dashboard_html(data: dict) -> str:
    """Render a premium dual-tab (Ops Health + Curated Dataset Explorer) HTML dashboard."""
    threshold = QualityScorer.ACCEPT_THRESHOLD
    curated_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    accepted_articles = data.get("accepted_articles", 0)
    rejected_articles = data.get("rejected_articles", 0)
    dedup_saved = data.get("dedup_saved", 0)
    avg_score = data.get("avg_score", 0)
    scrapers_html = data["scrapers_html"]
    articles_json = json.dumps(data["articles"])
    quality_stats_json = data["quality_stats_json"]
    
    html = get_html_head()
    html += "<style>\n" + DASHBOARD_STYLES + "</style>\n</head>\n<body>\n"
    html += get_dashboard_body(
        curated_date=curated_date,
        accepted_articles=accepted_articles,
        rejected_articles=rejected_articles,
        dedup_saved=dedup_saved,
        avg_score=avg_score,
        threshold=threshold,
        scrapers_html=scrapers_html
    )
    html += "<script>\n"
    html += get_dashboard_scripts(
        articles_json=articles_json, 
        quality_stats_json=quality_stats_json, 
        threshold=threshold
    )
    html += "</script>\n</body>\n</html>"
    return html
