import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any

class RepairLogger:
    def __init__(self, log_dir="data/repairs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def log_repair(self, collector_id: str, issue: str, prompt: str, result: Dict[str, Any]):
        """Log a repair for future ML training"""
        now_utc = datetime.now(timezone.utc)
        log_entry = {
            "timestamp": now_utc.isoformat(),
            "collector_id": collector_id,
            "issue": issue,
            "prompt": prompt,
            "result": result,
            "success": result.get("status") == "success" or result.get("success") is True
        }
        
        # Append to daily log file
        log_file = self.log_dir / f"{now_utc.strftime('%Y-%m-%d')}.jsonl"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        
        print(f"Logged repair for collector {collector_id}")
