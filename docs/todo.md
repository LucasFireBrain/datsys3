# DATSYS3 – TODO / ROADMAP

This file defines the **next concrete steps** for DATSYS3.
It exists so future chats or contributors can immediately see what remains to be built.

---

## 1. DICOM INGESTION (CORE)

### 1.1 ZIP / ARCHIVE EXTRACTION
- Accept user input:
  - Full path to archive (zip / rar / 7z)
  - OR keyword `auto` / `go`
- Auto-detect:
  - Latest archive in user's **Downloads** folder
- Extract to:
  ```
  clients/<CLIENT_ID>/<PROJECT_ID>/DICOM/
  ```
- Preserve original archive filename (optional subfolder)

Status: ❌ Not implemented

---

## 2. 3D SLICER AUTOMATION

### 2.1 Launch Slicer from DATSYS
- DATSYS calls external Slicer Python script
- Pass project DICOM directory as argument
- Use **persistent DICOM database** (not temporary)

Status: ❌ Not implemented

### 2.2 Load DICOM + Select Volume
After DICOM load:
- Automatically switch to **Volume Rendering** module
- Select best volume using keyword priority:
  - AXIAL
  - BONE
  - CT
  - Contrast 0.5 / 0.6
  - Doctor-specific keywords (future)
- Fallback: first available volume

Status: ❌ Not implemented

### 2.3 View Setup
- Center camera on volume
- Reset focal point
- Enable volume rendering
- Then **give full control to user**

Status: ❌ Not implemented

### 2.4 Extract Patient Metadata
- Read patient name from DICOM metadata
- Update:
  ```
  peek_case.json → nombre_paciente
  ```
- Only if field is empty (never overwrite silently)

Status: ❌ Not implemented

---

## 3. BLENDER INITIALIZATION (PEEK)

### 3.1 Trigger Blender Init from DATSYS
- After user confirms segmentation export is done
- DATSYS calls PEEK Blender init script

Status: ❌ Not implemented

### 3.2 Blender Init Responsibilities
- Open:
  ```
  project-id.blend
  ```
- Import segmentation meshes
- Place them in:
  ```
  Collection: Segmentations
  ```
- Apply naming conventions
- Preserve idempotency (safe to run twice)

Status: ⚠️ Partially implemented in DATSYS2 (to be ported)

---

## 4. DATA & SAFETY RULES (NON-NEGOTIABLE)

- DATSYS never modifies files outside project folder
- No hidden auto-actions
- User always confirms irreversible steps
- JSON is source of truth
- Filesystem structure > in-memory state

---

## 5. REFERENCES

- DATSYS2:
  - DICOM importer
  - Slicer automation
  - Blender segmentation import macros
- These will be provided and ported selectively

---

## NEXT IMMEDIATE TASK
**Implement DICOM ZIP extraction + auto-detect latest download**

