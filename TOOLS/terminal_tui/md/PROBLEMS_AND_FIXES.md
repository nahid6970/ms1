# Problems & Fixes Log

---

## [2026-07-06 15:24] - PowerShell Command Parsing Error with `$?`
**Problem:** Running debug scripts via PowerShell wrapper `& { script } ; if (-not $?) { ... }` failed with parser errors:
```
Missing expression after unary operator '-not'.
Unexpected token 'True' in expression or statement.
```
**Root Cause:** The outer shell was interpreting `$?` and other PowerShell syntax before the inner command could process it, causing token parsing failures.
**Solution:** Switched to PowerShell `-EncodedCommand` with Base64 encoding. The script is converted to UTF-16LE bytes, Base64-encoded, and passed as `-EncodedCommand` so no shell interpolation occurs.
**Files Modified:** `templates/index.html` — `handleRunDebugScript()` / `executeExplorerRun()`

---

## [2026-07-06 15:40] - File Delete Shows "Error deleting file" Despite Success
**Problem:** After successfully deleting a file, the UI displayed an alert saying "Error deleting file."
**Root Cause:** The success handler called `refreshFileTree()` which **did not exist** as a function. This threw a `ReferenceError`, which was caught by the surrounding `try/catch` block and displayed the error alert.
**Solution:** Replaced `refreshFileTree()` with `loadExplorerRoot()` — the actual function that reloads the file explorer tree.
**Files Modified:** `templates/index.html` — `deleteExplorerFile()`

---

## [2026-07-06 15:28] - Debug Script Runner Interfering with Agent CLIs
**Problem:** Running a debug script executed it in the current terminal pane, which disrupted any running agent CLI session.
**Root Cause:** The original implementation wrote the command directly to the active terminal pane.
**Solution:** Changed to open a new tab via `splitTerminal('tabs', cmd + '\r')` so the debug script runs in an isolated pane.
**Files Modified:** `templates/index.html` — `handleRunDebugScript()` → `executeExplorerRun()`

---

## [2026-07-06 ~15:25] - Autocomplete Dropdown Showing `python script.py` Instead of `script.py`
**Problem:** The debug script autocomplete dropdown was displaying command-prefixed strings (e.g., `python myscript.py`) instead of just the filename.
**Root Cause:** The dropdown options were being formatted with the runner prefix before being displayed.
**Solution:** Changed to show raw filenames only (e.g., `myscript.py`, `.\\test.ps1`). The runner prefix is added only at execution time based on the selected mode.
**Files Modified:** `templates/index.html` — `filterDebugScripts()` / `openDebugScriptModal()`

---

## [2026-07-08 21:00] - Mobile Layout Disappears / Covered by Black UI Overlay
**Problem:** On mobile browsers (Safari/Chrome), the top header and bottom status bar completely disappeared or were covered by a black/blurry layer after recent commits.
**Root Cause:** Hidden modal overlays (`.modal-overlay`) with high z-index (like `ai-model-tester-modal` and `ai-system-prompt-modal` at `z-index: 3000`) had `display: flex` and were only hidden via `opacity: 0; pointer-events: none;`. A rendering/compositing bug on mobile GPUs causes the `backdrop-filter: blur(8px)` and/or the background overlay to still render and composite on top of all other page elements, blocking the entire screen.
**Solution:** Added `visibility: hidden;` to `.modal-overlay` and transitioned it in CSS (`transition: opacity 0.25s ease, visibility 0.25s ease;`), toggling it to `visibility: visible;` in `.modal-overlay.show`. This completely excludes the hidden overlays from the render tree, resolving the GPU compositing bug.
**Files Modified:** `templates/index.html` — `.modal-overlay` / `.modal-overlay.show` styles

---

## [2026-07-08 21:05] - Upload Button Only Allows Selecting One Image at a Time
**Problem:** The screenshot/image upload button (`#screenshot-upload-btn`) only allowed selecting and uploading a single image at a time.
**Root Cause:** The underlying `<input type="file" id="screenshot-file-input">` element lacked the `multiple` HTML attribute, and the `handleScreenshotFileSelect(event)` javascript handler only processed `event.target.files[0]`.
**Solution:** Added the `multiple` attribute to the input file element, and updated `handleScreenshotFileSelect` to map files to concurrent upload promises, await them with `Promise.all`, and write the resulting space-separated, quoted paths to the active terminal input.
**Files Modified:** `templates/index.html` — screenshot-file-input element & handleScreenshotFileSelect JS function

