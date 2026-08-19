import requests
import json
import xml.etree.ElementTree as ET
from pathlib import Path

def fetch_real_dataset():
    print("Fetching real articles from arXiv API (AI/ML category)...")
    # Fetch 15 articles
    url = "http://export.arxiv.org/api/query?search_query=cat:cs.AI+OR+cat:cs.LG&start=0&max_results=15"
    response = requests.get(url)
    response.raise_for_status()
    
    # Parse XML
    root = ET.fromstring(response.content)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    
    dataset = []
    for entry in root.findall('atom:entry', ns):
        title_el = entry.find('atom:title', ns)
        summary_el = entry.find('atom:summary', ns)
        id_el = entry.find('atom:id', ns)
        published_el = entry.find('atom:published', ns)
        
        title = title_el.text.strip().replace("\n", " ") if title_el is not None else "Untitled"
        summary = summary_el.text.strip().replace("\n", " ") if summary_el is not None else ""
        paper_url = id_el.text.strip() if id_el is not None else ""
        published = published_el.text.strip()[:10] if published_el is not None else "2026-08-12"
        
        # Get authors
        authors = []
        for author in entry.findall('atom:author', ns):
            name_el = author.find('atom:name', ns)
            if name_el is not None:
                authors.append(name_el.text.strip())
        author_str = ", ".join(authors) if authors else "Unknown"
        
        # Inject HTML tags/boilerplate to test HTML Cleaner
        content_html = (
            f"<div class='arxiv-entry-wrapper'>\n"
            f"  <p class='ad-banner'>Sponsored Ad: Master AutoML with our new bootcamp!</p>\n"
            f"  <div class='abstract-content'>{summary}</div>\n"
            f"  <footer class='boilerplate'>For more details, visit <a href='{paper_url}'>arXiv page</a> or subscribe to our newsletter.</footer>\n"
            f"</div>"
        )
        
        dataset.append({
            "title": title,
            "author": author_str,
            "publication_date": published,
            "content": content_html,
            "url": paper_url,
            "source": "arxiv_dataset"
        })
        
    print(f"[*] Parsed {len(dataset)} papers from arXiv.")
    
    # Inject an exact duplicate to test the Deduplicator
    if dataset:
        print("[*] Injecting an exact duplicate to test the Deduplicator...")
        dataset.append(dataset[0].copy())
        
    # Inject a low-quality (thin content) article to test the Quality Scorer rejection
    print("[*] Injecting a low-quality (thin content) article to verify Quality Scorer rejection...")
    dataset.append({
        "title": "Quantum AI Hype - Brief Note",
        "author": "Hype Generator Bot",
        "publication_date": "2026-08-12",
        "content": "<div class='thin-body'>This is a very short text about AI. The hype is real but there is no technical content in this paper whatsoever.</div>",
        "url": "http://export.arxiv.org/abs/1234.5678",
        "source": "arxiv_dataset"
    })
        
    # Save the dataset
    out_dir = Path("data")
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "real_dataset_mock.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2)
    print(f"Successfully saved {len(dataset)} articles (including tests) to {out_path}")

if __name__ == "__main__":
    fetch_real_dataset()
