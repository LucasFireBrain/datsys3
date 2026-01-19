import subprocess
from utils import update_stage
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
def launch_blender_open(project_path: str, project_id: str):
    blend_file = Path(project_path) / "Blender" / f"{project_id}.blend"
    subprocess.Popen([str(BLENDER_EXE), str(blend_file)])
    update_stage(project_root, "Design")

def launch_blender_import(project_path: str, project_id: str, headless=False):
    blend_file = Path(project_path) / "Blender" / f"{project_id}.blend"
    script_file = Path(__file__).parent / "blender_initialization.py"

    cmd = [
        str(BLENDER_EXE),
        str(blend_file),
        "--python",
        str(script_file),
    ]

    if headless:
        cmd.insert(1, "--background")

    subprocess.Popen(cmd)
    


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
