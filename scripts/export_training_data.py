import sys
import os
import json
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from pipeline.exporter import Exporter
from pipeline.quality_scorer import QualityScorer

def export_all():
    scored_dir = Path("data/scored")
    all_scored_articles = []
    
    if not scored_dir.exists():
        print("[!] No scored data directory found. Please run scripts/run_pipeline.py first.")
        return
        
    for file_path in scored_dir.glob("*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                articles = json.load(f)
                all_scored_articles.extend(articles)
        except Exception as e:
            print(f"[!] Error reading {file_path.name}: {e}")
            
    if not all_scored_articles:
        print("[!] No scored articles found to export.")
        return
        
    print(f"[*] Found {len(all_scored_articles)} scored articles in total.")
    
    # Filter for high quality articles using centralized threshold
    threshold = QualityScorer.ACCEPT_THRESHOLD
    high_quality_articles = [a for a in all_scored_articles if a.get("quality_score", 0) >= threshold]
    print(f"[*] Filtered down to {len(high_quality_articles)} articles with quality_score >= {threshold}")

    
    exporter = Exporter()
    exporter.export_to_jsonl(high_quality_articles, "combined_training_data.jsonl")
    print("[+] Combined training dataset generated successfully.")

if __name__ == "__main__":
    export_all()
