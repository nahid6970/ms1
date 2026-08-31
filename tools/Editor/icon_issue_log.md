# Windows Executable & Icon Troubleshooting Log (CyberEditor)

This document outlines the issues encountered with the `CyberEditor` executable compilation, file associations, and taskbar icons, along with the steps taken to fix them.

---

## 1. File Association & Broken Registry Paths

### **The Issue:**
* Initially, the executable (`CyberEditor.exe`) was run and registered from its original folder.
* After moving the executable to another folder (e.g. the Desktop), attempting to open files with it through the Windows "Open With" dialog showed the application as "unknown" or failed entirely.
* This occurs because Windows caches the absolute path of the executable in the registry under `Classes\Applications\CyberEditor.exe`. When the file is moved, Windows Explorer ignores the new path when you browse for it and attempts to call the old, non-existent path.
* In the Python code, the association script (`do_assoc`) also failed to wrap the executable path in quotes, causing issues if the path contained space characters.

### **The Solution & Fixes:**
* **Quoting Fix**: Updated `cyber_editor.py` registry association methods to wrap `sys.executable` in quotes:
  ```python
  exe_path = f'"{sys.executable}"' if getattr(sys, 'frozen', False) else f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'
  ```
* **Handling Binary Files**: Fixed a bug where opening non-text files (like `.png` images) resulted in silent decoding crashes (`UnicodeDecodeError`), making the app open as "unknown" or blank. Added a fallback to load binary files with `errors='replace'` and present readable warning text in the editor.
* **Explorer Registry Workaround**: Windows caches the executable name aggressively. To force Windows Explorer to associate with the new path, you can rename the `.exe` slightly (e.g. `CyberEditor_v2.exe`) which forces Windows to register the new location.

---

## 2. Low Quality or Missing Executable Icon

### **The Issue:**
* The icon compiled into the executable appeared pixelated, low quality, or failed to display in Windows Explorer.
* This was due to:
  1. The `.ico` file containing low-resolution frames rendered without vector antialiasing.
  2. The `.ico` sizes in Pillow being ordered incorrectly (Windows Explorer requires the largest resolution first).
  3. The PyInstaller `.spec` file passing the icon as a list `icon=['icon.ico']` instead of a string `icon='icon.ico'`, which is unsupported on Windows PE compilers and fails silently.

### **The Solution & Fixes:**
* **PyInstaller Syntax**: Changed the spec configuration to:
  ```python
  icon='icon.ico'
  ```
* **High-Quality Rasterization**: Created a PyQt6 conversion script that rasterizes `icon.svg` onto a high-res `512x512` canvas using rendering hints:
  * `Antialiasing`
  * `TextAntialiasing`
  * `SmoothPixmapTransform`
* **Windows-Compliant Packaging**: Saved the multi-size `.ico` with sizes arranged from largest to smallest `[256, 128, 64, 48, 32, 16]`. Sub-images are packaged in Windows-compliant BMP formats (since Windows Explorer fails to read PNG-encoded ICO sub-images for smaller sizes).

---

## 3. Missing Taskbar Icon

### **The Issue:**
* While the icon appeared correctly in Windows Explorer, launching the app showed a generic/blank taskbar icon.
* This is a known limitation with Python-based GUIs on Windows, where the taskbar manager fails to associate the window handles with the parent executable, often grouping them under the generic python host process.

### **The Solution & Fixes:**
* **Explicit AppUserModelID**: Added ctypes logic to the main entry point to register an explicit App ID on Windows, forcing the taskbar to group the windows under the correct executable:
  ```python
  import ctypes
  ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("cyberpunk.cyber_editor.1.0")
  ```
* **Qt PNG Icon Bundling**: Bundled `icon.png` in PyInstaller's Virtual File System (`datas`) and changed the main window icon loader to bind directly to the PNG:
  ```python
  icon_path = os.path.join(sys._MEIPASS, "icon.png") if getattr(sys, 'frozen', False) else "icon.png"
  self.setWindowIcon(QIcon(icon_path))
  ```
  *(Qt natively decodes and displays PNG window/taskbar icons more reliably on Windows runtime than ICO headers).*
