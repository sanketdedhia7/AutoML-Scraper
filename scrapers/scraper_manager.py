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
        """
        return not self.api_key or self.api_key == "your_api_key_here"

    def scrape_url_via_brightdata(self, target_url: str) -> str:
        """Scrape raw page HTML via Bright Data CLI (`bdata scrape`) or Web Unlocker API fallback."""
        if self._mock_mode():
            raise RuntimeError("Mock mode active - no API key configured.")

        # Try CLI first (`bdata scrape <url> -f html`)
        import shutil
        if shutil.which("bdata"):
            try:
                return self.cli.scrape_url(target_url)
            except Exception as exc:
                logging.warning(f"bdata CLI scrape failed for {target_url}: {exc}. Trying REST API fallback.")

        # Fallback to direct Web Unlocker API if CLI is unavailable
        try:
            resp = requests.post(
                f"{self.base_url}/zone/route",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={"url": target_url, "zone": "web_unlocker", "format": "raw"},
                timeout=60
            )
            if resp.status_code == 200 and resp.text:
                return resp.text
        except Exception as e:
            logging.warning(f"Direct Bright Data Web Unlocker API request failed: {e}")

        raise RuntimeError(f"Unable to scrape {target_url} via Bright Data.")

    def create_scraper(self, config_path: str) -> dict:
        """Create a Scraper Studio collector via CLI (preferred) or REST API fallback."""
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

        import shutil
        if shutil.which("bdata"):
            try:
                logging.info(f"Using bdata CLI at: {shutil.which('bdata')}")
                return self.cli.create_scraper(target_url, description, name=collector_name)
            except Exception as exc:
                logging.warning(
                    f"bdata CLI create_scraper failed: {exc}. "
                    f"Falling back to REST API collector creation."
                )

        return self._create_via_rest_api(target_url, collector_name, description)

    def _create_via_rest_api(self, target_url: str, name: str, description: str) -> dict:
        """Create a Scraper Studio collector via Bright Data REST API when CLI is unavailable."""
        try:
            response = requests.post(
                f"{self.base_url}/dca/collector",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "name": name,
                    "url": target_url,
                    "description": description,
                },
                timeout=30,
            )

            if response.status_code in (200, 201):
                data = response.json()
                collector_id = data.get("collector_id") or data.get("id") or data.get("_id")
                if collector_id:
                    return {
                        "id": collector_id,
                        "collector_id": collector_id,
                        "name": name,
                        "status": "created",
                        "url": target_url,
                    }
        except Exception as exc:
            logging.warning(f"REST API collector creation failed for {target_url}: {exc}")

        return self._mock_collector({"url": target_url, "name": name}, status="api_error")

    def _mock_collector(self, config: dict, status: str = "mock_created") -> dict:
        return {
            "name": config.get("name", "unknown"),
            "id": f"col_{uuid.uuid4().hex[:8]}",
            "status": status,
            "url": config.get("url", ""),
        }

    def list_scrapers(self) -> list:
        return []

    def get_scraper_output(self, collector_id: str, snapshot_id: str = None) -> list:
        from pipeline.scraper_runner import ScraperRunner
        runner = ScraperRunner()
        return runner.get_scraper_output(collector_id, snapshot_id=snapshot_id)

    def _run_demo_scraper_parser(self) -> list:
        return DemoFixtureParser().run_parser()
