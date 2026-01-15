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
- **Dynamic Header**: Frameless window with custom drag logic and a 35px top margin to ensure utility buttons (+S, +F, CFG, X) are fully visible.
- **Multi-line Labels**: Supports HTML-style `<br>` tags in item names for precise aesthetic control on grid buttons.

### 3. Deep Customization (Cyberpunk Aesthetic)
- **Item Level**: Set specific colors, fonts, sizes, and corner radiuses for individual buttons.
- **Global Level (CFG Menu)**:
    - **Global Layout**: Define grid columns and default button heights.
    - **Global Typography**: Set default font family (Consolas recommended) and sizes.
    - **Appearance Settings**: 
        - Custom Main Background and Window Border colors.
        - **CFG Button Styling**: Independent Background (BG) and Foreground (FG/Text) controls for the main config button.
    - **Item Defaults**: Configure default background/foreground colors and hover states for both Scripts and Folders separately. New items automatically inherit these defaults.
- **Stats Dashboard**: Integrated real-time CPU, RAM, and Disk usage monitoring.

---

## 🛠 Internal Architecture

### `CyberButton` (Custom Widget)
- Handles the rendering of grid items.
- Manages multi-line text conversion (`<br>` -> `\n`).
- Implements hovering effects and context menu triggers (Edit, Copy, Cut, Delete).
- **Theme Awareness**: Ingests the global `config` object to apply dynamic defaults if individual overrides are missing.
- **Robust CSS**: Uses a 1px transparent border fallback to ensure background colors render correctly on Windows.

### `_run_shell` (Centralized Launch Helper)
- Standardizes process creation.
- Uses `ctypes.windll.shell32.ShellExecuteW` to avoid the multi-level string escaping issues common with `subprocess.Popen`.
- Correctly handles the `verb` (None vs "runas") and `show` (SW_HIDE vs SW_SHOWNORMAL) parameters.

### `EditDialog` & `SettingsDialog`
- **EditDialog**: 1150px wide, 45/55 split between settings and the Inline Script Editor. Now identifies parent config to provide accurate color previews.
- **SettingsDialog**: Advanced color pickers for every global default state, including new CFG button FG/BG controls.

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
      "use_inline": false
    },
    {
      "name": "Tools",
      "type": "folder",
      "scripts": [...]
    }
  ],
  "def_script_bg": "#FFFFFF",
  "def_folder_bg": "#FCEE0A",
  "cfg_btn_color": "#3a3a3a",
  "cfg_text_color": "white"
}
```

## 📝 Recent Version Notes (v3.3)
- **Fixed**: Header buttons (+S, +F, CFG, X) being cut off at the top.
- **Fixed**: Global Script Foreground color accidentally changing the CFG button text.
- **Added**: Interactive, clickable breadcrumb navigation with collapsed extra whitespace.
- **Added**: Full global item styling (BG, FG, Hover) in CFG menu.
- **Improved**: New items now strictly inherit global defaults instead of having hardcoded color keys.
