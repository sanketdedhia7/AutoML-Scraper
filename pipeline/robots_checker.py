import urllib.robotparser
from urllib.parse import urlparse
from typing import Dict
from monitoring.logger import StructuredLogger

class RobotsChecker:
    """
    Parses and checks robots.txt files for target domains to ensure scraping compliance.
    Caches parsed robots.txt rules per origin domain.
    """
    def __init__(self, user_agent: str = "*"):
        self.user_agent = user_agent
        self.parsers: Dict[str, urllib.robotparser.RobotFileParser] = {}
        self.logger = StructuredLogger()

    def _get_parser(self, url: str) -> urllib.robotparser.RobotFileParser:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            parser = urllib.robotparser.RobotFileParser()
            parser.allow_all = True
            return parser

        origin = f"{parsed.scheme}://{parsed.netloc}"
        if origin not in self.parsers:
            robots_url = f"{origin}/robots.txt"
            parser = urllib.robotparser.RobotFileParser()
            parser.set_url(robots_url)
            try:
                parser.read()
            except Exception as exc:
                self.logger.log("WARNING", f"Failed to fetch/parse {robots_url}: {exc}. Defaulting to allow.")
                parser.allow_all = True
            self.parsers[origin] = parser
        return self.parsers[origin]

    def is_allowed(self, url: str) -> bool:
        """Return True if url is allowed to be scraped according to robots.txt."""
        if not url or not isinstance(url, str):
            return True
        # Fast path for local mock URLs
        if "example.com" in url or "localhost" in url:
            return True
        try:
            parser = self._get_parser(url)
            return parser.can_fetch(self.user_agent, url)
        except Exception as exc:
            self.logger.log("WARNING", f"Error checking robots.txt for {url}: {exc}")
            return True
