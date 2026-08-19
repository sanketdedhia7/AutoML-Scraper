import re
from .pii_redactor import safe_str, redact_pii

def clean_title(title: str, source: str = "") -> str:
    """Clean article title"""
    title = safe_str(title)
    # If we have the source name, specifically target " - Source" or " | Source" suffix
    if source:
        src_escaped = re.escape(source)
        patterns = [
            rf"\s+[-–|]\s+{src_escaped}$",
        ]
        for pattern in patterns:
            title = re.sub(pattern, "", title, flags=re.IGNORECASE)
    
    # General safe pattern for | which is almost always a site name suffix
    title = re.sub(r"\s+\|\s+[^|\n]+$", "", title)
    
    return redact_pii(title.strip())
