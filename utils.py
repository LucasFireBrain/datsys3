import os
import json
from pathlib import Path
from datetime import datetime

# -------------------------
# PATHS
# -------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENTS_DIR = os.path.join(BASE_DIR, "clients")
DATA_DIR = os.path.join(BASE_DIR, "data")

# -------------------------
# FS HELPERS
# -------------------------

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def list_dirs(path):
    if not os.path.exists(path):
        return []
    return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

# -------------------------
# JSON HELPERS
# -------------------------

def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# -------------------------
# TIME
# -------------------------

def now_iso():
    return datetime.now().isoformat(timespec="seconds")

# -------------------------
# BASE36 DATE CODE (YYMMDD)
# -------------------------

BASE36 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def to_base36(n: int) -> str:
    if n < 0 or n >= len(BASE36):
        raise ValueError("base36 digit out of range")
    return BASE36[n]

def date_code_base36(dt=None):
    """
    2025-01-13 -> P113
    2026-12-05 -> QC05
    """
    from datetime import datetime

    if dt is None:
        dt = datetime.now()

    yy = dt.year % 100          # 2025 -> 25
    y = to_base36(yy)           # 25 -> P
    m = to_base36(dt.month)     # 1–12 -> 1–C
    d = f"{dt.day:02d}"         # always 2 digits

    return f"{y}{m}{d}"

def update_stage(project_dir, stage, message=None):
    project_dir = Path(project_dir)

    # ---- update peekCase.json ----
    peek_path = project_dir / "peekCase.json"
    data = load_json(peek_path, {})
    data["estado_caso"] = stage
    data["actualizado_en"] = now_iso()
    save_json(peek_path, data)

    # ---- append log ----
    log_path = project_dir / "Log.txt"
    log_path.touch(exist_ok=True)

    timestamp = now_iso()[:16].replace("T", " ")
    line = f"[{timestamp}] STAGE → {stage}"
    if message:
        line += f" | {message}"

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line + "\n")