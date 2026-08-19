import pytest
from unittest.mock import patch, MagicMock
from healing.healer import Healer
import os
import json
import subprocess

@pytest.fixture
def healer(monkeypatch):
    monkeypatch.setenv("BRIGHT_DATA_API_KEY", "fake-api-key")
    return Healer()

@patch('subprocess.run')
def test_heal_triggers_bdata_cli_no_auto_approve(mock_run, healer):
    """
    Real CLI call uses `bdata scraper heal` (not brightdata) with no --auto-approve by default,
    and includes --url when a broken_url is provided.
    """
    mock_run.return_value = MagicMock(
        stdout=json.dumps({
            "status": "awaiting_approval",
            "preview_result": "3 rows extracted",
            "diff_summary": "container: .old → .new"
        }),
        returncode=0
    )

    result = healer.trigger_self_healing(
        "col_123",
        "Selectors broken",
        broken_url="https://example.com/broken-page",
        auto_approve=False
    )

    assert mock_run.call_count == 1
    args = mock_run.call_args[0][0]

    # Verify: correct binary name (bdata, not brightdata)
    assert args[0] == "bdata"
    # Verify: --auto-approve is NOT included when auto_approve=False
    assert "--auto-approve" not in args
    # Verify: --url flag is included
    assert "--url" in args
    assert "https://example.com/broken-page" in args
    # Verify: correct subcommand structure
    assert "scraper" in args
    assert "heal" in args
    assert "col_123" in args

    assert result["status"] == "awaiting_approval"
    assert "preview_result" in result
    assert "diff_summary" in result

@patch('subprocess.run')
def test_heal_with_auto_approve_includes_flag(mock_run, healer):
    """When auto_approve=True, --auto-approve must be in the CLI call."""
    mock_run.return_value = MagicMock(
        stdout=json.dumps({"status": "success"}),
        returncode=0
    )

    healer.trigger_self_healing("col_123", "Selectors broken", auto_approve=True)

    args = mock_run.call_args[0][0]
    assert "--auto-approve" in args

@patch('subprocess.run')
@patch('time.time')
def test_heal_records_latency(mock_time, mock_run, healer):
    mock_run.return_value = MagicMock(stdout=json.dumps({"status": "awaiting_approval"}), returncode=0)
    mock_time.side_effect = [100.0, 101.5]

    result = healer.trigger_self_healing("col_123", "Selectors broken")

    assert result["latency_seconds"] == 1.5

@patch('subprocess.run')
def test_heal_handles_cli_not_found(mock_run, healer):
    mock_run.side_effect = FileNotFoundError()

    result = healer.trigger_self_healing("col_123", "Selectors broken")

    assert result["status"] == "awaiting_approval"
    assert "not installed or not in PATH" in result["message"]

def test_mock_mode_returns_awaiting_approval():
    """Mock mode (no real API key) returns awaiting_approval with preview and diff_summary."""
    healer = Healer()
    healer.api_key = "your_api_key_here"  # triggers mock mode

    result = healer.trigger_self_healing("col_123", "Selectors broken", auto_approve=False)

    # In mock mode with auto_approve=False, status should be awaiting_approval
    assert result["status"] == "awaiting_approval"
    assert "preview_result" in result
    assert "diff_summary" in result

def test_mock_mode_auto_approve_returns_success():
    """Mock mode with auto_approve=True returns success immediately."""
    healer = Healer()
    healer.api_key = "your_api_key_here"

    result = healer.trigger_self_healing("col_123", "Selectors broken", auto_approve=True)

    assert result["status"] == "success"

from pipeline.healing_cycle import run_validation_healing_cycle

