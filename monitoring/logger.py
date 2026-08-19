import json
import os
from datetime import datetime
from pathlib import Path
import logging

class StructuredLogger:
    def __init__(self, log_dir="logs", filename="pipeline.jsonl"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / filename
        
        # Setup standard python logging as well
        self.logger = logging.getLogger("ScraperPipeline")
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
            ch = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def log(self, level: int | str, event: str, scraper_id: str = None, **kwargs):
        """Write a structured JSON log entry"""
        if isinstance(level, int):
            level_name = logging.getLevelName(level)
            level_int = level
        else:
            level_name = str(level).upper()
            level_int = logging.getLevelNamesMapping().get(level_name, logging.INFO)
            
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level_name,
            "event": event,
        }
        if scraper_id:
            entry["scraper_id"] = scraper_id
            
        entry.update(kwargs)
        
        # Write to JSONL
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')
            
        # Also print to standard logging
        msg = f"[{event}]"
        if scraper_id:
            msg += f" [scraper: {scraper_id}]"
        for k, v in kwargs.items():
            if k not in ["output", "preview_result"]: # skip massive strings
                msg += f" {k}={v}"
        
        self.logger.log(level_int, msg)
