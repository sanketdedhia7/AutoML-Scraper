import html
from typing import Dict, Any, Set
from monitoring.presenters.healing_panel import render_healing_stepper, render_pending_heal

STATUS_ICONS = {
    "healthy": "<svg style='width:1.2em;height:1.2em;vertical-align:-0.2em;display:inline-block;' fill='none' stroke='currentColor' viewBox='0 0 24 24'><path stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M5 13l4 4L19 7'></path></svg>",
    "unhealthy": "<svg style='width:1.2em;height:1.2em;vertical-align:-0.2em;display:inline-block;' fill='none' stroke='currentColor' viewBox='0 0 24 24'><path stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M6 18L18 6M6 6l12 12'></path></svg>",
    "error": "<svg style='width:1.2em;height:1.2em;vertical-align:-0.2em;display:inline-block;' fill='none' stroke='currentColor' viewBox='0 0 24 24'><path stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z'></path></svg>",
    "healing": "<svg style='width:1.2em;height:1.2em;vertical-align:-0.2em;display:inline-block;' fill='none' stroke='currentColor' viewBox='0 0 24 24'><path stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M13 10V3L4 14h7v7l9-11h-7z'></path></svg>"
}

def render_scraper_card(
    collector_id: str,
    details: Dict[str, Any],
    meta: Dict[str, Any],
    pending_heals: Dict[str, Dict[str, Any]],
    healed_scrapers: Set[str]
) -> str:
    """Render HTML list card representing a scraper state record."""
    status_class = details.get('status', 'error')
    validation = details.get('validation', {})
    display_name = meta.get("display_name") or collector_id.replace("_", " ").title()
    scraper_url = meta.get("url", "")
    errors = validation.get('errors', [])
    warnings = validation.get('warnings', [])
    
    has_healed = collector_id in healed_scrapers or collector_id == "demo_scraper"
    
    err_list_html = ""
    if errors:
        err_list_html += "".join(f"<li>{html.escape(e)}</li>" for e in errors)
    if warnings:
        err_list_html += "".join(f"<li class='warning-item'>[Warning] {html.escape(w)}</li>" for w in warnings)
        
    narrative = ""
    if status_class == "healthy":
        if has_healed:
            narrative = (
                "Extraction pathways were recently compromised due to selector drift (validation error: Empty output). "
                "A self-healing restoration was completed successfully. Selectors were automatically updated and rebuilt "
                "using Scraper Studio self-heal APIs."
            )
        else:
            narrative = "Extraction pathways remain fully intact. Structure checks completed with zero deviations."
    else:
        plain_errors = "; ".join(errors) if errors else 'unknown structural shift'
        narrative = f"CRITICAL BREAKAGE: Validation checks failed. Extraction pathways returned invalid or empty segments. Error: {plain_errors}."

    seam_html = ""
    approve_button_html = ""
    collector_id_escaped = html.escape(collector_id)
    
    if status_class in ("unhealthy", "error") and errors:
        approve_button_html = f"""
        <div style="margin-top:16px; display:flex; gap:10px; flex-wrap:wrap;">
            <button class="heal-trigger-btn" data-action="trigger-heal" data-collector="{collector_id_escaped}">
                <svg style='width:1.2em;height:1.2em;vertical-align:-0.2em;display:inline-block;' fill='none' stroke='currentColor' viewBox='0 0 24 24'><path stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z'></path><path stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M15 12a3 3 0 11-6 0 3 3 0 016 0z'></path></svg> <span class="btn-text">Trigger Self-Heal & Review Preview</span>
            </button>
            <button class="heal-trigger-btn" style="border-color:var(--verdigris-green); color:var(--verdigris-green);" data-action="heal-now" data-collector="{collector_id_escaped}">
                <svg style='width:1.2em;height:1.2em;vertical-align:-0.2em;display:inline-block;' fill='none' stroke='currentColor' viewBox='0 0 24 24'><path stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M13 10V3L4 14h7v7l9-11h-7z'></path></svg> <span class="btn-text">Auto-Heal Now (Full Cycle)</span>
            </button>
        </div>
        """
    elif has_healed and status_class == "healthy":
        seam_html = """
        <div class="kintsugi-horizontal-seam">
            <svg class="seam-svg" viewBox="0 0 100 10" preserveAspectRatio="none">
                <path d="M0,5 L12,2 L23,8 L35,3 L48,7 L60,4 L72,8 L85,2 L100,5" stroke="var(--gold-seam)" stroke-width="1.5" fill="none" class="seam-path" />
            </svg>
        </div>
        """

    current_step = 1
    if collector_id in pending_heals:
        current_step = 3
    elif status_class == "healing":
        current_step = 2
    elif status_class == "healthy":
        current_step = 4

    stepper_html = render_healing_stepper(collector_id_escaped, current_step)
    
    pending_panel_html = ""
    if collector_id in pending_heals:
        pending_panel_html = render_pending_heal(collector_id_escaped, pending_heals[collector_id])
        approve_button_html = "" # Hide trigger button since we are pending

    status_badge_icon = STATUS_ICONS.get(status_class, "")
    article_count = details.get('articles_extracted', 0)
    last_run_str = html.escape(str(details.get('last_run', 'N/A')))

    return f"""
    <div class="ledger-record {status_class}" id="record-{collector_id_escaped}"
         data-status="{status_class}" data-collector="{collector_id_escaped}"
         data-articles="{article_count}" data-last-run="{last_run_str}">
        <div class="record-header">
            <div class="record-title-group">
                <span class="status-badge {status_class}">{status_badge_icon} {status_class.upper()}</span>
                <div class="record-id-group">
                    <span class="record-display-name">{html.escape(display_name)}</span>
                    <span class="record-num">{collector_id_escaped}</span>
                </div>
            </div>
            <div class="record-meta-group">
                <span class="meta-pill"><svg style='width:1.2em;height:1.2em;vertical-align:-0.2em;display:inline-block;' fill='none' stroke='currentColor' viewBox='0 0 24 24'><path stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M20 12l-4 7H8l-4-7 4-7h8l4 7z'></path></svg> {article_count} articles</span>
                {f"<span class='meta-pill'><svg style='width:1.2em;height:1.2em;vertical-align:-0.2em;display:inline-block;' fill='none' stroke='currentColor' viewBox='0 0 24 24'><path stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z'></path></svg> {last_run_str}</span>" if last_run_str != 'N/A' else ""}
                {f"<span class='meta-pill url-pill' title='{html.escape(scraper_url)}'>{html.escape(scraper_url[:40] + '…' if len(scraper_url) > 40 else scraper_url)}</span>" if scraper_url else ""}
            </div>
        </div>
        {stepper_html}
        <p class="record-body">{html.escape(narrative)}</p>
        {seam_html}
        {f"<div class='record-error-box'>{err_list_html}</div>" if err_list_html else ""}
        {approve_button_html}
        {pending_panel_html}
    </div>
    """
