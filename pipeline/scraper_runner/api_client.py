import time
import requests
from pipeline.utils import TIMEOUT_API_REQUEST
from .fallbacks import check_mock_mode

def trigger_scraper(collector_id, base_url, api_key, logger, url=None, retries=3, backoff_factor=2):
    """
    Queue a scraper job via POST /dca/trigger.
    Returns dict with snapshot_id on success so callers can poll.
    """
    if check_mock_mode(collector_id, api_key):
        return {"status": "triggered", "snapshot_id": "mock_snapshot_123"}

    last_response = None
    for attempt in range(retries):
        try:
            payload = [{"url": url}] if url else []
            response = requests.post(
                f"{base_url}/dca/trigger",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                params={"collector": collector_id, "queue_next": "1"},
                json=payload,
                timeout=TIMEOUT_API_REQUEST,
            )
            last_response = response

            # Hard failures — don't retry
            if response.status_code in (400, 401, 403, 404):
                return {
                    "status": "error",
                    "status_code": response.status_code,
                    "message": f"HTTP {response.status_code}: {response.text}",
                }

            if response.status_code == 200:
                data = response.json()
                # Bright Data returns snapshot_id (sometimes named collection_id)
                snapshot_id = data.get("snapshot_id") or data.get("collection_id") or data.get("id")
                return {"status": "triggered", "snapshot_id": snapshot_id, "raw": data}
                
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                sleep_time = None
                if retry_after:
                    try:
                        sleep_time = float(retry_after)
                    except ValueError:
                        pass
                if sleep_time is None:
                    sleep_time = backoff_factor ** attempt
                logger.log("WARNING", f"Rate limited (429). Sleeping for {sleep_time} seconds based on Retry-After.")
                time.sleep(sleep_time)
                continue

        except requests.RequestException as exc:
            last_response = None
            logger.log("ERROR", f"Request error (attempt {attempt + 1}/{retries}): {exc}")

        # Exponential back-off before retry
        if attempt < retries - 1:
            time.sleep(backoff_factor ** attempt)

    msg = f"Failed after {retries} retries."
    if last_response is not None:
        msg += f" Last HTTP status: {last_response.status_code}"
    return {"status": "error", "message": msg}
