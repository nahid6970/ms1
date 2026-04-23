import sys
import os
import math
import json
import re
import urllib.request
import difflib
from functools import partial
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QToolBar, QFileDialog, QColorDialog, QSlider, 
                             QLabel, QGraphicsView, QGraphicsScene, QGraphicsPathItem,
                             QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsLineItem,
                             QGraphicsPixmapItem, QFrame, QGroupBox, QFormLayout, QDialog, 
                             QSizePolicy, QComboBox, QGraphicsBlurEffect, QInputDialog,
                             QMessageBox, QMenu, QSpinBox, QPlainTextEdit, QLineEdit, QScrollArea,
                             QCheckBox)
from PyQt6.QtCore import Qt, QPointF, QRectF, QLineF, QSize, QByteArray, QTimer
from PyQt6.QtGui import (QPainter, QPen, QColor, QPainterPath, QPixmap, QCursor, QAction, QIcon, QTransform, QBrush, QKeySequence, QFont)
from PyQt6 import QtSvg
from PyQt6.QtSvg import QSvgGenerator, QSvgRenderer

# CONVEX CONFIG
CONVEX_URL = "https://different-gnat-734.convex.cloud"
SCRIPT_NAME = "svg_art_tool"

SVGS = {
    "UPLOAD": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>',        
    "DOWNLOAD": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>',   
    "TRASH": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2-0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>',
    "DIFF": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>',
    "SYNC": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"></path><path d="M21 3v5h-5"></path><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"></path><path d="M3 21v-5h5"></path></svg>',
    "SHAPE_LIB": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5z"></path><path d="M2 17l10 5 10-5"></path><path d="M2 12l10 5 10-5"></path></svg>',
    "ADD_SHAPE": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>',
    "IMPORT_SVG": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="12" y1="18" x2="12" y2="12"></line><line x1="9" y1="15" x2="15" y2="15"></line></svg>',
    "UNDO": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7v6h6"></path><path d="M21 17a9 9 0 0 0-9-9 9 9 0 0 0-6 2.3L3 13"></path></svg>',
    "REDO": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 7v6h-6"></path><path d="M3 17a9 9 0 0 1 9-9 9 9 0 0 1 6 2.3l3 2.7"></path></svg>',
    "IMAGE": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>',
    "SAVE_DISK": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline></svg>',
    "RESTART": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 4v6h-6"></path><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path></svg>',
    "COPY": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>',
    "EDIT": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>',
    "BRUSH": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9.06 11.9 8.07-8.06a2.85 2.85 0 1 1 4.03 4.03l-8.06 8.08"></path><path d="M7.07 14.94c-3.91.35-7.07 3.73-7.07 7.72 0 1.1.9 2 2 2 3.99 0 7.37-3.16 7.72-7.07"></path><path d="m2 22 3-3"></path></svg>',
    "POLYGON": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="5" x2="5" y2="19"></line></svg>',
    "CURVE": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 19c5-15 14-15 14 0"></path></svg>',
    "ERASER": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m7 21-4.3-4.3c-1-1-1-2.5 0-3.4l9.6-9.6c1-1 2.5-1 3.4 0l5.6 5.6c1 1 1 2.5 0 3.4L13 21"></path><path d="M22 21H7"></path><path d="m5 11 9 9"></path></svg>',
    "PAINT_BUCKET": '<svg viewBox="0 -32 576 576" xmlns="http://www.w3.org/2000/svg"><path fill="#3a3a3a" d="M502.63 217.06L294.94 9.37C288.69 3.12 280.5 0 272.31 0s-16.38 3.12-22.62 9.37l-81.58 81.58L81.93 4.76c-6.25-6.25-16.38-6.25-22.62 0L36.69 27.38c-6.24 6.25-6.24 16.38 0 22.62l86.19 86.18-94.76 94.76c-37.49 37.48-37.49 98.26 0 135.75l117.19 117.19c18.74 18.74 43.31 28.12 67.87 28.12 24.57 0 49.13-9.37 67.87-28.12l221.57-221.57c12.5-12.5 12.5-32.75.01-45.25z" /><path fill="currentColor" d="M512 320s-64 92.65-64 128c0 35.35 28.66 64 64 64s64-28.65 64-64-64-128-64-128z M386.41 288.03H65.93c1.36-3.84 3.57-7.98 7.43-11.83l13.15-13.15 81.61-81.61 58.6 58.6c12.49 12.49 32.75 12.49 45.24 0s12.49-32.75 0-45.24l-58.6-58.6 58.95-58.95 162.44 162.44-48.34 48.34z" /></svg>',
    "EYEDROPPER": '<svg viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg" fill="currentColor"><path d="M17.8 2.2c-1-1-2.6-1-3.6 0L12.4 4l-.7-.7c-.4-.4-1-.4-1.4 0l-.8.7c-.4.4-.4 1 0 1.4l5 5c.4.4 1 .4 1.4 0l.7-.7c.4-.4.4-1 0-1.4l-.6-.7 1.8-1.8c1-1 1-2.6 0-3.6zM4.4 12c-2.2 2.2-.9 3.2-2.9 5.8l.7.7c2.6-2 3.6-.7 5.8-2.9l5.1-5.1-3.6-3.6L4.4 12z"></path></svg>',
    "RECTANGLE": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"></rect></svg>',
    "CIRCLE": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle></svg>',
    "TRIANGLE": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13.73 4a2 2 0 0 0-3.46 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path></svg>',
    "CENTER": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="22" y1="12" x2="18" y2="12"></line><line x1="6" y1="12" x2="2" y2="12"></line><line x1="12" y1="6" x2="12" y2="2"></line><line x1="12" y1="22" x2="12" y2="18"></line></svg>',
    "ZOOM_IN": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line><line x1="11" y1="8" x2="11" y2="14"></line><line x1="8" y1="11" x2="14" y2="11"></line></svg>',
    "ZOOM_OUT": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line><line x1="8" y1="11" x2="14" y2="11"></line></svg>',
    "SCAN": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7V5a2 2 0 0 1 2-2h2"></path><path d="M17 3h2a2 2 0 0 1 2 2v2"></path><path d="M21 17v2a2 2 0 0 1-2 2h-2"></path><path d="M7 21H5a2 2 0 0 1-2-2v-2"></path><line x1="7" y1="12" x2="17" y2="12"></line></svg>',
    "PALETTE": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="13.5" cy="6.5" r=".5"></circle><circle cx="17.5" cy="10.5" r=".5"></circle><circle cx="8.5" cy="7.5" r=".5"></circle><circle cx="6.5" cy="12.5" r=".5"></circle><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.9 0 1.6-.7 1.6-1.6 0-.4-.2-.8-.5-1.1-.3-.3-.4-.7-.4-1.1 0-.9.7-1.6 1.6-1.6H17c2.8 0 5-2.2 5-5 0-5.5-4.5-10-10-10z"></path></svg>',
    "GLITCH": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="4 7 4 4 20 4 20 7"></polyline><line x1="9" y1="20" x2="15" y2="20"></line><line x1="12" y1="4" x2="12" y2="20"></line></svg>',
    "MOVE_ALL": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 9l-3 3 3 3M9 5l3-3 3 3M15 19l-3 3-3-3M19 9l3 3-3 3M2 12h20M12 2v20"></path></svg>',
    "REMOVE_IMAGE": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="9" y1="9" x2="15" y2="15"></line><line x1="15" y1="9" x2="9" y2="15"></line></svg>'
}

class ConvexButton(QPushButton):
    def __init__(self, text="", parent=None, color="#FCEE0A", is_outlined=False, svg_data=None):
        super().__init__(text, parent)
        self.color = color; self.is_outlined = is_outlined; self.svg_data = svg_data
        self.setFont(QFont("Consolas", 9, QFont.Weight.Bold)); self.setCursor(Qt.CursorShape.PointingHandCursor); self.setFixedHeight(34)
        if svg_data: self.update_icon(self.color if self.is_outlined else "#050505")
        self.update_style()

    def update_icon(self, color):
        if not self.svg_data: return
        colored_svg = self.svg_data.replace('currentColor', color)
        renderer = QSvgRenderer(QByteArray(colored_svg.encode()))
        pix = QPixmap(18, 18); pix.fill(Qt.GlobalColor.transparent); painter = QPainter(pix)
        renderer.render(painter); painter.end(); self.setIcon(QIcon(pix)); self.setIconSize(QSize(18, 18))

    def enterEvent(self, event):
        if self.svg_data: self.update_icon("#050505" if self.is_outlined else self.color)
        super().enterEvent(event)
    def leaveEvent(self, event):
        if self.svg_data: self.update_icon(self.color if self.is_outlined else "#050505")
        super().leaveEvent(event)
    def update_style(self):
        if self.is_outlined: self.setStyleSheet(f"QPushButton {{ background-color: transparent; color: {self.color}; border: 2px solid {self.color}; padding: 5px 15px; }} QPushButton:hover {{ background-color: {self.color}; color: #050505; }}")
        else: self.setStyleSheet(f"QPushButton {{ background-color: {self.color}; color: #050505; border: none; padding: 5px 15px; }} QPushButton:hover {{ background-color: #050505; color: {self.color}; border: 1px solid {self.color}; }}")

class DiffDialog(QDialog):
    def __init__(self, local_data, remote_data, title="SYSTEM // DIFF_VIEW", parent=None):
        super().__init__(parent); self.setWindowTitle(title); self.resize(900, 700); self.setObjectName("DiffDialog")
        self.setStyleSheet(f"#DiffDialog {{ background-color: {CP_BG}; border: 2px solid {CP_CYAN}; }} QLabel {{ border: none; }}")
        layout = QVBoxLayout(self)
        header = QLabel("COMPARISON: REMOTE (RED) vs LOCAL (GREEN)")
        header.setStyleSheet(f"color: {CP_YELLOW}; font-family: Consolas; font-weight: bold;"); layout.addWidget(header)
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet(f"QScrollArea {{ border: 1px solid {CP_DIM}; background: {CP_BG}; }}")
        content = QWidget(); vbox = QVBoxLayout(content); vbox.setSpacing(0); vbox.setContentsMargins(0,0,0,0)
        def fix(obj):
            if isinstance(obj, dict): return {k: fix(v) for k, v in obj.items()}
            if isinstance(obj, list): return [fix(i) for i in obj]
            if isinstance(obj, float) and obj.is_integer(): return int(obj)
            return obj
        l_str = json.dumps(fix(local_data), indent=2, sort_keys=True).splitlines()
        r_str = json.dumps(fix(remote_data), indent=2, sort_keys=True).splitlines()
        # Use a large context (n) to show the whole file, including unchanged custom shapes
        diff = list(difflib.unified_diff(r_str, l_str, fromfile='Backup', tofile='Local', lineterm='', n=10000))
        if not diff: vbox.addWidget(QLabel("No differences detected."))
        else:
            for line in diff:
                lbl = QLabel(line); lbl.setFont(QFont("Consolas", 9)); lbl.setContentsMargins(5, 1, 5, 1)
                if line.startswith('+'): lbl.setStyleSheet("background-color: #12261e; color: #3fb950;")
                elif line.startswith('-'): lbl.setStyleSheet("background-color: #2c1619; color: #f85149;")
                else: lbl.setStyleSheet(f"color: {CP_TEXT};")
                vbox.addWidget(lbl)
        vbox.addStretch(); self.scroll.setWidget(content); layout.addWidget(self.scroll)
        close = ConvexButton("CLOSE", color=CP_DIM, is_outlined=True)
        close.clicked.connect(self.accept); layout.addWidget(close)

