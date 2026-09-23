# Project DNA
A Flask/Socket.IO-based terminal TUI using Xterm.js for multi-pane workspace management. It utilizes a unified `tui_config.json` for persistent configuration and user-defined custom button shortcuts.

# Latest Implementation
* **app.py** (`system_template` PowerShell profile):
    * Added `$env:TERM`, `$env:COLORTERM`, and `$env:TERM_PROGRAM` declarations to the top of every project's auto-generated `profile.ps1`.
    * Fixes Codex (and other TUI apps like `fzf`, `bat`) falling back to muted/flat color rendering in the embedded terminal.
    * Root cause: winpty PTY inherited no color capability env vars, so Codex detected a low-color terminal and never emitted truecolor escape sequences.
    * xterm.js frontend was not the issue — it renders truecolor correctly once the PTY env is set properly.

# Critical Context
* Custom buttons and their order are persisted globally in `tui_config.json`.
* `refreshAllPaneCustomButtons()` handles the DOM logic by clearing existing buttons and re-restoring them, ensuring style/order updates are applied without full page reloads.
* Terminal env vars (`TERM=xterm-256color`, `COLORTERM=truecolor`) are now injected via the PowerShell profile template, not the PTY constructor — this is intentional since winpty's `PTY` class doesn't accept a custom env parameter.

# Pending Task
None — Codex resume terminal color issue resolved and verified.
