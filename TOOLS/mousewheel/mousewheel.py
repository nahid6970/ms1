import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt, QTimer
import pyautogui

CP_BG = "#050505"
CP_DIM = "#3a3a3a"
CP_YELLOW = "#FCEE0A"

STYLE = f"""
QWidget {{ background-color: {CP_BG}; }}
QPushButton {{
    background-color: {CP_DIM};
    border: 1px solid {CP_DIM};
    color: white;
    font-family: Consolas;
    font-size: 10pt;
    font-weight: bold;
    padding: 2px;
}}
QPushButton:hover {{
    background-color: #2a2a2a;
    border: 1px solid {CP_YELLOW};
    color: {CP_YELLOW};
}}
QPushButton:pressed {{
    background-color: {CP_YELLOW};
    color: black;
}}
"""

class MouseWheel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scroll")
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setFixedSize(36, 58)
        self.setStyleSheet(STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        self.btn_up = QPushButton("▲")
        self.btn_down = QPushButton("▼")
        for btn in (self.btn_up, self.btn_down):
            btn.setFixedHeight(24)
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setAutoRepeat(True)
            btn.setAutoRepeatDelay(400)
            btn.setAutoRepeatInterval(80)
            layout.addWidget(btn)

        self.btn_up.clicked.connect(lambda: pyautogui.scroll(3))
        self.btn_down.clicked.connect(lambda: pyautogui.scroll(-3))

        # drag support
        self._drag_pos = None

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self._drag_pos and e.buttons() == Qt.MouseButton.LeftButton:
            self.move(e.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, e):
        self._drag_pos = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MouseWheel()
    w.show()
    sys.exit(app.exec())
