import subprocess
import shutil
import json
import logging
import os
from pipeline.utils import PROJECT_ROOT

class BrightDataCLI:
    """Helper class to interact with the Bright Data 'bdata' command line interface."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key

    def _find_bdata_cmd(self) -> list:
        """Find the bdata executable command list across local and system paths."""
        exe = shutil.which("bdata")
        if exe and "PYTEST_CURRENT_TEST" not in os.environ:
            return [exe]

        candidates = [
            str(PROJECT_ROOT / "node_modules" / ".bin" / "bdata"),
            "/usr/local/bin/bdata",
            "/usr/bin/bdata",
            "/opt/render/project/src/node_modules/.bin/bdata",
            "C:\\Program Files\\nodejs\\bdata.cmd",
            os.path.expanduser("~\\AppData\\Roaming\\npm\\bdata.cmd")
        ]
        for c in candidates:
            if os.path.exists(c):
                return [c]

        npx = shutil.which("npx")
        if npx:
            return [npx, "bdata"]

        return ["bdata"]

    def scrape_url(self, target_url: str) -> str:
        """Run `bdata scrape <url> --zone cli_unlocker -f html` to fetch raw HTML via Bright Data Scraper Studio CLI."""
        base_cmd = self._find_bdata_cmd()
        cmd = base_cmd + ["scrape", target_url, "-f", "html", "--zone", "cli_unlocker"]
        if self.api_key:
            cmd += ["-k", self.api_key]

        use_shell = os.name == "nt"
        try:
            logging.info(f"Running CLI: {' '.join(cmd[:4])} -f html [URL={target_url}]")
            result = subprocess.run(
                cmd,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                check=True,
                timeout=120,
                shell=use_shell
            )
            output = result.stdout.strip()
            if output and len(output) > 50:
                logging.info(f"bdata scrape CLI succeeded for {target_url} (received {len(output)} chars)")
                return output
            raise RuntimeError(f"bdata scrape output too short ({len(output) if output else 0} chars). Stderr: {result.stderr}")
        except FileNotFoundError:
            logging.warning("bdata CLI not found in PATH.")
            raise RuntimeError("bdata CLI not found.")
        except subprocess.CalledProcessError as exc:
            err_msg = exc.stderr or exc.stdout
            logging.error(f"bdata scrape failed: {err_msg}")
            raise RuntimeError(f"CLI scrape failed: {err_msg}")
        except subprocess.TimeoutExpired:
            logging.error("bdata scrape timed out.")
            raise RuntimeError("CLI scrape timed out.")

    def create_scraper(self, target_url: str, description: str, name: str = None) -> dict:
        """Run `bdata scraper create <url> "<description>"` and return structured results."""
        base_cmd = self._find_bdata_cmd()
        cmd = base_cmd + ["scraper", "create", target_url, description]
        if self.api_key:
            cmd = base_cmd + ["--api-key", self.api_key, "scraper", "create", target_url, description]

        use_shell = os.name == "nt"
        try:
            logging.info(f"Running CLI: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                check=True,
                timeout=600,
                shell=use_shell
            )
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
