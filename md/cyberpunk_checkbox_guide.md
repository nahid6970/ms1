# Cyberpunk Checkbox Guide (PyQt6)

This note captures the square checkbox style used in `Duplicate Image Finder` so it can be reused in other PyQt6 projects.

## Goal

Checkboxes should look like this:

- square indicator
- dark background
- dim border when unchecked
- yellow border when checked
- yellow check mark only

## 1. Reusable Check SVG

Create a small SVG file for the check mark. Keep it next to your script or in an assets folder.

Example file: `cyberpunk_check.svg`

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">
    <path d="M3 8.5 L6.2 11.5 L13 4.5"
          fill="none"
          stroke="#FCEE0A"
          stroke-width="2.2"
          stroke-linecap="square"
          stroke-linejoin="miter"/>
</svg>
```

## 2. Helper Function

Use a helper so the SVG is written automatically if missing.

```python
import os

CP_YELLOW = "#FCEE0A"

def app_dir() -> str:
    return os.path.dirname(os.path.abspath(__file__))

def checkbox_check_icon_path() -> str:
    return os.path.join(app_dir(), "cyberpunk_check.svg")

def ensure_checkbox_check_icon() -> str:
    path = checkbox_check_icon_path()
    svg_markup = f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">
        <path d="M3 8.5 L6.2 11.5 L13 4.5" fill="none" stroke="{CP_YELLOW}" stroke-width="2.2" stroke-linecap="square" stroke-linejoin="miter"/>
    </svg>
    """
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(svg_markup)
    return path.replace("\\", "/")
```

## 3. QSS Style

Apply this in your main stylesheet.

```python
checkbox_icon = ensure_checkbox_check_icon()

app.setStyleSheet(f"""
    QCheckBox {{
        spacing: 0px;
        color: #E0E0E0;
    }}
    QCheckBox::indicator {{
        width: 16px;
        height: 16px;
        border: 1px solid #3a3a3a;
        background: #111111;
    }}
    QCheckBox::indicator:unchecked {{
        background: #111111;
        border: 1px solid #3a3a3a;
    }}
    QCheckBox::indicator:checked {{
        background: #111111;
        border: 1px solid #FCEE0A;
        image: url({checkbox_icon});
    }}
""")
```

## 4. Plain QCheckBox Usage

For normal forms or dialogs:

```python
from PyQt6.QtWidgets import QCheckBox

checkbox = QCheckBox("ENABLE SCAN")
checkbox.setChecked(True)
```

## 5. Using Inside a QTableWidget

Native table checkboxes usually keep platform styling. If you want the custom look inside a table, use a real `QCheckBox` widget inside a cell.

```python
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QCheckBox, QHBoxLayout, QTableWidget, QWidget

table = QTableWidget(0, 2)

row = table.rowCount()
table.insertRow(row)

container = QWidget()
layout = QHBoxLayout(container)
layout.setContentsMargins(0, 0, 0, 0)
layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

checkbox = QCheckBox()
checkbox.setChecked(True)
layout.addWidget(checkbox)

table.setCellWidget(row, 0, container)
```

## 6. Reading State From Table Rows

```python
from PyQt6.QtWidgets import QCheckBox

container = table.cellWidget(row, 0)
checkbox = container.findChild(QCheckBox) if container is not None else None

if checkbox and checkbox.isChecked():
    print("enabled")
```

## 7. Why This Approach

- `QTableWidgetItem` check states often keep native styling
- `QCheckBox` widgets inside cells follow your stylesheet
- SVG keeps the check sharp at different scales

## 8. Current Palette Reference

```python
CP_PANEL = "#111111"
CP_YELLOW = "#FCEE0A"
CP_DIM = "#3a3a3a"
CP_TEXT = "#E0E0E0"
```

