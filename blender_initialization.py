import bpy
from pathlib import Path

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

# Path to current .blend
BLEND_PATH = Path(bpy.data.filepath).resolve()

# Project root = parent of "Blender"
PROJECT_ROOT = BLEND_PATH.parent.parent

SEG_DIR = PROJECT_ROOT / "3DSlicer" / "Segmentations"

RENAME_RULES = {
    "skull_solid": "Skull Solid",
    "mandible_solid": "Mandible Solid",
    "mandible": "Mandible",
    "skull": "Skull",
    "upper teeth": "Upper Teeth",
    "lower teeth": "Lower Teeth",
    "skin": "Skin",
    "mandibular canal": "Mandibular Canal",
}

SUPPORTED_EXTS = {".stl", ".obj", ".ply"}

# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def import_mesh(path: Path):
    ext = path.suffix.lower()

    if ext == ".stl":
        bpy.ops.wm.stl_import(filepath=str(path))
    elif ext == ".obj":
        bpy.ops.wm.obj_import(filepath=str(path))
    else:
        print(f"[BLENDER] Unsupported mesh type: {path.name}")


def rename_object(obj):
    name = obj.name.lower()
    for key, target in RENAME_RULES.items():
        if key in name:
            obj.name = target
            return True
    return False

# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():
    if not bpy.data.filepath:
        raise RuntimeError("Blend file must be saved")

    project_root = Path(bpy.data.filepath).parent
    seg_path = project_root / SEG_DIR

    if not seg_path.exists():
        print(f"[BLENDER] No segmentations found: {seg_path}")
        return

    print(f"[BLENDER] Importing from {seg_path}")

    imported = []

    for file in seg_path.rglob("*"):
        if file.suffix.lower() not in SUPPORTED_EXTS:
            continue

        before = set(bpy.data.objects)
        import_mesh(file)
        after = set(bpy.data.objects)

        imported.extend(after - before)

    for obj in imported:
        if rename_object(obj):
            print(f"[BLENDER] Renamed → {obj.name}")
        else:
            print(f"[BLENDER] Unmatched → {obj.name}")

    print("[BLENDER] Initialization complete")

# --------------------------------------------------

if __name__ == "__main__":
    main()
