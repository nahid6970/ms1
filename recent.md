# Recent Handoff

## 1. Project DNA (Permanent)
PyQt6 status bar desktop application (`mypygui_qt.py`) built for system automation, quick script monitoring, and launcher controls with dynamic theme configurations.

## 2. Latest Implementation
- `mypygui_qt.py`:
  - Implemented Script Monitor feature (`RunningScriptScannerDialog`, `ScriptMonitorListDialog`, `ScriptMonitorSettingsDialog`).
  - Added left-click runner control panel (`python`, `pythonw`, `pwsh`, `cmd`) with batch launch for stopped scripts.
  - Added auto-window dynamic geometry calculation for long script paths.
  - Added customizable SVG icon and 3 status color pickers (`Running`, `Stopped 1`, `Stopped 2`) with visual swatch preview buttons.
  - Implemented 25 FPS smooth sine-wave breathing pulse color morphing animation for stopped script alerts.
  - Custom QSS `QSpinBox` styling with CSS triangle arrows (`▲`/`▼`).

## 3. Critical Context
- `ScriptMonitorListDialog` uses dynamic font metric width calculation and `QHeaderView.ResizeMode.Stretch` on column 1 so long script paths are fully visible without truncation.
- `_update_script_monitor_color()` invokes `repaint()` on `_script_monitor_btn` to guarantee immediate UI render during color pulses and config changes.
- Configuration is saved to `mypygui_config.json`.

## 4. Pending Task
Monitor runtime behavior and user feedback for additional script runner defaults or layout preferences.
