# Operating Notes

This tool is designed for **zero-friction case execution**. The UI is a single timeline view and the command language is deliberately terse. If something can be done in one line, it should be done in one line.

## Mental model

- **Timeline is the only screen.** No navigation or nested menus.
- **Commands are comma-separated.** That is the API.
- **Case IDs are stable.** Use the numeric index from the timeline or the full `CaseID`.

## Fast path workflow

1. `new` → create the case.
2. `#, edit` → fill or adjust `peekCase.json`.
3. `#, dicom` → ingest DICOMs from Downloads or a path.
4. `#, slicer` → open in 3D Slicer.
5. `#, blender` → launch Blender and auto-import segmentations.
6. `#, stage, <state>` → keep status current.
7. `#, log, <note>` → append any key note.

## Command contract

- **Selector**: first token (`#` or full ID).
- **Action**: second token.
- **Args**: any remaining tokens, concatenated when necessary.

Example:

```
2, stage, Ready for print, waiting on approval
```

The log message becomes `"Ready for print | waiting on approval"` inside `Log.txt`.

## File expectations

- `peekCase.json` is the single source of truth for case metadata.
- `Log.txt` is the append-only timeline of events.
- `DICOM/` is disposable and can be replaced on demand.

## Keep it lean

If a workflow step slows you down, it should be simplified or removed. The whole point is to keep the timeline tight and the operator unblocked.
