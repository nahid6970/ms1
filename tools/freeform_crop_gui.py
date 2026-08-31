import sys, os
# 1. Add the absolute path to the folder containing install_deps.py
UTILITY_PATH = r"C:\@delta\ms1"
if UTILITY_PATH not in sys.path: sys.path.append(UTILITY_PATH)

# 2. Import and run the bootstrap
import install_deps
install_deps.bootstrap(__file__)

import sys
import os
import json
from pathlib import Path
from datetime import datetime
import cv2
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QFileDialog, QMessageBox, QSpinBox,
                             QDialog, QFormLayout, QLineEdit, QColorDialog, QDialogButtonBox,
                             QInputDialog, QMenu, QWidgetAction)
from PyQt6.QtCore import Qt, QTimer, QByteArray, QSize, QPoint, QRect
from PyQt6.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QCursor, QIcon, QFont, QAction
from PyQt6.QtSvg import QSvgRenderer

# PALETTE
CP_BG = "#050505"
CP_PANEL = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN = "#00F0FF"
CP_RED = "#FF003C"
CP_GREEN = "#00ff21"
CP_DIM = "#3a3a3a"
CP_TEXT = "#E0E0E0"

CONFIG_FILE = Path(__file__).parent / ".freeform_crop_state.json"


def make_btn(label, accent, text_on_press="black"):
    ss = (f"QPushButton {{ background-color: {CP_DIM}; border: 1px solid {accent}; "
          f"color: {accent}; padding: 8px 16px; font-weight: bold; }}"
          f"QPushButton:hover {{ background-color: {accent}22; border: 1px solid {accent}; color: {accent}; }}"
          f"QPushButton:pressed {{ background-color: {accent}; color: {text_on_press}; }}")
    b = QPushButton(label)
    b.setStyleSheet(ss)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    return b


def svg_icon(svg_str, size=20):
    """Render an SVG string into a QIcon."""
    ba = QByteArray(svg_str.encode())
    renderer = QSvgRenderer(ba)
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pm)
    renderer.render(painter)
    painter.end()
    return QIcon(pm)


class SettingsDialog(QDialog):
    def __init__(self, parent, settings):
        super().__init__(parent)
        self.setWindowTitle("SETTINGS")
        self.setModal(True)
        self.setMinimumWidth(320)
        self.setStyleSheet(f"""
            QDialog {{ background: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: Consolas; font-size: 10pt; }}
            QLabel {{ color: {CP_TEXT}; }}
            QSpinBox, QLineEdit {{
                background: {CP_DIM}; color: {CP_TEXT}; border: 1px solid #555;
                padding: 4px; font-family: Consolas;
            }}
            QPushButton {{ background: {CP_DIM}; color: {CP_TEXT}; border: 1px solid #555; padding: 6px 12px; }}
            QPushButton:hover {{ border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }}
        """)
        self.settings = dict(settings)

        layout = QFormLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # Sub-points
        self.spin = QSpinBox()
        self.spin.setRange(1, 20)
        self.spin.setValue(self.settings.get("subpts", 4))
        self.spin.setStyleSheet("QSpinBox::up-button, QSpinBox::down-button { width: 0; }")
        layout.addRow("Auto-scan sub-points:", self.spin)

        # Text fg/bg/border
        self.btn_fg = self._color_btn(self.settings.get("text_fg", "#000000"))
        self.btn_bg = self._color_btn(self.settings.get("text_bg", "#ffffff"))
        self.btn_border = self._color_btn(self.settings.get("text_border", "#000000"))
        self.btn_fg.clicked.connect(lambda: self._pick("text_fg", self.btn_fg))
        self.btn_bg.clicked.connect(lambda: self._pick("text_bg", self.btn_bg))
        self.btn_border.clicked.connect(lambda: self._pick("text_border", self.btn_border))

        layout.addRow("Text color:", self.btn_fg)
        layout.addRow("Text background:", self.btn_bg)
        layout.addRow("Text border:", self.btn_border)

        # Font size
        self.font_spin = QSpinBox()
        self.font_spin.setRange(8, 120)
        self.font_spin.setValue(self.settings.get("font_size", 24))
        self.font_spin.setStyleSheet("QSpinBox::up-button, QSpinBox::down-button { width: 0; }")
        self.font_spin.valueChanged.connect(self._update_preview)
        layout.addRow("Font size:", self.font_spin)

        _spin_ss = "QSpinBox::up-button, QSpinBox::down-button { width: 0; }"
        self.canny_low_spin = QSpinBox()
        self.canny_low_spin.setRange(1, 255)
        self.canny_low_spin.setValue(self.settings.get("canny_low", 20))
        self.canny_low_spin.setStyleSheet(_spin_ss)
        layout.addRow("Canny low (was 30):", self.canny_low_spin)

        self.canny_high_spin = QSpinBox()
        self.canny_high_spin.setRange(1, 255)
        self.canny_high_spin.setValue(self.settings.get("canny_high", 80))
        self.canny_high_spin.setStyleSheet(_spin_ss)
        layout.addRow("Canny high (was 100):", self.canny_high_spin)

        # Preview
        self.preview = QLabel("Sample Text")
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setFixedHeight(48)
        self.preview.setContentsMargins(8, 4, 8, 4)
        layout.addRow("Preview:", self.preview)
        self._update_preview()

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def _update_preview(self):
        fg = self.settings.get("text_fg", "#000000")
        bg = self.settings.get("text_bg", "#ffffff")
        border = self.settings.get("text_border", "#000000")
        fs = self.font_spin.value()
        self.preview.setStyleSheet(
            f"color: {fg}; background: {bg}; border: 2px solid {border};"
            f"font-family: Consolas; font-size: {fs}pt; font-weight: bold;"
        )

    def _color_btn(self, hex_color):
        btn = QPushButton()
        btn.setFixedHeight(28)
        btn.setStyleSheet(f"background: {hex_color}; border: 1px solid #888;")
        btn._color = hex_color
        return btn

    def _pick(self, key, btn):
        c = QColorDialog.getColor(QColor(self.settings[key]), self, "Pick color")
        if c.isValid():
            self.settings[key] = c.name()
            btn.setStyleSheet(f"background: {c.name()}; border: 1px solid #888;")
            btn._color = c.name()
            self._update_preview()

    def get_settings(self):
        return {
            "subpts": self.spin.value(),
            "text_fg": self.settings["text_fg"],
            "text_bg": self.settings["text_bg"],
            "text_border": self.settings["text_border"],
            "font_size": self.font_spin.value(),
            "canny_low": self.canny_low_spin.value(),
            "canny_high": self.canny_high_spin.value(),
        }


