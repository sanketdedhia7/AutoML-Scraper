import re
from bs4 import BeautifulSoup
import html2text
from .pii_redactor import safe_str, redact_pii

class HTMLCleaner:
    def __init__(self):
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = True

    def clean_text(self, text: str) -> str:
        """Remove boilerplate, ads, navigation using trafilatura content extraction & regex rules"""
        text = safe_str(text)
        
        # If HTML, extract main content using trafilatura or BeautifulSoup node stripping
        if re.search(r"<\s*[a-zA-Z/]", text):
            extracted = None
            try:
                import trafilatura
                extracted = trafilatura.extract(text, include_links=False, include_images=False, favor_precision=True)
            except Exception:
                extracted = None
                
            if extracted and len(extracted.strip()) > 30:
                text = extracted
            else:
                try:
                    soup = BeautifulSoup(text, 'html.parser')
                    # Strip structural boilerplate tags
                    for tag in soup.find_all(['header', 'nav', 'footer', 'script', 'style', 'aside', 'iframe']):
                        tag.decompose()
                    # Strip elements with ad/banner/nav/cookie class names
                    for tag in soup.find_all(class_=re.compile(r'ad|banner|cookie|nav|header|footer', re.I)):
                        tag.decompose()
                    text = self.html_converter.handle(str(soup))
                except Exception:
                    text = self.html_converter.handle(text)
        
        # Comprehensive boilerplate & ad stripping regexes
        patterns = [
            # Sponsored Ads & Promoted Content
            r"(?mi)^\s*(?:Sponsored\s+Ad|Sponsored\s+Content|Sponsored|Advertisement|Promoted)\b.*$",
            r"(?mi)\bSponsored\s+Ad:[^\n]*",
            r"(?mi)^\s*Read more\b.*$",          # Standalone line starting with "Read more"
            r"(?mi)^\s*Share this\b.*$",         # Standalone line starting with "Share this"
            r"(?mi)^\s*Subscribe\b.*$",          # Standalone line starting with "Subscribe"
            r"(?mi)^\s*Related articles\b.*$",   # Standalone line starting with "Related articles"
            r"(?mi)^\s*Copyright\s+(?:©|\(c\)|[0-9]{4})\b.*$",  # Copyright line with year/symbol
            r"(?mi)\bCopyright\b[^.\n]*\Z",      # Copyright notice at the very end of the block
            
            # Common Crawl & Site Header / Navigation Chrome rules
            r"(?mi)^\s*We use cookies.*$",       # Cookie banners
            r"(?mi)^\s*By using this site.*$",   # Cookie/TOS banners
            r"(?mi)^\s*(?:Menu|Home|About Us|Contact Us|Privacy Policy)\s*$", # Nav links
            
            # arXiv domain chrome
            r"(?mi)arXiv is now an independent nonprofit.*$",
            r"(?mi)^\s*Skip to main content.*$",
            r"(?mi)^\s*Search arXiv.*$",
            r"(?mi)^\s*Press Enter to search.*$",
            r"(?mi)^\s*Help\s*\|\s*Advanced Search.*$",
            
            # PubMed / Medical domain chrome
            r"(?mi)^\s*National Library of Medicine.*$",
            r"(?mi)^\s*National Center for Biotechnology Information.*$",
            r"(?mi)^\s*An official website of the United States government.*$",
        ]
        
        for pattern in patterns:
            text = re.sub(pattern, "", text)
            
        # Clean up link dumps (lines with excessive separators like `|` or `>`)
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            if line.count('|') > 3 or line.count('>') > 3:
                continue # likely a breadcrumb or nav bar
            cleaned_lines.append(line)
        text = '\n'.join(cleaned_lines)
        
        # Remove excessive whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = text.strip()
        
        # Redact PII (emails & phone numbers)
        return redact_pii(text)
