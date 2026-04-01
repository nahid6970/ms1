# 🌌 PROJECT: CYBER_EDITOR

A premium, high-efficiency text editor built with **Python 3** and **PyQt6**, following a strict **Cyberpunk UI** aesthetic.

## 📋 Technical Snapshot
- **Core Engine**: PyQt6 (Qt 6.x)
- **Design System**: Derived from `THEME_GUIDE.md` (Sharp corners, high contrast, accent-driven).
- **Configuration**: JSON-based settings (`editor_settings.json`).
- **Permissions**: Built-in Windows UAC elevation mechanism with session preservation.

## 🚀 Key Modules & Features

### 1. 🛡️ Elevation & Recovery (ELEVATE_ACCESS)
The editor allows users to upgrade their permission level without losing progress.
- **Workflow**: 
  1. Current editor content is dumped to `%TEMP%\cyber_edit_lock.tmp`.
  2. The script re-launches itself using the `runas` verb via `ShellExecuteW`.
  3. The new instance detects the `--buffer` flag, loads the temporary data, and deletes the buffer file.

### 2. ⌨️ Advanced Shortcut Engine
Custom mapping in `keyPressEvent` overrides standard behavior for enhanced productivity:
- **Move Lines**: `Alt + Up/Down` swaps the current line with the neighbor.
- **Duplicate**: `Ctrl + D` copies the active line to the next row.
- **Delete**: `Ctrl + Shift + K` kills the active line.
- **Search**: `Ctrl + F` toggles the inline search terminal.

### 3. 🔍 Search_Mod_V1
A custom-built `SearchPanel` (QFrame) integrated into the layout.
- Supports **Find Next**, **Find Prev**, and **Replace All**.
- Features a "Wrap Around" logic ensuring searches cover the entire document buffer.

### 4. 🎨 Theme System
Three built-in presets that change the global accent color:
- **CyberYellow**: #FCEE0A (Classic)
- **CyberCyan**: #00F0FF (Neon)
- **CyberRed**: #FF003C (Alert)

## 📂 File Map
- `cyber_editor.py`: The monolithic application core.
- `editor_settings.json`: Stores window state, active theme, and custom keybinds.
- `PROJECT_SUMMARY.md`: This reference document.
- `walkthrough.md`: User-facing feature guide.

## 🛠️ Developer Notes (For Future Sessions)
- **Customization**: Use the `CyberButton` and `SettingsDialog` classes to add new UI modules.
- **Shortcuts**: To add more shortcuts, update `DEFAULT_SHORTCUTS` and the `keyPressEvent` handler in `CodeEditor`.
- **Styling**: All styles are managed via `apply_theme_global()` in `MainWindow` and `apply_theme()` in individual components.

---

*System state: STABLE. Ready for further expansion.*
