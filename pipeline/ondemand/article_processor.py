import logging
from typing import List, Dict, Any, Tuple
from pipeline.cleaner import Cleaner
from pipeline.validator import Validator
from pipeline.quality_scorer import QualityScorer
from pipeline.deduplicator import Deduplicator

class ArticleProcessor:
    """Executes pipeline safeguards (cleaning, validation, quality scoring, deduplication) on extracted articles."""

    def __init__(self):
        self.cleaner = Cleaner()
        self.validator = Validator()
        self.scorer = QualityScorer()
        self.deduplicator = Deduplicator()

    def process_articles(self, articles: List[Dict[str, Any]], target_url: str, extraction_source: str) -> Tuple[List[Dict[str, Any]], int]:
        """Process, score, and deduplicate articles, returning processed articles list and duplicate count."""
        processed_articles = []
        duplicates_removed = 0

        for raw_art in articles:
            if not raw_art.get("url"):
                raw_art["url"] = target_url

            cleaned_art = self.cleaner.clean_article(raw_art)
            val_res = self.validator.validate([cleaned_art])
            cleaned_art["validation_errors"] = val_res.get("errors", [])
            cleaned_art["is_valid"] = val_res.get("is_valid", True)
            
            scored_art = self.scorer.score_article(cleaned_art)
            if "extraction_source" in raw_art:
                scored_art["extraction_source"] = raw_art["extraction_source"]
            else:
                scored_art["extraction_source"] = extraction_source

            if self.deduplicator.is_duplicate(cleaned_art):
                logging.info(f"Omitted duplicate article: {cleaned_art.get('title')}")
                duplicates_removed += 1
                continue

            processed_articles.append(scored_art)

        return processed_articles, duplicates_removed
