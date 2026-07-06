# Task: Add Debug Script Runner

## Tasks
- [X] Add a new button before `#bookmark-dropdown-btn` in the header for "Run Debug Script".
- [X] Create a modal or popover for the Debug Script Runner where the user can specify a script path/command.
- [X] Add a JS function to run the script. To prevent auto-closing on error, wrap the execution in a shell construct that pauses or catches the error (e.g., `& { <command> } ; if (!$?) { pause }` for PowerShell, or just run it in the active shell pane so it naturally stays open).
- [X] Optionally add useful features like a file picker or predefined script types.
