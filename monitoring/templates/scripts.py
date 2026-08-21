# Modular scripts importer
from monitoring.templates.script_segments.core import CORE_JS
from monitoring.templates.script_segments.charting import CHARTING_JS
from monitoring.templates.script_segments.modal import MODAL_JS
from monitoring.templates.script_segments.healing import HEALING_JS
from monitoring.templates.script_segments.exports import EXPORTS_JS
from monitoring.templates.script_segments.ondemand import ONDEMAND_JS

def get_dashboard_scripts(articles_json: str, quality_stats_json: str, threshold: int) -> str:
    # Concatenate modularized JS segments
    full_js_template = CORE_JS + CHARTING_JS + MODAL_JS + HEALING_JS + EXPORTS_JS + ONDEMAND_JS
    
    # Evaluate variables using python string formatting
    return full_js_template.format(
        articles_json=articles_json,
        quality_stats_json=quality_stats_json,
        threshold=threshold
    )
