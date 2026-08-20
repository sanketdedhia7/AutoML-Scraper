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

        The Bright Data CLI binary (bdata) is installed globally during Render build
        (npm install -g @brightdata/cli) so shutil.which("bdata") will find it at runtime.

        Previously this method checked shutil.which("bdata") and forced mock mode when
        the binary was absent. That caused all Render deploys to use mock data since
        local (non-global) node_modules installations don't persist to the runtime.
        """
        return not self.api_key or self.api_key == "your_api_key_here"

    def create_scraper(self, config_path: str) -> dict:
        """Create a Scraper Studio collector via CLI (preferred) or REST API fallback.

        On Render, the CLI is installed globally via `npm install -g @brightdata/cli`
        in the buildCommand, so it is available in the runtime PATH.
        The REST API fallback is used only if the CLI binary is unexpectedly absent.
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

        # Try CLI first — globally installed on Render, locally installed in dev
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

        # CLI not available — use Bright Data REST API to create a Scraper Studio collector
        logging.info(f"bdata CLI not in PATH. Using REST API to create collector for {target_url}")
        return self._create_via_rest_api(target_url, collector_name, description)

    def _create_via_rest_api(self, target_url: str, name: str, description: str) -> dict:
        """
        Create a Scraper Studio collector via Bright Data REST API when the CLI is unavailable.

        Calls POST /dca/collector to create the collector, which returns a collector_id
        that can then be triggered and polled by the existing primary_extractor flow.
        """
        try:
            # Create a new Scraper Studio collector via REST API
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

            logging.info(f"REST API create collector response: HTTP {response.status_code} - {response.text[:200]}")

            if response.status_code in (200, 201):
                data = response.json()
                collector_id = data.get("collector_id") or data.get("id") or data.get("_id")
                if collector_id:
                    logging.info(f"REST API created collector successfully: {collector_id}")
                    return {
                        "id": collector_id,
                        "collector_id": collector_id,
                        "name": name,
                        "status": "created",
                        "url": target_url,
                    }
                else:
                    logging.warning(f"REST API create returned 200 but no collector_id in response: {data}")
            else:
                logging.warning(
                    f"REST API create collector returned HTTP {response.status_code}: {response.text[:300]}"
                )
        except Exception as exc:
            logging.warning(f"REST API collector creation failed for {target_url}: {exc}")

        # If REST API also fails, return mock as absolute last resort
        logging.warning(f"All collector creation methods failed for {target_url}. Returning api_error mock.")
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
