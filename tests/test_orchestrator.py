import pytest
import shutil
from pathlib import Path
from unittest.mock import MagicMock
from pipeline.orchestrator import run_etl_stage

def test_run_etl_stage_creates_directories():
    base_dir = Path(__file__).resolve().parent.parent
    cleaned_dir = base_dir / "data/cleaned"
    deduped_dir = base_dir / "data/deduplicated"
    scored_dir = base_dir / "data/scored"

    # Save initial state and remove directories if they exist
    dirs = [cleaned_dir, deduped_dir, scored_dir]
    existed = {}
    for d in dirs:
        existed[d] = d.exists()
        if d.exists():
            # Delete so we can verify the orchestrator creates them
            shutil.rmtree(d)

    try:
        # Create mocks
        mock_cleaner = MagicMock()
        mock_cleaner.clean_article.side_effect = lambda x: x
        
        mock_deduplicator = MagicMock()
        mock_deduplicator.deduplicate.return_value = ([], {"input": 0, "exact_removed": 0, "semantic_removed": 0, "output": 0})
        
        mock_scorer = MagicMock()
        mock_scorer.score_batch.return_value = ([], {"total": 0, "accepted": 0, "rejected": 0, "rejection_rate_pct": 0})
        
        mock_exporter = MagicMock()
        mock_logger = MagicMock()

        # Run orchestrator
        run_etl_stage(
            collector_id="test_orchestrator_temp",
            raw_data=[],
            cleaner=mock_cleaner,
            deduplicator=mock_deduplicator,
            scorer=mock_scorer,
            exporter=mock_exporter,
            logger=mock_logger,
            persist_intermediate=True
        )

        # Assert directories are successfully created
        assert cleaned_dir.exists(), "cleaned directory should be created"
        assert deduped_dir.exists(), "deduplicated directory should be created"
        assert scored_dir.exists(), "scored directory should be created"

    finally:
        # Clean up temporary test files created
        for d in dirs:
            temp_file = d / "test_orchestrator_temp.json"
            if temp_file.exists():
                temp_file.unlink()
            # If the directory did not exist before the test, remove it
            if not existed[d] and d.exists():
                try:
                    shutil.rmtree(d)
                except Exception:
                    pass
