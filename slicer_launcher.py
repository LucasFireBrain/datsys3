import subprocess
from pathlib import Path

SLICER_EXE = Path(r"C:\Users\Lucas\AppData\Local\slicer.org\Slicer 5.8.0\Slicer.exe")
SLICER_SCRIPT = Path(__file__).parent / "tools/slicer_autoload_volume.py"

def launch_slicer_with_dicom(dicom_dir):
    dicom_dir = Path(dicom_dir)  # 🔧 FIX

    if not dicom_dir.exists():
        raise RuntimeError(f"DICOM folder not found: {dicom_dir}")

    subprocess.Popen([
        str(SLICER_EXE),
        "--python-script",
        str(SLICER_SCRIPT),
        str(dicom_dir),
    ])