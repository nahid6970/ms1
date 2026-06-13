# Ctrl+Alt Visual Mode Issue Handoff

## Summary

`Alt+Up` / `Alt+Down` in Visual Mode are working and persisting.

The remaining issue is `Ctrl+Alt+Up` / `Ctrl+Alt+Down` in Visual Mode:
- the shortcut appears to do something in the editor
- but after refresh, the changes reset
- the user wants the visual-mode version to persist the same way `Alt+Up/Down` does

## What Was Tried

### Frontend
- Added contentEditable-aware multi-line cursor handling in `static/script.js`.
- Generalized the multi-cursor code to accept either textarea or visual preview targets.
- Made the visual-mode multi-cursor save path call `saveData()` immediately.
- Switched the save path to `navigator.sendBeacon()` for refresh safety.

### Backend
- Updated `app.py` so `POST /api/data` accepts both normal JSON bodies and raw beacon payloads.

## Current State

- `Alt+Up/Down` persists correctly.
- `Ctrl+Alt+Up/Down` still resets after refresh.
- The issue is now likely in the visual-mode Ctrl+Alt cursor/edit flow itself, not the backend JSON parser.

## Files Touched During Debugging

- `static/script.js`
- `app.py`

## Relevant Areas In `static/script.js`

- `handleKeyboardShortcuts()`
- `addCursorBelow()`
- `addCursorAbove()`
- `setupMultiLineCursorListener()`
- `syncMultiCursorValue()`
- `showCursorMarkers()`
- `handleMultiLineCursorMove()`
- `extractRawText()`
- `extractRawTextBeforeCaret()`
- `setCaretPosition()`

## Hypothesis To Test Next

1. The visual preview may be updating, but the exact raw text being saved may not match what the user sees.
2. The contentEditable multi-cursor path may need to mirror the raw textarea path more closely.
3. The save call may be happening, but the preview/re-render path may later overwrite the saved value before refresh.

## Repro

1. Open a cell in Visual Mode.
2. Use `Ctrl+Alt+Up` or `Ctrl+Alt+Down`.
3. Refresh the page.
4. The changes disappear.

## Notes

- Do not change the markdown docs for this handoff unless the fix is confirmed.
- The goal is to get a clean reproduction and fix with another AI model.