class CloudSyncDialog(QDialog):
    def __init__(self, convex_call_fn, config_data, parent=None):
        super().__init__(parent); self.setWindowTitle("CLOUD // SYNC MANAGER"); self.resize(550, 750)
        self._convex_call = convex_call_fn; self._config_data = config_data; self._backups = []
        self.selected_id = None; self.setStyleSheet(f"QDialog {{ background-color: {CP_BG}; border: 2px solid {CP_CYAN}; }} QLabel {{ color: {CP_TEXT}; font-family: Consolas; }} QLineEdit {{ background: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 8px; }} QGroupBox {{ color: {CP_YELLOW}; font-weight: bold; border: 1px solid {CP_DIM}; margin-top: 10px; padding-top: 15px; }}")
        layout = QVBoxLayout(self); grp_new = QGroupBox("CREATE NEW BACKUP"); new_lay = QVBoxLayout(grp_new)
        self.inp_label = QLineEdit(); self.inp_label.setPlaceholderText("Enter backup label..."); new_lay.addWidget(self.inp_label)
        btn_row = QHBoxLayout(); self.btn_backup = ConvexButton("UPLOAD", color=CP_CYAN, svg_data=SVGS["UPLOAD"])
        self.btn_backup.clicked.connect(self._do_backup); btn_row.addWidget(self.btn_backup); new_lay.addLayout(btn_row); layout.addWidget(grp_new)
        layout.addWidget(QLabel("CLOUD BACKUP HISTORY:")); self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True)
        layout.addWidget(self.scroll); QTimer.singleShot(10, self._fetch_and_render)

    def _fetch_and_render(self):
        try:
            result = self._convex_call("query", {"path": "functions:list", "args": {"scriptName": SCRIPT_NAME}})
            self._backups = result.get("value", [])
            import datetime; inner = QWidget(); vbox = QVBoxLayout(inner)
            for b in sorted(self._backups, key=lambda x: x["createdAt"], reverse=True):
                dt = datetime.datetime.fromtimestamp(b["createdAt"] / 1000).strftime("%Y-%m-%d %I:%M %p")
                row = QHBoxLayout(); btn = QPushButton(f"  {dt}  ->  {b['label']}")
                btn.setStyleSheet(f"text-align: left; padding: 8px; background: {CP_BG}; color: {CP_TEXT}; border: 1px solid {CP_DIM}; font-family: Consolas;")
                btn.clicked.connect(lambda checked, bid=b["id"]: self._select_restore(bid))
                
                diff_btn = QPushButton(); diff_btn.setFixedSize(32, 32); rd = QSvgRenderer(QByteArray(SVGS["DIFF"].replace('currentColor', CP_YELLOW).encode()))
                px = QPixmap(20, 20); px.fill(Qt.GlobalColor.transparent); pn = QPainter(px); rd.render(pn); pn.end()
                diff_btn.setIcon(QIcon(px)); diff_btn.clicked.connect(lambda checked, bid=b["id"], lbl=b["label"]: self._show_list_diff(bid, lbl))
                
                del_btn = QPushButton(); del_btn.setFixedSize(32, 32); rd_del = QSvgRenderer(QByteArray(SVGS["TRASH"].replace('currentColor', CP_RED).encode()))
                px_del = QPixmap(20, 20); px_del.fill(Qt.GlobalColor.transparent); pn_del = QPainter(px_del); rd_del.render(pn_del); pn_del.end()
                del_btn.setIcon(QIcon(px_del)); del_btn.clicked.connect(lambda checked, bid=b["id"]: self._do_remove(bid))
                
                row.addWidget(btn); row.addWidget(diff_btn); row.addWidget(del_btn); vbox.addLayout(row)
            vbox.addStretch(); self.scroll.setWidget(inner)
        except: pass

    def _do_backup(self):
        label = self.inp_label.text().strip()
        if not label: return
        self._convex_call("mutation", {"path": "functions:save", "args": {"scriptName": SCRIPT_NAME, "label": label, "data": self._config_data}})
        self.inp_label.clear(); self._fetch_and_render()

    def _do_remove(self, bid):
        if QMessageBox.question(self, "DELETE", "Delete this cloud backup permanently?") == QMessageBox.StandardButton.Yes:
            self._convex_call("mutation", {"path": "functions:remove", "args": {"id": bid}})
            self._fetch_and_render()
    def _show_list_diff(self, bid, label):
        remote = self._convex_call("query", {"path": "functions:get", "args": {"id": bid}}).get("value", {})
        DiffDialog(self._config_data, remote, title=f"DIFF // {label}", parent=self).exec()
    def _select_restore(self, bid): self.selected_id = bid; self.accept()

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

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
CUSTOM_SHAPES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "custom_shapes.json")

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
        self.multi_colors = []
        p = self.path()
        p.setFillRule(Qt.FillRule.WindingFill)
        self.setPath(p)

    def paint(self, painter, option, widget):
        if self.multi_colors:
            painter.setPen(self.pen())
            for path, color in self.multi_colors:
                if color == "transparent":
                    painter.setBrush(Qt.BrushStyle.NoBrush)
                else:
                    painter.setBrush(QBrush(QColor(color)))
                painter.drawPath(path)
        else:
            super().paint(painter, option, widget)

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
        self.center_marker = QGraphicsEllipseItem(-3, -3, 6, 6)
        self.center_marker.setPen(QPen(Qt.PenStyle.NoPen))
        self.center_marker.setBrush(QBrush(QColor(CP_YELLOW)))
        self.addItem(self.center_marker)
        self.center_marker.is_art_item = False

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
        self.app = parent # Store reference to SVGArtApp
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

    def scan_image_to_shaders(self, color_count=5, density=50, noise=0, auto_clr=False, shape_type="Cycle"):
        if not self.image_item:
            QMessageBox.warning(self.app, "No Image", "Load a background image first.")
            return
        
        if auto_clr: color_count = 256
        
        pixmap = self.image_item.pixmap()
        image = pixmap.toImage()
        w, h = image.width(), image.height()
        
        step_x = max(1, w // density)
        step_y = max(1, h // density)
        color_map = {} # hex -> list of (x, y)
        
        for y in range(0, h, step_y):
            for x in range(0, w, step_x):
                c = image.pixelColor(x, y)
                if c.alpha() < 50: continue
                # Quantization logic
                if auto_clr:
                    # 8-bit color binning (3R, 3G, 2B) -> 256 possible buckets
                    qr = (c.red() >> 5) << 5
                    qg = (c.green() >> 5) << 5
                    qb = (c.blue() >> 6) << 6
                    qc = QColor(qr, qg, qb)
                else:
                    q = 16
                    qc = QColor((c.red()//q)*q, (c.green()//q)*q, (c.blue()//q)*q)
                
                hex_c = qc.name()
                if hex_c not in color_map: color_map[hex_c] = []
                color_map[hex_c].append((x, y))
        
        if auto_clr:
            # In 8-bit mode, we take ALL found buckets (max 256) to ensure no pixels are missed
            sorted_colors = list(color_map.items())
        else:
            sorted_colors = sorted(color_map.items(), key=lambda x: len(x[1]), reverse=True)[:color_count]
        
        import random
        batch = []
        img_pos = self.image_item.pos()
        custom_names = list(self.custom_shapes.keys())
        
        for i, (hex_c, pts) in enumerate(sorted_colors):
            # SHAPE SELECTION LOGIC
            if shape_type == "Cycle":
                stype = i % 3 # Only Rect, Circle, Triangle
            elif shape_type == "Rect": stype = 0
            elif shape_type == "Circle": stype = 1
            elif shape_type == "Triangle": stype = 2
            elif shape_type == "All Customs":
                stype = (3 + (i % len(custom_names))) if custom_names else (i % 3)
            elif shape_type in custom_names:
                stype = 3 + custom_names.index(shape_type)
            else:
                stype = i % 3

            size = step_x * 0.8
            
            for px, py in pts:
                nx = px + random.uniform(-noise, noise)
                ny = py + random.uniform(-noise, noise)
                pos = img_pos + QPointF(nx, ny)
                
                item = None
                if stype == 0: item = SymRect(0, 0, size, size)
                elif stype == 1: item = SymEllipse(0, 0, size, size)
                elif stype == 2:
                    path = QPainterPath(); path.moveTo(size/2, 0); path.lineTo(0, size); path.lineTo(size, size); path.closeSubpath()
                    item = SymPath(path)
                else:
                    cidx = stype - 3
                    if 0 <= cidx < len(custom_names):
                        cname = custom_names[cidx]
                        path, multi = self._scale_custom_path(self.custom_shapes[cname], QPointF(size, size))
                        item = SymPath(path); item.multi_colors = multi
                    else: item = SymRect(0, 0, size, size) # Final fallback
                
                item.setPos(pos); item.setPen(QPen(Qt.PenStyle.NoPen))
                if not getattr(item, 'multi_colors', None):
                    item.setBrush(QBrush(QColor(hex_c)))
                item.is_art_item = True; item._shader_group = hex_c
                self.scene().addItem(item); batch.append(item)
        
        if batch:
            self.save_to_undo(batch, "add_batch")
            self.app.statusBar().showMessage(f"Generated {len(batch)} shader items across {len(sorted_colors)} colors.")

    def remove_background_image(self):
        if self.image_item:
            self.scene().removeItem(self.image_item)
            self.image_item = None
            self.image_path = ""
            self.app.statusBar().showMessage("Background image removed.")

    def apply_zoom(self, factor, target="Both"):
        if target == "Image" and self.image_item:
            self.image_item.setScale(self.image_item.scale() * factor)
        elif target == "SVG":
            for item in self.scene().items():
                if getattr(item, 'is_art_item', False):
                    item.setScale(item.scale() * factor)
        else:
            self.scale(factor, factor)
        if self.app: self.app.sync_zoom_ui()

    def set_absolute_zoom(self, scale, target="Both"):
        if target == "Image" and self.image_item:
            self.image_item.setScale(scale)
        elif target == "SVG":
            for item in self.scene().items():
                if getattr(item, 'is_art_item', False):
                    item.setScale(scale)
        else:
            self.resetTransform()
            self.scale(scale, scale)

    def get_target_scale(self, target="Both"):
        if target == "Image" and self.image_item:
            return self.image_item.scale()
        elif target == "SVG":
            # Return scale of first art item found, or 1.0
            for item in self.scene().items():
                if getattr(item, 'is_art_item', False): return item.scale()
            return 1.0
        else:
            return self.transform().m11()

    def wheelEvent(self, event):
        step = 5.0
        if self.app and hasattr(self.app, 'zoom_step_spin'):
            step = self.app.zoom_step_spin.value()
        
        factor = (1.0 + step/100.0) if event.angleDelta().y() > 0 else (1.0 / (1.0 + step/100.0))
        
        if self.tool == "move_image" and self.image_item:
            self.image_item.setScale(self.image_item.scale() * factor)
            event.accept()
        elif self.tool == "move_svg":
            for item in self.scene().items():
                if getattr(item, 'is_art_item', False):
                    item.setScale(item.scale() * factor)
            event.accept()
        elif self.tool == "move_all":
            if self.image_item:
                self.image_item.setScale(self.image_item.scale() * factor)
            for item in self.scene().items():
                if getattr(item, 'is_art_item', False):
                    item.setScale(item.scale() * factor)
            event.accept()
        else:
            self.scale(factor, factor)
        if self.app: self.app.sync_zoom_ui()

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
            elif self.tool in ["move_image", "move_svg", "move_sym", "move_all"]: self.drawing = True
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
                    path, multi = self._scale_custom_path(self.current_item._custom_base, local_pos)
                    self.current_item.setPath(path)
                    self.current_item.multi_colors = multi
                    self.update_clones(self.current_item)
            if self.tool == "eraser": self.erase_at(scene_pos)
            elif self.tool == "move_image" and self.image_item:
                delta = scene_pos - self.start_point; self.image_item.setPos(self.image_item.pos() + delta); self.start_point = scene_pos
            elif self.tool == "move_svg":
                delta = scene_pos - self.start_point
                for item in self.scene().items():
                    if getattr(item, 'is_art_item', False): item.setPos(item.pos() + delta)
                self.start_point = scene_pos
            elif self.tool == "move_all":
                delta = scene_pos - self.start_point
                if self.image_item: self.image_item.setPos(self.image_item.pos() + delta)
                for item in self.scene().items():
                    if getattr(item, 'is_art_item', False): item.setPos(item.pos() + delta)
                self.start_point = scene_pos
            elif self.tool == "move_sym":
                delta = scene_pos - self.start_point; self.sym_center += delta; self.start_point = scene_pos
                self.scene().center_marker.setPos(self.sym_center)
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
        mc = int(self.mirror_count)
        if self.symmetry_mode == "Radial":
            for i in range(1, mc):
                clone = self.clone_item(item)
                if not clone: continue
                clone.clone_type = "radial"
                angle = i * (360 / mc); tr = QTransform().translate(cx, cy).rotate(angle).translate(-cx, -cy)
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
        if isinstance(item, QGraphicsPathItem):
            clone = SymPath(item.path())
            if hasattr(item, 'multi_colors'): clone.multi_colors = item.multi_colors
        elif isinstance(item, QGraphicsRectItem): clone = SymRect(item.rect())
        elif isinstance(item, QGraphicsEllipseItem): clone = SymEllipse(item.rect())
        elif isinstance(item, QGraphicsLineItem): clone = SymLine(item.line())
        else: return None
        clone.setPen(item.pen()); clone.setBrush(item.brush()); clone.is_art_item = True
        if item.graphicsEffect():
            blur = QGraphicsBlurEffect(); blur.setBlurRadius(self.pen_width * 1.5); clone.setGraphicsEffect(blur)
        return clone

    def update_clones(self, item):
        cx, cy = self.sym_center.x(), self.sym_center.y()
        for i, clone in enumerate(item.symmetry_clones):
            if isinstance(item, QGraphicsPathItem):
                clone.setPath(item.path())
                if hasattr(item, 'multi_colors'): clone.multi_colors = item.multi_colors
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
        w, h = local_pos.x() or 1, local_pos.y() or 1
        full_path = QPainterPath()
        full_path.setFillRule(Qt.FillRule.WindingFill)
        current_path = QPainterPath()
        current_path.setFillRule(Qt.FillRule.WindingFill)
        current_color = None
        multi_colors = []
        for cmd, *args in points:
            if cmd == "COLOR":
                if not current_path.isEmpty():
                    multi_colors.append((current_path, current_color or "#00F0FF"))
                    current_path = QPainterPath()
                    current_path.setFillRule(Qt.FillRule.WindingFill)
                current_color = args[0]
                continue
            if cmd == "FILLRULE":
                fr = Qt.FillRule.OddEvenFill if args[0] == "evenodd" else Qt.FillRule.WindingFill
                full_path.setFillRule(fr)
                current_path.setFillRule(fr)
                continue
            
            # Ensure we only process coordinate pairs
            try:
                scaled = [QPointF(a[0] * w, a[1] * h) for a in args]
            except (TypeError, IndexError):
                continue

            if cmd == "M": 
                current_path.moveTo(scaled[0]); full_path.moveTo(scaled[0])
            elif cmd == "L": 
                current_path.lineTo(scaled[0]); full_path.lineTo(scaled[0])
            elif cmd == "Q": 
                current_path.quadTo(scaled[0], scaled[1]); full_path.quadTo(scaled[0], scaled[1])
            elif cmd == "C": 
                current_path.cubicTo(scaled[0], scaled[1], scaled[2]); full_path.cubicTo(scaled[0], scaled[1], scaled[2])
            elif cmd == "Z": 
                current_path.closeSubpath(); full_path.closeSubpath()
        if not current_path.isEmpty() and current_color:
            multi_colors.append((current_path, current_color))
        return full_path, multi_colors

    def _add_path_to_commands(self, path, item, bounds, w, h, commands):
        current_c = []
        for i in range(path.elementCount()):
            el = path.elementAt(i)
            sp = item.mapToScene(QPointF(el.x, el.y))
            nx, ny = (sp.x() - bounds.x()) / w, (sp.y() - bounds.y()) / h
            if el.type == QPainterPath.ElementType.MoveToElement:
                commands.append(["M", [nx, ny]])
            elif el.type == QPainterPath.ElementType.LineToElement:
                commands.append(["L", [nx, ny]])
            elif el.type == QPainterPath.ElementType.CurveToElement:
                current_c = [[nx, ny]]
            elif el.type == QPainterPath.ElementType.CurveToDataElement:
                current_c.append([nx, ny])
                if len(current_c) == 3:
                    commands.append(["C", current_c[0], current_c[1], current_c[2]])
                    current_c = []

    def collect_art_as_shape(self):
        """Collect current visible art items and return normalized commands."""
        items = [i for i in self.scene().items() if getattr(i, 'is_art_item', False) and i.isVisible()]
        if not items: return None
        
        bounds = QRectF()
        for item in items: bounds = bounds.united(item.mapToScene(item.boundingRect()).boundingRect())
        if bounds.isEmpty(): return None
        
        return self.collect_from_items(items, bounds)

    def collect_from_items(self, items, bounds):
        """Standardized processor to turn QGraphicsItems into normalized shape commands."""
        w, h = bounds.width() or 1, bounds.height() or 1
        commands = []
        items.sort(key=lambda x: x.zValue())
        
        for item in items:
            if isinstance(item, QGraphicsPathItem):
                if hasattr(item, 'multi_colors') and item.multi_colors:
                    for path, color in item.multi_colors:
                        commands.append(["COLOR", color])
                        if path.fillRule() == Qt.FillRule.OddEvenFill: commands.append(["FILLRULE", "evenodd"])
                        self._add_path_to_commands(path, item, bounds, w, h, commands)
                else:
                    if item.brush().style() != Qt.BrushStyle.NoBrush:
                        commands.append(["COLOR", item.brush().color().name()])
                    if item.path().fillRule() == Qt.FillRule.OddEvenFill:
                        commands.append(["FILLRULE", "evenodd"])
                    self._add_path_to_commands(item.path(), item, bounds, w, h, commands)
            elif isinstance(item, QGraphicsRectItem):
                commands.append(["COLOR", item.brush().color().name()])
                r = item.mapRectToScene(item.rect())
                pts = [[(r.left()-bounds.x())/w, (r.top()-bounds.y())/h], 
                       [(r.right()-bounds.x())/w, (r.top()-bounds.y())/h],
                       [(r.right()-bounds.x())/w, (r.bottom()-bounds.y())/h],
                       [(r.left()-bounds.x())/w, (r.bottom()-bounds.y())/h]]
                commands.append(["M", pts[0]])
                for p in pts[1:]: commands.append(["L", p])
                commands.append(["Z"])
            elif isinstance(item, QGraphicsEllipseItem):
                commands.append(["COLOR", item.brush().color().name()])
                r = item.mapRectToScene(item.rect())
                cx, cy = (r.center().x()-bounds.x())/w, (r.center().y()-bounds.y())/h
                rx, ry = r.width()/2/w, r.height()/2/h
                k = 0.5523
                commands += [["M",[cx,cy-ry]],["C",[cx+k*rx,cy-ry],[cx+rx,cy-k*rx],[cx+rx,cy]],
                              ["C",[cx+rx,cy+k*ry],[cx+k*rx,cy+ry],[cx,cy+ry]],
                              ["C",[cx-k*rx,cy+ry],[cx-rx,cy+k*ry],[cx-rx,cy]],
                              ["C",[cx-rx,cy-k*ry],[cx-k*rx,cy-ry],[cx,cy-ry]],["Z"]]
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
            self.pen_color = item.pen().color()
            if self.app: self.app.update_color_ui(self.pen_color)

    def undo(self):
        if not self.undo_stack: return
        a, i = self.undo_stack.pop()
        if a == "add":
            self.scene().removeItem(i); [self.scene().removeItem(c) for c in getattr(i, 'symmetry_clones', [])]
        elif a == "add_batch":
            for item in i: self.scene().removeItem(item)
        elif a == "remove":
            self.scene().addItem(i); [self.scene().addItem(c) for c in getattr(i, 'symmetry_clones', [])]
        elif a == "fill":
            old = i[2]; i.setBrush(old); [c.setBrush(old) for c in getattr(i, 'symmetry_clones', [])]
        self.redo_stack.append((a, i))

    def redo(self):
        if not self.redo_stack: return
        a, i = self.redo_stack.pop()
        if a == "add":
            self.scene().addItem(i); [self.scene().addItem(c) for c in getattr(i, 'symmetry_clones', [])]
        elif a == "add_batch":
            for item in i: self.scene().addItem(item)
        elif a == "remove":
            self.scene().removeItem(i); [self.scene().removeItem(c) for c in getattr(i, 'symmetry_clones', [])]
        elif a == "fill":
            # Item is (item, new_color, old_brush)
            # Actually apply_fill doesn't save new_color, it uses self.pen_color at the time.
            # Simple redo for fill:
            pass 
        self.undo_stack.append((a, i))

class ShapePickerDialog(QDialog):
    def __init__(self, custom_shapes, pixmap_cache, on_delete, parent=None):
        super().__init__(parent)
        self.app = parent
        self.setWindowTitle("Custom Shapes"); self.setModal(True)
        self.setStyleSheet(f"background-color: {CP_BG}; color: {CP_TEXT}; font-family: Consolas;")
        self.selected = None; self.custom_shapes = custom_shapes
        self.pixmap_cache = pixmap_cache; self.on_delete = on_delete
        self.columns = getattr(self.app, 'library_columns', 4)
        
        self.layout_ = QVBoxLayout(self)
        
        # Header: Search and Column Controls
        header = QHBoxLayout()
        
        header.addWidget(QLabel("SEARCH:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Filter shapes...")
        self.search_edit.setStyleSheet(f"background: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 5px;")
        self.search_edit.textChanged.connect(self._build_grid)
        header.addWidget(self.search_edit, stretch=1)
        
        header.addSpacing(20)
        header.addWidget(QLabel("COLS:"))
        self.col_spin = QSpinBox()
        self.col_spin.setRange(1, 10); self.col_spin.setValue(self.columns)
        self.col_spin.setStyleSheet(f"background: {CP_PANEL}; color: {CP_YELLOW}; border: 1px solid {CP_DIM}; padding: 5px; min-width: 50px;")
        self.col_spin.valueChanged.connect(self._update_cols)
        header.addWidget(self.col_spin)
        
        self.layout_.addLayout(header)
        
        # Scroll Area for the Grid
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet(f"QScrollArea {{ border: 1px solid {CP_DIM}; background: {CP_BG}; }}")
        self.layout_.addWidget(self.scroll)
        
        self._build_grid()

    def _update_cols(self, val):
        self.columns = val
        if self.app:
            self.app.library_columns = val
            self.app.save_settings()
        self._build_grid()

    def _build_grid(self):
        from PyQt6.QtWidgets import QGridLayout
        
        # Calculate dynamic width based on columns
        CELL_W = 120 # SIZE (100) + cell margins/border
        SPACING = 15
        MARGINS = 40 # Total side margins + scrollbar allowance
        target_w = (self.columns * CELL_W) + ((self.columns - 1) * SPACING) + MARGINS
        self.setFixedWidth(max(400, min(1400, target_w)))
        self.setMinimumHeight(500)

        # Clear existing container
        if self.scroll.widget():
            self.scroll.widget().deleteLater()

        search_text = self.search_edit.text().lower().strip()
        filtered_shapes = {n: c for n, c in self.custom_shapes.items() if search_text in n.lower()}

        if not filtered_shapes:
            container = QWidget(); vbox = QVBoxLayout(container)
            msg = "NO MATCHES FOUND" if self.custom_shapes else "NO CUSTOM SHAPES FOUND"
            lbl = QLabel(msg); lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(f"color: {CP_SUBTEXT}; font-size: 12pt; font-weight: bold; margin: 40px;")
            vbox.addWidget(lbl); self.scroll.setWidget(container)
            return

        container = QWidget(); gl = QGridLayout(container); gl.setSpacing(15); gl.setContentsMargins(10,10,10,10)
        SIZE, LABEL_H = 100, 44
        
        for i, (name, cmds) in enumerate(filtered_shapes.items()):
            cell = QWidget(); cell.setFixedSize(SIZE + 10, SIZE + LABEL_H + 10)
            cell.setStyleSheet(f"background: {CP_PANEL}; border: 1px solid {CP_DIM};")
            vl = QVBoxLayout(cell); vl.setContentsMargins(4, 4, 4, 4); vl.setSpacing(2)
            
            lbl = QLabel(); lbl.setFixedSize(SIZE, SIZE)
            lbl.setPixmap(self.pixmap_cache.get(name) or self.build_pixmap(cmds, SIZE, SIZE))
            lbl.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            lbl.mousePressEvent = lambda e, n=name: self._pick(n)
            vl.addWidget(lbl)
            
            nl = QLabel(name.upper()); nl.setStyleSheet(f"color: {CP_ORANGE}; font-size: 7pt; font-weight: bold; border: none;")
            nl.setAlignment(Qt.AlignmentFlag.AlignCenter); nl.setFixedHeight(18)
            vl.addWidget(nl)
            
            ctrls = QHBoxLayout(); ctrls.setSpacing(10); ctrls.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            copy_btn = QPushButton(); copy_btn.setFixedSize(22, 22); copy_btn.setToolTip("Copy SVG Code")
            rd = QSvgRenderer(QByteArray(SVGS["COPY"].replace('currentColor', CP_CYAN).encode()))
            px = QPixmap(18, 18); px.fill(Qt.GlobalColor.transparent); pn = QPainter(px); rd.render(pn); pn.end()
            copy_btn.setIcon(QIcon(px)); copy_btn.setStyleSheet("background: transparent; border: none;")
            copy_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            copy_btn.clicked.connect(lambda checked, n=name: self._copy_shape(n))

            edit_btn = QPushButton(); edit_btn.setFixedSize(22, 22); edit_btn.setToolTip("Rename Shape")
            rd_edit = QSvgRenderer(QByteArray(SVGS["EDIT"].replace('currentColor', CP_YELLOW).encode()))
            px_edit = QPixmap(18, 18); px_edit.fill(Qt.GlobalColor.transparent); pn_edit = QPainter(px_edit); rd_edit.render(pn_edit); pn_edit.end()
            edit_btn.setIcon(QIcon(px_edit)); edit_btn.setStyleSheet("background: transparent; border: none;")
            edit_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            edit_btn.clicked.connect(lambda checked, n=name: self._rename_shape(n))
            
            del_btn = QPushButton(); del_btn.setFixedSize(22, 22); del_btn.setToolTip("Remove Shape")
            rd_del = QSvgRenderer(QByteArray(SVGS["TRASH"].replace('currentColor', CP_RED).encode()))
            px_del = QPixmap(18, 18); px_del.fill(Qt.GlobalColor.transparent); pn_del = QPainter(px_del); rd_del.render(pn_del); pn_del.end()
            del_btn.setIcon(QIcon(px_del)); del_btn.setStyleSheet("background: transparent; border: none;")
            del_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            del_btn.clicked.connect(lambda checked, n=name: self._delete(n))
            
            ctrls.addWidget(copy_btn); ctrls.addWidget(edit_btn); ctrls.addWidget(del_btn)
            vl.addLayout(ctrls)
            
            gl.addWidget(cell, i // self.columns, i % self.columns)
        
        gl.setRowStretch(gl.rowCount(), 1)
        gl.setColumnStretch(self.columns, 1)
        self.scroll.setWidget(container)

    def _rename_shape(self, old_name):
        new_name, ok = QInputDialog.getText(self, "Rename Shape", f"Enter new name for '{old_name}':", text=old_name)
        if ok and new_name.strip() and new_name.strip() != old_name:
            n = new_name.strip()
            self.custom_shapes[n] = self.custom_shapes.pop(old_name)
            if old_name in self.pixmap_cache:
                self.pixmap_cache[n] = self.pixmap_cache.pop(old_name)
            self.on_delete() # This triggers the save_custom_shapes callback
            self._build_grid()

    def _copy_shape(self, name):
        cmds = self.custom_shapes.get(name, [])
        if not cmds: return
        
        svg_output = f'<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">\n'
        current_path = ""; color = "#00F0FF"
        
        def flush_path():
            nonlocal current_path
            if current_path:
                fill = "none" if color == "transparent" else color
                return f'  <path fill="{fill}" d="{current_path.strip()}" />\n'
            return ""

        for cmd, *args in cmds:
            if cmd == "COLOR":
                svg_output += flush_path()
                current_path = ""; color = args[0]; continue
            if cmd == "FILLRULE": continue
            
            pts = args
            if cmd == "M": current_path += f"M{pts[0][0]*100},{pts[0][1]*100} "
            elif cmd == "L": current_path += f"L{pts[0][0]*100},{pts[0][1]*100} "
            elif cmd == "Q": current_path += f"Q{pts[0][0]*100},{pts[0][1]*100} {pts[1][0]*100},{pts[1][1]*100} "
            elif cmd == "C": current_path += f"C{pts[0][0]*100},{pts[0][1]*100} {pts[1][0]*100},{pts[1][1]*100} {pts[2][0]*100},{pts[2][1]*100} "
            elif cmd == "Z": current_path += "Z "
            
        svg_output += flush_path()
        svg_output += "</svg>"
        QApplication.clipboard().setText(svg_output)

    @staticmethod
    def build_pixmap(cmds, w, h):
        px = QPixmap(w, h); px.fill(QColor(CP_PANEL))
        painter = QPainter(px); painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        margin = min(w, h) * 0.15
        pw, ph = w - 2 * margin, h - 2 * margin
        current_color = CP_CYAN
        path = QPainterPath()
        def flush():
            if not path.isEmpty():
                painter.setPen(QPen(QColor(current_color if current_color != "transparent" else "#00000000"), 0.5))
                if current_color == "transparent":
                    painter.setBrush(Qt.BrushStyle.NoBrush)
                else:
                    painter.setBrush(QBrush(QColor(current_color)))
                painter.drawPath(path)
        for cmd, *args in cmds:
            if cmd == "COLOR":
                flush(); path = QPainterPath(); current_color = args[0]; continue
            if cmd == "FILLRULE":
                # Optionally set fill rule if path exists, or just skip
                fr = Qt.FillRule.OddEvenFill if args[0] == "evenodd" else Qt.FillRule.WindingFill
                path.setFillRule(fr)
                continue
            pts = [QPointF(a[0] * pw + margin, a[1] * ph + margin) for a in args]
            if cmd == "M": path.moveTo(pts[0])
            elif cmd == "L": path.lineTo(pts[0])
            elif cmd == "Q": path.quadTo(pts[0], pts[1])
            elif cmd == "C": path.cubicTo(pts[0], pts[1], pts[2])
            elif cmd == "Z": path.closeSubpath()
        flush(); painter.end()
        return px

    def _pick(self, name): self.selected = name; self.accept()

    def _delete(self, name):
        del self.custom_shapes[name]; self.pixmap_cache.pop(name, None); self.on_delete()
        self._build_grid(); self.adjustSize()


class SVGInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("IMPORT SVG SHAPE")
        self.resize(600, 600)
        self.setStyleSheet(f"background-color: {CP_BG}; color: {CP_TEXT}; font-family: 'Consolas';")
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("SHAPE NAME:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter shape name...")
        self.name_edit.setStyleSheet(f"background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; color: {CP_CYAN}; padding: 8px;")
        layout.addWidget(self.name_edit)

        layout.addWidget(QLabel("SVG CODE / PATH DATA (d=...):"))
        self.text_edit = QPlainTextEdit()
        self.text_edit.setStyleSheet(f"background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; color: {CP_TEXT}; font-size: 9pt;")
        self.text_edit.setPlaceholderText("<path d=\"M 10 10 L 90 90 ...\" />\nor just the path data: M 10 10 L 90 90 ...")
        layout.addWidget(self.text_edit)

        layout.addWidget(QLabel("EXTRACTED COLORS (CLICK TO REPLACE):"))
        self.color_scroll = QScrollArea()
        self.color_scroll.setWidgetResizable(True)
        self.color_scroll.setFixedHeight(70)
        self.color_scroll.setStyleSheet(f"QScrollArea {{ border: 1px solid {CP_DIM}; background: {CP_PANEL}; }}")
        self.color_widget = QWidget()
        self.color_layout = QHBoxLayout(self.color_widget)
        self.color_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.color_scroll.setWidget(self.color_widget)
        layout.addWidget(self.color_scroll)

        self.color_timer = QTimer()
        self.color_timer.setSingleShot(True)
        self.color_timer.timeout.connect(self.update_color_panel)
        self.text_edit.textChanged.connect(lambda: self.color_timer.start(500))

        btns = QHBoxLayout()
        self.btn_ok = QPushButton("IMPORT")
        self.btn_ok.setStyleSheet(f"background-color: {CP_GREEN}; color: black; font-weight: bold; padding: 8px;")
        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel = QPushButton("CANCEL")
        self.btn_cancel.setStyleSheet(f"background-color: {CP_DIM}; color: white; padding: 8px;")
        self.btn_cancel.clicked.connect(self.reject)
        btns.addWidget(self.btn_ok); btns.addWidget(self.btn_cancel)
        layout.addLayout(btns)
        
        self.update_color_panel()

    def update_color_panel(self):
        while self.color_layout.count():
            item = self.color_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        
        svg = self.text_edit.toPlainText()
        colors = sorted(list(set(re.findall(r'#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3}', svg))), key=len, reverse=True)
        
        if not colors:
            lbl = QLabel("No hex colors found")
            lbl.setStyleSheet(f"color: {CP_SUBTEXT}; font-style: italic;")
            self.color_layout.addWidget(lbl)
        else:
            for c in colors:
                btn = QPushButton()
                btn.setFixedSize(40, 40)
                btn.setToolTip(f"Replace {c}")
                btn.setStyleSheet(f"background-color: {c}; border: 2px solid {CP_DIM}; border-radius: 4px;")
                btn.clicked.connect(partial(self.pick_replacement_color, c))
                self.color_layout.addWidget(btn)
        self.color_layout.addStretch()

    def pick_replacement_color(self, old_color):
        curr = QColor(old_color) if old_color.startswith('#') else QColor(Qt.GlobalColor.black)
        c = QColorDialog.getColor(curr, self, f"Replace {old_color}")
        if c.isValid():
            new_color = c.name().upper()
            svg = self.text_edit.toPlainText()
            pattern = re.compile(re.escape(old_color), re.IGNORECASE)
            new_svg = pattern.sub(new_color, svg)
            self.text_edit.setPlainText(new_svg)
            self.update_color_panel()

class SVGArtApp(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle("NEURAL ART V1.6.2 - SYNCED"); self.resize(1400, 900)
        self.library_columns = 4; self.last_dir = ""
        self.setup_ui(); self.apply_theme(); self.toggle_sharp(); self.load_settings(); self.load_custom_shapes()

    def setup_ui(self):
        self.central_widget = QWidget(); self.setCentralWidget(self.central_widget); self.main_layout = QVBoxLayout(self.central_widget)
        self.scene = ArtScene(); self.view = ArtView(self.scene, self); self.main_layout.addWidget(self.view)
        
        self.tb_main = QToolBar("Main"); self.tb_main.setObjectName("MainToolbar"); self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.tb_main)
        self.add_tool_action(self.tb_main, "BRUSH", "brush", CP_CYAN, SVGS["BRUSH"]); self.brush_combo = QComboBox(); self.brush_combo.addItems(["Marker", "Airbrush", "Multiline", "Highlighter"]); self.brush_combo.currentTextChanged.connect(self.set_brush_type); self.tb_main.addWidget(self.brush_combo)
        self.tb_main.addWidget(QLabel(" LINES: ")); self.multi_slider = QSpinBox(); self.multi_slider.setRange(1, 100); self.multi_slider.setValue(3); self.multi_slider.valueChanged.connect(self.set_multi_count); self.tb_main.addWidget(self.multi_slider)
        self.add_tool_action(self.tb_main, "POLY", "poly", CP_GREEN, SVGS["POLYGON"]); self.add_tool_action(self.tb_main, "CURVE", "curve", CP_GREEN, SVGS["CURVE"]); self.add_tool_action(self.tb_main, "ERASE", "eraser", CP_RED, SVGS["ERASER"]); self.add_tool_action(self.tb_main, "FILL", "fill", CP_YELLOW, SVGS["PAINT_BUCKET"]); self.add_tool_action(self.tb_main, "PICK", "picker", CP_CYAN, SVGS["EYEDROPPER"])
        self.tb_shapes = QToolBar("Shapes"); self.tb_shapes.setObjectName("ShapesToolbar"); self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.tb_shapes)
        self.add_tool_action(self.tb_shapes, "RECT", "rect", CP_ORANGE, SVGS["RECTANGLE"]); self.add_tool_action(self.tb_shapes, "CIRC", "ellipse", CP_ORANGE, SVGS["CIRCLE"]); self.add_tool_action(self.tb_shapes, "TRI", "triangle", CP_ORANGE, SVGS["TRIANGLE"])

        self.tb_move = QToolBar("Move"); self.tb_move.setObjectName("MoveToolbar"); self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.tb_move)
        self.tb_move.addWidget(QLabel(" MOVE MODE: ")); self.move_mode_combo = QComboBox()
        self.move_mode_combo.addItems(["None", "Image", "SVG", "Both", "Symmetry Center"])
        self.move_mode_combo.currentTextChanged.connect(self.update_move_mode)
        self.tb_move.addWidget(self.move_mode_combo)

        self.tb_library = QToolBar("Library"); self.tb_library.setObjectName("LibraryToolbar"); self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.tb_library)
        btn_list_shapes = ConvexButton(parent=self, color=CP_CYAN, svg_data=SVGS["SHAPE_LIB"])
        btn_list_shapes.setToolTip("Browse custom shapes"); btn_list_shapes.clicked.connect(self.show_shape_picker); self.tb_library.addWidget(btn_list_shapes)
        btn_import_svg = ConvexButton(parent=self, color=CP_CYAN, svg_data=SVGS["IMPORT_SVG"])
        btn_import_svg.setToolTip("Import shape by SVG code"); btn_import_svg.clicked.connect(self.add_svg_shape); self.tb_library.addWidget(btn_import_svg)
        btn_add_shape = ConvexButton(parent=self, color=CP_GREEN, svg_data=SVGS["ADD_SHAPE"])
        btn_add_shape.setToolTip("Save current art as custom shape"); btn_add_shape.clicked.connect(self.add_custom_shape); self.tb_library.addWidget(btn_add_shape)
        
        self.tb_zoom = QToolBar("Zoom"); self.tb_zoom.setObjectName("ZoomToolbar"); self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.tb_zoom)
        btn_zoom_in = QPushButton("ZOOM IN"); btn_zoom_in.clicked.connect(self.zoom_in); self.tb_zoom.addWidget(btn_zoom_in)
        btn_zoom_out = QPushButton("ZOOM OUT"); btn_zoom_out.clicked.connect(self.zoom_out); self.tb_zoom.addWidget(btn_zoom_out)
        self.tb_zoom.addWidget(QLabel(" TARGET: ")); self.zoom_target_combo = QComboBox(); self.zoom_target_combo.addItems(["Both", "Image", "SVG"]); self.zoom_target_combo.currentTextChanged.connect(self.sync_zoom_ui); self.tb_zoom.addWidget(self.zoom_target_combo)
        self.tb_zoom.addWidget(QLabel(" VAL%: ")); self.zoom_spin = QSpinBox(); self.zoom_spin.setRange(1, 5000); self.zoom_spin.setValue(100); self.zoom_spin.setSuffix("%"); self.zoom_spin.valueChanged.connect(self.zoom_val_changed); self.tb_zoom.addWidget(self.zoom_spin)
        self.tb_zoom.addWidget(QLabel(" STEP%: ")); self.zoom_step_spin = QSpinBox(); self.zoom_step_spin.setRange(1, 100); self.zoom_step_spin.setValue(5); self.zoom_step_spin.setSuffix("%"); self.tb_zoom.addWidget(self.zoom_step_spin)

        self.tb_props = QToolBar("Properties"); self.tb_props.setObjectName("PropsToolbar"); self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.tb_props)
        self.btn_color = QPushButton("COLOR"); self.btn_color.clicked.connect(self.choose_color); self.tb_props.addWidget(self.btn_color)
        self.tb_props.addWidget(QLabel(" THICK: ")); self.thickness_slider = QSpinBox(); self.thickness_slider.setRange(1, 100); self.thickness_slider.setValue(3); self.thickness_slider.valueChanged.connect(self.change_thickness); self.tb_props.addWidget(self.thickness_slider)
        self.btn_sharp = QPushButton("SHARP"); self.btn_sharp.setCheckable(True); self.btn_sharp.setChecked(True); self.btn_sharp.clicked.connect(self.toggle_sharp); self.tb_props.addWidget(self.btn_sharp)
        
        self.tb_grid = QToolBar("Grid"); self.tb_grid.setObjectName("GridToolbar"); self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.tb_grid)
        self.btn_show_grid = QPushButton("GRID"); self.btn_show_grid.setCheckable(True); self.btn_show_grid.clicked.connect(self.toggle_grid); self.tb_grid.addWidget(self.btn_show_grid)
        self.btn_snap_grid = QPushButton("SNAP"); self.btn_snap_grid.setCheckable(True); self.btn_snap_grid.clicked.connect(self.toggle_snap); self.tb_grid.addWidget(self.btn_snap_grid)
        self.tb_grid.addWidget(QLabel(" SIZE: ")); self.grid_size_spin = QSpinBox(); self.grid_size_spin.setRange(5, 200); self.grid_size_spin.setValue(20); self.grid_size_spin.valueChanged.connect(self.change_grid_size); self.tb_grid.addWidget(self.grid_size_spin)
        self.btn_canvas_bg = QPushButton("BG"); self.btn_canvas_bg.setToolTip("Change Canvas Background"); self.btn_canvas_bg.clicked.connect(self.choose_canvas_bg); self.tb_grid.addWidget(self.btn_canvas_bg)

        self.tb_shader = QToolBar("Shader"); self.tb_shader.setObjectName("ShaderToolbar"); self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.tb_shader)
        self.add_tool_action(self.tb_shader, "SCAN", "scan_img", CP_YELLOW, SVGS["SCAN"])
        btn_recolor = ConvexButton(parent=self, color=CP_CYAN, svg_data=SVGS["PALETTE"])
        btn_recolor.setToolTip("Manage Color Groups"); btn_recolor.clicked.connect(self.manage_shader_colors); self.tb_shader.addWidget(btn_recolor)
        self.tb_shader.addWidget(QLabel(" CLR: ")); self.chk_auto_clr = QCheckBox("AUTO"); self.chk_auto_clr.setToolTip("Auto-detect all colors (8-bit)"); self.tb_shader.addWidget(self.chk_auto_clr)
        self.shader_colors_spin = QSpinBox(); self.shader_colors_spin.setRange(1, 20); self.shader_colors_spin.setValue(5); self.tb_shader.addWidget(self.shader_colors_spin)
        self.tb_shader.addWidget(QLabel(" DEN: ")); self.shader_density_spin = QSpinBox(); self.shader_density_spin.setRange(10, 500); self.shader_density_spin.setValue(50); self.tb_shader.addWidget(self.shader_density_spin)
        self.tb_shader.addWidget(QLabel(" NSE: ")); self.shader_noise_spin = QSpinBox(); self.shader_noise_spin.setRange(0, 100); self.shader_noise_spin.setValue(0); self.tb_shader.addWidget(self.shader_noise_spin)
        self.tb_shader.addWidget(QLabel(" SHP: ")); self.shader_shape_combo = QComboBox(); self.update_shader_shape_list(); self.tb_shader.addWidget(self.shader_shape_combo)

        self.tb_sym = QToolBar("Symmetry"); self.tb_sym.setObjectName("SymmetryToolbar"); self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.tb_sym)

        self.tb_sym.addWidget(QLabel(" SYMMETRY ")); self.sym_combo = QComboBox(); self.sym_combo.addItems(["None", "Radial", "Reflect (H)", "Reflect (V)", "Reflect (B)"]); self.sym_combo.currentTextChanged.connect(self.set_symmetry_mode); self.tb_sym.addWidget(self.sym_combo)
        self.tb_sym.addWidget(QLabel(" MIRROR: ")); self.mirror_spin = QSpinBox(); self.mirror_spin.setRange(2, 100); self.mirror_spin.setValue(4); self.mirror_spin.valueChanged.connect(self.set_mirror_count); self.tb_sym.addWidget(self.mirror_spin)
        self.tb_sys = QToolBar("System"); self.tb_sys.setObjectName("SystemToolbar"); self.addToolBar(Qt.ToolBarArea.RightToolBarArea, self.tb_sys)
        
        btn_clean = ConvexButton(parent=self, color=CP_RED, svg_data=SVGS["TRASH"])
        btn_clean.setToolTip("Clear all art items"); btn_clean.clicked.connect(self.clear_art); self.tb_sys.addWidget(btn_clean)
        
        btn_undo = ConvexButton(parent=self, color=CP_YELLOW, svg_data=SVGS["UNDO"])
        btn_undo.setToolTip("Undo last action"); btn_undo.clicked.connect(self.undo); self.tb_sys.addWidget(btn_undo)
        
        btn_redo = ConvexButton(parent=self, color=CP_GREEN, svg_data=SVGS["REDO"])
        btn_redo.setToolTip("Redo last undone action"); btn_redo.clicked.connect(self.redo); self.tb_sys.addWidget(btn_redo)

        btn_recenter = ConvexButton(parent=self, color=CP_YELLOW, svg_data=SVGS["CENTER"])
        btn_recenter.setToolTip("Recenter view"); btn_recenter.clicked.connect(self.recenter_view); self.tb_sys.addWidget(btn_recenter)
        
        btn_img = ConvexButton(parent=self, color=CP_CYAN, svg_data=SVGS["IMAGE"])
        btn_img.setToolTip("Load background image"); btn_img.clicked.connect(self.load_image); self.tb_sys.addWidget(btn_img)
        
        self.btn_remove_img = ConvexButton(parent=self, color=CP_RED, svg_data=SVGS["REMOVE_IMAGE"])
        self.btn_remove_img.setToolTip("Remove background image"); self.btn_remove_img.clicked.connect(self.view.remove_background_image); self.tb_sys.addWidget(self.btn_remove_img)
        
        btn_save = ConvexButton(parent=self, color=CP_GREEN, svg_data=SVGS["SAVE_DISK"])
        btn_save.setToolTip("Export as SVG file"); btn_save.clicked.connect(self.save_svg); self.tb_sys.addWidget(btn_save)

        sync_btn = ConvexButton(parent=self, color=CP_CYAN, svg_data=SVGS["SYNC"])
        sync_btn.setToolTip("Cloud Sync Manager"); sync_btn.clicked.connect(self.open_cloud_sync); self.tb_sys.addWidget(sync_btn)
        
        btn_rst = ConvexButton(parent=self, color=CP_RED, svg_data=SVGS["RESTART"])
        btn_rst.setToolTip("Restart application"); btn_rst.clicked.connect(self.restart_app); self.tb_sys.addWidget(btn_rst)
        u_act = QAction("Undo", self); u_act.setShortcut(QKeySequence("Ctrl+Z")); u_act.triggered.connect(self.undo); self.addAction(u_act)
        r_act = QAction("Redo", self); r_act.setShortcut(QKeySequence("Ctrl+Y")); r_act.triggered.connect(self.redo); self.addAction(r_act)
        
        zi_act = QAction("Zoom In", self); zi_act.setShortcuts([QKeySequence("Ctrl++"), QKeySequence("Ctrl+=")]); zi_act.triggered.connect(self.zoom_in); self.addAction(zi_act)
        zo_act = QAction("Zoom Out", self); zo_act.setShortcut(QKeySequence("Ctrl+-")); zo_act.triggered.connect(self.zoom_out); self.addAction(zo_act)

    def add_tool_action(self, tb, text, tool_name, color, svg_data=None):
        if svg_data:
            btn = ConvexButton(parent=self, color=color, svg_data=svg_data)
            btn.setToolTip(text)
        else:
            btn = QPushButton(text)
            btn.setStyleSheet(f"color: {color}; font-weight: bold;")
        btn.clicked.connect(lambda: self.set_tool(tool_name)); tb.addWidget(btn)

    def manage_shader_colors(self):
        groups = {}
        for item in self.scene.items():
            if hasattr(item, '_shader_group'):
                g = item._shader_group
                if g not in groups: groups[g] = []
                groups[g].append(item)
        if not groups:
            QMessageBox.information(self, "No Groups", "Scan an image first to create color groups.")
            return
        dlg = QDialog(self); dlg.setWindowTitle("RECOLOR GROUPS"); layout = QVBoxLayout(dlg)
        dlg.setStyleSheet(f"background: {CP_BG}; border: 1px solid {CP_CYAN};")
        for hex_c, items in groups.items():
            row = QHBoxLayout(); btn = QPushButton(); btn.setFixedSize(60, 30)
            btn.setStyleSheet(f"background-color: {hex_c}; border: 2px solid white;")
            btn.clicked.connect(lambda checked, h=hex_c, itms=items, b=btn: self._recolor_group(h, itms, b))
            row.addWidget(btn); row.addWidget(QLabel(f"Group: {hex_c} ({len(items)} items)"))
            layout.addLayout(row)
        close = ConvexButton("CLOSE", color=CP_DIM, is_outlined=True); close.clicked.connect(dlg.accept); layout.addWidget(close); dlg.exec()

    def _recolor_group(self, old_hex, items, btn):
        c = QColorDialog.getColor(QColor(old_hex), self, "New Group Color")
        if c.isValid():
            new_hex = c.name().upper()
            for item in items:
                item.setBrush(QBrush(c))
                item._shader_group = new_hex
            btn.setStyleSheet(f"background-color: {new_hex}; border: 2px solid white;")

    def update_move_mode(self, mode):
        mapping = {
            "None": "brush", # Default back to brush when none is picked
            "Image": "move_image",
            "SVG": "move_svg",
            "Both": "move_all",
            "Symmetry Center": "move_sym"
        }
        tool = mapping.get(mode, "brush")
        # Update view tool but DON'T trigger a recursive set_tool call
        self.view.tool = tool
        self.view.current_item = None
        self.statusBar().showMessage(f"MOVE MODE: {mode}")

    def add_system_action(self, tb, text, func, color):
        btn = QPushButton(text); btn.setStyleSheet(f"color: {color}; font-weight: bold; border: 1px solid {color};"); btn.clicked.connect(func); tb.addWidget(btn)
    def set_tool(self, tool):
        if tool == "scan_img":
            self.view.scan_image_to_shaders(
                self.shader_colors_spin.value(), 
                self.shader_density_spin.value(), 
                self.shader_noise_spin.value(),
                auto_clr=self.chk_auto_clr.isChecked(),
                shape_type=self.shader_shape_combo.currentText()
            )
            return
        
        # Reset Move dropdown if a standard tool is picked
        if hasattr(self, 'move_mode_combo') and not tool.startswith("move_"):
            self.move_mode_combo.blockSignals(True)
            self.move_mode_combo.setCurrentText("None")
            self.move_mode_combo.blockSignals(False)

        self.view.tool = tool; self.view.current_item = None
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

    def choose_canvas_bg(self):
        c = QColorDialog.getColor(self.scene.backgroundBrush().color(), self, "CANVAS BACKGROUND")
        if c.isValid():
            self.scene.setBackgroundBrush(QColor(c))
            self.save_settings()

    def undo(self): self.view.undo()
    def redo(self): self.view.redo()
    def zoom_in(self): self.view.apply_zoom(1.25, self.zoom_target_combo.currentText())
    def zoom_out(self): self.view.apply_zoom(0.8, self.zoom_target_combo.currentText())

    def zoom_val_changed(self, val):
        # Prevent recursive calls by blocking signals temporarily
        self.zoom_spin.blockSignals(True)
        self.view.set_absolute_zoom(val / 100.0, self.zoom_target_combo.currentText())
        self.zoom_spin.blockSignals(False)

    def sync_zoom_ui(self):
        self.zoom_spin.blockSignals(True)
        scale = self.view.get_target_scale(self.zoom_target_combo.currentText())
        self.zoom_spin.setValue(int(scale * 100))
        self.zoom_spin.blockSignals(False)

    def recenter_view(self):
        self.view.resetTransform()
        self.view.centerOn(0, 0)
    def clear_art(self): [self.scene.removeItem(i) for i in self.scene.items() if getattr(i, 'is_art_item', False)]
    def load_image(self, path=None):
        if not path:
            path, _ = QFileDialog.getOpenFileName(self, "IMG", self.last_dir, "Images (*.png *.jpg *.jpeg *.bmp)")
            if path: self.last_dir = os.path.dirname(path)
        if path and os.path.exists(path):
            pix = QPixmap(path)
            if not pix.isNull():
                if self.view.image_item: self.scene.removeItem(self.view.image_item)
                self.view.image_item = QGraphicsPixmapItem(pix); self.view.image_item.setZValue(-1); self.view.image_item.is_art_item = False; self.view.image_path = path; self.scene.addItem(self.view.image_item)
    def save_svg(self):
        f, _ = QFileDialog.getSaveFileName(self, "SAVE SVG", os.path.join(self.last_dir, "art.svg"), "SVG files (*.svg)")
        if f:
            self.last_dir = os.path.dirname(f)
            hidden = []; r = QRectF()
            for i in self.scene.items():
                if not getattr(i, 'is_art_item', False): (i.hide(), hidden.append(i)) if i.isVisible() else None
                else: r = r.united(i.sceneBoundingRect())
            if r.isEmpty(): r = QRectF(0, 0, 800, 600)
            
            # Temporarily disable background for transparent export
            old_bg = self.scene.backgroundBrush()
            self.scene.setBackgroundBrush(QBrush(Qt.BrushStyle.NoBrush))
            
            g = QSvgGenerator(); g.setFileName(f); g.setSize(r.size().toSize()); g.setViewBox(r); painter = QPainter(g); self.scene.render(painter, r, r); painter.end()
            
            # Restore background
            self.scene.setBackgroundBrush(old_bg)
            [i.show() for i in hidden]
            
    def restart_app(self): self.save_settings(); os.execl(sys.executable, sys.executable, *sys.argv)

    def _convex_call(self, type, payload):
        try:
            req = urllib.request.Request(f"{CONVEX_URL}/api/{type}", data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req) as res: return json.loads(res.read().decode())
        except Exception as e: print(f"Cloud Error: {e}"); return {}

    def _fix_floats(self, obj):
        if isinstance(obj, dict): return {k: self._fix_floats(v) for k, v in obj.items()}
        if isinstance(obj, list): return [self._fix_floats(i) for i in obj]
        if isinstance(obj, float) and obj.is_integer(): return int(obj)
        return obj

    def open_cloud_sync(self):
        # Gather all data to sync
        self.save_settings()
        self.save_custom_shapes()
        config_data = {"custom_shapes": self.view.custom_shapes}
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f: config_data["settings"] = json.load(f)
        
        dlg = CloudSyncDialog(self._convex_call, config_data, self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.selected_id:
            res = self._convex_call("query", {"path": "functions:get", "args": {"id": dlg.selected_id}})
            data = res.get("value")
            if data:
                data = self._fix_floats(data)
                # Restore custom shapes
                if "custom_shapes" in data:
                    self.view.custom_shapes = data["custom_shapes"]
                    self.save_custom_shapes()
                    self._shape_pixmap_cache = {name: ShapePickerDialog.build_pixmap(cmds, 100, 100) for name, cmds in self.view.custom_shapes.items()}
                # Restore settings
                if "settings" in data:
                    with open(SETTINGS_FILE, 'w') as f: json.dump(data["settings"], f)
                    self.load_settings()
                QMessageBox.information(self, "RESTORE", "Cloud backup restored successfully.")

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
            self.update_shader_shape_list()
        except: pass

    def update_shader_shape_list(self):
        if not hasattr(self, 'shader_shape_combo'): return
        curr = self.shader_shape_combo.currentText()
        self.shader_shape_combo.clear()
        base = ["Cycle", "Rect", "Circle", "Triangle", "All Customs"]
        self.shader_shape_combo.addItems(base)
        
        # Add custom shapes sorted alphabetically
        if hasattr(self, 'view') and self.view.custom_shapes:
            customs = sorted(self.view.custom_shapes.keys())
            if customs:
                self.shader_shape_combo.insertSeparator(self.shader_shape_combo.count())
                self.shader_shape_combo.addItems(customs)
        
        idx = self.shader_shape_combo.findText(curr)
        if idx >= 0: self.shader_shape_combo.setCurrentIndex(idx)
        else: self.shader_shape_combo.setCurrentIndex(0)

    def add_custom_shape(self):
        cmds = self.view.collect_art_as_shape()
        if not cmds:
            QMessageBox.warning(self, "No Art", "Draw something first to save as a custom shape."); return
        name, ok = QInputDialog.getText(self, "Shape Name", "Enter shape name:")
        if ok and name.strip():
            self.save_named_shape(name.strip(), cmds)

    def save_named_shape(self, name, cmds):
        self.view.custom_shapes[name] = cmds
        self._shape_pixmap_cache[name] = ShapePickerDialog.build_pixmap(cmds, 100, 100)
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
            svg_code = dlg.text_edit.toPlainText().strip()
            name = dlg.name_edit.text().strip()
            if not (svg_code and name):
                if not name: QMessageBox.warning(self, "Missing Name", "Please enter a name.")
                return
                
            cmds = self.parse_svg_to_shape(svg_code)
            if not cmds:
                QMessageBox.warning(self, "Error", "Could not parse SVG code.")
                return

            # 1. Staging items in an invisible scene for perfect normalization parity with '+'
            staging_scene = QGraphicsScene()
            # Render at standard size (500x500) for high-fidelity processing
            path, multi = self.view._scale_custom_path(cmds, QPointF(500, 500))
            tmp = SymPath(path)
            tmp.multi_colors = multi
            tmp.setPen(self.view.get_pen())
            tmp.is_art_item = True # CRITICAL: Processor uses this flag
            staging_scene.addItem(tmp)
            
            # 2. Trace the staged item using the unified system processor
            final_cmds = self.view.collect_from_items([tmp], tmp.sceneBoundingRect())
            
            if final_cmds:
                self.save_named_shape(name, final_cmds)
                # Force refresh cache
                self._shape_pixmap_cache[name] = ShapePickerDialog.build_pixmap(final_cmds, 100, 100)
                self.set_tool(f"custom:{name}")
                self.statusBar().showMessage(f"SVG '{name}' processed ({len(final_cmds)} cmds). Ready to draw.")
            else:
                self.statusBar().showMessage("Error: Staging failed to capture shape data.")
                QMessageBox.warning(self, "Error", "Staging failed to capture shape data.")

    def parse_svg_to_shape(self, svg_code):
        token_pattern = re.compile(r'([a-zA-Z])|([-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?)')
        
        def parse_transform(t_str):
            trans = QTransform()
            if not t_str: return trans
            for m in re.finditer(r'([a-z]+)\s*\(([^)]+)\)', t_str):
                name = m.group(1); vals = [float(v) for v in re.split(r'[,\s]+', m.group(2).strip()) if v]
                if name == "matrix" and len(vals) == 6:
                    trans = QTransform(vals[0], vals[1], vals[2], vals[3], vals[4], vals[5]) * trans
                elif name == "translate": trans.translate(vals[0], vals[1] if len(vals)>1 else 0)
                elif name == "scale": trans.scale(vals[0], vals[1] if len(vals)>1 else vals[0])
                elif name == "rotate":
                    if len(vals) == 3: trans.translate(vals[1], vals[2]); trans.rotate(vals[0]); trans.translate(-vals[1], -vals[2])
                    else: trans.rotate(vals[0])
            return trans

        # Improved tag splitting to handle complex nested shapes
        tags = re.findall(r'<(path|rect|circle|ellipse|g|/g)\b([^>]*)>', svg_code, re.I)
        if not tags:
            d_matches = re.findall(r'\bd=["\']([^"\']+)["\']', svg_code)
            if not d_matches: d_matches = [svg_code]
            tags = [("path", f' d="{d}"') for d in d_matches]

        transform_stack = [QTransform()]; all_commands = []; all_pts = []
        
        for tag_name, attr_str in tags:
            tag_name = tag_name.lower()
            if tag_name == "g":
                m = re.search(r'transform=["\']([^"\']+)["\']', attr_str)
                t_str = m.group(1) if m else ""
                transform_stack.append(parse_transform(t_str) * transform_stack[-1])
                continue
            elif tag_name == "/g":
                if len(transform_stack) > 1: transform_stack.pop()
                continue
            
            ct = transform_stack[-1]
            m = re.search(r'transform=["\']([^"\']+)["\']', attr_str)
            if m: ct = parse_transform(m.group(1)) * ct
            def t_pt(x, y):
                p = ct.map(QPointF(x, y)); return p.x(), p.y()

            fill = None; m = re.search(r'fill=["\']([^"\']+)["\']', attr_str)
            if m: fill = m.group(1).strip()
            else:
                m = re.search(r'style=["\'][^"\']*fill:([^;]+)', attr_str)
                if m: fill = m.group(1).strip()
            
            if fill and fill.lower() == "none": fill = "transparent"
            if fill: all_commands.append(["COLOR", fill])

            fr = "nonzero"; m = re.search(r'fill-rule=["\']([^"\']+)["\']', attr_str)
            if m: fr = m.group(1).strip()
            else:
                m = re.search(r'style=["\'][^"\']*fill-rule:([^;]+)', attr_str)
                if m: fr = m.group(1).strip()
            if fr == "evenodd": all_commands.append(["FILLRULE", "evenodd"])

            if tag_name == "path":
                dm = re.search(r'\bd=["\']([^"\']+)["\']', attr_str)
                if not dm: continue
                tokens = []
                for m in token_pattern.finditer(dm.group(1)):
                    if m.group(1): tokens.append(m.group(1))
                    else: tokens.append(float(m.group(2)))
                
                i = 0; cur_x, cur_y = 0, 0; last_cmd = ""; start_x, start_y = 0, 0
                lbx, lby = 0, 0 # Last control point for smooth curves
                
                while i < len(tokens):
                    token = tokens[i]
                    if isinstance(token, str): cmd = token; i += 1
                    else: cmd = last_cmd
                    if not cmd: break
                    
                    try:
                        if cmd in 'Mm':
                            x, y = tokens[i], tokens[i+1]; i += 2
                            if cmd == 'm': x += cur_x; y += cur_y
                            tx, ty = t_pt(x, y); all_commands.append(["M", [tx, ty]]); all_pts.append(QPointF(tx, ty))
                            cur_x, cur_y = x, y; start_x, start_y = x, y; lbx, lby = x, y; last_cmd = 'L' if cmd == 'M' else 'l'
                        elif cmd in 'Ll':
                            x, y = tokens[i], tokens[i+1]; i += 2
                            if cmd == 'l': x += cur_x; y += cur_y
                            tx, ty = t_pt(x, y); all_commands.append(["L", [tx, ty]]); all_pts.append(QPointF(tx, ty))
                            cur_x, cur_y = x, y; lbx, lby = x, y; last_cmd = cmd
                        elif cmd in 'Hh':
                            x = tokens[i]; i += 1
                            if cmd == 'h': x += cur_x
                            tx, ty = t_pt(x, cur_y); all_commands.append(["L", [tx, ty]]); all_pts.append(QPointF(tx, ty))
                            cur_x = x; lbx, lby = x, cur_y; last_cmd = cmd
                        elif cmd in 'Vv':
                            y = tokens[i]; i += 1
                            if cmd == 'v': y += cur_y
                            tx, ty = t_pt(cur_x, y); all_commands.append(["L", [tx, ty]]); all_pts.append(QPointF(tx, ty))
                            cur_y = y; lbx, lby = cur_x, y; last_cmd = cmd
                        elif cmd in 'Cc':
                            x1, y1 = tokens[i], tokens[i+1]; i += 2; x2, y2 = tokens[i], tokens[i+1]; i += 2; x, y = tokens[i], tokens[i+1]; i += 2
                            if cmd == 'c': x1 += cur_x; y1 += cur_y; x2 += cur_x; y2 += cur_y; x += cur_x; y += cur_y
                            tx1, ty1 = t_pt(x1, y1); tx2, ty2 = t_pt(x2, y2); tx, ty = t_pt(x, y); lbx, lby = x2, y2
                            all_commands.append(["C", [tx1, ty1], [tx2, ty2], [tx, ty]]); all_pts.extend([QPointF(tx1, ty1), QPointF(tx2, ty2), QPointF(tx, ty)])
                            cur_x, cur_y = x, y; last_cmd = cmd
                        elif cmd in 'Ss':
                            x2, y2 = tokens[i], tokens[i+1]; i += 2; x, y = tokens[i], tokens[i+1]; i += 2
                            if cmd == 's': x2 += cur_x; y2 += cur_y; x += cur_x; y += cur_y
                            x1, y1 = (2*cur_x - lbx, 2*cur_y - lby) if last_cmd in 'CcSs' else (cur_x, cur_y)
                            tx1, ty1 = t_pt(x1, y1); tx2, ty2 = t_pt(x2, y2); tx, ty = t_pt(x, y); lbx, lby = x2, y2
                            all_commands.append(["C", [tx1, ty1], [tx2, ty2], [tx, ty]]); all_pts.extend([QPointF(tx1, ty1), QPointF(tx2, ty2), QPointF(tx, ty)])
                            cur_x, cur_y = x, y; last_cmd = cmd
                        elif cmd in 'Qq':
                            x1, y1 = tokens[i], tokens[i+1]; i += 2; x, y = tokens[i], tokens[i+1]; i += 2
                            if cmd == 'q': x1 += cur_x; y1 += cur_y; x += cur_x; y += cur_y
                            tx1, ty1 = t_pt(x1, y1); tx, ty = t_pt(x, y); lbx, lby = x1, y1
                            all_commands.append(["Q", [tx1, ty1], [tx, ty]]); all_pts.extend([QPointF(tx1, ty1), QPointF(tx, ty)])
                            cur_x, cur_y = x, y; last_cmd = cmd
                        elif cmd in 'Tt':
                            x, y = tokens[i], tokens[i+1]; i += 2
                            if cmd == 't': x += cur_x; y += cur_y
                            x1, y1 = (2*cur_x - lbx, 2*cur_y - lby) if last_cmd in 'QqTt' else (cur_x, cur_y)
                            tx1, ty1 = t_pt(x1, y1); tx, ty = t_pt(x, y); lbx, lby = x1, y1
                            all_commands.append(["Q", [tx1, ty1], [tx, ty]]); all_pts.extend([QPointF(tx1, ty1), QPointF(tx, ty)])
                            cur_x, cur_y = x, y; last_cmd = cmd
                        elif cmd in 'Aa':
                            # --- Proper SVG Arc-to-Bezier Converter ---
                            rx, ry = abs(tokens[i]), abs(tokens[i+1]); i += 2
                            rot = math.radians(tokens[i] % 360); i += 1
                            large, sweep = bool(tokens[i]), bool(tokens[i+1]); i += 2
                            x1, y1 = tokens[i], tokens[i+1]; i += 2
                            if cmd == 'a': x1 += cur_x; y1 += cur_y
                            
                            if cur_x == x1 and cur_y == y1: continue
                            if rx == 0 or ry == 0: 
                                tx, ty = t_pt(x1, y1); all_commands.append(["L", [tx, ty]]); all_pts.append(QPointF(tx, ty))
                            else:
                                # Center Parameterization Conversion
                                dx, dy = (cur_x - x1)/2.0, (cur_y - y1)/2.0
                                x1p =  math.cos(rot)*dx + math.sin(rot)*dy
                                y1p = -math.sin(rot)*dx + math.cos(rot)*dy
                                check = (x1p*x1p)/(rx*rx) + (y1p*y1p)/(ry*ry)
                                if check > 1: rx *= math.sqrt(check); ry *= math.sqrt(check)
                                sign = -1 if large == sweep else 1
                                sq = ((rx*rx*ry*ry)-(rx*rx*y1p*y1p)-(ry*ry*x1p*x1p)) / ((rx*rx*y1p*y1p)+(ry*ry*x1p*x1p))
                                coef = sign * math.sqrt(max(0, sq))
                                cxp, cyp = coef*((rx*y1p)/ry), coef*(-(ry*x1p)/rx)
                                cx = math.cos(rot)*cxp - math.sin(rot)*cyp + (cur_x + x1)/2.0
                                cy = math.sin(rot)*cxp + math.cos(rot)*cyp + (cur_y + y1)/2.0
                                # Use QPainterPath helper
                                helper = QPainterPath(); helper.moveTo(cur_x, cur_y)
                                # arcTo uses sweep angles, not coordinates
                                def angle(ux, uy, vx, vy):
                                    dot = ux*vx + uy*vy; len = math.sqrt(ux*ux + uy*uy) * math.sqrt(vx*vx + vy*vy)
                                    ang = math.acos(max(-1, min(1, dot/len))); return -ang if ux*vy - uy*vx < 0 else ang
                                start_ang = angle(1, 0, (x1p-cxp)/rx, (y1p-cyp)/ry)
                                sweep_ang = angle((x1p-cxp)/rx, (y1p-cyp)/ry, (-x1p-cxp)/rx, (-y1p-cyp)/ry) % (2*math.pi)
                                if not sweep and sweep_ang > 0: sweep_ang -= 2*math.pi
                                elif sweep and sweep_ang < 0: sweep_ang += 2*math.pi
                                helper.arcTo(cx-rx, cy-ry, rx*2, ry*2, -math.degrees(start_ang), -math.degrees(sweep_ang))
                                
                                # Iterate elements with proper skipping of curve data
                                k = 1
                                while k < helper.elementCount():
                                    el = helper.elementAt(k)
                                    tx, ty = t_pt(el.x, el.y); all_pts.append(QPointF(tx, ty))
                                    if el.type == QPainterPath.ElementType.LineToElement:
                                        all_commands.append(["L", [tx, ty]]); k += 1
                                    elif el.type == QPainterPath.ElementType.CurveToElement:
                                        e1, e2 = helper.elementAt(k+1), helper.elementAt(k+2)
                                        t1x, t1y = t_pt(e1.x, e1.y); t2x, t2y = t_pt(e2.x, e2.y)
                                        all_commands.append(["C", [tx, ty], [t1x, t1y], [t2x, t2y]]); k += 3
                                    else: k += 1
                            
                            cur_x, cur_y = x1, y1; lbx, lby = x1, y1; last_cmd = cmd
                        elif cmd in 'Zz':
                            all_commands.append(["Z"]); cur_x, cur_y = start_x, start_y; last_cmd = ""
                        else: i += 1
                    except: break
            elif tag_name == "rect":
                try:
                    x = float(re.search(r'\bx=["\']([^"\']+)["\']', attr_str).group(1)) if 'x=' in attr_str else 0
                    y = float(re.search(r'\by=["\']([^"\']+)["\']', attr_str).group(1)) if 'y=' in attr_str else 0
                    w = float(re.search(r'\bwidth=["\']([^"\']+)["\']', attr_str).group(1))
                    h = float(re.search(r'\bheight=["\']([^"\']+)["\']', attr_str).group(1))
                    tp = [t_pt(x,y), t_pt(x+w,y), t_pt(x+w,y+h), t_pt(x,y+h)]
                    all_commands.append(["M", tp[0]])
                    for p in tp[1:]: all_commands.append(["L", p])
                    all_commands.append(["Z"]); all_pts.extend([QPointF(*p) for p in tp])
                except: pass
            elif tag_name in ["circle", "ellipse"]:
                try:
                    cx = float(re.search(r'cx=["\']([^"\']+)["\']', attr_str).group(1)) if 'cx=' in attr_str else 0
                    cy = float(re.search(r'cy=["\']([^"\']+)["\']', attr_str).group(1)) if 'cy=' in attr_str else 0
                    rx = float(re.search(r'rx=["\']([^"\']+)["\']', attr_str).group(1)) if 'rx=' in attr_str else float(re.search(r'r=["\']([^"\']+)["\']', attr_str).group(1))
                    ry = float(re.search(r'ry=["\']([^"\']+)["\']', attr_str).group(1)) if 'ry=' in attr_str else rx
                    k = 0.5523
                    pts = [[cx,cy-ry],[cx+k*rx,cy-ry],[cx+rx,cy-k*rx],[cx+rx,cy],[cx+rx,cy+k*ry],[cx+k*rx,cy+ry],[cx,cy+ry],[cx-k*rx,cy+ry],[cx-rx,cy+k*ry],[cx-rx,cy],[cx-rx,cy-k*ry],[cx-k*rx,cy-ry]]
                    tp = [t_pt(px, py) for px, py in pts]
                    all_commands.append(["M", tp[0]])
                    all_commands.append(["C", tp[1], tp[2], tp[3]])
                    all_commands.append(["C", tp[4], tp[5], tp[6]])
                    all_commands.append(["C", tp[7], tp[8], tp[9]])
                    all_commands.append(["C", tp[10], tp[11], tp[0]])
                    all_commands.append(["Z"]); all_pts.extend([QPointF(*p) for p in tp])
                except: pass

        if not all_commands or not all_pts: return None
        return all_commands

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    s = json.load(f)
                    if "geom" in s: self.restoreGeometry(QByteArray.fromHex(s["geom"].encode()))
                    if "state" in s: self.restoreState(QByteArray.fromHex(s["state"].encode()))
                    self.library_columns = s.get("library_columns", 4); self.last_dir = s.get("last_dir", "")
                    self.view.tool = s.get("tool", "brush"); self.view.brush_type = s.get("brush_type", "marker"); self.view.pen_color = QColor(s.get("color", CP_CYAN)); self.view.pen_width = s.get("width", 3); self.view.multi_line_count = s.get("multi_count", 3); sm = s.get("symmetry_mode", "None"); self.view.symmetry_mode = sm; self.sym_combo.setCurrentText(sm); self.view.mirror_count = s.get("mirror_count", 4); self.view.sym_center = QPointF(s.get("sym_x", 0), s.get("sym_y", 0)); self.scene.center_marker.setPos(self.view.sym_center); self.brush_combo.setCurrentText(self.view.brush_type.capitalize()); self.thickness_slider.setValue(self.view.pen_width); self.multi_slider.setValue(self.view.multi_line_count); self.mirror_spin.setValue(self.view.mirror_count); self.update_color_ui(self.view.pen_color); ip = s.get("img_path", "")
                    self.view.is_sharp = s.get("is_sharp", True); self.btn_sharp.setChecked(self.view.is_sharp); self.toggle_sharp()
                    
                    self.scene.show_grid = s.get("show_grid", False); self.btn_show_grid.setChecked(self.scene.show_grid); self.toggle_grid()
                    self.view.snap_to_grid = s.get("snap_to_grid", False); self.btn_snap_grid.setChecked(self.view.snap_to_grid); self.toggle_snap()
                    gs = s.get("grid_size", 20); self.view.grid_size = gs; self.scene.grid_size = gs; self.grid_size_spin.setValue(gs)
                    
                    cbg = s.get("canvas_bg", CP_BG)
                    self.scene.setBackgroundBrush(QColor(cbg))

                    if ip and os.path.exists(ip):
                        self.load_image(ip)
                        if self.view.image_item: self.view.image_item.setPos(s.get("img_x", 0), s.get("img_y", 0))
            except: pass

    def save_settings(self):
        s = {"geom": self.saveGeometry().toHex().data().decode(), "state": self.saveState().toHex().data().decode(), "tool": self.view.tool, "brush_type": self.view.brush_type, "color": self.view.pen_color.name(), "width": self.view.pen_width, "multi_count": self.view.multi_line_count, "symmetry_mode": self.view.symmetry_mode, "mirror_count": self.view.mirror_count, "sym_x": self.view.sym_center.x(), "sym_y": self.view.sym_center.y(), "img_path": self.view.image_path, "img_x": self.view.image_item.x() if self.view.image_item else 0, "img_y": self.view.image_item.y() if self.view.image_item else 0, "is_sharp": self.view.is_sharp,
             "show_grid": self.scene.show_grid, "snap_to_grid": self.view.snap_to_grid, "grid_size": self.view.grid_size,
             "library_columns": getattr(self, 'library_columns', 4),
             "last_dir": self.last_dir,
             "canvas_bg": self.scene.backgroundBrush().color().name()}
        try:
            os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
            with open(SETTINGS_FILE, 'w') as f: json.dump(s, f)
        except: pass

    def closeEvent(self, e): self.save_settings(); super().closeEvent(e)
    def apply_theme(self):
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            QToolBar {{ background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; spacing: 5px; padding: 3px; }}
            
            QPushButton {{ background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 4px 8px; font-weight: bold; font-size: 9pt; }}
            QPushButton:hover {{ background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }}
            
            QComboBox {{ background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 2px; }}
            
            QSpinBox {{ background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 2px; max-width: 42px; }}
            QSpinBox::up-button, QSpinBox::down-button {{ width: 0; height: 0; border: none; }}
            
            QCheckBox {{ spacing: 8px; color: {CP_TEXT}; }}
            QCheckBox::indicator {{ width: 14px; height: 14px; border: 1px solid {CP_DIM}; background: {CP_PANEL}; }}
            QCheckBox::indicator:checked {{ background: {CP_YELLOW}; border-color: {CP_YELLOW}; }}
            
            QStatusBar {{ background-color: {CP_PANEL}; color: {CP_CYAN}; border-top: 1px solid {CP_DIM}; }}
            
            QScrollBar:vertical {{ background: {CP_BG}; width: 10px; margin: 0px; }}
            QScrollBar::handle:vertical {{ background: {CP_CYAN}; min-height: 20px; border-radius: 5px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; background: none; }}
            
            QScrollBar:horizontal {{ background: {CP_BG}; height: 10px; margin: 0px; }}
            QScrollBar::handle:horizontal {{ background: {CP_CYAN}; min-width: 20px; border-radius: 5px; }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0px; background: none; }}
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv); window = SVGArtApp(); window.show(); sys.exit(app.exec())
