# Using an SVG as a PyQt6 app and taskbar icon

This project uses `rss-svgrepo-com.svg` as the application icon. In a PyQt6 desktop app, set the icon on both the `QApplication` and the main window. The application icon supplies the app-wide default, while the window icon makes the choice explicit for the main window and its taskbar entry.

## 1. Keep the icon with the app

Place the SVG in a stable location in the project. This project keeps it beside `main.py`:

```text
my_app/
├── main.py
└── app-icon.svg
```

Build the path from the Python file's directory rather than the current working directory. That way the icon can still be found when the app is launched from a shortcut or another directory.

```python
import os

APP_DIR = os.path.dirname(os.path.abspath(__file__))
APP_ICON_FILE = os.path.join(APP_DIR, "app-icon.svg")
```

## 2. Set the application and main-window icons

Import `QIcon`, then set the icon in the entry point and in the main window constructor:

```python
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(APP_ICON_FILE))
        # Set up the rest of the window here.

def main():
    app = QApplication([])
    app.setWindowIcon(QIcon(APP_ICON_FILE))
    window = MainWindow()
    window.show()
    app.exec()
```

In this project, the same two calls are in `MyRSSApp.__init__` and `main()` in `main.py`; `APP_ICON_FILE` points at `rss-svgrepo-com.svg`.

## 3. Notes for other apps

- Use an absolute path derived from `__file__` so launching from a different working directory does not break icon loading.
- Keep the SVG file alongside the installed app, or include it in the app's bundled data files when packaging. A path that works from the source tree may need adjustment in a frozen build.
- SVG support depends on the Qt installation having its SVG image support available. If the icon does not appear in a packaged app or on a particular platform, convert the SVG to PNG or ICO and load that file with `QIcon` instead.
- For Windows shortcuts or a packaged executable's own Explorer icon, configure an `.ico` in the shortcut or packaging tool as well. `setWindowIcon()` controls the running Qt window/taskbar icon; it does not change the executable's embedded icon.
