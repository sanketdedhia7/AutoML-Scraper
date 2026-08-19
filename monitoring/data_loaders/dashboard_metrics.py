from typing import Dict, List, Any
from pipeline.quality_scorer import QualityScorer
from monitoring.data_loaders.metrics_loader import get_impact_metrics

def calculate_dashboard_metrics(articles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculates all key yield, rejection, and score stats."""
    total_articles = len(articles)
    accepted_articles = sum(1 for a in articles if a.get("quality_score", 0) >= QualityScorer.ACCEPT_THRESHOLD)
    rejected_articles = total_articles - accepted_articles
    avg_score = round(sum(a.get("quality_score", 0) for a in articles) / max(total_articles, 1), 1)
    
    impact = get_impact_metrics()
    
    return {
        "total_articles": total_articles,
        "accepted_articles": accepted_articles,
        "rejected_articles": rejected_articles,
        "avg_score": avg_score,
        "dedup_saved": impact.get("dedup_saved", 0)
    }
