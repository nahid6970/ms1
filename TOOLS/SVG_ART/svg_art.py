import sys
import os
import math
import json
import re
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QToolBar, QFileDialog, QColorDialog, QSlider, 
                             QLabel, QGraphicsView, QGraphicsScene, QGraphicsPathItem,
                             QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsLineItem,
                             QGraphicsPixmapItem, QFrame, QGroupBox, QFormLayout, QDialog, 
                             QSizePolicy, QComboBox, QGraphicsBlurEffect, QInputDialog,
                             QMessageBox, QMenu, QSpinBox, QPlainTextEdit, QLineEdit)
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

SETTINGS_FILE = os.path.join(r"C:\@delta\output\svg_art", "settings.json")
CUSTOM_SHAPES_FILE = os.path.join(r"C:\@delta\output\svg_art", "custom_shapes.json")

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
        self.show_grid = False
        self.grid_size = 20
        self.center_marker = QGraphicsLineItem(-15, 0, 15, 0)
        self.center_marker.setPen(QPen(QColor(CP_YELLOW), 1))
        self.center_marker_v = QGraphicsLineItem(0, -15, 0, 15)
        self.center_marker_v.setPen(QPen(QColor(CP_YELLOW), 1))
        self.addItem(self.center_marker)
        self.addItem(self.center_marker_v)
        self.center_marker.is_art_item = False
        self.center_marker_v.is_art_item = False

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        if not self.show_grid: return
        pen = QPen(QColor(CP_DIM), 0.5)
        painter.setPen(pen)
        left = int(rect.left()) - (int(rect.left()) % self.grid_size)
        top = int(rect.top()) - (int(rect.top()) % self.grid_size)
        lines = []
        for x in range(left, int(rect.right()) + 1, self.grid_size):
            lines.append(QLineF(x, rect.top(), x, rect.bottom()))
        for y in range(top, int(rect.bottom()) + 1, self.grid_size):
            lines.append(QLineF(rect.left(), y, rect.right(), y))
        painter.drawLines(lines)

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
        self.is_sharp = True; self.custom_shapes = {}
        self.snap_to_grid = False; self.grid_size = 20

    def get_pen(self, alpha=255):
        cap = Qt.PenCapStyle.SquareCap if self.is_sharp else Qt.PenCapStyle.RoundCap
        join = Qt.PenJoinStyle.MiterJoin if self.is_sharp else Qt.PenJoinStyle.RoundJoin
        return QPen(QColor(*self.pen_color.getRgb()[:3], alpha), self.pen_width, Qt.PenStyle.SolidLine, cap, join)

    def snap_point(self, point):
        if self.snap_to_grid:
            x = round(point.x() / self.grid_size) * self.grid_size
            y = round(point.y() / self.grid_size) * self.grid_size
            return QPointF(x, y)
        return point

    def save_to_undo(self, item, action="add"):
        self.undo_stack.append((action, item)); self.redo_stack.clear()

    def wheelEvent(self, event):
        zoom = 1.25 if event.angleDelta().y() > 0 else 0.8; self.scale(zoom, zoom)

    def mousePressEvent(self, event):
        scene_pos = self.snap_point(self.mapToScene(event.pos())); self.start_point = scene_pos
        if event.button() == Qt.MouseButton.LeftButton:
            if self.tool == "brush":
                self.drawing = True; self.create_brush_item(scene_pos)
            elif self.tool == "poly":
                if not self.poly_points:
                    self.poly_points = [scene_pos]; self.current_item = SymPath(QPainterPath()); self.current_item.setPos(scene_pos)
                    self.current_item.setPen(self.get_pen()); self.scene().addItem(self.current_item); self.create_symmetry_clones(self.current_item)
                else:
                    if (scene_pos - self.poly_points[0]).manhattanLength() < 15: self.finish_poly()
                    else: self.poly_points.append(scene_pos); self.update_poly()
            elif self.tool == "curve": self.handle_curve_click(scene_pos)
            elif self.tool in ["rect", "ellipse", "line", "triangle"] or self.tool.startswith("custom:"):
                self.drawing = True; p = self.get_pen()
                if self.tool == "rect": self.current_item = SymRect(0, 0, 0, 0)
                elif self.tool == "ellipse": self.current_item = SymEllipse(0, 0, 0, 0)
                elif self.tool == "line": self.current_item = SymLine(0, 0, 0, 0)
                elif self.tool == "triangle": self.current_item = SymPath(QPainterPath())
                elif self.tool.startswith("custom:"):
                    self.current_item = SymPath(QPainterPath())
                    self.current_item._custom_base = self.custom_shapes.get(self.tool[7:], [])
                self.current_item.setPos(scene_pos); self.current_item.setPen(p); self.scene().addItem(self.current_item); self.create_symmetry_clones(self.current_item)
            elif self.tool == "fill": self.apply_fill(scene_pos)
            elif self.tool == "picker": self.pick_color(scene_pos)
            elif self.tool == "eraser": self.drawing = True; self.erase_at(scene_pos)
            elif self.tool in ["move_image", "move_svg", "move_sym"]: self.drawing = True
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag); super().mousePressEvent(event)
        elif event.button() == Qt.MouseButton.RightButton:
            if self.tool == "poly": self.finish_poly()
            elif self.tool == "curve": self.finish_curve()

    def mouseMoveEvent(self, event):
        scene_pos = self.snap_point(self.mapToScene(event.pos()))
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
                elif self.tool.startswith("custom:") and hasattr(self.current_item, '_custom_base'):
                    self.current_item.setPath(self._scale_custom_path(self.current_item._custom_base, local_pos))
                    self.update_clones(self.current_item)
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
        p = self.get_pen(alpha)
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

    def cancel_poly(self):
        if self.current_item:
            self.save_to_undo(self.current_item)
        self.current_item = None; self.poly_points = []

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape and self.tool == "poly": self.cancel_poly()
        else: super().keyPressEvent(event)

    def handle_curve_click(self, pos):
        origin = self.current_item.pos() if self.current_item else pos
        if self.curve_state == 0:
            self.curve_points = [pos]; self.curve_state = 1; self.current_item = SymPath(QPainterPath()); self.current_item.setPos(pos)
            self.current_item.setPen(self.get_pen()); self.scene().addItem(self.current_item); self.create_symmetry_clones(self.current_item)
            self.persistent_path = QPainterPath(); self.persistent_path.moveTo(0, 0)
        elif self.curve_state == 1:
            self.curve_points.append(pos); self.curve_state = 2
        elif self.curve_state == 2:
            self.persistent_path.quadTo(pos - origin, self.curve_points[1] - origin)
            self.curve_points = [self.curve_points[1]]; self.curve_state = 1; self.update_curve_preview()

    def update_curve_preview(self, pos=None):
        if not self.current_item: return
        path = QPainterPath(self.persistent_path); origin = self.current_item.pos()
        if pos:
            if self.curve_state == 1: path.lineTo(pos - origin)
            elif self.curve_state == 2: path.quadTo(pos - origin, self.curve_points[1] - origin)
        self.current_item.setPath(path); self.update_clones(self.current_item)

    def finish_curve(self):
        if self.current_item:
            path = QPainterPath(self.persistent_path)
            if self.curve_state == 2:
                path.closeSubpath()
            self.current_item.setPath(path); self.update_clones(self.current_item); self.save_to_undo(self.current_item)
        self.current_item = None; self.curve_points = []; self.curve_state = 0
    def reset_curve(self):
        if self.current_item:
            self.scene().removeItem(self.current_item); [self.scene().removeItem(c) for c in getattr(self.current_item, 'symmetry_clones', [])]
        self.current_item = None; self.curve_points = []; self.curve_state = 0


    def _scale_custom_path(self, points, local_pos):
        """Scale stored path points (normalized 0-1) to fit drag bounding box."""
        path = QPainterPath()
        w, h = local_pos.x() or 1, local_pos.y() or 1
        for i, (cmd, *args) in enumerate(points):
            scaled = [QPointF(p[0] * w, p[1] * h) for p in args]
            if cmd == "M": path.moveTo(scaled[0])
            elif cmd == "L": path.lineTo(scaled[0])
            elif cmd == "Q": path.quadTo(scaled[0], scaled[1])
            elif cmd == "C": path.cubicTo(scaled[0], scaled[1], scaled[2])
            elif cmd == "Z": path.closeSubpath()
        return path

    def collect_art_as_shape(self):
        """Collect all art items and return normalized path commands (0-1 range)."""
        items = [i for i in self.scene().items() if getattr(i, 'is_art_item', False)]
        if not items: return None
        bounds = QRectF()
        for item in items: bounds = bounds.united(item.mapToScene(item.boundingRect()).boundingRect())
        if bounds.isEmpty(): return None
        w, h = bounds.width() or 1, bounds.height() or 1
        commands = []
        for item in items:
            if isinstance(item, QGraphicsPathItem):
                path = item.path()
                for i in range(path.elementCount()):
                    el = path.elementAt(i)
                    sp = item.mapToScene(QPointF(el.x, el.y))
                    nx, ny = (sp.x() - bounds.x()) / w, (sp.y() - bounds.y()) / h
                    if el.type == QPainterPath.ElementType.MoveToElement: commands.append(["M", [nx, ny]])
                    elif el.type == QPainterPath.ElementType.LineToElement: commands.append(["L", [nx, ny]])
                    elif el.type == QPainterPath.ElementType.CurveToElement: commands.append(["_C", [nx, ny]])
                    elif el.type == QPainterPath.ElementType.CurveToDataElement:
                        if commands and commands[-1][0] in ["_C", "_CD"]:
                            commands.append(["_CD", [nx, ny]])
                            # flush cubic when we have 3 control points
                            ctrl = [c for c in commands if c[0] in ["_C", "_CD"]]
                            if len(ctrl) >= 2:
                                pts = [c[1] for c in ctrl[-2:]] + [[nx, ny]]
                                commands = [c for c in commands if c[0] not in ["_C", "_CD"]]
                                commands.append(["C", pts[0], pts[1], [nx, ny]])
            elif isinstance(item, QGraphicsRectItem):
                r = item.mapRectToScene(item.rect())
                pts = [(r.left(), r.top()), (r.right(), r.top()), (r.right(), r.bottom()), (r.left(), r.bottom())]
                commands.append(["M", [(pts[0][0]-bounds.x())/w, (pts[0][1]-bounds.y())/h]])
                for px, py in pts[1:]: commands.append(["L", [(px-bounds.x())/w, (py-bounds.y())/h]])
                commands.append(["Z"])
            elif isinstance(item, QGraphicsEllipseItem):
                r = item.mapRectToScene(item.rect())
                cx, cy = (r.center().x()-bounds.x())/w, (r.center().y()-bounds.y())/h
                rx, ry = r.width()/2/w, r.height()/2/h
                # approximate ellipse with 4 cubic beziers
                k = 0.5523
                commands += [["M",[cx,cy-ry]],["C",[cx+k*rx,cy-ry],[cx+rx,cy-k*ry],[cx+rx,cy]],
                              ["C",[cx+rx,cy+k*ry],[cx+k*rx,cy+ry],[cx,cy+ry]],
                              ["C",[cx-k*rx,cy+ry],[cx-rx,cy+k*ry],[cx-rx,cy]],
                              ["C",[cx-rx,cy-k*ry],[cx-k*rx,cy-ry],[cx,cy-ry]],["Z"]]
        # clean up any leftover _C/_CD
        commands = [c for c in commands if not c[0].startswith("_")]
        return commands

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

