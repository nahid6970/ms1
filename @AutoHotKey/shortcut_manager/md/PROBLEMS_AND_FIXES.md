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


## 2026-06-10 17:05 - Exclusion rules saved as text shortcuts and causing AHK reload error

**Problem:** Adding an exclusion rule saved it under the Text Shortcut section, and generating the AHK script resulted in an invalid hotstring `:X:::Paste('')` (missing abbreviation error).

**Root Cause:** In `AddEditShortcutDialog.accept_dialog`, the logic for adding a new shortcut did not check for `self.shortcut_type == "exclude"`, causing new exclusion rules to default to the `text_shortcuts` list.

**Solution:** Included the `"exclude"` check to append rules to `self.parent_window.exclusion_rules`. Additionally, added a database self-healing check in `load_shortcuts_json` to automatically detect and migrate misplaced exclusion rules or context shortcuts from `text_shortcuts` to their correct arrays.

**Files Modified:**
- `ahk_gui_pyqt.py`

## 2026-06-10 17:15 - AHK local variable warning in exclusion rules and output path relocation

**Problem:** 
1. AutoHotkey v2 loaded with a warning: `Warning: This local variable appears to never be assigned a value. Specifically: processName`.
2. AHK script was generated in `C:\@delta\output\ahk` instead of the local project directory.

**Root Cause:**
1. `IsShortcutExcluded()` in the generated script evaluated expressions like `processName = "WindowsTerminal.exe"` but never initialized the local variables `processName`, `windowTitle`, or `windowClass`.
2. The generator output path was hardcoded to `C:\@delta\output\ahk`.

**Solution:**
1. Updated `append_exclusion_checker` to dynamically check if the enabled rules require window title, process name, or class and inject `WinGetTitle`, `WinGetProcessName`, or `WinGetClass` statements respectively inside `IsShortcutExcluded()`.
2. Changed generator `output_dir` from the hardcoded folder to `SCRIPT_DIR` so `generated_shortcuts.ahk` is created inside the project directory.

**Files Modified:**
- `ahk_gui_pyqt.py`
- `dev.md`



