"""
notify.py — Cyberpunk desktop notification popup.
Called by server.py or directly from CLI.

Usage:
    python notify.py "Title" "Message body" "Source"
    python notify.py  (shows a test notification)
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QGraphicsDropShadowEffect, QFrame
)
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import QColor

# ── Cyberpunk Palette (matches task_complete.py) ──────────────────────────────
CP_BG     = "#050505"
CP_PANEL  = "#111111"
CP_CYAN   = "#00e5ff"
CP_GREEN  = "#00ff21"
CP_YELLOW = "#ffe600"
CP_TEXT   = "#E0E0E0"
CP_DIM    = "#1a1a1a"
CP_BORDER = "#1e1e1e"


class NotificationPopup(QWidget):
    def __init__(self, title: str = "Notification", message: str = "", source: str = ""):
        super().__init__()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # ── Root layout ───────────────────────────────────────────────────────
        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        self.setLayout(root)

        # ── Container card ────────────────────────────────────────────────────
        self.container = QWidget()
        self.container.setObjectName("Container")
        root.addWidget(self.container)

        card = QVBoxLayout(self.container)
        card.setContentsMargins(20, 16, 20, 18)
        card.setSpacing(8)

        # Glow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(28)
        shadow.setColor(QColor(0, 229, 255, 180))
        shadow.setOffset(0, 0)
        self.container.setGraphicsEffect(shadow)

        # ── Header row: icon + title + close ─────────────────────────────────
        header = QHBoxLayout()
        header.setSpacing(8)

        icon_lbl = QLabel("◈")
        icon_lbl.setObjectName("Icon")
        header.addWidget(icon_lbl)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("Title")
        title_lbl.setWordWrap(True)
        header.addWidget(title_lbl, stretch=1)

        close_btn = QPushButton("✕")
        close_btn.setObjectName("CloseBtn")
        close_btn.setFixedSize(22, 22)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.close)
        header.addWidget(close_btn)

        card.addLayout(header)

        # ── Divider ───────────────────────────────────────────────────────────
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setObjectName("Divider")
        card.addWidget(line)

        # ── Message ───────────────────────────────────────────────────────────
        msg_lbl = QLabel(message or "(no message)")
        msg_lbl.setObjectName("Message")
        msg_lbl.setWordWrap(True)
        msg_lbl.setMaximumWidth(360)
        card.addWidget(msg_lbl)

        # ── Source tag (optional) ─────────────────────────────────────────────
        if source:
            src_lbl = QLabel(f"▸ {source}")
            src_lbl.setObjectName("Source")
            card.addWidget(src_lbl)

        card.addSpacing(4)

        # ── Dismiss button ────────────────────────────────────────────────────
        dismiss = QPushButton("ACKNOWLEDGE")
        dismiss.setObjectName("DismissBtn")
        dismiss.setCursor(Qt.CursorShape.PointingHandCursor)
        dismiss.clicked.connect(self.close)
        card.addWidget(dismiss, alignment=Qt.AlignmentFlag.AlignCenter)

        # ── Stylesheet ────────────────────────────────────────────────────────
        self.setStyleSheet(f"""
            QWidget#Container {{
                background-color: {CP_BG};
                border: 2px solid {CP_CYAN};
                border-radius: 6px;
                min-width: 320px;
                max-width: 420px;
            }}
            QLabel#Icon {{
                color: {CP_CYAN};
                font-size: 18pt;
                font-family: 'Consolas';
            }}
            QLabel#Title {{
                color: {CP_CYAN};
                font-family: 'Consolas';
                font-size: 13pt;
                font-weight: bold;
            }}
            QLabel#Message {{
                color: {CP_TEXT};
                font-family: 'Consolas';
                font-size: 10pt;
                line-height: 1.4;
            }}
            QLabel#Source {{
                color: {CP_YELLOW};
                font-family: 'Consolas';
                font-size: 9pt;
            }}
            QFrame#Divider {{
                color: {CP_CYAN};
                background-color: {CP_CYAN};
                max-height: 1px;
                opacity: 0.4;
            }}
            QPushButton#CloseBtn {{
                background-color: transparent;
                color: {CP_DIM};
                border: none;
                font-size: 10pt;
                font-family: 'Consolas';
            }}
            QPushButton#CloseBtn:hover {{
                color: {CP_CYAN};
            }}
            QPushButton#DismissBtn {{
                background-color: {CP_DIM};
                color: {CP_TEXT};
                border: 1px solid {CP_CYAN};
                padding: 5px 20px;
                font-family: 'Consolas';
                font-size: 10pt;
                font-weight: bold;
                border-radius: 3px;
            }}
            QPushButton#DismissBtn:hover {{
                background-color: {CP_CYAN};
                color: {CP_BG};
            }}
        """)

        # ── Position: bottom-right corner ─────────────────────────────────────
        self.adjustSize()
        self._position_bottom_right()

        # ── Auto-close after 30 seconds ───────────────────────────────────────
        QTimer.singleShot(30_000, self.close)

    def _position_bottom_right(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.adjustSize()
        x = screen.right() - self.width() - 24
        y = screen.bottom() - self.height() - 24
        self.move(x, y)

    # ── Draggable window ──────────────────────────────────────────────────────
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if hasattr(self, "_drag_pos"):
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.move(self.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        if hasattr(self, "_drag_pos"):
            del self._drag_pos


def show_notification(title: str, message: str, source: str = ""):
    """Show popup. Creates QApplication if none exists."""
    app = QApplication.instance() or QApplication(sys.argv)
    win = NotificationPopup(title, message, source)
    win.show()
    app.exec()


if __name__ == "__main__":
    args = sys.argv[1:]
    title   = args[0] if len(args) > 0 else "Webhook Notification"
    message = args[1] if len(args) > 1 else "A task has been completed."
    source  = args[2] if len(args) > 2 else ""
    show_notification(title, message, source)
