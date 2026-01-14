# 🚀 Antigravity Script Manager

A powerful, premium Python-based GUI application designed to centralize your workflow. It combines script management, Git repository monitoring, Rclone sync status, and real-time system performance metrics into a single, sleek, frameless dashboard.

## ✨ Key Features

### 🖥️ Advanced Script Launcher
- **Organization**: Group your scripts into **Folders** with intuitive breadcrumb navigation.
- **Cut & Paste**: Right-click any item to **Cut** it, then navigate to a folder and use the **Paste** button (appears in the Add dialog) to move it there.
- **Move Out**: When inside a folder, use the context menu's **"Move Up / Out"** option to move items back to the parent.
- **Drag & Drop**: Easily reorder your buttons and folders by dragging them across the grid.
- **PowerShell Ready**: 
    - Automatically detects and prefers `pwsh` (PowerShell Core) over legacy `powershell`.
    - Uses robust `-Command` syntax for better compatibility with complex scripts.
    - Scripts run from their own directory, ensuring relative paths work correctly.
- **Terminal Control**:
    - **Hide Terminal**: Run scripts silently in the background (Python, PowerShell, etc.).
    - **No Exit Terminal**: Keep the console window open after execution to view errors or output.

### 📝 Inline Script Editor
- **Integrated Code Panel**: Write multi-line `cmd`, `pwsh`, or `powershell` scripts directly within the application.
- **Dual Modes**: Toggle between executing a linked **File Path** or running your **Inline Script**.
- **Smart Layout**: The "Edit" dialog automatically adapts:
    - **Scripts**: Shows a side-by-side split view with the settings on the left and code editor on the right.
    - **Folders**: Shows a compact, focused settings dialog.

### 🎨 Premium Customization
- **Visual Editor**: A beautiful, borderless "Edit / Stylize" dialog to tweak every aspect of your buttons.
- **Typography control**: Change font family, font size and toggle **Bold** / *Italic* styles.
- **Shape & Colors**:
    - Custom **Corner Radius** for rounded or sharp buttons.
    - Adjustable **Border Width** and color.
    - Full control over button and text colors for both normal and hover states.
- **Per-Folder Grid Settings**: Customize grid columns and item dimensions for each folder independently.
- **Advanced Bindings**: Assign custom commands to **Ctrl + Left Click** and **Ctrl + Right Click** on any button for power-user multitasking.
- **Themed Dialogs**: All input prompts (add folder, add script) use the same dark theme and custom fonts as the main window.

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
- **Global Settings**:
    - **Window Behavior**: Toggle "Always on Top" instantly.
    - **Grid Layout**: Adjust columns and default font size.
    - **Widget Toggles**: Enable/disable GitHub, Rclone, or System Stats widgets.
- **Portable**: Configuration is saved to `script_launcher_config.json` relative to the script, making it fully portable.

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
