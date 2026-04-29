import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QPoint, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
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
        self._transition_progress = 0.0
        self.setup_ui()
        self.setup_gradient_timer()
        self.setup_animation()

    @pyqtProperty(float)
    def transition_progress(self):
        return self._transition_progress

    @transition_progress.setter
    def transition_progress(self, value):
        self._transition_progress = value
        self.update_gradient_style()

    def setup_animation(self):
        self.animation = QPropertyAnimation(self, b"transition_progress")
        self.animation.setDuration(1200)  # 1.2 second transition
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

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
        self.timer.timeout.connect(self.start_transition)
        self.timer.start(2500)  # Start new transition every 2.5 seconds

    def start_transition(self):
        self.gradient_index = (self.gradient_index + 1) % len(GRADIENT_COLORS)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()

    def interpolate_color(self, color1, color2, t):
        """Interpolate between two hex colors"""
        c1 = QColor(color1)
        c2 = QColor(color2)
        r = int(c1.red() + (c2.red() - c1.red()) * t)
        g = int(c1.green() + (c2.green() - c1.green()) * t)
        b = int(c1.blue() + (c2.blue() - c1.blue()) * t)
        return f"#{r:02x}{g:02x}{b:02x}"

    def update_gradient_style(self):
        current_colors = GRADIENT_COLORS[self.gradient_index]
        prev_index = (self.gradient_index - 1) % len(GRADIENT_COLORS)
        prev_colors = GRADIENT_COLORS[prev_index]
        
        # Interpolate between previous and current gradient
        color1 = self.interpolate_color(prev_colors[0], current_colors[0], self._transition_progress)
        color2 = self.interpolate_color(prev_colors[1], current_colors[1], self._transition_progress)
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
