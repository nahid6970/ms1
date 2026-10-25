# PyQt Theme Guide — Fluent Light

A bright Windows-inspired palette with clean white-gray surfaces and blue actions. It works well for productivity and settings-heavy utilities where crisp readability matters.

## Palette

| Token | Hex | Use |
|---|---|---|
| `FL_BG` | `#FAFAFA` | Main window |
| `FL_PANEL` | `#F0F0F0` | Panels and inputs |
| `FL_PANEL_ALT` | `#E5E5E5` | Raised controls |
| `FL_TEXT` | `#1A1A1A` | Primary text |
| `FL_MUTED` | `#666666` | Secondary text |
| `FL_ACCENT` | `#0067C0` | Primary action and focus |
| `FL_SUCCESS` | `#107C10` | Successful status |
| `FL_BORDER` | `#D5D5D5` | Borders |

## Visual direction

- Use light neutral surfaces, thin gray outlines, and 4–7 px corners.
- Keep text near black and secondary labels dark enough to remain readable.
- Use blue for actions and focus, green for success, and distinct semantic colors for alerts.

## PyQt6 QSS starter

```css
QMainWindow, QDialog { background: #FAFAFA; }
QWidget { color: #1A1A1A; font-family: "Segoe UI"; font-size: 10pt; }
QGroupBox { border: 1px solid #D5D5D5; border-radius: 6px; margin-top: 12px; padding: 12px 9px 9px; }
QGroupBox::title { color: #0067C0; subcontrol-origin: margin; left: 10px; padding: 0 5px; }
QLineEdit, QComboBox, QSpinBox, QPlainTextEdit, QTextEdit { background: #FFFFFF; color: #1A1A1A; border: 1px solid #C8C8C8; border-radius: 4px; padding: 7px 9px; selection-background-color: #0067C0; selection-color: #FFFFFF; }
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QPlainTextEdit:focus, QTextEdit:focus { border: 1px solid #0067C0; }
QPushButton { background: #E5E5E5; color: #1A1A1A; border: 1px solid #D5D5D5; border-radius: 4px; padding: 8px 13px; }
QPushButton:hover { background: #DADADA; border-color: #0067C0; }
QPushButton:pressed, QPushButton#primaryAction { background: #0067C0; color: #FFFFFF; border-color: #0067C0; }
QProgressBar { background: #E5E5E5; border: 0; border-radius: 4px; text-align: center; }
QProgressBar::chunk { background: #0067C0; border-radius: 4px; }
```

Set the primary button's `objectName` to `primaryAction`. Test text contrast at typical scaling and retain visible keyboard focus. Use relative paths, include **⚙ Settings** with an extensible empty `SettingsDialog`, and implement **↺ Restart** with `os.execv(sys.executable, [sys.executable] + sys.argv)`.
