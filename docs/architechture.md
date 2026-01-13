# DATSYS 3 — System Contract & Responsibilities

This document defines the **final, locked responsibilities** of each script in DATSYS 3.

If code violates this document, the code is wrong — not the document.

No implicit behavior.
No hidden coupling.
Filesystem is the source of truth.

---

## Core Principles

- The filesystem **is** the database
- Each project belongs to **exactly one client**
- No global mutable state
- No script edits files it does not own
- Terminal and Blender are the only interfaces
- Everything explicit, nothing automatic

---

## Final File Responsibilities

### `datsys.py`
**Role:** CLI entrypoint & menu conductor

Responsibilities:
- Display all menus
- Collect user intent
- Route actions to other scripts

Non-responsibilities:
- Does NOT edit JSON
- Does NOT create folders
- Does NOT contain business logic

Think of this as the **conductor**, not the musician.

---

### `clients.py`
**Role:** Client identity & metadata

Responsibilities:
- Manage `clients/<CLIENT_ID>/client.json`
- Store:
  - Client name
  - Contact info
  - `project_count` (global counter per client)
- Answer:
  - Does this client exist?
  - What is the next project number?

Non-responsibilities:
- Does NOT know about projects’ contents
- Does NOT know about PEEK

---

### `projects.py`
**Role:** Project creation & discovery

Responsibilities:
- Create project folders under a client
- Suggest project IDs
- List existing projects

Rules:
- One folder = one project
- Project suffix comes from `client.project_count`

Non-responsibilities:
- Does NOT edit client metadata directly
- Does NOT know about PEEK internals
- Does NOT write `peekCase.json`

---

### `peek.py`
**Role:** PEEK domain logic (terminal-side)

Responsibilities:
- Create and update `peekCase.json`
- Prompt user for PEEK fields
- Allow skipping fields
- Parse hospital list from `hospitals.csv`

Rules:
- User can press ENTER to skip
- User can type `0` to skip all remaining fields

Non-responsibilities:
- Does NOT create projects
- Does NOT touch Blender
- Does NOT manage clients

This is the **only terminal writer** of `peekCase.json`.

---

### `peek_blender_macros/`
**Role:** Blender-side PEEK tools

Responsibilities:
- Read and edit `peekCase.json`
- Provide UI in Blender (N-panel)
- Generate images and assets into project folder

Rules:
- Must respect existing JSON structure
- Must never create or delete projects

This is the **only non-terminal writer** of `peekCase.json`.

---

### `utils.py`
**Role:** Dumb helpers

Responsibilities:
- Base36 conversions
- Date parsing
- Input helpers
- Path helpers

Rules:
- No domain logic
- No file ownership
- Pure functions only

---

### `hospitals.csv`
**Role:** Static reference data

Responsibilities:
- Hospital ID → Hospital name mapping

Rules:
- Read-only
- Parsed by `peek.py`
- Never modified by code

---

## Hard Guarantees (Non-Negotiable)

1. DATSYS never edits files outside a project folder
2. No script writes a file it does not own
3. No hidden auto-actions
4. No cross-domain knowledge leakage
5. Blender and terminal are equals — neither is subordinate
6. Project folders are immutable identity
7. If unsure, do nothing and ask

---

## Lifecycle Summary

1. `datsys.py` gathers intent
2. `clients.py` resolves client
3. `projects.py` creates project
4. `peek.py` initializes PEEK metadata
5. Blender macros refine and enrich data
6. Exports read frozen data only

---

## Final Note

This system is designed for:
- One primary operator
- Maximum clarity
- Zero magic
- Long-term maintainability

Complexity is rejected by default.
