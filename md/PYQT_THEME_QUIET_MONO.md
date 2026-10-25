# PyQt Theme Guide — Quiet Mono

A restrained low-glare theme for tools that stay open all day. Neutral charcoal surfaces, soft text, and a pale green accent keep the interface calm while preserving clear focus and action states.

## Palette

| Token | Hex | Use |
|---|---|---|
| `QM_BG` | `#121416` | Main window |
| `QM_PANEL` | `#1B1E20` | Cards and fields |
| `QM_TEXT` | `#F0F1EF` | Primary text |
| `QM_MUTED` | `#949B9D` | Hints and secondary labels |
| `QM_ACCENT` | `#B7D9C7` | Primary actions, focus, selection |
| `QM_HIGHLIGHT` | `#D6D8D2` | Secondary emphasis |
| `QM_BORDER` | `#353A3B` | Outlines and dividers |

## Visual direction

- Keep saturation low and avoid decorative gradients or glow.
- Use 6–8 px corner radii, compact controls, and consistent alignment.
- Use the green accent selectively for focused controls and the primary action.
- Use a legible sans-serif for controls and monospace only for code or logs.

## PyQt6 QSS starter

```css
QMainWindow, QDialog { background: #121416; }
QWidget { color: #F0F1EF; font-family: "Segoe UI"; font-size: 10pt; }
QGroupBox { border: 1px solid #353A3B; border-radius: 7px; margin-top: 12px; padding: 12px 9px 9px; }
QGroupBox::title { color: #B7D9C7; subcontrol-origin: margin; left: 11px; padding: 0 5px; }
QLineEdit, QComboBox, QSpinBox, QPlainTextEdit, QTextEdit {
    background: #1B1E20; color: #F0F1EF; border: 1px solid #353A3B;
    border-radius: 5px; padding: 7px 9px; selection-background-color: #B7D9C7; selection-color: #121416;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QPlainTextEdit:focus, QTextEdit:focus { border-color: #B7D9C7; }
QPushButton {
    background: #24282A; color: #F0F1EF; border: 1px solid #353A3B;
    border-radius: 5px; padding: 7px 12px; font-weight: 600;
}
QPushButton:hover { border-color: #B7D9C7; }
QPushButton:pressed { background: #B7D9C7; color: #121416; }
QPushButton#primaryAction { background: #B7D9C7; color: #121416; border-color: #B7D9C7; }
QCheckBox::indicator { width: 15px; height: 15px; background: #1B1E20; border: 1px solid #555D5F; border-radius: 3px; }
QCheckBox::indicator:checked { background: #B7D9C7; border-color: #B7D9C7; }
QScrollBar:vertical { background: #121416; width: 9px; }
QScrollBar::handle:vertical { background: #4A5052; min-height: 22px; border-radius: 4px; }
```

## Implementation notes

- Assign `objectName="primaryAction"` to the main button.
- Do not rely on color alone for state; pair the accent with labels, icons, or shape changes.
- Use paths relative to the script directory for files and settings.
- Include a **⚙ Settings** button and an extensible `SettingsDialog` (empty by default).
- Include **↺ Restart**, implemented with `os.execv(sys.executable, [sys.executable] + sys.argv)`.
