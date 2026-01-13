# DATSYS3 – TODO / ROADMAP

## Core Structure

- [x] Project-based filesystem (clients / cases)
- [x] Deterministic case IDs
- [x] PEEK case metadata (peekCase.json)

## Templates

- [x] Define PEEK project template folder
- [ ] Copy PEEK template on PK project creation
- [ ] DICOM ingestion assumes template exists
- [ ] No script should create project subfolders ad-hoc

## DICOM

- [x] Ingest DICOM archives (zip / 7z / rar)
- [x] Extract patient name via pydicom
- [ ] Open project DICOM automatically in 3D Slicer
- [ ] Auto-select best CT volume
- [ ] Auto-enable volume rendering

## Blender

- [ ] Blender initialization script
- [ ] Import Slicer segmentations automatically
- [ ] Rename segmentation objects by keyword rules
- [ ] Save initialized .blend in project Blender folder