@patch('pipeline.healing_cycle.ScraperRunner')
@patch('pipeline.healing_cycle.Validator')
@patch('pipeline.healing_cycle.Healer')
@patch('pipeline.healing_cycle.update_scraper_state')
@patch('pipeline.healing_cycle.run_etl_stage')
@patch('pipeline.healing_cycle.time.sleep')
@patch('pipeline.healing_cycle.Alerter')
@patch('pipeline.healing_cycle.Deduplicator')
def test_run_validation_healing_cycle_bounded_retry(mock_dedup, mock_alerter, mock_sleep, mock_run_etl, mock_update, mock_healer_cls, mock_validator_cls, mock_runner_cls):
    """Healing cycle should exit loop after max_attempts if still invalid."""
    mock_runner = MagicMock()
    mock_runner.wait_for_completion.return_value = [{"broken": "data"}]
    mock_runner_cls.return_value = mock_runner
    
    mock_validator = MagicMock()
    mock_validator.validate.return_value = {"is_valid": False, "errors": ["Bad data"]}
    mock_validator_cls.return_value = mock_validator
    
    mock_healer = MagicMock()
    mock_healer.trigger_self_healing.return_value = {"status": "success", "latency_seconds": 1.0}
    mock_healer_cls.return_value = mock_healer
    
    res = run_validation_healing_cycle("demo_scraper", "col_123", auto_approve=True, max_attempts=2)
    
    assert res["is_valid"] is False
    assert res["errors"] == ["Bad data"]
    
    # It should have triggered scraper & validated exactly 2 times
    assert mock_runner.trigger_scraper.call_count == 2
    assert mock_validator.validate.call_count == 2
    # Healer is called only once because after the second fetch, attempt == max_attempts breaks the loop
    assert mock_healer.trigger_self_healing.call_count == 1
    # ETL shouldn't run
    assert mock_run_etl.call_count == 0
    # State update should end with "unhealthy"
    mock_update.assert_called_with("demo_scraper", "unhealthy", articles_extracted=1, validation_errors=["Bad data"])


@patch('pipeline.healing_cycle.ScraperRunner')
@patch('pipeline.healing_cycle.Validator')
@patch('pipeline.healing_cycle.Healer')
@patch('pipeline.healing_cycle.update_scraper_state')
@patch('pipeline.healing_cycle.run_etl_stage')
@patch('pipeline.healing_cycle.time.sleep')
@patch('pipeline.healing_cycle.Alerter')
@patch('pipeline.healing_cycle.Deduplicator')
def test_run_validation_healing_cycle_success_flow(mock_dedup, mock_alerter, mock_sleep, mock_run_etl, mock_update, mock_healer_cls, mock_validator_cls, mock_runner_cls):
    """Simulate validation failure -> self-heal -> re-validation success -> ETL flow."""
    mock_runner = MagicMock()
    mock_runner.wait_for_completion.side_effect = [
        [{"title": "Broken Article"}],
        [{"title": "Healed Article", "publication_date": "2026-08-14"}]
    ]
    mock_runner_cls.return_value = mock_runner

    mock_validator = MagicMock()
    # 1st attempt fails, 2nd attempt passes
    mock_validator.validate.side_effect = [
        {"is_valid": False, "errors": ["Selector mismatch"]},
        {"is_valid": True, "errors": []}
    ]
    mock_validator_cls.return_value = mock_validator

    mock_healer = MagicMock()
    mock_healer.trigger_self_healing.return_value = {"status": "success", "latency_seconds": 1.2}
    mock_healer_cls.return_value = mock_healer

    mock_run_etl.return_value = {
        "accepted_data": [{"title": "Healed Article"}],
        "rejected_data": []
    }

    res = run_validation_healing_cycle("demo_scraper", "col_123", auto_approve=True, max_attempts=3)

    assert res["is_valid"] is True
    assert res["etl_res"]["accepted_data"] == [{"title": "Healed Article"}]

    # Triggers scraper 2 times (attempt 1 and attempt 2)
    assert mock_runner.trigger_scraper.call_count == 2
    # Self-healing triggered 1 time
    assert mock_healer.trigger_self_healing.call_count == 1
    # ETL stage called 1 time
    assert mock_run_etl.call_count == 1
    # Final state update should mark scraper as healthy
    mock_update.assert_called_with("demo_scraper", "healthy", last_run="2026-08-14", articles_extracted=1)


