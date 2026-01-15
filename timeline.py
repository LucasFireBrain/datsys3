from pathlib import Path
from datetime import datetime, date, timedelta
from utils import CLIENTS_DIR, load_json

# --------------------------------------------------
# HELPERS
# --------------------------------------------------

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

def show_timeline():
    rows = []

    for client_dir in Path(CLIENTS_DIR).iterdir():
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
                "region": peek.get("region", ""),
                "complexity": peek.get("complejidad", ""),
                "stage": peek.get("estado_caso", ""),
            })

    if not rows:
        print("\nNo active cases found.")
        input("\nPress ENTER to return...")
        return None

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

    # --------------------------------------------------
    # SELECTION
    # --------------------------------------------------
    choice = input(
        "\nSelect case by [number], ProjectID, or press ENTER to go back: "
    ).strip()

    if not choice:
        return None

    if choice.isdigit():
        n = int(choice)
        if 1 <= n <= total:
            return rows[total - n]["project_id"]

    for r in rows:
        if r["project_id"] == choice:
            return choice

    print("Project not found.")
    input("Press ENTER...")
    return None
