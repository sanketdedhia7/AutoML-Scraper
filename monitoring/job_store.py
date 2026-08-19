import json
import time
import logging
import threading
from typing import Dict, Any
from pipeline.utils import PROJECT_ROOT, atomic_write_json

JOBS_FILE_PATH = PROJECT_ROOT / "data" / "on_demand_jobs.json"
_jobs_lock = threading.RLock()

class OnDemandJobStore:
    """Thread-safe persistent file-backed store for tracking on-demand scrapes."""

    @staticmethod
    def load_on_demand_jobs() -> Dict[str, Dict[str, Any]]:
        """Load jobs from disk store and evict jobs older than 24 hours."""
        with _jobs_lock:
            if not JOBS_FILE_PATH.exists():
                return {}
            try:
                with open(JOBS_FILE_PATH, 'r', encoding='utf-8') as f:
                    jobs = json.load(f)
                now = time.time()
                pruned_jobs = {
                    jid: j for jid, j in jobs.items()
                    if now - j.get("created_at", now) < 86400
                }
                if len(pruned_jobs) != len(jobs):
                    atomic_write_json(JOBS_FILE_PATH, pruned_jobs)
                return pruned_jobs
            except Exception as e:
                logging.warning(f"Failed to load on-demand jobs from disk: {e}")
                return {}

    @staticmethod
    def save_on_demand_job(job: Dict[str, Any]):
        """Persist a single job update to disk in a thread-safe atomic manner."""
        with _jobs_lock:
            jobs = OnDemandJobStore.load_on_demand_jobs()
            jobs[job["job_id"]] = job
            atomic_write_json(JOBS_FILE_PATH, jobs)
