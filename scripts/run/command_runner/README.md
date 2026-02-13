# Command Runner

A cyberpunk-themed terminal command launcher with FZF integration for quick command execution across multiple shells.

## Features

- **Multi-Shell Support**: Execute commands in CMD, PowerShell, or PowerShell Core (pwsh)
- **Command History**: Automatically tracks and displays previously executed commands
- **Bookmarks**: Save frequently used commands with custom shell and directory settings
- **Directory History**: Quick access to last 10 working directories used
- **FZF Integration**: Fast fuzzy search through commands and bookmarks
- **Cyberpunk UI**: Frameless, always-on-top GUI with keyboard navigation

## Files

- `RunCommand.py` - Main launcher that feeds data to FZF
- `terminal_chooser.py` - GUI for selecting terminal and working directory
- `executor.py` - Executes commands in the selected terminal
- `add_command_bookmark.py` - Add commands to bookmarks
- `view_command_bookmarks.py` - View and manage bookmarks

## Usage

1. Run `RunCommand.py` to launch the FZF command selector
2. Search and select a command (bookmarks marked with `*`)
3. Choose terminal type (CMD/PowerShell/PWSH)
4. Set working directory or select from history
5. Press Enter to execute

## Keyboard Navigation

- **Arrow Keys**: Navigate between terminal buttons
- **Up/Down**: Move between buttons and directory input
- **Enter**: Execute command
- **Escape**: Close window

## Data Storage

- Command history: `C:\@delta\db\FZF_launcher\command_history.json`
- Bookmarks: `C:\@delta\db\FZF_launcher\command_bookmarks.json`
- Directory history: `./dir_history.json`

## Requirements

- Python 3.x
- PyQt6
- FZF (fuzzy finder)
