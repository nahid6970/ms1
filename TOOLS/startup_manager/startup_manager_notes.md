# Startup Manager Execution & Preview Architecture

This document explains how the Startup Manager launches processes, how wrapper scripts are generated, and how the preview actions match the actual Windows system startup behavior. Use this file as context for future development or troubleshooting.

---

## 1. Startup Modes

The Startup Manager operates in two primary modes, toggleable from the UI:

### A. Registry Mode (`REGISTRY`)
Startup entries are registered in the Windows Registry under:
`HKCU\Software\Microsoft\Windows\CurrentVersion\Run`

Depending on the item configuration, the registry values point to:
1. **Raw Command**: `"{executable_path}" {args}`
2. **AutoHotkey Wrapper**: `"{manager_dir}\ahk_wrappers\{item_name}_wrapper.ahk"`
3. **VBScript Wrapper**: `wscript.exe "{manager_dir}\vbs\{item_name}_{suffix}.vbs"`

### B. Script Mode (`SCRIPT`)
Startup entries are generated into a single consolidated PowerShell script (`myStartup.ps1` by default).

---

## 2. Wrapper Scripts

To support advanced execution options (like hiding terminals or running as administrator) without complex registry configurations, the manager generates wrapper scripts:

### A. AutoHotkey Wrapper (`ahk_v2`)
Generates an `.ahk` script that launches the target.
- **Admin Verb**: Uses `*RunAs ` to request elevation.
- **Hide Terminal**: Employs the `"Hide"` parameter in AHK's `Run` command.
- **Key Syntax**:
  ```autohotkey
  #NoTrayIcon
  Run '*RunAs "C:\path\to\target.exe" arguments', , "Hide"
  ```

### B. VBScript Wrapper (`wscript.exe`)
Used for standard applications requiring admin execution or terminal hiding under Registry mode when AHK is not selected.
- **Admin Elevation**: Calls `ShellExecute` with the `"runas"` verb.
- **Hide Terminal**: Sets window style parameter to `0` (hidden).
- **Key Syntax**:
  ```vbscript
  ' Admin Elevation / Hidden
  CreateObject("Shell.Application").ShellExecute "C:\path\to\target.exe", "arguments", "", "runas", 0
  
  ' Non-Admin / Hidden
  CreateObject("WScript.Shell").Run """C:\path\to\target.exe"" arguments", 0, False
  ```

---

## 3. Preview Action (Execute Protocol)

### The Problem
Previously, right-clicking an item and choosing **EXECUTE PROTOCOL** or **EXECUTE AS ADMIN** ran the executable target directly (`subprocess.Popen`). This bypassed the generated AHK/VBS wrappers entirely, resulting in "false positives" where previews succeeded but actual startup failed due to syntax issues in the generated wrappers.

### The Solution
The launch preview handler (`handle_launch` in `startup.py`) is aligned to mimic the Windows Startup environment exactly:
- **Registry Mode Preview**: Runs the wrapper script directly (`wscript.exe` for VBS, or opening the `.ahk` script) if the configuration mandates wrappers.
- **Script Mode Preview**: Executes the target command line exactly as it would be formatted in the PowerShell script.
