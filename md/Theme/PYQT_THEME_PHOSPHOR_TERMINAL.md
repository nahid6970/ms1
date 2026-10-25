# PyQt Theme Guide — Phosphor Terminal

A retro terminal-inspired theme with deep green-black surfaces and phosphor green. Use it for command runners, developer utilities, and log viewers where the terminal character is part of the experience.

## Palette

| Token | Hex | Use |
|---|---|---|
| `PT_BG` | `#050B08` | Main window |
| `PT_PANEL` | `#0B1510` | Cards and fields |
| `PT_TEXT` | `#C3F6D0` | Primary text |
| `PT_MUTED` | `#6E9F7C` | Hints and secondary labels |
| `PT_ACCENT` | `#70F59B` | Primary action, focus, selection |
| `PT_LIME` | `#B8FF68` | Success and progress highlight |
| `PT_BORDER` | `#1C4229` | Outlines and dividers |

## Visual direction

- Use square or nearly square corners, thin green borders, and compact spacing.
- Use Consolas or another readable monospace for terminal-oriented labels and logs. Long-form help text may use a sans-serif for readability.
- Use phosphor green for the active command and lime sparingly for completed states.
- Optional scanline or glow decoration should be subtle and must not obscure text or rely on animation to convey state.

## PyQt6 QSS starter

```css
QMainWindow, QDialog { background: #050B08; }
QWidget { color: #C3F6D0; font-family: "Consolas", monospace; font-size: 10pt; }
QGroupBox { border: 1px solid #1C4229; margin-top: 11px; padding: 11px 8px 8px; }
QGroupBox::title { color: #70F59B; subcontrol-origin: margin; left: 10px; padding: 0 4px; }
QLineEdit, QComboBox, QSpinBox, QPlainTextEdit, QTextEdit {
    background: #0B1510; color: #70F59B; border: 1px solid #1C4229;
    padding: 7px 8px; selection-background-color: #70F59B; selection-color: #050B08;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QPlainTextEdit:focus, QTextEdit:focus { border-color: #70F59B; }
QPushButton {
    background: #0B1510; color: #C3F6D0; border: 1px solid #1C4229;
    padding: 8px 12px; font-weight: bold;
}
QPushButton:hover { color: #70F59B; border-color: #70F59B; }
QPushButton:pressed { background: #70F59B; color: #050B08; }
QPushButton#primaryAction { background: #70F59B; color: #050B08; border-color: #70F59B; }
QProgressBar { background: #0B1510; border: 1px solid #1C4229; text-align: center; }
QProgressBar::chunk { background: #70F59B; }
QScrollBar:vertical { background: #050B08; width: 9px; }
QScrollBar::handle:vertical { background: #28633B; min-height: 22px; }
QPushButton#restartAction { background: transparent; color: #70F59B; border: 1px solid #70F59B; border-radius: 1px; padding: 8px 12px; font-weight: 600; }
QPushButton#restartAction:hover { background: #70F59B; color: #050B08; border-color: #70F59B; }
QPushButton#restartAction:pressed { background: #102017; color: #70F59B; }

```

Set the Restart button's `objectName` to `restartAction` to use this outlined accent treatment; it fills with the theme accent on hover.

## Implementation notes

- Set `objectName="primaryAction"` on the main command button.
- Keep keyboard focus visible and ensure the small monospace text remains readable at typical desktop scaling.
- Use paths relative to the script directory for files and settings.
- Include a **⚙ SETTINGS** button and an extensible `SettingsDialog` (empty by default).
- Include **↺ RESTART**, implemented with `os.execv(sys.executable, [sys.executable] + sys.argv)`.
