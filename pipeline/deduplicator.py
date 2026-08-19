import hashlib
import json
import numpy as np
from typing import Any, List, Dict
import logging
import threading
from pathlib import Path

from pipeline.utils import PROJECT_ROOT, ensure_directories, atomic_write_json

_global_hash_lock = threading.RLock()
_SENTENCE_TRANSFORMER_CACHE = None
_SENTENCE_TRANSFORMER_FAILED = False

def _get_sentence_transformer():
    global _SENTENCE_TRANSFORMER_CACHE, _SENTENCE_TRANSFORMER_FAILED
    import os
    if os.getenv("DISABLE_SENTENCE_TRANSFORMERS") == "1":
        return None
    if _SENTENCE_TRANSFORMER_CACHE is None and not _SENTENCE_TRANSFORMER_FAILED:
        try:
            from sentence_transformers import SentenceTransformer
            logging.info("Loading SentenceTransformer model 'all-MiniLM-L6-v2'...")
            _SENTENCE_TRANSFORMER_CACHE = SentenceTransformer('all-MiniLM-L6-v2')
            logging.info("SentenceTransformer model loaded successfully.")
        except Exception as e:
            logging.warning(f"Could not load SentenceTransformer: {e}. Falling back to Jaccard similarity.")
            _SENTENCE_TRANSFORMER_FAILED = True
    return _SENTENCE_TRANSFORMER_CACHE

def safe_str(value: Any) -> str:
    """Coerce None / non-str scalars to empty string.
    Handles JSON null fields that a scraper stored as None instead of
    omitting the key entirely."""
    return value if isinstance(value, str) else ""

class Deduplicator:
    def __init__(self, similarity_threshold=0.9, model=None):
        self.similarity_threshold = similarity_threshold
        self.model = model
        if self.model is None:
            self.model = _get_sentence_transformer()
    
    def is_duplicate(self, article: Dict[str, Any]) -> bool:
        """Check if a single article is an exact duplicate against global_seen_hashes.json."""
        try:
            ensure_directories()
        except Exception:
            pass
        global_hashes_file = PROJECT_ROOT / "data" / "global_seen_hashes.json"
        
        dedup_key = safe_str(article.get("url"))
        if not dedup_key:
            dedup_key = safe_str(article.get("title"))
        if not dedup_key:
            raw = json.dumps(article, sort_keys=True, default=str)
            dedup_key = "hash:" + hashlib.sha256(raw.encode()).hexdigest()

        with _global_hash_lock:
            if global_hashes_file.exists():
                try:
                    with open(global_hashes_file, 'r', encoding='utf-8') as f:
                        seen_keys = set(json.load(f))
                        return dedup_key in seen_keys
                except Exception:
                    pass
        return False

    def deduplicate(self, articles: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Remove exact and near-duplicates and return (unique_articles, stats)"""
        stats = {
            "input": len(articles),
            "exact_removed": 0,
            "semantic_removed": 0,
            "output": 0
        }
        
        try:
            ensure_directories()
        except Exception as e:
            logging.warning(f"Failed to ensure directories: {e}")
            
        global_hashes_file = PROJECT_ROOT / "data" / "global_seen_hashes.json"
        
        # Exact deduplication by URL → title → content-hash (in priority order).
        # Falling back to a content-hash instead of discarding ensures that articles
        # with no URL/title are never silently dropped — they are only removed if
        # their *content* is also a true duplicate.
        seen_keys: set = set()
        unique_articles = []

        with _global_hash_lock:
            if global_hashes_file.exists():
                try:
                    with open(global_hashes_file, 'r', encoding='utf-8') as f:
                        seen_keys = set(json.load(f))
                except Exception as e:
                    logging.warning(f"Failed to read global_seen_hashes.json: {e}")
            
            initial_seen_keys = set(seen_keys)

            for article in articles:
                dedup_key = safe_str(article.get("url"))
                if not dedup_key:
                    dedup_key = safe_str(article.get("title"))
                if not dedup_key:
                    # Last resort: hash the full article so we always have a key.
                    raw = json.dumps(article, sort_keys=True, default=str)
                    dedup_key = "hash:" + hashlib.sha256(raw.encode()).hexdigest()

                if dedup_key not in seen_keys:
                    seen_keys.add(dedup_key)
                    unique_articles.append(article)
            
            if len(seen_keys) > len(initial_seen_keys):
                try:
                    atomic_write_json(global_hashes_file, list(seen_keys))
                except Exception as e:
                    logging.warning(f"Failed to write global_seen_hashes.json: {e}")
        
        stats["exact_removed"] = len(articles) - len(unique_articles)
        
        # Near-duplicate detection (Note: Pairwise similarity computation is O(n²); acceptable for demo scale but requires LSH/Vector index for production)
        if len(unique_articles) == 0:
            return [], stats
            
        # Protect against O(N^2) memory/compute blowup for large datasets (e.g., 5000+ articles)
        if len(unique_articles) > 1000:
            logging.warning(
                f"Batch size too large ({len(unique_articles)} articles) for pairwise similarity checks. "
                "Skipping semantic/Jaccard near-duplicate removal to prevent O(N^2) hang. "
                "Returning exact deduplicated articles."
            )
            stats["semantic_removed"] = 0
            stats["output"] = len(unique_articles)
            return unique_articles, stats

        
        if self.model is not None:
            try:
                # Prepare high-signal content representation (title + body snippet)
                # This ensures the 256-token window receives unique article content rather than site header chrome
                contents = []
                for article in unique_articles:
                    title = safe_str(article.get("title"))
                    content = safe_str(article.get("content"))
                    if title:
                        text_snippet = f"{title}. {content}"
                    else:
                        text_snippet = content
                    contents.append(text_snippet[:1200].strip())
                    
                embeddings = self.model.encode(contents, convert_to_numpy=True)
                
                # Calculate cosine similarity
                norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
                # avoid division by zero
                norms[norms == 0] = 1e-12
                normalized_embeddings = embeddings / norms
                similarity_matrix = np.dot(normalized_embeddings, normalized_embeddings.T)
                
                # Remove near-duplicates
                keep_indices = set(range(len(unique_articles)))
                for i in range(len(unique_articles)):
                    if i in keep_indices:
                        for j in range(i + 1, len(unique_articles)):
                            if j in keep_indices and similarity_matrix[i, j] > self.similarity_threshold:
                                keep_indices.remove(j)  # Remove duplicate
                
                deduped = [unique_articles[i] for i in sorted(list(keep_indices))]
                stats["semantic_removed"] = len(unique_articles) - len(deduped)
                stats["output"] = len(deduped)
                return deduped, stats
            except Exception as e:
                logging.error(f"Error during SentenceTransformer deduplication: {e}. Falling back to Jaccard.")
        
        # Jaccard similarity fallback
        keep_indices = set(range(len(unique_articles)))
        for i in range(len(unique_articles)):
            if i in keep_indices:
                words_i = set(safe_str(unique_articles[i].get("content")).lower().split())
                for j in range(i + 1, len(unique_articles)):
                    if j in keep_indices:
                        words_j = set(safe_str(unique_articles[j].get("content")).lower().split())
                        intersection = len(words_i.intersection(words_j))
                        union = len(words_i.union(words_j))
                        jaccard = intersection / max(union, 1)
                        if jaccard > self.similarity_threshold:
                            keep_indices.remove(j)
                            
        deduped = [unique_articles[i] for i in sorted(list(keep_indices))]
        stats["semantic_removed"] = len(unique_articles) - len(deduped)
        stats["output"] = len(deduped)
        return deduped, stats
