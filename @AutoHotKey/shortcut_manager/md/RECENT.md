# Recent Development Log

All sessions are recorded here. Do not archive old entries.

## 2026-06-26 19:30 - Launcher Shortcut Type & Terminal Hide Toggle

**What We Accomplished:**

- Introduced a new "Launcher Shortcut" type which allows users to directly map hotkeys to python scripts, shell scripts, applications, and files without writing raw AutoHotkey code.
- Added support for specifying target paths (with browse buttons) and arguments.
- Added a "Hide Terminal Window" checkbox/toggle for the Launcher Shortcut dialog.
- Configured dynamic AHK code generation for Launcher Shortcuts:
  - If the path is a Python file (`.py`, `.pyw`), it prepends `pythonw.exe` (hidden) or `python.exe` (visible) and correctly handles command-line arguments.
  - If the path is a PowerShell file (`.ps1`), it prepends `powershell.exe -WindowStyle Hidden` (hidden) or `powershell.exe -NoExit` (visible).
  - For other files/applications, it runs them directly, applying the `"Hide"` window option if requested.
- Integrated the new type into the GUI main list, add menu, database JSON serialization/deserialization, search, category color/grouping support, and duplication/removal operations.
- Fixed an UnboundLocalError during dialog confirmation validation in `accept_dialog` by separating the dictionary creation logic for the File and Launcher shortcut types.

**Files Modified:**

- `ahk_gui_pyqt.py`
- `md/RECENT.md`
- `md/FEATURES.md`

## 2026-06-13 20:19 - match_foreground toggle for context shortcuts

**What We Accomplished:**

- Added "Match any foreground window (not just focused)" checkbox to the context shortcut edit dialog, shown below the Enabled toggle.
- New field `match_foreground` (bool, default `false`) stored in `context_shortcuts` JSON entries.
- When disabled (default): behaviour unchanged — `#HotIf` guard checks active window `"A"`.
- When enabled: no `#HotIf` guard is emitted. Instead a finder function `Is<Name>Context()` loops `WinGetList()` and returns the first matching `hwnd` (or `0`). The hotkey body calls the finder, runs `WinActivate(hwnd)` + `Sleep(100)`, then executes the action. Outer `{…}` braces are stripped from the action before inlining so no double-block is generated.

**Files Modified:**

- `ahk_gui_pyqt.py`

## 2026-06-10 12:00 - Documentation bootstrap

**What We Accomplished:**

- Created project-specific documentation structure for easier AI handoff.
- Added `dev.md` with project architecture, run instructions, and generation flow.
- Added `md/RECENT.md`, `md/FEATURES.md`, `md/PROBLEMS_AND_FIXES.md`, `md/UI_UX.md`, and `md/KEYBOARD_SHORTCUTS.md`.

**Files Modified:**

- `dev.md`
- `md/RECENT.md`
- `md/FEATURES.md`
- `md/PROBLEMS_AND_FIXES.md`
- `md/UI_UX.md`
- `md/KEYBOARD_SHORTCUTS.md`

**Known Issues:**

- Shortcut builder special-key sizing has had layout quirks during selection state changes.
- Documentation currently reflects the codebase as of this session; future feature additions should update the docs.

**Next Session:**

- Keep `dev.md` and `md/FEATURES.md` in sync with any new shortcut types or generator changes.

## 2026-06-10 17:10 - Exclusion rule list assignment bugfix

**What We Accomplished:**

- Fixed bug where newly added exclusion rules defaulted to the text shortcuts list.
- Implemented robust database migration logic to move misplaced exclusion rules and context shortcuts from `text_shortcuts` back to their correct sections in the JSON database on startup.
- Documented the bug details and resolution steps in `md/PROBLEMS_AND_FIXES.md`.

**Files Modified:**

- `ahk_gui_pyqt.py`
- `md/PROBLEMS_AND_FIXES.md`
- `md/RECENT.md`

## 2026-06-10 18:48 - Per-field enable/disable toggles for context fields

**What We Accomplished:**

