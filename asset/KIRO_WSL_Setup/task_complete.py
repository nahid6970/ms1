import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QColor

BG_COLOR = "#1E1E2E"
BORDER_COLOR = "#313244"
PRIMARY_COLOR = "#89B4FA"  # Kiro Blue
TEXT_COLOR = "#CDD6F4"
BTN_HOVER = "#74C7EC"

class TaskCompletePopup(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(layout)

        self.container = QWidget()
        self.container.setObjectName("Container")
        c_layout = QVBoxLayout(self.container)
        c_layout.setContentsMargins(30, 30, 30, 30)
        layout.addWidget(self.container)

        self.setStyleSheet(f"""
            QWidget#Container {{
                background-color: {BG_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
            }}
            QLabel#title {{
                color: {PRIMARY_COLOR};
                font-family: 'Segoe UI', sans-serif;
                font-size: 11pt;
                font-weight: 700;
                letter-spacing: 1px;
            }}
            QLabel#msg {{
                color: {TEXT_COLOR};
                font-family: 'Segoe UI', sans-serif;
                font-size: 13pt;
            }}
            QPushButton {{
                background-color: {PRIMARY_COLOR};
                color: #1E1E2E;
                border: none;
                border-radius: 4px;
                padding: 8px 24px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 10pt;
                font-weight: 700;
            }}
            QPushButton:hover {{ background-color: {BTN_HOVER}; }}
            QPushButton:pressed {{ background-color: #89DCEB; }}
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)

        title = QLabel("✦ KIRO AI")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c_layout.addWidget(title)

        c_layout.addSpacing(8)

        msg = QLabel("Task Completed Successfully")
        msg.setObjectName("msg")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c_layout.addWidget(msg)

        c_layout.addSpacing(20)

        btn = QPushButton("Dismiss")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(self.close)
        c_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.adjustSize()
        qr = self.frameGeometry()
        qr.moveCenter(self.screen().availableGeometry().center())
        self.move(qr.topLeft())

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
