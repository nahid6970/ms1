# Keyboard Shortcuts

## In-App Builder Controls

**Shortcut Builder:**

- Click the keyboard icon next to a hotkey field to open the builder.
- Click modifier buttons to build the prefix.
- Click a main key to set the key.
- Click the same key again to deselect it.

**Relevant Keys:**

- `Ctrl`
- `Alt`
- `Shift`
- `Win`
- Left/right variants for all four modifiers

## App UI Actions

- Add: open the Add menu
- Edit: double-click a shortcut or use the context menu
- Duplicate: right-click a selected shortcut
- Remove: right-click a selected shortcut
- Toggle enabled/disabled: click the status icon next to a shortcut
- Search: type in the search field
- Generate: build the output AHK file

## AutoHotkey Notes

**Common Prefixes:**

- `^` = Ctrl
- `!` = Alt
- `+` = Shift
- `#` = Win

**Common Keys:**

- `{Enter}`
- `{Tab}`
- `{Esc}`
- `{Space}`
- `{Backspace}`

## Context and Exclusion Matching

**Supported match fields:**

- Window title
- Process name
- Window class

**Behavior:**

- Comma-separated values are treated as multiple match options.
- Context shortcuts activate only when their match function returns true.
- Exclusion rules disable shortcuts in matching applications.

