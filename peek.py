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

# -------------------------
# HELPERS
# -------------------------

def read_patient_from_dicom(dicom_dir: Path) -> str:
    for p in dicom_dir.rglob("*"):
        if not p.is_file():
            continue
        try:
            ds = dcmread(p, stop_before_pixels=True)
            name = getattr(ds, "PatientName", "")
            if name:
                return str(name)
        except Exception:
            pass
    return ""


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


# -------------------------
# INIT
# -------------------------

def init_peek_case(project_path: str):
    project_dir = Path(project_path)
    case_path = project_dir / PEEK_CASE_FILENAME

    project_id = project_dir.name
    client_id = project_id.split("-")[1]
    client_json = project_dir.parent / f"client_{client_id}.json"
    client = load_json(client_json, {})

    if case_path.exists():
        return

    data = dict(PEEK_CASE_SCHEMA)
    data["id_caso"] = project_id
    data["nombre_doctor"] = client.get("name", "")
    data["creado_en"] = now_iso()
    data["actualizado_en"] = now_iso()

    dicom_dir = project_dir / "DICOM"
    if dicom_dir.exists():
        data["nombre_paciente"] = read_patient_from_dicom(dicom_dir)

    save_json(case_path, data)


# -------------------------
# INTERACTIVE EDIT
# -------------------------

def prompt_peek_case(project_path: str):
    project_dir = Path(project_path)
    case_path = project_dir / PEEK_CASE_FILENAME

    init_peek_case(project_path)
    data = load_json(case_path, dict(PEEK_CASE_SCHEMA))

    # Ensure missing keys (old cases)
    for k, v in PEEK_CASE_SCHEMA.items():
        data.setdefault(k, v)

    print("\n--- PEEK Case Info ---")
    print("Press ENTER to skip | Type 0 to stop\n")

    print(f"id_caso [{data.get('id_caso','')}]")

    val = input(f"nombre_paciente [{data.get('nombre_paciente','')}]: ").strip()
    if val == "0":
        return
    if val:
        data["nombre_paciente"] = val

    print(f"nombre_doctor [{data.get('nombre_doctor','')}]")

    hospital = choose_hospital_interactive()
    if hospital:
        data["hospital_clinica"] = hospital

    # -------- Región anatómica --------
    regions = list_regions()
    print("\nRegión anatómica:")
    for i, r in enumerate(regions, 1):
        print(f"[{i}] {r}")

    val = input("> ").strip()
    if val == "0":
        return
    if val.isdigit() and 1 <= int(val) <= len(regions):
        data["region_anatomica"] = regions[int(val) - 1]

    # -------- Complejidad --------
    val = input("Complejidad (A/B/C/D): ").strip().upper()
    if val in ("A", "B", "C", "D"):
        data["complejidad"] = val

    # -------- Precio --------
    if data.get("region_anatomica") and data.get("complejidad"):
        base = get_price(data["region_anatomica"], data["complejidad"])
        data["precio_base"] = base
        print(f"Precio base: ${base:,}")

        val = input(f"Precio final [{base}]: ").strip()
        data["precio_final"] = int(val) if val else base

    # -------- Resto --------
    val = input(f"requerimiento [{data.get('requerimiento','')}]: ").strip()
    if val:
        data["requerimiento"] = val

    val = input(f"iva_incluido [{data.get('iva_incluido',True)}]: ").strip().lower()
    if val in ("true", "false"):
        data["iva_incluido"] = val == "true"

    fc = prompt_date("Fecha cirugía")
    if fc:
        data["fecha_cirugia"] = fc

    fe = prompt_date("Fecha entrega estimada")
    if fe:
        data["fecha_entrega_estimada"] = fe

    val = input(f"estado_caso [{data.get('estado_caso','')}]: ").strip()
    if val:
        data["estado_caso"] = val

    val = input(f"notas [{data.get('notas','')}]: ").strip()
    if val:
        data["notas"] = val

    data["actualizado_en"] = now_iso()
    save_json(case_path, data)
