import asyncio
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from monitoring.dependencies import verify_same_origin
from monitoring.rate_limit import rate_limit
from pipeline.utils import PROJECT_ROOT

router = APIRouter()

@router.post("/api/run-demo", dependencies=[Depends(verify_same_origin), Depends(rate_limit)])
async def api_run_demo():
    """Trigger the deterministic demo break/heal script live asynchronously."""
    try:
        script_path = PROJECT_ROOT / "scripts" / "demo_break_heal.py"
        if not script_path.exists():
            return JSONResponse({"status": "error", "message": "Demo script not found."})
        
        proc = await asyncio.create_subprocess_exec(
            "python", str(script_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        
        if proc.returncode != 0:
            err_msg = stderr.decode(errors='replace')[-500:]
            return JSONResponse({"status": "error", "message": f"Demo script failed: {err_msg}"})
            
        return JSONResponse({"status": "success", "message": "Demo completed."})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)})
