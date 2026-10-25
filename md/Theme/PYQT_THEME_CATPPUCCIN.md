# PyQt Theme Guide — Catppuccin Mocha

A soothing dark palette with cool lavender text, mauve actions, and pastel green success states. This guide uses the Mocha variant shown in the smoke test.

## Palette

| Token | Hex | Use |
|---|---|---|
| `CAT_BG` | `#1E1E2E` | Main window |
| `CAT_PANEL` | `#252538` | Panels and inputs |
| `CAT_PANEL_ALT` | `#313149` | Raised controls |
| `CAT_TEXT` | `#CDD6F4` | Primary text |
| `CAT_MUTED` | `#9399B2` | Secondary text |
| `CAT_ACCENT` | `#CBA6F7` | Primary action and selection |
| `CAT_SUCCESS` | `#A6E3A1` | Successful status |
| `CAT_BORDER` | `#3B3D55` | Borders |

## Visual direction

- Use soft 9–11 px corners and gentle surface contrast.
- Use mauve as the main action color and green for completed or healthy states.
- Keep text sizes comfortable; use accent colors selectively so the pastel palette stays calm.

## PyQt6 QSS starter

```css
QMainWindow, QDialog { background: #1E1E2E; }
QWidget { color: #CDD6F4; font-family: "Segoe UI"; font-size: 10pt; }
QGroupBox { border: 1px solid #3B3D55; border-radius: 10px; margin-top: 12px; padding: 12px 9px 9px; }
QGroupBox::title { color: #CBA6F7; subcontrol-origin: margin; left: 11px; padding: 0 5px; }
QLineEdit, QComboBox, QSpinBox, QPlainTextEdit, QTextEdit { background: #252538; color: #CDD6F4; border: 1px solid #3B3D55; border-radius: 7px; padding: 7px 9px; selection-background-color: #CBA6F7; selection-color: #1E1E2E; }
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QPlainTextEdit:focus, QTextEdit:focus { border-color: #CBA6F7; }
QPushButton { background: #313149; color: #CDD6F4; border: 1px solid #3B3D55; border-radius: 7px; padding: 8px 12px; }
QPushButton:hover { border-color: #CBA6F7; }
QPushButton:pressed, QPushButton#primaryAction { background: #CBA6F7; color: #1E1E2E; }
QProgressBar { background: #313149; border: 0; border-radius: 5px; text-align: center; }
QProgressBar::chunk { background: #CBA6F7; border-radius: 5px; }
QPushButton#restartAction { background: transparent; color: #CBA6F7; border: 1px solid #CBA6F7; border-radius: 7px; padding: 8px 12px; font-weight: 600; }
QPushButton#restartAction:hover { background: #CBA6F7; color: #1E1E2E; border-color: #CBA6F7; }
QPushButton#restartAction:pressed { background: #313149; color: #CBA6F7; }

```

Set the Restart button's `objectName` to `restartAction` to use this outlined accent treatment; it fills with the theme accent on hover.

Set the primary button's `objectName` to `primaryAction`. Keep success green and warnings/errors semantically distinct. Use relative paths, include **⚙ Settings** with an extensible empty `SettingsDialog`, and implement **↺ Restart** with `os.execv(sys.executable, [sys.executable] + sys.argv)`.
