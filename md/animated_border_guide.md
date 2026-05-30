# Implementing Animated Multicolored Borders in PyQt6

This guide explains how to implement dynamic, rotating multicolored borders (cyberpunk style) for frameless or floating window interfaces in PyQt6.

## How It Works
The technique relies on three core concepts:
1. **`QTimer`**: Driving the animation by periodically triggering updates.
2. **`QConicalGradient`**: Creating a color wheel centered on the window.
3. **`paintEvent` Override**: Custom-drawing the border rect on top of the window's existing styling.

---

## Code Breakdown

### 1. Initializing Animation State
In your window's `__init__` method, initialize an offset angle (usually `0.0`) and start a periodic timer that updates the angle and requests a redraw.

```python
from PyQt6.QtCore import QTimer

# Inside __init__:
self.border_offset = 0.0
self.timer = QTimer(self)
self.timer.timeout.connect(self.update_border_animation)
self.timer.start(30) # Redraws at ~33 FPS
```

### 2. Updating the Frame
The timer triggers the update method, which increments the angle offset and tells PyQt to repaint the widget.

```python
def update_border_animation(self):
    # Rotate the gradient offset (3 degrees per frame)
    self.border_offset = (self.border_offset + 3) % 360
    self.update() # Triggers paintEvent
```

### 3. Rendering the Border
Override the `paintEvent` of the window or central widget to perform custom drawing:

```python
from PyQt6.QtGui import QPainter, QColor, QPen, QConicalGradient

def paintEvent(self, event):
    # Paint background & children first
    super().paintEvent(event)
    
    painter = QPainter(self)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    pen_width = 3
    # Adjust rect boundaries inset by half the pen width to prevent edge clipping
    rect = self.rect().adjusted(1, 1, -2, -2)
    
    # Create the color wheel gradient centered in the window
    gradient = QConicalGradient(self.width() / 2.0, self.height() / 2.0, self.border_offset)
    gradient.setColorAt(0.0, QColor("#00F0FF"))    # Cyan
    gradient.setColorAt(0.25, QColor("#FF007F"))   # Magenta
    gradient.setColorAt(0.5, QColor("#FCEE0A"))    # Yellow
    gradient.setColorAt(0.75, QColor("#00FF66"))   # Green
    gradient.setColorAt(1.0, QColor("#00F0FF"))    # Cyan (ends back at start)
    
    # Configure and apply the pen
    pen = QPen(gradient, pen_width)
    painter.setPen(pen)
    painter.drawRect(rect)
```

---

## Copy-Paste Boilerplate Template
Below is a complete, minimal, and self-contained window application using this technique:

```python
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QConicalGradient

class AnimatedBorderWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Configure Frameless Window Settings
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.resize(300, 200)
        
        # Set Window Background (Use dark backgrounds for best color contrast)
        self.setStyleSheet("QMainWindow { background-color: #0d0d0d; }")
        
        # Add Central Widget & Layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Margin should be at least border pen width to prevent content overlap
        layout.setContentsMargins(10, 10, 10, 10)
        
        label = QLabel("ANIMATED BORDER")
        label.setStyleSheet("color: white; font-family: 'Consolas'; font-size: 16pt; font-weight: bold;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        # Setup Animation Timer
        self.border_offset = 0.0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_border_animation)
        self.timer.start(30)
        
    def update_border_animation(self):
        self.border_offset = (self.border_offset + 2) % 360
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        pen_width = 4
        # Inset rect to keep pen entirely within the bounds of the window
        rect = self.rect().adjusted(2, 2, -3, -3)
        
        # Conical gradient centered at widget center
        gradient = QConicalGradient(self.width() / 2.0, self.height() / 2.0, self.border_offset)
        gradient.setColorAt(0.0, QColor("#00F0FF"))
        gradient.setColorAt(0.25, QColor("#FF007F"))
        gradient.setColorAt(0.5, QColor("#FCEE0A"))
        gradient.setColorAt(0.75, QColor("#00FF66"))
        gradient.setColorAt(1.0, QColor("#00F0FF"))
        
        pen = QPen(gradient, pen_width)
        painter.setPen(pen)
        painter.drawRect(rect)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AnimatedBorderWindow()
    window.show()
    sys.exit(app.exec())
```
