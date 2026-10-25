# PyQt Theme Guide — Fluent Dark

A clean Windows-inspired dark theme with neutral gray surfaces and bright cyan-blue actions. Use it for modern utilities that should feel native to a dark desktop environment.

## Palette

| Token | Hex | Use |
|---|---|---|
| `FD_BG` | `#202020` | Main window |
| `FD_PANEL` | `#2B2B2B` | Panels and inputs |
| `FD_PANEL_ALT` | `#393939` | Raised controls |
| `FD_TEXT` | `#F5F5F5` | Primary text |
| `FD_MUTED` | `#AAAAAA` | Secondary text |
| `FD_ACCENT` | `#60CDFF` | Primary action and focus |
| `FD_SUCCESS` | `#6CCB5F` | Successful status |
| `FD_BORDER` | `#454545` | Borders |

## Visual direction

- Use moderate corner radii (6–8 px), restrained outlines, and a clear hierarchy.
- Keep backgrounds neutral; use cyan-blue for interaction and green for positive status.
- Avoid excessive gradients or shadows. Use simple hover and pressed feedback.

## PyQt6 QSS starter

```css
QMainWindow, QDialog { background: #202020; }
QWidget { color: #F5F5F5; font-family: "Segoe UI"; font-size: 10pt; }
QGroupBox { border: 1px solid #454545; border-radius: 7px; margin-top: 12px; padding: 12px 9px 9px; }
QGroupBox::title { color: #60CDFF; subcontrol-origin: margin; left: 10px; padding: 0 5px; }
QLineEdit, QComboBox, QSpinBox, QPlainTextEdit, QTextEdit { background: #2B2B2B; color: #F5F5F5; border: 1px solid #454545; border-radius: 4px; padding: 7px 9px; }
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QPlainTextEdit:focus, QTextEdit:focus { border-color: #60CDFF; }
QPushButton { background: #393939; color: #F5F5F5; border: 1px solid #454545; border-radius: 4px; padding: 8px 13px; }
QPushButton:hover { border-color: #60CDFF; }
QPushButton:pressed, QPushButton#primaryAction { background: #60CDFF; color: #202020; }
QCheckBox::indicator { width: 16px; height: 16px; border: 1px solid #777; border-radius: 3px; background: #2B2B2B; }
QCheckBox::indicator:checked { background: #60CDFF; border-color: #60CDFF; }
```

Set the primary button's `objectName` to `primaryAction`. For closer platform-native behavior, pair QSS with an appropriate Qt style rather than relying on CSS alone. Use relative paths, add **⚙ Settings** with an extensible empty `SettingsDialog`, and implement **↺ Restart** with `os.execv(sys.executable, [sys.executable] + sys.argv)`.
