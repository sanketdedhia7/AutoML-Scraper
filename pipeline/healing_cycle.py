import json
import time
from pathlib import Path
from typing import Dict, Any, List

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
from monitoring.telemetry import (
    SCRAPER_SUCCESS_TOTAL,
    SCRAPER_FAILURE_TOTAL,
    SCRAPER_DURATION_SECONDS,
    HEAL_REQUESTS_TOTAL
)
from pipeline.orchestrator import run_etl_stage
from pipeline.utils import update_scraper_state

def run_validation_healing_cycle(col_name: str, col_id: str, auto_approve: bool = True, max_attempts: int = 3) -> Dict[str, Any]:
    """
    Generalized validation + self-healing loop for Scraper Studio collectors.
    Runs the full lifecycle:
    1. Triggers and fetches raw data
    2. Runs Validator
    3. If invalid, triggers self-healing, re-fetches, and re-validates (bounded by max_attempts)
    4. Runs ETL (clean -> deduplicate -> score -> export)
    5. Updates health status in scraper_states.json & logs performance/rejections.
    """
    runner = ScraperRunner()
    validator = Validator()
    cleaner = Cleaner()
    deduplicator = Deduplicator()
    scorer = QualityScorer()
    exporter = Exporter()
    healer = Healer()
    repair_logger = RepairLogger()
    alerter = Alerter()
    logger = StructuredLogger()
    
    logger.log("INFO", f"=================== [HEALING CYCLE] {col_name} ({col_id}) ===================")
    
    # 1. Update state to healing
    update_scraper_state(col_name, "healing", articles_extracted=0, validation_errors=["Self-healing in progress..."])
    
    try:
        raw_data: List[Dict[str, Any]] = []
        validation_result: Dict[str, Any] = {"is_valid": False, "errors": []}
        
        for attempt in range(1, max_attempts + 1):
            # Trigger scraper and fetch raw data
            logger.log("INFO", f"Fetching data from scraper {col_name} (Attempt {attempt}/{max_attempts})...")
            start_time = time.time()
            runner.trigger_scraper(col_id)
            raw_data = runner.wait_for_completion(col_id)
            duration = time.time() - start_time
            SCRAPER_DURATION_SECONDS.labels(collector_id=col_name).observe(duration)
            
            # Save raw data
            raw_path = Path("data/raw") / f"{col_name}.json"
            raw_path.parent.mkdir(parents=True, exist_ok=True)
            with open(raw_path, 'w', encoding='utf-8') as f:
                json.dump(raw_data, f, indent=2)
                
            # 2. Validate
            logger.log("INFO", "Validating raw data...")
            validation_result = validator.validate(raw_data)
            
            # 3. Handle healing if invalid
            if validation_result["is_valid"]:
                break
                
            logger.log("WARNING", f"Validation failed: {validation_result['errors']}")
            issue_description = "; ".join(validation_result["errors"])
            
            if attempt == max_attempts:
                break
                
            alerter.send_alert(f"Validation failed for {col_name}, triggering self-healing: {issue_description}", "warning")
            
            # Update state to reflect unhealthy and healing
            update_scraper_state(col_name, "healing", articles_extracted=len(raw_data), validation_errors=validation_result["errors"])
            
            # Select prompt and heal
            heal_prompt = PromptTemplates.select_prompt(validation_result)
            logger.log("INFO", f"Triggering self-healing (auto_approve={auto_approve})...")
            HEAL_REQUESTS_TOTAL.labels(collector_id=col_name).inc()
            heal_result = healer.trigger_self_healing(col_id, heal_prompt, auto_approve=auto_approve)
            
            # Log repair attempt
            repair_logger.log_repair(col_id, issue_description, heal_prompt, heal_result)
            
            if heal_result.get("status") in ("success", "awaiting_approval"):
                logger.log("INFO", f"Self-healing succeeded or is awaiting approval: {heal_result.get('status')}")
                logger.log("INFO", "Self-heal completed", scraper_id=col_name, latency_seconds=heal_result.get("latency_seconds", 0))
                
                # If auto-approved, re-run scraper to get healed data
                if auto_approve or heal_result.get("status") == "success":
                    logger.log("INFO", "Re-triggering scraper with healed selectors...")
                    # Give it a tiny sleep to allow selector changes to propagate in API
                    time.sleep(1)
                    continue
                else:
                    # Awaiting approval, so break loop and don't retry until user approves
                    break
            else:
                err_msg = heal_result.get("message", "Unknown healer error")
                logger.log("ERROR", f"Self-healing failed: {err_msg}")
                alerter.send_alert(f"Self-healing failed for {col_name}: {err_msg}", "critical")
                update_scraper_state(col_name, "error", articles_extracted=len(raw_data), validation_errors=validation_result["errors"] + [f"Heal failed: {err_msg}"])
                return {"is_valid": False, "raw_data": raw_data, "errors": validation_result["errors"]}

        # Update status if still invalid
        if not validation_result["is_valid"]:
            logger.log("WARNING", f"Scraper {col_name} remains invalid after healing attempt(s).")
            update_scraper_state(col_name, "unhealthy", articles_extracted=len(raw_data), validation_errors=validation_result["errors"])
            SCRAPER_FAILURE_TOTAL.labels(collector_id=col_name).inc()
            return {"is_valid": False, "raw_data": raw_data, "errors": validation_result["errors"]}

        # 4. Run the ETL Stage if valid
        logger.log("INFO", "Validation passed. Running ETL stage...")
        etl_res = run_etl_stage(
            collector_id=col_name,
            raw_data=raw_data,
            cleaner=cleaner,
            deduplicator=deduplicator,
            scorer=scorer,
            exporter=exporter,
            logger=logger,
            persist_intermediate=True
        )
        
        # 5. Update state to healthy
        last_run_date = raw_data[0].get("publication_date", "recent") if raw_data else "recent"
        update_scraper_state(col_name, "healthy", last_run=last_run_date, articles_extracted=len(raw_data))
        
        SCRAPER_SUCCESS_TOTAL.labels(collector_id=col_name).inc()
        accepted_count = len(etl_res["accepted_data"])
        alerter.send_alert(f"Pipeline completed successfully for {col_name}. Exported {accepted_count} articles.", "info")
        return {"is_valid": True, "raw_data": raw_data, "etl_res": etl_res}
        
    except Exception as e:
        logger.log("ERROR", f"Exception in validation/healing cycle for {col_name}: {e}")
        alerter.send_alert(f"Pipeline error for {col_name}: {e}", "critical")
        update_scraper_state(col_name, "error", articles_extracted=0, validation_errors=[str(e)])
        SCRAPER_FAILURE_TOTAL.labels(collector_id=col_name).inc()
        return {"is_valid": False, "errors": [str(e)]}
