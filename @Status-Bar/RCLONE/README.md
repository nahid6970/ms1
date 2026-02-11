# RClone GUI Manager

A lightweight, customizable GUI for managing multiple rclone sync operations with automatic monitoring and synchronization.

## Features

### Core Functionality
- **Multiple Sync Profiles**: Manage multiple rclone sync configurations from a single interface
- **Visual Status Indicators**: Color-coded labels (Green = synced, Red = differences detected)
- **Auto-Sync on Red**: Automatically syncs items when differences are detected
- **Periodic Checking**: Configurable interval for checking sync status
- **Manual Sync Operations**: 
  - Ctrl + Left Click: Sync source to destination
  - Ctrl + Right Click: Sync destination to source
  - Left Click: View check log

### Interface Features
- **Draggable Window**: Click and drag to reposition
- **Always on Top**: Optional topmost mode (hides for fullscreen apps)
- **System Tray**: Minimize to tray instead of closing
- **Reload Button**: Restart the script without closing
- **Custom Positioning**: Configure X/Y position and window dimensions

### Configuration
- **Width/Height**: Auto or custom window size
- **X/Y Position**: Auto-center or custom screen position
- **Check Interval**: How often to check for differences (seconds)
- **Auto-Sync Toggle**: Enable/disable automatic syncing
- **Auto-Sync on Red**: Sync items immediately when they turn red
- **Minimize to Tray**: Close button minimizes to system tray

## Installation

### Requirements
```bash
pip install customtkinter pillow pystray pywin32
```

### Required Tools
- Python 3.x
- rclone (must be installed and configured)

## Usage

### Running the Application
```bash
python mypygui.py
```

### Adding a Sync Profile
1. Click the **+** button
2. Fill in the form:
   - **Name**: Unique identifier for the profile
   - **Label**: Display text/icon (supports Unicode/emoji)
   - **Source Path**: Source directory or remote
   - **Destination Path**: Destination directory or remote
   - **Left Click Command**: Command for Ctrl+Left click (default: sync src→dst)
   - **Right Click Command**: Command for Ctrl+Right click (default: sync dst→src)
3. Click **Add**

### Editing a Profile
1. Right-click on any label
2. Modify the fields
3. Click **Save** to update or **Delete** to remove

### Auto-Sync Workflow
1. Enable auto-sync by clicking the **🕒** button (turns green when ON)
2. Enable "Auto-Sync When Item Turns Red" in settings
3. When a check detects differences (item turns red):
   - Auto-sync triggers immediately for that item only
   - Syncs the item
   - Runs a check to verify
   - Item turns green if successful

### Manual Operations
- **Left Click**: View check log for the item
- **Ctrl + Left Click**: Manually sync source → destination
- **Ctrl + Right Click**: Manually sync destination → source
- **Right Click**: Edit the profile

## Configuration Files

### commands.json
Stores all sync profiles:
```json
{
  "profile_name": {
    "cmd": "rclone check src dst --fast-list --size-only",
    "src": "/path/to/source",
    "dst": "/path/to/destination",
    "label": "📁",
    "left_click_cmd": "rclone sync src dst -P --fast-list --log-level INFO",
    "right_click_cmd": "rclone sync dst src -P --fast-list"
  }
}
```

### settings.json
Application settings:
```json
{
  "width": null,
  "height": 39,
  "x": null,
  "y": 800,
  "interval": 3600,
  "check_interval": 600,
  "minimize_to_tray": true,
  "auto_sync_enabled": false,
  "auto_sync_on_red": true,
  "topmost": false
}
```

## Logs

All logs are saved to: `C:\Users\<username>\script_output\rclone\`

- `<label>_check.log`: Check operation logs
- `<label>_sync.log`: Sync operation logs

## Terminal Output

The application provides detailed terminal output:
- 🔍 Check operations with status
- ✅ Success indicators (green/synced)
- ❌ Difference indicators (red/needs sync)
- 🔄 Auto-sync triggers with details
- 📁 Source/destination paths
- ⚙️ Command execution status
- 📝 Log file locations

## Keyboard Shortcuts

- **Drag**: Click and hold to move window
- **Ctrl + Left Click**: Sync source → destination
- **Ctrl + Right Click**: Sync destination → source

## Buttons

- **+**: Add new sync profile
- **🕒**: Toggle auto-sync (OFF=red, ON=green with pulse)
- **🔄**: Reload/restart the application
- **⚙️**: Open settings
- **✕**: Close (or minimize to tray if enabled)

## Tips

1. **Use Unicode Icons**: Labels support emoji and Unicode characters (📁, 🔥, ⭐, etc.)
2. **Check Interval**: Set based on your needs (600s = 10 minutes is default)
3. **Auto-Sync**: Enable for hands-free synchronization
4. **Logs**: Check logs when items stay red to diagnose issues
5. **System Tray**: Enable to keep the app running in background

## Troubleshooting

### Item stays red after sync
- Check the sync log: `C:\Users\<username>\script_output\rclone\<label>_sync.log`
- Verify rclone configuration
- Check source/destination paths

### Auto-sync not working
- Ensure auto-sync button is ON (green)
- Verify "Auto-Sync When Item Turns Red" is enabled in settings
- Check terminal output for error messages

### Window position issues
- Reset X/Y position in settings to auto-center
- Manually drag window to desired position (saves automatically)

## License

This project is provided as-is for personal use.

## Credits

Built with:
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- [Pillow](https://python-pillow.org/)
- [pystray](https://github.com/moses-palmer/pystray)
- [pywin32](https://github.com/mhammond/pywin32)
- [rclone](https://rclone.org/)
