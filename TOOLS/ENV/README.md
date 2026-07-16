# ⚡ ALIAS & CONTEXT MANAGER v1.0

A cyberpunk-themed, premium PyQt6 GUI tool for managing Windows command aliases and custom right-click context menu entries.

---

## 🚀 Key Features

### 🎯 Command Aliases (Universal System)
* **Write Once, Work Everywhere**: Setup aliases that work seamlessly across **CMD, PowerShell, and Git Bash**.
* **Auto-Setup**: Configures loader scripts and registry keys automatically (`AutoRun` for CMD, profile path for PowerShell, and `.bashrc` for Git Bash).
* **Instant Session Binding**: Apply aliases to the current CMD session dynamically.

### 🎛️ Windows Context Menu Customizer
* **Registry Integration**: Directly manage custom cascading menus, groups, separators, and actions under `HKEY_CURRENT_USER\Software\Classes`.
* **Drag-and-Drop / Reordering**: Move context menu entries Up or Down easily.
* **Auto-Export Pipeline**: All changes (adding, editing, removing, or reordering context items and aliases) are instantly and silently synchronized to `data.json` so your configuration is never lost.

### 🎨 SVG-to-ICO Compiler
* **No File Browse Required**: Paste raw SVG XML code (`<svg ...> ... </svg>`) directly into the dialog box.
* **Under-the-Hood Compilation**: The manager automatically renders and compiles the SVG to a `.ico` file.
* **Local Storage**: Compiled icons are saved under `C:\@delta\ms1\TOOLS\ENV\icon`.
* **Explorer Cache Busting**: Filenames are generated using an MD5 hash of the SVG code (e.g. `LabelName_a8f9c1b2.ico`). This ensures that changes to an icon take effect immediately without being blocked by the Windows Explorer icon cache.
* **Automatic Directory Cleanup**: Whenever an icon is updated, previous versions of the `.ico` file for that command label are automatically purged to prevent clutter.
* **PC Move Protection**: Raw SVG code is saved inside the exported configuration JSON, meaning you can easily restore your setup on any new machine.

### 💡 Interactive Command Help
* Features a built-in guide displaying command templates for:
  * **CMD**: using `/k` to keep terminal windows open or chaining commands with `&&`.
  * **PowerShell / pwsh**: using `-NoExit`, `-WorkingDirectory`, and environment mapping.
  * **Windows Terminal (wt)**: launching dedicated profile tabs at the right directory (`-d "%V"`).

---

## 📂 File Structure

* `env_variable_manager.py`: Core GUI application logic.
* `data.json`: The automatically updated configuration store (holds aliases and context menu data, including raw SVGs).
* `icon/`: Local directory housing all generated `.ico` icon files compiled from SVG inputs.

---

## 🔧 Installation & Usage

### 1. Requirements
Ensure you have Python 3.8+ and PyQt6 installed:
```bash
pip install PyQt6
```

### 2. Launching the App
Run the script directly from your terminal:
```bash
python env_variable_manager.py
```

### 3. Migrating to a New PC
1. Copy the project folder to the new machine.
2. Launch the application.
3. Click the **⚙️ SETTINGS** button at the top-right and select **📥 IMPORT FROM data.json**.
4. The system will automatically recreate the local `icon` folder, compile the SVGs back into `.ico` files, and write all context menu entries and shell aliases to the Windows registry.
