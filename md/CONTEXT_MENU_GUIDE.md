# Context Menu Command Reference

I have a GUI app that manages Windows right-click context menu entries. When I ask for context menu commands, provide ONLY the command string itself - nothing else.

## What to Provide

Just the command line, like:
```
cmd.exe /k cd /d "%1"
```

## Placeholders

- `%1` - Selected file/folder path
- `%V` - Directory path (backgrounds)

## Examples

**Open Terminal:**
```
cmd.exe /k cd /d "%1"
```

**Copy Path:**
```
cmd /c echo %1 | clip
```

**Run Python Script:**
```
pythonw "C:\path\to\script.py" "%1"
```

**PowerShell Script:**
```
powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File "C:\path\to\script.ps1" "%1"
```

## Notes

- Use `pythonw` to avoid terminal windows
- Wrap paths in quotes: `"%1"`
- Don't include menu labels, scope, or explanations - just the command
