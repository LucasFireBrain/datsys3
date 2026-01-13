# DATSYS 3

DATSYS is a minimal, deterministic CLI system to manage client-based medical 3D projects (PEEK, PLA, etc.), designed to be **stable first, automatable later**.

This is a clean rewrite from previous iterations, focused on:
- Predictability
- Explicit actions
- File-system truth
- Zero hidden state

---

## Core Principles

- **Clients own projects**
- **Each project lives entirely inside its own folder**
- **No global mutable state**
- **No silent automation**
- **If it’s not visible in the filesystem, it doesn’t exist**

---

## Folder Structure

```
datsys3/
├── datsys.py          # Main CLI + orchestration
├── utils.py           # File, JSON, time utilities
├── clients/           # One folder per client (ignored by git)
│   └── PSO/
│       ├── client_pso.json
│       └── QXXX-PSO-PK1/
│           ├── QXXX-PSO-PK1.json
│           └── (project files)
├── peek/
│   └── peek.py        # PEEK-specific workflow (domain logic)
├── templates/         # Optional project templates
├── data/              # Local runtime data (ignored)
└── docs/
```

---

## Client Model

Each client has:
- A folder: `clients/<CLIENT_ID>/`
- A metadata file: `client_<client_id>.json`

Example:
```json
{
  "id": "PSO",
  "name": "Pablo Solar",
  "contact": "",
  "project_count": 5,
  "created_at": "2025-01-13T10:32:00"
}
```

`project_count` is the **only authoritative counter** for project suffixes.

---

## Project Model

Projects are created inside their client folder:

```
clients/PSO/QXXX-PSO-PK6/
```

Each project has a minimal JSON:
```json
{
  "id": "QXXX-PSO-PK6",
  "client_id": "PSO",
  "type": "PK",
  "created_at": "2025-01-13T11:02:10"
}
```

No project metadata lives outside its folder.

---

## Project ID Format

```
<DATE>-<CLIENT_ID>-<TYPE><N>
```

Example:
```
Q113-PSO-PK6
```

Where:
- `Q` = base36(year % 100)
- `1` = month
- `13` = day
- `PK` = project type
- `6` = client-local project counter

---

## Current Features

- Create clients
- Create projects
- Open existing projects
- Deterministic project IDs
- Client-based project counting

---

## Not Implemented Yet (By Design)

- DICOM import / extraction
- 3D Slicer automation
- Blender initialization
- Reporting / exports

These will be added **after** the core is locked.

---

## Philosophy

DATSYS is not a framework.
It is a **toolbox with rules**.

Automation is layered on top of stability — never the other way around.

If something breaks:
- The filesystem still makes sense
- The data is still readable
- Recovery is manual but possible

That is intentional.

---

## Status

DATSYS 3 is in **active development**, currently stabilizing core workflows before adding medical imaging automation.
