from fastapi import APIRouter
from fastapi.responses import HTMLResponse, JSONResponse
from monitoring.data_loaders import get_dashboard_data_dict, get_repairs_data
from monitoring.templates import render_dashboard_html

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def dashboard():
    """Render a premium dual-tab (Ops Health + Curated Dataset Explorer) HTML dashboard."""
    data = get_dashboard_data_dict()
    html_content = render_dashboard_html(data)
    return HTMLResponse(content=html_content)

@router.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes/container orchestration."""
    return JSONResponse({"status": "ok"})

@router.get("/api/dashboard-data")
async def api_dashboard_data():
    """Retrieve current pipeline statuses and data for in-place re-rendering."""
    return JSONResponse(get_dashboard_data_dict())

@router.get("/api/repairs")
async def api_repairs():
    """Return all repair log entries as JSON."""
    return JSONResponse(get_repairs_data())
