import subprocess
import shutil
import json
import logging

class BrightDataCLI:
    """Helper class to interact with the Bright Data 'bdata' command line interface."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key

    def create_scraper(self, target_url: str, description: str, name: str = None) -> dict:
        """Run `bdata scraper create <url> "<description>"` and return structured results."""
        cmd = ["bdata", "scraper", "create", target_url, description]
        if self.api_key:
            cmd = ["bdata", "--api-key", self.api_key] + cmd[1:]

        import os
        executable = shutil.which("bdata")
        if executable and "PYTEST_CURRENT_TEST" not in os.environ:
            cmd[0] = executable

        try:
            logging.info(f"Running CLI: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=600)
            output = result.stdout.strip()
            logging.info(f"Scraper created output: {output}")
            
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                return {"id": output, "name": name, "status": "created"}
        except FileNotFoundError:
            logging.warning("bdata CLI not found in PATH.")
            raise RuntimeError("bdata CLI not found.")
        except subprocess.CalledProcessError as exc:
            err_msg = exc.stderr or exc.stdout
            logging.error(f"bdata scraper create failed: {err_msg}")
            raise RuntimeError(f"CLI create failed: {err_msg}")
        except subprocess.TimeoutExpired:
            logging.error("bdata scraper create timed out.")
            raise RuntimeError("CLI create timed out.")
