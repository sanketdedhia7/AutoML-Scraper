import json
from pipeline.utils import PROJECT_ROOT, is_mock_mode

def check_mock_mode(collector_id: str, api_key: str) -> bool:
    return is_mock_mode(collector_id, api_key)

def get_fallback_data(collector_id, logger) -> list:
    """Return domain-differentiated local mock data when API is unavailable."""
    cid_str = str(collector_id).lower()
    if "medical" in cid_str:
        target_mock = PROJECT_ROOT / "data" / "medical_mock.json"
    elif "legal" in cid_str:
        target_mock = PROJECT_ROOT / "data" / "legal_mock.json"
    else:
        target_mock = PROJECT_ROOT / "data" / "real_dataset_mock.json"

    if target_mock.exists():
        try:
            with open(target_mock, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for item in data:
                item["source"] = f"{collector_id} [MOCK FALLBACK]"
            return data
        except Exception as e:
            logger.log("WARNING", f"Failed to load fallback JSON file {target_mock}: {e}")

    return [
        {
            "title": f"Fallback Mock Article for {collector_id}",
            "author": "Author Unknown",
            "publication_date": "2026-08-13",
            "content": "Fallback content: real API unavailable and no local mock file found.",
            "url": f"https://example.com/fallback-{collector_id}",
            "source": f"{collector_id} [MOCK FALLBACK]",
        }
    ]
