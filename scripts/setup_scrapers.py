import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from scrapers.scraper_manager import ScraperManager

def main():
    import json
    manager = ScraperManager()
    
    # Create scrapers from config files
    scrapers_dir = Path(__file__).resolve().parent.parent / "scrapers"
    active_scrapers = {}
    for config_file in scrapers_dir.glob("*.json"):
        if config_file.name == "active_scrapers.json":
            continue
        print(f"Creating scraper from {config_file.name}...")
        result = manager.create_scraper(config_file)
        print(f"Created: {result['name']} (ID: {result['id']})")
        active_scrapers[result['name']] = result['id']
        
    # Save the mapping to active_scrapers.json
    mapping_path = scrapers_dir / "active_scrapers.json"
    with open(mapping_path, 'w', encoding='utf-8') as f:
        json.dump(active_scrapers, f, indent=2)
    print(f"[+] Saved active scraper mapping to {mapping_path}")

if __name__ == "__main__":
    main()
