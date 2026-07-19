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

## Launcher Shortcuts

**Status:** Complete

**Description:** Hotkeys that run any script, app, or file directly without writing raw AutoHotkey code. Supports toggling the terminal window visibility.

**Implementation:**

- Stored in `launcher_shortcuts`
- Target path input with file browse dialog
- Supports optional command line arguments
- "Hide Terminal Window" toggle (boolean, `hide_terminal`)
- Generates `Run()` statements:
  - `.py`/`.pyw` files execute via `pythonw.exe` (hidden) or `python.exe` (shown)
  - `.ps1` files execute via `powershell.exe -WindowStyle Hidden` (hidden) or `powershell.exe -NoExit` (shown)
  - Other executables/files run directly, using `"Hide"` window option if hidden

**Usage:**

- Select Launcher Shortcut from the ADD menu.
- Browse to the target script or application.
- Toggle terminal window hide/show using the checkbox.
- Set a hotkey and category.
- Generate and run the AHK script.

## Context Shortcuts

**Status:** Complete

**Description:** Hotkeys that only activate in matching windows, with an optional mode to find and focus any open matching window.

**Implementation:**

- Stored in `context_shortcuts`
- Matches by window title, process name, and window class
- Supports comma-separated values for each field
- `match_foreground` (bool, default `false`):
  - `false`: generates `#HotIf Is<Name>Context()` guard that checks the active window `"A"` — shortcut only fires when the matching window is already focused.
  - `true`: emits a global hotkey (no `#HotIf`). The generated `Is<Name>Context()` function iterates `WinGetList()` and returns the first matching `hwnd`. The hotkey body activates that window (`WinActivate(hwnd)` + `Sleep(100)`) then runs the action.

**Usage:**

- Add a context shortcut and fill in one or more context fields.
- Enable "Match any foreground window" to have the shortcut find and focus the window even if it is not currently active.
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

**Description:** Hotstrings or hotkeys that expand text snippets or display an interactive selection menu/submenu structure.

**Implementation:**

- Stored in `text_shortcuts`
- Automatically detects if the trigger is a hotkey (e.g., starts with modifier chars like `^`, `!`, `+`, `#` or contains ` & `) or a hotstring, compiling as a hotkey (`trigger::`) or hotstring (`:X:trigger::`) dynamically.
- When "Show multi-line text as a selection menu" is checked, parses the replacement text to generate interactive hierarchically nested menus (up to 5 levels) in AutoHotkey v2 using leading-dash syntax.
- Renders using a custom, high-performance GUI wrapper (`CustomMenu`/`CustomMenuGUI`) supporting full typography customization (font size and font family adjustable via the editor's Settings dialog).
- Supports fully fluid mouse hover highlighting, smooth keyboard arrow-key navigation (Esc to close, Left Arrow to go Back, Right/Enter to select), and automatic auto-close on lost focus.
- Supports modular option tags enclosed in brackets: `[name:Display Label]`, `[text:Text to paste]`, and `[folder:Folder path to open in Explorer]`. Extensible for future action tags.
- Uses standard AutoHotkey `Paste(...)` (or other selected delivery modes) for text insertion, and `OpenFolderInTab(...)` for opening folders (opening in a new tab if an existing Explorer window is present).

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

