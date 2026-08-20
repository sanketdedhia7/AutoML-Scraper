import uuid
import json
import logging
from bs4 import BeautifulSoup
import trafilatura

from scrapers.scraper_manager import ScraperManager
from pipeline.utils import PROJECT_ROOT, ensure_directories

class PrimaryExtractor:
    """Invokes Bright Data Scraper Studio CLI (bdata scrape) to scrape target URL."""

    def __init__(self):
        self.collector_registry = ScraperManager()

    def run_primary_scrape(self, target_url: str) -> list:
        """Run primary path via Bright Data CLI / Web Unlocker API, returning structured articles."""
        articles = []
        if self.collector_registry._mock_mode():
            url_lower = target_url.lower()
            if any(k in url_lower for k in ["fail", "drift", "error", "unhealthy"]):
                logging.warning(f"[!] PRIMARY SCRAPER STUDIO FAILED for {target_url}: Mock selector drift/error simulation triggered.")
                return []

            logging.info(f"Primary Scraper Studio completed successfully for {target_url} (Mock Mode).")
            articles = self._get_mock_scraper_studio_articles(target_url)
            for art in articles:
                art["extraction_source"] = "mock_scraper_studio"
            return articles

        try:
            # 1. Fetch raw page HTML via Bright Data Scraper Studio CLI / API
            raw_html = self.collector_registry.scrape_url_via_brightdata(target_url)
            if not raw_html or len(raw_html.strip()) < 50:
                logging.warning(f"[!] PRIMARY SCRAPER STUDIO returned empty content for {target_url}.")
                return []

            # 2. Parse structured specimens/articles from Bright Data fetched HTML
            articles = self._parse_html_to_articles(raw_html, target_url)
            for art in articles:
                art["extraction_source"] = "scraper_studio_cli"

            logging.info(f"Primary Scraper Studio CLI completed successfully for {target_url} ({len(articles)} items extracted).")
            return articles
        except Exception as exc:
            logging.warning(f"[!] PRIMARY SCRAPER STUDIO FAILED for {target_url}: {exc}.")
            return []

    def _parse_html_to_articles(self, raw_html: str, target_url: str) -> list:
        soup = BeautifulSoup(raw_html, "html.parser")
        title = soup.title.string.strip() if (soup.title and soup.title.string) else "Web Specimen"

        # Check for quotes on quotes.toscrape.com or generic quote listings
        quote_elements = soup.select(".quote")
        if quote_elements:
            articles = []
            for q in quote_elements:
                text_el = q.select_one(".text")
                author_el = q.select_one(".author")
                quote_text = text_el.get_text(strip=True) if text_el else ""
                author_text = author_el.get_text(strip=True) if author_el else "Unknown Author"
                if quote_text:
                    articles.append({
                        "title": f"Quote by {author_text}",
                        "author": author_text,
                        "publication_date": "2026-08-20",
                        "content": quote_text,
                        "url": target_url,
                        "language": "en"
                    })
            if articles:
                return articles

        # Check for book listings (e.g. books.toscrape.com)
        book_elements = soup.select(".product_pod")
        if book_elements:
            md_lines = [
                f"# Catalog Specimen - {title}",
                "Successfully extracted structured product catalog details:",
                ""
            ]
            for idx, b in enumerate(book_elements, 1):
                h3_a = b.select_one("h3 a")
                title_text = h3_a.get("title") or h3_a.get_text(strip=True) if h3_a else "Unknown Book"
                
                price_el = b.select_one(".price_color")
                price_text = price_el.get_text(strip=True) if price_el else "Unknown Price"
                
                avail_el = b.select_one(".instock.availability")
                avail_text = avail_el.get_text(strip=True) if avail_el else "Unknown Availability"
                if avail_text:
                    avail_text = avail_text.strip()
                
                rating_el = b.select_one("p.star-rating")
                rating_classes = rating_el.get("class", []) if rating_el else []
                rating_text = "Unknown"
                for c in rating_classes:
                    if c != "star-rating":
                        rating_text = c
                        break
                
                img_el = b.select_one(".image_container img")
                img_src = img_el.get("src") if img_el else ""
                
                link_el = b.select_one(".image_container a")
                link_href = link_el.get("href") if link_el else ""
                
                md_lines.append(f"{idx}. **{title_text}**")
                md_lines.append(f"   - **Price**: {price_text}")
                md_lines.append(f"   - **Availability**: {avail_text}")
                md_lines.append(f"   - **Rating**: {rating_text} out of 5 stars")
                if img_src:
                    md_lines.append(f"   - **Thumbnail**: {img_src}")
                if link_href:
                    md_lines.append(f"   - **Detail Page**: {link_href}")
                md_lines.append("")
                
            cleaned_text = "\n".join(md_lines)
            return [
                {
                    "title": title,
                    "author": "Bright Data Scraper Studio",
                    "publication_date": "2026-08-20",
                    "content": cleaned_text,
                    "url": target_url,
                    "language": "en"
                }
            ]

        # General article text extraction using trafilatura
        cleaned_text = trafilatura.extract(raw_html, include_links=True, include_formatting=False)
        if not cleaned_text or len(cleaned_text.strip()) < 50:
            for script in soup(["script", "style", "header", "footer", "nav"]):
                script.extract()
            cleaned_text = soup.get_text(separator="\n").strip()[:10000]
        else:
            cleaned_text = cleaned_text[:10000]

        if not cleaned_text:
            cleaned_text = "No content extracted from Bright Data raw HTML."

        return [
            {
                "title": title,
                "author": "Bright Data Scraper Studio",
                "publication_date": "2026-08-20",
                "content": cleaned_text,
                "url": target_url,
                "language": "en"
            }
        ]

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
