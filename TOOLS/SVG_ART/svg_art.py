import sys
import os
import math
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QToolBar, QFileDialog, QColorDialog, QSlider, 
                             QLabel, QGraphicsView, QGraphicsScene, QGraphicsPathItem,
                             QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsLineItem,
                             QGraphicsPixmapItem, QFrame, QGroupBox, QFormLayout, QDialog, QSizePolicy)
from PyQt6.QtCore import Qt, QPointF, QRectF, QLineF
from PyQt6.QtGui import (QPainter, QPen, QColor, QPainterPath, QPixmap, QCursor, QAction, QIcon, QTransform)
from PyQt6 import QtSvg
from PyQt6.QtSvg import QSvgGenerator

# CYBERPUNK THEME PALETTE
CP_BG = "#050505"
CP_PANEL = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN = "#00F0FF"
CP_RED = "#FF003C"
CP_GREEN = "#00ff21"
CP_ORANGE = "#ff934b"
CP_DIM = "#3a3a3a"
CP_TEXT = "#E0E0E0"
CP_SUBTEXT = "#808080"

class SmoothPathItem(QGraphicsPathItem):
    def __init__(self, path=None, parent=None):
        super().__init__(path, parent)
        self.setAcceptHoverEvents(True)

class ArtScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackgroundBrush(QColor(CP_BG))
        self.setSceneRect(-5000, -5000, 10000, 10000)

