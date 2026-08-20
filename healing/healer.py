import os
import json
import logging
from dotenv import load_dotenv
from pipeline.utils import is_mock_mode
from healing.brightdata_cli import BrightDataHealingCLI
from healing.mock_healer import MockHealer

load_dotenv()

class Healer:
    """Orchestrator for CSS selector repairs using Bright Data CLI or mock paths."""

    def __init__(self):
        self.api_key = os.getenv("BRIGHT_DATA_API_KEY")
        self.cli = BrightDataHealingCLI(self.api_key)
        self.mock = MockHealer()

    def _mock_mode(self, collector_id: str) -> bool:
        """
        Mock mode for healing is active only when no API key is configured.
        The CLI binary check has been removed — if the CLI is unavailable on the runtime
        (e.g. Render), run_heal() will return status="error" which is caught and triggers
        the Gemini LLM fallback path, rather than silently going into mock mode.
        """
        return is_mock_mode(collector_id, self.api_key)

    def trigger_self_healing(
        self,
        collector_id: str,
        issue_description: str,
        broken_url: str = "",
        auto_approve: bool = False,
    ) -> dict:
        """Run bdata scraper heal or fall back to mock self-healing."""
        if self._mock_mode(collector_id):
            return self.mock.run_mock_heal(collector_id, auto_approve, broken_url)
            
        result = self.cli.run_heal(collector_id, issue_description, broken_url, auto_approve)
        
        # If Bright Data CLI failed (e.g. collector not found), explicitly trigger Gemini fallback
        if result.get("status") == "error":
            logging.warning(f"Bright Data CLI failed for {collector_id}: {result.get('message')}. Falling back to Gemini LLM.")
            fallback = self.mock.run_mock_heal(collector_id, auto_approve, broken_url)
            # Prepend the Bright Data error to the message so it's provable!
            fallback["message"] = f"Bright Data CLI Failed: {result.get('message')}. Triggered Gemini Fallback."
            return fallback
            
        # Use Gemini to generate a human-readable explanation for Bright Data's choices
        if result.get("diff_summary"):
            from pipeline.ondemand.gemini_extractor import GeminiExtractor
            explanation = GeminiExtractor().generate_selector_explanation(
                {"status": "broken"},
                {"changes": result["diff_summary"]}
            )
            result["explanation"] = explanation
            
        return result

    def approve_healing(self, collector_id: str) -> dict:
        """Approve a pending heal and commit it to the dataset or Scraper Studio."""
        # Handle on-demand scraper approval by promoting quarantine data to scored data
        if collector_id.startswith("ondemand_"):
            from pipeline.utils import PROJECT_ROOT, atomic_write_json
            qfile = PROJECT_ROOT / "data" / "repairs" / f"quarantine_{collector_id}.json"
            if not qfile.exists():
                return {"status": "error", "message": f"Quarantine file not found for {collector_id}", "collector_id": collector_id}
            try:
                with open(qfile, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Move preview_result to data/scored/{collector_id}.json
                articles = data.get("preview_result", [])
                if articles:
                    scored_file = PROJECT_ROOT / "data" / "scored" / f"{collector_id}.json"
                    atomic_write_json(scored_file, articles)
                
                # Delete quarantine file so it is no longer pending
                try:
                    qfile.unlink()
                except Exception as e:
                    logging.warning(f"Could not delete quarantine file {qfile}: {e}")
                
                return {
                    "status": "success",
                    "message": f"On-demand scrape approved. {len(articles)} specimens added to catalog.",
                    "collector_id": collector_id
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to approve on-demand scrape: {str(e)}",
                    "collector_id": collector_id
                }

        if self._mock_mode(collector_id):
            if collector_id == "demo_scraper":
                try:
                    from scrapers.scraper_manager import ScraperManager
                    from pipeline.utils import PROJECT_ROOT, atomic_write_json
                    
                    # Run demo parser to get raw items
                    raw_items = ScraperManager()._run_demo_scraper_parser()
                    
                    # Run pipeline safeguards (clean -> score) to simulate final scoring
                    from pipeline.quality_scorer import QualityScorer
                    from pipeline.cleaner import Cleaner
                    from pipeline.validator import Validator
                    
                    cleaner = Cleaner()
                    validator = Validator()
                    scorer = QualityScorer()
                    
                    processed = []
                    for raw_art in raw_items:
                        cleaned = cleaner.clean_article(raw_art)
                        val_res = validator.validate([cleaned])
                        cleaned["validation_errors"] = val_res.get("errors", [])
                        cleaned["is_valid"] = val_res.get("is_valid", True)
                        scored = scorer.score_article(cleaned)
                        scored["extraction_source"] = "demo_scraper"
                        processed.append(scored)
                    
                    if processed:
                        scored_file = PROJECT_ROOT / "data" / "scored" / "demo_scraper.json"
                        atomic_write_json(scored_file, processed)
                except Exception as e:
                    logging.error(f"Error writing mock scored data: {e}")

            return {"status": "success", "message": "Mock heal approved.", "collector_id": collector_id}

        return self.cli.approve_heal(collector_id)
