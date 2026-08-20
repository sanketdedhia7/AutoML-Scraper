import os
import uuid
import json
import logging
import requests
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
        """
        Mock mode is active ONLY when no valid API key is configured.

        The Bright Data CLI binary (bdata) is NOT required for production scraping.
        The actual data retrieval uses the Bright Data REST API directly.
        The CLI is only attempted for create_scraper (collector definition), and
        when not present the code falls back to the REST API trigger path automatically.

        Previously this checked shutil.which("bdata") which caused the system to
        fall into mock mode on Render (where node_modules do not persist to the runtime
        container even though npm install runs during the build step).
        """
        return not self.api_key or self.api_key == "your_api_key_here"

    def create_scraper(self, config_path: str) -> dict:
        """Create a collector via the Bright Data CLI if available, or REST API fallback.

        On environments where the bdata CLI is not installed (e.g. Render free tier),
        this method triggers an ad-hoc scrape via the Bright Data dataset trigger REST API
        instead, which avoids falling into mock mode while still using real Bright Data
        infrastructure.
        """
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception as e:
            logging.error(f"Failed to load scraper config {config_path}: {e}")
            config = {}

        target_url = config.get("url", "")
        description = config.get("description", config.get("name", "Scraper"))
        collector_name = config.get("name", f"collector_{uuid.uuid4().hex[:6]}")

        if self._mock_mode():
            return self._mock_collector(config)

        # Try CLI first (works locally and on environments with Node.js in PATH)
        import shutil
        if shutil.which("bdata"):
            try:
                return self.cli.create_scraper(target_url, description, name=collector_name)
            except Exception as exc:
                logging.warning(
                    f"bdata CLI create_scraper failed: {exc}. "
                    f"Falling back to REST API collector creation."
                )

        # CLI not available or failed - use REST API to trigger scrape directly.
        # This returns a virtual "collector" dict with a real snapshot_id so the
        # trigger/poll chain in primary_extractor.py continues with real Bright Data data.
        return self._create_via_rest_api(target_url, collector_name, description)

    def _create_via_rest_api(self, target_url: str, name: str, description: str) -> dict:
        """
        Trigger a Bright Data scrape via REST API when the CLI is unavailable.

        Uses the /datasets/v3/trigger endpoint which initiates an async scraping job.
        Returns a dict in the same shape as the CLI output so the existing trigger/poll
        chain in primary_extractor.py can consume it without modification.
        """
        try:
            response = requests.post(
                f"{self.base_url}/datasets/v3/trigger",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                params={"dataset_id": "gd_l1vikfnt1wgvvqz95w", "include_errors": "true"},
                json=[{"url": target_url}],
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                snapshot_id = data.get("snapshot_id") or data.get("id")
                logging.info(f"REST API trigger success for {target_url}: snapshot_id={snapshot_id}")
                return {
                    "id": snapshot_id or name,
                    "collector_id": snapshot_id or name,
                    "name": name,
                    "status": "created",
                    "url": target_url,
                    "snapshot_id": snapshot_id,
                }
            else:
                logging.warning(
                    f"REST API trigger returned HTTP {response.status_code} for {target_url}: {response.text}"
                )
        except Exception as exc:
            logging.warning(f"REST API collector creation failed for {target_url}: {exc}")

        # If REST API also fails, fall back to mock as last resort
        logging.warning(f"All collector creation methods failed. Returning mock collector for {target_url}.")
        return self._mock_collector({"url": target_url, "name": name}, status="api_error")

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
