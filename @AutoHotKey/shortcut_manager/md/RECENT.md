# Recent Development Log

All sessions are recorded here. Do not archive old entries.

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



