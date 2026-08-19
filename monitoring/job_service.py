import logging
import threading
from monitoring.job_store import OnDemandJobStore
from pipeline.ondemand_runner import OnDemandRunner

_runner_instance = None
_runner_lock = threading.RLock()

def get_ondemand_runner() -> OnDemandRunner:
    """Singleton getter to prevent instantiating heavy model/deduplicator on every request."""
    global _runner_instance
    if _runner_instance is None:
        with _runner_lock:
            if _runner_instance is None:
                _runner_instance = OnDemandRunner()
    return _runner_instance

def execute_ondemand_job(job_id: str, target_url: str):
    """Executes the on-demand runner and updates the job persistence status."""
    jobs = OnDemandJobStore.load_on_demand_jobs()
    job = jobs.get(job_id)
    if not job:
        return

    job["status"] = "running"
    OnDemandJobStore.save_on_demand_job(job)
    
    def update_progress(msg: str):
        job["step_message"] = msg
        OnDemandJobStore.save_on_demand_job(job)

    try:
        runner = get_ondemand_runner()
        result = runner.run_ondemand_scrape(target_url, update_progress_cb=update_progress)
        job["status"] = "completed"
        job["step_message"] = result.get("message", "Scrape completed.")
        job["extraction_method"] = result.get("extraction_method")
        job["result"] = result
        job["error"] = None
    except ValueError as ve:
        logging.warning(f"On-demand job {job_id} validation error: {ve}")
        job["status"] = "failed"
        job["step_message"] = f"Failed: {str(ve)}"
        job["error"] = str(ve)
    except Exception as exc:
        logging.error(f"On-demand job {job_id} internal execution error: {exc}", exc_info=True)
        job["status"] = "failed"
        job["step_message"] = "Processing error encountered during extraction."
        job["error"] = "An internal error occurred while scraping the target URL."
    
    OnDemandJobStore.save_on_demand_job(job)
