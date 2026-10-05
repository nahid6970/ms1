import sys

from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QPoint, QTimer, QRectF, QPointF
from PyQt6.QtGui import (QColor, QPainter, QPainterPath,
                         QFont, QConicalGradient, QRadialGradient)

W, H          = 460, 220
CORNER_RADIUS = 22
BTN_W, BTN_H  = 120, 36
BTN_X         = (W - BTN_W) // 2
BTN_Y         = H - 58


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
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.setMouseTracking(True)

        self._aurora_t    = 0.0
        self._opacity     = 0.0
        self._slide_y     = 24.0
        self._btn_hovered = False
        self._btn_pressed = False

        self._tick_timer = QTimer()
        self._tick_timer.timeout.connect(self._tick)
        self._tick_timer.start(16)

        screen = self.screen().availableGeometry()
        self.move(
            (screen.width()  - self.width())  // 2,
            (screen.height() - self.height()) // 2,
        )

    def _btn_rect(self) -> QRectF:
        return QRectF(BTN_X, BTN_Y + self._slide_y, BTN_W, BTN_H)

    def _tick(self):
        self._aurora_t = (self._aurora_t + 0.003) % 1.0
        if self._opacity < 1.0:
            self._opacity = min(self._opacity + 0.055, 1.0)
            self._slide_y = max(self._slide_y - 1.3, 0.0)
        self.update()

    def mouseMoveEvent(self, event):
        pos = event.position()
        hovered = self._btn_rect().contains(pos)
        if hovered != self._btn_hovered:
            self._btn_hovered = hovered
            self.setCursor(Qt.CursorShape.PointingHandCursor if hovered
                           else Qt.CursorShape.ArrowCursor)
            self.update()
        if hasattr(self, "_drag_pos"):
            delta = QPoint(event.globalPosition().toPoint() - self._drag_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self._drag_pos = event.globalPosition().toPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self._btn_rect().contains(event.position()):
                self._btn_pressed = True
                self.update()
            else:
                self._drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self._btn_pressed and self._btn_rect().contains(event.position()):
                self.close()
                return
            self._btn_pressed = False
            if hasattr(self, "_drag_pos"):
                del self._drag_pos
            self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        p.setOpacity(self._opacity)
        p.translate(0, self._slide_y)

        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, W, H), CORNER_RADIUS, CORNER_RADIUS)

        # background
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

        # main message
        p.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        p.setPen(QColor(255, 255, 255, 238))
        p.drawText(QRectF(0, 90, W, 32), Qt.AlignmentFlag.AlignCenter,
                   "Task Completed Successfully")

        # timestamp
        p.setFont(QFont("Segoe UI", 8))
        p.setPen(QColor(255, 255, 255, 75))
        p.drawText(QRectF(0, 126, W, 20), Qt.AlignmentFlag.AlignCenter,
                   "Finished at  2026-10-05 14:22")

        # dismiss button — fully painted
        btn = QRectF(BTN_X, BTN_Y, BTN_W, BTN_H)
        btn_path = QPainterPath()
        btn_path.addRoundedRect(btn, BTN_H / 2, BTN_H / 2)

        if self._btn_pressed:
            p.fillPath(btn_path, QColor(255, 255, 255, 30))
        elif self._btn_hovered:
            p.fillPath(btn_path, QColor(255, 255, 255, 18))

        # border ring
        btn_outer = QPainterPath()
        btn_outer.addRoundedRect(btn, BTN_H / 2, BTN_H / 2)
        btn_inner = QPainterPath()
        btn_inner.addRoundedRect(
            QRectF(BTN_X + 1, BTN_Y + 1, BTN_W - 2, BTN_H - 2),
            (BTN_H - 2) / 2, (BTN_H - 2) / 2
        )
        border_alpha = 100 if not self._btn_hovered else 160
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(255, 255, 255, border_alpha))
        p.drawPath(btn_outer - btn_inner)

        # label
        p.setFont(QFont("Segoe UI", 10))
        p.setPen(QColor(255, 255, 255, 220))
        p.drawText(btn, Qt.AlignmentFlag.AlignCenter, "Dismiss")

        # aurora border
        cg = QConicalGradient(QPointF(W / 2, H / 2), self._aurora_t * 360.0)
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TaskCompletePopup()
    window.show()
    sys.exit(app.exec())
