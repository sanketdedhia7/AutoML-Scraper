import os
import sys
import json
import time
import requests
import io
from pathlib import Path
from warcio.archiveiterator import ArchiveIterator

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from pipeline.utils import ensure_directories
from pipeline.orchestrator import run_etl_stage
from pipeline.cleaner import Cleaner
from pipeline.deduplicator import Deduplicator
from pipeline.quality_scorer import QualityScorer
from pipeline.exporter import Exporter
from monitoring.logger import StructuredLogger

CDX_URL = "https://index.commoncrawl.org/{crawl}-index"
DATA_BASE = "https://data.commoncrawl.org/"

def query_cdx(domain, crawl="CC-MAIN-2026-30", limit=50):
    print(f"[*] Querying CDX index for {domain} in {crawl}...")
    resp = requests.get(CDX_URL.format(crawl=crawl), params={
        "url": f"{domain}/*",
        "output": "json",
        "limit": limit,
        "collapse": "urlkey",
        "filter": ["=status:200", "=mime-detected:text/html"],
    }, timeout=30)
    
    if resp.status_code != 200:
        print(f"[!] CDX Query failed with {resp.status_code}: {resp.text}")
        return []

    entries = []
    for line in resp.text.strip().split("\n"):
        if line:
            entries.append(json.loads(line))
    return entries

def fetch_record(entry):
    offset, length = int(entry["offset"]), int(entry["length"])
    headers = {"Range": f"bytes={offset}-{offset+length-1}"}
    try:
        resp = requests.get(DATA_BASE + entry["filename"], headers=headers, timeout=30)
        resp.raise_for_status()
        stream = io.BytesIO(resp.content)
        for record in ArchiveIterator(stream):
            if record.rec_type == "response":
                return record.content_stream().read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"[-] Failed to fetch record {entry.get('url')}: {e}")
    return None

def to_article_schema(html, entry, source):
    return {
        "title": None,  # CC gives you no parsed metadata
        "author": None, 
        "publication_date": entry.get("timestamp"),
        "content": html, # raw HTML for cleaner to chew on
        "url": entry.get("url"),
        "source": source,
    }

def main():
    ensure_directories()
    
    cleaner = Cleaner()
    deduplicator = Deduplicator()
    scorer = QualityScorer()
    exporter = Exporter()
    logger = StructuredLogger()
    
    domains = {
        "cc_arxiv": "arxiv.org",
        "cc_legal": "lawreview.org",  # replaced fake domain with a more plausible one if needed, or just let it fail gracefully
        "cc_medical": "pubmed.ncbi.nlm.nih.gov"
    }
    
    for source, domain in domains.items():
        print(f"\n=======================================================")
        print(f" Processing Common Crawl Domain: {domain}")
        print(f"=======================================================")
        
        entries = query_cdx(domain, limit=50)
        print(f"[*] Found {len(entries)} entries in CDX index.")
        
        articles = []
        for i, e in enumerate(entries):
            html = fetch_record(e)
            if html:
                articles.append(to_article_schema(html, e, source))
            
            # Etiquette: Pause between API calls to avoid rate-limiting
            time.sleep(0.5)
            if (i+1) % 10 == 0:
                print(f"  -> Fetched {i+1}/{len(entries)} records...")
                
        # Save raw fetched articles
        raw_path = Path(f"data/raw/commoncrawl_{source}.json")
        with open(raw_path, "w", encoding="utf-8") as f:
            json.dump(articles, f, indent=2)
            
        print(f"[+] {source}: {len(articles)} real WARC records saved.")
        
        if not articles:
            print("[!] No articles fetched, skipping ETL stage.")
            continue
            
        print(f"\n--- Running ETL Stage for {source} ---")
        # Run orchestrated ETL exactly like run_pipeline.py
        etl_res = run_etl_stage(
            collector_id=f"commoncrawl_{source}",
            raw_data=articles,
            cleaner=cleaner,
            deduplicator=deduplicator,
            scorer=scorer,
            exporter=exporter,
            logger=logger,
            persist_intermediate=True
        )
        
        print(f"[+] Pipeline completed for {source}.")

if __name__ == "__main__":
    main()
