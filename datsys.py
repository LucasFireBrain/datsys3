import os
import shutil
from pathlib import Path

from dicom_ingestion import ingest_dicom
from utils import (
    CLIENTS_DIR,
    ensure_dir,
    load_json,
    save_json,
    now_iso,
    date_code_base36,
    update_stage,
)

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
PEEK_TEMPLATE_DIR = TEMPLATES_DIR / "PK"

# --------------------------------------------------
# CAPABILITIES
# --------------------------------------------------

def init_clients_dir():
    ensure_dir(CLIENTS_DIR)

def create_client(client_id: str, name: str, contact: str) -> Path:
    client_id = client_id.upper()
    client_dir = Path(CLIENTS_DIR) / client_id
    client_json_path = client_dir / f"client_{client_id}.json"

    if client_dir.exists():
        return client_dir

    client_dir.mkdir(parents=True, exist_ok=True)
    save_json(client_json_path, {
        "id": client_id,
        "name": name,
        "contact": contact,
        "created_at": now_iso(),
        "project_count": 0,
    })
    return client_dir

def new_project(client_id: str, project_type: str, name: str = "", contact: str = ""):
    init_clients_dir()

    client_id = client_id.upper()
    client_dir = Path(CLIENTS_DIR) / client_id
    client_json_path = client_dir / f"client_{client_id}.json"

    if not client_dir.exists():
        create_client(client_id, name, contact)

    client = load_json(client_json_path, {})
    suffix = client.get("project_count", 0) + 1
    client["project_count"] = suffix
    save_json(client_json_path, client)

    date_code = date_code_base36()
    project_id = f"{date_code}-{client_id}-{project_type}{suffix}"
    project_dir = client_dir / project_id
    project_dir.mkdir()

    if project_type == "PK":
        if not PEEK_TEMPLATE_DIR.exists():
            raise RuntimeError("PEEK template folder missing")
        shutil.copytree(
            PEEK_TEMPLATE_DIR,
            project_dir,
            dirs_exist_ok=True
        )

        old_blend = project_dir / "Blender" / "PEEK.blend"
        new_blend = project_dir / "Blender" / f"{project_id}.blend"

        if old_blend.exists() and not new_blend.exists():
            old_blend.rename(new_blend)

    save_json(
        project_dir / f"{project_id}.json",
        {
            "id": project_id,
            "client_id": client_id,
            "type": project_type,
            "created_at": now_iso(),
        },
    )

    update_stage(project_dir, "NEW")

    return project_id, project_dir

def open_project_folder(project_path: str):
    os.startfile(project_path)

def open_log(project_path: str):
    log_path = Path(project_path) / "Log.txt"
    log_path.touch(exist_ok=True)
    os.startfile(log_path)

def open_peek_case(project_path: str):
    from peek import prompt_peek_case
    prompt_peek_case(project_path)

def ingest_project_dicom(project_path: str):
    ingest_dicom(project_path)

def open_slicer(project_path: str):
    from slicer_launcher import launch_slicer_with_dicom
    dicom_dir = Path(project_path) / "DICOM"
    launch_slicer_with_dicom(dicom_dir)

def open_blender(project_path, project_id):
    from blender_launcher import launch_blender_open
    launch_blender_open(project_path, project_id)

def import_segmentations(project_path, project_id, headless=False):
    from blender_launcher import launch_blender_import
    launch_blender_import(project_path, project_id, headless=headless)



def append_log(project_path: str, message: str):
    log_path = Path(project_path) / "Log.txt"
    log_path.touch(exist_ok=True)
    timestamp = now_iso()[:16].replace("T", " ")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")