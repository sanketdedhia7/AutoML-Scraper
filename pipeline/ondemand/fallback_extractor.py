import logging
import trafilatura
from bs4 import BeautifulSoup
from pipeline.security import safe_fetch_html

class FallbackExtractor:
    """Safe HTML retrieval and text extraction heuristic."""

    def fetch_and_extract_text(self, target_url: str) -> str:
        """Fetch remote HTML securely and extract plain content."""
        raw_html = safe_fetch_html(target_url, max_redirects=3, timeout=15.0)
        cleaned_text = trafilatura.extract(raw_html, include_links=True, include_formatting=False)
        
        if not cleaned_text or len(cleaned_text.strip()) < 50:
            # Fallback to bs4 text snippet
            soup = BeautifulSoup(raw_html, 'html.parser')
            for script in soup(["script", "style", "header", "footer", "nav"]):
                script.extract()
            cleaned_text = soup.get_text(separator="\n").strip()[:10000]
        else:
            cleaned_text = cleaned_text[:10000] # Cap text length to prevent context overflow

        return cleaned_text
