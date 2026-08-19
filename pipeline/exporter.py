import json
from pathlib import Path
from typing import List, Dict, Any
from pipeline.utils import PROJECT_ROOT

class Exporter:
    def __init__(self, output_dir=None):
        if output_dir is None:
            self.output_dir = PROJECT_ROOT / "data" / "exports"
        else:
            self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_to_jsonl(self, articles: List[Dict[str, Any]], filename: str, append: bool = True):
        """Export articles to JSONL format (appends by default to avoid overwriting previous dataset runs)"""
        output_path = self.output_dir / filename
        mode = 'a' if append else 'w'
        
        with open(output_path, mode, encoding='utf-8') as f:
            for article in articles:
                # Format for LLM training
                training_example = {
                    "text": f"Title: {article.get('title', '')}\n\n{article.get('content', '')}",
                    "meta": {
                        "url": article.get("url", ""),
                        "author": article.get("author") or article.get("authors") or "",
                        "publication_date": article.get("publication_date", ""),
                        "quality_score": article.get("quality_score", 0),
                        "source": article.get("source", "")
                    }
                }
                f.write(json.dumps(training_example, ensure_ascii=False) + "\n")
        
        print(f"Exported {len(articles)} articles to {output_path}")
        return output_path
