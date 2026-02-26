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
        self.points = []
        self.dragging = None
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)
    
    def load_image(self, path):
        self.image = cv2.imread(path)
        if self.image is None:
            return False
        self.points = []
        self.update_display()
        return True
    
    def update_display(self):
        if self.image is None:
            return
        
        h, w = self.image.shape[:2]
        canvas_w, canvas_h = self.width(), self.height()
        
        # Calculate scale to fit
        scale_w = canvas_w / w
        scale_h = canvas_h / h
        self.scale = min(scale_w, scale_h, 1.0)
        
        display_w = int(w * self.scale)
        display_h = int(h * self.scale)
        
        self.offset_x = (canvas_w - display_w) // 2
        self.offset_y = (canvas_h - display_h) // 2
        
        # Resize image
        self.display_image = cv2.resize(self.image, (display_w, display_h))
        
        # Draw points and lines
        if len(self.points) > 1:
            for i in range(len(self.points)):
                pt1 = self.points[i]
                pt2 = self.points[(i + 1) % len(self.points)]
                cv2.line(self.display_image, tuple(pt1), tuple(pt2), (0, 255, 0), 2)
        
        for pt in self.points:
            cv2.circle(self.display_image, tuple(pt), 6, (0, 0, 255), -1)
            cv2.circle(self.display_image, tuple(pt), 7, (0, 240, 255), 1)
        
        # Convert to QPixmap
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
    
    def mousePressEvent(self, event):
        if self.image is None or event.button() != Qt.MouseButton.LeftButton:
            return
        
        x = event.pos().x() - self.offset_x
        y = event.pos().y() - self.offset_y
        
        # Check if clicking near existing point
        for i, pt in enumerate(self.points):
            if np.linalg.norm(np.array([x, y]) - np.array(pt)) < 10:
                self.dragging = i
                return
        
        # Add new point
        self.points.append([x, y])
        self.update_display()
    
    def mouseMoveEvent(self, event):
        if self.dragging is not None:
            x = event.pos().x() - self.offset_x
            y = event.pos().y() - self.offset_y
            self.points[self.dragging] = [x, y]
            self.update_display()
    
    def mouseReleaseEvent(self, event):
        self.dragging = None
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.image is not None:
            self.update_display()
    
    def reset_points(self):
        self.points = []
        self.update_display()
    
    def crop_image(self):
        if self.image is None or len(self.points) < 3:
            return None
        
        # Convert points back to original scale
        original_points = np.array([[int(p[0] / self.scale), int(p[1] / self.scale)] 
                                   for p in self.points], dtype=np.float32)
        
        # For 4 points, do perspective transform
        if len(self.points) == 4:
            rect = self.order_points(original_points)
            (tl, tr, br, bl) = rect
            
            widthA = np.linalg.norm(br - bl)
            widthB = np.linalg.norm(tr - tl)
            maxWidth = int(max(widthA, widthB))
            
            heightA = np.linalg.norm(tr - br)
            heightB = np.linalg.norm(tl - bl)
            maxHeight = int(max(heightA, heightB))
            
            dst = np.array([[0, 0], [maxWidth - 1, 0], 
                           [maxWidth - 1, maxHeight - 1], [0, maxHeight - 1]], dtype=np.float32)
            
            M = cv2.getPerspectiveTransform(rect, dst)
            return cv2.warpPerspective(self.image, M, (maxWidth, maxHeight))
        
        # For other polygons, create mask and crop
        else:
            mask = np.zeros(self.image.shape[:2], dtype=np.uint8)
            cv2.fillPoly(mask, [original_points.astype(np.int32)], 255)
            
            x, y, w, h = cv2.boundingRect(original_points.astype(np.int32))
            masked = cv2.bitwise_and(self.image, self.image, mask=mask)
            return masked[y:y+h, x:x+w]
    
    def order_points(self, pts):
        rect = np.zeros((4, 2), dtype=np.float32)
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        return rect


class FreeformCropGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FREEFORM CROP")
        self.resize(1000, 700)
        
        self.current_image_path = None
        
        # Apply Theme
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
        
        # Layout
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        # Canvas
        self.canvas = ImageCanvas()
        main_layout.addWidget(self.canvas)
        
        # Controls
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
        
        self.info_label = QLabel("Click to add points • Drag to move • 4 points = perspective correction")
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
                self.info_label.setText(f"Loaded: {Path(file_path).name}")
            else:
                QMessageBox.critical(self, "Error", "Failed to load image")
    
    def crop_and_save(self):
        if self.canvas.image is None:
            QMessageBox.warning(self, "Warning", "No image loaded")
            return
        
        if len(self.canvas.points) < 3:
            QMessageBox.warning(self, "Warning", "Need at least 3 points to crop")
            return
        
        result = self.canvas.crop_image()
        if result is None:
            QMessageBox.critical(self, "Error", "Crop failed")
            return
        
        # Save dialog
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
