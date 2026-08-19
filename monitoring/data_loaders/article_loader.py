import json
import logging
from pipeline.quality_scorer import QualityScorer
from pipeline.utils import PROJECT_ROOT
import monitoring.data_loaders

def _open(*args, **kwargs):
    return monitoring.data_loaders.open(*args, **kwargs)

def get_quality_stats_per_source() -> list:
    """Return [{source, count, avg_score, accepted, rejected}] from data/scored/*.json."""
    scored_dir = PROJECT_ROOT / "data" / "scored"
    buckets: dict = {}
    if scored_dir.exists():
        for fp in scored_dir.glob("*.json"):
            try:
                with _open(fp, 'r', encoding='utf-8') as f:
                    arts = json.load(f)
                for a in arts:
                    src = a.get("source") or fp.stem
                    q = a.get("quality_score", 0)
                    b = buckets.setdefault(src, {"count": 0, "total": 0.0, "accepted": 0, "rejected": 0})
                    b["count"] += 1
                    b["total"] += q
                    if q >= QualityScorer.ACCEPT_THRESHOLD:
                        b["accepted"] += 1
                    else:
                        b["rejected"] += 1
            except Exception as e:
                logging.warning(f"Error loading scored file {fp}: {e}")
    result = []
    for src, b in sorted(buckets.items()):
        result.append({
            "source": src,
            "count": b["count"],
            "avg_score": round(b["total"] / max(b["count"], 1), 1),
            "accepted": b["accepted"],
            "rejected": b["rejected"],
        })
    return result


def load_all_articles(raw_map: dict) -> list:
    """Load all scored articles and attach raw HTML content from raw_map."""
    scored_dir = PROJECT_ROOT / "data" / "scored"
    all_articles = []
    if scored_dir.exists():
        for file in scored_dir.glob("*.json"):
            try:
                with _open(file, 'r', encoding='utf-8') as f:
                    articles = json.load(f)
                    for art in articles:
                        title = art.get("title", "").strip()
                        content = art.get("content", "")
                        # Attach raw HTML for HTML diff comparison
                        art["raw_content"] = raw_map.get(title, "Raw content not captured.")
                        art["has_email_redacted"] = "[REDACTED_EMAIL]" in content or "[REDACTED_EMAIL]" in title
                        art["has_phone_redacted"] = "[REDACTED_PHONE]" in content or "[REDACTED_PHONE]" in title
                        if "language" not in art or not art["language"]:
                            art["language"] = "en"
                        
                        src_stem = file.stem.upper()
                        ext_src = art.get("extraction_source")
                        if ext_src:
                            art["source"] = f"{src_stem} [{ext_src.upper()}]"
                        else:
                            art["source"] = src_stem
                            
                        all_articles.append(art)
            except Exception as e:
                logging.warning(f"Error loading scored JSON file {file}: {e}")
    return all_articles
