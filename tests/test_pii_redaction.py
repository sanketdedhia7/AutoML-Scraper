import pytest
from pipeline.cleaner import Cleaner

def test_pii_redaction_emails_and_phones():
    cleaner = Cleaner()
    raw_text = "Contact john.doe@example.com or call +1 (555) 123-4567 for more info."
    cleaned = cleaner.clean_text(raw_text)
    
    assert "john.doe@example.com" not in cleaned
    assert "+1 (555) 123-4567" not in cleaned
    assert "[REDACTED_EMAIL]" in cleaned
    assert "[REDACTED_PHONE]" in cleaned

def test_pii_redaction_in_article():
    cleaner = Cleaner()
    article = {
        "title": "Email us at support@company.org",
        "content": "Reach support via phone 555-867-5309 or email help@company.org."
    }
    cleaned_article = cleaner.clean_article(article)
    
    assert "[REDACTED_EMAIL]" in cleaned_article["title"]
    assert "[REDACTED_EMAIL]" in cleaned_article["content"]
    assert "[REDACTED_PHONE]" in cleaned_article["content"]

def test_pii_redaction_preserves_scientific_ids():
    cleaner = Cleaner()
    scientific_text = "arXiv:2103.01234 doi:10.1016/j.cell.2021.05.012 page range 101-105-1234"
    cleaned = cleaner.clean_text(scientific_text)
    
    assert "[REDACTED_PHONE]" not in cleaned
    assert "2103.01234" in cleaned
    assert "10.1016/j.cell.2021.05.012" in cleaned
    assert "101-105-1234" in cleaned

