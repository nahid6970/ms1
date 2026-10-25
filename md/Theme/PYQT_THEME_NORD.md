# PyQt Theme Guide — Nord

A cool arctic blue-gray theme with cyan accents and muted evergreen success states. It provides a calm dark interface with slightly softer contrast than pure charcoal themes.

## Palette

| Token | Hex | Use |
|---|---|---|
| `NORD_BG` | `#2E3440` | Main window |
| `NORD_PANEL` | `#3B4252` | Panels and inputs |
| `NORD_PANEL_ALT` | `#434C5E` | Raised controls |
| `NORD_TEXT` | `#ECEFF4` | Primary text |
| `NORD_MUTED` | `#A7B0BF` | Secondary text |
| `NORD_ACCENT` | `#88C0D0` | Primary action and focus |
| `NORD_SUCCESS` | `#A3BE8C` | Successful status |
| `NORD_BORDER` | `#4C566A` | Borders |

## Visual direction

- Use dark blue-gray surfaces and 6–8 px corner radii.
- Use cyan for selection, links, and the main action. Use muted green for healthy status.
- Favor subtle borders and spacing over high-intensity shadows or saturated decoration.
- Use readable sans-serif controls and monospace for logs or code only.

## PyQt6 QSS starter

```css
QMainWindow, QDialog { background: #2E3440; }
QWidget { color: #ECEFF4; font-family: "Segoe UI"; font-size: 10pt; }
QGroupBox { border: 1px solid #4C566A; border-radius: 7px; margin-top: 12px; padding: 12px 9px 9px; }
QGroupBox::title { color: #88C0D0; subcontrol-origin: margin; left: 10px; padding: 0 5px; }
QLineEdit, QComboBox, QSpinBox, QPlainTextEdit, QTextEdit { background: #3B4252; color: #ECEFF4; border: 1px solid #4C566A; border-radius: 5px; padding: 7px 9px; selection-background-color: #88C0D0; selection-color: #2E3440; }
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QPlainTextEdit:focus, QTextEdit:focus { border-color: #88C0D0; }
QPushButton { background: #434C5E; color: #ECEFF4; border: 1px solid #4C566A; border-radius: 5px; padding: 8px 12px; }
QPushButton:hover { border-color: #88C0D0; }
QPushButton:pressed, QPushButton#primaryAction { background: #88C0D0; color: #2E3440; }
QProgressBar { background: #434C5E; border: 0; border-radius: 4px; text-align: center; }
QProgressBar::chunk { background: #88C0D0; border-radius: 4px; }
QPushButton#restartAction { background: transparent; color: #88C0D0; border: 1px solid #88C0D0; border-radius: 5px; padding: 8px 12px; font-weight: 600; }
QPushButton#restartAction:hover { background: #88C0D0; color: #2E3440; border-color: #88C0D0; }
QPushButton#restartAction:pressed { background: #434C5E; color: #88C0D0; }

```

Set the Restart button's `objectName` to `restartAction` to use this outlined accent treatment; it fills with the theme accent on hover.

Set the primary button's `objectName` to `primaryAction`. Keep success green separate from cyan focus, and use semantic colors for errors. Use relative paths, include **⚙ Settings** with an extensible empty `SettingsDialog`, and implement **↺ Restart** with `os.execv(sys.executable, [sys.executable] + sys.argv)`.
