import subprocess
import json
import time
import logging
from pipeline.utils import TIMEOUT_HEAL_SUBPROCESS

class BrightDataHealingCLI:
    """Helper class to run Bright Data CLI scraper healing commands."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key

    def run_heal(self, collector_id: str, issue_description: str, broken_url: str = "", auto_approve: bool = False) -> dict:
        """Run `bdata scraper heal` and return the structured JSON result."""
        cmd = [
            "bdata",
            "--api-key", self.api_key,
            "scraper", "heal",
            collector_id,
            issue_description,
        ]
        if broken_url:
            cmd += ["--url", broken_url]
        if auto_approve:
            cmd.append("--auto-approve")

        import shutil
        import os
        executable = shutil.which("bdata")
        if executable and "PYTEST_CURRENT_TEST" not in os.environ:
            cmd[0] = executable

        try:
            logging.info(f"Running CLI: {' '.join(cmd)}")
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=TIMEOUT_HEAL_SUBPROCESS)
            latency = round(time.time() - start_time, 2)

            output_text = result.stdout.strip()
            try:
                data = json.loads(output_text)
            except json.JSONDecodeError:
                data = {"raw_output": output_text}

            status = data.get("status", "awaiting_approval" if not auto_approve else "success")
            return {
                "status": status,
                "collector_id": collector_id,
                "preview_result": data.get("preview_result", ""),
                "diff_summary": data.get("diff_summary", ""),
                "message": data.get("message", "Heal initiated."),
                "latency_seconds": latency,
                "raw": data,
            }
        except FileNotFoundError:
            err = "Bright Data CLI ('bdata') is not installed or not in PATH."
            logging.error(err)
            return {"status": "error", "message": err, "collector_id": collector_id}
        except subprocess.CalledProcessError as exc:
            err = f"Heal command failed (exit {exc.returncode}): {exc.stderr or exc.stdout}"
            logging.error(err)
            return {"status": "error", "message": err, "collector_id": collector_id}
        except subprocess.TimeoutExpired:
            err = "bdata scraper heal timed out after 120s."
            logging.error(err)
            return {"status": "error", "message": err, "collector_id": collector_id}

    def approve_heal(self, collector_id: str) -> dict:
        """Run `bdata scraper approve` and return status success/error."""
        cmd = ["bdata", "--api-key", self.api_key, "scraper", "approve", collector_id]
        import shutil
        import os
        executable = shutil.which("bdata")
        if executable and "PYTEST_CURRENT_TEST" not in os.environ:
            cmd[0] = executable
        try:
            logging.info(f"Running CLI: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=60)
            output_text = result.stdout.strip()
            try:
                data = json.loads(output_text)
            except json.JSONDecodeError:
                data = {"raw_output": output_text}
            return {"status": "success", "collector_id": collector_id, "output": data}
        except FileNotFoundError:
            err = "Bright Data CLI ('bdata') not found."
            logging.error(err)
            return {"status": "error", "message": err, "collector_id": collector_id}
        except subprocess.CalledProcessError as exc:
            err = f"Approve command failed (exit {exc.returncode}): {exc.stderr or exc.stdout}"
            logging.error(err)
            return {"status": "error", "message": err, "collector_id": collector_id}
        except subprocess.TimeoutExpired:
            err = "bdata scraper approve timed out."
            logging.error(err)
            return {"status": "error", "message": err, "collector_id": collector_id}
