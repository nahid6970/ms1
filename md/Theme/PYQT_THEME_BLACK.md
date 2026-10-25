# PyQt Theme Guide — Black

A near-black theme with white emphasis and minimal decoration. It suits OLED screens and users who want a stark, low-distraction interface.

## Palette

| Token | Hex | Use |
|---|---|---|
| `BLACK_BG` | `#050505` | Main window |
| `BLACK_PANEL` | `#111111` | Panels and inputs |
| `BLACK_PANEL_ALT` | `#202020` | Raised controls |
| `BLACK_TEXT` | `#F4F4F4` | Primary text |
| `BLACK_MUTED` | `#A3A3A3` | Secondary text |
| `BLACK_ACCENT` | `#FFFFFF` | Primary actions and focus |
| `BLACK_SUCCESS` | `#BDBDBD` | Neutral positive status |
| `BLACK_BORDER` | `#303030` | Borders |

## Visual direction

- Use square or lightly rounded corners (0–2 px) and thin borders.
- Separate controls with spacing and surface tones; avoid glow effects.
- Since the accent is white, distinguish selected, pressed, and success states with shape, labels, or icons as well as color.

## PyQt6 QSS starter

```css
QMainWindow, QDialog { background: #050505; }
QWidget { color: #F4F4F4; font-family: "Segoe UI"; font-size: 10pt; }
QGroupBox { border: 1px solid #303030; margin-top: 11px; padding: 11px 8px 8px; }
QGroupBox::title { color: #FFFFFF; subcontrol-origin: margin; left: 9px; padding: 0 4px; }
QLineEdit, QComboBox, QSpinBox, QPlainTextEdit, QTextEdit { background: #111111; color: #F4F4F4; border: 1px solid #303030; padding: 7px 8px; selection-background-color: #FFFFFF; selection-color: #050505; }
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QPlainTextEdit:focus, QTextEdit:focus { border-color: #FFFFFF; }
QPushButton { background: #202020; color: #F4F4F4; border: 1px solid #303030; padding: 8px 12px; font-weight: 600; }
QPushButton:hover { border-color: #FFFFFF; }
QPushButton:pressed, QPushButton#primaryAction { background: #FFFFFF; color: #050505; }
QScrollBar:vertical { background: #050505; width: 9px; }
QScrollBar::handle:vertical { background: #555555; min-height: 22px; }
QPushButton#restartAction { background: transparent; color: #FFFFFF; border: 1px solid #FFFFFF; border-radius: 1px; padding: 8px 12px; font-weight: 600; }
QPushButton#restartAction:hover { background: #FFFFFF; color: #050505; border-color: #FFFFFF; }
QPushButton#restartAction:pressed { background: #202020; color: #FFFFFF; }

```

Set the Restart button's `objectName` to `restartAction` to use this outlined accent treatment; it fills with the theme accent on hover.

Set the primary button's `objectName` to `primaryAction`. Ensure text and focus remain legible at common display scaling. Use paths relative to the script directory, include **⚙ Settings** with an extensible empty `SettingsDialog`, and implement **↺ Restart** with `os.execv(sys.executable, [sys.executable] + sys.argv)`.
