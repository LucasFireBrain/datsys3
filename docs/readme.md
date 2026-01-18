# Datsys3

A single-operator workflow tool for tracking medical device cases (PEEK/PLA/archive) and launching the exact tools needed to execute a case. The core interface is a timeline screen with a terse, comma-separated command language so you can move fast without nested menus or extra UI layers.

## Philosophy

- **Less friction > handholding.**
- **No nested menus.** Everything happens from the main timeline screen.
- **Single operator.** Optimize for speed, not onboarding.
- **Focus on sculpting, not bureaucracy.** No forced directory wrangling or manual logging.

## What it does

- Creates clients and projects with stable IDs.
- Tracks case metadata (`peekCase.json`) and status updates.
- Maintains a flat, always-visible timeline view.
- Launches DICOM ingestion, 3D Slicer, and Blender with project context.
- Appends logs and updates stages automatically.

## Quick start

> This repository is currently tailored for Windows paths and tools (Blender/Slicer). If you run on another OS, update the executable paths in the launchers.

1. **Install Python 3.10+** (recommended).
2. **Install dependencies** (minimal):
   - `pydicom`
   - `py7zr`
   - `rarfile`
3. **Run the timeline shell**:

```bash
python timeline.py
```

You’ll land directly in the timeline view and can drive everything from there.

## Timeline commands

All commands are **comma-separated** in the main timeline screen. The first token selects the case (either the `#` shown in the timeline or the full `CaseID`).

```
<case>, stage, <value>, <optional message>
<case>, log, <message>
<case>, open
<case>, logopen
<case>, edit
<case>, dicom
<case>, slicer
<case>, blender
```

Other commands:

```
new
help
quit
```

Examples:

```
1, stage, Design, imported mesh set
3, log, waiting on surgeon feedback
AR-ABCDE-PL1, dicom
```

## Data layout

```
clients/
  <CLIENT_ID>/
    client_<CLIENT_ID>.json
    <PROJECT_ID>/
      <PROJECT_ID>.json
      peekCase.json
      Log.txt
      DICOM/
      Blender/
      3DSlicer/
```

`PROJECT_ID` format: `<base36-date>-<CLIENT_ID>-<type><counter>`

## Key scripts

- `timeline.py` — timeline UI and command router.
- `datsys.py` — project creation and action wrappers.
- `peek.py` — case metadata editor for PEEK projects.
- `dicom_ingestion.py` — ingest DICOM from downloads or a path.
- `blender_launcher.py` — open Blender and apply initialization.
- `slicer_launcher.py` — open 3D Slicer with the case DICOM.

## Configuration touchpoints

- **Blender**: `blender_launcher.py` → `BLENDER_EXE`
- **Slicer**: `slicer_launcher.py` → `SLICER_EXE` and `SLICER_SCRIPT`
- **Templates**: `templates/PK` for PEEK project initialization

## Project scope

This is a single-operator tool. Expect the workflow to be opinionated, direct, and optimized for speed rather than onboarding or guardrails.
