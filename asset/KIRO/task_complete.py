import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import QColor, QLinearGradient

BG_COLOR = "#1E1E2E"
BORDER_COLOR = "#313244"
PRIMARY_COLOR = "#89B4FA"  # Kiro Blue
TEXT_COLOR = "#CDD6F4"
BTN_HOVER = "#74C7EC"

# Gradient color sets for animation
GRADIENT_COLORS = [
    ("#FF6B6B", "#4ECDC4"),  # Red to Teal
    ("#667eea", "#764ba2"),  # Blue to Purple
    ("#f093fb", "#f5576c"),  # Pink to Red
    ("#4facfe", "#00f2fe"),  # Blue to Cyan
    ("#43e97b", "#38f9d7"),  # Green to Cyan
    ("#fa709a", "#fee140"),  # Pink to Yellow
    ("#a8edea", "#fed6e3"),  # Cyan to Pink
    ("#ff9a9e", "#fecfef"),  # Pink to Light Pink
]

class TaskCompletePopup(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.gradient_index = 0
        self.setup_ui()
        self.setup_gradient_timer()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(layout)

        self.container = QWidget()
        self.container.setObjectName("Container")
        c_layout = QVBoxLayout(self.container)
        c_layout.setContentsMargins(30, 30, 30, 30)
        layout.addWidget(self.container)

        self.update_gradient_style()

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

    def setup_gradient_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.change_gradient)
        self.timer.start(1500)  # Change every 1.5 seconds

    def change_gradient(self):
        self.gradient_index = (self.gradient_index + 1) % len(GRADIENT_COLORS)
        self.update_gradient_style()

    def update_gradient_style(self):
        color1, color2 = GRADIENT_COLORS[self.gradient_index]
        self.setStyleSheet(f"""
            QWidget#Container {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 {color1}, stop:1 {color2});
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
            }}
            QLabel#title {{
                color: white;
                font-family: 'Segoe UI', sans-serif;
                font-size: 11pt;
                font-weight: 700;
                letter-spacing: 1px;
            }}
            QLabel#msg {{
                color: white;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13pt;
            }}
            QPushButton {{
                background-color: rgba(255, 255, 255, 0.9);
                color: #1E1E2E;
                border: none;
                border-radius: 4px;
                padding: 8px 24px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 10pt;
                font-weight: 700;
            }}
            QPushButton:hover {{ background-color: rgba(255, 255, 255, 1); }}
            QPushButton:pressed {{ background-color: rgba(255, 255, 255, 0.8); }}
        """)

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
