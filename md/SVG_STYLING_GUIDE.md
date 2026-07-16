# 🎨 SVG Styling & Preview Implementation Guide

This guide explains how the interactive **SVG Live Preview and Color Extraction/Styling** feature works, so you can easily implement it in your other PyQt6 projects!

---

## 1. Core Concepts

The SVG styling system works by directly manipulating raw SVG XML code as a string, extracting colors with regular expressions, and re-rendering it using Qt's SVG tools. 

### Key Components:
- **`QTextEdit` / `QPlainTextEdit`**: Holds the raw SVG code.
- **Regex (`re`)**: Finds all Hex colors in the SVG.
- **`QColorDialog`**: Provides an interactive palette for users to pick replacement colors.
- **`QSvgRenderer`**: Takes the modified SVG string and draws it onto a `QPixmap` for preview.

---

## 2. Extracting Colors from SVG

To dynamically find all the colors present in an SVG file, use this regular expression, which matches both 6-character (`#FFFFFF`) and 3-character (`#FFF`) hex codes:

```python
import re

svg_code = "<svg> ... </svg>"
# Find all unique hex colors and sort them by length (to avoid partial replacements)
colors = sorted(list(set(re.findall(r'#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3}', svg_code))), key=len, reverse=True)
```

## 3. Rendering a Live SVG Preview

To show the user what the SVG looks like, you convert the SVG string into a byte array, render it to a transparent `QPixmap`, and display it on a standard `QLabel`.

```python
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import QByteArray, Qt

def generate_preview(svg_string):
    # Initialize a transparent canvas (e.g., 256x256)
    pixmap = QPixmap(256, 256)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    # Render the SVG onto the canvas
    renderer = QSvgRenderer(QByteArray(svg_string.encode('utf-8')))
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    
    return pixmap

# Usage: my_label.setPixmap(generate_preview(current_svg_code))
```

## 4. Replacing a Color

When a user selects a color button and picks a new color via `QColorDialog`, you replace the specific color string in the SVG text and immediately update the preview.

```python
from PyQt6.QtWidgets import QColorDialog
from PyQt6.QtGui import QColor
import re

def replace_color(old_color_hex, current_svg_text):
    # Open color picker dialog starting at the old color
    new_c = QColorDialog.getColor(QColor(old_color_hex), title="Select New Color")
    
    if new_c.isValid():
        new_color_hex = new_c.name().upper() # Gets the #RRGGBB format
        
        # Replace case-insensitively using regex
        pattern = re.compile(re.escape(old_color_hex), re.IGNORECASE)
        updated_svg_text = pattern.sub(new_color_hex, current_svg_text)
        
        return updated_svg_text
    
    return current_svg_text
```

## 5. Complete Boilerplate `QDialog` Structure

Here is a simplified blueprint of how these pieces fit together into a cohesive `QDialog` class. You can copy-paste this into any PyQt6 script and style it with your preferred theme.

```python
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QPlainTextEdit, QScrollArea, QWidget, QColorDialog)
from PyQt6.QtGui import QPixmap, QPainter, QColor
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import QByteArray, Qt, QTimer
import re
from functools import partial

class ReusableSvgEditor(QDialog):
    def __init__(self, initial_svg="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("SVG Editor")
        self.resize(700, 500)
        
        main_layout = QHBoxLayout(self)
        
        # --- LEFT PANEL: Code & Colors ---
        left_layout = QVBoxLayout()
        
        self.text_editor = QPlainTextEdit(initial_svg)
        left_layout.addWidget(QLabel("SVG Code:"))
        left_layout.addWidget(self.text_editor)
        
        # Scroll area for dynamically generated color buttons
        self.color_scroll = QScrollArea()
        self.color_scroll.setFixedHeight(70)
        self.color_container = QWidget()
        self.color_layout = QHBoxLayout(self.color_container)
        self.color_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.color_scroll.setWidget(self.color_container)
        left_layout.addWidget(QLabel("Extracted Colors:"))
        left_layout.addWidget(self.color_scroll)
        
        # --- RIGHT PANEL: Preview ---
        right_layout = QVBoxLayout()
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(QLabel("Live Preview:"))
        right_layout.addWidget(self.preview_label)
        
        # --- ASSEMBLY ---
        main_layout.addLayout(left_layout, stretch=2)
        main_layout.addLayout(right_layout, stretch=1)
        
        # Add a debounced timer so typing doesn't instantly crash/lag the preview
        self.debounce_timer = QTimer(self)
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self.refresh_ui)
        self.text_editor.textChanged.connect(lambda: self.debounce_timer.start(500))
        
        self.refresh_ui()

    def refresh_ui(self):
        svg_code = self.text_editor.toPlainText()
        
        # 1. Update Preview
        if svg_code.strip():
            renderer = QSvgRenderer(QByteArray(svg_code.encode('utf-8')))
            pix = QPixmap(200, 200)
            pix.fill(Qt.GlobalColor.transparent)
            p = QPainter(pix)
            renderer.render(p)
            p.end()
            self.preview_label.setPixmap(pix)
        else:
            self.preview_label.setPixmap(QPixmap())
            
        # 2. Re-extract Colors
        while self.color_layout.count():
            item = self.color_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        colors = sorted(list(set(re.findall(r'#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3}', svg_code))), key=len, reverse=True)
        
        for c in colors:
            btn = QPushButton()
            btn.setFixedSize(30, 30)
            btn.setStyleSheet(f"background-color: {c}; border: 1px solid gray;")
            btn.clicked.connect(partial(self.trigger_color_replace, c))
            self.color_layout.addWidget(btn)

    def trigger_color_replace(self, old_color):
        new_color = QColorDialog.getColor(QColor(old_color), self, "Pick Replacement")
        if new_color.isValid():
            updated_svg = re.sub(
                re.compile(re.escape(old_color), re.IGNORECASE), 
                new_color.name().upper(), 
                self.text_editor.toPlainText()
            )
            self.text_editor.setPlainText(updated_svg)
            self.refresh_ui()
```
