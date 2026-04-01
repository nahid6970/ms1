import sys
import os
import math
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QToolBar, QFileDialog, QColorDialog, QSlider, 
                             QLabel, QGraphicsView, QGraphicsScene, QGraphicsPathItem,
                             QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsLineItem,
                             QGraphicsPixmapItem, QFrame, QGroupBox, QFormLayout, QDialog, 
                             QSizePolicy, QComboBox, QGraphicsBlurEffect)
from PyQt6.QtCore import Qt, QPointF, QRectF, QLineF, QSize
from PyQt6.QtGui import (QPainter, QPen, QColor, QPainterPath, QPixmap, QCursor, QAction, QIcon, QTransform, QBrush)
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

class SymItem:
    """ Mixin to track symmetry clones for any QGraphicsItem """
    def __init__(self):
        self.symmetry_clones = []
        self.is_art_item = True # To distinguish from UI markers

class SymPath(QGraphicsPathItem, SymItem):
    def __init__(self, *args, **kwargs):
        QGraphicsPathItem.__init__(self, *args, **kwargs)
        SymItem.__init__(self)
        self.path_points = [] # For stroke reconstruction

class SymRect(QGraphicsRectItem, SymItem):
    def __init__(self, *args, **kwargs):
        QGraphicsRectItem.__init__(self, *args, **kwargs)
        SymItem.__init__(self)

class SymEllipse(QGraphicsEllipseItem, SymItem):
    def __init__(self, *args, **kwargs):
        QGraphicsEllipseItem.__init__(self, *args, **kwargs)
        SymItem.__init__(self)

class SymLine(QGraphicsLineItem, SymItem):
    def __init__(self, *args, **kwargs):
        QGraphicsLineItem.__init__(self, *args, **kwargs)
        SymItem.__init__(self)

class ArtScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackgroundBrush(QColor(CP_BG))
        self.setSceneRect(-5000, -5000, 10000, 10000)
        
        # Center Marker
        self.center_marker = QGraphicsLineItem(-15, 0, 15, 0)
        self.center_marker.setPen(QPen(QColor(CP_YELLOW), 1))
        self.center_marker_v = QGraphicsLineItem(0, -15, 0, 15)
        self.center_marker_v.setPen(QPen(QColor(CP_YELLOW), 1))
        self.addItem(self.center_marker)
        self.addItem(self.center_marker_v)
        self.center_marker.is_art_item = False
        self.center_marker_v.is_art_item = False

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
        
        self.tool = "brush" 
        self.brush_type = "marker" 
        self.pen_color = QColor(CP_CYAN)
        self.pen_width = 3
        self.multi_line_count = 3
        
        self.image_item = None
        self.symmetry_mode = "none"
        self.mirror_count = 4
        self.undo_stack = []

        # Tool states
        self.poly_points = []
        self.curve_state = 0 # 0: none, 1: start set, 2: end set
        self.curve_points = []

    def wheelEvent(self, event):
        zoom = 1.25 if event.angleDelta().y() > 0 else 0.8
        self.scale(zoom, zoom)

    def mousePressEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        
        if event.button() == Qt.MouseButton.LeftButton:
            if self.tool == "brush":
                self.drawing = True
                self.start_point = scene_pos
                self.create_brush_item(scene_pos)
            
            elif self.tool == "poly":
                if not self.poly_points:
                    self.poly_points = [scene_pos]
                    path = QPainterPath()
                    path.moveTo(0, 0)
                    self.current_item = SymPath(path)
                    self.current_item.setPos(scene_pos)
                    self.current_item.setPen(QPen(self.pen_color, self.pen_width))
                    self.scene().addItem(self.current_item)
                    self.create_symmetry_clones(self.current_item)
                else:
                    # Check for closure
                    dist = (scene_pos - self.poly_points[0]).manhattanLength()
                    if dist < 15:
                        self.finish_poly()
                    else:
                        self.poly_points.append(scene_pos)
                        self.update_poly()

            elif self.tool == "curve":
                self.handle_curve_click(scene_pos)

            elif self.tool in ["rect", "ellipse", "line", "triangle"]:
                self.drawing = True
                self.start_point = scene_pos
                pen = QPen(self.pen_color, self.pen_width)
                if self.tool == "rect": self.current_item = SymRect(0, 0, 0, 0)
                elif self.tool == "ellipse": self.current_item = SymEllipse(0, 0, 0, 0)
                elif self.tool == "line": self.current_item = SymLine(0, 0, 0, 0)
                elif self.tool == "triangle": self.current_item = SymPath(QPainterPath())
                
                self.current_item.setPos(scene_pos)
                self.current_item.setPen(pen)
                self.scene().addItem(self.current_item)
                self.create_symmetry_clones(self.current_item)
            
            elif self.tool == "fill": self.apply_fill(scene_pos)
            elif self.tool == "picker": self.pick_color(scene_pos)
            elif self.tool == "eraser": self.drawing = True; self.erase_at(scene_pos)
            elif self.tool == "move_image":
                if self.image_item: self.drawing = True; self.start_point = scene_pos
            elif self.tool == "move_svg": self.drawing = True; self.start_point = scene_pos
        
        elif event.button() == Qt.MouseButton.RightButton:
            if self.tool == "poly": self.finish_poly()
            elif self.tool == "curve": self.reset_curve()

        elif event.button() == Qt.MouseButton.MiddleButton:
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        
        if self.drawing and self.current_item:
            local_pos = scene_pos - self.current_item.pos()
            if self.tool == "brush" and isinstance(self.current_item, SymPath):
                self.current_item.path_points.append(local_pos)
                if self.brush_type == "multiline":
                    new_path = QPainterPath()
                    spacing = self.pen_width * 2.5
                    for i in range(self.multi_line_count):
                        offset = (i - (self.multi_line_count - 1) / 2) * spacing
                        off_pt = QPointF(offset, offset)
                        
                        new_path.moveTo(self.current_item.path_points[0] + off_pt)
                        for pt in self.current_item.path_points[1:]:
                            new_path.lineTo(pt + off_pt)
                    self.current_item.setPath(new_path)
                else:
                    path = self.current_item.path()
                    path.lineTo(local_pos)
                    self.current_item.setPath(path)
                self.update_clones(self.current_item)
            
            elif self.tool in ["rect", "ellipse"]:
                rect = QRectF(QPointF(0,0), local_pos).normalized()
                self.current_item.setRect(rect); self.update_clones(self.current_item)
            elif self.tool == "line":
                self.current_item.setLine(QLineF(QPointF(0,0), local_pos)); self.update_clones(self.current_item)
            elif self.tool == "triangle":
                path = QPainterPath()
                top_x = local_pos.x() / 2
                path.moveTo(top_x, 0); path.lineTo(0, local_pos.y()); path.lineTo(local_pos.x(), local_pos.y()); path.closeSubpath()
                self.current_item.setPath(path); self.update_clones(self.current_item)
            elif self.tool == "eraser": self.erase_at(scene_pos)
            
        # Tool-specific previews
        if self.tool == "poly" and self.poly_points:
            self.update_poly(scene_pos)
        elif self.tool == "curve" and self.curve_state > 0:
            self.update_curve_preview(scene_pos)

        # Image/SVG Movement
        if self.drawing:
            if self.tool == "move_image" and self.image_item:
                delta = scene_pos - self.start_point; self.image_item.setPos(self.image_item.pos() + delta); self.start_point = scene_pos
            elif self.tool == "move_svg":
                delta = scene_pos - self.start_point
                for item in self.scene().items():
                    if getattr(item, 'is_art_item', False):
                        item.setPos(item.pos() + delta)
                self.start_point = scene_pos

        super().mouseMoveEvent(event)

    def create_brush_item(self, pos):
        path = QPainterPath()
        path.moveTo(0, 0)
        self.current_item = SymPath(path)
        self.current_item.setPos(pos)
        
        alpha = 100 if self.brush_type == "highlighter" else 255
        color = QColor(self.pen_color.red(), self.pen_color.green(), self.pen_color.blue(), alpha)
        
        pen = QPen(color, self.pen_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        self.current_item.setPen(pen)
        
        if self.brush_type == "airbrush":
            blur = QGraphicsBlurEffect()
            blur.setBlurRadius(self.pen_width * 1.5); self.current_item.setGraphicsEffect(blur)
            
        self.scene().addItem(self.current_item)
        self.create_symmetry_clones(self.current_item)

    def create_symmetry_clones(self, item):
        if self.symmetry_mode == "none": return
        for i in range(1, self.mirror_count if self.symmetry_mode == "radial" else 4):
            clone = self.clone_item(item)
            if not clone: continue
            if self.symmetry_mode == "radial":
                angle = i * (360 / self.mirror_count)
                tr = QTransform().rotate(angle)
                clone.setPos(tr.map(item.pos()))
                clone.setRotation(angle)
            elif self.symmetry_mode == "reflect":
                if i == 1: clone.setPos(-item.x(), item.y()); clone.setTransform(QTransform().scale(-1, 1))
                elif i == 2: clone.setPos(item.x(), -item.y()); clone.setTransform(QTransform().scale(1, -1))
                elif i == 3: clone.setPos(-item.x(), -item.y()); clone.setTransform(QTransform().scale(-1, -1))
            self.scene().addItem(clone); item.symmetry_clones.append(clone)

    def clone_item(self, item):
        if isinstance(item, QGraphicsPathItem): clone = SymPath(item.path())
        elif isinstance(item, QGraphicsRectItem): clone = SymRect(item.rect())
        elif isinstance(item, QGraphicsEllipseItem): clone = SymEllipse(item.rect())
        elif isinstance(item, QGraphicsLineItem): clone = SymLine(item.line())
        else: return None
        clone.setPen(item.pen()); clone.setBrush(item.brush()); clone.is_art_item = True
        if item.graphicsEffect():
            blur = QGraphicsBlurEffect(); blur.setBlurRadius(item.graphicsEffect().blurRadius()); clone.setGraphicsEffect(blur)
        return clone

    def update_clones(self, item):
        for clone in item.symmetry_clones:
            if isinstance(item, QGraphicsPathItem): clone.setPath(item.path())
            elif isinstance(item, QGraphicsRectItem): clone.setRect(item.rect())
            elif isinstance(item, QGraphicsEllipseItem): clone.setRect(item.rect())
            elif isinstance(item, QGraphicsLineItem): clone.setLine(item.line())

    def update_poly(self, preview_pos=None):
        if not self.current_item: return
        path = QPainterPath()
        path.moveTo(0, 0)
        for p in self.poly_points[1:]:
            path.lineTo(p - self.current_item.pos())
        if preview_pos:
            path.lineTo(preview_pos - self.current_item.pos())
        self.current_item.setPath(path)
        self.update_clones(self.current_item)

    def finish_poly(self):
        if self.current_item:
            path = self.current_item.path(); path.closeSubpath()
            self.current_item.setPath(path); self.update_clones(self.current_item)
            self.undo_stack.append(("add", self.current_item))
            self.current_item = None; self.poly_points = []

    def handle_curve_click(self, pos):
        if self.curve_state == 0:
            self.curve_points = [pos]
            self.curve_state = 1
            path = QPainterPath(); path.moveTo(0, 0)
            self.current_item = SymPath(path); self.current_item.setPos(pos)
            self.current_item.setPen(QPen(self.pen_color, self.pen_width))
            self.scene().addItem(self.current_item); self.create_symmetry_clones(self.current_item)
        elif self.curve_state == 1:
            self.curve_points.append(pos)
            self.curve_state = 2
        elif self.curve_state == 2:
            self.curve_points.append(pos)
            self.finish_curve()

    def update_curve_preview(self, pos):
        if not self.current_item: return
        path = QPainterPath(); path.moveTo(0, 0)
        if self.curve_state == 1:
            path.lineTo(pos - self.current_item.pos())
        elif self.curve_state == 2:
            path.quadTo(pos - self.current_item.pos(), self.curve_points[1] - self.current_item.pos())
        self.current_item.setPath(path); self.update_clones(self.current_item)

    def finish_curve(self):
        self.undo_stack.append(("add", self.current_item))
        self.current_item = None; self.curve_points = []; self.curve_state = 0

    def reset_curve(self):
        if self.current_item:
            self.scene().removeItem(self.current_item)
            for c in self.current_item.symmetry_clones: self.scene().removeItem(c)
        self.current_item = None; self.curve_points = []; self.curve_state = 0

    def erase_at(self, pos):
        items = self.scene().items(pos)
        for item in items:
            if getattr(item, 'is_art_item', False):
                for c in getattr(item, 'symmetry_clones', []): self.scene().removeItem(c)
                self.scene().removeItem(item)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.tool not in ["poly", "curve"] and self.drawing:
                self.undo_stack.append(("add", self.current_item))
                self.drawing = False; self.current_item = None
        elif event.button() == Qt.MouseButton.MiddleButton: self.setDragMode(QGraphicsView.DragMode.NoDrag)
        super().mouseReleaseEvent(event)

    def apply_fill(self, pos):
        item = self.scene().itemAt(pos, QTransform())
        if item and getattr(item, 'is_art_item', False):
            if hasattr(item, 'setBrush'):
                item.setBrush(QBrush(self.pen_color))
                for c in getattr(item, 'symmetry_clones', []): c.setBrush(QBrush(self.pen_color))

    def pick_color(self, pos):
        item = self.scene().itemAt(pos, QTransform())
        if item and hasattr(item, 'pen'):
            self.pen_color = item.pen().color()
            if hasattr(self.parent(), 'update_color_ui'): self.parent().update_color_ui(self.pen_color)

    def undo(self):
        if not self.undo_stack: return
        action = self.undo_stack.pop()
        if action[0] == "add" and action[1]:
            item = action[1]; self.scene().removeItem(item)
            for c in getattr(item, 'symmetry_clones', []): self.scene().removeItem(c)

class SVGArtApp(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle("NEURAL ART V1.3 - CYBER-PAINT PRO"); self.resize(1400, 900)
        self.setup_ui(); self.apply_theme()

    def setup_ui(self):
        self.central_widget = QWidget(); self.setCentralWidget(self.central_widget); self.main_layout = QVBoxLayout(self.central_widget)
        
        # Upper Toolbar
        self.toolbar = QToolBar("Tools"); self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)
        self.add_tool_action("BRUSH", "brush", CP_CYAN)
        self.brush_combo = QComboBox(); self.brush_combo.addItems(["Marker", "Airbrush", "Multiline", "Highlighter"])
        self.brush_combo.currentTextChanged.connect(self.set_brush_type); self.toolbar.addWidget(self.brush_combo)
        
        self.toolbar.addWidget(QLabel(" LINES: "))
        self.multi_slider = QSlider(Qt.Orientation.Horizontal); self.multi_slider.setRange(1, 10); self.multi_slider.setValue(3)
        self.multi_slider.setFixedWidth(60); self.multi_slider.valueChanged.connect(self.set_multi_count); self.toolbar.addWidget(self.multi_slider)

        self.add_tool_action("POLY", "poly", CP_GREEN)
        self.add_tool_action("CURVE", "curve", CP_GREEN)
        self.add_tool_action("ERASE", "eraser", CP_RED)
        self.add_tool_action("FILL", "fill", CP_YELLOW); self.add_tool_action("PICK", "picker", CP_CYAN)
        
        self.toolbar.addSeparator()
        self.add_tool_action("RECT", "rect", CP_ORANGE); self.add_tool_action("CIRC", "ellipse", CP_ORANGE); self.add_tool_action("TRI", "triangle", CP_ORANGE)
        self.toolbar.addSeparator(); self.add_tool_action("MOVE IMG", "move_image", CP_SUBTEXT); self.add_tool_action("MOVE SVG", "move_svg", CP_SUBTEXT)
        
        self.toolbar.addSeparator(); self.btn_color = QPushButton("COLOR"); self.btn_color.clicked.connect(self.choose_color); self.toolbar.addWidget(self.btn_color)
        self.toolbar.addWidget(QLabel(" THICK: ")); self.thickness_slider = QSlider(Qt.Orientation.Horizontal); self.thickness_slider.setRange(1, 100); self.thickness_slider.setValue(3); self.thickness_slider.valueChanged.connect(self.change_thickness); self.toolbar.addWidget(self.thickness_slider)
        
        # Left Toolbar
        self.sym_toolbar = QToolBar("Symmetry"); self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.sym_toolbar)
        self.sym_toolbar.addWidget(QLabel(" SYMMETRY "))
        self.sym_combo = QComboBox(); self.sym_combo.addItems(["None", "Radial", "Reflect"]); self.sym_combo.currentTextChanged.connect(self.set_symmetry_mode); self.sym_toolbar.addWidget(self.sym_combo)
        self.sym_toolbar.addWidget(QLabel(" MIRROR: ")); self.mirror_spin = QSlider(Qt.Orientation.Horizontal); self.mirror_spin.setRange(2, 20); self.mirror_spin.setValue(4); self.mirror_spin.valueChanged.connect(self.set_mirror_count); self.sym_toolbar.addWidget(self.mirror_spin)
        
        spacer = QWidget(); spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred); self.toolbar.addWidget(spacer)
        self.add_system_action("UNDO", self.undo, CP_YELLOW); self.add_system_action("IMG", self.load_image, CP_CYAN); self.add_system_action("SAVE", self.save_svg, CP_GREEN); self.add_system_action("RST", self.restart_app, CP_RED)

        self.scene = ArtScene(); self.view = ArtView(self.scene, self); self.main_layout.addWidget(self.view)
        self.statusBar().showMessage("SYSTEM READY | POLY: R-Click to close | CURVE: 3-Click Tool")

    def add_tool_action(self, text, tool_name, color):
        btn = QPushButton(text); btn.setStyleSheet(f"color: {color}; font-weight: bold;"); btn.clicked.connect(lambda: self.set_tool(tool_name)); self.toolbar.addWidget(btn)

    def add_system_action(self, text, func, color):
        btn = QPushButton(text); btn.setStyleSheet(f"color: {color}; font-weight: bold; border: 1px solid {color};"); btn.clicked.connect(func); self.toolbar.addWidget(btn)

    def set_tool(self, tool): self.view.tool = tool; self.view.current_item = None; self.statusBar().showMessage(f"ACTIVE TOOL: {tool.upper()}")
    def set_brush_type(self, btype): self.view.brush_type = btype.lower(); self.set_tool("brush")
    def set_multi_count(self, val): self.view.multi_line_count = val
    def set_symmetry_mode(self, mode): self.view.symmetry_mode = mode.lower()
    def set_mirror_count(self, val): self.view.mirror_count = val
    def update_color_ui(self, color): self.btn_color.setStyleSheet(f"background-color: {color.name()}; color: {'black' if color.lightness() > 128 else 'white'};")
    def choose_color(self):
        color = QColorDialog.getColor(self.view.pen_color, self, "CHOOSE COLOR")
        if color.isValid(): self.view.pen_color = color; self.update_color_ui(color)
    def change_thickness(self, value): self.view.pen_width = value
    def undo(self): self.view.undo()
    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "LOAD IMAGE", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            pixmap = QPixmap(file_path); self.view.image_item = QGraphicsPixmapItem(pixmap); self.view.image_item.setZValue(-1); self.view.image_item.is_art_item = False; self.scene.addItem(self.view.image_item)
    def save_svg(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "SAVE SVG", "art.svg", "SVG files (*.svg)")
        if file_path:
            generator = QSvgGenerator(); generator.setFileName(file_path); rect = self.scene.itemsBoundingRect()
            if rect.isEmpty(): rect = QRectF(0, 0, 800, 600)
            generator.setSize(rect.size().toSize()); generator.setViewBox(rect); painter = QPainter(generator); self.scene.render(painter, rect, rect); painter.end()
    def restart_app(self): os.execl(sys.executable, sys.executable, *sys.argv)
    def apply_theme(self):
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            QToolBar {{ background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; spacing: 5px; padding: 3px; }}
            QPushButton {{ background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 4px 8px; font-weight: bold; font-size: 9pt; }}
            QPushButton:hover {{ background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }}
            QComboBox {{ background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 2px; }}
            QSlider::handle:horizontal {{ background: {CP_CYAN}; border: 1px solid {CP_DIM}; width: 14px; margin: -2px 0; }}
            QStatusBar {{ background-color: {CP_PANEL}; color: {CP_CYAN}; border-top: 1px solid {CP_DIM}; }}
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv); window = SVGArtApp(); window.show(); sys.exit(app.exec())
