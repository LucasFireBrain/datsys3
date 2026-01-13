# DATSYS – Philosophy

## What DATSYS Is

DATSYS is a **personal, local, single-operator system** designed to support a very specific real-world workflow:
medical 3D cases (primarily PEEK) handled by one person.

It is a **craft tool**, not a product.
More like a workbench than a platform.

Its purpose is to:
- Reduce cognitive load
- Make work predictable
- Preserve context across long, interrupted workflows
- Act as a reliable assistant, not an autonomous agent

## What DATSYS Is NOT

DATSYS is **not**:
- A scalable system
- A multi-user system
- A cloud service
- An enterprise platform
- An API-first architecture
- A product meant to grow indefinitely

If DATSYS ever needs to scale, **it should be replaced, not extended**.

## Design Priorities (In Order)

1. **Clarity over abstraction**
2. **Explicit steps over hidden automation**
3. **Local files over services**
4. **Determinism over flexibility**
5. **Human-readable state over clever logic**

Folders, filenames, and JSON files are preferred over databases or complex schemas.

## Operator-Centered Design

The system is optimized for:
- A tired operator
- Interrupted work sessions
- Parallel cases
- High responsibility, low tolerance for mistakes

Anything that increases mental overhead is considered a bug.

## Local-First, Source-of-Truth

- The filesystem is the source of truth
- Each project folder is self-contained
- No global state is required to understand a project
- Logs and JSON files exist to support human understanding first

## Automation Philosophy

Automation is allowed **only when**:
- It is predictable
- It is reversible
- It is transparent

No hidden background actions.
No AI agents making decisions.
The system assists; the human decides.

## Relationship With Tools

DATSYS orchestrates tools, it does not replace them:
- 3D Slicer is responsible for medical imaging
- Blender is responsible for geometry and visualization
- DATSYS is responsible for structure, flow, and memory

Each tool does one job well.

## Guiding Principle

> If the system becomes harder to understand than the work it supports, it has failed.

This document exists to prevent that failure.
