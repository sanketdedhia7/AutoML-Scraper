import glob
import json
import logging
from pipeline.utils import PROJECT_ROOT
import monitoring.data_loaders

def _open(*args, **kwargs):
    return monitoring.data_loaders.open(*args, **kwargs)

def get_repairs_data() -> list:
    """Read all data/repairs/*.jsonl files and return a sorted list of entries."""
    from pathlib import Path
    entries = []
    
    # 1. First, calculate which collector IDs are currently pending approval
    pending_heals = set()
    
    # Check quarantine files
    for fp in glob.glob(str(PROJECT_ROOT / "data" / "repairs" / "quarantine_*.json")):
        stem = Path(fp).stem
        if stem.startswith("quarantine_"):
            cid = stem[len("quarantine_"):]
            pending_heals.add(cid)
            
    # Load .jsonl files and resolve pending states from repair history logs
    for fp in sorted(glob.glob(str(PROJECT_ROOT / "data" / "repairs" / "*.jsonl"))):
        try:
            with _open(fp, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line:
                        try:
                            data = json.loads(line)
                            entries.append(data)
                            
                            cid = data.get("collector_id")
                            if cid:
                                status = data.get("result", {}).get("status")
                                if status == "awaiting_approval":
                                    pending_heals.add(cid)
                                elif status == "success":
                                    if cid in pending_heals:
                                        pending_heals.remove(cid)
                        except Exception as e:
                            logging.warning(f"Error parsing repair line {line_num} in {fp}: {e}")
        except Exception as e:
            logging.error(f"Error reading repairs file {fp}: {e}")

    # Load standalone quarantine .json files
    for fp in sorted(glob.glob(str(PROJECT_ROOT / "data" / "repairs" / "quarantine_*.json"))):
        try:
            with _open(fp, 'r', encoding='utf-8') as f:
                data = json.load(f)
                entries.append(data)
        except Exception as e:
            logging.error(f"Error reading quarantine file {fp}: {e}")

    # Deduplicate entries and flag whether they are still pending approval
    seen = set()
    unique_entries = []
    for entry in entries:
        cid = entry.get("collector_id")
        ts = entry.get("timestamp")
        res = entry.get("result") or {}
        status = res.get("status") or (entry.get("success") and "success") or "error"
        
        # Unique signature: (collector_id, timestamp, status)
        sig = (cid, ts, status)
        if sig not in seen:
            seen.add(sig)
            
            # Attach is_pending flag dynamically
            if status == "awaiting_approval" and cid in pending_heals:
                entry["is_pending"] = True
            else:
                entry["is_pending"] = False
                
            unique_entries.append(entry)

    # Most recent first
    unique_entries.sort(key=lambda e: e.get("timestamp", ""), reverse=True)
    return unique_entries
