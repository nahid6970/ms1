# Directory Launcher

A terminal-based tool to quickly access your favorite directories and open them with specific applications or commands. Built with Python and FZF, featuring a cyberpunk aesthetic.

## Features

*   **Quick Navigation**: Browse and select directories using `fzf`.
*   **Action Menu**: Choose specific actions for each directory (e.g., Open in Explorer, Gemini, Terminal, Code).
*   **View Modes**: Toggle between "Name Only" and "Full Path" views.
*   **Management**: Add, remove, and reorder directories and commands directly from the UI.
*   **Persistent Settings**: Your directories, commands, and view preferences are saved automatically.
*   **Cyberpunk Theme**: Styled with a dark theme and neon accents.

## Installation

Ensure you have [fzf](https://github.com/junegunn/fzf) installed and available in your system PATH.

## Usage

Run the script with Python:

```powershell
python dir_launcher.py
```

## Shortcuts

| Key | Action | Context |
| :--- | :--- | :--- |
| **Enter** | Select Directory / Run Command | Directory List / Command List |
| **Tab** | Toggle View Mode (Name/Path) | Directory List |
| **Ctrl + A** | Add New Directory / Command | Directory List / Command List |
| **Ctrl + D** | Remove Selected Item | Directory List / Command List |
| **Alt + Up** | Move Item Up | Directory List / Command List |
| **Alt + Down** | Move Item Down | Directory List / Command List |
| **?** | Toggle Help Preview | Directory List / Command List |
| **Esc** | Go Back / Exit | Directory List / Command List |

## Configuration

All data is stored in `dir_launcher.json` located in the same directory as the script. You can edit this file manually if preferred.

**Example `dir_launcher.json`:**

```json
{
    "directories": [
        "C:/Projects/WebApp",
        "D:/Photos"
    ],
    "commands": [
        {
            "name": "Explorer",
            "template": "explorer \"{path}\""
        },
        {
            "name": "VS Code",
            "template": "code \"{path}\""
        }
    ],
    "settings": {
        "view_mode": "name"
    }
}
```
