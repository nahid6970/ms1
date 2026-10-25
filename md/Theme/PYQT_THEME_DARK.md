# PyQt Theme Guide — Dark

A balanced charcoal desktop theme with blue actions and green success states. Use it as an understated default for general-purpose PyQt utilities.

## Palette

| Token | Hex | Use |
|---|---|---|
| `DARK_BG` | `#17191E` | Main window |
| `DARK_PANEL` | `#22252C` | Panels and inputs |
| `DARK_PANEL_ALT` | `#30343D` | Buttons and raised surfaces |
| `DARK_TEXT` | `#E5E7EB` | Primary text |
| `DARK_MUTED` | `#9DA3AD` | Secondary text |
| `DARK_ACCENT` | `#4EA1FF` | Actions and focus |
| `DARK_SUCCESS` | `#67C587` | Successful status |
| `DARK_BORDER` | `#383D47` | Borders |

## Visual direction

- Use 6–8 px rounded corners, clear panel separation, and moderate spacing.
- Keep the blue accent for primary actions, selected items, and focus. Use green for positive status.
- Use Segoe UI or another readable system sans-serif. Reserve monospace for code and logs.

## PyQt6 QSS starter

```css
QMainWindow, QDialog { background: #17191E; }
QWidget { color: #E5E7EB; font-family: "Segoe UI"; font-size: 10pt; }
QGroupBox { border: 1px solid #383D47; border-radius: 7px; margin-top: 12px; padding: 12px 9px 9px; }
QGroupBox::title { color: #4EA1FF; subcontrol-origin: margin; left: 10px; padding: 0 5px; }
QLineEdit, QComboBox, QSpinBox, QPlainTextEdit, QTextEdit {
    background: #22252C; color: #E5E7EB; border: 1px solid #383D47;
    border-radius: 5px; padding: 7px 9px; selection-background-color: #4EA1FF;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QPlainTextEdit:focus, QTextEdit:focus { border-color: #4EA1FF; }
QPushButton { background: #30343D; color: #E5E7EB; border: 1px solid #383D47; border-radius: 5px; padding: 8px 12px; }
QPushButton:hover { border-color: #4EA1FF; }
QPushButton:pressed, QPushButton#primaryAction { background: #4EA1FF; color: #17191E; }
QProgressBar { background: #30343D; border: 0; border-radius: 4px; text-align: center; }
QProgressBar::chunk { background: #4EA1FF; border-radius: 4px; }
QPushButton#restartAction { background: transparent; color: #4EA1FF; border: 1px solid #4EA1FF; border-radius: 5px; padding: 8px 12px; font-weight: 600; }
QPushButton#restartAction:hover { background: #4EA1FF; color: #17191E; border-color: #4EA1FF; }
QPushButton#restartAction:pressed { background: #30343D; color: #4EA1FF; }

```

Set the Restart button's `objectName` to `restartAction` to use this outlined accent treatment; it fills with the theme accent on hover.

Set the primary button's `objectName` to `primaryAction`. Keep focus states visible and use semantic colors for warnings and errors. For reusable app boilerplate, use paths relative to the script directory, include **⚙ Settings** with an extensible empty `SettingsDialog`, and implement **↺ Restart** with `os.execv(sys.executable, [sys.executable] + sys.argv)`.