class ShapePickerDialog(QDialog):
    def __init__(self, custom_shapes, pixmap_cache, on_delete, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Custom Shapes"); self.setModal(True)
        self.setStyleSheet(f"background-color: {CP_BG}; color: {CP_TEXT}; font-family: Consolas;")
        self.selected = None; self.custom_shapes = custom_shapes
        self.pixmap_cache = pixmap_cache; self.on_delete = on_delete
        self.layout_ = QVBoxLayout(self); self.layout_.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)
        self._build_grid()

    def _build_grid(self):
        from PyQt6.QtWidgets import QGridLayout
        if self.layout_.count():
            old = self.layout_.takeAt(0).widget()
            if old: old.deleteLater()
        container = QWidget(); gl = QGridLayout(container); gl.setSpacing(10); gl.setContentsMargins(10,10,10,10)
        COLS, SIZE, LABEL_H = 4, 100, 36
        for i, (name, cmds) in enumerate(self.custom_shapes.items()):
            cell = QWidget(); cell.setFixedSize(SIZE + 4, SIZE + LABEL_H)
            cell.setStyleSheet(f"background: {CP_PANEL}; border: 1px solid {CP_DIM};")
            vl = QVBoxLayout(cell); vl.setContentsMargins(2, 2, 2, 2); vl.setSpacing(0)
            lbl = QLabel(); lbl.setFixedSize(SIZE, SIZE)
            lbl.setPixmap(self.pixmap_cache.get(name) or self.build_pixmap(cmds, SIZE, SIZE))
            lbl.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            lbl.mousePressEvent = lambda e, n=name: self._pick(n)
            vl.addWidget(lbl)
            nl = QLabel(name.upper()); nl.setStyleSheet(f"color: {CP_ORANGE}; font-size: 7pt; font-weight: bold; border: none;")
            nl.setAlignment(Qt.AlignmentFlag.AlignCenter); nl.setFixedHeight(18)
            vl.addWidget(nl)
            del_btn = QPushButton("✕ remove"); del_btn.setFixedHeight(16)
            del_btn.setStyleSheet(f"color: {CP_RED}; background: transparent; border: none; font-size: 7pt; padding: 0;")
            del_btn.clicked.connect(lambda checked, n=name: self._delete(n))
            vl.addWidget(del_btn)
            gl.addWidget(cell, i // COLS, i % COLS)
        self.layout_.addWidget(container)

    @staticmethod
    def build_pixmap(cmds, w, h):
        px = QPixmap(w, h); px.fill(QColor(CP_PANEL))
        p = QPainter(px); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(QPen(QColor(CP_CYAN), 1.5))
        path = QPainterPath()
        pw, ph = w - 10, h - 10
        for cmd, *args in cmds:
            pts = [QPointF(a[0] * pw + 5, a[1] * ph + 5) for a in args]
            if cmd == "M": path.moveTo(pts[0])
            elif cmd == "L": path.lineTo(pts[0])
            elif cmd == "Q": path.quadTo(pts[0], pts[1])
            elif cmd == "C": path.cubicTo(pts[0], pts[1], pts[2])
            elif cmd == "Z": path.closeSubpath()
        p.drawPath(path); p.end()
        return px

    def _pick(self, name): self.selected = name; self.accept()

    def _delete(self, name):
        del self.custom_shapes[name]; self.pixmap_cache.pop(name, None); self.on_delete()
        self._build_grid(); self.adjustSize()


class SVGInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("IMPORT SVG SHAPE")
        self.setFixedSize(500, 450)
        self.setStyleSheet(f"background-color: {CP_BG}; color: {CP_TEXT}; font-family: 'Consolas';")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("SHAPE NAME:"))
        self.name_edit = QLineEdit()
        self.name_edit.setStyleSheet(f"background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; color: {CP_CYAN}; padding: 5px;")
        layout.addWidget(self.name_edit)
        layout.addWidget(QLabel("SVG CODE / PATH DATA (d=...):"))
        self.text_edit = QPlainTextEdit()
        self.text_edit.setStyleSheet(f"background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; color: {CP_TEXT}; font-size: 9pt;")
        self.text_edit.setPlaceholderText("<path d=\"M 10 10 L 90 90 ...\" />\nor just the path data: M 10 10 L 90 90 ...")
        layout.addWidget(self.text_edit)
        btns = QHBoxLayout()
        self.btn_ok = QPushButton("IMPORT")
        self.btn_ok.setStyleSheet(f"background-color: {CP_GREEN}; color: black; font-weight: bold; padding: 8px;")
        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel = QPushButton("CANCEL")
        self.btn_cancel.setStyleSheet(f"background-color: {CP_DIM}; color: white; padding: 8px;")
        self.btn_cancel.clicked.connect(self.reject)
        btns.addWidget(self.btn_ok); btns.addWidget(self.btn_cancel)
        layout.addLayout(btns)

