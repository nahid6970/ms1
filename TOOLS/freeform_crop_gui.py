import sys
import os
import json
from pathlib import Path
from datetime import datetime
import cv2
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QFileDialog, QMessageBox, QSpinBox,
                             QDialog, QFormLayout, QLineEdit, QColorDialog, QDialogButtonBox)
from PyQt6.QtCore import Qt, QTimer, QByteArray, QSize, QPoint, QRect
from PyQt6.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QCursor, QIcon, QFont
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

CONFIG_FILE = Path(__file__).parent / ".freeform_crop_last.txt"
SETTINGS_FILE = Path(__file__).parent / ".freeform_crop_settings.json"


def make_btn(label, accent, text_on_press="black"):
    ss = (f"QPushButton {{ background-color: {CP_DIM}; border: 1px solid {accent}; "
          f"color: {accent}; padding: 8px 16px; font-weight: bold; }}"
          f"QPushButton:hover {{ background-color: {accent}22; border: 1px solid {accent}; color: {accent}; }}"
          f"QPushButton:pressed {{ background-color: {accent}; color: {text_on_press}; }}")
    b = QPushButton(label)
    b.setStyleSheet(ss)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    return b


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
        layout.addRow("Font size:", self.font_spin)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

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

    def get_settings(self):
        return {
            "subpts": self.spin.value(),
            "text_fg": self.settings["text_fg"],
            "text_bg": self.settings["text_bg"],
            "text_border": self.settings["text_border"],
            "font_size": self.font_spin.value(),
        }


class TextOverlay:
    """Represents a draggable text box on the canvas."""
    def __init__(self, text, x, y, settings):
        self.text = text
        self.x = x  # display coords
        self.y = y
        self.settings = settings

    def get_rect(self, painter_fm):
        """Return bounding QRect for this text label in display coords."""
        fm = painter_fm
        tw = fm.horizontalAdvance(self.text) + 12
        th = fm.height() + 8
        return QRect(self.x, self.y, tw, th)


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
                rect = ov.get_rect(fm)
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
            rect = ov.get_rect(fm)
            if rect.contains(x, y):
                return i
        return -1

    def mousePressEvent(self, event):
        if self.image is None or event.button() != Qt.MouseButton.LeftButton:
            return

        x = event.pos().x() - self.offset_x
        y = event.pos().y() - self.offset_y

        # Check text overlays first
        idx = self._hit_text(x, y)
        if idx >= 0:
            self.dragging_text = idx
            ov = self.text_overlays[idx]
            self.drag_offset = QPoint(x - ov.x, y - ov.y)
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
            ov.x = x - self.drag_offset.x()
            ov.y = y - self.drag_offset.y()
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

        btn_autoscan = make_btn("AUTO SCAN", "#00BFFF")
        btn_autoscan.clicked.connect(self.auto_scan)

        btn_add_text = make_btn("ADD TEXT", "#FF8C00")
        btn_add_text.clicked.connect(self.add_text_overlay)

        btn_settings = make_btn("⚙ SETTINGS", "#9E9E9E", "black")
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
        controls.addWidget(btn_reset)
        controls.addWidget(btn_autoscan)
        controls.addWidget(btn_settings)
        controls.addWidget(btn_add_text)
        controls.addWidget(btn_crop)
        controls.addWidget(btn_overwrite)
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
            SETTINGS_FILE.write_text(json.dumps(self.canvas.settings), encoding="utf-8")
            self.canvas.update_display()

    # ── Text overlay ──────────────────────────────────────────────────────────
    def add_text_overlay(self):
        if self.canvas.image is None:
            return
        # Default position: bottom-right area of canvas image
        cw = self.canvas.width() - self.canvas.offset_x
        ch = self.canvas.height() - self.canvas.offset_y
        x = max(0, cw - 150)
        y = max(0, ch - 60)
        ov = TextOverlay("Text", x, y, dict(self.canvas.settings))
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
        font_size = self.canvas.settings["font_size"]
        font = QFont("Consolas", font_size)
        painter.setFont(font)
        fm = painter.fontMetrics()

        # Scale text positions from display coords to output image coords
        scale_x = w / (self.canvas.width() - 2 * self.canvas.offset_x) if self.canvas.scale else 1
        scale_y = h / (self.canvas.height() - 2 * self.canvas.offset_y) if self.canvas.scale else 1

        for ov in self.canvas.text_overlays:
            ox = int(ov.x * scale_x)
            oy = int(ov.y * scale_y)
            tw = fm.horizontalAdvance(ov.text) + 12
            th = fm.height() + 8
            rect = QRect(ox, oy, tw, th)
            painter.fillRect(rect, QColor(ov.settings["text_bg"]))
            painter.setPen(QPen(QColor(ov.settings["text_border"]), 1))
            painter.drawRect(rect)
            painter.setPen(QColor(ov.settings["text_fg"]))
            painter.drawText(rect.adjusted(6, 4, -6, -4), Qt.AlignmentFlag.AlignCenter, ov.text)
        painter.end()

        result = pixmap.toImage().convertToFormat(QImage.Format.Format_RGB888)
        ptr = result.bits()
        ptr.setsize(result.sizeInBytes())
        arr = np.frombuffer(ptr, dtype=np.uint8).reshape((h, w, 3))
        return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

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
            self.flash_status(f"✔ Overwritten: {Path(self.current_image_path).name}")
        else:
            QMessageBox.warning(self, "Warning", "No source path available")

    def rotate_image(self):
        if self.canvas.image is None:
            return
        self.canvas.image = cv2.rotate(self.canvas.image, cv2.ROTATE_90_CLOCKWISE)
        self.canvas.reset_points()

    def flash_status(self, msg, duration=3000):
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
        edges = cv2.Canny(blurred, 30, 100)
        edges = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=2)

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        best_cnt = None
        img_area = w * h
        for cnt in contours[:10]:
            area = cv2.contourArea(cnt)
            if area < img_area * 0.10 or area > img_area * 0.98:
                continue
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            if len(approx) == 4:
                best_cnt = cnt
                corners_approx = approx.reshape(4, 2).astype(np.float32)
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
        if self.current_image_path:
            CONFIG_FILE.write_text(self.current_image_path, encoding="utf-8")
        SETTINGS_FILE.write_text(json.dumps(self.canvas.settings), encoding="utf-8")
        QApplication.quit()
        os.execv(sys.executable, [sys.executable, str(Path(__file__).resolve())])


def main():
    app = QApplication(sys.argv)
    window = FreeformCropGUI()
    window.show()
    if SETTINGS_FILE.exists():
        try:
            window.canvas.settings.update(json.loads(SETTINGS_FILE.read_text(encoding="utf-8")))
        except Exception:
            pass
    if CONFIG_FILE.exists():
        last = CONFIG_FILE.read_text(encoding="utf-8").strip()
        if last and Path(last).exists():
            window._set_folder(last)
            window._load_image_from_path(last)
        CONFIG_FILE.unlink(missing_ok=True)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
