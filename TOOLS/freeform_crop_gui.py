import sys
import os
from pathlib import Path
import cv2
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QCursor

# PALETTE
CP_BG = "#050505"
CP_PANEL = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN = "#00F0FF"
CP_RED = "#FF003C"
CP_GREEN = "#00ff21"
CP_DIM = "#3a3a3a"
CP_TEXT = "#E0E0E0"

class ImageCanvas(QLabel):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 600)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(f"background-color: {CP_PANEL}; border: 1px solid {CP_DIM};")
        
        self.image = None
        self.display_image = None
        self.corners = []  # 4 main corner points
        self.sides = [[], [], [], []]  # sub-points for top, right, bottom, left
        self.dragging = None
        self.phase = 0  # 0=setting corners, 1=adding sub-points
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)
    
    def load_image(self, path):
        self.image = cv2.imread(path)
        if self.image is None:
            return False
        self.corners = []
        self.sides = [[], [], [], []]
        self.phase = 0
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
                side_points = [self.corners[i]] + self.sides[i] + [self.corners[(i+1)%4]]
                for j in range(len(side_points)-1):
                    cv2.line(self.display_image, tuple(side_points[j]), tuple(side_points[j+1]), (0, 255, 0), 2)
                
                # Draw sub-points
                for pt in self.sides[i]:
                    cv2.circle(self.display_image, tuple(pt), 5, (255, 255, 0), -1)
        elif len(self.corners) > 1:
            for i in range(len(self.corners)):
                cv2.line(self.display_image, tuple(self.corners[i]), tuple(self.corners[(i+1)%len(self.corners)]), (0, 255, 0), 2)
        
        # Draw corners
        for pt in self.corners:
            cv2.circle(self.display_image, tuple(pt), 6, (0, 0, 255), -1)
            cv2.circle(self.display_image, tuple(pt), 7, (0, 240, 255), 1)
        
        rgb = cv2.cvtColor(self.display_image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        
        pixmap = QPixmap(canvas_w, canvas_h)
        pixmap.fill(QColor(CP_PANEL))
        
        painter = QPainter(pixmap)
        painter.drawImage(self.offset_x, self.offset_y, qt_image)
        painter.end()
        
        self.setPixmap(pixmap)
    
    def point_to_line_distance(self, pt, line_start, line_end):
        px, py = pt
        x1, y1 = line_start
        x2, y2 = line_end
        
        line_len = np.linalg.norm(np.array([x2-x1, y2-y1]))
        if line_len == 0:
            return np.linalg.norm(np.array([px-x1, py-y1]))
        
        t = max(0, min(1, ((px-x1)*(x2-x1) + (py-y1)*(y2-y1)) / (line_len**2)))
        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)
        
        return np.linalg.norm(np.array([px-proj_x, py-proj_y])), t
    
    def mousePressEvent(self, event):
        if self.image is None or event.button() != Qt.MouseButton.LeftButton:
            return
        
        x = event.pos().x() - self.offset_x
        y = event.pos().y() - self.offset_y
        
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
        
        # Phase 0: Add corners
        if self.phase == 0:
            if len(self.corners) < 4:
                self.corners.append([x, y])
                if len(self.corners) == 4:
                    self.phase = 1
        # Phase 1: Add sub-points to sides
        else:
            best_side = None
            best_dist = float('inf')
            
            for i in range(4):
                dist, t = self.point_to_line_distance([x, y], self.corners[i], self.corners[(i+1)%4])
                if dist < best_dist and dist < 15:
                    best_dist = dist
                    best_side = (i, t)
            
            if best_side is not None:
                side_idx, t = best_side
                self.sides[side_idx].append([x, y])
                # Sort by position along the line
                self.sides[side_idx].sort(key=lambda p: self.point_to_line_distance(p, self.corners[side_idx], self.corners[(side_idx+1)%4])[1])
        
        self.update_display()
    
    def mouseMoveEvent(self, event):
        if self.dragging is not None:
            x = event.pos().x() - self.offset_x
            y = event.pos().y() - self.offset_y
            
            if self.dragging[0] == 'corner':
                self.corners[self.dragging[1]] = [x, y]
            elif self.dragging[0] == 'side':
                self.sides[self.dragging[1]][self.dragging[2]] = [x, y]
            
            self.update_display()
    
    def mouseReleaseEvent(self, event):
        self.dragging = None
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.image is not None:
            self.update_display()
    
    def reset_points(self):
        self.corners = []
        self.sides = [[], [], [], []]
        self.phase = 0
        self.update_display()
    
    def crop_image(self):
        if self.image is None or len(self.corners) != 4:
            return None
        
        # Build all points for each side
        all_sides = []
        for i in range(4):
            side_points = [self.corners[i]] + self.sides[i] + [self.corners[(i+1)%4]]
            all_sides.append(np.array([[int(p[0]/self.scale), int(p[1]/self.scale)] for p in side_points], dtype=np.float32))
        
        # Calculate output dimensions
        top_len = sum(np.linalg.norm(all_sides[0][i+1] - all_sides[0][i]) for i in range(len(all_sides[0])-1))
        bottom_len = sum(np.linalg.norm(all_sides[2][i+1] - all_sides[2][i]) for i in range(len(all_sides[2])-1))
        left_len = sum(np.linalg.norm(all_sides[3][i+1] - all_sides[3][i]) for i in range(len(all_sides[3])-1))
        right_len = sum(np.linalg.norm(all_sides[1][i+1] - all_sides[1][i]) for i in range(len(all_sides[1])-1))
        
        width = int(max(top_len, bottom_len))
        height = int(max(left_len, right_len))
        
        # Create mesh grid
        n_top = len(all_sides[0])
        n_bottom = len(all_sides[2])
        n_left = len(all_sides[3])
        n_right = len(all_sides[1])
        
        rows = max(n_left, n_right)
        cols = max(n_top, n_bottom)
        
        # Interpolate points on each side
        top_interp = self.interpolate_points(all_sides[0], cols)
        bottom_interp = self.interpolate_points(all_sides[2][::-1], cols)[::-1]
        left_interp = self.interpolate_points(all_sides[3], rows)
        right_interp = self.interpolate_points(all_sides[1][::-1], rows)[::-1]
        
        # Build mesh
        src_points = []
        dst_points = []
        
        for i in range(rows):
            t_row = i / (rows - 1) if rows > 1 else 0
            for j in range(cols):
                t_col = j / (cols - 1) if cols > 1 else 0
                
                top_pt = top_interp[j]
                bottom_pt = bottom_interp[j]
                left_pt = left_interp[i]
                right_pt = right_interp[i]
                
                # Bilinear interpolation
                src_x = (1-t_row)*(1-t_col)*top_interp[0][0] + (1-t_row)*t_col*top_interp[-1][0] + \
                        t_row*(1-t_col)*bottom_interp[0][0] + t_row*t_col*bottom_interp[-1][0]
                src_y = (1-t_row)*(1-t_col)*top_interp[0][1] + (1-t_row)*t_col*top_interp[-1][1] + \
                        t_row*(1-t_col)*bottom_interp[0][1] + t_row*t_col*bottom_interp[-1][1]
                
                # Better interpolation using all sides
                h_interp = (1-t_row) * top_pt + t_row * bottom_pt
                v_interp = (1-t_col) * left_pt + t_col * right_pt
                src_pt = (h_interp + v_interp) / 2
                
                src_points.append(src_pt)
                dst_points.append([j * width / (cols-1) if cols > 1 else 0, 
                                  i * height / (rows-1) if rows > 1 else 0])
        
        src_points = np.array(src_points, dtype=np.float32)
        dst_points = np.array(dst_points, dtype=np.float32)
        
        # Use thin plate spline or piecewise affine
        result = np.zeros((height, width, 3), dtype=np.uint8)
        
        for y in range(height):
            for x in range(width):
                # Find nearest grid points
                grid_x = x * (cols - 1) / width if width > 0 else 0
                grid_y = y * (rows - 1) / height if height > 0 else 0
                
                gx0, gx1 = int(grid_x), min(int(grid_x) + 1, cols - 1)
                gy0, gy1 = int(grid_y), min(int(grid_y) + 1, rows - 1)
                
                tx = grid_x - gx0
                ty = grid_y - gy0
                
                idx00 = gy0 * cols + gx0
                idx01 = gy0 * cols + gx1
                idx10 = gy1 * cols + gx0
                idx11 = gy1 * cols + gx1
                
                src_x = (1-tx)*(1-ty)*src_points[idx00][0] + tx*(1-ty)*src_points[idx01][0] + \
                        (1-tx)*ty*src_points[idx10][0] + tx*ty*src_points[idx11][0]
                src_y = (1-tx)*(1-ty)*src_points[idx00][1] + tx*(1-ty)*src_points[idx01][1] + \
                        (1-tx)*ty*src_points[idx10][1] + tx*ty*src_points[idx11][1]
                
                src_x, src_y = int(src_x), int(src_y)
                if 0 <= src_x < self.image.shape[1] and 0 <= src_y < self.image.shape[0]:
                    result[y, x] = self.image[src_y, src_x]
        
        return result
    
    def interpolate_points(self, points, n):
        if len(points) == 0:
            return np.zeros((n, 2))
        if len(points) == 1:
            return np.tile(points[0], (n, 1))
        
        # Calculate cumulative distances
        dists = [0]
        for i in range(len(points)-1):
            dists.append(dists[-1] + np.linalg.norm(points[i+1] - points[i]))
        
        total_dist = dists[-1]
        if total_dist == 0:
            return np.tile(points[0], (n, 1))
        
        # Interpolate
        result = []
        for i in range(n):
            target_dist = i * total_dist / (n - 1) if n > 1 else 0
            
            # Find segment
            for j in range(len(dists)-1):
                if dists[j] <= target_dist <= dists[j+1]:
                    seg_len = dists[j+1] - dists[j]
                    if seg_len == 0:
                        result.append(points[j])
                    else:
                        t = (target_dist - dists[j]) / seg_len
                        result.append((1-t) * points[j] + t * points[j+1])
                    break
            else:
                result.append(points[-1])
        
        return np.array(result)


class FreeformCropGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FREEFORM CROP")
        self.resize(1000, 700)
        
        self.current_image_path = None
        
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
            QPushButton:pressed {{
                background-color: {CP_YELLOW}; color: black;
            }}
            
            QLabel {{ color: {CP_TEXT}; }}
        """)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        self.canvas = ImageCanvas()
        main_layout.addWidget(self.canvas)
        
        controls = QHBoxLayout()
        
        btn_load = QPushButton("LOAD IMAGE")
        btn_load.clicked.connect(self.load_image)
        btn_load.setCursor(Qt.CursorShape.PointingHandCursor)
        
        btn_reset = QPushButton("RESET POINTS")
        btn_reset.clicked.connect(self.canvas.reset_points)
        btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        
        btn_crop = QPushButton("CROP & SAVE")
        btn_crop.clicked.connect(self.crop_and_save)
        btn_crop.setCursor(Qt.CursorShape.PointingHandCursor)
        
        btn_restart = QPushButton("RESTART")
        btn_restart.clicked.connect(self.restart_app)
        btn_restart.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.info_label = QLabel("Phase 1: Click 4 corners • Phase 2: Click edges to add sub-points")
        self.info_label.setStyleSheet(f"color: {CP_CYAN}; font-size: 9pt;")
        
        controls.addWidget(btn_load)
        controls.addWidget(btn_reset)
        controls.addWidget(btn_crop)
        controls.addWidget(btn_restart)
        controls.addStretch()
        controls.addWidget(self.info_label)
        
        main_layout.addLayout(controls)
    
    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        if file_path:
            if self.canvas.load_image(file_path):
                self.current_image_path = file_path
                self.info_label.setText(f"Loaded: {Path(file_path).name} | Phase 1: Set 4 corners")
            else:
                QMessageBox.critical(self, "Error", "Failed to load image")
    
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
        
        default_name = "cropped_output.png"
        if self.current_image_path:
            stem = Path(self.current_image_path).stem
            default_name = f"{stem}_cropped.png"
        
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save Cropped Image", default_name, "PNG (*.png);;JPEG (*.jpg);;All Files (*)"
        )
        
        if save_path:
            cv2.imwrite(save_path, result)
            QMessageBox.information(self, "Success", f"Saved to:\n{save_path}")
    
    def restart_app(self):
        QApplication.quit()
        os.execv(sys.executable, [sys.executable] + sys.argv)


def main():
    app = QApplication(sys.argv)
    window = FreeformCropGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
