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
SUPPORTED_EXTS = (".zip", ".7z", ".rar")
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


def list_recent_archives():
    archives = [
        p for p in DOWNLOADS_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS
    ]
    archives.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return archives[:MAX_LIST]


def select_archive_interactive() -> Path | None:
    archives = list_recent_archives()

    if not archives:
        print("No zip / 7z / rar files found in Downloads.")
        return None

    print("\nRecent archives:")
    for i, p in enumerate(archives, 1):
        mtime = datetime.fromtimestamp(p.stat().st_mtime)
        print(f"[{i}] {p.name}  ({mtime:%Y-%m-%d %H:%M})")

    print("\nSelect archive [1-{}] or paste full path".format(len(archives)))
    print("Press ENTER to cancel")

    choice = input("> ").strip()
    if not choice:
        return None

    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(archives):
            return archives[idx]
        raise RuntimeError("Invalid selection number")

    path = Path(choice.strip('"'))
    if not path.exists():
        raise RuntimeError(f"Archive not found: {path}")
    if path.suffix.lower() not in SUPPORTED_EXTS:
        raise RuntimeError("Unsupported archive format")

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

    archive = select_archive_interactive()
    if archive is None:
        print("Aborted.")
        return

    print(f"\nUsing archive: {archive}")

    dicom_dir.mkdir()
    extract_archive(archive, dicom_dir)

    if not contains_dicom(dicom_dir):
        shutil.rmtree(dicom_dir)
        raise RuntimeError("Extracted data does not appear to contain DICOM files")

    patient_name = extract_patient_name(dicom_dir)
    update_peek_case_patient(project_dir, patient_name)

    append_log(project_dir, f'DICOM ingested from "{archive.name}"')
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