class TextOverlay:
    """Represents a draggable text box on the canvas."""
    def __init__(self, text, x, y, settings):
        self.text = text
        self.x = x  # image coords (not display coords)
        self.y = y
        self.settings = settings

    def get_rect(self, painter_fm, scale=1.0):
        """Return bounding QRect for this text label in display coords."""
        fm = painter_fm
        tw = fm.horizontalAdvance(self.text) + 12
        th = fm.height() + 8
        return QRect(int(self.x * scale), int(self.y * scale), tw, th)


class ImageCanvas(QLabel):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 600)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(f"background-color: {CP_PANEL}; border: 1px solid {CP_DIM};")

        self.image = None
        self.display_image = None
        self.corners = []
        self.sides = [[], [], [], []]
        self.dragging = None
        self.phase = 0
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0

        # Text overlays
        self.text_overlays = []
        self.dragging_text = None
        self.drag_offset = QPoint()
        self.settings = {
            "subpts": 4,
            "text_fg": "#000000",
            "text_bg": "#ffffff",
            "text_border": "#000000",
            "font_size": 24,
            "canny_low": 20,
            "canny_high": 80,
        }

        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)

    def load_image(self, path):
        self.image = cv2.imread(path)
        if self.image is None:
            return False
        self.corners = []
        self.sides = [[], [], [], []]
        self.phase = 0
        self.text_overlays = []
        self.update_display()
        return True

    def update_display(self):
        if self.image is None:
            return

        h, w = self.image.shape[:2]
        canvas_w, canvas_h = self.width(), self.height()

        scale_w = canvas_w / w
        scale_h = canvas_h / h
        self.scale = min(scale_w, scale_h, 1.0)

        display_w = int(w * self.scale)
        display_h = int(h * self.scale)

        self.offset_x = (canvas_w - display_w) // 2
        self.offset_y = (canvas_h - display_h) // 2

        self.display_image = cv2.resize(self.image, (display_w, display_h))

        # Draw corners and sides
        if len(self.corners) == 4:
            for i in range(4):
                side_points = [self.corners[i]] + self.sides[i] + [self.corners[(i + 1) % 4]]
                for j in range(len(side_points) - 1):
                    cv2.line(self.display_image, tuple(side_points[j]), tuple(side_points[j + 1]), (0, 255, 0), 2)
                for pt in self.sides[i]:
                    cv2.circle(self.display_image, tuple(pt), 5, (255, 255, 0), -1)
        elif len(self.corners) > 1:
            for i in range(len(self.corners)):
                cv2.line(self.display_image, tuple(self.corners[i]),
                         tuple(self.corners[(i + 1) % len(self.corners)]), (0, 255, 0), 2)

        for pt in self.corners:
            cv2.circle(self.display_image, tuple(pt), 6, (0, 0, 255), -1)
            cv2.circle(self.display_image, tuple(pt), 7, (0, 240, 255), 1)

        rgb = cv2.cvtColor(self.display_image, cv2.COLOR_BGR2RGB)
        h2, w2, ch = rgb.shape
        qt_image = QImage(rgb.data, w2, h2, ch * w2, QImage.Format.Format_RGB888)

        pixmap = QPixmap(canvas_w, canvas_h)
        pixmap.fill(QColor(CP_PANEL))

        painter = QPainter(pixmap)
        painter.drawImage(self.offset_x, self.offset_y, qt_image)

        # Draw text overlays
        if self.text_overlays:
            font = QFont("Consolas", self.settings["font_size"])
            painter.setFont(font)
            fm = painter.fontMetrics()
            for ov in self.text_overlays:
                rect = ov.get_rect(fm, self.scale)
                rect.translate(self.offset_x, self.offset_y)
                painter.fillRect(rect, QColor(ov.settings["text_bg"]))
                painter.setPen(QPen(QColor(ov.settings["text_border"]), 1))
                painter.drawRect(rect)
                painter.setPen(QColor(ov.settings["text_fg"]))
                painter.drawText(rect.adjusted(6, 4, -6, -4), Qt.AlignmentFlag.AlignCenter, ov.text)

        painter.end()
        self.setPixmap(pixmap)

    def _hit_text(self, x, y):
        """Return index of text overlay hit at display coords (x,y), or -1."""
        if not self.text_overlays:
            return -1
        tmp_pm = QPixmap(1, 1)
        p = QPainter(tmp_pm)
        p.setFont(QFont("Consolas", self.settings["font_size"]))
        fm = p.fontMetrics()
        p.end()
        for i, ov in enumerate(self.text_overlays):
            rect = ov.get_rect(fm, self.scale)
            if rect.contains(x, y):
                return i
        return -1

    def mousePressEvent(self, event):
        if self.image is None:
            return

        x = event.pos().x() - self.offset_x
        y = event.pos().y() - self.offset_y

        # Right-click: remove sub-point
        if event.button() == Qt.MouseButton.RightButton:
            if self.phase == 1:
                for side_idx in range(4):
                    for pt_idx, pt in enumerate(self.sides[side_idx]):
                        if np.linalg.norm(np.array([x, y]) - np.array(pt)) < 10:
                            self.sides[side_idx].pop(pt_idx)
                            self.update_display()
                            return
            return

        if event.button() != Qt.MouseButton.LeftButton:
            return

        # Check text overlays first
        idx = self._hit_text(x, y)
        if idx >= 0:
            self.dragging_text = idx
            ov = self.text_overlays[idx]
            # x,y are display coords; ov.x/y are image coords
            self.drag_offset = QPoint(x - int(ov.x * self.scale), y - int(ov.y * self.scale))
            return

        # Check if clicking near existing corner
        for i, pt in enumerate(self.corners):
            if np.linalg.norm(np.array([x, y]) - np.array(pt)) < 10:
                self.dragging = ('corner', i)
                return

        # Check if clicking near sub-point
        if self.phase == 1:
            for side_idx in range(4):
                for pt_idx, pt in enumerate(self.sides[side_idx]):
                    if np.linalg.norm(np.array([x, y]) - np.array(pt)) < 10:
                        self.dragging = ('side', side_idx, pt_idx)
                        return

        if self.phase == 0:
            if len(self.corners) < 4:
                self.corners.append([x, y])
                if len(self.corners) == 4:
                    self.phase = 1
        else:
            best_side = None
            best_dist = float('inf')
            for i in range(4):
                dist, t = self.point_to_line_distance([x, y], self.corners[i], self.corners[(i + 1) % 4])
                if dist < best_dist and dist < 15:
                    best_dist = dist
                    best_side = (i, t)
            if best_side is not None:
                side_idx, t = best_side
                self.sides[side_idx].append([x, y])
                self.sides[side_idx].sort(
                    key=lambda p: self.point_to_line_distance(p, self.corners[side_idx],
                                                               self.corners[(side_idx + 1) % 4])[1])

        self.update_display()

    def mouseMoveEvent(self, event):
        x = event.pos().x() - self.offset_x
        y = event.pos().y() - self.offset_y

        if self.dragging_text is not None:
            ov = self.text_overlays[self.dragging_text]
            # convert display drag pos back to image coords
            ov.x = int((x - self.drag_offset.x()) / self.scale)
            ov.y = int((y - self.drag_offset.y()) / self.scale)
            self.update_display()
            return

        if self.dragging is not None:
            if self.dragging[0] == 'corner':
                self.corners[self.dragging[1]] = [x, y]
            elif self.dragging[0] == 'side':
                self.sides[self.dragging[1]][self.dragging[2]] = [x, y]
            self.update_display()

    def mouseReleaseEvent(self, event):
        self.dragging = None
        self.dragging_text = None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.image is not None:
            self.update_display()

    def reset_points(self):
        self.corners = []
        self.sides = [[], [], [], []]
        self.phase = 0
        self.update_display()

    def point_to_line_distance(self, pt, line_start, line_end):
        px, py = pt
        x1, y1 = line_start
        x2, y2 = line_end
        line_len = np.linalg.norm(np.array([x2 - x1, y2 - y1]))
        if line_len == 0:
            return np.linalg.norm(np.array([px - x1, py - y1])), 0
        t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / (line_len ** 2)))
        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)
        return np.linalg.norm(np.array([px - proj_x, py - proj_y])), t

    def crop_image(self):
        if self.image is None or len(self.corners) != 4:
            return None

        all_sides = []
        for i in range(4):
            side_points = [self.corners[i]] + self.sides[i] + [self.corners[(i + 1) % 4]]
            all_sides.append(np.array([[p[0] / self.scale, p[1] / self.scale] for p in side_points], dtype=np.float32))

        top_len = sum(np.linalg.norm(all_sides[0][i + 1] - all_sides[0][i]) for i in range(len(all_sides[0]) - 1))
        bottom_len = sum(np.linalg.norm(all_sides[2][i + 1] - all_sides[2][i]) for i in range(len(all_sides[2]) - 1))
        left_len = sum(np.linalg.norm(all_sides[3][i + 1] - all_sides[3][i]) for i in range(len(all_sides[3]) - 1))
        right_len = sum(np.linalg.norm(all_sides[1][i + 1] - all_sides[1][i]) for i in range(len(all_sides[1]) - 1))

        width = int(max(top_len, bottom_len))
        height = int(max(left_len, right_len))
        if width <= 1 or height <= 1:
            return None

        top_full = self.interpolate_points(all_sides[0], width)
        bottom_full = self.interpolate_points(all_sides[2][::-1], width)
        left_full = self.interpolate_points(all_sides[3][::-1], height)
        right_full = self.interpolate_points(all_sides[1], height)

        u_coords = np.linspace(0, 1, width)
        v_coords = np.linspace(0, 1, height)
        u_mesh, v_mesh = np.meshgrid(u_coords, v_coords)

        U, V = u_mesh[..., np.newaxis], v_mesh[..., np.newaxis]
        T, B = top_full[np.newaxis, ...], bottom_full[np.newaxis, ...]
        L, R = left_full[:, np.newaxis, :], right_full[:, np.newaxis, :]
        c00, c10, c11, c01 = top_full[0], top_full[-1], bottom_full[-1], bottom_full[0]

        bilinear = (1 - U) * (1 - V) * c00 + U * (1 - V) * c10 + U * V * c11 + (1 - U) * V * c01
        map_full = (1 - V) * T + V * B + (1 - U) * L + U * R - bilinear

        map_x = map_full[:, :, 0].astype(np.float32)
        map_y = map_full[:, :, 1].astype(np.float32)
        return cv2.remap(self.image, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

    def interpolate_points(self, points, n):
        if len(points) == 0:
            return np.zeros((n, 2))
        if len(points) == 1:
            return np.tile(points[0], (n, 1))
        dists = [0]
        for i in range(len(points) - 1):
            dists.append(dists[-1] + np.linalg.norm(points[i + 1] - points[i]))
        total_dist = dists[-1]
        if total_dist == 0:
            return np.tile(points[0], (n, 1))
        result = []
        for i in range(n):
            target_dist = i * total_dist / (n - 1) if n > 1 else 0
            for j in range(len(dists) - 1):
                if dists[j] <= target_dist <= dists[j + 1]:
                    seg_len = dists[j + 1] - dists[j]
                    if seg_len == 0:
                        result.append(points[j])
                    else:
                        t = (target_dist - dists[j]) / seg_len
                        result.append((1 - t) * points[j] + t * points[j + 1])
                    break
            else:
                result.append(points[-1])
        return np.array(result)


class FreeformCropGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FREEFORM CROP")
        self.resize(1000, 700)
        self.setAcceptDrops(True)
        self.current_image_path = None
        self.folder_images = []
        self.folder_index = -1
        self._text_serial = 1

        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            QPushButton {{
                background-color: {CP_DIM}; border: 1px solid {CP_DIM};
                color: white; padding: 8px 16px; font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW};
            }}
            QPushButton:pressed {{ background-color: {CP_YELLOW}; color: black; }}
            QLabel {{ color: {CP_TEXT}; }}
        """)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        self.canvas = ImageCanvas()
        main_layout.addWidget(self.canvas)

        controls = QHBoxLayout()

        btn_load = make_btn("LOAD IMAGE", CP_CYAN)
        btn_load.clicked.connect(self.load_image)

        btn_reset = make_btn("RESET POINTS", CP_YELLOW, "black")
        btn_reset.clicked.connect(self.canvas.reset_points)

        btn_autoscan = make_btn("", "#00BFFF")
        btn_autoscan.setIcon(svg_icon('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#00BFFF" d="M15.5 14h-.79l-.28-.27A6.47 6.47 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14"/><path fill="#00BFFF" d="M12 10h-2v2H9v-2H7V9h2V7h1v2h2z"/></svg>'))
        btn_autoscan.setIconSize(QSize(22, 22))
        btn_autoscan.setFixedSize(38, 38)
        btn_autoscan.setToolTip("Auto Scan")
        btn_autoscan.clicked.connect(self.auto_scan)

        btn_add_text = make_btn("", "#FF8C00")
        btn_add_text.setIcon(svg_icon('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#FF8C00" d="M19 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2m-5 14H8v-2h6zm3-4H8v-2h9zm0-4H8V7h9z"/></svg>'))
        btn_add_text.setIconSize(QSize(22, 22))
        btn_add_text.setFixedSize(38, 38)
        btn_add_text.setToolTip("Add Text")
        btn_add_text.clicked.connect(self.add_text_overlay)

        btn_settings = make_btn("", "#9E9E9E", "black")
        btn_settings.setIcon(svg_icon('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#9E9E9E" d="M19.14 12.94c.04-.3.06-.61.06-.94s-.02-.64-.07-.94l2.03-1.58a.49.49 0 0 0 .12-.61l-1.92-3.32a.49.49 0 0 0-.59-.22l-2.39.96a7 7 0 0 0-1.62-.94l-.36-2.54a.484.484 0 0 0-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54a7.4 7.4 0 0 0-1.62.94l-2.39-.96a.47.47 0 0 0-.59.22L2.74 8.87a.47.47 0 0 0 .12.61l2.03 1.58c-.05.3-.07.63-.07.94s.02.64.07.94l-2.03 1.58a.49.49 0 0 0-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.36 1.04.67 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54a7.4 7.4 0 0 0 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32a.47.47 0 0 0-.12-.61zM12 15.6a3.6 3.6 0 1 1 0-7.2 3.6 3.6 0 0 1 0 7.2"/></svg>'))
        btn_settings.setIconSize(QSize(22, 22))
        btn_settings.setFixedSize(38, 38)
        btn_settings.setToolTip("Settings")
        btn_settings.clicked.connect(self.open_settings)

        btn_crop = make_btn("CROP_SAVE", CP_GREEN)
        btn_crop.clicked.connect(self.crop_and_save)

        btn_overwrite = make_btn("CROP_OVERRIDE", CP_RED)
        btn_overwrite.clicked.connect(self.crop_and_overwrite)
        # Rotate SVG button
        _svg = b'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
            stroke="#FF8C00" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 2v6h-6"/>
          <path d="M21 8A10 10 0 1 0 19 19"/>
        </svg>'''
        _renderer = QSvgRenderer(QByteArray(_svg))
        _pm = QPixmap(22, 22)
        _pm.fill(Qt.GlobalColor.transparent)
        _p = QPainter(_pm)
        _renderer.render(_p)
        _p.end()
        btn_rotate = QPushButton()
        btn_rotate.setIcon(QIcon(_pm))
        btn_rotate.setIconSize(QSize(20, 20))
        btn_rotate.setFixedWidth(40)
        btn_rotate.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_rotate.setStyleSheet(
            f"QPushButton {{ background-color: {CP_DIM}; border: 1px solid #FF8C00; padding: 6px; }}"
            f"QPushButton:hover {{ background-color: #FF8C0022; }}"
            f"QPushButton:pressed {{ background-color: #FF8C00; }}"
        )
        btn_rotate.clicked.connect(self.rotate_image)

        btn_prev = make_btn("◀", CP_CYAN)
        btn_prev.clicked.connect(self.prev_image)
        btn_prev.setFixedWidth(40)

        btn_next = make_btn("▶", CP_CYAN)
        btn_next.clicked.connect(self.next_image)
        btn_next.setFixedWidth(40)

        btn_restart = make_btn("RESTART", "#BB86FC")
        btn_restart.clicked.connect(self.restart_app)

        self.info_label = QLabel("Phase 1: Click 4 corners • Phase 2: Click edges to add sub-points")
        self.info_label.setStyleSheet(f"color: {CP_CYAN}; font-size: 9pt;")

        controls.addWidget(btn_load)

        def show_save_menu():
            menu = QMenu()
            menu.setStyleSheet("""
                QMenu {
                    background: #1e1e1e;
                    color: #f0f0f0;
                    border: 1px solid #555;
                    padding: 4px;
                    font-size: 13px;
                }
                QMenu::item {
                    padding: 8px 20px;
                    border-radius: 4px;
                }
                QMenu::item:selected {
                    background: #3a3a3a;
                    color: #ffffff;
                }
                QMenu::separator { height: 1px; background: #444; margin: 3px 8px; }
            """)

            def _wa(label, slot, red=False):
                btn = QPushButton(label)
                btn.setFlat(True)
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                bg = "#4a1a1a" if red else "#1e1e1e"
                hover = "#6b2020" if red else "#3a3a3a"
                btn.setStyleSheet(f"QPushButton {{ background:{bg}; color:#f0f0f0; text-align:left;"
                                  f"padding:8px 20px; border:none; font-size:13px; }}"
                                  f"QPushButton:hover {{ background:{hover}; }}")
                wa = QWidgetAction(menu)
                wa.setDefaultWidget(btn)
                btn.clicked.connect(lambda: (menu.close(), slot()))
                return wa

            menu.addAction(QAction("✂  CROP SAVE", menu, triggered=self.crop_and_save))
            menu.addAction(_wa("✂  CROP OVERRIDE", self.crop_and_overwrite, red=True))
            menu.addSeparator()
            menu.addAction(QAction("T  SAVE TEXT", menu, triggered=self.save_with_text))
            menu.addAction(_wa("T  TEXT OVERRIDE", self.text_override, red=True))

            pos = btn_save.mapToGlobal(btn_save.rect().topLeft())
            menu.adjustSize()
            pos.setY(pos.y() - menu.sizeHint().height())
            menu.exec(pos)

        btn_save = make_btn("SAVE ▾", CP_GREEN)
        btn_save.clicked.connect(show_save_menu)

        controls.addWidget(btn_reset)
        controls.addWidget(btn_autoscan)
        controls.addWidget(btn_settings)
        controls.addWidget(btn_add_text)
        controls.addWidget(btn_save)
        controls.addWidget(btn_rotate)
        controls.addWidget(btn_prev)
        controls.addWidget(btn_next)
        controls.addStretch()
        controls.addWidget(btn_restart)

        main_layout.addLayout(controls)
        main_layout.addWidget(self.info_label)

    # ── Settings ──────────────────────────────────────────────────────────────
    def open_settings(self):
        dlg = SettingsDialog(self, self.canvas.settings)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.canvas.settings = dlg.get_settings()
            state = json.loads(CONFIG_FILE.read_text(encoding="utf-8")) if CONFIG_FILE.exists() else {}
            state["settings"] = self.canvas.settings
            state["text_serial"] = self._text_serial
            CONFIG_FILE.write_text(json.dumps(state), encoding="utf-8")
            self.canvas.update_display()

    # ── Text overlay ──────────────────────────────────────────────────────────
    def add_text_overlay(self):
        if self.canvas.image is None:
            return
        text, ok = QInputDialog.getText(self, "Add Text", "Enter text:")
        if not ok:
            return
        if not text.strip():
            text = str(self._text_serial)
        else:
            try:
                self._text_serial = int(text.strip())
            except ValueError:
                pass
        self._text_serial += 1
        state = json.loads(CONFIG_FILE.read_text(encoding="utf-8")) if CONFIG_FILE.exists() else {}
        state["text_serial"] = self._text_serial
        CONFIG_FILE.write_text(json.dumps(state), encoding="utf-8")
        cw = self.canvas.width() - self.canvas.offset_x
        ch = self.canvas.height() - self.canvas.offset_y
        scale = self.canvas.scale if self.canvas.scale else 1.0
        x = max(0, int((cw // 2 - 75) / scale))
        y = max(0, int((ch - 60) / scale))
        ov = TextOverlay(text.strip(), x, y, dict(self.canvas.settings))
        self.canvas.text_overlays.append(ov)
        self.canvas.update_display()

    # ── Image loading ─────────────────────────────────────────────────────────
    def _load_image_from_path(self, file_path):
        if self.canvas.load_image(file_path):
            self.current_image_path = file_path
            idx_str = f"{self.folder_index + 1}/{len(self.folder_images)}" if self.folder_images else ""
            self.info_label.setText(f"{Path(file_path).name}  {idx_str} | Phase 1: Set 4 corners")
        else:
            QMessageBox.critical(self, "Error", "Failed to load image")

    def _set_folder(self, file_path):
        folder = Path(file_path).parent
        exts = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff'}
        self.folder_images = sorted([str(p) for p in folder.iterdir() if p.suffix.lower() in exts])
        try:
            self.folder_index = self.folder_images.index(str(Path(file_path)))
        except ValueError:
            self.folder_index = 0

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "",
                                                   "Images (*.png *.jpg *.jpeg *.bmp *.tiff)")
        if file_path:
            self._set_folder(file_path)
            self._load_image_from_path(file_path)

    def prev_image(self):
        if not self.folder_images:
            return
        self.folder_index = (self.folder_index - 1) % len(self.folder_images)
        self._load_image_from_path(self.folder_images[self.folder_index])

    def next_image(self):
        if not self.folder_images:
            return
        self.folder_index = (self.folder_index + 1) % len(self.folder_images)
        self._load_image_from_path(self.folder_images[self.folder_index])

    # ── Crop helpers ──────────────────────────────────────────────────────────
    def _apply_text_overlays(self, result_img):
        """Render text overlays onto the cropped cv2 image."""
        if not self.canvas.text_overlays:
            return result_img
        h, w = result_img.shape[:2]
        # Convert to QImage, draw text, convert back
        rgb = cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB)
        qt_img = QImage(rgb.data.tobytes(), w, h, 3 * w, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_img)
        painter = QPainter(pixmap)
        # overlays stored in image coords; output may be same size or cropped
        ih, iw = self.canvas.image.shape[:2]
        sx = w / iw if iw > 0 else 1.0
        sy = h / ih if ih > 0 else 1.0
        # font was set at display scale; scale up to output resolution
        display_scale = self.canvas.scale if self.canvas.scale > 0 else 1.0
        font_scale = sx / display_scale

        font_size = max(1, int(self.canvas.settings["font_size"] * font_scale))
        font = QFont("Consolas", font_size)
        painter.setFont(font)
        fm = painter.fontMetrics()
        pad_x = max(1, int(12 * font_scale))
        pad_y = max(1, int(8 * font_scale))
        border_w = max(1, int(font_scale))

        for ov in self.canvas.text_overlays:
            ox = int(ov.x * sx)
            oy = int(ov.y * sy)
            tw = fm.horizontalAdvance(ov.text) + pad_x
            th = fm.height() + pad_y
            rect = QRect(ox, oy, tw, th)
            painter.fillRect(rect, QColor(ov.settings["text_bg"]))
            painter.setPen(QPen(QColor(ov.settings["text_border"]), border_w))
            painter.drawRect(rect)
            painter.setPen(QColor(ov.settings["text_fg"]))
            painter.drawText(rect.adjusted(pad_x // 2, pad_y // 2, -(pad_x // 2), -(pad_y // 2)),
                             Qt.AlignmentFlag.AlignCenter, ov.text)
        painter.end()

        result = pixmap.toImage().convertToFormat(QImage.Format.Format_RGB888)
        ptr = result.bits()
        ptr.setsize(result.sizeInBytes())
        bpl = result.bytesPerLine()
        arr = np.frombuffer(ptr, dtype=np.uint8).reshape((h, bpl))[:, :w * 3].reshape((h, w, 3))
        return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

    def save_with_text(self):
        if self.canvas.image is None:
            QMessageBox.warning(self, "Warning", "No image loaded")
            return
        if not self.canvas.text_overlays:
            QMessageBox.warning(self, "Warning", "No text overlays added")
            return
        result = self._apply_text_overlays(self.canvas.image.copy())
        if self.current_image_path:
            original_path = Path(self.current_image_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = original_path.parent / f"{original_path.stem}_{timestamp}{original_path.suffix}"
            cv2.imwrite(str(save_path), result)
            self.flash_status(f"✔ Saved: {save_path.name}")
        else:
            QMessageBox.warning(self, "Warning", "No source path available")

    def text_override(self):
        if self.canvas.image is None or not self.canvas.text_overlays or not self.current_image_path:
            return
        result = self._apply_text_overlays(self.canvas.image.copy())
        cv2.imwrite(self.current_image_path, result)
        self._load_image_from_path(self.current_image_path)
        self.flash_status(f"✔ Override saved: {Path(self.current_image_path).name}")

    def crop_and_save(self):
        if self.canvas.image is None:
            QMessageBox.warning(self, "Warning", "No image loaded")
            return
        if len(self.canvas.corners) != 4:
            QMessageBox.warning(self, "Warning", "Need 4 corner points to crop")
            return
        result = self.canvas.crop_image()
        if result is None:
            QMessageBox.critical(self, "Error", "Crop failed")
            return
        result = self._apply_text_overlays(result)
        if self.current_image_path:
            original_path = Path(self.current_image_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = original_path.parent / f"{original_path.stem}_{timestamp}{original_path.suffix}"
            cv2.imwrite(str(save_path), result)
            self.flash_status(f"✔ Saved: {save_path.name}")
        else:
            QMessageBox.warning(self, "Warning", "No source path available")

    def crop_and_overwrite(self):
        if self.canvas.image is None:
            QMessageBox.warning(self, "Warning", "No image loaded")
            return
        if len(self.canvas.corners) != 4:
            QMessageBox.warning(self, "Warning", "Need 4 corner points to crop")
            return
        result = self.canvas.crop_image()
        if result is None:
            QMessageBox.critical(self, "Error", "Crop failed")
            return
        result = self._apply_text_overlays(result)
        if self.current_image_path:
            cv2.imwrite(self.current_image_path, result)
            self._load_image_from_path(self.current_image_path)
            self.flash_status(f"✔ Overwritten: {Path(self.current_image_path).name}")
        else:
            QMessageBox.warning(self, "Warning", "No source path available")

    def rotate_image(self):
        if self.canvas.image is None:
            return
        self.canvas.image = cv2.rotate(self.canvas.image, cv2.ROTATE_90_CLOCKWISE)
        self.canvas.reset_points()

    def _flash_center_overlay(self):
        lbl = QLabel("✔", self.canvas)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(
            "background-color: rgba(0,0,0,160); color: #00FF88;"
            "font-size: 64pt; font-weight: bold; border-radius: 16px; padding: 16px 32px;"
        )
        lbl.adjustSize()
        cx = (self.canvas.width() - lbl.width()) // 2
        cy = (self.canvas.height() - lbl.height()) // 2
        lbl.move(cx, cy)
        lbl.show()
        QTimer.singleShot(1000, lbl.deleteLater)

    def flash_status(self, msg, duration=3000):
        if msg.startswith("✔"):
            self._flash_center_overlay()
        self.info_label.setStyleSheet(f"color: {CP_GREEN}; font-size: 9pt;")
        self.info_label.setText(msg)
        QTimer.singleShot(duration, lambda: (
            self.info_label.setStyleSheet(f"color: {CP_CYAN}; font-size: 9pt;"),
            self.info_label.setText(
                Path(self.current_image_path).name if self.current_image_path
                else "Phase 1: Click 4 corners • Phase 2: Click edges to add sub-points")
        ))

    # ── Auto scan ─────────────────────────────────────────────────────────────
    def auto_scan(self):
        if self.canvas.image is None:
            return

        img = self.canvas.image
        h, w = img.shape[:2]
        scale = self.canvas.scale

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        canny_low = self.canvas.settings.get("canny_low", 20)
        canny_high = self.canvas.settings.get("canny_high", 80)
        edges = cv2.Canny(blurred, canny_low, canny_high)
        edges = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=2)

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        best_cnt = None
        corners_approx = None
        img_area = w * h
        for cnt in contours[:15]:
            area = cv2.contourArea(cnt)
            if area < img_area * 0.05 or area > img_area * 0.9995:
                continue
            peri = cv2.arcLength(cnt, True)
            # Try progressively looser epsilon until we get 4 points
            for eps in [0.01, 0.02, 0.03, 0.05, 0.08]:
                approx = cv2.approxPolyDP(cnt, eps * peri, True)
                if len(approx) == 4:
                    best_cnt = cnt
                    corners_approx = approx.reshape(4, 2).astype(np.float32)
                    break
            if best_cnt is not None:
                break

        if best_cnt is None:
            self.flash_status("✘ Auto scan failed — try manual points", duration=3000)
            return

        pts = corners_approx
        s = pts.sum(axis=1)
        diff = np.diff(pts, axis=1).ravel()
        ordered = np.array([
            pts[np.argmin(s)],
            pts[np.argmin(diff)],
            pts[np.argmax(s)],
            pts[np.argmax(diff)],
        ]).astype(np.float32)
        tl, tr, br, bl = ordered

        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.drawContours(mask, [best_cnt], -1, 255, 2)

        NUM_SUB = self.canvas.settings.get("subpts", 4)

        def scan_side(p_start, p_end, axis, num=NUM_SUB):
            pts_out = []
            for i in range(1, num + 1):
                t = i / (num + 1)
                mid = (1 - t) * p_start + t * p_end
                if axis == 0:
                    x = int(mid[0])
                    col = mask[:, max(0, x - 3):min(w, x + 4)].max(axis=1)
                    ys = np.where(col > 0)[0]
                    if len(ys) == 0:
                        pts_out.append([int(mid[0]), int(mid[1])])
                        continue
                    best_y = ys[np.argmin(np.abs(ys - mid[1]))]
                    pts_out.append([x, int(best_y)])
                else:
                    y = int(mid[1])
                    row = mask[max(0, y - 3):min(h, y + 4), :].max(axis=0)
                    xs = np.where(row > 0)[0]
                    if len(xs) == 0:
                        pts_out.append([int(mid[0]), int(mid[1])])
                        continue
                    best_x = xs[np.argmin(np.abs(xs - mid[0]))]
                    pts_out.append([int(best_x), y])
            return [[int(p[0] * scale), int(p[1] * scale)] for p in pts_out]

        self.canvas.corners = [[int(p[0] * scale), int(p[1] * scale)] for p in ordered]
        self.canvas.sides = [
            scan_side(tl, tr, axis=0),
            scan_side(tr, br, axis=1),
            scan_side(br, bl, axis=0),
            scan_side(bl, tl, axis=1),
        ]
        self.canvas.phase = 1
        self.canvas.update_display()
        self.flash_status("✔ Auto scan complete — adjust if needed")

    # ── Keyboard / DnD ────────────────────────────────────────────────────────
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Left:
            self.prev_image()
        elif event.key() == Qt.Key.Key_Right:
            self.next_image()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self._set_folder(file_path)
            self._load_image_from_path(file_path)

    def restart_app(self):
        state = {"settings": self.canvas.settings, "text_serial": self._text_serial}
        if self.current_image_path:
            state["last_image"] = self.current_image_path
        CONFIG_FILE.write_text(json.dumps(state), encoding="utf-8")
        QApplication.quit()
        os.execv(sys.executable, [sys.executable, str(Path(__file__).resolve())])


def main():
    app = QApplication(sys.argv)
    window = FreeformCropGUI()
    window.show()
    if CONFIG_FILE.exists():
        try:
            state = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            if "settings" in state:
                window.canvas.settings.update(state["settings"])
            if "text_serial" in state:
                window._text_serial = int(state["text_serial"])
            last = state.get("last_image", "")
            if last and Path(last).exists():
                window._set_folder(last)
                window._load_image_from_path(last)
        except Exception:
            pass
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
