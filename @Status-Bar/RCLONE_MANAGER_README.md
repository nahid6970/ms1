# Rclone Sync Manager

A standalone GUI application for managing rclone sync operations with auto-sync timers and system tray support.

## Features

- **JSON-based Configuration**: All projects stored in `rclone_config.json`
- **Auto-Sync Timers**: Set individual sync intervals for each project
- **System Tray Support**: Minimize to tray option in settings
- **Cyberpunk Theme**: Dark theme based on THEME_GUIDE.md
- **Easy Management**: Add, edit, and delete rclone projects through GUI
- **Multiple Sync Options**:
  - CHECK: Verify sync status
  - SYNC →: Sync from source to destination
  - ← SYNC: Reverse sync from destination to source
- **Log Viewing**: Click project label to view logs in PowerShell

## Installation

### Requirements

```bash
pip install pillow pystray
```

## Usage

### Running the Application

```bash
python rclone_manager.py
```

### Adding a New Project

1. Click "**+ ADD RCLONE PROJECT**" button
2. Fill in the form:
   - **Name**: Unique identifier for the project
   - **Label**: Display text (can use emoji/icons)
   - **Source Path**: Local path to sync from
   - **Destination**: Rclone remote destination
   - **Check Command**: Command to verify sync status (use `src` and `dst` as placeholders)
   - **Sync Command**: Command to sync source → destination
   - **Reverse Sync**: Command to sync destination → source
   - **Auto-Sync (min)**: Interval in minutes (0 = disabled)
3. Click "**SAVE**"

### Auto-Sync Timer

- Set **Auto-Sync (min)** to a value greater than 0 to enable automatic syncing
- The timer will execute the sync command (SYNC →) at the specified interval
- Each project can have its own timer interval
- Set to 0 to disable auto-sync for a project

### Settings

Click "**⚙ SETTINGS**" to configure:
- **Minimize to System Tray**: When enabled, closing the window minimizes to tray instead of exiting

### System Tray

When minimized to tray:
- Right-click the tray icon to:
  - **Show**: Restore the window
  - **Exit**: Quit the application

## Configuration File

The `rclone_config.json` file structure:

```json
{
    "rclone": [
        {
            "name": "project_name",
            "path": "C:/source/path",
            "dst": "remote:/destination",
            "label": "Display Label",
            "cmd": "rclone check src dst --fast-list --size-only",
            "left_click_cmd": "rclone sync src dst -P --fast-list",
            "right_click_cmd": "rclone sync dst src -P --fast-list",
            "log": "C:\\path\\to\\log.log",
            "auto_sync_interval": 30
        }
    ],
    "settings": {
        "minimize_to_tray": true
    },
    "theme": {
        "bg": "#050505",
        "panel": "#111111",
        "accent": "#00F0FF",
        "text": "#E0E0E0",
        "subtext": "#808080",
        "dim": "#3a3a3a",
        "green": "#00ff21",
        "red": "#FF003C",
        "yellow": "#FCEE0A",
        "font_family": "Consolas",
        "font_size": 10
    }
}
```

## Button Actions

- **CHECK**: Runs the check command and updates status indicator (green = OK, red = errors)
- **SYNC →**: Syncs from source to destination (equivalent to Ctrl+Left click in original)
- **← SYNC**: Reverse syncs from destination to source (equivalent to Ctrl+Right click)
- **EDIT**: Modify project settings
- **DELETE**: Remove project from list
- **Label Click**: Opens log file in PowerShell editor

## Status Indicators

- **Gray ●**: Not checked yet
- **Green ●**: Last check successful (no errors)
- **Red ●**: Last check found errors

## Notes

- Commands use `src` and `dst` as placeholders which are automatically replaced with actual paths
- Log files are stored in `C:\Users\nahid\script_output\rclone\`
- Auto-sync timers run in background threads
- All sync operations open in new PowerShell windows for monitoring

## Customization

Edit the `theme` section in `rclone_config.json` to customize colors and fonts.
