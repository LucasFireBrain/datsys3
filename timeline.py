from pathlib import Path
from datetime import datetime, date, timedelta
from utils import CLIENTS_DIR, load_json
from datsys import (
    import_segmentations,
    init_clients_dir,
    new_project,
    open_project_folder,
    open_log,
    open_peek_case,
    ingest_project_dicom,
    open_slicer,
    open_blender,
    import_segmentations,   
    append_log,
)

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def wait_for_enter():
    input("\n[Press ENTER to continue]")

def parse_date(s):
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except Exception:
        return None


def business_days_left(deadline_date):
    """
    Count days until deadline, excluding Sundays.
    """
    if not deadline_date:
        return None

    today = date.today()
    if deadline_date < today:
        return 0

    days = 0
    d = today
    while d < deadline_date:
        if d.weekday() != 6:  # Sunday
            days += 1
        d += timedelta(days=1)

    return days


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def collect_rows():
    rows = []

    clients_path = Path(CLIENTS_DIR)
    if not clients_path.exists():
        return rows

    for client_dir in clients_path.iterdir():
        if not client_dir.is_dir():
            continue

        for project_dir in client_dir.iterdir():
            if not project_dir.is_dir():
                continue

            peek_path = project_dir / "peekCase.json"
            if not peek_path.exists():
                continue

            peek = load_json(peek_path, {})

            deadline_date = parse_date(peek.get("fecha_entrega_estimada", ""))
            dleft = business_days_left(deadline_date)

            rows.append({
                "project_id": project_dir.name,
                "request_date": peek.get("creado_en", "")[:10],
                "deadline": peek.get("fecha_entrega_estimada", ""),
                "days_left": dleft,
                "surgery": peek.get("fecha_cirugia", ""),
                "region": peek.get("region_anatomica", ""),
                "complexity": peek.get("complejidad", ""),
                "stage": peek.get("estado_caso", ""),
            })

    # --------------------------------------------------
    # SORT (UNCHANGED – this is your stable logic)
    # --------------------------------------------------
    rows.sort(
        key=lambda r: (
            r["days_left"] is not None,                 # backlog first (None)
            -(r["days_left"] if r["days_left"] is not None else 0),  # urgent LAST
            r["project_id"]
        )
    )


    return rows

def render_timeline(rows):
    if not rows:
        print("\nNo active cases found.")
        return

    total = len(rows)

    # --------------------------------------------------
    # PRINT TABLE (NO HEADER AT TOP)
    # --------------------------------------------------
    print("\n==================== CASE TIMELINE ====================")

    for i, r in enumerate(rows):
        idx = total - i   # bottom row = 1
        print(
            f"{idx:<3} "
            f"{r['project_id']:<15} "
            f"{r['deadline']:<10} "
            f"{str(r['days_left']) if r['days_left'] is not None else '':<6} "
            f"{r['surgery']:<10} "
            f"{r['region']:<15} "
            f"{r['complexity']:<4} "
            f"{r['stage']:<20}"
        )

    # --------------------------------------------------
    # HEADER AT BOTTOM (as requested)
    # --------------------------------------------------
    print("-" * 110)
    print(
        f"{'#':<3} {'CaseID':<15} {'Deadline':<10} "
        f"{'ΔDays':<6} {'Surgery':<10} {'Region':<15} "
        f"{'Cpx':<4} {'Stage':<20}"
    )

def resolve_project_id(selector, rows):
    if not selector:
        return None

    total = len(rows)

    if selector.isdigit():
        n = int(selector)
        if 1 <= n <= total:
            return rows[total - n]["project_id"]
        return None

    for r in rows:
        if r["project_id"] == selector:
            return selector

    return None

COMMANDS = [
    "new",
    "help",
    "quit",
    "<case>, stage, <value>",
    "<case>, log, <message>",
    "<case>, open",
    "<case>, logopen",
    "<case>, edit",
    "<case>, dicom",
    "<case>, slicer",
    "<case>, blender",
]

def print_help():
    print("\nCommands:")
    print(" | ".join(COMMANDS))


def prompt_new_project():
    client_id = input("Client ID: ").strip().upper()
    if not client_id:
        print("Missing client ID.")
        return None

    name = input("Client full name (ENTER to skip): ").strip()
    contact = input("Contact info (ENTER to skip): ").strip()

    print("\nProject type:")
    print("[1] PK - PEEK")
    print("[2] PL - PLA")
    print("[3] AR - Archive")
    t = input("> ").strip()
    type_map = {"1": "PK", "2": "PL", "3": "AR"}
    if t not in type_map:
        print("Invalid project type.")
        return None

    return client_id, type_map[t], name, contact

def handle_command(command, rows):
    if not command:
        return True

    if command in ("q", "quit", "exit"):
        return False

    if command == "help":
        print_help()
        wait_for_enter()
        return True

    if command == "new":
        result = prompt_new_project()
        if not result:
            return True
        client_id, project_type, name, contact = result
        project_id, _project_dir = new_project(
            client_id=client_id,
            project_type=project_type,
            name=name,
            contact=contact,
        )
        print(f"[OK] Project created: {project_id}")
        return True

    parts = [p.strip() for p in command.split(",")]
    if len(parts) < 2:
        print("Invalid command. Type 'help'.")
        return True

    selector = parts[0]
    action = parts[1].lower()
    args = parts[2:]

    project_id = resolve_project_id(selector, rows)
    if not project_id:
        print("Project not found.")
        return True

    client_id = project_id.split("-")[1]
    project_dir = Path(CLIENTS_DIR) / client_id / project_id

    if action == "stage":
        if not args:
            print("Missing stage value.")
            return True
        value = args[0]
        message = ", ".join(args[1:]).strip() if len(args) > 1 else None
        from utils import update_stage
        update_stage(project_dir, value, message=message)
        print(f"[OK] Stage updated: {project_id} → {value}")
        return True

    if action == "log":
        if not args:
            print("Missing log message.")
            return True
        message = ", ".join(args)
        append_log(project_dir, message)
        print("[OK] Log appended.")
        return True

    if action == "open":
        open_project_folder(project_dir)
        return True

    if action == "logopen":
        open_log(project_dir)
        return True

    if action == "edit":
        open_peek_case(project_dir)
        return True

    if action == "dicom":
        ingest_project_dicom(project_dir)
        return True

    if action == "slicer":
        open_slicer(project_dir)
        return True

    if action == "blender":
        open_blender(project_dir, project_id)
        return True

    if action == "import":
        import_segmentations(project_dir, project_id)
        return True

    if action == "importbg":
        import_segmentations(project_dir, project_id, headless=True)
        return True



    print("Unknown action. Type 'help'.")
    return True

def run_timeline_shell():
    init_clients_dir()
    while True:
        rows = collect_rows()
        render_timeline(rows)
        command = input("\n> ").strip()
        if not handle_command(command, rows):
            break

if __name__ == "__main__":
    run_timeline_shell()

