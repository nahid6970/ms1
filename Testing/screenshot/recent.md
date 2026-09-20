# 1. Project DNA (Permanent)

Windows screenshot utility built with PyQt6 and Pillow, using a single Qt event loop with modular dialogs for region selection, destination actions, folder management, and lazy OCR. Its goal is to capture a screen region quickly and copy, save, move, open, search, or extract text from it.

# 2. Latest Implementation

- `region_screenshot.py` — Replaced Tkinter/bootstrap flow with PyQt6; added cyberpunk QSS, explicit screenshot action row, “MOVE TO FOLDER”, folder destinations, restart/settings controls, responsive OCR worker, larger centered JetBrainsMono NFP icons, and right-click folder menus for Rename/Color/Icon/Remove.

# 3. Critical Context

- Theme constants and styling follow `C:\@delta\ms1\md\THEME_GUIDE.md`.
- `BASE_DIR = Path(__file__).resolve().parent` keeps `folders.json` relative to the script.
- OCR imports remain lazy and run in `QThread`; EasyOCR is preferred with pytesseract fallback.
- Startup no longer calls `install_deps.bootstrap()`; dependencies must already be installed.
- Action results are represented by `FolderChooser.choice`; selecting a destination folder saves the in-memory crop directly.
- Folder display names are stored as optional `name` fields; renaming does not change the actual filesystem path.

# 4. Pending Task

Run the script interactively and verify region coordinates, multi-monitor/high-DPI behavior, and each action button on the target Windows setup.
