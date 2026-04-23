import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QColor

# PROFESSIONAL PALETTE
BG_COLOR = "#FFFFFF"
BORDER_COLOR = "#E0E0E0"
PRIMARY_COLOR = "#0078D4"  # Enterprise Blue
TEXT_COLOR = "#201F1E"
SECONDARY_TEXT = "#605E5C"
BTN_HOVER = "#005A9E"

class TaskCompletePopup(QWidget):
    def __init__(self):
        super().__init__()
        
        # Window Flags: Frameless and Always on Top
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Central Layout
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(self.layout)
        
        # Main Container
        self.container = QWidget()
        self.container.setObjectName("Container")
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(30, 30, 30, 30)
        self.layout.addWidget(self.container)
        
        # Styling
        self.setStyleSheet(f"""
            QWidget#Container {{
                background-color: {BG_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
            }}
            QLabel {{
                color: {TEXT_COLOR};
                font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;
                font-size: 14pt;
                font-weight: 400;
            }}
            QPushButton {{
                background-color: {PRIMARY_COLOR};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 24px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 10pt;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {BTN_HOVER};
            }}
            QPushButton:pressed {{
                background-color: #004578;
            }}
        """)
        
        # Subtle Shadow Effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)
        
        # Message Label
        self.label = QLabel("Task Completed Successfully")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.container_layout.addWidget(self.label)
        
        # Spacer
        self.container_layout.addSpacing(20)
        
        # Close Button
        self.close_btn = QPushButton("Dismiss")
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.clicked.connect(self.close)
        self.container_layout.addWidget(self.close_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Center the window on screen
        self.adjustSize()
        self.center()
        
    def center(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # Allow dragging the frameless window
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if hasattr(self, 'oldPos'):
            delta = QPoint(event.globalPosition().toPoint() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        if hasattr(self, 'oldPos'):
            del self.oldPos

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TaskCompletePopup()
    window.show()
    sys.exit(app.exec())
