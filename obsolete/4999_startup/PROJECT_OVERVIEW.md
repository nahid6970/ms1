# STARTUP // MANAGER_V2.0 // PROJECT_OVERVIEW

## 1. Project Purpose
A high-performance, Cyberpunk-themed Windows Startup Manager designed to provide granular control over system startup items. It allows users to consolidate scattered startup entries (Registry, Folders, Tasks) into a single managed dashboard.

## 2. Technology Stack
- **Core**: Python 3.x
- **UI Framework**: PyQt6 (Custom Cyberpunk styling)
- **OS Integration**: Windows Registry (`winreg`), Task Scheduler (`schtasks` & PowerShell), Windows Startup Folders.
- **Persistence**: JSON-based storage for items (`startup_items.json`) and application preferences (`settings.json`).

## 3. Core Architecture: Dual-Mode Operation
The application operates in two distinct modes, switchable via the **MODE** button:

### A. REGISTRY Mode (Neon Cyan)
- Directly manages keys in `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` and `HKLM\...`.
- Deactivating an item in this mode removes the registry key. Activating it recreates it.

### B. SCRIPT Mode (Cyber Yellow)
- Manages startup items via a generated PowerShell script (`myStartup.ps1`).
- Users can choose the script path via the **PS1_PATH** button.
- Deactivating/activating items updates the internal database and regenerates the script.
- **Workflow**: The user should ensure `myStartup.ps1` itself is triggered at system startup (e.g., via a single Registry key or Task).

## 4. Key Features
- **Intelligent Scanning**:
    - `SCAN_SYS`: Scans Windows Startup folders.
    - `SCAN_REG`: Scans HKLM and HKCU 'Run' keys.
    - `SCAN_TASKS`: Scans Task Scheduler for "Logon" triggers (captures elusive apps like PowerToys).
- **Auto-Disabling**: When importing from Registry or Tasks, the app automatically disables the original OS entry to prevent duplicate launches.
- **Clean Interface**: Actions are hidden behind a right-click context menu (Launch, Open Dir, Edit, Delete).
- **Timeline Tracking**: Tracks the date each item was added to the manager.
- **Advanced Sorting**: Sort items by **Name** or **Date Added** (Logged), with Persistent ASC/DESC order.
- **PSReadLine Fix**: Automatically configures `PSReadLineScreenReaderOptimization` to "None" to prevent terminal warnings caused by UI Automation tools.

## 5. File Structure
- `startup.py`: Main application logic and UI.
- `startup_items.json`: Database of managed startup items.
- `settings.json`: App preferences (Last mode, PS1 path, Sort settings).
- `PROJECT_OVERVIEW.md`: This documentation.

## 6. Recent Major Fixes
- **Startup Crash**: Fixed a `NameError` where `MainWindow` class definition was missing.
- **Task Scanning**: Rewrote the Task Scheduler parser to use robust PowerShell JSON output, correctly identifying PowerToys and similar apps.
- **UI Alignment**: Synchronized heights and styles for sorting controls to match the Cyberpunk aesthetic.
- **Persistence**: ensured `current_mode` and `ps1_file_path` are correctly loaded *before* the UI initializes to prevent visual glitches.

## 7. Future Considerations
- Implement a "Master Enable" for the PowerShell script mode to automatically register the script in the Windows Registry.
- Add support for "Delayed Start" (custom sleep timers between launches).
- Implement batch actions (Delete All, Enable All).