class SVGArtApp(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle("NEURAL ART V1.6.2 - SYNCED"); self.resize(1400, 900)
        self.setup_ui(); self.apply_theme(); self.toggle_sharp(); self.load_settings(); self.load_custom_shapes()

    def setup_ui(self):
        self.central_widget = QWidget(); self.setCentralWidget(self.central_widget); self.main_layout = QVBoxLayout(self.central_widget)
        self.tb_main = QToolBar("Main"); self.tb_main.setObjectName("MainToolbar"); self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.tb_main)
        self.add_tool_action(self.tb_main, "BRUSH", "brush", CP_CYAN); self.brush_combo = QComboBox(); self.brush_combo.addItems(["Marker", "Airbrush", "Multiline", "Highlighter"]); self.brush_combo.currentTextChanged.connect(self.set_brush_type); self.tb_main.addWidget(self.brush_combo)
        self.tb_main.addWidget(QLabel(" LINES: ")); self.multi_slider = QSpinBox(); self.multi_slider.setRange(1, 100); self.multi_slider.setValue(3); self.multi_slider.valueChanged.connect(self.set_multi_count); self.tb_main.addWidget(self.multi_slider)
        self.add_tool_action(self.tb_main, "POLY", "poly", CP_GREEN); self.add_tool_action(self.tb_main, "CURVE", "curve", CP_GREEN); self.add_tool_action(self.tb_main, "ERASE", "eraser", CP_RED); self.add_tool_action(self.tb_main, "FILL", "fill", CP_YELLOW); self.add_tool_action(self.tb_main, "PICK", "picker", CP_CYAN)
        self.tb_shapes = QToolBar("Shapes"); self.tb_shapes.setObjectName("ShapesToolbar"); self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.tb_shapes)
        self.add_tool_action(self.tb_shapes, "RECT", "rect", CP_ORANGE); self.add_tool_action(self.tb_shapes, "CIRC", "ellipse", CP_ORANGE); self.add_tool_action(self.tb_shapes, "TRI", "triangle", CP_ORANGE)
        btn_add_shape = QPushButton("+"); btn_add_shape.setToolTip("Save current art as custom shape"); btn_add_shape.setStyleSheet(f"color: {CP_GREEN}; font-weight: bold; font-size: 14pt; padding: 0px 6px;"); btn_add_shape.clicked.connect(self.add_custom_shape); self.tb_shapes.addWidget(btn_add_shape)
        btn_import_svg = QPushButton("SVG+"); btn_import_svg.setToolTip("Import shape by SVG code"); btn_import_svg.setStyleSheet(f"color: {CP_CYAN}; font-weight: bold; font-size: 10pt; padding: 0px 6px;"); btn_import_svg.clicked.connect(self.add_svg_shape); self.tb_shapes.addWidget(btn_import_svg)
        btn_list_shapes = QPushButton("SHAPE"); btn_list_shapes.setToolTip("Browse custom shapes"); btn_list_shapes.setStyleSheet(f"color: {CP_CYAN}; font-weight: bold;"); btn_list_shapes.clicked.connect(self.show_shape_picker); self.tb_shapes.addWidget(btn_list_shapes)
        self.tb_shapes.addSeparator(); self.add_tool_action(self.tb_shapes, "MOVE IMG", "move_image", CP_SUBTEXT); self.add_tool_action(self.tb_shapes, "MOVE SVG", "move_svg", CP_SUBTEXT); self.add_tool_action(self.tb_shapes, "MOVE SYM", "move_sym", CP_YELLOW)
        self.tb_props = QToolBar("Properties"); self.tb_props.setObjectName("PropsToolbar"); self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.tb_props)
        self.btn_color = QPushButton("COLOR"); self.btn_color.clicked.connect(self.choose_color); self.tb_props.addWidget(self.btn_color)
        self.tb_props.addWidget(QLabel(" THICK: ")); self.thickness_slider = QSpinBox(); self.thickness_slider.setRange(1, 100); self.thickness_slider.setValue(3); self.thickness_slider.valueChanged.connect(self.change_thickness); self.tb_props.addWidget(self.thickness_slider)
        self.btn_sharp = QPushButton("SHARP"); self.btn_sharp.setCheckable(True); self.btn_sharp.setChecked(True); self.btn_sharp.clicked.connect(self.toggle_sharp); self.tb_props.addWidget(self.btn_sharp)
        
        self.tb_grid = QToolBar("Grid"); self.tb_grid.setObjectName("GridToolbar"); self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.tb_grid)
        self.btn_show_grid = QPushButton("GRID"); self.btn_show_grid.setCheckable(True); self.btn_show_grid.clicked.connect(self.toggle_grid); self.tb_grid.addWidget(self.btn_show_grid)
        self.btn_snap_grid = QPushButton("SNAP"); self.btn_snap_grid.setCheckable(True); self.btn_snap_grid.clicked.connect(self.toggle_snap); self.tb_grid.addWidget(self.btn_snap_grid)
        self.tb_grid.addWidget(QLabel(" SIZE: ")); self.grid_size_spin = QSpinBox(); self.grid_size_spin.setRange(5, 200); self.grid_size_spin.setValue(20); self.grid_size_spin.valueChanged.connect(self.change_grid_size); self.tb_grid.addWidget(self.grid_size_spin)

        self.tb_sym = QToolBar("Symmetry"); self.tb_sym.setObjectName("SymmetryToolbar"); self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.tb_sym)
        self.tb_sym.addWidget(QLabel(" SYMMETRY ")); self.sym_combo = QComboBox(); self.sym_combo.addItems(["None", "Radial", "Reflect (H)", "Reflect (V)", "Reflect (B)"]); self.sym_combo.currentTextChanged.connect(self.set_symmetry_mode); self.tb_sym.addWidget(self.sym_combo)
        self.tb_sym.addWidget(QLabel(" MIRROR: ")); self.mirror_spin = QSpinBox(); self.mirror_spin.setRange(2, 100); self.mirror_spin.setValue(4); self.mirror_spin.valueChanged.connect(self.set_mirror_count); self.tb_sym.addWidget(self.mirror_spin)
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
    def toggle_sharp(self):
        self.view.is_sharp = self.btn_sharp.isChecked()
        color = CP_GREEN if self.view.is_sharp else CP_DIM
        self.btn_sharp.setStyleSheet(f"background-color: {color}; color: white; font-weight: bold; padding: 4px 8px;")

    def toggle_grid(self):
        self.scene.show_grid = self.btn_show_grid.isChecked()
        color = CP_CYAN if self.scene.show_grid else CP_DIM
        self.btn_show_grid.setStyleSheet(f"background-color: {color}; color: white; font-weight: bold; padding: 4px 8px;")
        self.scene.update()

    def toggle_snap(self):
        self.view.snap_to_grid = self.btn_snap_grid.isChecked()
        color = CP_GREEN if self.view.snap_to_grid else CP_DIM
        self.btn_snap_grid.setStyleSheet(f"background-color: {color}; color: white; font-weight: bold; padding: 4px 8px;")

    def change_grid_size(self, v):
        self.view.grid_size = v; self.scene.grid_size = v; self.scene.update()

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

    def load_custom_shapes(self):
        if os.path.exists(CUSTOM_SHAPES_FILE):
            try:
                with open(CUSTOM_SHAPES_FILE, 'r') as f:
                    self.view.custom_shapes = json.load(f)
            except: self.view.custom_shapes = {}
        self._shape_pixmap_cache = {name: ShapePickerDialog.build_pixmap(cmds, 100, 100) for name, cmds in self.view.custom_shapes.items()}

    def save_custom_shapes(self):
        try:
            os.makedirs(os.path.dirname(CUSTOM_SHAPES_FILE), exist_ok=True)
            with open(CUSTOM_SHAPES_FILE, 'w') as f: json.dump(self.view.custom_shapes, f)
        except: pass

    def add_custom_shape(self):
        cmds = self.view.collect_art_as_shape()
        if not cmds:
            QMessageBox.warning(self, "No Art", "Draw something first to save as a custom shape."); return
        name, ok = QInputDialog.getText(self, "Shape Name", "Enter shape name:")
        if ok and name.strip():
            n = name.strip(); self.view.custom_shapes[n] = cmds
            self._shape_pixmap_cache[n] = ShapePickerDialog.build_pixmap(cmds, 100, 100)
            self.save_custom_shapes()

    def show_shape_picker(self):
        if not self.view.custom_shapes:
            QMessageBox.information(self, "No Shapes", "No custom shapes saved yet."); return
        dlg = ShapePickerDialog(self.view.custom_shapes, self._shape_pixmap_cache, self.save_custom_shapes, self)
        if dlg.exec() and dlg.selected:
            self.set_tool(f"custom:{dlg.selected}")

    def add_svg_shape(self):
        dlg = SVGInputDialog(self)
        if dlg.exec():
            name = dlg.name_edit.text().strip()
            svg_code = dlg.text_edit.toPlainText().strip()
            if name and svg_code:
                cmds = self.parse_svg_to_shape(svg_code)
                if cmds:
                    self.view.custom_shapes[name] = cmds
                    self._shape_pixmap_cache[name] = ShapePickerDialog.build_pixmap(cmds, 100, 100)
                    self.save_custom_shapes()
                    QMessageBox.information(self, "Success", f"Shape '{name}' added!")
                else:
                    QMessageBox.warning(self, "Error", "Could not parse SVG code. Ensure it has a <path d='...' /> or valid path data.")

    def parse_svg_to_shape(self, svg_code):
        d_match = re.search(r'\bd=["\']([^"\']+)["\']', svg_code)
        d_string = d_match.group(1) if d_match else svg_code
        token_pattern = re.compile(r'([a-zA-Z])|([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)')
        tokens = []
        for m in token_pattern.finditer(d_string):
            if m.group(1): tokens.append(m.group(1))
            else: tokens.append(float(m.group(2)))
        commands = []; i = 0; cur_x, cur_y = 0, 0; last_cmd = ""
        while i < len(tokens):
            token = tokens[i]
            if isinstance(token, str): cmd = token; i += 1
            else: cmd = last_cmd
            if not cmd: break
            try:
                if cmd in 'Mm':
                    x, y = tokens[i], tokens[i+1]; i += 2
                    if cmd == 'm': x += cur_x; y += cur_y
                    commands.append(["M", [x, y]]); cur_x, cur_y = x, y; last_cmd = 'L' if cmd == 'M' else 'l'
                elif cmd in 'Ll':
                    x, y = tokens[i], tokens[i+1]; i += 2
                    if cmd == 'l': x += cur_x; y += cur_y
                    commands.append(["L", [x, y]]); cur_x, cur_y = x, y; last_cmd = cmd
                elif cmd in 'Hh':
                    x = tokens[i]; i += 1
                    if cmd == 'h': x += cur_x
                    commands.append(["L", [x, cur_y]]); cur_x = x; last_cmd = cmd
                elif cmd in 'Vv':
                    y = tokens[i]; i += 1
                    if cmd == 'v': y += cur_y
                    commands.append(["L", [cur_x, y]]); cur_y = y; last_cmd = cmd
                elif cmd in 'Qq':
                    x1, y1 = tokens[i], tokens[i+1]; i += 2; x, y = tokens[i], tokens[i+1]; i += 2
                    if cmd == 'q': x1 += cur_x; y1 += cur_y; x += cur_x; y += cur_y
                    commands.append(["Q", [x1, y1], [x, y]]); cur_x, cur_y = x, y; last_cmd = cmd
                elif cmd in 'Cc':
                    x1, y1 = tokens[i], tokens[i+1]; i += 2; x2, y2 = tokens[i], tokens[i+1]; i += 2; x, y = tokens[i], tokens[i+1]; i += 2
                    if cmd == 'c': x1 += cur_x; y1 += cur_y; x2 += cur_x; y2 += cur_y; x += cur_x; y += cur_y
                    commands.append(["C", [x1, y1], [x2, y2], [x, y]]); cur_x, cur_y = x, y; last_cmd = cmd
                elif cmd in 'Zz':
                    commands.append(["Z"]); last_cmd = ""
                else: i += 1
            except: break
        if not commands: return None
        all_pts = []
        for c in commands:
            for pt in c[1:]: all_pts.append(QPointF(pt[0], pt[1]))
        if not all_pts: return None
        rect = QRectF(all_pts[0], all_pts[0])
        for p in all_pts[1:]: rect = rect.united(QRectF(p, p))
        w, h = rect.width() or 1, rect.height() or 1
        norm_cmds = []
        for c in commands:
            pts = [[(p[0]-rect.x())/w, (p[1]-rect.y())/h] for p in c[1:]]
            norm_cmds.append([c[0]] + pts)
        return norm_cmds

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    s = json.load(f)
                    if "geom" in s: self.restoreGeometry(QByteArray.fromHex(s["geom"].encode()))
                    if "state" in s: self.restoreState(QByteArray.fromHex(s["state"].encode()))
                    self.view.tool = s.get("tool", "brush"); self.view.brush_type = s.get("brush_type", "marker"); self.view.pen_color = QColor(s.get("color", CP_CYAN)); self.view.pen_width = s.get("width", 3); self.view.multi_line_count = s.get("multi_count", 3); sm = s.get("symmetry_mode", "None"); self.view.symmetry_mode = sm; self.sym_combo.setCurrentText(sm); self.view.mirror_count = s.get("mirror_count", 4); self.view.sym_center = QPointF(s.get("sym_x", 0), s.get("sym_y", 0)); self.scene.center_marker.setPos(self.view.sym_center); self.scene.center_marker_v.setPos(self.view.sym_center); self.brush_combo.setCurrentText(self.view.brush_type.capitalize()); self.thickness_slider.setValue(self.view.pen_width); self.multi_slider.setValue(self.view.multi_line_count); self.mirror_spin.setValue(self.view.mirror_count); self.update_color_ui(self.view.pen_color); ip = s.get("img_path", "")
                    self.view.is_sharp = s.get("is_sharp", True); self.btn_sharp.setChecked(self.view.is_sharp); self.toggle_sharp()
                    
                    self.scene.show_grid = s.get("show_grid", False); self.btn_show_grid.setChecked(self.scene.show_grid); self.toggle_grid()
                    self.view.snap_to_grid = s.get("snap_to_grid", False); self.btn_snap_grid.setChecked(self.view.snap_to_grid); self.toggle_snap()
                    gs = s.get("grid_size", 20); self.view.grid_size = gs; self.scene.grid_size = gs; self.grid_size_spin.setValue(gs)

                    if ip and os.path.exists(ip):
                        self.load_image(ip)
                        if self.view.image_item: self.view.image_item.setPos(s.get("img_x", 0), s.get("img_y", 0))
            except: pass

    def save_settings(self):
        s = {"geom": self.saveGeometry().toHex().data().decode(), "state": self.saveState().toHex().data().decode(), "tool": self.view.tool, "brush_type": self.view.brush_type, "color": self.view.pen_color.name(), "width": self.view.pen_width, "multi_count": self.view.multi_line_count, "symmetry_mode": self.view.symmetry_mode, "mirror_count": self.view.mirror_count, "sym_x": self.view.sym_center.x(), "sym_y": self.view.sym_center.y(), "img_path": self.view.image_path, "img_x": self.view.image_item.x() if self.view.image_item else 0, "img_y": self.view.image_item.y() if self.view.image_item else 0, "is_sharp": self.view.is_sharp,
             "show_grid": self.scene.show_grid, "snap_to_grid": self.view.snap_to_grid, "grid_size": self.view.grid_size}
        try:
            os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
            with open(SETTINGS_FILE, 'w') as f: json.dump(s, f)
        except: pass

    def closeEvent(self, e): self.save_settings(); super().closeEvent(e)
    def apply_theme(self):
        self.setStyleSheet(f"QMainWindow {{ background-color: {CP_BG}; }} QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }} QToolBar {{ background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; spacing: 5px; padding: 3px; }} QPushButton {{ background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 4px 8px; font-weight: bold; font-size: 9pt; }} QPushButton:hover {{ background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }} QComboBox {{ background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 2px; }} QSpinBox {{ background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 2px; max-width: 36px; }} QSpinBox::up-button, QSpinBox::down-button {{ width: 0; height: 0; border: none; }} QStatusBar {{ background-color: {CP_PANEL}; color: {CP_CYAN}; border-top: 1px solid {CP_DIM}; }}")

if __name__ == "__main__":
    app = QApplication(sys.argv); window = SVGArtApp(); window.show(); sys.exit(app.exec())
