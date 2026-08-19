from typing import Any, Dict
from .pii_redactor import safe_str, redact_pii
from .html_cleaner import HTMLCleaner
from .title_cleaner import clean_title

try:
    from langdetect import detect
    HAS_LANGDETECT = True
except ImportError:
    HAS_LANGDETECT = False

class Cleaner:
    def __init__(self):
        self._html_cleaner = HTMLCleaner()

    @property
    def html_converter(self):
        return self._html_cleaner.html_converter

    def redact_pii(self, text: str) -> str:
        return redact_pii(text)

    def clean_text(self, text: str) -> str:
        return self._html_cleaner.clean_text(text)

    def clean_title(self, title: str, source: str = "") -> str:
        return clean_title(title, source=source)

    def clean_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Clean a single article"""
        cleaned = article.copy()
        
        # Clean content
        if "content" in cleaned:
            cleaned["content"] = self.clean_text(safe_str(cleaned["content"]))
            
            # Detect language
            if HAS_LANGDETECT:
                try:
                    if len(cleaned["content"].strip()) > 20:
                        cleaned["language"] = detect(cleaned["content"])
                    else:
                        cleaned["language"] = "unknown"
                except Exception:
                    cleaned["language"] = "unknown"
            else:
                cleaned["language"] = "unknown"
        
        # Clean title
        if "title" in cleaned:
            source = safe_str(cleaned.get("source"))
            cleaned["title"] = self.clean_title(safe_str(cleaned["title"]), source=source)
        
        return cleaned
