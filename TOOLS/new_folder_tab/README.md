# Explorer Tabs

Automatically merges new File Explorer windows into tabs of an existing window instead of opening separately. Two implementations: Python and C#.

---

## Setup After PC Reset

### 1. Install Scoop (package manager)

Open PowerShell as normal user:
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex
```

### 2. Install Python (via Scoop)

```powershell
scoop install python
```

Verify: `python --version` → should show 3.12+

### 3. Install .NET SDK (via Scoop)

```powershell
scoop bucket add main
scoop install dotnet-sdk
```

Verify: `dotnet --version` → should show 9.x

### 4. Install Python dependencies

```powershell
pip install pywin32==311 comtypes==1.4.8 uiautomation==2.0.29
```

### 5. Build the C# project

```powershell
cd C:\@delta\ms1\TOOLS\new_folder_tab\csharp
dotnet build -c Release
```

---

## Running

### C# version (recommended — zero flash, no polling)

```powershell
# Run silently in background
start_explorer_tabs.bat
```

Or directly:
```powershell
.\csharp\bin\Release\net9.0-windows\ExplorerTabs.exe
```

### Python version (fallback)

```powershell
# With console output
python explorer_tabs.py

# Silent background
start_explorer_tabs.bat
```

---

## Auto-start on Login

1. Press `Win+R` → type `shell:startup` → Enter
2. Drop a shortcut to `csharp\bin\Release\net9.0-windows\ExplorerTabs.exe` in that folder

---

## How It Works

| | C# | Python |
|---|---|---|
| Detection | `SetWinEventHook` (instant, event-driven) | Polling every 300ms |
| Open tab | `WM_COMMAND 0xA21B` → `IWebBrowser2.Navigate2` | Same |
| Flash | None (window hidden before it renders) | Minimal (hidden on detection) |
| Dependencies | .NET 9 runtime (built-in on Win11) | Python + pywin32 + comtypes |
