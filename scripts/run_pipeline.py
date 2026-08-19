import sys
import os
import json
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from pipeline.scraper_runner import ScraperRunner
from pipeline.validator import Validator
from pipeline.cleaner import Cleaner
from pipeline.deduplicator import Deduplicator
from pipeline.quality_scorer import QualityScorer
from pipeline.exporter import Exporter
from healing.healer import Healer
from healing.prompt_templates import PromptTemplates
from healing.repair_logger import RepairLogger
from monitoring.alerts import Alerter
from monitoring.logger import StructuredLogger

from pipeline.utils import ensure_directories
from pipeline.healing_cycle import run_validation_healing_cycle

from pipeline.orchestrator import run_etl_stage

def run_pipeline():
    ensure_directories()
    
    # Load active scrapers mapping
    active_scrapers = {}
    mapping_path = Path(__file__).resolve().parent.parent / "scrapers" / "active_scrapers.json"
    if mapping_path.exists():
        try:
            with open(mapping_path, 'r') as f:
                active_scrapers = json.load(f)
        except Exception as e:
            print(f"[!] Warning: Could not read active_scrapers.json: {e}")
            
    # List of collectors to run
    collectors = list(active_scrapers.keys())
    if not collectors:
        scrapers_dir = Path(__file__).resolve().parent.parent / "scrapers"
        collectors = [p.stem for p in scrapers_dir.glob("*.json") 
                      if p.stem != "active_scrapers" and not p.stem.endswith("_selectors")]
    if not collectors:
        collectors = ["legal_blog_scraper", "medical_journal_scraper", "arxiv_scraper"]
    
    for col_name in collectors:
        col_id = active_scrapers.get(col_name, col_name)
        run_validation_healing_cycle(col_name, col_id, auto_approve=True)

if __name__ == "__main__":
    run_pipeline()
