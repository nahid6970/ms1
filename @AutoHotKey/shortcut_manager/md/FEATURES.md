# Feature Specifications

## Visual Shortcut Builder

**Status:** Complete

**Description:** Lets the user build hotkeys visually instead of typing raw AHK prefix syntax.

**Implementation:**

- Supports Ctrl, Alt, Shift, Win
- Supports left/right-specific modifiers
- Supports keyboard rows, navigation cluster, numpad, and generic modifier strip

**Files Involved:**

- `ahk_gui_pyqt.py`

**Usage:**

- Click the keyboard icon next to a hotkey field.
- Select modifiers and a main key.
- Apply the generated hotkey string.

## Script Shortcuts

**Status:** Complete

**Description:** Global hotkeys that run AutoHotkey v2 code.

**Implementation:**

- Stored in `script_shortcuts`
- Supports single-line and multi-line action code
- Multi-line code is wrapped in a block when generated

**Files Involved:**

- `ahk_gui_pyqt.py`
- `ahk_shortcuts.json`

## Context Shortcuts

**Status:** Complete

**Description:** Hotkeys that only activate in matching windows.

**Implementation:**

- Stored in `context_shortcuts`
- Matches by window title, process name, and window class
- Supports comma-separated values for each field
- Generates `#HotIf` functions

**Usage:**

- Add a context shortcut.
- Fill in one or more context fields.
- Generate the script and run it under AutoHotkey v2.

## Exclusion Rules

**Status:** Complete

**Description:** Prevents AHK shortcuts from firing in specific apps/windows.

**Implementation:**

- Stored in `exclusion_rules`
- Generates `IsShortcutExcluded()` function using `WinGetProcessName`, `WinGetTitle`, `WinGetClass`
- `excluded_hotkeys` field (one per line): if filled, only those hotkeys are guarded; if blank, all script/context shortcuts are guarded
- Applied only to script shortcuts and context shortcuts — text and file hotstrings are never excluded
- Each script shortcut gets its own `#HotIf !IsShortcutExcluded()` / `#HotIf` pair only when needed

**Usage:**

- Add an exclusion rule, set process/title/class to match the app.
- Optionally enter specific hotkeys to exclude (e.g. `^r`). Leave blank to exclude all.
- Regenerate the script.

## Text Shortcuts

**Status:** Complete

**Description:** Hotstrings that expand text snippets.

**Implementation:**

- Stored in `text_shortcuts`
- Uses `Paste(...)` helper for literal text insertion
- Handles multiline replacements

## File Shortcuts

**Status:** Complete

**Description:** Hotstrings that paste file paths or drop files.

**Implementation:**

- Stored in `file_shortcuts`
- Uses `PasteFile(...)`

## Background Scripts

**Status:** Complete

**Description:** Auto-executed code that runs when the generated AHK script starts. Supports optional context filtering.

**Implementation:**

- Stored in `startup_scripts`
- Emitted near the top of the generated file
- Optional fields: `context_mode` (`none` / `active` / `inactive`), `window_title`, `process_name`, `window_class`
- When context fields are set, code is wrapped with `#HotIf IsStartup<Name>Context()` (active) or `#HotIf !IsStartup<Name>Context()` (inactive)
- This allows inline hotkey definitions inside a startup script to be suppressed in specific apps

**Usage:**

- Set "Inactive in" + process name to stop a background script's hotkeys from firing in a conflicting app.
- Leave context mode as "No context" for scripts with no hotkeys (timers, hooks, globals).

## Search and Organization

**Status:** Complete

**Description:** Filters shortcuts by name, hotkey, trigger, description, category, and context fields.

**Implementation:**

- Search box filters all shortcut lists
- Category grouping can be toggled on/off
- Category colors are editable

