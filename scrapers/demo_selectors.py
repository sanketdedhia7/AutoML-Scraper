import json
import os

DEFAULT_SELECTORS = {
    "container": ".article-item",
    "title": "h3.article-title a",
    "author": ".meta-author",
    "publication_date": ".meta-date",
    "content": ".abstract-text",
}

def load_demo_selectors() -> dict:
    """Load selectors from scrapers/demo_selectors.json or fall back to defaults."""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    selector_path = os.path.join(base_dir, "scrapers", "demo_selectors.json")
    if not os.path.exists(selector_path):
        return DEFAULT_SELECTORS
    try:
        with open(selector_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return DEFAULT_SELECTORS
