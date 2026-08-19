import re
from typing import Any

def safe_str(value: Any) -> str:
    """Return *value* as a str, coercing None (and any non-str scalar)
    to an empty string.  This handles the common case where a scraper
    selector matched nothing and the field is stored as JSON null / Python
    None rather than being absent from the dict entirely."""
    return value if isinstance(value, str) else ""

def redact_pii(text: str) -> str:
    """Redact PII (emails and phone numbers) from text."""
    text = safe_str(text)
    if not text:
        return ""
    # Redact email addresses
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    text = re.sub(email_pattern, "[REDACTED_EMAIL]", text)
    
    # Redact phone numbers (tuned to avoid corrupting arXiv IDs, DOIs, page ranges, or scientific IDs)
    # 1. Phone numbers with explicit phone keywords (e.g., "Phone: 123-456-7890", "Call (555) 123-4567")
    text = re.sub(r"(?i)(\b(?:phone|tel|mobile|cell|fax|contact|call)\b[:\s]*)(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", r"\1[REDACTED_PHONE]", text)
    # 2. International phone numbers with + prefix (e.g., "+1-800-555-0199", "+1 (555) 123-4567")
    text = re.sub(r"\b\+\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", "[REDACTED_PHONE]", text)
    # 3. Phone numbers with area code in parentheses (e.g., "(555) 123-4567")
    text = re.sub(r"\b\(\d{3}\)\s*\d{3}[-.\s]?\d{4}\b", "[REDACTED_PHONE]", text)
    
    return text
