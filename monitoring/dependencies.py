import os
from fastapi import Request, HTTPException

async def verify_same_origin(request: Request):
    """
    Basic Same-Origin verification to prevent CSRF on mutating endpoints.
    Verifies that the Origin or Referer header matches the Host header.
    """
    origin = request.headers.get("origin")
    host = request.headers.get("host")
    referer = request.headers.get("referer")
    
    if origin:
        origin_clean = origin.split("://")[-1]
        if origin_clean != host:
            raise HTTPException(status_code=403, detail="Forbidden: Cross-Origin request blocked.")
    elif referer:
        referer_clean = referer.split("://")[-1].split("/")[0]
        if referer_clean != host:
            raise HTTPException(status_code=403, detail="Forbidden: Cross-Origin request blocked.")

def get_client_ip(request: Request) -> str:
    """Extract client IP securely, respecting TRUST_PROXY headers if enabled."""
    trust_proxy = os.getenv("TRUST_PROXY", "").lower() in ("true", "1", "yes")
    if trust_proxy:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"
