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
