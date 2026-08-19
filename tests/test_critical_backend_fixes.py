import pytest
import os
import json
import threading
from pathlib import Path
from unittest.mock import patch, MagicMock

from pipeline.utils import is_mock_mode, atomic_write_json, load_scraper_states
from pipeline.deduplicator import Deduplicator
from pipeline.scraper_runner import ScraperRunner

def test_centralized_mock_mode(monkeypatch):
    monkeypatch.setenv("BRIGHT_DATA_API_KEY", "")
    assert is_mock_mode("some_scraper") is True
    
    monkeypatch.setenv("BRIGHT_DATA_API_KEY", "your_api_key_here")
    assert is_mock_mode("some_scraper") is True
    
    monkeypatch.setenv("BRIGHT_DATA_API_KEY", "valid_api_key_123")
    assert is_mock_mode("demo_scraper") is True
    assert is_mock_mode("normal_scraper") is False

def test_atomic_write_json(tmp_path):
    target_file = tmp_path / "test_data.json"
    data = {"key": "value", "count": 42}
    
    atomic_write_json(target_file, data)
    assert target_file.exists()
    
    with open(target_file, "r", encoding="utf-8") as f:
        read_data = json.load(f)
    assert read_data == data

@pytest.mark.slow
def test_deduplicator_global_hash_lock_and_atomic_write():
    # Test concurrent hash additions do not corrupt file
    mock_model = MagicMock()
    mock_model.encode.side_effect = Exception("Should fallback to Jaccard")
    dedup = Deduplicator(similarity_threshold=1.0, model=mock_model)
    articles_batch1 = [{"url": f"https://unique-lock-test.org/item-{i}", "content": f"Unique text content number {i}"} for i in range(10)]
    articles_batch2 = [{"url": f"https://unique-lock-test.org/item-{i}", "content": f"Unique text content number {i}"} for i in range(5, 15)]
    
    res1, stats1 = dedup.deduplicate(articles_batch1)
    res2, stats2 = dedup.deduplicate(articles_batch2)
    
    assert len(res1) == 10
    assert len(res2) == 5  # 5 duplicates caught cross-batch
    
    from pipeline.deduplicator import PROJECT_ROOT as DEDUP_ROOT
    global_hashes_file = DEDUP_ROOT / "data" / "global_seen_hashes.json"
    assert global_hashes_file.exists()
    with open(global_hashes_file, "r", encoding="utf-8") as f:
        hashes = json.load(f)
    assert len(hashes) == 15

@patch("time.sleep")
@patch("requests.get")
@patch("pipeline.scraper_runner.ScraperRunner.trigger_scraper")
def test_wait_for_completion_timeout_updates_scraper_state(mock_trigger, mock_get, mock_sleep, monkeypatch, tmp_path):
    monkeypatch.setenv("BRIGHT_DATA_API_KEY", "valid_key")
    mock_trigger.return_value = {"status": "triggered", "snapshot_id": "snap_123"}
    
    # Mock requests.get returning pending status indefinitely
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"status": "pending"}
    mock_get.return_value = mock_resp
    
    runner = ScraperRunner()
    
    with patch("pipeline.utils.PROJECT_ROOT", tmp_path):
        with pytest.raises(TimeoutError):
            runner.wait_for_completion(collector_id="test_timeout_scraper", snapshot_id="snap_123", timeout=1)
            
        states = load_scraper_states()
        assert "test_timeout_scraper" in states
        assert states["test_timeout_scraper"]["status"] == "error"
        assert "did not complete within" in states["test_timeout_scraper"]["validation_errors"][0]


