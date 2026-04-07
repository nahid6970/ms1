# Cyberpunk UI Theme Guide

A reusable styling reference for PyQt6 applications with a dark, neon-accented cyberpunk aesthetic.

---

## Color Palette

```python
# Core Colors
CP_BG = "#050505"           # Main Background (almost black)
CP_PANEL = "#111111"        # Panel/Card Background
CP_DIM = "#3a3a3a"          # Dimmed/Inactive elements, borders

# Text Colors
CP_TEXT = "#E0E0E0"         # Primary text
CP_SUBTEXT = "#808080"      # Secondary/muted text

# Accent Colors
CP_YELLOW = "#FCEE0A"       # Primary accent (Cyber Yellow)
CP_CYAN = "#00F0FF"         # Secondary accent (Neon Cyan)
CP_RED = "#FF003C"          # Error/Delete/Danger
CP_GREEN = "#00FF00"        # Success/Confirm
CP_MAGENTA = "#FF00FF"      # Alternate accent
CP_ORANGE = "#FFA500"       # Warning/Highlight
```

---

## Typography

- **Primary Font:** `Consolas` (monospace)
- **Fallback:** Any monospace font
- **Weights:** Normal (400), Bold (700)
- **Sizes:**
  - Headers: 16px bold
  - Section titles: 11-12px bold
  - Body text: 10-11px
  - Labels/Status: 8-9px
  - Timestamps: 7px

```python
from PyQt6.QtGui import QFont

# Header
QFont("Consolas", 16, QFont.Weight.Bold)

# Section Title
QFont("Consolas", 11, QFont.Weight.Bold)

# Body/Button
QFont("Consolas", 10, QFont.Weight.Bold)

# Small Labels
QFont("Consolas", 8)
```

---

## Button Styles

### Solid Button (Primary Action)
```python
QPushButton {
    background-color: #FCEE0A;
    color: #050505;
    border: none;
    padding: 5px 15px;
    font-family: 'Consolas';
    font-weight: bold;
}
QPushButton:hover {
    background-color: #050505;
    color: #FCEE0A;
    border: 1px solid #FCEE0A;
}
```

### Outlined Button (Secondary Action)
```python
QPushButton {
    background-color: transparent;
    color: #FCEE0A;
    border: 2px solid #FCEE0A;
    padding: 5px 15px;
    font-family: 'Consolas';
    font-weight: bold;
}
QPushButton:hover {
    background-color: #FCEE0A;
    color: #050505;
}
```

### Danger Button
```python
QPushButton {
    background-color: transparent;
    color: #FF003C;
    border: 2px solid #FF003C;
    padding: 5px 15px;
    font-family: 'Consolas';
}
QPushButton:hover {
    background-color: #FF003C;
    color: #050505;
}
```

---

## Input Fields

```python
QLineEdit {
    background-color: #111111;
    color: #FCEE0A;
    border: 1px solid #3a3a3a;
    padding: 8px;
    font-family: 'Consolas';
}
QLineEdit:focus {
    border: 1px solid #00F0FF;
}
QLineEdit::placeholder {
    color: #808080;
}
```

---

## Dropdown / ComboBox

```python
QComboBox {
    background-color: transparent;
    color: #00F0FF;
    border: 1px solid #00F0FF;
    padding: 5px 15px;
    font-family: 'Consolas';
    font-weight: bold;
}
QComboBox:hover {
    background-color: #00F0FF;
    color: #050505;
}
QComboBox::drop-down {
    border: 0px;
    width: 0px;
}
QComboBox QAbstractItemView {
    background-color: #111111;
    color: #E0E0E0;
    selection-background-color: #00F0FF;
    selection-color: #050505;
    border: 1px solid #00F0FF;
    outline: none;
}
```

---

## Checkbox

```python
QCheckBox {
    color: #E0E0E0;
    font-family: 'Consolas';
    font-size: 11px;
    spacing: 10px;
    padding: 10px;
    border: 1px solid #111111;
    background: #111111;
}
QCheckBox::indicator {
    width: 14px;
    height: 14px;
    border: 1px solid #3a3a3a;
    background: #050505;
}
QCheckBox::indicator:checked {
    background: #FCEE0A;
    border: 1px solid #FCEE0A;
}
QCheckBox::indicator:hover {
    border: 1px solid #00F0FF;
}
QCheckBox:hover {
    border: 1px solid #3a3a3a;
    background: #1a1a25;
}
```

