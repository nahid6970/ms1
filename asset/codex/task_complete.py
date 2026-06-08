import sys

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

BG_COLOR = "#FFFFFF"
BORDER_COLOR = "#E0E0E0"
PRIMARY_COLOR = "#0078D4"
TEXT_COLOR = "#201F1E"
BTN_HOVER = "#005A9E"


class TaskCompletePopup(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)

        container = QWidget()
        container.setObjectName("Container")
        inner = QVBoxLayout(container)
        inner.setContentsMargins(30, 30, 30, 30)
        outer.addWidget(container)

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

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 4)
        container.setGraphicsEffect(shadow)

        label = QLabel("Codex Task Completed")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        inner.addWidget(label)
        inner.addSpacing(20)

        close_btn = QPushButton("Dismiss")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.close)
        inner.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.adjustSize()
        self.center()

    def center(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TaskCompletePopup()
    window.show()
    sys.exit(app.exec())

