import datetime
import uuid
import logging
from pipeline.utils import PROJECT_ROOT, ensure_directories, atomic_write_json

class QuarantineRepository:
    """Handles persistence of quarantined/pending review scrapers."""

    def save_to_quarantine(self
        , target_url: str
        , processed_articles: list
        , extraction_source: str
    ) -> str:
        """Create a quarantine record, write to disk, log event, and return the collector_id."""
        repairs_dir = PROJECT_ROOT / "data" / "repairs"
        ensure_directories()
        
        collector_id = f"ondemand_{uuid.uuid4().hex[:6]}"
        quarantine_record = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "collector_id": collector_id,
            "broken_url": target_url,
            "issue": f"On-demand user submission ({extraction_source})",
            "issue_description": f"On-demand user submission ({extraction_source})",
            "prompt": "User On-Demand Request",
            "status": "awaiting_approval",
            "preview_result": processed_articles,
            "diff_summary": f"Extracted {len(processed_articles)} new specimens awaiting manual review.",
            "extraction_method": extraction_source
        }

        quarantine_file = repairs_dir / f"quarantine_{collector_id}.json"
        atomic_write_json(quarantine_file, quarantine_record)

        try:
            from healing.repair_logger import RepairLogger
            RepairLogger().log_repair(
                collector_id=collector_id,
                issue=quarantine_record["issue_description"],
                prompt="User On-Demand Request",
                result=quarantine_record
            )
        except Exception as e:
            logging.warning(f"Failed to log repair to repository logs: {e}")

        return collector_id
