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

**Description:** Global app/window exclusions that prevent shortcuts from firing in conflicting applications.

**Implementation:**

- Stored in `exclusion_rules`
- Generates `IsShortcutExcluded()`
- Applied to script, context, text, and file shortcuts

**Usage:**

- Add an exclusion rule for an app with built-in shortcuts.
- Match by title, process, or class.
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

**Description:** Auto-executed code that runs when the generated AHK script starts.

**Implementation:**

- Stored in `startup_scripts`
- Emitted near the top of the generated file

## Search and Organization

**Status:** Complete

**Description:** Filters shortcuts by name, hotkey, trigger, description, category, and context fields.

**Implementation:**

- Search box filters all shortcut lists
- Category grouping can be toggled on/off
- Category colors are editable

