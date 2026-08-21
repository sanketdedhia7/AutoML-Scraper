# Modular styles importer
from monitoring.templates.style_segments.base import BASE_STYLES
from monitoring.templates.style_segments.navigation import NAVIGATION_STYLES
from monitoring.templates.style_segments.healing import HEALING_STYLES
from monitoring.templates.style_segments.modal import MODAL_STYLES
from monitoring.templates.style_segments.utility import UTILITY_STYLES

DASHBOARD_STYLES = BASE_STYLES + NAVIGATION_STYLES + HEALING_STYLES + MODAL_STYLES + UTILITY_STYLES
