# PyQt Theme Guide — Deep Ocean

A focused blue dark theme with crisp cyan-green highlights. It suits monitoring tools, network utilities, and dashboards that need a clear primary action and readable status information.

## Palette

| Token | Hex | Use |
|---|---|---|
| `DO_BG` | `#071625` | Main window |
| `DO_PANEL` | `#0D2236` | Cards and fields |
| `DO_TEXT` | `#E7F3FF` | Primary text |
| `DO_MUTED` | `#829BB1` | Hints and secondary labels |
| `DO_ACCENT` | `#4DB8FF` | Primary action, focus, selection |
| `DO_MINT` | `#65E1D2` | Success and secondary highlights |
| `DO_BORDER` | `#20415B` | Outlines and dividers |

## Visual direction

- Use 7–9 px corner radii and strong alignment; let status data provide visual interest.
- Keep surfaces dark navy and use cyan-blue for the main action. Use mint for healthy or completed states.
- Use visible focus borders and clear progress indicators for monitoring workflows.
- Use Segoe UI for interface text and Consolas for logs, addresses, and code.

## PyQt6 QSS starter

```css
QMainWindow, QDialog { background: #071625; }
QWidget { color: #E7F3FF; font-family: "Segoe UI"; font-size: 10pt; }
QGroupBox { border: 1px solid #20415B; border-radius: 8px; margin-top: 12px; padding: 12px 9px 9px; }
QGroupBox::title { color: #65E1D2; subcontrol-origin: margin; left: 11px; padding: 0 5px; }
QLineEdit, QComboBox, QSpinBox, QPlainTextEdit, QTextEdit {
    background: #0D2236; color: #E7F3FF; border: 1px solid #20415B;
    border-radius: 6px; padding: 7px 9px; selection-background-color: #4DB8FF; selection-color: #071625;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QPlainTextEdit:focus, QTextEdit:focus { border-color: #4DB8FF; }
QPushButton {
    background: #12304A; color: #E7F3FF; border: 1px solid #20415B;
    border-radius: 6px; padding: 8px 13px; font-weight: 600;
}
QPushButton:hover { border-color: #4DB8FF; }
QPushButton:pressed { background: #4DB8FF; color: #071625; }
QPushButton#primaryAction { background: #4DB8FF; color: #071625; border-color: #4DB8FF; }
QProgressBar { background: #0D2236; border: 1px solid #20415B; border-radius: 4px; text-align: center; }
QProgressBar::chunk { background: #65E1D2; border-radius: 3px; }
QScrollBar:vertical { background: #071625; width: 10px; }
QScrollBar::handle:vertical { background: #2D5D7D; min-height: 24px; border-radius: 5px; }
```

## Implementation notes

- Assign `objectName="primaryAction"` to the main button.
- Use mint for positive status and dedicated semantic colors for errors and warnings.
- Use paths relative to the script directory for files and settings.
- Include a **⚙ Settings** button and an extensible `SettingsDialog` (empty by default).
- Include **↺ Restart**, implemented with `os.execv(sys.executable, [sys.executable] + sys.argv)`.
