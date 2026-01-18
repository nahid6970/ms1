# Script Manager GUI Qt

A cyberpunk-themed script launcher and manager built with PyQt6.

## Features

- **Grid-based Layout**: Customizable grid with drag & drop support
- **Script & Folder Management**: Organize scripts in folders with custom styling
- **Icon Support**: Add custom icons (.ico, .png, .jpg, .svg) with positioning options
- **Inline Script Editor**: Write and execute scripts directly in the app
- **Custom Styling**: Per-item colors, fonts, borders, and hover effects
- **Admin Execution**: Run scripts with elevated privileges
- **Multiple Interpreters**: Support for cmd, PowerShell, Python
- **Cyberpunk Theme**: Dark theme with neon accents

## Recent Changes

### ✅ Performance Widget Removal
- Removed CPU, RAM, and SSD monitoring widgets
- Eliminated psutil dependency
- Cleaner, lighter interface focused on script management
- Removed dashboard settings from configuration panel

## Installation

1. Install Python 3.8+
2. Install dependencies: `pip install PyQt6`
3. Run: `python script_manager_gui_qt.py`

## Configuration

Settings are stored in `script_launcher_config.json` and include:
- Grid layout (columns, button height)
- Default fonts and styling
- Window dimensions and behavior
- Item style defaults for scripts and folders
