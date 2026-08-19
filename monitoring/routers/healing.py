import json
import logging
from fastapi import APIRouter, Request, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from monitoring.dependencies import verify_same_origin
from monitoring.rate_limit import rate_limit
from monitoring.collector_registry import validate_collector_id
from pipeline.utils import PROJECT_ROOT

router = APIRouter()

@router.post("/api/trigger-heal", dependencies=[Depends(verify_same_origin), Depends(rate_limit)])
async def api_trigger_heal(request: Request):
    """Trigger self-healing preview (does not auto-commit)."""
    body = await request.json()
    collector_id = body.get("collector_id", "")
    issue = body.get("issue_description", "Validation failed: empty or broken extraction output")
    broken_url = body.get("broken_url", "")
    if not collector_id or not validate_collector_id(collector_id):
        return JSONResponse({"status": "error", "message": f"Invalid or unrecognized collector_id '{collector_id}'"}, status_code=400)
    
    from healing.healer import Healer
    from healing.repair_logger import RepairLogger
    
    result = Healer().trigger_self_healing(
        collector_id=collector_id,
        issue_description=issue,
        broken_url=broken_url,
        auto_approve=False
    )
    RepairLogger().log_repair(collector_id, issue, prompt="Triggered from UI", result=result)
    return JSONResponse(result)

@router.post("/api/approve-heal", dependencies=[Depends(verify_same_origin), Depends(rate_limit)])
async def api_approve_heal(request: Request):
    """Commit a pending heal after human review."""
    body = await request.json()
    collector_id = body.get("collector_id", "")
    if not collector_id or not validate_collector_id(collector_id):
        return JSONResponse({"status": "error", "message": f"Invalid or unrecognized collector_id '{collector_id}'"}, status_code=400)
    
    from healing.healer import Healer
    from healing.repair_logger import RepairLogger
    
    result = Healer().approve_healing(collector_id)
    RepairLogger().log_repair(collector_id, "Approved via UI", prompt="Approve", result=result)
    return JSONResponse(result)

@router.post("/api/heal-now", dependencies=[Depends(verify_same_origin), Depends(rate_limit)])
async def api_heal_now(request: Request, background_tasks: BackgroundTasks):
    """Trigger background validation and self-healing loop for a collector."""
    body = await request.json()
    col_name = body.get("collector_id", "")
    if not col_name or not validate_collector_id(col_name):
        return JSONResponse({"status": "error", "message": f"Invalid or unrecognized collector_id '{col_name}'"}, status_code=400)
    
    active_scrapers = {}
    mapping_path = PROJECT_ROOT / "scrapers" / "active_scrapers.json"
    if mapping_path.exists():
        try:
            with open(mapping_path, 'r', encoding='utf-8') as f:
                active_scrapers = json.load(f)
        except Exception as e:
            logging.error(f"Error loading active_scrapers.json: {e}")
    col_id = active_scrapers.get(col_name, col_name)
    
    from pipeline.healing_cycle import run_validation_healing_cycle
    from pipeline.utils import update_scraper_state
    
    update_scraper_state(col_name, "healing", articles_extracted=0, validation_errors=["Validation & healing triggered..."])
    background_tasks.add_task(run_validation_healing_cycle, col_name, col_id, True)
    
    return JSONResponse({"status": "success", "message": f"Validation & healing cycle queued for {col_name}."})
