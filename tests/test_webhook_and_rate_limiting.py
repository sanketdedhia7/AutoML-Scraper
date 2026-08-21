import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from monitoring.alerts import Alerter
from pipeline.quality_scorer import QualityScorer
from monitoring.routes import app, _request_timestamps

def test_alerter_retries_webhook_on_failure(monkeypatch):
    alerter = Alerter()
    alerter.discord_webhook = "https://discord.com/api/webhooks/mock_test_url"
    
    with patch("requests.post") as mock_post:
        # Mock 2 failed attempts (HTTP 500) then success (HTTP 204)
        resp_fail = MagicMock(status_code=500, text="Internal Server Error")
        resp_success = MagicMock(status_code=204, text="")
        mock_post.side_effect = [resp_fail, resp_fail, resp_success]
        
        alerter.send_alert("Test retry alert", severity="info", retries=3, backoff_factor=0)
        assert mock_post.call_count == 3

def test_quality_scorer_authority_hierarchy():
    scorer = QualityScorer()
    
    # 100 — academic/gov
    assert scorer.score_authority({"url": "https://arxiv.org/abs/123"}) == 100.0
    assert scorer.score_authority({"url": "https://cdc.gov/health"}) == 100.0
    
    # 70 — news
    assert scorer.score_authority({"url": "https://reuters.com/world"}) == 70.0
    
    # 60 — blog
    assert scorer.score_authority({"url": "https://techblog.medium.com/post"}) == 60.0
    
    # 50 — neutral/unknown
    assert scorer.score_authority({"url": "https://unknown-company.io/about"}) == 50.0
    
    # 30 — low quality / spam
    assert scorer.score_authority({"url": "https://clickbait-spam-site.net/free"}) == 30.0

def test_api_rate_limiting():
    _request_timestamps.clear()
    client = TestClient(app)
    
    # Patch get_client_ip to return a fixed, predictable IP so the rate limiter
    # accumulates requests under the same key regardless of TestClient's httpx transport.
    with patch("monitoring.rate_limit.get_client_ip", return_value="1.2.3.4"):
        # Make 10 allowed requests
        for _ in range(10):
            resp = client.post("/api/trigger-heal", json={"collector_id": "demo_scraper"})
            assert resp.status_code == 200
            
        # 11th request should be rate limited with HTTP 429
        resp_overflow = client.post("/api/trigger-heal", json={"collector_id": "demo_scraper"})
        assert resp_overflow.status_code == 429
        assert "Rate limit exceeded" in resp_overflow.json()["detail"]

