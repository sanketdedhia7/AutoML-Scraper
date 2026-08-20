import subprocess
import shutil
import json
import logging
import os

class BrightDataCLI:
    """Helper class to interact with the Bright Data 'bdata' command line interface."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key

    def scrape_url(self, target_url: str) -> str:
        """Run `bdata scrape <url> -f html` to fetch raw HTML via Bright Data Scraper Studio CLI."""
        cmd = ["bdata", "scrape", target_url, "-f", "html"]
        if self.api_key:
            cmd += ["-k", self.api_key]

        executable = shutil.which("bdata")
        if executable and "PYTEST_CURRENT_TEST" not in os.environ:
            cmd[0] = executable

        try:
            logging.info(f"Running CLI: {' '.join(cmd[:3])} -f html [URL={target_url}]")
            result = subprocess.run(
                cmd,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                check=True,
                timeout=120
            )
            output = result.stdout.strip()
            if output:
                logging.info(f"bdata scrape CLI succeeded for {target_url} (received {len(output)} chars)")
                return output
            raise RuntimeError("bdata scrape returned empty output.")
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
        cmd = ["bdata", "scraper", "create", target_url, description]
        if self.api_key:
            cmd = ["bdata", "--api-key", self.api_key] + cmd[1:]

        executable = shutil.which("bdata")
        if executable and "PYTEST_CURRENT_TEST" not in os.environ:
            cmd[0] = executable

        try:
            logging.info(f"Running CLI: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                check=True,
                timeout=600
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
