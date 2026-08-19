import os
import sys
import json
import shutil
import time
import subprocess
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))


def run_cmd(args):
    print(f"[*] Running: {' '.join(args)}")
    result = subprocess.run(args, capture_output=True, text=True)
    return result

def main():
    base_dir = Path(__file__).resolve().parent.parent
    
    print("==================================================================")
    print("      arXiv AI/ML CURATION & SELF-HEALING END-TO-END DEMO")
    print("==================================================================")
    print("\nNarrative Story:")
    print("1. Scraping real AI/ML research papers from arXiv API.")
    print("2. Detecting structural breakage (redesign layout) and triggering self-heal.")
    print("3. Executing pipeline: Validation -> Cleaning -> Semantic Deduplication -> Scorer.")
    print("4. Output verification & inspection dashboard updates.")
    print("==================================================================")
    
    # Reset and prepare the scraper demo state
    demo_script_path = base_dir / "scripts" / "demo_break_heal.py"
    if not demo_script_path.exists():
        print("[!] demo_break_heal.py script not found!")
        return
        
    print("\n>>> STEP 1: Running Scraper Studio Break-and-Heal storyboard...")
    # This runs the full mock layout break and heal sequence
    p = subprocess.run([sys.executable, str(demo_script_path)], capture_output=True, text=True)
    print(p.stdout)
    if p.returncode != 0:
        print(f"[!] Break-and-heal storyboard failed: {p.stderr}")
        return

    # Step 2: Combine master datasets
    print("\n>>> STEP 2: Running Master Dataset Aggregation and Export...")
    export_script = base_dir / "scripts" / "export_training_data.py"
    p2 = subprocess.run([sys.executable, str(export_script)], capture_output=True, text=True)
    print(p2.stdout)
    
    # Step 3: Run and display Data Quality Report
    print("\n>>> STEP 3: Running Heuristic Quality Validation Spot Checks...")
    report_script = base_dir / "scripts" / "generate_quality_report.py"
    p3 = subprocess.run([sys.executable, str(report_script)], capture_output=True, text=True)
    print(p3.stdout)
    
    print("\n>>> STEP 4: Next Steps for the Hackathon Demo:")
    print("1. Start the FastAPI Product Dashboard:")
    print("   uvicorn monitoring.dashboard:app --reload")
    print("2. Open http://localhost:8000 in your browser.")
    print("3. Toggle to the 'Curated Data' tab to inspect before/after HTML diffs,")
    print("   view quality scores, and spot check rejected articles.")
    print("==================================================================")
    print("[+] DEMO WORKFLOW RUN COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
