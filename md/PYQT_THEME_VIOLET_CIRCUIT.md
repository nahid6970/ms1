# PyQt Theme Guide — Violet Circuit

A vivid night theme for creative technical tools. Electric violet gives primary controls personality while mint marks focus and live status. The result is expressive without returning to a full neon cyberpunk palette.

## Palette

| Token | Hex | Use |
|---|---|---|
| `VC_BG` | `#100C1B` | Main window |
| `VC_PANEL` | `#1B142A` | Cards and fields |
| `VC_TEXT` | `#F2EAFF` | Primary text |
| `VC_MUTED` | `#A398B8` | Hints and secondary labels |
| `VC_ACCENT` | `#C084FC` | Primary action, selection |
| `VC_MINT` | `#74E6D4` | Focus and success |
| `VC_BORDER` | `#3C2C55` | Outlines and dividers |

## Visual direction

- Use 10–12 px corner radii, with a subtle brighter top edge or restrained shadow on key panels.
- Keep the background nearly black-purple and panels visibly separated from it.
- Violet is for primary actions and selected items; mint is for focus and positive status.
- Use a clean sans-serif for controls; use monospace sparingly for terminal snippets.

## PyQt6 QSS starter

```css
QMainWindow, QDialog { background: #100C1B; }
QWidget { color: #F2EAFF; font-family: "Segoe UI"; font-size: 10pt; }
QGroupBox { border: 1px solid #3C2C55; border-radius: 11px; margin-top: 12px; padding: 12px 9px 9px; }
QGroupBox::title { color: #C084FC; subcontrol-origin: margin; left: 12px; padding: 0 5px; }
QLineEdit, QComboBox, QSpinBox, QPlainTextEdit, QTextEdit {
    background: #1B142A; color: #F2EAFF; border: 1px solid #3C2C55;
    border-radius: 8px; padding: 7px 9px; selection-background-color: #C084FC; selection-color: #100C1B;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QPlainTextEdit:focus, QTextEdit:focus { border-color: #74E6D4; }
QPushButton {
    background: #261B38; color: #F2EAFF; border: 1px solid #3C2C55;
    border-radius: 8px; padding: 8px 13px; font-weight: 600;
}
QPushButton:hover { border-color: #C084FC; }
QPushButton:pressed { background: #C084FC; color: #100C1B; }
QPushButton#primaryAction { background: #C084FC; color: #100C1B; border-color: #C084FC; }
QCheckBox::indicator { width: 15px; height: 15px; background: #1B142A; border: 1px solid #66527D; border-radius: 4px; }
QCheckBox::indicator:checked { background: #74E6D4; border-color: #74E6D4; }
QScrollBar:vertical { background: #100C1B; width: 10px; }
QScrollBar::handle:vertical { background: #594278; min-height: 24px; border-radius: 5px; }
```

## Implementation notes

- Set `objectName="primaryAction"` on the main action button.
- Avoid using both accent colors at full strength in the same control; keep each state easy to parse.
- Use paths relative to the script directory for files and settings.
- Include a **⚙ Settings** button and an extensible `SettingsDialog` (empty by default).
- Include **↺ Restart**, implemented with `os.execv(sys.executable, [sys.executable] + sys.argv)`.
