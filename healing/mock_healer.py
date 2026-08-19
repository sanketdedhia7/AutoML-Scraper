import os
import json
import logging

class MockHealer:
    """Simulates Bright Data self-healing API for local fixture scraper runs."""
    
    def run_mock_heal(self, collector_id: str, auto_approve: bool, broken_url: str = "") -> dict:
        """Simulate structural repair on selector dictionaries for demo_scraper or dynamically heal on-demand scrapers."""
        if collector_id.startswith("ondemand_"):
            from pipeline.utils import PROJECT_ROOT, atomic_write_json
            if not broken_url:
                qfile = PROJECT_ROOT / "data" / "repairs" / f"quarantine_{collector_id}.json"
                if qfile.exists():
                    try:
                        with open(qfile, 'r', encoding='utf-8') as f:
                            broken_url = json.load(f).get("broken_url", "")
                    except Exception:
                        pass
            if not broken_url:
                broken_url = "https://www.scrapethissite.com/pages/"

            try:
                from pipeline.ondemand.fallback_extractor import FallbackExtractor
                from pipeline.ondemand.gemini_extractor import GeminiExtractor
                from pipeline.ondemand.article_processor import ArticleProcessor

                fallback = FallbackExtractor()
                gemini = GeminiExtractor()
                processor = ArticleProcessor()

                cleaned_text = fallback.fetch_and_extract_text(broken_url)
                raw_articles = gemini.extract_with_gemini(cleaned_text, broken_url)
                processed_articles, duplicates_removed = processor.process_articles(raw_articles, broken_url, "gemini_llm_healer")

                old_state = {"status": "unhealthy", "error": "validation check failed: missing required fields"}
                new_state = {"status": "recovered", "extraction_path": "Gemini Fallback"}
                explanation = gemini.generate_selector_explanation(old_state, new_state)

                import datetime
                qfile = PROJECT_ROOT / "data" / "repairs" / f"quarantine_{collector_id}.json"
                qdata = {}
                if qfile.exists():
                    try:
                        with open(qfile, 'r', encoding='utf-8') as f:
                            qdata = json.load(f)
                    except Exception:
                        pass
                
                qdata.update({
                    "timestamp": qdata.get("timestamp") or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "collector_id": collector_id,
                    "broken_url": broken_url,
                    "issue_description": qdata.get("issue_description") or "On-demand user submission (gemini_llm_fallback)",
                    "prompt": qdata.get("prompt") or "User On-Demand Request",
                    "status": "awaiting_approval",
                    "preview_result": processed_articles,
                    "diff_summary": f"Healed via Gemini fallback. Extracted {len(processed_articles)} specimens.",
                    "explanation": explanation
                })
                atomic_write_json(qfile, qdata)

                preview_text = "\n\n".join(
                    f"№ {art.get('quality_score', 0)}/100 - HEALED: {art.get('title')}\n"
                    f"BY: {art.get('author')}\n"
                    f"DATE: {art.get('publication_date')}\n"
                    f"Content: {art.get('content')[:200]}..."
                    for art in processed_articles
                )
                return {
                    "status": "awaiting_approval",
                    "collector_id": collector_id,
                    "preview_result": preview_text,
                    "diff_summary": f"Fallback to Gemini LLM healer. Selector drift bypassed.\nProcessed {len(processed_articles)} specimens.",
                    "message": "Dynamic repair preview generated using safe-fetch Gemini fallback.",
                    "explanation": explanation,
                    "latency_seconds": 0.5,
                }
            except Exception as e:
                logging.error(f"Dynamic mock heal failed: {e}")

        explanation = ""
        if collector_id == "demo_scraper":
            try:
                base_dir = os.path.dirname(os.path.dirname(__file__))
                selector_path = os.path.join(base_dir, "scrapers", "demo_selectors.json")
                healed_selectors = {
                    "container": ".post-block",
                    "title": ".heading-link",
                    "author": ".creator-name",
                    "publication_date": ".pub-time",
                    "content": ".body-content",
                }
                with open(selector_path, 'w', encoding='utf-8') as f:
                    json.dump(healed_selectors, f, indent=2)
                logging.info("Mock Healer: Updated demo_selectors.json with healed selectors.")
                
                old_selectors = {
                    "container": ".article-item",
                    "title": "h3.article-title a",
                    "author": ".meta-author",
                    "publication_date": ".meta-date",
                    "content": ".abstract-text"
                }
                from pipeline.ondemand.gemini_extractor import GeminiExtractor
                explanation = GeminiExtractor().generate_selector_explanation(old_selectors, healed_selectors)
            except Exception as exc:
                logging.error(f"Mock Healer failed to write healed selectors: {exc}")

        preview_text = (
            "Mock preview: 3 sample records successfully extracted with updated selectors. "
            "Titles, authors, and publication dates all resolved correctly."
        )
        if collector_id == "demo_scraper":
            try:
                from scrapers.scraper_manager import ScraperManager
                raw_items = ScraperManager()._run_demo_scraper_parser()
                # generate preview text based on raw_items
                preview_text = "\n\n".join(
                    f"№ {i+1} - HEALED: {art.get('title')}\n"
                    f"BY: {art.get('author')}\n"
                    f"DATE: {art.get('publication_date')}\n"
                    f"Content: {str(art.get('content'))[:200]}..."
                    for i, art in enumerate(raw_items[:3])
                )
            except Exception as e:
                logging.error(f"Failed to generate dynamic preview for demo_scraper: {e}")

        status = "success" if auto_approve else "awaiting_approval"
        return {
            "status": status,
            "collector_id": collector_id,
            "preview_result": preview_text,
            "diff_summary": (
                "Selector changes:\n"
                "  container: .article-item → .post-block\n"
                "  title:     h3.article-title a → .heading-link\n"
                "  author:    .meta-author → .creator-name\n"
                "  date:      .meta-date → .pub-time\n"
                "  content:   .abstract-text → .body-content"
            ),
            "message": (
                "Mock self-heal complete. Selectors rebuilt."
                if auto_approve
                else "Awaiting approval. Review preview_result and diff_summary, then call approve_healing()."
            ),
            "explanation": explanation,
            "latency_seconds": 0.5,
        }
