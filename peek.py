from pathlib import Path
from pydicom import dcmread

from utils import load_json, save_json, now_iso
from hospital_registry import choose_hospital_interactive
from price_list import list_regions, get_price

PEEK_CASE_FILENAME = "peekCase.json"

PEEK_CASE_SCHEMA = {
    "id_caso": "",
    "nombre_paciente": "",
    "nombre_doctor": "",
    "hospital_clinica": "",
    "region_anatomica": "",
    "complejidad": "",
    "requerimiento": "",
    "precio_base": 0,
    "precio_final": 0,
    "iva_incluido": True,
    "fecha_cirugia": "",
    "hora_cirugia": "",
    "fecha_entrega_estimada": "",
    "estado_caso": "",
    "notas": "",
    "creado_en": "",
    "actualizado_en": "",
}

# --------------------------------------------------
# LOGGING
# --------------------------------------------------

def log(msg: str):
    # Centralized, low-noise logging for peek operations
    print(f"[PEEK] {msg}")

# --------------------------------------------------
# LOW-LEVEL HELPERS
# --------------------------------------------------

def read_patient_from_dicom(dicom_dir: Path) -> str:
    # Scan all files until a PatientName is found
    for p in dicom_dir.rglob("*"):
        if not p.is_file():
            continue
        try:
            ds = dcmread(p, stop_before_pixels=True)
            name = getattr(ds, "PatientName", "")
            if name:
                return str(name)
        except Exception:
            # Ignore unreadable files silently, keep scanning
            pass
    return ""

def ensure_peek_case(project_dir: Path) -> dict:
    # Ensure peekCase.json exists and contains all schema keys
    peek_path = project_dir / PEEK_CASE_FILENAME

    if not peek_path.exists():
        log(f"peekCase.json not found, creating new one at {peek_path}")
        data = dict(PEEK_CASE_SCHEMA)
        data["id_caso"] = project_dir.name
        data["creado_en"] = now_iso()
        data["actualizado_en"] = now_iso()
        save_json(peek_path, data)

    data = load_json(peek_path, {})

    # Always enforce project ID (important for exports)
    data["id_caso"] = project_dir.name

    # Backfill missing keys (old cases)
    for k, v in PEEK_CASE_SCHEMA.items():
        data.setdefault(k, v)

    save_json(peek_path, data)
    return data


def save_peek_case(project_dir: Path, data: dict):
    # Always update timestamp on save
    data["actualizado_en"] = now_iso()
    save_json(project_dir / PEEK_CASE_FILENAME, data)
    log("peekCase.json saved")

# --------------------------------------------------
# ATOMIC SETTERS (NON-INTERACTIVE)
# --------------------------------------------------

def set_patient_name_from_dicom(project_dir: Path):
    dicom_dir = project_dir / "DICOM"
    log(f"Looking for DICOM directory: {dicom_dir}")

    if not dicom_dir.exists():
        log("DICOM directory not found, skipping patient extraction")
        return

    data = ensure_peek_case(project_dir)
    patient = read_patient_from_dicom(dicom_dir)

    if not patient:
        log("No PatientName found in DICOM files")
        return

    log(f"Patient name extracted from DICOM: {patient}")
    data["nombre_paciente"] = patient
    save_peek_case(project_dir, data)

def set_doctor_name_from_client(project_dir: Path):
    project_id = project_dir.name
    parts = project_id.split("-")

    if len(parts) < 2:
        log(f"Invalid project_id format: {project_id}")
        return

    # Enforce uppercase for consistency (Windows is case-insensitive, JSON is not)
    client_id = parts[1].upper()
    client_json = project_dir.parent / f"client_{client_id}.json"

    log(f"Looking for client file: {client_json}")

    if not client_json.exists():
        log("Client JSON not found, skipping doctor name")
        return

    client = load_json(client_json, {})
    name = client.get("name")

    if not name:
        log("Client name missing in client JSON")
        return

    log(f"Doctor name resolved from client: {name}")
    data = ensure_peek_case(project_dir)
    data["nombre_doctor"] = name
    save_peek_case(project_dir, data)

# --------------------------------------------------
# INIT (ORCHESTRATION ONLY)
# --------------------------------------------------

def init_peek_case(project_path: str):
    project_dir = Path(project_path)
    log(f"Initializing peekCase.json for project: {project_dir}")

    # Ensure file exists first
    ensure_peek_case(project_dir)

    # Sync metadata from authoritative sources
    set_doctor_name_from_client(project_dir)
    set_patient_name_from_dicom(project_dir)

    log("peekCase.json initialization complete")

# --------------------------------------------------
# INTERACTIVE EDIT (LEGACY / FALLBACK)
# --------------------------------------------------

def prompt_date(label: str) -> str:
    print(f"\n{label} (ENTER to skip, Q to leave blank)")
    y = input("Year (YYYY or YY): ").strip()
    if not y or y.lower() == "q":
        return ""
    if len(y) == 2:
        y = f"20{y}"
    m = input("Month (MM): ").strip()
    d = input("Day (DD): ").strip()
    return f"{y}-{m.zfill(2)}-{d.zfill(2)}"

def prompt_peek_case(project_path: str):
    project_dir = Path(project_path)
    data = ensure_peek_case(project_dir)

    print("\n--- PEEK Case Info (interactive / fallback) ---")
    print("Press ENTER to skip | Type 0 to stop\n")

    val = input(f"nombre_paciente [{data['nombre_paciente']}]: ").strip()
    if val == "0":
        return
    if val:
        data["nombre_paciente"] = val

    hospital = choose_hospital_interactive()
    if hospital:
        data["hospital_clinica"] = hospital

    regions = list_regions()
    print("\nRegión anatómica:")
    for i, r in enumerate(regions, 1):
        print(f"[{i}] {r}")

    val = input("> ").strip()
    if val.isdigit() and 1 <= int(val) <= len(regions):
        data["region_anatomica"] = regions[int(val) - 1]

    val = input("Complejidad (A/B/C/D): ").strip().upper()
    if val in ("A", "B", "C", "D"):
        data["complejidad"] = val

    if data["region_anatomica"] and data["complejidad"]:
        base = get_price(data["region_anatomica"], data["complejidad"])
        data["precio_base"] = base
        val = input(f"Precio final [{base}]: ").strip()
        data["precio_final"] = int(val) if val else base

    val = input(f"requerimiento [{data['requerimiento']}]: ").strip()
    if val:
        data["requerimiento"] = val

    fc = prompt_date("Fecha cirugía")
    if fc:
        data["fecha_cirugia"] = fc

    fe = prompt_date("Fecha entrega estimada")
    if fe:
        data["fecha_entrega_estimada"] = fe

    val = input(f"estado_caso [{data['estado_caso']}]: ").strip()
    if val:
        data["estado_caso"] = val

    val = input(f"notas [{data['notas']}]: ").strip()
    if val:
        data["notas"] = val

    save_peek_case(project_dir, data)
