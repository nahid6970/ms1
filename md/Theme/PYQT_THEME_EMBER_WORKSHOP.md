# PyQt Theme Guide — Ember Workshop

A warm, tactile dark theme for hands-on utilities. Deep brown surfaces and copper-orange actions make the interface feel like a focused workshop without sacrificing the clarity expected of a desktop tool.

## Palette

| Token | Hex | Use |
|---|---|---|
| `EW_BG` | `#1B1513` | Main window |
| `EW_PANEL` | `#27201D` | Cards and fields |
| `EW_TEXT` | `#F5E9DC` | Primary text |
| `EW_MUTED` | `#B09B8D` | Hints and secondary labels |
| `EW_ACCENT` | `#FF9A62` | Primary actions and focus |
| `EW_GOLD` | `#F2D492` | Secondary highlight |
| `EW_BORDER` | `#49362D` | Outlines and dividers |

## Visual direction

- Use 8–10 px corner radii, warm borders, and moderate control padding.
- Keep panels close in brightness; use borders and spacing to define groups rather than heavy shadows.
- Reserve copper for actions and focus. Use gold for progress, highlights, or selected navigation.
- Use Segoe UI for interface text and Consolas for logs or command output.

## PyQt6 QSS starter

```css
QMainWindow, QDialog { background: #1B1513; }
QWidget { color: #F5E9DC; font-family: "Segoe UI"; font-size: 10pt; }
QGroupBox { border: 1px solid #49362D; border-radius: 9px; margin-top: 12px; padding: 12px 9px 9px; }
QGroupBox::title { color: #F2D492; subcontrol-origin: margin; left: 12px; padding: 0 5px; }
QLineEdit, QComboBox, QSpinBox, QPlainTextEdit, QTextEdit {
    background: #27201D; color: #F5E9DC; border: 1px solid #49362D;
    border-radius: 6px; padding: 7px 9px; selection-background-color: #FF9A62;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QPlainTextEdit:focus, QTextEdit:focus { border-color: #FF9A62; }
QPushButton {
    background: #342720; color: #F5E9DC; border: 1px solid #604536;
    border-radius: 6px; padding: 8px 13px; font-weight: 600;
}
QPushButton:hover { background: #3C2B22; border-color: #FF9A62; }
QPushButton:pressed { background: #FF9A62; color: #1B1513; }
QPushButton#primaryAction { background: #FF9A62; color: #1B1513; border-color: #FF9A62; }
QProgressBar { background: #27201D; border: 1px solid #49362D; border-radius: 4px; text-align: center; }
QProgressBar::chunk { background: #F2D492; border-radius: 3px; }
QScrollBar:vertical { background: #1B1513; width: 10px; }
QScrollBar::handle:vertical { background: #75513E; min-height: 24px; border-radius: 5px; }
QPushButton#restartAction { background: transparent; color: #FF9A62; border: 1px solid #FF9A62; border-radius: 6px; padding: 8px 12px; font-weight: 600; }
QPushButton#restartAction:hover { background: #FF9A62; color: #1B1513; border-color: #FF9A62; }
QPushButton#restartAction:pressed { background: #342720; color: #FF9A62; }

```

Set the Restart button's `objectName` to `restartAction` to use this outlined accent treatment; it fills with the theme accent on hover.

## Implementation notes

- Set `objectName="primaryAction"` on the main action button.
- Keep error and warning colors distinct from the warm orange accent.
- Use paths relative to the script directory for files and settings.
- Include a **⚙ Settings** button and an extensible `SettingsDialog` (empty by default).
- Include **↺ Restart**, implemented with `os.execv(sys.executable, [sys.executable] + sys.argv)`.
