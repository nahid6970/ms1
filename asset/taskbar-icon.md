# Taskbar Icon + Process Name (PyQt6)

## Minimal Setup

```python
import ctypes
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt, QByteArray
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import QPainter  # only if needed

# 1. Set unique process/app ID (groups taskbar correctly)
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('yourname.APPNAME.version')

# 2. SVG → QIcon
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

# 3. Apply
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(make_app_icon())
```

---

## Notes

| Thing | What it does |
|---|---|
| `SetCurrentProcessExplicitAppUserModelID` | Makes Windows treat the app as its own taskbar group with the right icon |
| `app.setWindowIcon(...)` | Sets icon on all windows of the app |
| `window.setWindowIcon(...)` | Sets icon on a specific window only |
| AppUserModelID string | Must be unique — use format `author.appname.version` |

---

## SVG Tips

- Keep viewBox `0 0 64 64` for clean rendering at taskbar size
- Use `fill` colors directly in SVG (no CSS classes — Qt SVG renderer has limited CSS support)
- Transparent background: `pix.fill(Qt.GlobalColor.transparent)` before rendering
- Test your SVG at small sizes (16px, 32px) — complex paths get muddy

---

## Quick SVG Snippets

**Rocket**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="10" fill="#050505"/>
  <path d="M32 6 C22 6 14 18 14 30 L14 38 L20 44 L20 52 L26 52 L26 46 L38 46 L38 52 L44 52 L44 44 L50 38 L50 30 C50 18 42 6 32 6Z" fill="#FCEE0A"/>
  <circle cx="32" cy="26" r="6" fill="#050505"/>
  <path d="M20 44 L16 54 L26 50Z" fill="#FF003C"/>
  <path d="M44 44 L48 54 L38 50Z" fill="#FF003C"/>
  <circle cx="32" cy="26" r="3" fill="#00F0FF"/>
</svg>
```

**Terminal `>`**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="10" fill="#050505"/>
  <polyline points="14,20 34,32 14,44" fill="none" stroke="#FCEE0A" stroke-width="5" stroke-linejoin="round" stroke-linecap="round"/>
  <line x1="36" y1="44" x2="52" y2="44" stroke="#00F0FF" stroke-width="5" stroke-linecap="round"/>
</svg>
```

**Gear**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="10" fill="#050505"/>
  <circle cx="32" cy="32" r="10" fill="none" stroke="#FCEE0A" stroke-width="4"/>
  <circle cx="32" cy="32" r="4" fill="#00F0FF"/>
  <path d="M32 8 L34 16 L30 16Z M32 56 L34 48 L30 48Z M8 32 L16 34 L16 30Z M56 32 L48 34 L48 30Z M14 14 L20 20 L17 23Z M50 50 L44 44 L47 41Z M50 14 L44 20 L47 23Z M14 50 L20 44 L17 41Z" fill="#FCEE0A"/>
</svg>
```
