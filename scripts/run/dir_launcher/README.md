# Directory Launcher

A terminal-based tool to quickly access your favorite directories and open them with specific applications or commands. Built with Python and FZF, featuring a cyberpunk aesthetic with colored categories.

## Features

*   **Quick Navigation**: Browse and select directories using `fzf`.
*   **Action Menu**: Choose specific actions for each directory (e.g., Open in Explorer, Gemini, Terminal, VS Code).
*   **Categories**: Organize directories and commands into categories displayed in Cyan.
*   **View Modes**: Toggle between "Name Only" and "Full Path" views.
*   **Management**: Add, edit, remove, and reorder directories and commands directly from the UI.
*   **Persistent Settings**: Your directories, commands, categories, and view preferences are saved automatically.
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
| **Ctrl + E** | Edit Selected Directory / Command | Directory List / Command List |
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
        {
            "path": "C:/Projects/WebApp",
            "category": "Work"
        },
        {
            "path": "D:/Photos",
            "category": "Personal"
        }
    ],
    "commands": [
        {
            "name": "Gemini",
            "template": "start \"Gemini\" /D \"{path}\" cmd /k gemini",
            "category": "AI"
        },
        {
            "name": "📁Explorer",
            "template": "explorer \"{path}\"",
            "category": "General"
        },
        {
            "name": "VS Code",
            "template": "code \"{path}\"",
            "category": "Editor"
        }
    ],
    "settings": {
        "view_mode": "name"
    }
}
```

### Template Placeholders

*   `{path}` - The selected directory path.
