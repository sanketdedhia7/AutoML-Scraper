import time
import uuid
from urllib.parse import urlparse
from fastapi import APIRouter, Request, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from monitoring.dependencies import verify_same_origin
from monitoring.rate_limit import rate_limit_ondemand
from monitoring.job_store import OnDemandJobStore
from monitoring.job_service import execute_ondemand_job
from pipeline.security import resolve_and_validate_ip

router = APIRouter()

@router.post("/api/scrape-url", dependencies=[Depends(verify_same_origin), Depends(rate_limit_ondemand)])
async def api_scrape_url(request: Request, background_tasks: BackgroundTasks):
    """
    On-Demand URL Scraper endpoint:
    - Validates scheme & performs SSRF IP check upfront
    - Enforces 3 req/hr per IP and global/concurrency caps
    - Returns job_id immediately and runs in background
    """
    body = await request.json()
    url = body.get("url", "").strip()
    if not url:
        return JSONResponse({"status": "error", "message": "Missing target URL."}, status_code=400)

    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            return JSONResponse({"status": "error", "message": "Invalid URL scheme or missing hostname."}, status_code=400)
        resolve_and_validate_ip(parsed.hostname)
    except Exception as ve:
        return JSONResponse({"status": "error", "message": f"URL validation failed: {str(ve)}"}, status_code=400)

    job_id = uuid.uuid4().hex
    job = {
        "job_id": job_id,
        "url": url,
        "status": "queued",
        "step_message": "Job queued for processing...",
        "created_at": time.time(),
        "result": None,
        "error": None
    }
    OnDemandJobStore.save_on_demand_job(job)

    background_tasks.add_task(execute_ondemand_job, job_id, url)
    return JSONResponse({"status": "success", "job_id": job_id, "message": "Scrape job queued."})

@router.get("/api/scrape-url/{job_id}")
async def api_get_scrape_job(job_id: str):
    """Poll job status for on-demand URL scrape."""
    jobs = OnDemandJobStore.load_on_demand_jobs()
    job = jobs.get(job_id)
    if not job:
        return JSONResponse({"status": "error", "message": "Job not found."}, status_code=404)
    return JSONResponse(job)
