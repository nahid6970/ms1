# SCRIPT MANAGER // PROJECT OVERVIEW

## Project Description
A high-performance, cyberpunk-themed script management application built with **Python** and **PyQt6**. It allows users to organize, customize, and launch various scripts (Python, PowerShell, Batch) and executables through a sleek, grid-based dashboard.

## Technical Core
- **Framework**: PyQt6 (Frameless, Custom Styling)
- **Execution Engine**: Native Windows `ShellExecuteW` API (via `ctypes`) for robust process handling.
- **Data Persistence**: `script_launcher_config.json` (Stores hierarchy, script metadata, and global styles).

---

## 🚀 Key Features

### 1. Advanced Execution Logic
Universal support for `.py`, `.ps1`, `.bat`, and `.exe` with the following flags:
- **Run as Admin**: Elevates process using the native Windows `runas` verb.
- **New Terminal**: Launches scripts in a fresh `cmd` or `pwsh` instance.
- **Keep Open**: Prevents the terminal window from closing after execution (uses `/k` for CMD, `-NoExit` for PWSH).
- **Hide Terminal**: Conceals the console window entirely (useful for automation).
- **Working Directory Context**: Automatically anchors all processes to their source directory to prevent path errors.

### 2. Interactive Navigation
- **Hierarchy**: Supports infinite nesting of folders.
- **Clickable Breadcrumbs**: The header shows `// ROOT / FOLDER / SUBFOLDER`. Each part is a clickable link for instant "jump-back" navigation.
- **Multi-line Labels**: Supports HTML-style `<br>` tags in item names for precise aesthetic control on grid buttons.

### 3. Deep Customization (Cyberpunk Aesthetic)
- **Item Level**: Set specific colors, fonts, sizes, and corner radiuses for individual buttons.
- **Global Level (CFG Menu)**:
    - **Global Layout**: Define grid columns and default button heights.
    - **Global Typography**: Set default font family (Consolas recommended) and sizes.
    - **Item Defaults**: Configure default background/foreground colors and hover states for both Scripts and Folders separately.
- **Stats Dashboard**: Integrated real-time CPU, RAM, and Disk usage monitoring.

---

## 🛠 Internal Architecture

### `CyberButton` (Custom Widget)
- Handles the rendering of grid items.
- Manages multi-line text conversion (`<br>` -> `\n`).
- Implements hovering effects and context menu triggers (Edit, Copy, Cut, Delete).
- Dynamically calculates height based on `row_span` and grid spacing.

### `_run_shell` (Centralized Launch Helper)
- Standardizes process creation.
- Uses `ctypes.windll.shell32.ShellExecuteW` to avoid the multi-level string escaping issues common with `subprocess.Popen`.
- Correctly handles the `verb` (None vs "runas") and `show` (SW_HIDE vs SW_SHOWNORMAL) parameters.

### `EditDialog` & `SettingsDialog`
- **EditDialog**: 1150px wide, 45/55 split between settings and the Inline Script Editor.
- **SettingsDialog**: Advanced color pickers for every global default state.

---

## 📂 Configuration Schema (`script_launcher_config.json`)
The JSON follows a recursive structure:
```json
{
  "scripts": [
    {
      "name": "My Script",
      "type": "script",
      "path": "C:\\...",
      "run_admin": true,
      "use_inline": false,
      "color": "#FFFFFF"
    },
    {
      "name": "Tools",
      "type": "folder",
      "scripts": [...]
    }
  ],
  "def_script_bg": "#FFFFFF",
  "def_folder_bg": "#FCEE0A"
}
```

## 📝 Recent Version Notes (v3.2)
- **Fixed**: Admin elevation path mangling ("Syntax Incorrect" error).
- **Fixed**: Elevated PowerShell windows closing immediately.
- **Added**: Breadcrumb-based navigation.
- **Added**: Detailed global item styling in CFG menu.
- **Improved**: Collapsed redundant whitespace in folder navigation titles.
