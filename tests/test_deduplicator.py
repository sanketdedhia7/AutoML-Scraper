import pytest
from pipeline.deduplicator import Deduplicator
from unittest.mock import MagicMock, patch

def test_exact_deduplication():
    # Pass a MagicMock so it skips model loading, but don't care about semantic output
    # because we are testing exact dedup logic.
    mock_model = MagicMock()
    mock_model.encode.side_effect = Exception("Should fallback to Jaccard")
    deduplicator = Deduplicator(model=mock_model)
    articles = [
        {"url": "https://example.com/art1", "content": "This is a completely unique story about a cat climbing a tree in the backyard."},
        {"url": "https://example.com/art1", "content": "Different content but same url"},
        {"url": "https://example.com/art2", "content": "An entirely unrelated article about deep sea exploration and marine biology vessels."}
    ]
    result, stats = deduplicator.deduplicate(articles)
    assert len(result) == 2
    assert result[0]["url"] == "https://example.com/art1"
    assert result[1]["url"] == "https://example.com/art2"

@pytest.mark.slow
def test_near_duplicate_deduplication(dedup_model):
    deduplicator = Deduplicator(similarity_threshold=0.8, model=dedup_model)
    articles = [
        {"url": "https://example.com/1", "content": "This is a sentence about learning data curation for training large language models."},
        {"url": "https://example.com/2", "content": "This is a sentence about learning data curation for training large language models. It is useful."},
        {"url": "https://example.com/3", "content": "Something completely different and unrelated to machine learning or scraping pipelines."}
    ]
    result, stats = deduplicator.deduplicate(articles)
    # The first two are near-duplicates. The third is unique. We expect 2 articles.
    assert len(result) == 2
    # Ensure it keeps index 0 and 2
    urls = [a["url"] for a in result]
    assert "https://example.com/1" in urls
    assert "https://example.com/3" in urls

def test_cross_batch_deduplication(tmp_path):
    mock_model = MagicMock()
    mock_model.encode.side_effect = Exception("Should fallback to Jaccard")
    deduplicator = Deduplicator(model=mock_model)
    
    articles_b1 = [{"url": "https://example.com/shared", "content": "A story."}]
    articles_b2 = [
        {"url": "https://example.com/shared", "content": "A story duplicate."},
        {"url": "https://example.com/unique", "content": "New content"}
    ]
    
    # Create data dir manually since ensure_directories() uses the real PROJECT_ROOT.
    (tmp_path / "data").mkdir(exist_ok=True)
    
    res1, _ = deduplicator.deduplicate(articles_b1)
    assert len(res1) == 1
    
    res2, _ = deduplicator.deduplicate(articles_b2)
    assert len(res2) == 1
    assert res2[0]["url"] == "https://example.com/unique"

