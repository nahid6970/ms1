# Problems & Fixes Log

## 2026-06-10 12:00 - Context matching treated comma-separated values as one string

**Problem:** Context shortcut fields like window title, process name, and window class accepted comma-separated text in the GUI, but generation treated the whole field as a single literal string.

**Root Cause:** The generator emitted one `InStr(...)` or equality check per field without splitting comma-separated entries.

**Solution:** Split each field on commas, trim values, and emit `OR` conditions for multiple values.

**Files Modified:**

- `ahk_gui_pyqt.py`

## 2026-06-10 12:00 - Need for app-level shortcut exclusion

**Problem:** Some applications have built-in shortcuts that conflict with AHK hotkeys and hotstrings.

**Root Cause:** The generated script had no global exclusion layer.

**Solution:** Added `exclusion_rules` plus `IsShortcutExcluded()` and wrapped generated shortcut sections with `#HotIf !IsShortcutExcluded()`.

**Files Modified:**

- `ahk_gui_pyqt.py`
- `ahk_shortcuts.json`

