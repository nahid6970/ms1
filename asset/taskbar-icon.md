# Taskbar Icon + Process Name (PyQt6)

## Boilerplate

```python
import ctypes
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon, QPixmap, QPainter
from PyQt6.QtCore import Qt, QByteArray
from PyQt6.QtSvg import QSvgRenderer

# Set unique process ID — groups taskbar icon correctly
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('yourname.APPNAME.version')

def make_app_icon():
    svg = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
        <!-- your svg here -->
    </svg>'
    renderer = QSvgRenderer(QByteArray(svg))
    pix = QPixmap(64, 64)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    renderer.render(painter)
    painter.end()
    return QIcon(pix)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(make_app_icon())
```

## Notes

| Thing | What it does |
|---|---|
| `SetCurrentProcessExplicitAppUserModelID` | Makes Windows use the correct icon in the taskbar |
| `app.setWindowIcon(...)` | Sets icon on all windows |
| `window.setWindowIcon(...)` | Sets icon on a specific window only |
| AppUserModelID string | Must be unique — format: `author.appname.version` |

## SVG Tips

- Keep viewBox `0 0 64 64`
- Use `fill`/`stroke` attributes directly — Qt SVG renderer has limited CSS support
- `pix.fill(Qt.GlobalColor.transparent)` for transparent background
