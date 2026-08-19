import time
from collections import defaultdict
from fastapi import Request, HTTPException
from monitoring.dependencies import get_client_ip

_ondemand_ip_timestamps = defaultdict(list)
_ondemand_global_timestamps = []
_request_timestamps = defaultdict(list)

ON_DEMAND_PER_IP_MAX = 50
ON_DEMAND_GLOBAL_MAX = 100
ON_DEMAND_WINDOW_SECONDS = 3600
MAX_CONCURRENT_JOBS = 10

RATE_LIMIT_MAX_REQUESTS = 10
RATE_LIMIT_WINDOW_SECONDS = 60

def _prune_rate_limit_dicts(now: float):
    """Evict stale IP entries from rate limiter dicts to prevent unbounded memory growth."""
    stale_ips = [ip for ip, ts_list in _request_timestamps.items() if not [t for t in ts_list if now - t < RATE_LIMIT_WINDOW_SECONDS]]
    for ip in stale_ips:
        del _request_timestamps[ip]

    stale_ondemand_ips = [ip for ip, ts_list in _ondemand_ip_timestamps.items() if not [t for t in ts_list if now - t < ON_DEMAND_WINDOW_SECONDS]]
    for ip in stale_ondemand_ips:
        del _ondemand_ip_timestamps[ip]

async def rate_limit(request: Request):
    client_ip = get_client_ip(request)
    now = time.time()
    _prune_rate_limit_dicts(now)

    timestamps = [ts for ts in _request_timestamps[client_ip] if now - ts < RATE_LIMIT_WINDOW_SECONDS]
    _request_timestamps[client_ip] = timestamps
    
    if len(timestamps) >= RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Maximum 10 requests per minute allowed."
        )
    _request_timestamps[client_ip].append(now)

async def rate_limit_ondemand(request: Request):
    client_ip = get_client_ip(request)
    now = time.time()
    _prune_rate_limit_dicts(now)
    
    # 1. Per-IP Check
    ip_ts = [ts for ts in _ondemand_ip_timestamps[client_ip] if now - ts < ON_DEMAND_WINDOW_SECONDS]
    _ondemand_ip_timestamps[client_ip] = ip_ts
    if len(ip_ts) >= ON_DEMAND_PER_IP_MAX:
        raise HTTPException(
            status_code=429,
            detail=f"Per-IP rate limit exceeded ({ON_DEMAND_PER_IP_MAX} requests/hour allowed)."
        )

    # 2. Global Check
    global _ondemand_global_timestamps
    _ondemand_global_timestamps = [ts for ts in _ondemand_global_timestamps if now - ts < ON_DEMAND_WINDOW_SECONDS]
    if len(_ondemand_global_timestamps) >= ON_DEMAND_GLOBAL_MAX:
        raise HTTPException(
            status_code=429,
            detail=f"Global rate limit exceeded ({ON_DEMAND_GLOBAL_MAX} requests/hour across system)."
        )

    # 3. Concurrency Check (using file-backed job store)
    from monitoring.job_store import OnDemandJobStore
    jobs = OnDemandJobStore.load_on_demand_jobs()
    active_jobs = sum(1 for j in jobs.values() if j.get("status") in ("queued", "running"))
    if active_jobs >= MAX_CONCURRENT_JOBS:
        raise HTTPException(
            status_code=429,
            detail=f"System busy. Maximum concurrent jobs limit ({MAX_CONCURRENT_JOBS}) reached. Please try again shortly."
        )

    _ondemand_ip_timestamps[client_ip].append(now)
    _ondemand_global_timestamps.append(now)
