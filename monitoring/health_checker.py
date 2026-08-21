import json
from pathlib import Path
from typing import Dict, Any, List
from pipeline.validator import Validator

class HealthChecker:
    def __init__(self, data_dir="data/raw"):
        self.data_dir = Path(data_dir)
        self.validator = Validator()
    
    def check_scraper_health(self, collector_id: str, preloaded_data: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Check health of a single scraper from local raw pipeline artifacts or states file"""
        from pipeline.utils import load_scraper_states
        states = load_scraper_states()
        
        if collector_id in states and not collector_id.startswith("ondemand_"):
            state = states[collector_id]
            is_valid = state.get("status") == "healthy"
            errors = state.get("validation_errors", [])
            validation = {
                "is_valid": is_valid,
                "errors": errors,
                "warnings": []
            }
            return {
                "collector_id": collector_id,
                "status": state.get("status", "error"),
                "last_run": state.get("last_run", "recent"),
                "articles_extracted": state.get("articles_extracted", 0),
                "validation": validation
            }

        try:
            if preloaded_data is not None:
                output = preloaded_data
            else:
                raw_path = self.data_dir / f"{collector_id}.json"
                
                # Load local raw pipeline artifacts if they exist
                if not raw_path.exists():
                    if collector_id == "demo_scraper":
                        from scrapers.scraper_manager import ScraperManager
                        output = ScraperManager()._run_demo_scraper_parser()
                    elif collector_id.startswith("ondemand_"):
                        scored_path = self.data_dir.parent / "scored" / f"{collector_id}.json"
                        if scored_path.exists():
                            with open(scored_path, 'r', encoding='utf-8') as f:
                                output = json.load(f)
                        else:
                            output = []
                    else:
                        output = []
                else:
                    with open(raw_path, 'r', encoding='utf-8') as f:
                        output = json.load(f)
            
            # Validate the local raw data
            validation = self.validator.validate(output)
            
            # Get last run info or default
            last_run = "unknown"
            if isinstance(output, list) and len(output) > 0:
                last_run = output[0].get("publication_date", "recent")
            
            return {
                "collector_id": collector_id,
                "status": "healthy" if validation["is_valid"] else "unhealthy",
                "last_run": last_run,
                "articles_extracted": len(output) if isinstance(output, list) else 0,
                "validation": validation
            }
        except Exception as e:
            import logging
            logging.warning(f"Error checking health for scraper {collector_id}: {e}")
            return {
                "collector_id": collector_id,
                "status": "error",
                "last_run": "failed",
                "articles_extracted": 0,
                "validation": {
                    "is_valid": False,
                    "errors": [str(e)],
                    "warnings": []
                }
            }
    
    def check_all_scrapers(self, collector_ids: List[str], preloaded_raw: Dict[str, List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Check health of all scrapers based on local artifacts"""
        results = {}
        for collector_id in collector_ids:
            preload = preloaded_raw.get(collector_id) if preloaded_raw else None
            results[collector_id] = self.check_scraper_health(collector_id, preload)
        
        return {
            "total_scrapers": len(collector_ids),
            "healthy": sum(1 for r in results.values() if r["status"] == "healthy"),
            "unhealthy": sum(1 for r in results.values() if r["status"] == "unhealthy"),
            "error": sum(1 for r in results.values() if r["status"] == "error"),
            "details": results
        }

