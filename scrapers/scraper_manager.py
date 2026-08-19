import os
import uuid
import json
import logging
from dotenv import load_dotenv
load_dotenv()

from scrapers.studio_cli import BrightDataCLI
from scrapers.demo_fixture_parser import DemoFixtureParser

class ScraperManager:
    """Manages Scraper Studio collectors and output retrieval."""

    def __init__(self):
        self.api_key = os.getenv("BRIGHT_DATA_API_KEY")
        self.org_id = os.getenv("BRIGHT_DATA_ORG_ID")
        self.base_url = "https://api.brightdata.com"
        self.cli = BrightDataCLI(self.api_key)

    def _mock_mode(self) -> bool:
        import shutil
        if not shutil.which("bdata"):
            return True
        return not self.api_key or self.api_key == "your_api_key_here"

    def create_scraper(self, config_path: str) -> dict:
        """Create a collector via the Bright Data CLI, or fallback to mock mode."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            logging.error(f"Failed to load scraper config {config_path}: {e}")
            config = {}

        target_url = config.get("url", "")
        description = config.get("description", config.get("name", "Scraper"))

        if self._mock_mode():
            return self._mock_collector(config)

        try:
            return self.cli.create_scraper(target_url, description, name=config.get("name"))
        except Exception as exc:
            logging.warning(f"bdata scraper create failed: {exc}. Returning mock collector.")
            return self._mock_collector(config, status="cli_error")

    def _mock_collector(self, config: dict, status: str = "mock_created") -> dict:
        return {
            "name": config.get("name", "unknown"),
            "id": f"col_{uuid.uuid4().hex[:8]}",
            "status": status,
            "url": config.get("url", ""),
        }

    def list_scrapers(self) -> list:
        """List collectors. No public endpoint - returns empty list."""
        return []

    def get_scraper_output(self, collector_id: str, snapshot_id: str = None) -> list:
        """Retrieve scraper output from ScraperRunner."""
        from pipeline.scraper_runner import ScraperRunner
        runner = ScraperRunner()
        return runner.get_scraper_output(collector_id, snapshot_id=snapshot_id)

    def _run_demo_scraper_parser(self) -> list:
        """Legacy helper for demo cyclical break/heals."""
        return DemoFixtureParser().run_parser()
