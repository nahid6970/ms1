import sys
import os
import math
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QToolBar, QFileDialog, QColorDialog, QSlider, 
                             QLabel, QGraphicsView, QGraphicsScene, QGraphicsPathItem,
                             QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsLineItem,
                             QGraphicsPixmapItem, QFrame, QGroupBox, QFormLayout, QDialog, 
                             QSizePolicy, QComboBox, QGraphicsBlurEffect)
from PyQt6.QtCore import Qt, QPointF, QRectF, QLineF, QSize, QByteArray
from PyQt6.QtGui import (QPainter, QPen, QColor, QPainterPath, QPixmap, QCursor, QAction, QIcon, QTransform, QBrush, QKeySequence)
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

SETTINGS_FILE = "settings.json"

class SymItem:
    def __init__(self):
        self.symmetry_clones = []
        self.is_art_item = True
        self.clone_type = "master" # master, radial, reflect_h, reflect_v, reflect_b

class SymPath(QGraphicsPathItem, SymItem):
    def __init__(self, *args, **kwargs):
        QGraphicsPathItem.__init__(self, *args, **kwargs)
        SymItem.__init__(self)
        self.path_points = []

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
        self.setStyleSheet(f"background-color: {CP_BG}; border: 1px solid {CP_DIM};")
        self.drawing = False; self.current_item = None; self.start_point = QPointF() 
        self.tool = "brush"; self.brush_type = "marker"; self.pen_color = QColor(CP_CYAN); self.pen_width = 3; self.multi_line_count = 3
        self.image_item = None; self.image_path = ""; self.sym_center = QPointF(0, 0)
        self.symmetry_mode = "None"; self.mirror_count = 4; self.undo_stack = []; self.redo_stack = []
        self.poly_points = []; self.curve_state = 0; self.curve_points = []

    def save_to_undo(self, item, action="add"):
        self.undo_stack.append((action, item)); self.redo_stack.clear()

    def wheelEvent(self, event):
        zoom = 1.25 if event.angleDelta().y() > 0 else 0.8; self.scale(zoom, zoom)

    def mousePressEvent(self, event):
        scene_pos = self.mapToScene(event.pos()); self.start_point = scene_pos
        if event.button() == Qt.MouseButton.LeftButton:
            if self.tool == "brush":
                self.drawing = True; self.create_brush_item(scene_pos)
            elif self.tool == "poly":
                if not self.poly_points:
                    self.poly_points = [scene_pos]; self.current_item = SymPath(QPainterPath()); self.current_item.setPos(scene_pos)
                    self.current_item.setPen(QPen(self.pen_color, self.pen_width)); self.scene().addItem(self.current_item); self.create_symmetry_clones(self.current_item)
                else:
                    if (scene_pos - self.poly_points[0]).manhattanLength() < 15: self.finish_poly()
                    else: self.poly_points.append(scene_pos); self.update_poly()
            elif self.tool == "curve": self.handle_curve_click(scene_pos)
            elif self.tool in ["rect", "ellipse", "line", "triangle"]:
                self.drawing = True; p = QPen(self.pen_color, self.pen_width)
                if self.tool == "rect": self.current_item = SymRect(0, 0, 0, 0)
                elif self.tool == "ellipse": self.current_item = SymEllipse(0, 0, 0, 0)
                elif self.tool == "line": self.current_item = SymLine(0, 0, 0, 0)
                elif self.tool == "triangle": self.current_item = SymPath(QPainterPath())
                self.current_item.setPos(scene_pos); self.current_item.setPen(p); self.scene().addItem(self.current_item); self.create_symmetry_clones(self.current_item)
            elif self.tool == "fill": self.apply_fill(scene_pos)
            elif self.tool == "picker": self.pick_color(scene_pos)
            elif self.tool == "eraser": self.drawing = True; self.erase_at(scene_pos)
            elif self.tool in ["move_image", "move_svg", "move_sym"]: self.drawing = True
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag); super().mousePressEvent(event)
        elif event.button() == Qt.MouseButton.RightButton:
            if self.tool == "poly": self.finish_poly()
            elif self.tool == "curve": self.reset_curve()

    def mouseMoveEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        if self.drawing:
            if self.current_item:
                local_pos = scene_pos - self.current_item.pos()
                if self.tool == "brush" and isinstance(self.current_item, SymPath):
                    self.current_item.path_points.append(local_pos)
                    if self.brush_type == "multiline":
                        new_path = QPainterPath(); spacing = self.pen_width * 2.5
                        for i in range(self.multi_line_count):
                            off = (i - (self.multi_line_count - 1) / 2) * spacing; off_pt = QPointF(off, off)
                            new_path.moveTo(self.current_item.path_points[0] + off_pt)
                            for pt in self.current_item.path_points[1:]: new_path.lineTo(pt + off_pt)
                        self.current_item.setPath(new_path)
                    else:
                        path = self.current_item.path(); path.lineTo(local_pos); self.current_item.setPath(path)
                    self.update_clones(self.current_item)
                elif self.tool in ["rect", "ellipse"]:
                    self.current_item.setRect(QRectF(QPointF(0,0), local_pos).normalized()); self.update_clones(self.current_item)
                elif self.tool == "line":
                    self.current_item.setLine(QLineF(QPointF(0,0), local_pos)); self.update_clones(self.current_item)
                elif self.tool == "triangle":
                    path = QPainterPath(); top_x = local_pos.x() / 2
                    path.moveTo(top_x, 0); path.lineTo(0, local_pos.y()); path.lineTo(local_pos.x(), local_pos.y()); path.closeSubpath()
                    self.current_item.setPath(path); self.update_clones(self.current_item)
            if self.tool == "eraser": self.erase_at(scene_pos)
            elif self.tool == "move_image" and self.image_item:
                delta = scene_pos - self.start_point; self.image_item.setPos(self.image_item.pos() + delta); self.start_point = scene_pos
            elif self.tool == "move_svg":
                delta = scene_pos - self.start_point
                for item in self.scene().items():
                    if getattr(item, 'is_art_item', False): item.setPos(item.pos() + delta)
                self.start_point = scene_pos
            elif self.tool == "move_sym":
                delta = scene_pos - self.start_point; self.sym_center += delta; self.start_point = scene_pos
                self.scene().center_marker.setPos(self.sym_center); self.scene().center_marker_v.setPos(self.sym_center)
        if self.tool == "poly" and self.poly_points: self.update_poly(scene_pos)
        elif self.tool == "curve" and self.curve_state > 0: self.update_curve_preview(scene_pos)
        super().mouseMoveEvent(event)

    def create_brush_item(self, pos):
        path = QPainterPath(); path.moveTo(0, 0); self.current_item = SymPath(path); self.current_item.setPos(pos); self.current_item.path_points = [QPointF(0,0)]
        alpha = 100 if self.brush_type == "highlighter" else 255
        p = QPen(QColor(*self.pen_color.getRgb()[:3], alpha), self.pen_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        self.current_item.setPen(p)
        if self.brush_type == "airbrush":
            blur = QGraphicsBlurEffect(); blur.setBlurRadius(self.pen_width * 1.5); self.current_item.setGraphicsEffect(blur)
        self.scene().addItem(self.current_item); self.create_symmetry_clones(self.current_item)

    def create_symmetry_clones(self, item):
        if self.symmetry_mode == "None": return
        cx, cy = self.sym_center.x(), self.sym_center.y()
        if self.symmetry_mode == "Radial":
            for i in range(1, self.mirror_count):
                clone = self.clone_item(item)
                if not clone: continue
                clone.clone_type = "radial"
                angle = i * (360 / self.mirror_count); tr = QTransform().translate(cx, cy).rotate(angle).translate(-cx, -cy)
                clone.setPos(tr.map(item.pos())); clone.setRotation(angle); self.scene().addItem(clone); item.symmetry_clones.append(clone)
        elif "Reflect" in self.symmetry_mode:
            modes = []
            if "(H)" in self.symmetry_mode: modes = ["h"]
            elif "(V)" in self.symmetry_mode: modes = ["v"]
            elif "(B)" in self.symmetry_mode: modes = ["h", "v", "b"]
            for m in modes:
                clone = self.clone_item(item)
                if not clone: continue
                if m == "h":
                    clone.clone_type = "reflect_h"; clone.setPos(2*cx - item.x(), item.y()); clone.setTransform(QTransform.fromScale(-1, 1))
                elif m == "v":
                    clone.clone_type = "reflect_v"; clone.setPos(item.x(), 2*cy - item.y()); clone.setTransform(QTransform.fromScale(1, -1))
                elif m == "b":
                    clone.clone_type = "reflect_b"; clone.setPos(2*cx - item.x(), 2*cy - item.y()); clone.setTransform(QTransform.fromScale(-1, -1))
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
        cx, cy = self.sym_center.x(), self.sym_center.y()
        for i, clone in enumerate(item.symmetry_clones):
            if isinstance(item, QGraphicsPathItem): clone.setPath(item.path())
            elif isinstance(item, QGraphicsRectItem): clone.setRect(item.rect())
            elif isinstance(item, QGraphicsEllipseItem): clone.setRect(item.rect())
            elif isinstance(item, QGraphicsLineItem): clone.setLine(item.line())
            if clone.clone_type == "radial":
                angle = (i+1) * (360 / self.mirror_count); tr = QTransform().translate(cx, cy).rotate(angle).translate(-cx, -cy)
                clone.setPos(tr.map(item.pos()))
            elif clone.clone_type == "reflect_h": clone.setPos(2*cx - item.x(), item.y())
            elif clone.clone_type == "reflect_v": clone.setPos(item.x(), 2*cy - item.y())
            elif clone.clone_type == "reflect_b": clone.setPos(2*cx - item.x(), 2*cy - item.y())

    def update_poly(self, pos=None):
        if not self.current_item: return
        path = QPainterPath(); path.moveTo(0, 0)
        for p in self.poly_points[1:]: path.lineTo(p - self.current_item.pos())
        if pos: path.lineTo(pos - self.current_item.pos())
        self.current_item.setPath(path); self.update_clones(self.current_item)

    def finish_poly(self):
        if self.current_item:
            path = self.current_item.path(); path.closeSubpath(); self.current_item.setPath(path); self.update_clones(self.current_item)
            self.save_to_undo(self.current_item); self.current_item = None; self.poly_points = []

    def handle_curve_click(self, pos):
        if self.curve_state == 0:
            self.curve_points = [pos]; self.curve_state = 1; self.current_item = SymPath(QPainterPath()); self.current_item.setPos(pos)
            self.current_item.setPen(QPen(self.pen_color, self.pen_width)); self.scene().addItem(self.current_item); self.create_symmetry_clones(self.current_item)
        elif self.curve_state == 1: self.curve_points.append(pos); self.curve_state = 2
        elif self.curve_state == 2: self.curve_points.append(pos); self.finish_curve()

    def update_curve_preview(self, pos):
        if not self.current_item: return
        path = QPainterPath(); path.moveTo(0, 0)
        if self.curve_state == 1: path.lineTo(pos - self.current_item.pos())
        elif self.curve_state == 2: path.quadTo(pos - self.current_item.pos(), self.curve_points[1] - self.current_item.pos())
        self.current_item.setPath(path); self.update_clones(self.current_item)

    def finish_curve(self): self.save_to_undo(self.current_item); self.current_item = None; self.curve_points = []; self.curve_state = 0
    def reset_curve(self):
        if self.current_item:
            self.scene().removeItem(self.current_item); [self.scene().removeItem(c) for c in self.current_item.symmetry_clones]
        self.current_item = None; self.curve_points = []; self.curve_state = 0

    def erase_at(self, pos):
        items = self.scene().items(pos)
        for item in items:
            if getattr(item, 'is_art_item', False):
                [self.scene().removeItem(c) for c in getattr(item, 'symmetry_clones', [])]; self.scene().removeItem(item); self.save_to_undo(item, "remove")

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.tool not in ["poly", "curve"] and self.drawing:
                self.save_to_undo(self.current_item); self.drawing = False; self.current_item = None
        elif event.button() == Qt.MouseButton.MiddleButton: self.setDragMode(QGraphicsView.DragMode.NoDrag)
        super().mouseReleaseEvent(event)

    def apply_fill(self, pos):
        item = self.scene().itemAt(pos, QTransform())
        if item and getattr(item, 'is_art_item', False):
            old = item.brush(); item.setBrush(QBrush(self.pen_color))
            [c.setBrush(QBrush(self.pen_color)) for c in getattr(item, 'symmetry_clones', [])]; self.undo_stack.append(("fill", item, old))

    def pick_color(self, pos):
        item = self.scene().itemAt(pos, QTransform())
        if item and hasattr(item, 'pen'):
            self.pen_color = item.pen().color(); self.parent().update_color_ui(self.pen_color)

    def undo(self):
        if not self.undo_stack: return
        a, i = self.undo_stack.pop()
        if a == "add":
            self.scene().removeItem(i); [self.scene().removeItem(c) for c in getattr(i, 'symmetry_clones', [])]; self.redo_stack.append((a, i))
        elif a == "remove":
            self.scene().addItem(i); [self.scene().addItem(c) for c in getattr(i, 'symmetry_clones', [])]; self.redo_stack.append((a, i))
        elif a == "fill":
            old = i[2]; i.setBrush(old); [c.setBrush(old) for c in getattr(i, 'symmetry_clones', [])]

    def redo(self):
        if not self.redo_stack: return
        a, i = self.redo_stack.pop(); self.scene().addItem(i) if a == "add" else self.scene().removeItem(i)
        if a == "add": [self.scene().addItem(c) for c in getattr(i, 'symmetry_clones', [])]
        else: [self.scene().removeItem(c) for c in getattr(i, 'symmetry_clones', [])]
        self.undo_stack.append((a, i))

class SVGArtApp(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle("NEURAL ART V1.6.2 - SYNCED"); self.resize(1400, 900)
        self.setup_ui(); self.apply_theme(); self.load_settings()

    def setup_ui(self):
        self.central_widget = QWidget(); self.setCentralWidget(self.central_widget); self.main_layout = QVBoxLayout(self.central_widget)
        self.tb_main = QToolBar("Main"); self.tb_main.setObjectName("MainToolbar"); self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.tb_main)
        self.add_tool_action(self.tb_main, "BRUSH", "brush", CP_CYAN); self.brush_combo = QComboBox(); self.brush_combo.addItems(["Marker", "Airbrush", "Multiline", "Highlighter"]); self.brush_combo.currentTextChanged.connect(self.set_brush_type); self.tb_main.addWidget(self.brush_combo)
        self.tb_main.addWidget(QLabel(" LINES: ")); self.multi_slider = QSlider(Qt.Orientation.Horizontal); self.multi_slider.setRange(1, 10); self.multi_slider.setValue(3); self.multi_slider.valueChanged.connect(self.set_multi_count); self.tb_main.addWidget(self.multi_slider)
        self.add_tool_action(self.tb_main, "POLY", "poly", CP_GREEN); self.add_tool_action(self.tb_main, "CURVE", "curve", CP_GREEN); self.add_tool_action(self.tb_main, "ERASE", "eraser", CP_RED); self.add_tool_action(self.tb_main, "FILL", "fill", CP_YELLOW); self.add_tool_action(self.tb_main, "PICK", "picker", CP_CYAN)
        self.tb_shapes = QToolBar("Shapes"); self.tb_shapes.setObjectName("ShapesToolbar"); self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.tb_shapes)
        self.add_tool_action(self.tb_shapes, "RECT", "rect", CP_ORANGE); self.add_tool_action(self.tb_shapes, "CIRC", "ellipse", CP_ORANGE); self.add_tool_action(self.tb_shapes, "TRI", "triangle", CP_ORANGE)
        self.tb_shapes.addSeparator(); self.add_tool_action(self.tb_shapes, "MOVE IMG", "move_image", CP_SUBTEXT); self.add_tool_action(self.tb_shapes, "MOVE SVG", "move_svg", CP_SUBTEXT); self.add_tool_action(self.tb_shapes, "MOVE SYM", "move_sym", CP_YELLOW)
        self.tb_props = QToolBar("Properties"); self.tb_props.setObjectName("PropsToolbar"); self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.tb_props)
        self.btn_color = QPushButton("COLOR"); self.btn_color.clicked.connect(self.choose_color); self.tb_props.addWidget(self.btn_color)
        self.tb_props.addWidget(QLabel(" THICK: ")); self.thickness_slider = QSlider(Qt.Orientation.Horizontal); self.thickness_slider.setRange(1, 100); self.thickness_slider.setValue(3); self.thickness_slider.valueChanged.connect(self.change_thickness); self.tb_props.addWidget(self.thickness_slider)
        self.tb_sym = QToolBar("Symmetry"); self.tb_sym.setObjectName("SymmetryToolbar"); self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.tb_sym)
        self.tb_sym.addWidget(QLabel(" SYMMETRY ")); self.sym_combo = QComboBox(); self.sym_combo.addItems(["None", "Radial", "Reflect (H)", "Reflect (V)", "Reflect (B)"]); self.sym_combo.currentTextChanged.connect(self.set_symmetry_mode); self.tb_sym.addWidget(self.sym_combo)
        self.tb_sym.addWidget(QLabel(" MIRROR: ")); self.mirror_spin = QSlider(Qt.Orientation.Horizontal); self.mirror_spin.setRange(2, 20); self.mirror_spin.setValue(4); self.mirror_spin.valueChanged.connect(self.set_mirror_count); self.tb_sym.addWidget(self.mirror_spin)
        self.tb_sys = QToolBar("System"); self.tb_sys.setObjectName("SystemToolbar"); self.addToolBar(Qt.ToolBarArea.RightToolBarArea, self.tb_sys)
        self.add_system_action(self.tb_sys, "CLEAN", self.clear_art, CP_RED); self.add_system_action(self.tb_sys, "UNDO", self.undo, CP_YELLOW); self.add_system_action(self.tb_sys, "REDO", self.redo, CP_GREEN)
        self.add_system_action(self.tb_sys, "IMG", self.load_image, CP_CYAN); self.add_system_action(self.tb_sys, "SAVE", self.save_svg, CP_GREEN); self.add_system_action(self.tb_sys, "RST", self.restart_app, CP_RED)
        self.scene = ArtScene(); self.view = ArtView(self.scene, self); self.main_layout.addWidget(self.view)
        u_act = QAction("Undo", self); u_act.setShortcut(QKeySequence("Ctrl+Z")); u_act.triggered.connect(self.undo); self.addAction(u_act)
        r_act = QAction("Redo", self); r_act.setShortcut(QKeySequence("Ctrl+Y")); r_act.triggered.connect(self.redo); self.addAction(r_act)

    def add_tool_action(self, tb, text, tool_name, color):
        btn = QPushButton(text); btn.setStyleSheet(f"color: {color}; font-weight: bold;"); btn.clicked.connect(lambda: self.set_tool(tool_name)); tb.addWidget(btn)
    def add_system_action(self, tb, text, func, color):
        btn = QPushButton(text); btn.setStyleSheet(f"color: {color}; font-weight: bold; border: 1px solid {color};"); btn.clicked.connect(func); tb.addWidget(btn)
    def set_tool(self, tool): self.view.tool = tool; self.view.current_item = None
    def set_brush_type(self, b): self.view.brush_type = b.lower(); self.set_tool("brush")
    def set_multi_count(self, v): self.view.multi_line_count = v
    def set_symmetry_mode(self, m): self.view.symmetry_mode = m; self.statusBar().showMessage(f"MODE: {m}")
    def set_mirror_count(self, v): self.view.mirror_count = v
    def update_color_ui(self, c): self.btn_color.setStyleSheet(f"background-color: {c.name()}; color: {'black' if c.lightness() > 128 else 'white'};")
    def choose_color(self):
        c = QColorDialog.getColor(self.view.pen_color, self, "COLOR")
        if c.isValid(): self.view.pen_color = c; self.update_color_ui(c)
    def change_thickness(self, v): self.view.pen_width = v
    def undo(self): self.view.undo()
    def redo(self): self.view.redo()
    def clear_art(self): [self.scene.removeItem(i) for i in self.scene.items() if getattr(i, 'is_art_item', False)]
    def load_image(self, path=None):
        if not path: path, _ = QFileDialog.getOpenFileName(self, "IMG", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if path and os.path.exists(path):
            pix = QPixmap(path)
            if not pix.isNull():
                if self.view.image_item: self.scene.removeItem(self.view.image_item)
                self.view.image_item = QGraphicsPixmapItem(pix); self.view.image_item.setZValue(-1); self.view.image_item.is_art_item = False; self.view.image_path = path; self.scene.addItem(self.view.image_item)
    def save_svg(self):
        f, _ = QFileDialog.getSaveFileName(self, "SAVE SVG", "art.svg", "SVG files (*.svg)")
        if f:
            hidden = []; r = QRectF()
            for i in self.scene.items():
                if not getattr(i, 'is_art_item', False): (i.hide(), hidden.append(i)) if i.isVisible() else None
                else: r = r.united(i.sceneBoundingRect())
            if r.isEmpty(): r = QRectF(0, 0, 800, 600)
            g = QSvgGenerator(); g.setFileName(f); g.setSize(r.size().toSize()); g.setViewBox(r); painter = QPainter(g); self.scene.render(painter, r, r); painter.end(); [i.show() for i in hidden]
    def restart_app(self): self.save_settings(); os.execl(sys.executable, sys.executable, *sys.argv)
    
    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    s = json.load(f)
                    if "geom" in s: self.restoreGeometry(QByteArray.fromHex(s["geom"].encode()))
                    if "state" in s: self.restoreState(QByteArray.fromHex(s["state"].encode()))
                    self.view.tool = s.get("tool", "brush"); self.view.brush_type = s.get("brush_type", "marker"); self.view.pen_color = QColor(s.get("color", CP_CYAN)); self.view.pen_width = s.get("width", 3); self.view.multi_line_count = s.get("multi_count", 3); sm = s.get("symmetry_mode", "None"); self.view.symmetry_mode = sm; self.sym_combo.setCurrentText(sm); self.view.mirror_count = s.get("mirror_count", 4); self.view.sym_center = QPointF(s.get("sym_x", 0), s.get("sym_y", 0)); self.scene.center_marker.setPos(self.view.sym_center); self.scene.center_marker_v.setPos(self.view.sym_center); self.brush_combo.setCurrentText(self.view.brush_type.capitalize()); self.thickness_slider.setValue(self.view.pen_width); self.multi_slider.setValue(self.view.multi_line_count); self.mirror_spin.setValue(self.view.mirror_count); self.update_color_ui(self.view.pen_color); ip = s.get("img_path", "")
                    if ip and os.path.exists(ip):
                        self.load_image(ip)
                        if self.view.image_item: self.view.image_item.setPos(s.get("img_x", 0), s.get("img_y", 0))
            except: pass

    def save_settings(self):
        s = {"geom": self.saveGeometry().toHex().data().decode(), "state": self.saveState().toHex().data().decode(), "tool": self.view.tool, "brush_type": self.view.brush_type, "color": self.view.pen_color.name(), "width": self.view.pen_width, "multi_count": self.view.multi_line_count, "symmetry_mode": self.view.symmetry_mode, "mirror_count": self.view.mirror_count, "sym_x": self.view.sym_center.x(), "sym_y": self.view.sym_center.y(), "img_path": self.view.image_path, "img_x": self.view.image_item.x() if self.view.image_item else 0, "img_y": self.view.image_item.y() if self.view.image_item else 0}
        with open(SETTINGS_FILE, 'w') as f: json.dump(s, f)

    def closeEvent(self, e): self.save_settings(); super().closeEvent(e)
    def apply_theme(self):
        self.setStyleSheet(f"QMainWindow {{ background-color: {CP_BG}; }} QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }} QToolBar {{ background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; spacing: 5px; padding: 3px; }} QPushButton {{ background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 4px 8px; font-weight: bold; font-size: 9pt; }} QPushButton:hover {{ background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }} QComboBox {{ background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 2px; }} QSlider::handle:horizontal {{ background: {CP_CYAN}; border: 1px solid {CP_DIM}; width: 14px; margin: -2px 0; }} QStatusBar {{ background-color: {CP_PANEL}; color: {CP_CYAN}; border-top: 1px solid {CP_DIM}; }}")

if __name__ == "__main__":
    app = QApplication(sys.argv); window = SVGArtApp(); window.show(); sys.exit(app.exec())
