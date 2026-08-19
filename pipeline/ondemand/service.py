import logging
from dotenv import load_dotenv
load_dotenv()

from typing import Dict, Any
from pipeline.ondemand.primary_extractor import PrimaryExtractor
from pipeline.ondemand.fallback_extractor import FallbackExtractor
from pipeline.ondemand.gemini_extractor import GeminiExtractor
from pipeline.ondemand.article_processor import ArticleProcessor
from pipeline.ondemand.quarantine_repository import QuarantineRepository

class OnDemandRunner:
    """Orchestrates secure on-demand URL scraping and pipeline safeguarding workflow."""

    def __init__(self):
        self.primary = PrimaryExtractor()
        self.fallback = FallbackExtractor()
        self.gemini = GeminiExtractor()
        self.processor = ArticleProcessor()
        self.quarantine_repo = QuarantineRepository()

    def run_ondemand_scrape(self, target_url: str, update_progress_cb=None) -> Dict[str, Any]:
        """Run the full on-demand scrape workflow."""
        def update_progress(step_msg: str):
            if update_progress_cb:
                update_progress_cb(step_msg)
            logging.info(f"[OnDemandRunner] {step_msg}")

        # 1. Primary Scrape: Bright Data CLI
        is_mock = self.primary.collector_registry._mock_mode()
        if is_mock:
            update_progress(f"[Mock Mode Enabled] Initiating mock primary scrape path for {target_url}...")
        else:
            update_progress(f"Initiating primary scrape path via Scraper Studio for {target_url}...")
            
        articles = self.primary.run_primary_scrape(target_url)
        extraction_source = "mock_scraper_studio" if is_mock else "scraper_studio_cli"

        # 2. Secondary Scrape: Web Unlocker + Gemini
        if not articles:
            # Fallback default value (will be refined by the extractor inside articles)
            extraction_source = "gemini_llm_fallback"
            update_progress("Primary path returned no data. Executing Secondary Path (Safe Fetch + Gemini LLM)...")
            
            cleaned_text = self.fallback.fetch_and_extract_text(target_url)
            update_progress("Extracting structured content using Gemini LLM...")
            articles = self.gemini.extract_with_gemini(cleaned_text, target_url)

        if not articles:
            raise RuntimeError("Scrape failed: Unable to extract valid structured content from target URL.")

        # 3. Process & Safeguards
        update_progress("Running Pipeline Safeguards (Cleaning, Validation, Quality Scoring, Deduplication)...")
        processed_articles, duplicates_removed = self.processor.process_articles(articles, target_url, extraction_source)

        if not processed_articles:
            return {
                "status": "warning",
                "message": "Scrape completed but all extracted items were flagged as duplicates.",
                "articles": [],
                "quarantined": True,
                "duplicates_removed": duplicates_removed
            }

        # Resolve actual extraction method from first processed article
        actual_source = processed_articles[0].get("extraction_source", extraction_source) if processed_articles else extraction_source

        # 4. Save to Quarantine
        update_progress("Placing items into Quarantine / Pending Approval state for dashboard moderation...")
        collector_id = self.quarantine_repo.save_to_quarantine(target_url, processed_articles, actual_source)

        update_progress("Complete! Items successfully queued in Pending Review.")
        return {
            "status": "success",
            "message": f"Successfully scraped {len(processed_articles)} article(s). Placed in Quarantine (Pending Review).",
            "articles": processed_articles,
            "collector_id": collector_id,
            "quarantined": True,
            "duplicates_removed": duplicates_removed,
            "extraction_method": actual_source
        }
