import pytest
from fastapi.testclient import TestClient

from monitoring.app import app
from monitoring.dashboard import app as app_shim

client = TestClient(app)
client_shim = TestClient(app_shim)

def test_dashboard_shim_reexports_app():
    """Verify that monitoring.dashboard re-exports the exact same FastAPI app."""
    assert app_shim is app

def test_dashboard_html_route():
    """Verify '/' renders HTML with key title and section elements."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    html = response.text
    assert "<title>Conservator's Workshop Ledger</title>" in html
    assert "Conservator's Workshop Ledger" in html
    assert "Specimen Catalog" in html
    assert "Quality Stats" in html
    assert "Repair History" in html

def test_api_dashboard_data_route():
    """Verify '/api/dashboard-data' returns expected JSON key structure."""
    response = client.get("/api/dashboard-data")
    assert response.status_code == 200
    data = response.json()
    assert "scrapers_html" in data
    assert "accepted_articles" in data
    assert "rejected_articles" in data
    assert "dedup_saved" in data
    assert "avg_score" in data
    assert "articles" in data
    assert "quality_stats" in data

def test_api_repairs_route():
    """Verify '/api/repairs' returns repair logs list."""
    response = client.get("/api/repairs")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_mutating_endpoints_same_origin_protection():
    """Verify cross-origin block on mutating endpoints when Origin header mismatches Host."""
    headers = {"origin": "http://malicious-site.com", "host": "localhost:8000"}
    
    resp_trigger = client.post("/api/trigger-heal", json={"collector_id": "demo_scraper"}, headers=headers)
    assert resp_trigger.status_code == 403

    resp_approve = client.post("/api/approve-heal", json={"collector_id": "demo_scraper"}, headers=headers)
    assert resp_approve.status_code == 403

    resp_heal_now = client.post("/api/heal-now", json={"collector_id": "demo_scraper"}, headers=headers)
    assert resp_heal_now.status_code == 403

    resp_demo = client.post("/api/run-demo", headers=headers)
    assert resp_demo.status_code == 403

def test_dashboard_html_detailed_content():
    """Verify that dashboard renders stepper component, buttons, and preview panels correctly."""
    from unittest.mock import patch, mock_open
    
    mock_states = {
        "demo_scraper": {
            "status": "healthy",
            "last_run": "2026-08-14 18:00:00",
            "articles_extracted": 10,
            "validation_errors": []
        },
        "broken_scraper": {
            "status": "unhealthy",
            "last_run": "2026-08-14 18:00:00",
            "articles_extracted": 5,
            "validation_errors": ["Empty output"]
        }
    }
    
    mock_repair_line = '{"collector_id": "broken_scraper", "timestamp": "2026-08-14T18:00:00", "result": {"status": "awaiting_approval", "diff_summary": "Proposed selectors change", "preview_result": "Preview of healed data"}}\n'
    
    def smart_open(filename, *args, **kwargs):
        import io
        fn = str(filename)
        if "active_scrapers.json" in fn:
            return io.StringIO('{"demo_scraper": "col_demo", "broken_scraper": "col_broken"}')
        elif "repairs" in fn or "mock_repair" in fn:
            return io.StringIO(mock_repair_line)
        else:
            return io.StringIO('[]')

    with patch("pipeline.utils.load_scraper_states", return_value=mock_states), \
         patch("monitoring.data_loaders.get_scraper_meta", return_value={
             "demo_scraper": {"display_name": "Demo Scraper", "url": "http://demo.com", "schedule": "daily"},
             "broken_scraper": {"display_name": "Broken Scraper", "url": "http://broken.com", "schedule": "hourly"}
         }), \
         patch("glob.glob") as mock_glob, \
         patch("monitoring.data_loaders.open", side_effect=smart_open):
         
        def side_effect(pattern):
            if "repairs" in pattern:
                return ["mock_repair.jsonl"]
            return []
        mock_glob.side_effect = side_effect
        
        response = client.get("/")
        assert response.status_code == 200
        html = response.text
        
        # 1. Verify Stepper component renders correctly
        assert "class=\"kintsugi-stepper\"" in html or "class='kintsugi-stepper'" in html
        assert "id=\"stepper-demo_scraper\"" in html or "id='stepper-demo_scraper'" in html
        assert "id=\"stepper-broken_scraper\"" in html or "id='stepper-broken_scraper'" in html
        assert "Detected" in html
        assert "Healing" in html
        assert "Awaiting Approval" in html
        assert "Committed" in html
        
        # 2. Verify Preview panel shows when awaiting_approval
        assert "class=\"heal-preview-panel visible\"" in html or "class='heal-preview-panel visible'" in html
        assert "Proposed selectors change" in html
        assert "Preview of healed data" in html
        
        # 3. Verify Buttons have correct data-action and data-collector attributes
        assert "data-action=\"trigger-heal\"" in html or "data-action='trigger-heal'" in html
        assert "data-action=\"heal-now\"" in html or "data-action='heal-now'" in html
        assert "data-action=\"approve-heal\"" in html or "data-action='approve-heal'" in html
        assert "data-collector=\"broken_scraper\"" in html or "data-collector='broken_scraper'" in html

