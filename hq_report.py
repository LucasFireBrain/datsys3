from pathlib import Path
from datetime import datetime

from utils import CLIENTS_DIR, load_json

IVA_FACTOR = 1.19

HQ_HEADERS = [
    "ID del Caso",
    "Nombre del Doctor",
    "Hospital",
    "Nombre del Paciente",
    "Contacto",
    "Fecha Ingreso",
    "Fecha Entrega",
    "DC",
    "Fecha Cirugía",
    "Descripcion",
    "Precio Implante (IVA Incluido)",
    "Neto",
]

# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def log(msg: str):
    print(f"[HQ] {msg}")

def safe(v):
    return "" if v is None else str(v)

def title_case_name(s: str) -> str:
    # Simple, predictable title case (export-only)
    return " ".join(w.capitalize() for w in s.split())

def normalize_dicom_name(raw: str) -> str:
    """
    Convert DICOM PN:
      'PEREZ LOPEZ^JUAN'
    -> 'Juan Perez Lopez'

    Applied ONLY at export time.
    """
    if not raw:
        return ""

    parts = str(raw).replace(",", "").split("^")

    if len(parts) == 1:
        return title_case_name(parts[0].strip())

    last = title_case_name(parts[0].strip())
    first = title_case_name(parts[1].strip())

    return f"{first} {last}"

def compute_neto(precio_final, iva_incluido=True):
    try:
        p = float(precio_final)
    except Exception:
        return ""
    if iva_incluido:
        return int(round(p / IVA_FACTOR))
    return int(round(p))

# --------------------------------------------------
# EXPORT
# --------------------------------------------------

def export_hq_tsv(out_path: Path):
    rows = []

    clients_root = Path(CLIENTS_DIR)
    if not clients_root.exists():
        log("CLIENTS_DIR not found")
        return

    for client_dir in clients_root.iterdir():
        if not client_dir.is_dir():
            continue

        client_id = client_dir.name.upper()
        client_json = client_dir / f"client_{client_id}.json"
        client = load_json(client_json, {}) if client_json.exists() else {}

        for project_dir in client_dir.iterdir():
            if not project_dir.is_dir():
                continue

            peek_path = project_dir / "peekCase.json"
            if not peek_path.exists():
                continue

            peek = load_json(peek_path, {})

            # ---- Patient name (normalize ONLY for export) ----
            raw_patient = (
                peek.get("nombre_paciente_dicom")
                or peek.get("nombre_paciente")
                or ""
            )
            patient_name = normalize_dicom_name(raw_patient)

            precio_final = peek.get("precio_final", "")
            iva_incluido = peek.get("iva_incluido", True)

            row = [
                safe(peek.get("id_caso")),
                title_case_name(safe(peek.get("nombre_doctor"))),
                safe(peek.get("hospital_clinica")),
                patient_name,
                safe(client.get("contact")),
                safe(peek.get("creado_en")),
                safe(peek.get("fecha_entrega_estimada")),
                safe(peek.get("complejidad")),
                safe(peek.get("fecha_cirugia")),
                safe(peek.get("requerimiento")),
                safe(precio_final),
                safe(compute_neto(precio_final, iva_incluido)),
            ]

            rows.append(row)

    if not rows:
        log("No cases found to export")
        return

    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\t".join(HQ_HEADERS) + "\n")
        for r in rows:
            f.write("\t".join(r) + "\n")

    log(f"Exported {len(rows)} rows to {out_path}")

# --------------------------------------------------
# DEFAULT ENTRYPOINT
# --------------------------------------------------

def export_hq_tsv_default():
    today = datetime.today().strftime("%Y-%m-%d")
    out = Path("exports") / f"HQ_EXPORT_{today}.tsv"
    export_hq_tsv(out)
