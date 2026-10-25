# PyQt Theme Guide — Material Design

A light, card-based theme with soft gray surroundings, white surfaces, purple actions, and green success feedback. The guide captures a Material-inspired visual direction rather than prescribing a particular Material component library.

## Palette

| Token | Hex | Use |
|---|---|---|
| `MAT_BG` | `#F4F5F7` | Main window |
| `MAT_PANEL` | `#FFFFFF` | Cards and inputs |
| `MAT_PANEL_ALT` | `#E7E9EC` | Raised controls |
| `MAT_TEXT` | `#252A31` | Primary text |
| `MAT_MUTED` | `#6C7580` | Secondary text |
| `MAT_ACCENT` | `#6750A4` | Primary action and selection |
| `MAT_SUCCESS` | `#25856B` | Successful status |
| `MAT_BORDER` | `#D8DDE3` | Borders |

## Visual direction

- Use spacious cards with 10–12 px corners and restrained elevation.
- Use purple for the main action and selected controls; keep status colors semantic.
- Use clear typographic hierarchy, consistent spacing, and obvious focus states.
- Prefer native Qt effects or a Material component library for elevation; QSS alone cannot reproduce all Material behavior.

## PyQt6 QSS starter

```css
QMainWindow, QDialog { background: #F4F5F7; }
QWidget { color: #252A31; font-family: "Segoe UI"; font-size: 10pt; }
QFrame#card, QGroupBox { background: #FFFFFF; border: 1px solid #D8DDE3; border-radius: 10px; }
QGroupBox { margin-top: 13px; padding: 13px 10px 10px; }
QGroupBox::title { color: #6750A4; subcontrol-origin: margin; left: 12px; padding: 0 5px; }
QLineEdit, QComboBox, QSpinBox, QPlainTextEdit, QTextEdit { background: #FFFFFF; color: #252A31; border: 1px solid #D8DDE3; border-radius: 6px; padding: 8px 10px; selection-background-color: #6750A4; selection-color: #FFFFFF; }
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QPlainTextEdit:focus, QTextEdit:focus { border: 1px solid #6750A4; }
QPushButton { background: #FFFFFF; color: #252A31; border: 1px solid #D8DDE3; border-radius: 7px; padding: 9px 15px; font-weight: 600; }
QPushButton:hover { background: #F6F3FC; border-color: #6750A4; }
QPushButton:pressed, QPushButton#primaryAction { background: #6750A4; color: #FFFFFF; border-color: #6750A4; }
QProgressBar { background: #E7E9EC; border: 0; border-radius: 5px; text-align: center; }
QProgressBar::chunk { background: #6750A4; border-radius: 5px; }
```

Set `objectName="card"` on card frames and `objectName="primaryAction"` on the main button. Add shadow effects sparingly so dense utility screens stay clear. Use relative paths, include **⚙ Settings** with an extensible empty `SettingsDialog`, and implement **↺ Restart** with `os.execv(sys.executable, [sys.executable] + sys.argv)`.
