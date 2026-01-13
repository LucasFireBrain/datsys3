import os
import csv
from utils import load_json, save_json, now_iso, DATA_DIR

PEEK_CASE_FILENAME = "peekCase.json"

PEEK_CASE_SCHEMA = {
    "id_caso": "",
    "nombre_paciente": "",
    "nombre_doctor": "",
    "hospital_clinica": "",
    "fecha_cirugia": "",
    "hora_cirugia": "",
    "region": "",
    "especificaciones": "",
    "requiere_material_adicional": "",
    "precio_clp": 0,
    "iva_incluido": True,
    "fecha_entrega_estimada": "",
    "estado_caso": "",
    "notas": "",
    "link_dicom": "",
    "creado_en": "",
    "actualizado_en": ""
}

# -------------------------
# HOSPITALS
# -------------------------

def load_hospitals():
    path = os.path.join(DATA_DIR, "hospitals.csv")
    hospitals = {}

    if not os.path.exists(path):
        return hospitals

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if len(row) >= 2:
                code, name = row[0].strip(), row[1].strip()
                hospitals[code] = name

    return hospitals

# -------------------------
# DATE PROMPT
# -------------------------

def prompt_date(label):
    print(f"\n{label} (ENTER to skip, Q to leave blank)")

    y = input("Year (YYYY or YY): ").strip()
    if not y or y.upper() == "Q":
        return ""

    if len(y) == 2 and y.isdigit():
        y = "20" + y

    m = input("Month (MM): ").strip()
    if not m:
        return ""

    d = input("Day (DD): ").strip()
    if not d:
        return ""

    return f"{y}-{m.zfill(2)}-{d.zfill(2)}"

# -------------------------
# CASE INIT
# -------------------------

def init_peek_case(project_path, project_id, doctor_name=""):
    case_path = os.path.join(project_path, PEEK_CASE_FILENAME)

    if os.path.exists(case_path):
        return case_path

    data = dict(PEEK_CASE_SCHEMA)
    data["id_caso"] = project_id
    data["nombre_doctor"] = doctor_name
    data["creado_en"] = now_iso()
    data["actualizado_en"] = now_iso()

    save_json(case_path, data)
    return case_path

# -------------------------
# INTERACTIVE EDIT
# -------------------------

def prompt_peek_case(project_path):
    case_path = os.path.join(project_path, PEEK_CASE_FILENAME)
    data = load_json(case_path, dict(PEEK_CASE_SCHEMA))

    hospitals = load_hospitals()

    print("\n--- PEEK Case Info ---")
    print("Press ENTER to skip | Type 0 to stop\n")

    for key in data.keys():

        if key in ("creado_en", "actualizado_en"):
            continue

        if key == "id_caso":
            print(f"id_caso [{data[key]}]")
            continue

        if key == "nombre_doctor":
            print(f"nombre_doctor [{data[key]}]")
            continue

        if key == "fecha_cirugia":
            val = prompt_date("Fecha cirugía")
            if val:
                data[key] = val
            continue

        if key == "fecha_entrega_estimada":
            val = prompt_date("Fecha entrega estimada")
            if val:
                data[key] = val
            continue

        if key == "hospital_clinica" and hospitals:
            print("\nHospital:")
            for i, (code, name) in enumerate(hospitals.items(), 1):
                print(f"[{i}] {code} - {name}")
            print("Or type manually:")

            choice = input("> ").strip()
            if choice == "0":
                break

            if choice.isdigit() and 1 <= int(choice) <= len(hospitals):
                data[key] = list(hospitals.values())[int(choice) - 1]
            elif choice:
                data[key] = choice
            continue

        val = input(f"{key} [{data.get(key,'')}]: ").strip()
        if val == "0":
            break
        if val:
            data[key] = val

    data["actualizado_en"] = now_iso()
    save_json(case_path, data)
