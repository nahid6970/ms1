import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QPoint

# CYBERPUNK PALETTE
CP_BG = "#050505"
CP_PANEL = "#111111"
CP_GREEN = "#00ff21"
CP_TEXT = "#E0E0E0"
CP_DIM = "#3a3a3a"

class TaskCompletePopup(QWidget):
    def __init__(self):
        super().__init__()
        
        # Window Flags: Frameless and Always on Top
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Central Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Main Container (to hold the border and background)
        self.container = QWidget()
        self.container.setObjectName("Container")
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(20, 20, 20, 20)
        self.layout.addWidget(self.container)
        
        # Styling
        self.setStyleSheet(f"""
            QWidget#Container {{
                background-color: {CP_BG};
                border: 2px solid {CP_GREEN};
                border-radius: 5px;
            }}
            QLabel {{
                color: {CP_GREEN};
                font-family: 'Consolas';
                font-size: 18pt;
                font-weight: bold;
            }}
            QPushButton {{
                background-color: {CP_DIM};
                color: {CP_TEXT};
                border: 1px solid {CP_GREEN};
                padding: 5px 15px;
                font-family: 'Consolas';
                font-size: 10pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {CP_GREEN};
                color: {CP_BG};
            }}
        """)
        
        # Glow Effect for the Border
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(Qt.GlobalColor.green)
        shadow.setOffset(0, 0)
        self.container.setGraphicsEffect(shadow)
        
        # Message Label
        self.label = QLabel("Your task has been Completed✅")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.container_layout.addWidget(self.label)
        
        # Spacer
        self.container_layout.addSpacing(10)
        
        # Close Button
        self.close_btn = QPushButton("ACKNOWLEDGE")
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
