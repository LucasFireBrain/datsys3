from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
HOSPITALS_CSV = DATA_DIR / "hospitals.csv"


def ensure_registry():
    DATA_DIR.mkdir(exist_ok=True)
    if not HOSPITALS_CSV.exists():
        HOSPITALS_CSV.touch()


def load_hospitals():
    """
    Returns list of (code, name)
    """
    ensure_registry()
    hospitals = []

    with open(HOSPITALS_CSV, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            code, name = line.strip().split("\t", 1)
            hospitals.append((code.upper(), name.strip()))

    return hospitals


def append_hospital(code: str, name: str):
    ensure_registry()
    with open(HOSPITALS_CSV, "a", encoding="utf-8") as f:
        f.write(f"{code.upper()}\t{name.strip()}\n")


def choose_hospital_interactive() -> str:
    hospitals = load_hospitals()

    if hospitals:
        print("\nHospital:")
        for i, (code, name) in enumerate(hospitals, 1):
            print(f"[{i}] {code} - {name}")

    print("Select by number, 3-letter code, or full name")
    val = input("> ").strip()

    if not val:
        return ""

    # --- numeric choice ---
    if val.isdigit():
        idx = int(val) - 1
        if 0 <= idx < len(hospitals):
            return hospitals[idx][1]
        print("Invalid selection")
        return ""

    val_lower = val.lower()

    # --- code or name lookup ---
    for code, name in hospitals:
        if val.upper() == code or val_lower == name.lower():
            return name

    # --- not found: ask to create ---
    create = input("Hospital not found. Create it? [y/N]: ").strip().lower()
    if create != "y":
        return ""

    # determine code + name
    if len(val) == 3 and val.isalpha():
        code = val.upper()
        name = input("New hospital name: ").strip()
    else:
        name = val
        code = name[:3].upper()

    append_hospital(code, name)
    print(f"[OK] Added hospital: {code} - {name}")
    return name
