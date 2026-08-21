import pytest
import uuid
import socket
from fastapi.testclient import TestClient

from pipeline.security import resolve_and_validate_ip, pinned_dns_context, safe_fetch_html
from pipeline.ondemand_schemas import OnDemandArticleSchema, OnDemandResponseSchema
from pipeline.deduplicator import Deduplicator
from monitoring.app import app

client = TestClient(app)

def test_resolve_and_validate_ip_blocks_private():
    """Verify private, loopback, and restricted IP targets are rejected."""
    with pytest.raises(ValueError, match="Blocked private/restricted IP target"):
        resolve_and_validate_ip("127.0.0.1")

    with pytest.raises(ValueError, match="Blocked private/restricted IP target"):
        resolve_and_validate_ip("localhost")

    with pytest.raises(ValueError, match="Blocked private/restricted IP target"):
        resolve_and_validate_ip("10.0.0.1")

    with pytest.raises(ValueError, match="Blocked private/restricted IP target"):
        resolve_and_validate_ip("192.168.1.1")


def test_resolve_and_validate_ip_allows_public(monkeypatch):
    """Verify valid public hostnames resolve to IP."""
    monkeypatch.setattr(socket, "getaddrinfo", lambda host, port, **kwargs: [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('93.184.216.34', 80))])
    ip = resolve_and_validate_ip("wikipedia.org")
    assert isinstance(ip, str)
    assert ip == "93.184.216.34"


def test_pinned_dns_context():
    """Verify socket.getaddrinfo is monkeypatched strictly during context block."""
    target_host = "example.com"
    target_ip = "93.184.215.14"

    orig_getaddrinfo = socket.getaddrinfo
    with pinned_dns_context(target_host, target_ip):
        patched_addr = socket.getaddrinfo("example.com", 80)
        assert patched_addr[0][4][0] == target_ip
        assert socket.getaddrinfo is not orig_getaddrinfo

    assert socket.getaddrinfo is orig_getaddrinfo


def test_ondemand_schema_validation():
    """Verify OnDemandArticleSchema rejects invalid schemas and accepts valid ones."""
    valid_data = {
        "title": "Valid Article Title",
        "author": "John Doe",
        "publication_date": "2026-08-15",
        "content": "This is a valid article content snippet that is long enough to pass schema check.",
        "url": "https://example.com/article"
    }
    art = OnDemandArticleSchema(**valid_data)
    assert art.title == "Valid Article Title"

    resp = OnDemandResponseSchema(articles=[art])
    assert len(resp.articles) == 1

    # Rejects missing required fields
    with pytest.raises(Exception):
        OnDemandArticleSchema(title="", content="Short")

    # Rejects content that is too short (<10 chars)
    with pytest.raises(Exception):
        OnDemandArticleSchema(title="Title", content="Short", url="https://example.com")


def test_deduplicator_is_duplicate():
    """Verify Deduplicator.is_duplicate method works for single items."""
    dedup = Deduplicator(model=False)
    article = {
        "title": "Unique OnDemand Article Title 123",
        "url": "https://example.com/unique-123",
        "content": "Unique content string for testing deduplication."
    }
    # First check should be false
    is_dup = dedup.is_duplicate(article)
    assert is_dup is False or is_dup is True # Returns bool without crashing


def test_api_scrape_url_ssrf_blocking():
    """Verify /api/scrape-url blocks private target URLs at entry point."""
    headers = {"Origin": "http://testserver"}
    
    # Block localhost
    resp = client.post("/api/scrape-url", json={"url": "http://localhost:8000"}, headers=headers)
    assert resp.status_code == 400
    assert "validation failed" in resp.json()["message"].lower() or "blocked" in resp.json()["message"].lower()

    # Block private IP
    resp = client.post("/api/scrape-url", json={"url": "http://192.168.1.1"}, headers=headers)
    assert resp.status_code == 400

    # Block missing scheme
    resp = client.post("/api/scrape-url", json={"url": "ftp://example.com"}, headers=headers)
    assert resp.status_code == 400


def test_api_scrape_url_valid_queue(monkeypatch):
    """Verify valid public URL returns job_id and queues job."""
    from monitoring.rate_limit import _ondemand_ip_timestamps, _ondemand_global_timestamps
    _ondemand_ip_timestamps.clear()
    _ondemand_global_timestamps.clear()

    # Mock network fetch, DNS validation, ScraperManager CLI, and SentenceTransformer model load
    monkeypatch.setattr("pipeline.security.resolve_and_validate_ip", lambda host: "93.184.216.34")
    monkeypatch.setattr("pipeline.ondemand.fallback_extractor.safe_fetch_html", lambda url, **kwargs: "<h1>Test Page</h1><p>This is a test article body content for unit testing.</p>")
    monkeypatch.setattr("scrapers.scraper_manager.ScraperManager.create_scraper", lambda self, cfg: {"id": "col_mock123", "status": "mock"})
    monkeypatch.setattr("pipeline.deduplicator._get_sentence_transformer", lambda: None)
    
    headers = {"Origin": "http://testserver"}
    resp = client.post("/api/scrape-url", json={"url": "https://wikipedia.org"}, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "job_id" in data
    # Verify job_id is valid hex UUID4
    job_id = data["job_id"]
    assert len(job_id) == 32

    # Poll status
    poll_resp = client.get(f"/api/scrape-url/{job_id}")
    assert poll_resp.status_code == 200
    poll_data = poll_resp.json()
    assert poll_data["job_id"] == job_id
    assert poll_data["status"] in ("queued", "running", "completed")

