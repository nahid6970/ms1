# 1. Project DNA (Permanent)

Windows screenshot utility built with PyQt6 and Pillow, using a single Qt event loop with modular dialogs for region selection, destination actions, folder management, and lazy OCR. Its goal is to capture a screen region quickly and copy, save, move, open, search, or extract text from it.

# 2. Latest Implementation

- `region_screenshot.py` — Replaced Tkinter/bootstrap flow with PyQt6; added cyberpunk QSS, explicit screenshot action row, “MOVE TO FOLDER”, a four-column destination grid with native default folder icons, restart/settings controls, responsive OCR worker, and right-click folder menus for Rename/Color/Remove.

# 3. Critical Context

- Theme constants and styling follow `C:\@delta\ms1\md\THEME_GUIDE.md`.
- `BASE_DIR = Path(__file__).resolve().parent` keeps `folders.json` relative to the script.
- OCR imports remain lazy and run in `QThread`; EasyOCR is preferred with pytesseract fallback.
- Startup no longer calls `install_deps.bootstrap()`; dependencies must already be installed.
- Action results are represented by `FolderChooser.choice`; selecting a destination folder saves the in-memory crop directly.
- Folder display names are stored as optional `name` fields; renaming does not change the actual filesystem path.
- Destination card colors now appear as consistent card borders; all destination icons intentionally use the native Windows folder icon.
- Native folder icons are color-tinted with the saved color, and icon/name spacing is compact.
- Destination cards use borderless dark rounded panels with compact icon/caption spacing; folder colors remain on the icon and caption.
- Google Lens copies a durable Windows CF_DIB bitmap before opening `https://lens.google.com/`, allowing manual Ctrl+V on the Lens page.
- The Copy action publishes both CF_DIB and CF_HDROP, so image editors get pixels and Windows Explorer can paste a PNG file.

# 4. Pending Task

Run the script interactively and verify region coordinates, multi-monitor/high-DPI behavior, and each action button on the target Windows setup.
