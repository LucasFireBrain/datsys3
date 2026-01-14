import shutil
from pathlib import Path
import zipfile
from datetime import datetime

# optional deps
import py7zr
import rarfile
import pydicom

from utils import load_json, save_json

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

DICOM_DIRNAME = "DICOM"
LOG_FILENAME = "Log.txt"
PEEK_CASE_FILENAME = "peekCase.json"

DOWNLOADS_DIR = Path.home() / "Downloads"
ARCHIVE_EXTS = (".zip", ".7z", ".rar")
SINGLE_DICOM_EXTS = (".dcm",)

MAX_LIST = 10


# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def confirm(msg: str) -> bool:
    return input(f"{msg} [y/N]: ").strip().lower() == "y"


def extract_archive(archive: Path, target_dir: Path):
    ext = archive.suffix.lower()

    if ext == ".zip":
        with zipfile.ZipFile(archive, "r") as z:
            z.extractall(target_dir)
    elif ext == ".7z":
        with py7zr.SevenZipFile(archive, "r") as z:
            z.extractall(target_dir)
    elif ext == ".rar":
        with rarfile.RarFile(archive, "r") as r:
            r.extractall(target_dir)
    else:
        raise RuntimeError(f"Unsupported archive format: {ext}")


def contains_dicom(folder: Path) -> bool:
    for p in folder.rglob("*"):
        if p.is_file() and (p.suffix.lower() == ".dcm" or p.suffix == ""):
            return True
    return False


def list_recent_inputs():
    items = []

    for p in DOWNLOADS_DIR.iterdir():
        if not p.is_file():
            continue
        if p.suffix.lower() in ARCHIVE_EXTS + SINGLE_DICOM_EXTS:
            items.append(p)

    items.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return items[:MAX_LIST]


def select_input_interactive() -> Path | None:
    items = list_recent_inputs()

    if not items:
        print("No DICOM archives or files found in Downloads.")
        return None

    print("\nRecent inputs:")
    for i, p in enumerate(items, 1):
        mtime = datetime.fromtimestamp(p.stat().st_mtime)
        print(f"[{i}] {p.name}  ({mtime:%Y-%m-%d %H:%M})")

    print("\nSelect [1-{}] or paste full path".format(len(items)))
    print("Press ENTER to cancel")

    choice = input("> ").strip()
    if not choice:
        return None

    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(items):
            return items[idx]
        raise RuntimeError("Invalid selection number")

    path = Path(choice.strip('"'))
    if not path.exists():
        raise RuntimeError(f"Path not found: {path}")

    return path


def append_log(project_dir: Path, message: str):
    log_path = project_dir / LOG_FILENAME
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


def extract_patient_name(dicom_dir: Path) -> str:
    for p in dicom_dir.rglob("*"):
        if not p.is_file():
            continue
        try:
            ds = pydicom.dcmread(p, stop_before_pixels=True)
            name = ds.get("PatientName", "")
            if name:
                return str(name)
        except Exception:
            pass
    return ""


def update_peek_case_patient(project_dir: Path, patient_name: str):
    if not patient_name:
        return

    peek_path = project_dir / PEEK_CASE_FILENAME
    if not peek_path.exists():
        return

    data = load_json(peek_path, {})
    if not data.get("nombre_paciente"):
        data["nombre_paciente"] = patient_name
        save_json(peek_path, data)


# --------------------------------------------------
# MAIN INGESTION
# --------------------------------------------------

def ingest_dicom(project_path: str):
    project_dir = Path(project_path)
    if not project_dir.exists():
        raise RuntimeError(f"Project path does not exist: {project_dir}")

    dicom_dir = project_dir / DICOM_DIRNAME

    if dicom_dir.exists():
        if not confirm("DICOM folder already exists. Replace it?"):
            print("Aborted.")
            return
        shutil.rmtree(dicom_dir)

    dicom_dir.mkdir()

    source = select_input_interactive()
    if source is None:
        print("Aborted.")
        return

    print(f"\nUsing input: {source}")

    # ---- HANDLE INPUT TYPES ----
    if source.is_dir():
        shutil.copytree(source, dicom_dir, dirs_exist_ok=True)

    elif source.suffix.lower() in ARCHIVE_EXTS:
        extract_archive(source, dicom_dir)

    elif source.suffix.lower() in SINGLE_DICOM_EXTS:
        shutil.copy2(source, dicom_dir / source.name)

    else:
        shutil.rmtree(dicom_dir)
        raise RuntimeError("Unsupported DICOM input")

    if not contains_dicom(dicom_dir):
        shutil.rmtree(dicom_dir)
        raise RuntimeError("Input does not appear to contain DICOM files")

    patient_name = extract_patient_name(dicom_dir)
    update_peek_case_patient(project_dir, patient_name)

    append_log(project_dir, f'DICOM ingested from "{source.name}"')
    print(f"[OK] DICOM ingested into: {dicom_dir}")


# --------------------------------------------------
# CLI ENTRY
# --------------------------------------------------

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python dicom_ingestion.py <project_path>")
        sys.exit(1)
    ingest_dicom(sys.argv[1])
