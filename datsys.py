import os
from utils import (
    CLIENTS_DIR,
    ensure_dir,
    list_dirs,
    load_json,
    save_json,
    now_iso
)

from peek.peek import init_peek_case, prompt_peek_case

# -------------------------
# CLIENTS
# -------------------------

def get_client(client_id):
    client_dir = os.path.join(CLIENTS_DIR, client_id)
    if not os.path.isdir(client_dir):
        return None, None

    for f in os.listdir(client_dir):
        if f.startswith("client_") and f.endswith(".json"):
            return load_json(os.path.join(client_dir, f)), client_dir

    return None, client_dir

def create_client(client_id):
    client_dir = os.path.join(CLIENTS_DIR, client_id)
    ensure_dir(client_dir)

    name = input("Client name: ").strip()
    contact = input("Contact info: ").strip()

    data = {
        "id": client_id,
        "name": name,
        "contact": contact,
        "project_count": 0,
        "created_at": now_iso()
    }

    path = os.path.join(client_dir, f"client_{client_id}.json")
    save_json(path, data)
    return data, client_dir

# -------------------------
# PROJECTS
# -------------------------

def next_project_id(client, client_dir, project_type):
    client["project_count"] += 1
    suffix = client["project_count"]

    year_code = "Q"  # placeholder, you can refine later
    pid = f"{year_code}{suffix:02d}-{client['id']}-{project_type}"

    save_json(
        os.path.join(client_dir, f"client_{client['id']}.json"),
        client
    )
    return pid

def create_project(client, client_dir):
    print("\nProject type:")
    print("[1] PK - PEEK")
    choice = input("> ").strip()

    if choice != "1":
        print("Only PK supported for now.")
        return

    project_type = "PK"
    pid = next_project_id(client, client_dir, project_type)

    project_path = os.path.join(client_dir, pid)
    ensure_dir(project_path)

    print(f"\nProject created: {pid}")

    init_peek_case(project_path, doctor_name=client["name"])
    prompt_peek_case(project_path)

# -------------------------
# CLI
# -------------------------

def main():
    ensure_dir(CLIENTS_DIR)

    while True:
        print("\n=== DATSYS ===")
        print("[1] New project")
        print("[2] Exit")

        choice = input("> ").strip()

        if choice == "1":
            client_id = input("Enter client ID: ").strip().upper()
            client, client_dir = get_client(client_id)

            if client:
                print(f"Client found: {client['name']}")
            else:
                print("New client.")
                client, client_dir = create_client(client_id)

            create_project(client, client_dir)

        elif choice == "2":
            break

if __name__ == "__main__":
    main()
