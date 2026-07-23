# Recent Handoff

## 1. Project DNA (Permanent)
PyQt6 status bar desktop application (`mypygui_qt.py`) built for system automation, quick script monitoring, and launcher controls with dynamic theme configurations.

## 2. Latest Implementation
- `mypygui_qt.py`:
  - Added `QPlainTextEdit` and `QTextEdit` border styling to `DIALOG_QSS` so the SVG custom code box renders with a clean visible border and focus highlight.
  - Implemented Script Monitor (`RunningScriptScannerDialog`, `ScriptMonitorListDialog`, `ScriptMonitorSettingsDialog`).
  - Added customizable SVG icon and 3 status color pickers (`Running`, `Stopped 1`, `Stopped 2`) with visual swatch preview buttons.
  - Implemented 25 FPS smooth sine-wave breathing pulse color morphing animation for stopped script alerts.

## 3. Critical Context
- `ScriptMonitorListDialog` uses dynamic font metric width calculation and `QHeaderView.ResizeMode.Stretch` on column 1 so long script paths are fully visible without truncation.
- `_update_script_monitor_color()` invokes `repaint()` on `_script_monitor_btn` to guarantee immediate UI render during color pulses and config changes.
- Configuration is saved to `mypygui_config.json`.

## 4. Pending Task
Monitor runtime behavior and user feedback for additional script runner defaults or layout preferences.
