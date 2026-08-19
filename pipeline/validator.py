from typing import List, Dict, Any

class Validator:
    def __init__(self, min_articles=1, required_fields=None):
        self.min_articles = min_articles
        self.required_fields = required_fields if required_fields is not None else ["title", "content"]
    
    def validate(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate scraper output"""
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Coerce unexpected shapes
        if not isinstance(data, list):
            if isinstance(data, dict):
                if "title" in data or "content" in data:
                    data = [data]
                else:
                    result["is_valid"] = False
                    result["errors"].append(f"Invalid output shape: received dict instead of list. Content: {data}")
                    return result
            else:
                result["is_valid"] = False
                result["errors"].append(f"Invalid output shape: expected list, received {type(data).__name__}")
                return result
        
        # Check for empty output
        if len(data) == 0:
            result["is_valid"] = False
            result["errors"].append("Empty output: scraper returned 0 articles")
            return result
        
        # Check minimum articles
        if len(data) < self.min_articles:
            result["warnings"].append(
                f"Low output: only {len(data)} articles (expected >= {self.min_articles})"
            )
        
        # Check required fields — count per-record, then decide on the rate.
        # A single article missing a byline/abstract is normal; we only
        # consider the batch corrupt when >30% of records are affected.
        # Note: missing_fields_set is still exposed so downstream code (healer
        # prompt routing) can inspect *which* fields are sparse.
        missing_fields_set: set = set()
        missing_count = 0
        for article in data:
            article_missing = [
                field for field in self.required_fields
                if not article.get(field)  # catches both absent key and None/empty
            ]
            if article_missing:
                missing_count += 1
                missing_fields_set.update(article_missing)

        missing_rate = missing_count / len(data)

        # Always surface which fields are sparse as a diagnostic warning.
        if missing_fields_set:
            result["warnings"].append(
                f"Sparse fields detected: {sorted(missing_fields_set)} "
                f"({missing_count}/{len(data)} articles affected)"
            )

        # Only hard-fail when the rate crosses the threshold.
        if missing_rate > 0.3:
            result["is_valid"] = False
            result["errors"].append(
                f"High missing rate: {missing_rate*100:.1f}% of articles "
                f"missing required fields {sorted(missing_fields_set)}"
            )

        # Expose the missing-fields set for self-healing prompt selection.
        result["missing_fields"] = sorted(missing_fields_set)
        result["missing_rate"] = round(missing_rate, 4)

        return result
