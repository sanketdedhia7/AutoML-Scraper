import pytest
from pipeline.cleaner import Cleaner

def test_clean_text_boilerplate():
    cleaner = Cleaner()
    text = "Important content.\nRead more articles here.\nShare this with friends.\nSubscribe now!\nCopyright 2026."
    cleaned = cleaner.clean_text(text)
    assert "Important content." in cleaned
    assert "Read more" not in cleaned
    assert "Share this" not in cleaned
    assert "Subscribe" not in cleaned
    assert "Copyright" not in cleaned

def test_clean_text_html():
    cleaner = Cleaner()
    html_content = "<p>Hello <b>World</b></p>"
    cleaned = cleaner.clean_text(html_content)
    assert "Hello" in cleaned
    assert "World" in cleaned
    assert "<p>" not in cleaned

def test_clean_title():
    cleaner = Cleaner()
    # General cleaning only strips general suffixes like | site
    assert cleaner.clean_title("Healthcare Insights | MedJournal") == "Healthcare Insights"
    
    # Specific cleaning requires matching source to prevent eating subheadings
    assert cleaner.clean_title("Roe v. Wade - What Comes Next", source="arxiv") == "Roe v. Wade - What Comes Next"
    assert cleaner.clean_title("Roe v. Wade - arXiv", source="arxiv") == "Roe v. Wade"
    assert cleaner.clean_title("Roe v. Wade – arXiv", source="arxiv") == "Roe v. Wade"

def test_clean_article():
    cleaner = Cleaner()
    article = {
        "title": "Article Title - Blog",
        "content": "<p>Content body</p>\nShare this.",
        "source": "Blog"
    }
    cleaned = cleaner.clean_article(article)
    assert cleaned["title"] == "Article Title"
    assert "Content body" in cleaned["content"]
    assert "Share this" not in cleaned["content"]

def test_preserves_mid_sentence_triggers():
    cleaner = Cleaner()
    # Verdigris / law content shouldn't be eaten if trigger words appear in mid-sentence
    body = "In this landmark case, Copyright law reform is being debated. We should read more books about it."
    cleaned_body = cleaner.clean_text(body)
    assert "Copyright law reform is being debated" in cleaned_body
    assert "read more books about it" in cleaned_body

    title = "Roe v. Wade - What Comes Next"
    cleaned_title = cleaner.clean_title(title, source="arxiv")
    assert cleaned_title == "Roe v. Wade - What Comes Next"