---

## Context Menu

```python
QMenu {
    background-color: #050505;
    color: #E0E0E0;
    border: 1px solid #00F0FF;
    font-family: 'Consolas';
}
QMenu::item {
    padding: 6px 25px;
    background-color: transparent;
}
QMenu::item:selected {
    background-color: #00F0FF;
    color: #050505;
}
```

---

## Scrollbar

```python
QScrollBar:vertical {
    background: #050505;
    width: 8px;
}
QScrollBar::handle:vertical {
    background: #3a3a3a;
}
QScrollBar::handle:vertical:hover {
    background: #00F0FF;
}
```

---

## Cards / List Items

```python
/* Item card with left accent border */
QFrame {
    background-color: #0f0f15;
    border-left: 3px solid #FCEE0A;  /* Active state */
    border-bottom: 1px solid #111111;
}
QFrame:hover {
    background-color: #1a1a25;
}

/* Inactive state: change border-left to #3a3a3a */
```

---

## Status Toggle Button

```python
/* Active State */
QPushButton {
    background-color: #FCEE0A;
    color: #050505;
    border: 1px solid #FCEE0A;
    border-radius: 0px;
}

/* Inactive State */
QPushButton {
    background-color: transparent;
    color: #808080;
    border: 1px solid #3a3a3a;
    border-radius: 0px;
}
QPushButton:hover {
    border: 1px solid #00F0FF;
    color: #00F0FF;
}
```

---

## Dialog Windows

```python
QDialog {
    background-color: #050505;
    border: 1px solid #3a3a3a;
}
QDialog QLabel {
    color: #00F0FF;
    font-family: 'Consolas';
    font-weight: bold;
    font-size: 12px;
}
```

---

## Headers & Labels

```python
/* Main Title */
QLabel {
    color: #FCEE0A;
    font-family: 'Consolas';
    font-size: 16px;
    font-weight: bold;
    letter-spacing: 2px;
}

/* Section Header */
QLabel {
    color: #808080;
    font-family: 'Consolas';
    font-size: 11px;
    font-weight: bold;
    padding-bottom: 5px;
    border-bottom: 2px solid #3a3a3a;
}

/* Status Text */
QLabel {
    color: #00F0FF;
    font-family: 'Consolas';
    font-size: 10px;
}
```

---

## Splitter

```python
QSplitter::handle {
    background-color: #3a3a3a;
}
QSplitter::handle:hover {
    background-color: #00F0FF;
}
```

---

## Design Principles

1. **Dark Foundation:** Near-black backgrounds (#050505, #111111)
2. **Neon Accents:** Yellow for primary, Cyan for secondary, Red for danger
3. **Monospace Typography:** Consolas throughout for that terminal/hacker feel
4. **Sharp Edges:** No border-radius (0px) for that angular cyberpunk look
5. **Hover States:** Invert colors on hover (bg becomes text color, text becomes bg)
6. **Left Border Accents:** Use colored left borders to indicate state/importance
7. **Uppercase Text:** Headers and labels in uppercase for impact
8. **Minimal Padding:** Tight, efficient layouts
9. **Status Indicators:** Text-based ("ON"/"OFF", "ACTV") rather than icons

---

## Naming Conventions

Use tech/system-inspired terminology:
- "EXECUTE PROTOCOL" instead of "Run"
- "PURGE ENTRY" instead of "Delete"
- "EDIT CONFIG" instead of "Edit"
- "SCAN_SYS" instead of "Scan System"
- "UPLOAD" instead of "Save"
- "ABORT" instead of "Cancel"
- "IDENTITY // NAME" instead of "Name"
- "SOURCE // PATH" instead of "Path"

---

## Quick Start Template

```python
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QFont

# Palette
CP_BG = "#050505"
CP_PANEL = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN = "#00F0FF"
CP_RED = "#FF003C"
CP_DIM = "#3a3a3a"
CP_TEXT = "#E0E0E0"
CP_SUBTEXT = "#808080"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"QMainWindow {{ background-color: {CP_BG}; }}")
        # ... your UI setup

if __name__ == "__main__":
    app = QApplication([])
    app.setStyle("Fusion")  # Important for consistent styling
    window = MainWindow()
    window.show()
    app.exec()
```

---

*Generated from startup.py cyberpunk theme implementation*
