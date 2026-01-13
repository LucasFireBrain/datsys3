import os
import json
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
