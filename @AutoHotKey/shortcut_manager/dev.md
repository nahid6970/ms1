# AutoHotkey Shortcut Manager

Project-specific development guide for `ahk_gui_pyqt.py`.

## Purpose

This app is a PyQt6 GUI for managing AutoHotkey v2 shortcuts and generating a runnable script at:

`C:\@delta\ms1\@AutoHotKey\shortcut_manager\generated_shortcuts.ahk`

It supports:

- Script shortcuts
- Context shortcuts
- Exclusion rules
- Text shortcuts
- File shortcuts
- Background scripts
- A visual shortcut builder for hotkeys

## Main Files

- `ahk_gui_pyqt.py`: the entire GUI, JSON persistence, and AHK generation logic
- `ahk_shortcuts.json`: saved shortcut data and app settings
- `README.md`: long-form project reference and examples
- `dev.md`: this document
- `md/AI_CONTEXT.md`: stable short project brief for AI handoff
- `md/RECENT.md`: session history
- `md/FEATURES.md`: feature inventory
- `md/PROBLEMS_AND_FIXES.md`: bug history and solutions
- `md/UI_UX.md`: UI behavior and styling rules
- `md/KEYBOARD_SHORTCUTS.md`: builder and app shortcut notes

## Run

```bash
python ahk_gui_pyqt.py
```

Requirements:

- Python 3.10+
- PyQt6
- AutoHotkey v2 for running generated output

## Data Model

Shortcut data is stored in `ahk_shortcuts.json` as arrays:

- `script_shortcuts`
- `context_shortcuts`
- `exclusion_rules`
- `text_shortcuts`
- `file_shortcuts`
- `startup_scripts`

App settings stored in the same JSON:

- `app_font_family`
- `app_font_size`

## Generation Flow

`generate_ahk_script()` writes helper functions first, then emits shortcuts in this order:

1. Startup scripts
2. Exclusion guard function
3. Script shortcuts
4. Context shortcuts
5. Text shortcuts
6. File shortcuts

Important behavior:

- Context shortcuts generate `#HotIf` guards based on window title, process name, and window class.
- Exclusion rules generate `IsShortcutExcluded()` and are applied globally so matching apps do not trigger shortcuts.
- Comma-separated values are treated as multiple matches.
- Multi-line script actions are wrapped into block syntax.
- Text/file shortcuts use helper paste functions in the generated AHK script.
- Text shortcuts can be configured as selection menus. When enabled, multi-line replacements compile into interactive hierarchical menus (using leading dashes for submenus up to 5 levels) with bracketed modular action tags (such as `[name:]`, `[text:]`, and `[folder:]`).

## Development Conventions

- Use `apply_patch` for edits.
- Keep file paths absolute when referring to repo files in notes.
- Prefer small, targeted changes to `ahk_gui_pyqt.py`.
- If adding a new shortcut type, update:
  - add dialog
  - selection handling
  - duplicate/remove logic
  - JSON save/load
  - display rendering
  - generator output

## Documentation Workflow

Read these when relevant:

- `md/AI_CONTEXT.md` for a short stable project summary
- `md/RECENT.md` for the last few sessions
- `md/PROBLEMS_AND_FIXES.md` when a bug reappears
- `md/FEATURES.md` when changing shortcut types
- `md/UI_UX.md` when touching layout or styling
- `md/KEYBOARD_SHORTCUTS.md` when changing builder behavior

## Known Sensitive Areas

- The shortcut builder uses fixed sizing and style sheets that can affect layout quickly.
- Context/exclusion matching logic is string-based and should be kept explicit.
- The GUI persists state in a single JSON file, so schema changes should include backward compatibility.
- Generated AHK syntax must stay valid for AutoHotkey v2.

## Practical AI Handoff Notes

When resuming work, the most useful sequence is:

1. Read `dev.md`
2. Read `md/AI_CONTEXT.md`
3. Read the last 1-5 entries in `md/RECENT.md`
4. Check `md/PROBLEMS_AND_FIXES.md` for related regressions
5. Inspect `ahk_gui_pyqt.py`
