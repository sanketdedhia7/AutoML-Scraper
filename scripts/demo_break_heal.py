import os
import sys
import json
import shutil
import time
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from pipeline.scraper_runner import ScraperRunner
from pipeline.validator import Validator
from pipeline.cleaner import Cleaner
from pipeline.deduplicator import Deduplicator
from pipeline.quality_scorer import QualityScorer
from pipeline.exporter import Exporter
from healing.healer import Healer
from healing.prompt_templates import PromptTemplates
from healing.repair_logger import RepairLogger
from monitoring.alerts import Alerter
from monitoring.logger import StructuredLogger
from pipeline.utils import ensure_directories
from pipeline.orchestrator import run_etl_stage as run_orchestrated_etl

def reset_selectors():
    """Reset selectors to the broken 'before' state"""
    base_dir = Path(__file__).resolve().parent.parent
    selector_path = base_dir / "scrapers" / "demo_selectors.json"
    initial_selectors = {
        "container": ".article-item",
        "title": "h3.article-title a",
        "author": ".meta-author",
        "publication_date": ".meta-date",
        "content": ".abstract-text"
    }
    with open(selector_path, 'w', encoding='utf-8') as f:
        json.dump(initial_selectors, f, indent=2)
    print("[+] Reset selectors to INITIAL/BEFORE state.")

def copy_fixture(fixture_name):
    """Copy target fixture to current_demo_page.html"""
    base_dir = Path(__file__).resolve().parent.parent
    src = base_dir / "tests" / "fixtures" / fixture_name
    dest = base_dir / "tests" / "fixtures" / "current_demo_page.html"
    shutil.copy(src, dest)
    print(f"[+] Loaded HTML Layout: {fixture_name}")

def run_etl_stage(collector_id, runner, validator, cleaner, deduplicator, scorer, exporter, alerter, logger, timeout=15):
    """Run the ETL pipeline and return results/status"""
    print(f"\n--- Running ETL Stage for: {collector_id} ---")
    try:
        raw_data = runner.get_scraper_output(collector_id, timeout=timeout)
    except Exception as exc:
        print(f"[!] Error fetching dataset for {collector_id}: {exc}. Using fallback.")
        raw_data = runner._get_fallback_data(collector_id)
    print(f"[*] Retrieved {len(raw_data)} raw items.")
    
    # Save raw data
    raw_path = Path("data/raw") / f"{collector_id}.json"
    with open(raw_path, 'w', encoding='utf-8') as f:
        json.dump(raw_data, f, indent=2)
        
    validation_result = validator.validate(raw_data)
    
    if not validation_result["is_valid"]:
        print(f"[!] Validation FAILED: {validation_result['errors']}")
        return {"is_valid": False, "raw_data": raw_data, "errors": validation_result["errors"], "validation_result": validation_result}
        
    print("[+] Validation PASSED.")
    
    # Run the shared ETL stage orchestrator
    etl_res = run_orchestrated_etl(
        collector_id=collector_id,
        raw_data=raw_data,
        cleaner=cleaner,
        deduplicator=deduplicator,
        scorer=scorer,
        exporter=exporter,
        logger=logger,
        persist_intermediate=True
    )
    
    return {"is_valid": True, "raw_data": raw_data, "scored_data": etl_res["scored_data"]}

def main():
    # Ensure raw/cleaned/repairs directories exist on clean clone
    ensure_directories()

    # Instantiate modules
    runner = ScraperRunner()
    validator = Validator(required_fields=["title", "content"])
    cleaner = Cleaner()
    deduplicator = Deduplicator()
    scorer = QualityScorer()
    exporter = Exporter()
    healer = Healer()
    repair_logger = RepairLogger()
    alerter = Alerter()
    logger = StructuredLogger()
    
    collector_id = "demo_scraper"
    
    print("==================================================================")
    print("      SCRApER STUDIO DETERMINISTIC SELF-HEALING DEMO")
    print("==================================================================")
    
    try:
        # Step 1: Initial Success Run (Before Redesign)
        print("\n>>> STEP 1: Run scraper on original layout (before_layout.html)")
        reset_selectors()
        copy_fixture("before_layout.html")
        
        res1 = run_etl_stage(collector_id, runner, validator, cleaner, deduplicator, scorer, exporter, alerter, logger)
        if res1["is_valid"]:
            alerter.send_alert(f"Scraper runs successfully on original layout for {collector_id}.", "info")
        else:
            print("[!] Step 1 failed unexpectedly.")
            return
            
        time.sleep(2)
        
        # Step 2: Break Trigger (Redesign layout, using old selectors)
        print("\n>>> STEP 2: Website redesign occurs! (after_layout.html)")
        copy_fixture("after_layout.html")
        
        res2 = run_etl_stage(collector_id, runner, validator, cleaner, deduplicator, scorer, exporter, alerter, logger)
        if not res2["is_valid"]:
            issue_description = "; ".join(res2["errors"])
            alerter.send_alert(f"Scraper validation failed for {collector_id}: {issue_description}", "error")
            
            # Step 3: Trigger Healing Loop
            print("\n>>> STEP 3: Triggering Bright Data self-healing command...")
            heal_prompt = PromptTemplates.select_prompt(res2["validation_result"])
            
            # Trigger healing (actually updates selector config in demo mode)
            heal_result = healer.trigger_self_healing(collector_id, heal_prompt, auto_approve=True)
            repair_logger.log_repair(collector_id, issue_description, heal_prompt, heal_result)
            
            logger.log("INFO", "Self-heal completed", scraper_id=collector_id, latency_seconds=heal_result.get("latency_seconds", 0))
            
            alerter.send_alert(f"Triggered Scraper Studio self-heal for {collector_id}. Prompt: '{heal_prompt}'", "warning")
            print(f"[+] Healing output: {heal_result.get('message')}")
            
        else:
            print("[!] Step 2 did not fail. Verification cannot proceed.")
            return
            
        time.sleep(2)
        
        # Step 4: Re-run Scraper (After Redesign, using healed selectors)
        print("\n>>> STEP 4: Re-running scraper with healed selectors...")
        res3 = run_etl_stage(collector_id, runner, validator, cleaner, deduplicator, scorer, exporter, alerter, logger)
        if res3["is_valid"]:
            accepted_count = len([a for a in res3["scored_data"] if a.get("quality_score", 0) >= QualityScorer.ACCEPT_THRESHOLD])
            alerter.send_alert(f"Scraper self-healed successfully for {collector_id}. Pipeline resumed and exported {accepted_count} articles.", "info")
            print("\n[+] SUCCESS: Self-healing demo completed successfully!")
        else:
            print("[!] Self-healing verification failed.")
    except Exception as e:
        print(f"[CRITICAL ERROR] Demo pipeline crashed: {e}")
        alerter.send_alert(f"Demo pipeline error: {e}", "critical")


if __name__ == "__main__":
    main()
