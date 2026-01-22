# Cyberpunk UI Theme Guide

This document outlines the visual style, color palette, and widget stylesheets used in `script_manager_gui_qt.py`. Use this guide to bootstrap new PyQt6 applications with the same Cyberpunk aesthetic.

## 1. Color Palette

Define these constants at the top of your layout file.

```python
# CYBERPUNK THEME PALETTE
CP_BG = "#050505"           # Main Window Background
CP_PANEL = "#111111"        # Panel/Input Background
CP_YELLOW = "#FCEE0A"       # Accent: Yellow
CP_CYAN = "#00F0FF"         # Accent: Cyan
CP_RED = "#FF003C"          # Accent: Red
CP_GREEN = "#00ff21"        # Accent: Green
CP_ORANGE = "#ff934b"       # Accent: Orange
CP_DIM = "#3a3a3a"          # Dimmed/Borders/Inactive
CP_TEXT = "#E0E0E0"         # Primary Text
CP_SUBTEXT = "#808080"      # Secondary Text
```

## 2. Fonts

*   **Primary Font:** `Consolas`
*   **Fallback:** Monospace

## 3. Widget Stylesheets (QSS)

### Global Window & Dialog
Apply this to `QMainWindow` or `QDialog`.

```css
QMainWindow, QDialog {
    background-color: #050505; /* CP_BG */
}
QWidget {
    color: #E0E0E0; /* CP_TEXT */
    font-family: 'Consolas';
    font-size: 10pt;
}
```

### Input Fields (LineEdit, SpinBox, ComboBox, TextEdit)
Gives a dark panel look with cyan text and dim borders.

```css
QLineEdit, QSpinBox, QComboBox, QPlainTextEdit, QTextEdit {
    background-color: #111111; /* CP_PANEL */
    color: #00F0FF;            /* CP_CYAN */
    border: 1px solid #3a3a3a; /* CP_DIM */
    padding: 4px;
    selection-background-color: #00F0FF; /* CP_CYAN */
    selection-color: #000000;
}

QLineEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 1px solid #00F0FF; /* CP_CYAN */
}

QSpinBox::up-button, QSpinBox::down-button {
    width: 0px; 
    border: none; /* Hidden spinners for clean look */
}
```

### Buttons (Standard)
Dark gray buttons that highlight yellow on hover.

```css
QPushButton {
    background-color: #3a3a3a; /* CP_DIM */
    border: 1px solid #3a3a3a;
    color: white;
    padding: 6px 12px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #2a2a2a;
    border: 1px solid #FCEE0A; /* CP_YELLOW */
    color: #FCEE0A;
}

QPushButton:pressed {
    background-color: #FCEE0A;
    color: black;
}
```

### Group Boxes
Styled with a top-left aligned title and dim borders.

```css
QGroupBox {
    border: 1px solid #3a3a3a; /* CP_DIM */
    margin-top: 10px;
    padding-top: 10px;
    font-weight: bold;
    color: #FCEE0A; /* CP_YELLOW */
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
}
```

### Checkboxes
Custom square styling.

```css
QCheckBox {
    spacing: 8px;
    color: #E0E0E0;
}

QCheckBox::indicator {
    width: 14px;
    height: 14px;
    border: 1px solid #3a3a3a; /* CP_DIM */
    background: #111111;       /* CP_PANEL */
}

QCheckBox::indicator:checked {
    background: #FCEE0A;       /* CP_YELLOW */
    border-color: #FCEE0A;
}
```

### Context Menus
Dark menus with cyan highlights.

```css
QMenu {
    background-color: #111111; /* CP_PANEL */
    color: #E0E0E0;            /* CP_TEXT */
    border: 1px solid #00F0FF; /* CP_CYAN */
}

QMenu::item:selected {
    background-color: #00F0FF; /* CP_CYAN */
    color: #050505;            /* CP_BG */
}
```

### Scroll Area
Transparent and frameless to blend into the background.

```css
QScrollArea {
    background: transparent;
    border: none;
}
```

## 4. Custom Component: "CyberButton"

For the main grid buttons, the theme uses a dynamic `CyberButton` class. Here is the core logic for reproducing that specific look:

**Key Properties:**
*   **Font:** Consolas, Bold.
*   **Cursor:** PointingHand.
*   **HTML Support:** Text is rendered using a `QTextDocument` to support `<br>` tags and custom positioning.

**Dynamic Stylesheet Template:**
```python
# Assuming variables: bg_color, text_color, hover_bg, hover_text, border_color
style = f"""
    QPushButton {{
        background-color: {bg_color};
        color: {text_color};
        border: 1px solid {border_color};
        padding: 10px;
        border-radius: 0px; /* Sharp corners preferred */
    }}
    QPushButton:hover {{
        background-color: {hover_bg};
        color: {hover_text};
        border: 1px solid {border_color};
    }}
"""
button.setStyleSheet(style)
```

## 5. Boilerplate Starter Script

Copy this to start a new project with the theme pre-applied.

```python
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QLabel, QPushButton, QLineEdit, QGroupBox, QFormLayout)
from PyQt6.QtCore import Qt

# PALETTE
CP_BG = "#050505"
CP_PANEL = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN = "#00F0FF"
CP_DIM = "#3a3a3a"
CP_TEXT = "#E0E0E0"

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cyberpunk App Template")
        self.resize(800, 600)
        
        # Apply Global Theme
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            
            QLineEdit {{
                background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px;
            }}
            QLineEdit:focus {{ border: 1px solid {CP_CYAN}; }}
            
            QPushButton {{
                background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 6px 12px; font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW};
            }}
            
            QGroupBox {{
                border: 1px solid {CP_DIM}; margin-top: 10px; padding-top: 10px; font-weight: bold; color: {CP_YELLOW};
            }}
            QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }}
        """)

        # Layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Example Controls
        grp = QGroupBox("USER INPUT")
        form = QFormLayout()
        form.addRow("Username:", QLineEdit())
        form.addRow("Command:", QLineEdit())
        grp.setLayout(form)
        
        btn = QPushButton("EXECUTE")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout.addWidget(QLabel("SYSTEM READY..."))
        layout.addWidget(grp)
        layout.addWidget(btn)
        layout.addStretch()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())
```
