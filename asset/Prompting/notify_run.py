import sys

from PyQt6.QtWidgets import QApplication, QWidget, QPushButton
from PyQt6.QtCore import Qt, QPoint, QTimer, QRectF, QPointF
from PyQt6.QtGui import (QColor, QPainter, QPainterPath, QPen,
                         QFont, QRadialGradient, QConicalGradient, QRegion)

W, H          = 460, 220
CORNER_RADIUS = 22
PAD           = 20
BG_COLOR      = QColor(11, 14, 26)

AURORA = [
    QColor(80,  60, 255),   # violet-blue
    QColor(0,  160, 255),   # cyan-blue
    QColor(0,  220, 180),   # mint/teal
    QColor(120, 60, 255),   # purple
    QColor(255, 80, 180),   # pink
    QColor(255, 160,  40),  # amber
    QColor(0,  200, 255),   # bright cyan
    QColor(160, 40, 255),   # deep violet
]


class NotifyCard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(W, H)

        self._aurora_t   = 0.0
        self._glow_pulse = 0.0
        self._glow_dir   = 1
        self._opacity    = 0.0
        self._slide_y    = 20.0

        self._tick_timer = QTimer()
        self._tick_timer.timeout.connect(self._tick)
        self._tick_timer.start(16)

        self.btn = QPushButton("Dismiss", self)
        self.btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn.setFixedSize(120, 36)
        self.btn.move((W - 120) // 2, H - 60)
        self.btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid rgba(255, 255, 255, 0.30);
                border-radius: 18px;
                color: rgba(255, 255, 255, 0.88);
                font-family: 'Segoe UI', sans-serif;
                font-size: 10pt;
                font-weight: 500;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.07);
                border-color: rgba(255, 255, 255, 0.55);
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 0.12);
            }
        """)

    def _tick(self):
        self._aurora_t = (self._aurora_t + 0.008) % 1.0
        self._glow_pulse += self._glow_dir * 0.012
        if self._glow_pulse >= 1.0:
            self._glow_dir = -1
        elif self._glow_pulse <= 0.0:
            self._glow_dir = 1
        if self._opacity < 1.0:
            self._opacity = min(self._opacity + 0.06, 1.0)
            self._slide_y = max(self._slide_y - 1.2, 0.0)
        self.update()

    def stop(self):
        self._tick_timer.stop()

    def _aurora_color(self) -> QColor:
        n   = len(AURORA)
        pos = self._aurora_t * n
        i   = int(pos) % n
        j   = (i + 1) % n
        t   = pos - int(pos)
        a, b = AURORA[i], AURORA[j]
        return QColor(
            int(a.red()   + (b.red()   - a.red())   * t),
            int(a.green() + (b.green() - a.green()) * t),
            int(a.blue()  + (b.blue()  - a.blue())  * t),
        )

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        p.setOpacity(self._opacity)

        rect = QRectF(0, 0, W, H)
        path = QPainterPath()
        path.addRoundedRect(rect, CORNER_RADIUS, CORNER_RADIUS)

        self.setMask(QRegion(path.toFillPolygon().toPolygon()))

        p.setClipPath(path)
        p.fillPath(path, BG_COLOR)

        # subtle centre glow
        rg = QRadialGradient(QPointF(W * 0.5, H * 0.4), W * 0.65)
        rg.setColorAt(0, QColor(255, 255, 255, 8))
        rg.setColorAt(1, QColor(0, 0, 0, 0))
        p.fillPath(path, rg)

        p.setClipping(False)

        # ✦ sparkle
        p.setFont(QFont("Segoe UI", 18))
        p.setPen(QColor(255, 255, 255, 230))
        p.drawText(QRectF(0, 24, W, 36), Qt.AlignmentFlag.AlignCenter, "✦")

        # AI ASSISTANT
        f_sub = QFont("Segoe UI", 8, QFont.Weight.Bold)
        f_sub.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 4.0)
        p.setFont(f_sub)
        p.setPen(QColor(255, 255, 255, 100))
        p.drawText(QRectF(0, 66, W, 20), Qt.AlignmentFlag.AlignCenter, "AI ASSISTANT")

        # Main message
        p.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        p.setPen(QColor(255, 255, 255, 240))
        p.drawText(QRectF(0, 94, W, 30), Qt.AlignmentFlag.AlignCenter,
                   "Task Completed Successfully")

        # Timestamp
        p.setFont(QFont("Segoe UI", 8))
        p.setPen(QColor(255, 255, 255, 80))
        p.drawText(QRectF(0, 128, W, 20), Qt.AlignmentFlag.AlignCenter,
                   "Finished at  2026-10-05 14:22")

        # ── Aurora border — rotating conical gradient ────────────────────────
        cx, cy = W / 2, H / 2
        angle  = self._aurora_t * 360.0

        cg = QConicalGradient(QPointF(cx, cy), angle)
        cg.setColorAt(0.00, QColor(80,  60, 255, 220))
        cg.setColorAt(0.14, QColor(0,  160, 255, 220))
        cg.setColorAt(0.28, QColor(0,  230, 180, 220))
        cg.setColorAt(0.42, QColor(255, 80, 180, 220))
        cg.setColorAt(0.57, QColor(255, 160, 40,  220))
        cg.setColorAt(0.71, QColor(160, 40, 255,  220))
        cg.setColorAt(0.85, QColor(0,  200, 255,  220))
        cg.setColorAt(1.00, QColor(80,  60, 255,  220))

        outer_path = QPainterPath()
        outer_path.addRoundedRect(QRectF(0, 0, W, H), CORNER_RADIUS, CORNER_RADIUS)

        cut_path = QPainterPath()
        cut_path.addRoundedRect(QRectF(1.5, 1.5, W - 3, H - 3),
                                CORNER_RADIUS - 1, CORNER_RADIUS - 1)

        ring = outer_path - cut_path
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(cg)
        p.drawPath(ring)

        p.end()


class TaskCompletePopup(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(W + PAD * 2, H + PAD * 2)

        self.card = NotifyCard(self)
        self.card.move(PAD, PAD)
        self.card.btn.clicked.connect(self.close)

        screen = self.screen().availableGeometry()
        self.move(
            (screen.width()  - self.width())  // 2,
            (screen.height() - self.height()) // 2,
        )

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx, cy = self.width() // 2, self.height() // 2
        rg = QRadialGradient(QPointF(cx, cy), 180)
        rg.setColorAt(0, QColor(60, 80, 220, 20))
        rg.setColorAt(1, QColor(0, 0, 0, 0))
        gp = QPainterPath()
        gp.addEllipse(QPointF(cx, cy), 180, 180)
        p.fillPath(gp, rg)
        p.end()

    def closeEvent(self, event):
        self.card.stop()
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
