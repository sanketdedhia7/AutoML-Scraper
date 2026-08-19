import os
from bs4 import BeautifulSoup
from scrapers.demo_selectors import load_demo_selectors

class DemoFixtureParser:
    """Deterministic BeautifulSoup parser for local HTML fixtures using current demo selectors."""
    
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            self.base_dir = os.path.dirname(os.path.dirname(__file__))
        else:
            self.base_dir = base_dir

    def run_parser(self) -> list:
        """Parse static HTML fixture and return a list of mapped dictionary items."""
        fixture_path = os.path.join(self.base_dir, "tests", "fixtures", "current_demo_page.html")
        if not os.path.exists(fixture_path):
            fixture_path = os.path.join(self.base_dir, "tests", "fixtures", "before_layout.html")

        selectors = load_demo_selectors()

        with open(fixture_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, 'html.parser')
        results = []

        containers = soup.select(selectors.get("container", ".article-item"))
        for item in containers:
            title_el = item.select_one(selectors.get("title", "h3.article-title a"))
            title = title_el.text.strip() if title_el else ""

            url = ""
            if title_el:
                if title_el.name == 'a':
                    url = title_el.get('href', '')
                else:
                    a_el = title_el.select_one('a')
                    url = a_el.get('href', '') if a_el else ""

            author_el = item.select_one(selectors.get("author", ".meta-author"))
            author = author_el.text.strip() if author_el else ""

            pub_el = item.select_one(selectors.get("publication_date", ".meta-date"))
            pub_date = pub_el.text.strip() if pub_el else ""

            content_el = item.select_one(selectors.get("content", ".abstract-text"))
            content = content_el.text.strip() if content_el else ""

            results.append({
                "title": title,
                "author": author,
                "publication_date": pub_date,
                "content": content,
                "url": url,
                "source": "demo_scraper",
            })

        return results
