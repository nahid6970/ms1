import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QSlider, QSpinBox, QFileDialog, QMessageBox,
    QFrame, QCheckBox, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QMimeData, QSize
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QPixmap, QIcon, QFont, QColor
from PIL import Image

class DragDropLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("Drag & Drop Image Here\nor Click to Browse")
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #6c7086;
                border-radius: 12px;
                background-color: #313244;
                color: #cdd6f4;
                font-size: 16px;
                font-weight: bold;
            }
            QLabel:hover {
                border-color: #89b4fa;
                background-color: #45475a;
            }
        """)
        self.setAcceptDrops(True)
        self.parent_window = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.parent_window:
                self.parent_window.browse_image()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if self.parent_window:
                self.parent_window.load_image(file_path)

class ModernSlider(QSlider):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #313244;
                height: 8px;
                background: #313244;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #89b4fa;
                border: 1px solid #89b4fa;
                width: 18px;
                height: 18px;
                margin: -7px 0;
                border-radius: 9px;
            }
            QSlider::sub-page:horizontal {
                background: #89b4fa;
                border-radius: 4px;
            }
        """)

class ImageResizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Antigravity Image Resizer")
        self.resize(600, 600)
        self.current_image_path = None
        self.original_image = None
        self.original_width = 0
        self.original_height = 0
        self.aspect_ratio = 1.0

        # Styles
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e2e;
                color: #cdd6f4;
            }
            QWidget {
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }
            QLabel {
                color: #cdd6f4;
            }
            QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #b4befe;
            }
            QPushButton:pressed {
                background-color: #74c7ec;
            }
            QSpinBox {
                background-color: #313244;
                border: 1px solid #45475a;
                border-radius: 6px;
                color: #cdd6f4;
                padding: 6px 8px;
                font-weight: bold;
                selection-background-color: #585b70;
            }
            QSpinBox:focus {
                border: 1px solid #89b4fa;
            }
            QCheckBox {
                spacing: 8px;
                color: #cdd6f4;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #6c7086;
            }
            QCheckBox::indicator:checked {
                background-color: #89b4fa;
                border-color: #89b4fa;
            }
        """)

        # Main Widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Layouts
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Title
        title_label = QLabel("Image Resizer")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #89b4fa; margin-bottom: 5px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Drop Zone
        self.drop_label = DragDropLabel()
        self.drop_label.parent_window = self
        self.drop_label.setMinimumHeight(140)
        main_layout.addWidget(self.drop_label)

        # File Info Frame
        self.info_frame = QFrame()
        self.info_frame.setStyleSheet("background-color: #313244; border-radius: 12px; padding: 10px;")
        info_layout = QVBoxLayout(self.info_frame)
        
        self.filename_label = QLabel("No file selected")
        self.filename_label.setStyleSheet("color: #a6adc8; font-style: italic;")
        self.filename_label.setWordWrap(True)
        self.filename_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.original_info_label = QLabel("Original Size: -")
        self.original_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.original_info_label.setStyleSheet("font-weight: bold; color: #f38ba8;")

        info_layout.addWidget(self.filename_label)
        info_layout.addWidget(self.original_info_label)
        main_layout.addWidget(self.info_frame)

        # Controls Container
        controls_group = QWidget()
        controls_layout = QVBoxLayout(controls_group)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        
        # Dimensions Row (Width x Height)
        dims_layout = QHBoxLayout()
        
        # Width Input
        width_container = QVBoxLayout()
        width_label = QLabel("Width")
        width_label.setStyleSheet("font-weight: bold; color: #a6e3a1;")
        self.width_spinbox = QSpinBox()
        self.width_spinbox.setRange(1, 99999)
        self.width_spinbox.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons) # Remove arrows
        self.width_spinbox.valueChanged.connect(self.on_width_changed)
        width_container.addWidget(width_label)
        width_container.addWidget(self.width_spinbox)
        
        # X label
        x_label = QLabel("x")
        x_label.setStyleSheet("font-size: 18px; color: #6c7086; margin-top: 20px;")
        
        # Height Input
        height_container = QVBoxLayout()
        height_label = QLabel("Height")
        height_label.setStyleSheet("font-weight: bold; color: #a6e3a1;")
        self.height_spinbox = QSpinBox()
        self.height_spinbox.setRange(1, 99999)
        self.height_spinbox.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons) # Remove arrows
        self.height_spinbox.valueChanged.connect(self.on_height_changed)
        height_container.addWidget(height_label)
        height_container.addWidget(self.height_spinbox)

        dims_layout.addLayout(width_container)
        dims_layout.addWidget(x_label)
        dims_layout.addLayout(height_container)
        
        controls_layout.addLayout(dims_layout)

        # Aspect Ratio Checkbox
        self.aspect_ratio_cb = QCheckBox("Lock Aspect Ratio")
        self.aspect_ratio_cb.setChecked(True)
        self.aspect_ratio_cb.setStyleSheet("margin-top: 5px;")
        controls_layout.addWidget(self.aspect_ratio_cb, alignment=Qt.AlignmentFlag.AlignCenter)

        # Slider Section
        slider_container = QWidget()
        slider_container.setStyleSheet("margin-top: 10px;")
        slider_inner_layout = QVBoxLayout(slider_container)

        slider_header = QHBoxLayout()
        scale_label = QLabel("Scale:")
        self.scale_value_display = QLabel("100%")
        self.scale_value_display.setStyleSheet("color: #89b4fa; font-weight: bold;")
        slider_header.addWidget(scale_label)
        slider_header.addStretch()
        slider_header.addWidget(self.scale_value_display)
        
        self.scale_slider = ModernSlider(Qt.Orientation.Horizontal)
        self.scale_slider.setRange(1, 300)
        self.scale_slider.setValue(100)
        self.scale_slider.valueChanged.connect(self.on_slider_changed)

        slider_inner_layout.addLayout(slider_header)
        slider_inner_layout.addWidget(self.scale_slider)
        
        controls_layout.addWidget(slider_container)
        main_layout.addWidget(controls_group)

        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save Image")
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.clicked.connect(self.save_image)
        self.save_btn.setEnabled(False) 
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                padding: 12px 30px;
                font-size: 16px;
            }
            QPushButton:disabled {
                background-color: #45475a;
                color: #6c7086;
            }
        """)

        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        main_layout.addStretch()

        # State flags
        self.updating_ui = False

    def browse_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.webp *.tiff)"
        )
        if file_name:
            self.load_image(file_name)

    def load_image(self, file_path):
        try:
            self.updating_ui = True
            
            self.current_image_path = file_path
            self.original_image = Image.open(file_path)
            self.original_width, self.original_height = self.original_image.size
            
            # Avoid division by zero
            if self.original_height > 0:
                self.aspect_ratio = self.original_width / self.original_height
            else:
                self.aspect_ratio = 1.0
            
            # Update UI Info
            self.filename_label.setText(os.path.basename(file_path))
            self.original_info_label.setText(f"Original: {self.original_width} x {self.original_height} px")
            
            self.drop_label.setText("Image Loaded!\nClick to Change")
            self.drop_label.setStyleSheet("""
                QLabel {
                    border: 2px solid #a6e3a1;
                    border-radius: 12px;
                    background-color: #313244;
                    color: #a6e3a1;
                    font-size: 16px;
                    font-weight: bold;
                }
                QLabel:hover {
                    background-color: #45475a;
                }
            """)
            
            # Init values
            self.width_spinbox.setValue(self.original_width)
            self.height_spinbox.setValue(self.original_height)
            self.scale_slider.setValue(100)
            self.scale_value_display.setText("100%")
            
            self.save_btn.setEnabled(True)
            self.updating_ui = False
            
        except Exception as e:
            self.updating_ui = False
            QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")

    def on_width_changed(self, new_width):
        if self.updating_ui or not self.original_image:
            return
        
        self.updating_ui = True
        
        if self.aspect_ratio_cb.isChecked() and self.aspect_ratio > 0:
            new_height = int(new_width / self.aspect_ratio)
            self.height_spinbox.setValue(new_height)
        
        # Update slider roughly
        if self.original_width > 0:
            percentage = int((new_width / self.original_width) * 100)
            # Unblock signals for slider if needed, but we don't want it to trigger on_slider_changed
            self.scale_slider.blockSignals(True)
            self.scale_slider.setValue(percentage)
            self.scale_slider.blockSignals(False)
            self.scale_value_display.setText(f"{percentage}%")

        self.updating_ui = False

    def on_height_changed(self, new_height):
        if self.updating_ui or not self.original_image:
            return
            
        self.updating_ui = True
        
        if self.aspect_ratio_cb.isChecked():
            new_width = int(new_height * self.aspect_ratio)
            self.width_spinbox.setValue(new_width)
            
        # Update slider roughly
        if self.original_height > 0:
            percentage = int((new_height / self.original_height) * 100)
            self.scale_slider.blockSignals(True)
            self.scale_slider.setValue(percentage)
            self.scale_slider.blockSignals(False)
            self.scale_value_display.setText(f"{percentage}%")

        self.updating_ui = False

    def on_slider_changed(self, value):
        if self.updating_ui or not self.original_image:
            self.scale_value_display.setText(f"{value}%")
            return
            
        self.updating_ui = True
        self.scale_value_display.setText(f"{value}%")
        
        scale_factor = value / 100.0
        new_width = int(self.original_width * scale_factor)
        new_height = int(self.original_height * scale_factor)
        
        self.width_spinbox.setValue(new_width)
        # Height will auto-update via on_width_changed if chained, but let's set it explicitly to avoid rounding chains
        self.height_spinbox.blockSignals(True)
        self.height_spinbox.setValue(new_height)
        self.height_spinbox.blockSignals(False)
        
        self.updating_ui = False

    def save_image(self):
        if not self.original_image:
            return

        new_w = self.width_spinbox.value()
        new_h = self.height_spinbox.value()

        if new_w <= 0 or new_h <= 0:
             QMessageBox.warning(self, "Invalid Size", "Width and Height must be greater than 0.")
             return

        default_name = f"{os.path.splitext(os.path.basename(self.current_image_path))[0]}_{new_w}x{new_h}"
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save Image", default_name, "PNG (*.png);;JPEG (*.jpg);;WEBP (*.webp)"
        )

        if save_path:
            try:
                # Resize
                resized_img = self.original_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
                resized_img.save(save_path)
                
                QMessageBox.information(self, "Success", "Image saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save image: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set app-wide font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = ImageResizerApp()
    window.show()
    sys.exit(app.exec())
