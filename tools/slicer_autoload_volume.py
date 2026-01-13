import sys
import os
import slicer
from DICOMLib import DICOMUtils

KEYWORDS = ["bone", "hard", "tac", "axial", "dr", "hueso", "oseo"]

def score_name(name: str) -> int:
    n = name.lower()
    return sum(1 for k in KEYWORDS if k in n)

def main():
    if len(sys.argv) < 2:
        raise RuntimeError("Usage: slicer_autoload_volume.py <DICOM_FOLDER>")

    dicom_dir = sys.argv[-1]
    if not os.path.isdir(dicom_dir):
        raise RuntimeError(f"DICOM folder not found: {dicom_dir}")

    print(f"[SLICER] Importing DICOM from: {dicom_dir}")

    # --- TEMPORARY DICOM DB ---
    with DICOMUtils.TemporaryDICOMDatabase() as db:
        DICOMUtils.importDicom(dicom_dir, db)

        patients = db.patients()
        if not patients:
            raise RuntimeError("No patients found")

        patient_uid = patients[0]
        loaded_ids = DICOMUtils.loadPatientByUID(patient_uid)

    # --- RESOLVE LOADED NODES ---
    volumes = []
    for node_id in loaded_ids:
        node = slicer.mrmlScene.GetNodeByID(node_id)
        if node and node.IsA("vtkMRMLScalarVolumeNode"):
            volumes.append(node)

    if not volumes:
        raise RuntimeError("No volume nodes loaded")

    # --- PICK BEST VOLUME ---
    scored = [(score_name(v.GetName()), v) for v in volumes]
    scored.sort(key=lambda x: x[0], reverse=True)
    best_volume = scored[0][1]

    print(f"[SLICER] Selected volume: {best_volume.GetName()}")

    # --- SHOW IN SLICES ---
    slicer.util.setSliceViewerLayers(background=best_volume)
    slicer.util.resetSliceViews()

    # --- VOLUME RENDERING (GUI-SAFE) ---
    slicer.util.selectModule("VolumeRendering")
    vr_logic = slicer.modules.volumerendering.logic()

    display_node = vr_logic.GetVolumeRenderingDisplayNode(best_volume)
    if not display_node:
        display_node = vr_logic.CreateVolumeRenderingDisplayNode()
        slicer.mrmlScene.AddNode(display_node)
        vr_logic.UpdateDisplayNodeFromVolumeNode(display_node, best_volume)
        best_volume.AddAndObserveDisplayNodeID(display_node.GetID())

    preset = vr_logic.GetPresetByName("CT-Bone")
    if preset:
        display_node.GetVolumePropertyNode().Copy(preset)

    display_node.SetVisibility(True)

    slicer.util.resetThreeDViews()

    print("[SLICER] Volume rendering enabled (single node, GUI synced)")

if __name__ == "__main__":
    main()
