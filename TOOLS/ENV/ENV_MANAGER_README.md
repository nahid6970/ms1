# ⚡ Windows Environment Variable Manager

A cyberpunk-themed GUI application for managing Windows environment variables, PATH entries, and command aliases.

## Features

### 🛣️ PATH Manager
- View and edit USER and SYSTEM PATH variables
- Add, edit, remove PATH entries
- Reorder PATH entries (move up/down)
- Visual list interface with real-time updates

### 🔧 Environment Variables
- Manage all USER and SYSTEM environment variables
- Create new variables
- Edit existing variables
- Delete variables
- Separate views for USER and SYSTEM scope

### 🎯 Command Aliases (Universal System)
- Create command shortcuts/aliases **once**
- **Auto-works in CMD, PowerShell, and Git Bash**
- One-click setup with "AUTO-SETUP" button
- Comes with default aliases (ll, gs, ga, gc, gp, gl)
- Apply to current session or auto-load on shell startup

## Installation

1. Install Python 3.8 or higher
2. Install dependencies:
```bash
pip install -r env_manager_requirements.txt
```

## Usage

### Run the Application
```bash
python env_variable_manager.py
```

### For SYSTEM-level Changes
Run as Administrator:
```bash
# Right-click Command Prompt/PowerShell -> Run as Administrator
python env_variable_manager.py
```

## Interface Guide

### PATH Manager Tab
- **USER/SYSTEM buttons**: Switch between user and system PATH
- **Add**: Add new PATH entry
- **Edit**: Modify selected entry
- **Remove**: Delete selected entry
- **Move Up/Down**: Reorder PATH entries
- **Refresh**: Reload from registry

### Environment Variables Tab
- **USER/SYSTEM buttons**: Switch scope
- **Add**: Create new environment variable
- **Edit**: Modify variable value
- **Remove**: Delete variable
- **Refresh**: Reload from registry

### Aliases Tab
- **Add Alias**: Create command shortcut (e.g., `ll` → `ls -la`)
- **Remove**: Delete alias
- **Apply All**: Apply aliases to current CMD session
- **Auto-Setup**: Configure automatic loading for all shells (one-time setup)
- **Refresh**: Reload from storage

#### How It Works
1. Aliases are stored in `~/.aliases/aliases.json`
2. Loader scripts are auto-generated for each shell:
   - `aliases.cmd` for CMD (via Registry AutoRun)
   - `aliases.ps1` for PowerShell (via profile)
   - `aliases.sh` for Bash/Git Bash (via .bashrc)
3. Click "AUTO-SETUP" once to configure all shells
4. Add/edit aliases anytime - they auto-update all shells

## Alias Storage & Auto-Loading

### Storage Location
All aliases are stored in: `~/.aliases/`
- `aliases.json` - Master alias definitions
- `aliases.cmd` - CMD loader (auto-generated)
- `aliases.ps1` - PowerShell loader (auto-generated)
- `aliases.sh` - Bash loader (auto-generated)

### Default Aliases Included
```json
{
  "ll": "ls -la",
  "gs": "git status",
  "ga": "git add",
  "gc": "git commit",
  "gp": "git push",
  "gl": "git log --oneline",
  "cls": "clear"
}
```

### One-Time Setup
Click **"AUTO-SETUP"** button to configure:
1. **PowerShell**: Adds loader to profile
2. **CMD**: Sets Registry AutoRun key
3. **Bash/Git Bash**: Adds source line to .bashrc

After setup, all new shells automatically load your aliases!

### Manual Application
- **Apply All**: Applies to current CMD session only
- Useful for testing before auto-setup

## Latest Improvements

- **Crash Prevention**: Uses `SendMessageTimeout` when broadcasting environment changes. This prevents the UI from hanging or crashing if other applications (like an unresponsive Explorer window) fail to respond to the system-wide message.
- **Robust Registry Management**: All registry operations now use Python context managers (`with winreg.OpenKey(...)`), ensuring registry handles are safely closed even if an error occurs.
- **Enhanced Safety Checks**: Added validation for table selection and item existence to prevent null-pointer style crashes during editing and removal.
- **Smart PATH Loading**: Improved detection of the `Path` variable, handling cases where it might be missing or named differently (`PATH` vs `Path`).

## Theme

Uses cyberpunk color scheme from THEME_GUIDE.md:
- Background: Dark (#050505)
- Accents: Cyan (#00F0FF), Yellow (#FCEE0A)
- Font: JetBrainsMono NFP (Nerd Font Mono)

## Permissions

- **USER scope**: No special permissions needed
- **SYSTEM scope**: Requires Administrator privileges

## Notes

- Changes to environment variables may require restarting applications
- PATH changes are immediately written to registry
- Aliases apply to current session via doskey
- For persistent aliases across all sessions, export to PowerShell profile

## Troubleshooting

**"Permission denied" error**
- Run as Administrator for SYSTEM-level changes

**Changes not visible in other programs**
- Restart the application/terminal
- Log out and log back in
- Restart Windows (for system-wide changes)

**Aliases not working**
- Click "AUTO-SETUP" button (one-time)
- Restart your shell after setup
- For immediate use, click "APPLY ALL" in current CMD session
- Check if loader files exist in `~/.aliases/`

## Safety

- Backup your PATH before making changes
- Test changes in USER scope first
- Be careful with SYSTEM variables (affects all users)
