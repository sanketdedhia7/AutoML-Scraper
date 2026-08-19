import os
from dotenv import load_dotenv
from monitoring.logger import StructuredLogger
from pipeline.robots_checker import RobotsChecker
from .fallbacks import check_mock_mode, get_fallback_data
from .api_client import trigger_scraper as _trigger_scraper
from .poller import fetch_scraper_output, wait_for_completion as _wait_for_completion, filter_by_robots

load_dotenv()

class ScraperRunner:
    """
    Interfaces with Bright Data'real API and CLI.

    Real API surface used:
      - POST /dca/trigger          -> queues a job, returns snapshot_id
      - GET  /dca/dataset?id=<sid> -> polls / fetches completed records
    Scraper *creation* is done via the Bright Data CLI (bdata scraper create),
    mirroring how healer.py already shells out to bdata scraper heal.
    """

    def __init__(self):
        self.api_key = os.getenv("BRIGHT_DATA_API_KEY")
        self.base_url = "https://api.brightdata.com"
        self.logger = StructuredLogger()
        self.robots_checker = RobotsChecker()

    def _mock_mode(self, collector_id: str = ""):
        return check_mock_mode(collector_id, self.api_key)

    def _filter_by_robots(self, items: list) -> list:
        return filter_by_robots(items, self.robots_checker, self.logger)

    def _get_fallback_data(self, collector_id):
        return get_fallback_data(collector_id, self.logger)

    def trigger_scraper(self, collector_id, url=None, retries=3, backoff_factor=2):
        return _trigger_scraper(
            collector_id=collector_id,
            base_url=self.base_url,
            api_key=self.api_key,
            logger=self.logger,
            url=url,
            retries=retries,
            backoff_factor=backoff_factor,
        )

    def get_scraper_output(self, collector_id, snapshot_id=None, timeout=None):
        return fetch_scraper_output(
            collector_id=collector_id,
            base_url=self.base_url,
            api_key=self.api_key,
            logger=self.logger,
            robots_checker=self.robots_checker,
            snapshot_id=snapshot_id,
            timeout=timeout,
        )

    def wait_for_completion(self, collector_id, snapshot_id=None, timeout=None):
        return _wait_for_completion(
            collector_id=collector_id,
            base_url=self.base_url,
            api_key=self.api_key,
            logger=self.logger,
            robots_checker=self.robots_checker,
            snapshot_id=snapshot_id,
            timeout=timeout,
            get_output_fn=self.get_scraper_output,
        )
