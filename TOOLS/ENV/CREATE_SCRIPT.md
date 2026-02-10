# 🛠️ Automated Script Creation Guide

Follow these templates to create scripts that automatically receive the file path when clicked from the Windows Context Menu.

## 🐍 Python Template (`.py`)

Save as `your_script.py`. The path of the clicked file will be in `sys.argv[1]`.

```python
import sys
import os

def main():
    if len(sys.argv) < 2:
        print("No file path received.")
        return

    # Automatically get the file path from context menu
    file_path = sys.argv[1]
    
    print(f"Processing: {file_path}")
    
    # YOUR LOGIC HERE
    # Example: print file size
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        print(f"File size: {size} bytes")

    input("
Press Enter to exit...")

if __name__ == "__main__":
    main()
```

## 📜 PowerShell Template (`.ps1`)

Save as `your_script.ps1`. The path of the clicked file will be in `$args[0]`.

```powershell
# Automatically get the file path from context menu
$filePath = $args[0]

if (-not $filePath) {
    Write-Host "No file path received." -ForegroundColor Red
    $filePath = Read-Host "Please enter file path manually"
}

Write-Host "Processing: $filePath" -ForegroundColor Cyan

# YOUR LOGIC HERE
# Example: Show file info
Get-Item $filePath | Select-Object Name, Length, LastWriteTime | Format-List

Write-Host "`nDone. Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
```

## ⚙️ How to use:
1. Create your script using one of the templates above.
2. Save it into your manager's script folder.
3. In the **SCRIPTS** tab, select your script and click **"ADD TO CONTEXT MENU"**.
4. The manager will now automatically handle the `%1` (File) or `%V` (Folder) parameter passing for you.
