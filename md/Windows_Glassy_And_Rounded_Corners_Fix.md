# Windows 11 Glassy Effect & Rounded Corners Fix Guide (AI Agent SOP)

This document provides the exact technical steps and PowerShell scripts to disable Windows transparency/glassy effects and permanently remove Windows 11 rounded window corners (with automatic startup persistence).

---

## 🪟 Part 1: Disabling Transparency & Glassy Effects

Disabling transparency removes the acrylic/glass blur on the taskbar, Start Menu, Settings, and app windows, reducing GPU and CPU usage from `dwm.exe` (Desktop Window Manager).

### Registry Key Specification
- **Path**: `HKCU:\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize`
- **Value Name**: `EnableTransparency`
- **Type**: `DWORD`
- **Value Data**: `0` (Disabled) / `1` (Enabled)

### PowerShell Command
```powershell
# Disable transparency in Registry
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize" -Name "EnableTransparency" -Value 0

# Broadcast system color change to apply immediately without restart
$code = @"
using System;
using System.Runtime.InteropServices;
public class WinApi {
    [DllImport("user32.dll", SetLastError = true, CharSet = CharSet.Auto)]
    public static extern IntPtr SendMessageTimeout(IntPtr hWnd, uint Msg, UIntPtr wParam, string lParam, uint flags, uint timeout, out UIntPtr result);
}
"@
Add-Type -TypeDefinition $code -ErrorAction SilentlyContinue
$result = [UIntPtr]::Zero
[WinApi]::SendMessageTimeout([IntPtr]0xffff, 0x001A, [UIntPtr]::Zero, "ImmersiveColorSet", 2, 5000, [ref]$result)
```

---

## 📐 Part 2: Disabling Windows 11 Rounded Window Corners

Windows 11 hardcodes rounded corners into `uDWM.dll`. The open-source utility **`win11-toggle-rounded-corners`** patches `dwm.exe` in memory to enforce square window corners.

### Tool Information
- **Repository**: `https://github.com/rich-ayr/win11-toggle-rounded-corners`
- **Latest Installer Download**:  
  `https://github.com/rich-ayr/win11-toggle-rounded-corners/releases/download/v1.4/win11-toggle-rounded-corners-setup.exe`
- **Standalone Executable**:  
  `https://github.com/rich-ayr/win11-toggle-rounded-corners/releases/download/v1.4/win11-toggle-rounded-corners.exe`

### Startup Persistence Mechanics
1. Running `win11-toggle-rounded-corners-setup.exe` installs the program.
2. The installer automatically registers a Windows Scheduled Task (`Win11ToggleRoundedCorners`).
3. On every Windows logon/startup, the task executes `win11-toggle-rounded-corners.exe --disable` with `HighestAvailable` privileges.
4. This ensures square corners persist across system reboots automatically.

---

## ⚙️ Part 3: Automated One-Click Script for AI Agents

```powershell
# 1. Disable Transparency / Glassy Effects
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize" -Name "EnableTransparency" -Value 0

# 2. Download and Run Installer for Rounded Corners Fix
$setupUrl = "https://github.com/rich-ayr/win11-toggle-rounded-corners/releases/download/v1.4/win11-toggle-rounded-corners-setup.exe"
$setupPath = "$env:USERPROFILE\Downloads\win11-toggle-rounded-corners-setup.exe"

if (!(Test-Path $setupPath)) {
    Invoke-WebRequest -Uri $setupUrl -OutFile $setupPath -UserAgent "Mozilla/5.0"
}

# Launch installer (registers startup Scheduled Task)
Start-Process -FilePath $setupPath
```
