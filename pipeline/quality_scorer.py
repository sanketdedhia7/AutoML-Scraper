import re
import math
from typing import Any, Dict, List


def safe_str(value: Any) -> str:
    """Coerce None / non-str scalars to empty string.
    Handles JSON null fields (e.g. Kaggle CSV NaN serialised to null)
    that would otherwise crash .split(), re.split(), or 'in' tests."""
    return value if isinstance(value, str) else ""

class QualityScorer:
    ACCEPT_THRESHOLD = 50.0

    def __init__(self):
        self.weights = {
            "length": 0.3,
            "readability": 0.3,
            "structure": 0.2,
            "source_authority": 0.2
        }
    
    def score_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Score article quality (0-100) and provide rejection explanations if low quality"""
        scored = article.copy()
        
        # Calculate individual scores
        length_score = self.score_length(safe_str(article.get("content")))
        readability_score = self.score_readability(safe_str(article.get("content")))
        structure_score = self.score_structure(article)
        authority_score = self.score_authority(article)
        
        # Weighted average
        overall_score = (
            length_score * self.weights["length"] +
            readability_score * self.weights["readability"] +
            structure_score * self.weights["structure"] +
            authority_score * self.weights["source_authority"]
        )
        
        # Language penalty
        lang = article.get("language", "en") # assume en if missing to avoid breaking legacy tests
        if lang != "en" and lang != "unknown":
            overall_score = min(overall_score, 20.0)
            
        # Hard penalty for thin content (essential for LLM training data quality)
        word_count = len(safe_str(article.get("content")).split())
        if word_count < 50:
            overall_score = min(overall_score, 30.0)  # Critical Fail
        elif word_count < 80:
            overall_score = min(overall_score, 45.0)  # Moderate Fail (Rejected)
            
        scored["quality_score"] = round(overall_score, 2)
        scored["quality_breakdown"] = {
            "length": length_score,
            "readability": readability_score,
            "structure": structure_score,
            "authority": authority_score
        }
        
        # Add human-readable reason if quality is low (rejected threshold is < 50.0)
        rejection_reasons = []
        if lang != "en" and lang != "unknown":
            rejection_reasons.append(f"Non-English content ({lang})")
        if word_count < 50:
            rejection_reasons.append(f"Critical thin content ({word_count} words)")
        elif word_count < 80:
            rejection_reasons.append(f"Sub-optimal content length ({word_count} words)")
            
        if length_score < 70:
            rejection_reasons.append("Short content length")
        if readability_score < 70:
            rejection_reasons.append("Unusual sentence or structural pacing")
        if structure_score < 70:
            rejection_reasons.append("Missing critical metadata fields")
        if authority_score < 70:
            rejection_reasons.append("Low-authority domain")
            
        scored["rejection_reason"] = "; ".join(rejection_reasons) if overall_score < self.ACCEPT_THRESHOLD else ""
        
        return scored
        
    def score_batch(self, articles: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Score a batch of articles and return (scored_articles, stats)"""
        scored_data = [self.score_article(article) for article in articles]
        total = len(scored_data)
        accepted = sum(1 for a in scored_data if a.get("quality_score", 0) >= self.ACCEPT_THRESHOLD)
        rejected = total - accepted
        rejection_rate = (rejected / total * 100) if total > 0 else 0
        
        stats = {
            "total": total,
            "accepted": accepted,
            "rejected": rejected,
            "rejection_rate_pct": round(rejection_rate, 1)
        }
        
        return scored_data, stats
    
    def score_length(self, content: str) -> float:
        """Score based on content length using a continuous curve (ideal: 80-1000 words for abstracts)"""
        content = safe_str(content)
        word_count = len(content.split())
        
        if word_count < 80:
            # Smoothly curve from 20 to 100 for short content
            return round(20.0 + 80.0 * ((word_count / 80.0) ** 0.7), 2)
        elif word_count <= 1000:
            # Flat ideal range
            return 100.0
        else:
            # Smooth exponential decay towards a lower bound of 50 for overly verbose text
            decay = math.exp(-(word_count - 1000) / 1500.0)
            return round(50.0 + 50.0 * decay, 2)

    
    def score_readability(self, content: str) -> float:
        """Score based on readability (sentence length, paragraph structure)"""
        content = safe_str(content)
        sentences = re.split(r'[.!?]+', content)
        # Filter out empty strings
        sentences = [s.strip() for s in sentences if s.strip()]
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        
        if 10 <= avg_sentence_length <= 25:
            return 100.0
        elif 5 <= avg_sentence_length < 10 or 25 < avg_sentence_length <= 35:
            return 70.0
        else:
            return 40.0
    
    def score_structure(self, article: Dict[str, Any]) -> float:
        """Score based on article structure (has title, author, date, etc.)"""
        score = 0
        
        if article.get("title"):
            score += 25
        if article.get("author") or article.get("authors"):
            score += 25
        if article.get("publication_date"):
            score += 25
        if article.get("content") and len(safe_str(article["content"])) > 100:
            score += 25
        
        return score
    
    def score_authority(self, article: Dict[str, Any]) -> float:
        """Score based on source authority (domain reputation).

        Scoring hierarchy (high → low):
          100 — known authoritative academic/gov/legal domains (.edu, .gov, arxiv, pubmed)
           70 — recognised news outlets (news, reuters, bbc, times, bloomberg, post)
           60 — recognised blog platforms (blog, medium, substack, wordpress)
           50 — unknown / unrecognised neutral domains (default baseline)
           30 — known low-quality / clickbait / spam domains (clickbait, spam, adfly, bit.ly, pirate)
        """
        url = safe_str(article.get("url")).lower()
        
        authoritative_domains = [
            "arxiv.org", "pubmed", "scholar", "edu", "gov",
            "lawreview", "journal", "academic"
        ]
        news_domains = ["news", "times", "reuters", "bloomberg", "bbc", "washingtonpost", "nypost", "huffpost"]
        blog_domains = ["blog", "medium.com", "substack.com", "wordpress.com"]
        low_quality_domains = ["spam", "clickbait", "adfly", "bit.ly", "pirate"]
        
        if any(d in url for d in low_quality_domains):
            return 30.0
        elif any(d in url for d in authoritative_domains):
            return 100.0
        elif any(d in url for d in news_domains):
            return 70.0
        elif any(d in url for d in blog_domains):
            return 60.0
        else:
            return 50.0  # Unknown domain baseline — lower than blogs & news, higher than spam
