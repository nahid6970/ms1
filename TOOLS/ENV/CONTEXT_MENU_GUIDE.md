# Context Menu Command Reference

I have a PyQt6 GUI application (`env_variable_manager.py`) that manages Windows right-click context menu entries. When I ask for context menu commands, provide ONLY the command string - no registry scripts or manual setup needed.

## How to Provide Commands

**Format:**
```
Menu Label: <what appears in context menu>
Command: <the actual command to execute>
Scope: Files | Folders | Background | (combination)
```

## Command Placeholders

- `%1` - Full path to the selected file/folder
- `%V` - Directory path (for folder backgrounds)
- `%*` - All selected files (space-separated)

## Examples

### Open Terminal Here
```
Menu Label: Open Terminal Here
Command: cmd.exe /k cd /d "%1"
Scope: Folders, Background
```

### Copy File Path
```
Menu Label: Copy Path
Command: cmd /c echo %1 | clip
Scope: Files
```

### Open with VS Code
```
Menu Label: Open with VS Code
Command: "C:\Program Files\Microsoft VS Code\Code.exe" "%1"
Scope: Files, Folders
```

### Run Python Script
```
Menu Label: Process with Python
Command: pythonw "C:\path\to\script.py" "%1"
Scope: Files
```

### PowerShell Script
```
Menu Label: My PowerShell Action
Command: powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File "C:\path\to\script.ps1" "%1"
Scope: Files
```

## Notes

- Use `pythonw` instead of `python` to avoid terminal windows
- Use `start /B` or `-WindowStyle Hidden` for background execution
- Wrap paths with spaces in quotes: `"%1"`
- I can add icons during setup via the GUI
- Commands can be batch files, executables, or direct shell commands

## What NOT to Provide

❌ Registry scripts (.reg files)
❌ Manual registry editing instructions
❌ Long setup procedures

✅ Just give me the command string - I'll add it through my GUI!
