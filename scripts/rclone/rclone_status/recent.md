# Project DNA (Permanent)
Python/Tkinter desktop app for managing rclone tasks with a cyberpunk custom UI, JSON-backed commands, and PowerShell execution. The app is a modular task runner/status dashboard whose main goal is fast manual control over rclone commands with saved presets and per-project actions.

# Latest Implementation
- `Rclone-Status.py`: replaced raw runtime flags with toggle chips for `--dry-run`, `--fast-list`, `-P`, `--track-renames`, and `--size-only`; added editable `--transfers` input and `+` placeholder.
- `Rclone-Status.py`: added configurable `project_spacing` for header gaps and `path_font_size` for left/right path fields in the task runner.
- `Rclone-Status.py`: added Tab-triggered folder/file browser entries for the left/right path fields using a Tk browser dialog, with callback-based selection, filtered list mapping, and restored parent focus after selection.
- `Rclone-Status.py`: removed hover background effects from the arrow switcher and toolbar controls; fixed title-bar close button alignment/styling.
- `Rclone-Status.py`: moved `EXECUTE_CMD` to the bottom-right footer, removed the in-app command preview, and now echoes the full rclone command in the terminal only.
- `Rclone-Status.py`: replaced the focusable log area with a passive status label to avoid the blue clickable block.

# Critical Context
`HoverButton` now supports `hover_bg` and `hover_effect`; use these instead of custom per-button hover hacks. The task runner builds the final rclone command in `run_task()`, prints it through PowerShell, and keeps the UI command area hidden. Project label spacing comes from `app_settings["project_spacing"]`, and path entry font size comes from `app_settings["path_font_size"]`. Tab on the left/right path entries opens `BrowserDialog`; selections must come from the visible filtered list, and the dialog now explicitly restores focus to the parent window and clicked entry.

# Pending Task
None.
