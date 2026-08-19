import pytest
from pipeline.quality_scorer import QualityScorer

def test_score_length():
    scorer = QualityScorer()
    # Ideal: 500-2000 words -> score 100
    ideal_text = " ".join(["word"] * 600)
    assert scorer.score_length(ideal_text) == 100
    
    # Too short -> penalized score
    short_text = "too short content"
    assert 20 < scorer.score_length(short_text) < 30

def test_score_readability():
    scorer = QualityScorer()
    # Good readability sentence length (10-25 words)
    good_readability = "This is a sentence that contains exactly ten words to test our quality score function."
    assert scorer.score_readability(good_readability) == 100

def test_score_structure():
    scorer = QualityScorer()
    full_article = {
        "title": "A Great Title",
        "author": "Dr. Smith",
        "publication_date": "2026-08-12",
        "content": "This is a longer paragraph of content text that satisfies the structural check of 100 characters in the quality scoring validation routine."
    }
    assert scorer.score_structure(full_article) == 100
    
    partial_article = {
        "title": "Minimal Title",
        "content": "Short"
    }
    # Has title (+25), doesn't have author (+0), doesn't have publication_date (+0), short content (+0) -> 25
    assert scorer.score_structure(partial_article) == 25

def test_score_authority():
    scorer = QualityScorer()
    assert scorer.score_authority({"url": "https://arxiv.org/abs/2301.0000"}) == 100
    assert scorer.score_authority({"url": "https://myblog.com/post"}) == 60
    # Unknown domains must score LOWER than recognised blogs (bug: was 80, now 50)
    assert scorer.score_authority({"url": "https://generic-site.com"}) == 50
    # Hierarchy: authoritative > blog > unknown
    academic = scorer.score_authority({"url": "https://arxiv.org/abs/1234"})
    blog     = scorer.score_authority({"url": "https://myblog.com/post"})
    unknown  = scorer.score_authority({"url": "https://random-domain.net"})
    assert academic > blog > unknown

def test_score_article():
    scorer = QualityScorer()
    article = {
        "title": "Deep Learning Discoveries",
        "author": "Jane Doe",
        "publication_date": "2026-08-12",
        "content": " ".join(["word"] * 600),
        "url": "https://arxiv.org/abs/12345"
    }
    scored = scorer.score_article(article)
    assert "quality_score" in scored
    assert "quality_breakdown" in scored
    assert scored["quality_score"] > 0
    assert scored["quality_breakdown"]["authority"] == 100
