import os
import json
import datetime
from datetime import timezone
import threading
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Add local node_modules/.bin to PATH so local npm installations are discoverable
node_modules_bin = str(PROJECT_ROOT / "node_modules" / ".bin")
if node_modules_bin not in os.environ.get("PATH", ""):
    os.environ["PATH"] = node_modules_bin + os.pathsep + os.environ.get("PATH", "")

# Configurable timeouts with environment overrides
TIMEOUT_API_REQUEST = int(os.getenv("TIMEOUT_API_REQUEST", "30"))
TIMEOUT_HEAL_SUBPROCESS = int(os.getenv("TIMEOUT_HEAL_SUBPROCESS", "120"))
TIMEOUT_WAIT_COMPLETION = int(os.getenv("TIMEOUT_WAIT_COMPLETION", "300"))

# Process-wide lock for thread-safe state modification
_state_lock = threading.RLock()

def is_mock_mode(collector_id: str = "", api_key: str = None) -> bool:
    """Centralized mock mode evaluation across scrapers and healers."""
    if api_key is None:
        api_key = os.getenv("BRIGHT_DATA_API_KEY", "")
    if not api_key or api_key == "your_api_key_here":
        return True
    if collector_id == "demo_scraper":
        return True
    return False

def atomic_write_json(file_path: Path, data: Any, indent: int = 2):
    """Write data to JSON atomically using a temp file and os.replace."""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = file_path.with_name(f"{file_path.name}.tmp")
    try:
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent)
        os.replace(tmp_path, file_path)
    except Exception as e:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except Exception:
                pass
        raise e

def ensure_directories():
    """Ensure all required data directories exist relative to project root."""
    dirs = [
        "data/raw",
        "data/cleaned",
        "data/deduplicated",
        "data/scored",
        "data/exports",
        "data/repairs"
    ]
    for d in dirs:
        (PROJECT_ROOT / d).mkdir(parents=True, exist_ok=True)

def _get_states_file_path() -> Path:
    return PROJECT_ROOT / "data" / "scraper_states.json"

def load_scraper_states() -> dict:
    """Load the scraper states from scraper_states.json in a thread-safe manner"""
    path = _get_states_file_path()
    with _state_lock:
        if not path.exists():
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

def save_scraper_states(states: dict):
    """Save the scraper states to scraper_states.json atomically using a temp file"""
    path = _get_states_file_path()
    tmp_path = path.with_suffix(".tmp")
    with _state_lock:
        try:
            # Write to temporary file first
            with open(tmp_path, 'w', encoding='utf-8') as f:
                json.dump(states, f, indent=2)
            # Atomically replace the destination file
            os.replace(tmp_path, path)
        except Exception as e:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
            print(f"[!] Error saving scraper states: {e}")

def update_scraper_state(
    collector_id: str,
    status: str,
    last_run: str = None,
    articles_extracted: int = 0,
    validation_errors: list = None
):
    """Update the state of a single scraper in a thread-safe atomic manner"""
    ensure_directories()
    with _state_lock:
        states = load_scraper_states()
        now_str = datetime.datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        
        state = states.setdefault(collector_id, {})
        state["collector_id"] = collector_id
        state["status"] = status
        if last_run is not None:
            state["last_run"] = last_run
        state["articles_extracted"] = articles_extracted
        state["validation_errors"] = validation_errors or []
        state["last_updated"] = now_str
        
        save_scraper_states(states)

