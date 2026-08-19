import sys
import json
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from pipeline.quality_scorer import QualityScorer

def generate_report():
    print("==================================================================")
    print("                 PIPELINE DATA QUALITY REPORT")
    print("==================================================================")
    
    scored_dir = Path("data/scored")
    if not scored_dir.exists():
        print("[!] No scored data found. Run the pipeline first.")
        return
        
    all_articles = []
    for file in scored_dir.glob("*.json"):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                articles = json.load(f)
                all_articles.extend(articles)
        except Exception as e:
            print(f"[!] Error loading {file.name}: {e}")
            
    if not all_articles:
        print("[!] No articles loaded from data/scored/")
        return
        
    threshold = QualityScorer.ACCEPT_THRESHOLD
    total = len(all_articles)
    accepted = [a for a in all_articles if a.get("quality_score", 0) >= threshold]
    rejected = [a for a in all_articles if a.get("quality_score", 0) < threshold]
    
    # Calculate bins using threshold
    bins = {
        "0-30 (Critical Fail)": 0,
        f"30-{int(threshold)} (Rejected)": 0,
        f"{int(threshold)}-70 (Marginal Pass)": 0,
        "70-100 (High Quality)": 0
    }
    
    for a in all_articles:
        score = a.get("quality_score", 0)
        if score < 30:
            bins["0-30 (Critical Fail)"] += 1
        elif score < threshold:
            bins[f"30-{int(threshold)} (Rejected)"] += 1
        elif score < 70:
            bins[f"{int(threshold)}-70 (Marginal Pass)"] += 1
        else:
            bins["70-100 (High Quality)"] += 1
            
    print(f"Total Scraped Rows Analyzed: {total}")
    print(f"Accepted Curation Rows (Score >= {threshold}): {len(accepted)} ({len(accepted)/total*100:.1f}%)")
    print(f"Rejected Curation Rows (Score < {threshold}) : {len(rejected)} ({len(rejected)/total*100:.1f}%)")
    print("\nQuality Score Distribution:")
    for label, count in bins.items():
        bar = "#" * int(count / max(total, 1) * 30)
        print(f"  {label:<25}: {count:<4} {bar}")
        
    # Spot-check Accepted
    print("\n------------------------------------------------------------------")
    print(" SPOT-CHECK: TOP 3 HIGHEST QUALITY ACCEPTED ARTICLES")
    print("------------------------------------------------------------------")
    sorted_accepted = sorted(accepted, key=lambda x: x.get("quality_score", 0), reverse=True)
    for i, a in enumerate(sorted_accepted[:3]):
        print(f"\n[{i+1}] Title: {a.get('title')[:80]}...")
        print(f"    Author   : {a.get('author')}")
        print(f"    URL      : {a.get('url')}")
        print(f"    Final Score: {a.get('quality_score')} / 100")
        print(f"    Breakdown: {a.get('quality_breakdown')}")
        
    # Spot-check Rejected
    print("\n------------------------------------------------------------------")
    print(" SPOT-CHECK: TOP 3 REJECTED (LOW QUALITY) ARTICLES")
    print("------------------------------------------------------------------")
    sorted_rejected = sorted(rejected, key=lambda x: x.get("quality_score", 0))
    for i, a in enumerate(sorted_rejected[:3]):
        print(f"\n[{i+1}] Title: {a.get('title')[:80]}...")
        print(f"    Author   : {a.get('author')}")
        print(f"    Final Score: {a.get('quality_score')} / 100")
        print(f"    Breakdown: {a.get('quality_breakdown')}")
        print(f"    Reason for Rejection: {a.get('rejection_reason')}")
        
    # Before/After Cleaning HTML Snippet
    print("\n------------------------------------------------------------------")
    print(" BEFORE/AFTER HTML BOILERPLATE STRIPPING EXAMPLE")
    print("------------------------------------------------------------------")
    if all_articles:
        sample = all_articles[-1] # Let's show the last one (often the thin mock injected one)
        # Fetch the raw article matching this title
        raw_article = None
        raw_dir = Path("data/raw")
        for file in raw_dir.glob("*.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    raws = json.load(f)
                    for r in raws:
                        if r.get("title") == sample.get("title"):
                            raw_article = r
                            break
            except:
                pass
                
        if raw_article:
            print("\n>>> RAW DATA (With HTML & Ad Banner boilerplate):")
            print(raw_article.get("content", "")[:300] + "...")
            print("\n>>> CLEANED DATA (Stripped to markdown abstract text):")
            print(sample.get("content", "")[:300] + "...")
            print("------------------------------------------------------------------")

if __name__ == "__main__":
    generate_report()
