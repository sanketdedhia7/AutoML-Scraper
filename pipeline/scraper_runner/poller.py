import time
import requests
from pipeline.utils import update_scraper_state, TIMEOUT_API_REQUEST, TIMEOUT_WAIT_COMPLETION
from .fallbacks import check_mock_mode, get_fallback_data
from .api_client import trigger_scraper

def filter_by_robots(items: list, robots_checker, logger) -> list:
    """Filter items based on robots.txt compliance."""
    if not isinstance(items, list):
        return items
    allowed_items = []
    for item in items:
        url = item.get("url") if isinstance(item, dict) else None
        if not url or robots_checker.is_allowed(url):
            allowed_items.append(item)
        else:
            logger.log("WARNING", f"Skipping item due to robots.txt restriction: {url}")
    return allowed_items

def fetch_scraper_output(collector_id, base_url, api_key, logger, robots_checker, snapshot_id=None, timeout=None):
    if timeout is None:
        timeout = TIMEOUT_API_REQUEST

    # Special case: deterministic demo scraper (HTML fixture parser)
    if collector_id == "demo_scraper" or str(collector_id).startswith("col_demo"):
        from scrapers.collector_registry import ScraperManager
        return ScraperManager()._run_demo_scraper_parser()

    if check_mock_mode(collector_id, api_key):
        return get_fallback_data(collector_id, logger)

    # If we don't have a snapshot_id, trigger first and use that id
    if not snapshot_id:
        trigger_result = trigger_scraper(collector_id, base_url, api_key, logger)
        if trigger_result.get("status") != "triggered":
            logger.log("WARNING", f"Trigger failed: {trigger_result.get('message')}. Using fallback.")
            return get_fallback_data(collector_id, logger)
        snapshot_id = trigger_result.get("snapshot_id")

    if not snapshot_id:
        return get_fallback_data(collector_id, logger)

    try:
        response = requests.get(
            f"{base_url}/dca/dataset",
            headers={"Authorization": f"Bearer {api_key}"},
            params={"id": snapshot_id},
            timeout=timeout,
        )
        if response.status_code != 200:
            logger.log("WARNING", f"/dca/dataset returned {response.status_code}. Using fallback.")
            return get_fallback_data(collector_id, logger)
        data = response.json()
        items = []
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            if "content" in data or "title" in data:
                items = [data]
            else:
                logger.log("WARNING", f"/dca/dataset returned a status/error dict instead of list: {data}. Using fallback.")
                return get_fallback_data(collector_id, logger)
        else:
            logger.log("WARNING", f"/dca/dataset returned unexpected shape: {type(data)}. Using fallback.")
            return get_fallback_data(collector_id, logger)

        return filter_by_robots(items, robots_checker, logger)
    except Exception as exc:
        logger.log("ERROR", f"Error fetching dataset: {exc}. Using fallback.")
        return get_fallback_data(collector_id, logger)

def wait_for_completion(collector_id, base_url, api_key, logger, robots_checker, snapshot_id=None, timeout=None, get_output_fn=None):
    if timeout is None:
        timeout = TIMEOUT_WAIT_COMPLETION

    fetch_fn = get_output_fn if get_output_fn else (lambda cid: fetch_scraper_output(cid, base_url, api_key, logger, robots_checker))

    if check_mock_mode(collector_id, api_key):
        return fetch_fn(collector_id)

    if not snapshot_id:
        trigger_result = trigger_scraper(collector_id, base_url, api_key, logger)
        if trigger_result.get("status") != "triggered":
            return get_fallback_data(collector_id, logger)
        snapshot_id = trigger_result.get("snapshot_id")

    start = time.time()
    while time.time() - start < timeout:
        try:
            response = requests.get(
                f"{base_url}/dca/dataset",
                headers={"Authorization": f"Bearer {api_key}"},
                params={"id": snapshot_id},
                timeout=30,
            )
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    return filter_by_robots(data, robots_checker, logger)
                if isinstance(data, dict) and data.get("status") == "failed":
                    logger.log("WARNING", f"Snapshot {snapshot_id} failed on Bright Data side.")
                    return filter_by_robots(get_fallback_data(collector_id, logger), robots_checker, logger)
        except Exception as exc:
            logger.log("ERROR", f"Polling error: {exc}")
        time.sleep(10)

    err_msg = f"Snapshot {snapshot_id} did not complete within {timeout}s"
    logger.log("ERROR", err_msg)
    update_scraper_state(collector_id, status="error", validation_errors=[err_msg])
    raise TimeoutError(err_msg)
