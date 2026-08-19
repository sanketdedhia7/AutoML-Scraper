import pytest
from unittest.mock import patch, MagicMock
from pipeline.scraper_runner import ScraperRunner
import os

@pytest.fixture
def runner():
    os.environ["BRIGHT_DATA_API_KEY"] = "fake-api-key"
    return ScraperRunner()

@patch('requests.post')
def test_trigger_scraper_success(mock_post, runner):
    """POST /dca/trigger returns snapshot_id on success."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"snapshot_id": "snap_abc123"}
    mock_post.return_value = mock_response

    result = runner.trigger_scraper("fake_col_id")
    assert result["status"] == "triggered"
    assert result["snapshot_id"] == "snap_abc123"
    assert mock_post.call_count == 1
    # Verify the correct real endpoint is called
    call_url = mock_post.call_args[0][0]
    assert "/dca/trigger" in call_url

@patch('time.sleep')
@patch('requests.post')
def test_trigger_scraper_retries_on_503(mock_post, mock_sleep, runner):
    """503s trigger exponential back-off retries; success on 3rd attempt."""
    mock_response_err = MagicMock()
    mock_response_err.status_code = 503
    
    mock_response_ok = MagicMock()
    mock_response_ok.status_code = 200
    mock_response_ok.json.return_value = {"snapshot_id": "snap_retried"}
    
    mock_post.side_effect = [mock_response_err, mock_response_err, mock_response_ok]
    
    result = runner.trigger_scraper("fake_col_id", retries=3)
    assert result["status"] == "triggered"
    assert result["snapshot_id"] == "snap_retried"
    assert mock_post.call_count == 3
    assert mock_sleep.call_count == 2

@patch('time.sleep')
@patch('requests.post')
def test_trigger_scraper_respects_retry_after(mock_post, mock_sleep, runner):
    """429 responses parse and sleep for the duration in the Retry-After header."""
    mock_response_429 = MagicMock()
    mock_response_429.status_code = 429
    mock_response_429.headers = {"Retry-After": "15"}
    
    mock_response_ok = MagicMock()
    mock_response_ok.status_code = 200
    mock_response_ok.json.return_value = {"snapshot_id": "snap_after_429"}
    
    mock_post.side_effect = [mock_response_429, mock_response_ok]
    
    result = runner.trigger_scraper("fake_col_id", retries=2)
    
    assert result["status"] == "triggered"
    assert result["snapshot_id"] == "snap_after_429"
    assert mock_post.call_count == 2
    mock_sleep.assert_called_once_with(15.0)

@patch('requests.get')
@patch('requests.post')
def test_get_scraper_output_fallback(mock_post, mock_get, runner):
    """When /dca/trigger succeeds but /dca/dataset fails, fall back to mock data."""
    # Trigger succeeds
    trigger_resp = MagicMock()
    trigger_resp.status_code = 200
    trigger_resp.json.return_value = {"snapshot_id": "snap_xyz"}
    mock_post.return_value = trigger_resp

    # Dataset fetch fails
    dataset_resp = MagicMock()
    dataset_resp.status_code = 401
    dataset_resp.text = "Unauthorized"
    mock_get.return_value = dataset_resp

    result = runner.get_scraper_output("fake_col_id")
    assert isinstance(result, list)
    assert len(result) > 0
    assert "title" in result[0]
    # Verify dataset endpoint was called with correct params
    call_url = mock_get.call_args[0][0]
    assert "/dca/dataset" in call_url

@patch('requests.get')
def test_get_scraper_output_shapes(mock_get, runner):
    """Test get_scraper_output with different response shapes."""
    # 1. API returns a list (Normal Case)
    resp_list = MagicMock()
    resp_list.status_code = 200
    resp_list.json.return_value = [{"title": "API Article", "content": "Some content"}]
    mock_get.return_value = resp_list
    
    res = runner.get_scraper_output("fake_col_id", snapshot_id="snap_123")
    assert isinstance(res, list)
    assert len(res) == 1
    assert res[0]["title"] == "API Article"

    # 2. API returns a single article dict (Coerced to list)
    resp_dict = MagicMock()
    resp_dict.status_code = 200
    resp_dict.json.return_value = {"title": "Single Article", "content": "Just one article"}
    mock_get.return_value = resp_dict
    
    res = runner.get_scraper_output("fake_col_id", snapshot_id="snap_123")
    assert isinstance(res, list)
    assert len(res) == 1
    assert res[0]["title"] == "Single Article"

    # 3. API returns status/error dict (Falls back)
    resp_err = MagicMock()
    resp_err.status_code = 200
    resp_err.json.return_value = {"status": "error", "message": "API broke"}
    mock_get.return_value = resp_err
    
    res = runner.get_scraper_output("fake_col_id", snapshot_id="snap_123")
    assert isinstance(res, list)
    assert len(res) > 0
    # Fallback marker should be in source
    assert "MOCK FALLBACK" in res[0].get("source", "")
