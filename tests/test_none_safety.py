"""
Regression tests: None values in article fields (present-key / null-value).

These test the exact failure mode described in the bug report:
    article = {"content": None}   ← key exists, value is None
    article.get("content", "")    → returns None, NOT ""
    None.split()                  → AttributeError
    "x" in None                   → TypeError

All three pipeline stages must survive these inputs silently.
"""
import pytest

# ── Cleaner ────────────────────────────────────────────────────────────────────

from pipeline.cleaner import Cleaner, safe_str


class TestCleanerNoneSafety:
    def setup_method(self):
        self.cleaner = Cleaner()

    def test_clean_text_with_none_does_not_raise(self):
        """clean_text(None) must not raise TypeError."""
        result = self.cleaner.clean_text(None)  # type: ignore[arg-type]
        assert isinstance(result, str)

    def test_clean_title_with_none_does_not_raise(self):
        result = self.cleaner.clean_title(None)  # type: ignore[arg-type]
        assert isinstance(result, str)

    def test_clean_article_with_null_content_field(self):
        """Article where 'content' key is present but None must not crash."""
        article = {"title": "Real Title", "content": None, "source": None}
        result = self.cleaner.clean_article(article)
        assert result["content"] == ""
        assert result["title"] == "Real Title"

    def test_clean_article_with_null_title_field(self):
        article = {"title": None, "content": "Some real content here."}
        result = self.cleaner.clean_article(article)
        assert result["title"] == ""
        assert "Some real content" in result["content"]

    def test_safe_str_helper(self):
        assert safe_str(None) == ""
        assert safe_str("hello") == "hello"
        assert safe_str(42) == ""
        assert safe_str("") == ""
        assert safe_str(0) == ""


# ── Deduplicator ───────────────────────────────────────────────────────────────

from pipeline.deduplicator import Deduplicator, safe_str as dedup_safe_str
from unittest.mock import MagicMock


class TestDeduplicatorNoneSafety:
    def setup_method(self):
        # Use a mock model so we don't load the real SentenceTransformer
        mock_model = MagicMock()
        import numpy as np
        # Return a deterministic zero-vector for any input — forces Jaccard path
        mock_model.encode.return_value = np.zeros((3, 10))
        self.dedup = Deduplicator(model=mock_model)

    def test_null_content_key_does_not_raise(self):
        """Articles where 'content' is None must not crash model.encode()."""
        articles = [
            {"url": "http://a.com", "title": "A", "content": None},
            {"url": "http://b.com", "title": "B", "content": "Real content here."},
            {"url": "http://c.com", "title": "C"},  # key entirely absent
        ]
        result, stats = self.dedup.deduplicate(articles)
        assert isinstance(result, list)
        assert stats["input"] == 3

    def test_missing_content_key_does_not_raise(self):
        """Articles without a 'content' key at all must not raise KeyError."""
        articles = [
            {"url": "http://x.com", "title": "X"},
        ]
        result, stats = self.dedup.deduplicate(articles)
        assert len(result) == 1

    def test_no_url_and_no_title_article_is_retained_not_discarded(self):
        """An article with no url AND no title must NOT be silently dropped.
        Previously the guard `if url and url not in seen_urls` discarded it
        because empty string is falsy. The content-hash fallback must keep it.
        """
        articles = [
            {"content": "This article has no url or title but real content."},
        ]
        result, stats = self.dedup.deduplicate(articles)
        assert len(result) == 1, "Article with no url/title was silently discarded"
        # It should NOT be counted in exact_removed — it was never a duplicate
        assert stats["exact_removed"] == 0

    def test_two_identical_no_url_articles_are_deduped_not_both_kept(self):
        """Two articles with identical content and no url/title ARE genuine duplicates
        and should be reduced to one via the content-hash dedup key."""
        same = {"content": "Exact same text. No url. No title."}
        articles = [same.copy(), same.copy()]
        result, stats = self.dedup.deduplicate(articles)
        assert len(result) == 1
        assert stats["exact_removed"] == 1

    def test_two_distinct_no_url_articles_are_both_kept(self):
        """Two articles with different content but no url/title are distinct records
        and must both survive deduplication."""
        articles = [
            {"content": "First unique article with no identifying metadata."},
            {"content": "Second distinct article, completely different topic."},
        ]
        result, stats = self.dedup.deduplicate(articles)
        assert len(result) == 2
        assert stats["exact_removed"] == 0


# ── QualityScorer ──────────────────────────────────────────────────────────────

from pipeline.quality_scorer import QualityScorer, safe_str as qs_safe_str


class TestQualityScorerNoneSafety:
    def setup_method(self):
        self.scorer = QualityScorer()

    def test_score_article_with_null_content(self):
        """score_article must not crash when 'content' is None."""
        article = {"title": "My Title", "content": None, "url": "http://arxiv.org/1"}
        scored = self.scorer.score_article(article)
        assert "quality_score" in scored
        assert isinstance(scored["quality_score"], float)

    def test_score_article_with_null_url(self):
        article = {"title": "My Title", "content": "Some decent content " * 20, "url": None}
        scored = self.scorer.score_article(article)
        assert "quality_score" in scored

    def test_score_article_with_all_null_fields(self):
        """An article with every field None should be scored 0 gracefully."""
        article = {"title": None, "content": None, "url": None, "author": None}
        scored = self.scorer.score_article(article)
        assert scored["quality_score"] <= 30.0  # thin-content penalty

    def test_score_length_with_none(self):
        # score_length is called with safe_str(None) = "" internally,
        # but also verify calling with None directly doesn't crash.
        score = self.scorer.score_length(None)  # type: ignore[arg-type]
        assert isinstance(score, float)

    def test_score_readability_with_none(self):
        score = self.scorer.score_readability(None)  # type: ignore[arg-type]
        assert isinstance(score, float)

    def test_score_batch_survives_null_fields(self):
        articles = [
            {"content": None, "url": None},
            {"content": "Good long article content here. " * 40, "url": "http://arxiv.org/2"},
        ]
        scored, stats = self.scorer.score_batch(articles)
        assert stats["total"] == 2
        assert stats["accepted"] + stats["rejected"] == 2
