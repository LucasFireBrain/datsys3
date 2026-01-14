import subprocess
from pathlib import Path

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

# Adjust if needed
BLENDER_EXE = Path(
    r"C:\Program Files\Blender Foundation\Blender 4.4\blender.exe"
)

SCRIPT_NAME = "blender_initialization.py"

# --------------------------------------------------
# LAUNCHER
# --------------------------------------------------

def launch_blender(project_path: str, project_id: str):
    project_dir = Path(project_path)
    blend_file = project_dir / "Blender" / f"{project_id}.blend"
    script_file = Path(__file__).parent / SCRIPT_NAME

    if not BLENDER_EXE.exists():
        raise RuntimeError("Blender executable not found")

    if not blend_file.exists():
        raise RuntimeError(f"Blend file not found: {blend_file}")

    if not script_file.exists():
        raise RuntimeError(f"Init script not found: {script_file}")

    cmd = [
        str(BLENDER_EXE),
        str(blend_file),
        "--python",
        str(script_file),
    ]

    subprocess.Popen(cmd)  # non-blocking
    print("[OK] Blender launched")
