import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from pipeline.scraper_runner import ScraperRunner
from pipeline.utils import TIMEOUT_API_REQUEST, TIMEOUT_HEAL_SUBPROCESS, TIMEOUT_WAIT_COMPLETION
from monitoring.routes import app

def test_configurable_timeouts_exist():
    assert isinstance(TIMEOUT_API_REQUEST, int)
    assert isinstance(TIMEOUT_HEAL_SUBPROCESS, int)
    assert isinstance(TIMEOUT_WAIT_COMPLETION, int)

@patch("pipeline.robots_checker.RobotsChecker.is_allowed")
def test_wait_for_completion_filters_robots(mock_is_allowed):
    mock_is_allowed.side_effect = lambda url: "disallowed" not in url
    
    runner = ScraperRunner()

    raw_items = [
        {"url": "https://allowed.com/article1", "title": "A1"},
        {"url": "https://disallowed.com/secret", "title": "A2"}
    ]
    
    with patch.object(runner, "get_scraper_output", return_value=runner._filter_by_robots(raw_items)):
        output = runner.wait_for_completion("demo_scraper")
        
        assert len(output) == 1
        assert output[0]["url"] == "https://allowed.com/article1"

def test_api_routes_validate_collector_id():
    client = TestClient(app)
    
    # Invalid collector ID should return HTTP 400
    resp = client.post("/api/trigger-heal", json={"collector_id": "malicious_hacker_id"})
    assert resp.status_code == 400
    assert "Invalid or unrecognized collector_id" in resp.json()["message"]
    
    resp_approve = client.post("/api/approve-heal", json={"collector_id": "malicious_hacker_id"})
    assert resp_approve.status_code == 400
    
    resp_heal_now = client.post("/api/heal-now", json={"collector_id": "malicious_hacker_id"})
    assert resp_heal_now.status_code == 400
    
    # Valid collector ID (demo_scraper) should pass validation (returns 200 or processed status)
    resp_valid = client.post("/api/trigger-heal", json={"collector_id": "demo_scraper"})
    assert resp_valid.status_code == 200
