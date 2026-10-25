# PyQt Theme Guide — Aurora Glass

A calm, layered dark theme for dashboards, utility apps, and script managers. It uses cool blue surfaces with violet actions and mint highlights. The glass effect is suggested through layered surfaces and subtle gradients; standard Qt widgets remain readable and practical.

## Palette

| Token | Hex | Use |
|---|---|---|
| `AG_BG` | `#0B101D` | Main window |
| `AG_PANEL` | `#121C2E` | Cards, inputs, menus |
| `AG_TEXT` | `#E5F4FF` | Primary text |
| `AG_MUTED` | `#8294AC` | Hints and secondary labels |
| `AG_ACCENT` | `#A78BFA` | Primary action, selection |
| `AG_MINT` | `#46E2CF` | Focus, links, success |
| `AG_BORDER` | `#25364B` | Separators and outlines |

## Visual direction

- Use 12–14 px corner radii on cards and controls, with consistent spacing.
- Distinguish elevation with slightly lighter panels, thin borders, and restrained shadows. Avoid strong blur effects that reduce text clarity.
- Use violet for the main action and mint for focus or successful status. Keep warnings and errors semantically distinct.
- Use Segoe UI or another clear sans-serif; reserve monospace for logs and code.

## PyQt6 QSS starter

```css
QMainWindow, QDialog { background: #0B101D; }
QWidget { color: #E5F4FF; font-family: "Segoe UI"; font-size: 10pt; }
QFrame, QGroupBox {
    background: #121C2E; border: 1px solid #25364B; border-radius: 12px;
}
QLineEdit, QComboBox, QSpinBox, QPlainTextEdit, QTextEdit {
    background: #121C2E; color: #E5F4FF; border: 1px solid #25364B;
    border-radius: 8px; padding: 7px 9px; selection-background-color: #A78BFA;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus,
QPlainTextEdit:focus, QTextEdit:focus { border: 1px solid #46E2CF; }
QPushButton {
    background: #1B2940; color: #E5F4FF; border: 1px solid #25364B;
    border-radius: 8px; padding: 8px 13px; font-weight: 600;
}
QPushButton:hover { border-color: #A78BFA; }
QPushButton:pressed { background: #A78BFA; color: #0B101D; }
QPushButton#primaryAction { background: #A78BFA; color: #0B101D; border-color: #A78BFA; }
QCheckBox::indicator { width: 15px; height: 15px; }
QCheckBox::indicator:unchecked { background: #121C2E; border: 1px solid #8294AC; border-radius: 4px; }
QCheckBox::indicator:checked { background: #46E2CF; border: 1px solid #46E2CF; border-radius: 4px; }
QScrollBar:vertical { background: #0B101D; width: 10px; margin: 2px; }
QScrollBar::handle:vertical { background: #435571; min-height: 24px; border-radius: 5px; }
QPushButton#restartAction { background: transparent; color: #A78BFA; border: 1px solid #A78BFA; border-radius: 8px; padding: 8px 12px; font-weight: 600; }
QPushButton#restartAction:hover { background: #A78BFA; color: #0B101D; border-color: #A78BFA; }
QPushButton#restartAction:pressed { background: #1B2940; color: #A78BFA; }

```

Set the Restart button's `objectName` to `restartAction` to use this outlined accent treatment; it fills with the theme accent on hover.

## Implementation notes

- Set the primary button's `objectName` to `primaryAction` before applying the stylesheet.
- For translucent glass panels, use a `QGraphicsDropShadowEffect` sparingly; QSS does not provide reliable backdrop blur.
- Keep contrast and focus visible when adding disabled, hover, and selected states.
- Use paths relative to the script directory for files and settings, not the current working directory.
- Include a **⚙ Settings** button and an extensible `SettingsDialog` (empty by default).
- Include **↺ Restart**, implemented with `os.execv(sys.executable, [sys.executable] + sys.argv)`.
