# 🚀 Antigravity Script Manager

A powerful, premium Python-based GUI application designed to centralize your workflow. It combines script management, Git repository monitoring, Rclone sync status, and real-time system performance metrics into a single, sleek, frameless dashboard.

## ✨ Key Features

### 🖥️ Script Launcher
- **Customizable Buttons**: Add any script or executable with a dedicated button.
- **Advanced Styling**: Individual control over background, hover background, text color, hover text color, border width, and border color.
- **Context Actions**: Right-click any button to **Edit / Stylize**, **Duplicate**, or **Delete** it.
- **Dynamic Grid**: Adjust the number of columns in settings to fit your screen.

### 📊 System Performance Widget
- **CPU Monitoring**: Real-time percentage with individual core-by-core micro bars.
- **Memory & Storage**: Progress bars for RAM usage and Disk C/D status.
- **Live Network**: Monitor MB/s speed for both Upload (▲) and Download (▼).
- **Resource Optimized**: Threads are staggered to prevent CPU spikes and can be disabled to save resources.

### 🐙 GitHub Repository Status
- **Real-time Monitoring**: Instant visual feedback (Green for clean, Red for dirty/modified).
- **Quick Shortcuts**:
    - **Left Click**: Launch `gitter` sync.
    - **Right Click**: Open `lazygit` in a new terminal.
    - **Ctrl + Left Click**: Open repo folder in Explorer.
    - **Ctrl + Right Click**: Execute `git restore .` to revert changes.

### ☁️ Rclone & Folder Sync
- **Status Indicators**: Background checking for differences between local and cloud folders.
- **Interaction**:
    - **Left Click**: View the last `rclone check` logs.
    - **Ctrl + Left Click**: Sync Local ➔ Cloud.
    - **Ctrl + Right Click**: Sync Cloud ➔ Local.

## 🛠️ Configuration & Settings
- **Toggle Widgets**: Enable or disable GitHub, Rclone, or System Stats widgets to declutter the UI.
- **Topmost Window**: Frameless design that stays on top by default for quick access.
- **Draggable UI**: Move the window anywhere by dragging the header.

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Dependencies: `pip install customtkinter psutil`
- Optional tools in PATH: `git`, `rclone`, `lazygit`, `pwsh`.

### Installation
1. Clone the repository or copy `script_manager_gui.py`.
2. Run the application:
   ```pwsh
   python script_manager_gui.py
   ```

## 📂 File Structure
- `script_manager_gui.py`: Main application code.
- `script_launcher_config.json`: Automatically generated configuration file for your scripts and settings.
- `script_output/rclone/`: Directory where background rclone logs are stored.

---
*Created with ❤️ by Antigravity*
