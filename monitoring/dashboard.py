"""
AutoML Data Curator Dashboard Entrypoint Shim.

This module re-exports the FastAPI `app` from `monitoring.routes` for backward compatibility.
Existing invocation commands such as `uvicorn monitoring.dashboard:app` continue to work unchanged.
"""

import os
import uvicorn
from monitoring.routes import app

__all__ = ["app"]

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
