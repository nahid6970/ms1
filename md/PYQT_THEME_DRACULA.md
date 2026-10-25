# PyQt Theme Guide — Dracula

A dark violet theme with vivid green success states. The palette is expressive and high contrast, making it a strong fit for developer tools and creative utilities.

## Palette

| Token | Hex | Use |
|---|---|---|
| `DRACULA_BG` | `#282A36` | Main window |
| `DRACULA_PANEL` | `#343746` | Panels and inputs |
| `DRACULA_PANEL_ALT` | `#44475A` | Raised controls and borders |
| `DRACULA_TEXT` | `#F8F8F2` | Primary text |
| `DRACULA_MUTED` | `#A6A8B8` | Secondary text |
| `DRACULA_ACCENT` | `#BD93F9` | Primary action and selection |
| `DRACULA_SUCCESS` | `#50FA7B` | Successful status |

## Visual direction

- Use charcoal-purple surfaces, 6–8 px radii, and violet for selected controls.
- Keep green reserved for success and completed states; use dedicated colors for warnings and errors.
- Use Segoe UI for standard controls and monospace for code or terminal output.

## PyQt6 QSS starter

```css
QMainWindow, QDialog { background: #282A36; }
QWidget { color: #F8F8F2; font-family: "Segoe UI"; font-size: 10pt; }
QGroupBox { border: 1px solid #44475A; border-radius: 7px; margin-top: 12px; padding: 12px 9px 9px; }
QGroupBox::title { color: #BD93F9; subcontrol-origin: margin; left: 10px; padding: 0 5px; }
QLineEdit, QComboBox, QSpinBox, QPlainTextEdit, QTextEdit { background: #343746; color: #F8F8F2; border: 1px solid #44475A; border-radius: 5px; padding: 7px 9px; selection-background-color: #BD93F9; }
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QPlainTextEdit:focus, QTextEdit:focus { border-color: #BD93F9; }
QPushButton { background: #44475A; color: #F8F8F2; border: 1px solid #44475A; border-radius: 5px; padding: 8px 12px; }
QPushButton:hover { border-color: #BD93F9; }
QPushButton:pressed, QPushButton#primaryAction { background: #BD93F9; color: #282A36; }
QProgressBar { background: #44475A; border: 0; border-radius: 4px; text-align: center; }
QProgressBar::chunk { background: #BD93F9; border-radius: 4px; }
```

Set the primary button's `objectName` to `primaryAction`. Use green only for positive status and keep focus indicators clear. Use relative paths, provide **⚙ Settings** with an extensible empty `SettingsDialog`, and implement **↺ Restart** with `os.execv(sys.executable, [sys.executable] + sys.argv)`.
