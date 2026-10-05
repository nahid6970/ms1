import sys

from PyQt6.QtWidgets import QApplication, QWidget, QPushButton
from PyQt6.QtCore import Qt, QPoint, QTimer, QRectF, QPointF
from PyQt6.QtGui import (QColor, QPainter, QPainterPath,
                         QFont, QConicalGradient, QRadialGradient)

W, H          = 460, 220
CORNER_RADIUS = 22


class TaskCompletePopup(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(W, H)

        self._aurora_t   = 0.0
        self._glow_pulse = 0.0
        self._glow_dir   = 1
        self._opacity    = 0.0
        self._slide_y    = 24.0

        self.btn = QPushButton("Dismiss", self)
        self.btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn.setFixedSize(120, 36)
        self.btn.move((W - 120) // 2, H - 58)
        self.btn.clicked.connect(self.close)
        self.btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid rgba(255,255,255,0.28);
                border-radius: 18px;
                color: rgba(255,255,255,0.88);
                font-family: 'Segoe UI', sans-serif;
                font-size: 10pt;
                font-weight: 500;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.07);
                border-color: rgba(255,255,255,0.55);
            }
            QPushButton:pressed {
                background: rgba(255,255,255,0.12);
            }
        """)

        self._tick_timer = QTimer()
        self._tick_timer.timeout.connect(self._tick)
        self._tick_timer.start(16)

        screen = self.screen().availableGeometry()
        self.move(
            (screen.width()  - self.width())  // 2,
            (screen.height() - self.height()) // 2,
        )

    def _tick(self):
        self._aurora_t = (self._aurora_t + 0.008) % 1.0
        self._glow_pulse += self._glow_dir * 0.012
        if self._glow_pulse >= 1.0:
            self._glow_dir = -1
        elif self._glow_pulse <= 0.0:
            self._glow_dir = 1
        if self._opacity < 1.0:
            self._opacity = min(self._opacity + 0.055, 1.0)
            self._slide_y = max(self._slide_y - 1.3, 0.0)
            self.btn.move((W - 120) // 2, H - 58 + int(self._slide_y))
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        p.translate(0, self._slide_y)
        p.setOpacity(self._opacity)

        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, W, H), CORNER_RADIUS, CORNER_RADIUS)

        p.setClipPath(path)
        p.fillPath(path, QColor(11, 14, 26))

        rg = QRadialGradient(QPointF(W * 0.5, H * 0.38), W * 0.65)
        rg.setColorAt(0, QColor(255, 255, 255, 9))
        rg.setColorAt(1, QColor(0, 0, 0, 0))
        p.fillPath(path, rg)

        p.setClipping(False)

        # ✦ sparkle
        p.setFont(QFont("Segoe UI", 18))
        p.setPen(QColor(255, 255, 255, 230))
        p.drawText(QRectF(0, 22, W, 36), Qt.AlignmentFlag.AlignCenter, "✦")

        # AI ASSISTANT
        f_sub = QFont("Segoe UI", 8, QFont.Weight.Bold)
        f_sub.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 4.0)
        p.setFont(f_sub)
        p.setPen(QColor(255, 255, 255, 95))
        p.drawText(QRectF(0, 64, W, 20), Qt.AlignmentFlag.AlignCenter, "AI ASSISTANT")

        # Main message
        p.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        p.setPen(QColor(255, 255, 255, 238))
        p.drawText(QRectF(0, 90, W, 32), Qt.AlignmentFlag.AlignCenter,
                   "Task Completed Successfully")

        # Timestamp
        p.setFont(QFont("Segoe UI", 8))
        p.setPen(QColor(255, 255, 255, 75))
        p.drawText(QRectF(0, 126, W, 20), Qt.AlignmentFlag.AlignCenter,
                   "Finished at  2026-10-05 14:22")

        # Aurora border
        cx, cy = W / 2, H / 2
        angle  = self._aurora_t * 360.0

        cg = QConicalGradient(QPointF(cx, cy), angle)
        cg.setColorAt(0.00, QColor(80,  60, 255, 220))
        cg.setColorAt(0.14, QColor(0,  160, 255, 220))
        cg.setColorAt(0.28, QColor(0,  230, 180, 220))
        cg.setColorAt(0.42, QColor(255,  80, 180, 220))
        cg.setColorAt(0.57, QColor(255, 160,  40, 220))
        cg.setColorAt(0.71, QColor(160,  40, 255, 220))
        cg.setColorAt(0.85, QColor(0,   200, 255, 220))
        cg.setColorAt(1.00, QColor(80,   60, 255, 220))

        outer = QPainterPath()
        outer.addRoundedRect(QRectF(0, 0, W, H), CORNER_RADIUS, CORNER_RADIUS)
        inner = QPainterPath()
        inner.addRoundedRect(QRectF(1.5, 1.5, W - 3, H - 3),
                             CORNER_RADIUS - 1.5, CORNER_RADIUS - 1.5)

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(cg)
        p.drawPath(outer - inner)

        p.end()

    def closeEvent(self, event):
        self._tick_timer.stop()
        QApplication.instance().quit()
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if hasattr(self, "oldPos"):
            delta = QPoint(event.globalPosition().toPoint() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        if hasattr(self, "oldPos"):
            del self.oldPos


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TaskCompletePopup()
    window.show()
    sys.exit(app.exec())
