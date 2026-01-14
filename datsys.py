import os
import shutil
from pathlib import Path

from dicom_ingestion import ingest_dicom
from utils import (
    CLIENTS_DIR,
    ensure_dir,
    list_dirs,
    load_json,
    save_json,
    now_iso,
    date_code_base36,
)

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
PEEK_TEMPLATE_DIR = TEMPLATES_DIR / "PK"

# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def prompt(msg):
    return input(msg).strip()

def select_from_list(items, title):
    if not items:
        print("Nothing found.")
        return None

    print(f"\n--- {title} ---")
    for i, item in enumerate(items, 1):
        print(f"[{i}] {item}")
    print("[B] Back")

    choice = prompt("> ").lower()
    if choice == "b":
        return None

    if not choice.isdigit():
        return None

    idx = int(choice) - 1
    if 0 <= idx < len(items):
        return items[idx]

    return None

# --------------------------------------------------
# PROJECT MENU
# --------------------------------------------------

def project_menu(client_id, project_id, project_path):
    while True:
        print("\n==============================")
        print(f"Client:  {client_id}")
        print(f"Project: {project_id}")
        print("==============================")

        print("[1] Open project folder")
        print("[2] Open LOG.txt")
        print("[3] PEEK Case Info")
        print("[4] Ingest DICOM")
        print("[5] Open in 3D Slicer")
        print("[6] Open in Blender")
        print("[B] Back")

        choice = prompt("> ").lower()

        if choice == "1":
            os.startfile(project_path)

        elif choice == "2":
            log_path = Path(project_path) / "Log.txt"
            log_path.touch(exist_ok=True)
            os.startfile(log_path)

        elif choice == "3":
            from peek import prompt_peek_case
            prompt_peek_case(project_path)

        elif choice == "4":
            ingest_dicom(project_path)

        elif choice == "5":
            from slicer_launcher import launch_slicer_with_dicom
            dicom_dir = Path(project_path) / "DICOM"
            launch_slicer_with_dicom(dicom_dir)
        elif choice == "6":
            from blender_launcher import launch_blender
            launch_blender(project_path, project_id)

        elif choice == "b":
            return

# --------------------------------------------------
# NEW PROJECT
# --------------------------------------------------

def new_project():
    ensure_dir(CLIENTS_DIR)

    client_id = prompt("Enter client ID: ").upper()
    if not client_id:
        return

    client_dir = Path(CLIENTS_DIR) / client_id
    client_json_path = client_dir / f"client_{client_id}.json"

    if not client_dir.exists():
        print("New client detected.")
        name = prompt("Client full name: ")
        contact = prompt("Contact info: ")

        client_dir.mkdir(parents=True)
        save_json(client_json_path, {
            "id": client_id,
            "name": name,
            "contact": contact,
            "created_at": now_iso(),
            "project_count": 0,
        })
    else:
        client = load_json(client_json_path, {})
        print(f"Client found: {client.get('name','')} ({client_id})")
        if prompt("Continue? [y/N]: ").lower() != "y":
            return

    print("\nProject type:")
    print("[1] PK - PEEK")
    print("[2] PL - PLA")
    print("[3] AR - Archive")

    t = prompt("> ")
    type_map = {"1": "PK", "2": "PL", "3": "AR"}
    if t not in type_map:
        return

    project_type = type_map[t]

    client = load_json(client_json_path, {})
    suffix = client.get("project_count", 0) + 1
    client["project_count"] = suffix
    save_json(client_json_path, client)

    date_code = date_code_base36()
    project_id = f"{date_code}-{client_id}-{project_type}{suffix}"
    project_dir = client_dir / project_id
    project_dir.mkdir()

    # ---- TEMPLATE COPY ----
    if project_type == "PK":
        if not PEEK_TEMPLATE_DIR.exists():
            raise RuntimeError("PEEK template folder missing")
        shutil.copytree(
            PEEK_TEMPLATE_DIR,
            project_dir,
            dirs_exist_ok=True
        )
    # ---- RENAME PEEK BLEND TEMPLATE ----
    if project_type == "PK":
        old_blend = project_dir / "Blender" / "PEEK.blend"
        new_blend = project_dir / "Blender" / f"{project_id}.blend"

        if old_blend.exists() and not new_blend.exists():
            old_blend.rename(new_blend)

    # ---- CASE METADATA ----
    save_json(
        project_dir / f"{project_id}.json",
        {
            "id": project_id,
            "client_id": client_id,
            "type": project_type,
            "created_at": now_iso(),
        },
    )

    print(f"\nProject created: {project_id}")
    project_menu(client_id, project_id, project_dir)

# --------------------------------------------------
# OPEN PROJECT
# --------------------------------------------------

def open_project():
    clients = list_dirs(CLIENTS_DIR)
    client_id = select_from_list(clients, "Select client")
    if not client_id:
        return

    client_dir = Path(CLIENTS_DIR) / client_id
    projects = list_dirs(client_dir)
    project_id = select_from_list(projects, "Select project")
    if not project_id:
        return

    project_dir = client_dir / project_id
    project_menu(client_id, project_id, project_dir)

# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():
    ensure_dir(CLIENTS_DIR)

    while True:
        print("\n=== DATSYS ===")
        print("[1] New project")
        print("[2] Open project")
        print("[3] Exit")

        choice = prompt("> ")

        if choice == "1":
            new_project()
        elif choice == "2":
            open_project()
        elif choice == "3":
            break

if __name__ == "__main__":
    main()