- Replaced single "Enable context filter" checkbox with per-field checkboxes for Window Title, Process Name, and Window Class in Context Shortcuts, Exclusion Rules, and Background Scripts dialogs.
- Each field's checkbox is its label — unchecking grays out the field and the generator ignores that field's value entirely.
- Data model uses `window_title_enabled`, `process_name_enabled`, `window_class_enabled` booleans (default `true`).
- Generator masks disabled fields to empty string before passing to `build_condition_clause` / `append_context_checker` / startup context logic.
- Removed now-redundant `context_filter_enabled` single-toggle field from all code paths.

**Files Modified:**

- `ahk_gui_pyqt.py`

## 2026-06-10 18:16 - Background scripts: context mode (active in / inactive in)

**What We Accomplished:**

- Added `context_mode`, `window_title`, `process_name`, `window_class` fields to background scripts.
- Dialog left panel now shows these fields for startup type with a mode combobox: "No context / Active in / Inactive in".
- Generator wraps startup script code with `#HotIf IsStartup<Name>Context()` (active) or `#HotIf !IsStartup<Name>Context()` (inactive) when fields are filled. Uses same `append_context_checker` as context shortcuts.
- Function name is sanitized with `re.sub(r'[^a-zA-Z0-9]', '', name)` to avoid invalid AHK identifiers.
- Display shows `🚀 ✅[proc]` or `🚀 🚫[proc]` in the list when context mode is set.
- Patched Macro Recorder JSON directly: `context_mode: inactive`, `process_name: chrome.exe` so ^r and ^e don't fire in Chrome.

**Files Modified:**

- `ahk_gui_pyqt.py`
- `ahk_shortcuts.json`

## 2026-06-10 17:49 - Per-hotkey exclusion: excluded_hotkeys field added to exclusion rules

**What We Accomplished:**

- Added `excluded_hotkeys` field to exclusion rules (one hotkey per line, e.g. `^r`, `^s`). Leave blank to exclude ALL shortcuts in matching app.
- Updated exclusion rule dialog: right panel now shows a text area for entering excluded hotkeys instead of a static info label.
- Rewrote script shortcuts generator: each shortcut only gets `#HotIf !IsShortcutExcluded()` guard if it matches an exclusion rule's hotkey list (or if any rule has blank hotkeys = exclude all).
- Updated context shortcuts generator same way: `#HotIf` drops `&& !IsShortcutExcluded()` unless the hotkey needs it.
- Updated exclusion rule display to show `🚫 [process | hotkeys]` in the list.
- Fixed existing Chrome exclusion rule JSON: cleared `window_title` ("vlr"), added `excluded_hotkeys: ""` so all shortcuts are excluded in Chrome.

**Files Modified:**

- `ahk_gui_pyqt.py`
- `ahk_shortcuts.json`

## 2026-06-10 17:42 - Exclusion rule fixes: text shortcuts unwrapped + JSON data corrected

**What We Accomplished:**

- Removed `#HotIf !IsShortcutExcluded()` wrapper from text shortcuts and file shortcuts sections — exclusion only applies to script shortcuts and context shortcuts, not text/file hotstrings.
- Fixed exclusion rule JSON data: cleared `window_title` ("vlr") from the Chrome rule so the rule now excludes Chrome based on process name alone, regardless of active tab title.

**Files Modified:**

- `ahk_gui_pyqt.py`
- `ahk_shortcuts.json`

**Next Session:**

- Re-run the GUI, click Generate AHK, then test that AHK shortcuts are suppressed in Chrome but text hotstrings still fire.

## 2026-06-10 17:20 - Exclusion rules variable warning fix & path relocation

**What We Accomplished:**

- Fixed AHK v2 variable warnings by dynamically initializing `processName`, `windowTitle`, and `windowClass` in `IsShortcutExcluded()` based on active exclusion filters.
- Relocated generated AHK output path from the hardcoded folder to the local workspace folder.
- Updated documentation `dev.md` to reflect the new location of `generated_shortcuts.ahk`.

**Files Modified:**

- `ahk_gui_pyqt.py`
- `dev.md`
- `md/PROBLEMS_AND_FIXES.md`
- `md/RECENT.md`



