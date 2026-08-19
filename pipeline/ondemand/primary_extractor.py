import uuid
import json
import logging
from scrapers.scraper_manager import ScraperManager
from pipeline.utils import PROJECT_ROOT, ensure_directories

class PrimaryExtractor:
    """Invokes Scraper Studio CLI to scrape target URL."""

    def __init__(self):
        self.collector_registry = ScraperManager()

    def run_primary_scrape(self, target_url: str) -> list:
        """Run primary path via Scraper Studio CLI, returning raw data or empty list if failed."""
        articles = []
        if self.collector_registry._mock_mode():
            url_lower = target_url.lower()
            if any(k in url_lower for k in ["fail", "drift", "error", "unhealthy"]):
                logging.warning(f"[!] PRIMARY SCRAPER STUDIO CLI FAILED for {target_url}: Mock selector drift/error simulation triggered.")
                return []
            
            logging.info(f"Primary Scraper Studio CLI completed successfully for {target_url} (Mock Mode).")
            articles = self._get_mock_scraper_studio_articles(target_url)
            for art in articles:
                art["extraction_source"] = "mock_scraper_studio"
            return articles

        config_path = None
        try:
            from pipeline.ondemand.gemini_extractor import GeminiExtractor
            desc = GeminiExtractor().draft_scraper_description(target_url)
            
            ad_hoc_config = {
                "name": f"ondemand_{uuid.uuid4().hex[:6]}",
                "url": target_url,
                "description": desc
            }
            config_path = PROJECT_ROOT / "data" / f"temp_config_{uuid.uuid4().hex[:6]}.json"
            ensure_directories()
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(ad_hoc_config, f)

            collector_info = self.collector_registry.create_scraper(config_path)

            collector_id = collector_info.get("collector_id") or collector_info.get("id")
            
            # Robust check to verify if the collector is mock or real.
            # Mock collectors returned by ScraperManager._mock_collector use "col_" prefix or
            # carry a mock-specific status ("mock_created", "cli_error").
            # Real Bright Data Scraper Studio collectors generated via CLI carry a standard status like "created".
            is_mock_collector = (
                not collector_id or 
                collector_id.startswith("col_") or 
                collector_info.get("status") in ("mock_created", "cli_error")
            )
            
            if collector_id and not is_mock_collector:
                from pipeline.scraper_runner import ScraperRunner
                runner = ScraperRunner()
                trigger_result = runner.trigger_scraper(collector_id, url=target_url)
                logging.info(f"[OnDemand] trigger_result: {trigger_result}")
                if trigger_result.get("status") == "triggered":
                    snapshot_id = trigger_result.get("snapshot_id")
                    records = runner.wait_for_completion(collector_id, snapshot_id=snapshot_id, timeout=300)
                    if records and isinstance(records, list) and len(records) > 0:
                        articles = records
                        for art in articles:
                            art["extraction_source"] = "scraper_studio_cli"
                        logging.info(f"Primary Scraper Studio CLI completed successfully for {target_url}.")
                    else:
                        logging.warning(f"[!] PRIMARY SCRAPER STUDIO CLI FAILED for {target_url}: Empty snapshot dataset returned.")
                else:
                    logging.warning(f"[!] PRIMARY SCRAPER STUDIO CLI FAILED for {target_url}: Trigger API request rejected.")
        except Exception as exc:
            logging.warning(f"[!] PRIMARY SCRAPER STUDIO CLI FAILED for {target_url}: {exc}.")
        finally:
            if config_path and config_path.exists():
                try:
                    config_path.unlink()
                except Exception as e:
                    logging.warning(f"Failed to delete temp config file {config_path}: {e}")
        return articles

    def _get_mock_scraper_studio_articles(self, target_url: str) -> list:
        return [
            {
                "title": "A single page that lists information about all the countries in the world. Good for those just get started with web scraping.",
                "author": "System Heuristic",
                "publication_date": "2026-08-18",
                "content": "Browse through a database of NHL team stats since 1990. Practice building a scraper that handles common website interface components. Click through a bunch of great films. Learn how content is added ...",
                "url": target_url,
                "language": "en"
            }
        ]