class ArtView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setStyleSheet(f"background-color: {CP_BG}; border: 1px solid {CP_DIM};")
        
        self.drawing = False
        self.current_item = None
        self.start_point = QPointF()
        
        self.tool = "pen" # pen, eraser, rect, ellipse, line, move_image, move_svg
        self.pen_color = QColor(CP_CYAN)
        self.pen_width = 3
        
        self.image_item = None
        self.zoom_level = 1.0

    def wheelEvent(self, event):
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
        self.scale(zoom_factor, zoom_factor)
        self.zoom_level *= zoom_factor

    def mousePressEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        self.start_point = scene_pos
        
        if event.button() == Qt.MouseButton.LeftButton:
            if self.tool == "pen":
                self.drawing = True
                path = QPainterPath()
                path.moveTo(scene_pos)
                self.current_item = SmoothPathItem(path)
                pen = QPen(self.pen_color, self.pen_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
                self.current_item.setPen(pen)
                self.scene().addItem(self.current_item)
            
            elif self.tool in ["rect", "ellipse", "line"]:
                self.drawing = True
                pen = QPen(self.pen_color, self.pen_width)
                if self.tool == "rect":
                    self.current_item = QGraphicsRectItem(QRectF(scene_pos, scene_pos))
                elif self.tool == "ellipse":
                    self.current_item = QGraphicsEllipseItem(QRectF(scene_pos, scene_pos))
                elif self.tool == "line":
                    self.current_item = QGraphicsLineItem(QLineF(scene_pos, scene_pos))
                
                self.current_item.setPen(pen)
                self.scene().addItem(self.current_item)
            
            elif self.tool == "eraser":
                self.drawing = True
                self.erase_at(scene_pos)
                
            elif self.tool == "move_image":
                if self.image_item:
                    self.drawing = True
            
            elif self.tool == "move_svg":
                self.drawing = True
        
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        
        if self.drawing:
            if self.tool == "pen" and isinstance(self.current_item, QGraphicsPathItem):
                path = self.current_item.path()
                path.lineTo(scene_pos)
                self.current_item.setPath(path)
            
            elif self.tool == "rect" and isinstance(self.current_item, QGraphicsRectItem):
                rect = QRectF(self.start_point, scene_pos).normalized()
                self.current_item.setRect(rect)
                
            elif self.tool == "ellipse" and isinstance(self.current_item, QGraphicsEllipseItem):
                rect = QRectF(self.start_point, scene_pos).normalized()
                self.current_item.setRect(rect)
                
            elif self.tool == "line" and isinstance(self.current_item, QGraphicsLineItem):
                self.current_item.setLine(QLineF(self.start_point, scene_pos))
            
            elif self.tool == "eraser":
                self.erase_at(scene_pos)
                
            elif self.tool == "move_image":
                if self.image_item:
                    delta = scene_pos - self.start_point
                    self.image_item.setPos(self.image_item.pos() + delta)
                    self.start_point = scene_pos
            
            elif self.tool == "move_svg":
                delta = scene_pos - self.start_point
                for item in self.scene().items():
                    if item != self.image_item and not isinstance(item, QGraphicsPixmapItem):
                        item.setPos(item.pos() + delta)
                self.start_point = scene_pos

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False
            self.current_item = None
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
        super().mouseReleaseEvent(event)

    def erase_at(self, pos):
        items = self.scene().items(pos)
        for item in items:
            if item != self.image_item and not isinstance(item, QGraphicsPixmapItem):
                self.scene().removeItem(item)

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SYSTEM SETTINGS")
        self.resize(300, 200)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {CP_BG}; border: 1px solid {CP_CYAN}; }}
            QLabel {{ color: {CP_YELLOW}; font-weight: bold; }}
            QPushButton {{ background-color: {CP_DIM}; color: white; border: 1px solid {CP_DIM}; padding: 5px; }}
            QPushButton:hover {{ border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }}
        """)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("--- CUSTOMIZATION PANEL ---"))
        layout.addWidget(QLabel("(Empty for now - add your settings here)"))
        
        close_btn = QPushButton("CLOSE")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

class SVGArtApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NEURAL ART V1.0 - SVG EDITOR")
        self.resize(1200, 800)
        
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Toolbar
        self.toolbar = QToolBar("Main Tools")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)
        
        # Tools Actions
        self.add_tool_action("PEN", "pen", CP_CYAN)
        self.add_tool_action("ERASER", "eraser", CP_RED)
        self.add_tool_action("RECT", "rect", CP_YELLOW)
        self.add_tool_action("CIRCLE", "ellipse", CP_YELLOW)
        self.add_tool_action("LINE", "line", CP_YELLOW)
        self.toolbar.addSeparator()
        self.add_tool_action("MOVE IMG", "move_image", CP_ORANGE)
        self.add_tool_action("MOVE SVG", "move_svg", CP_GREEN)
        self.toolbar.addSeparator()
        
        self.btn_color = QPushButton("COLOR")
        self.btn_color.clicked.connect(self.choose_color)
        self.toolbar.addWidget(self.btn_color)
        
        self.toolbar.addWidget(QLabel(" THICK: "))
        self.thickness_slider = QSlider(Qt.Orientation.Horizontal)
        self.thickness_slider.setRange(1, 50)
        self.thickness_slider.setValue(3)
        self.thickness_slider.setFixedWidth(100)
        self.thickness_slider.valueChanged.connect(self.change_thickness)
        self.toolbar.addWidget(self.thickness_slider)
        
        self.toolbar.addSeparator()
        
        btn_load = QPushButton("LOAD IMG")
        btn_load.clicked.connect(self.load_image)
        self.toolbar.addWidget(btn_load)
        
        btn_save = QPushButton("SAVE SVG")
        btn_save.clicked.connect(self.save_svg)
        self.toolbar.addWidget(btn_save)
        
        self.toolbar.addSeparator()
        
        btn_zoom_in = QPushButton("+")
        btn_zoom_in.clicked.connect(lambda: self.view.scale(1.2, 1.2))
        self.toolbar.addWidget(btn_zoom_in)
        
        btn_zoom_out = QPushButton("-")
        btn_zoom_out.clicked.connect(lambda: self.view.scale(0.8, 0.8))
        self.toolbar.addWidget(btn_zoom_out)
        
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.toolbar.addWidget(spacer)
        
        btn_restart = QPushButton("RESTART")
        btn_restart.clicked.connect(self.restart_app)
        self.toolbar.addWidget(btn_restart)
        
        btn_settings = QPushButton("SET")
        btn_settings.clicked.connect(self.show_settings)
        self.toolbar.addWidget(btn_settings)

        # Scene and View
        self.scene = ArtScene()
        self.view = ArtView(self.scene)
        self.main_layout.addWidget(self.view)
        
        # Status Bar
        self.statusBar().showMessage("SYSTEM ONLINE")

    def add_tool_action(self, text, tool_name, color):
        btn = QPushButton(text)
        btn.setStyleSheet(f"color: {color}; font-weight: bold;")
        btn.clicked.connect(lambda: self.set_tool(tool_name))
        self.toolbar.addWidget(btn)

    def set_tool(self, tool):
        self.view.tool = tool
        self.statusBar().showMessage(f"TOOL ACTIVE: {tool.upper()}")

    def choose_color(self):
        color = QColorDialog.getColor(self.view.pen_color, self, "CHOOSE NEURAL COLOR")
        if color.isValid():
            self.view.pen_color = color
            self.btn_color.setStyleSheet(f"background-color: {color.name()}; color: {'black' if color.lightness() > 128 else 'white'};")

    def change_thickness(self, value):
        self.view.pen_width = value

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "LOAD BACKGROUND IMAGE", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                if self.view.image_item:
                    self.scene.removeItem(self.view.image_item)
                self.view.image_item = QGraphicsPixmapItem(pixmap)
                self.view.image_item.setZValue(-1) # Behind everything
                self.scene.addItem(self.view.image_item)
                self.statusBar().showMessage(f"IMAGE LOADED: {os.path.basename(file_path)}")

    def save_svg(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "SAVE NEURAL ART", "art_output.svg", "SVG files (*.svg)")
        if file_path:
            # We want to save the scene items as SVG
            # Only SVG items, maybe excluding the background image or including it?
            # User said "art with svg and save them". Usually SVG export includes everything.
            
            generator = QSvgGenerator()
            generator.setFileName(file_path)
            # Use items bounding rect or scene rect
            rect = self.scene.itemsBoundingRect()
            if rect.isEmpty():
                rect = QRectF(0, 0, 800, 600)
            
            generator.setSize(rect.size().toSize())
            generator.setViewBox(rect)
            generator.setTitle("Neural Art Export")
            generator.setDescription("Generated by Neural Art V1.0")
            
            painter = QPainter(generator)
            self.scene.render(painter, rect, rect)
            painter.end()
            self.statusBar().showMessage(f"ART SAVED TO: {file_path}")

    def restart_app(self):
        os.execl(sys.executable, sys.executable, *sys.argv)

    def show_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec()

    def apply_theme(self):
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            QToolBar {{ background-color: {CP_PANEL}; border-bottom: 1px solid {CP_DIM}; spacing: 5px; padding: 3px; }}
            
            QPushButton {{
                background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 6px 12px; font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW};
            }}
            QPushButton:pressed {{
                background-color: {CP_YELLOW}; color: black;
            }}
            
            QSlider::handle:horizontal {{
                background: {CP_CYAN}; border: 1px solid {CP_DIM}; width: 18px; margin: -2px 0;
            }}
            QStatusBar {{ background-color: {CP_PANEL}; color: {CP_CYAN}; border-top: 1px solid {CP_DIM}; }}
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SVGArtApp()
    window.show()
    sys.exit(app.exec())
