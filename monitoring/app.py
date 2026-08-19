import os
import logging
from dotenv import load_dotenv
load_dotenv()

from contextlib import asynccontextmanager
from fastapi import FastAPI
from monitoring.telemetry import metrics_app, HAVE_PROMETHEUS
from monitoring.routers.dashboard import router as dashboard_router
from monitoring.routers.healing import router as healing_router
from monitoring.routers.ondemand import router as ondemand_router
from monitoring.routers.demo import router as demo_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.environ.get("BRIGHT_DATA_API_KEY"):
        logging.warning("WARNING: BRIGHT_DATA_API_KEY environment variable is not set. Scrapers requiring authentication will fail.")
    yield

app = FastAPI(title="AutoML Data Curator Dashboard", lifespan=lifespan)

# Mount Prometheus endpoint if available
if HAVE_PROMETHEUS and metrics_app:
    app.mount("/metrics", metrics_app)

# Include routers
app.include_router(dashboard_router)
app.include_router(healing_router)
app.include_router(ondemand_router)
app.include_router(demo_router)
