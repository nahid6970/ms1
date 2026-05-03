# mypygui_qt.py — PyQt6 rewrite of the Windows taskbar status bar

import ctypes
import json
import os
import subprocess
import sys
import threading
import time
import re
from functools import partial
from datetime import datetime
from queue import Queue, Empty

import psutil
import win32gui
import win32process

try:
    from pyadl import ADLManager
    _HAS_ADL = True
except Exception:
    _HAS_ADL = False

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QDialog, QLineEdit, QComboBox, QCheckBox,
    QGroupBox, QFormLayout, QScrollArea, QMessageBox, QInputDialog,
    QFrame, QSizePolicy, QPlainTextEdit, QColorDialog,
    QStyle, QStyleOption, QGridLayout, QMenu,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QByteArray, QSize, QPoint, QEvent
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QPixmap, QTextDocument, QIcon, QFontDatabase
from PyQt6.QtSvg import QSvgRenderer


start_time = time.time()

class _RcloneSignal(QObject):
    update = pyqtSignal(object, str)  # (toggle_lbl, color)
_rclone_sig = None  # initialized after QApplication exists

from ctypes import wintypes

# AppBar Constants
ABM_NEW = 0x00000000
ABM_REMOVE = 0x00000001
ABM_QUERYPOS = 0x00000002
ABM_SETPOS = 0x00000003
ABE_TOP = 1
WM_USER = 0x0400

class APPBARDATA(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("hWnd", wintypes.HWND),
        ("uCallbackMessage", wintypes.UINT),
        ("uEdge", wintypes.UINT),
        ("rc", wintypes.RECT),
        ("lParam", wintypes.LPARAM),
    ]

def register_appbar(hwnd):
    abd = APPBARDATA()
    abd.cbSize = ctypes.sizeof(APPBARDATA)
    abd.hWnd = hwnd
    abd.uCallbackMessage = WM_USER + 42
    ctypes.windll.shell32.SHAppBarMessage(ABM_NEW, ctypes.byref(abd))

def unregister_appbar(hwnd):
    abd = APPBARDATA()
    abd.cbSize = ctypes.sizeof(APPBARDATA)
    abd.hWnd = hwnd
    ctypes.windll.shell32.SHAppBarMessage(ABM_REMOVE, ctypes.byref(abd))

def set_appbar_position(hwnd, width, height):
    screen_geo = QApplication.primaryScreen().geometry()
    sw, sh = screen_geo.width(), screen_geo.height()
    abd = APPBARDATA()
    abd.cbSize = ctypes.sizeof(APPBARDATA)
    abd.hWnd = hwnd
    abd.uEdge = ABE_TOP
    abd.rc.top = 0
    abd.rc.left = 0
    abd.rc.right = sw
    abd.rc.bottom = height
    ctypes.windll.shell32.SHAppBarMessage(ABM_QUERYPOS, ctypes.byref(abd))
    ctypes.windll.shell32.SHAppBarMessage(ABM_SETPOS, ctypes.byref(abd))

# ─── Theme ────────────────────────────────────────────────────────────────────
CP_BG     = "#050505"
CP_PANEL  = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN   = "#00F0FF"
CP_RED    = "#FF003C"
CP_GREEN  = "#00ff21"
CP_ORANGE = "#ff934b"
CP_DIM    = "#3a3a3a"
CP_TEXT   = "#E0E0E0"

GLOBAL_QSS = f"""
QMainWindow, QWidget {{
    background-color: {CP_BG};
    color: {CP_TEXT};
    font-family: "JetBrainsMono NFP";
    font-size: 10pt;
}}
QPushButton {{
    background-color: {CP_DIM};
    color: {CP_TEXT};
    border: none;
    padding: 2px 6px;
}}
QPushButton:hover {{
    border: 1px solid {CP_YELLOW};
    color: {CP_YELLOW};
}}
QPushButton:pressed {{
    background-color: {CP_YELLOW};
    color: black;
}}
QLabel {{
    background: transparent;
    color: {CP_TEXT};
    margin: 0px;
    padding: 0px;
}}
"""

DIALOG_QSS = f"""
    QDialog, QWidget {{ background-color: {CP_BG}; color: {CP_TEXT}; font-family: Consolas; font-size: 10pt; }}
    QLineEdit, QComboBox, QSpinBox {{
        background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px;
    }}
    QLineEdit:focus, QComboBox:focus {{ border: 1px solid {CP_CYAN}; }}
    QComboBox QAbstractItemView {{ background: {CP_PANEL}; color: {CP_CYAN}; selection-background-color: {CP_CYAN}; selection-color: {CP_BG}; }}
    QPushButton {{
        background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 6px 14px; font-weight: bold;
    }}
    QPushButton:hover {{ background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }}
    QPushButton:pressed {{ background-color: {CP_YELLOW}; color: black; }}
    QPushButton#btn_save {{ border-color: {CP_GREEN}; color: {CP_GREEN}; }}
    QPushButton#btn_save:hover {{ background-color: {CP_GREEN}; color: black; }}
    QPushButton#btn_delete {{ border-color: {CP_RED}; color: {CP_RED}; }}
    QPushButton#btn_delete:hover {{ background-color: {CP_RED}; color: white; }}
    QGroupBox {{
        border: 1px solid {CP_DIM}; margin-top: 10px; padding-top: 8px; font-weight: bold; color: {CP_YELLOW};
    }}
    QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }}
    QCheckBox {{ spacing: 8px; color: {CP_TEXT}; }}
    QCheckBox::indicator {{ width: 13px; height: 13px; border: 1px solid {CP_DIM}; background: {CP_PANEL}; }}
    QCheckBox::indicator:checked {{ background: {CP_YELLOW}; border-color: {CP_YELLOW}; }}
    QScrollArea {{ background: transparent; border: none; }}
    QScrollBar:vertical {{ background: {CP_BG}; width: 8px; margin: 0; }}
    QScrollBar::handle:vertical {{ background: {CP_CYAN}; min-height: 20px; border-radius: 4px; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; background: none; }}
    QLabel#section_label {{ color: {CP_YELLOW}; font-weight: bold; font-size: 9pt; }}
"""

DEFAULT_FONT_FALLBACK = ["JetBrainsMono NFP", 16, "bold"]

# ─── Config ───────────────────────────────────────────────────────────────────
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mypygui_config.json")

def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

def save_config(config):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving config: {e}")

def get_default_font():
    return load_config().get("default_font", DEFAULT_FONT_FALLBACK)

# ─── SVG / Icon Widgets ────────────────────────────────────────────────────────
class SvgInputDialog(QDialog):
    def __init__(self, current_svg="", hover_map=None, parent=None):
        super().__init__(None)
        self.setWindowTitle("PASTE SVG CODE")
        self.resize(600, 580)
        self.svg_code = current_svg
        self.hover_map = hover_map or {}
        self.setStyleSheet(f"""
            QDialog {{ background-color: {CP_BG}; border: 2px solid {CP_CYAN}; }}
            QPlainTextEdit {{ background-color: {CP_PANEL}; color: {CP_TEXT}; font-family: 'Consolas'; border: 1px solid {CP_DIM}; }}
            QPushButton {{ background-color: {CP_DIM}; color: white; padding: 8px; border: 1px solid {CP_DIM}; }}
            QPushButton:hover {{ border: 1px solid {CP_CYAN}; }}
            QLabel {{ color: {CP_YELLOW}; font-family: 'Consolas'; font-weight: bold; font-size: 9pt; }}
            QScrollArea {{ border: 1px solid {CP_DIM}; background: {CP_PANEL}; }}
        """)
        layout = QVBoxLayout(self)
        
        # Live Preview section at top
        layout.addWidget(QLabel("LIVE PREVIEW:"))
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(64, 64)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet(f"border: 1px solid {CP_DIM}; background: {CP_PANEL};")
        p_box = QHBoxLayout(); p_box.addStretch(); p_box.addWidget(self.preview_label); p_box.addStretch()
        layout.addLayout(p_box)

        layout.addWidget(QLabel("SVG CODE:"))
        self.txt_input = QPlainTextEdit()
        self.txt_input.setPlaceholderText("<svg>...</svg>")
        self.txt_input.setPlainText(self.svg_code)
        layout.addWidget(self.txt_input, stretch=2)
        layout.addWidget(QLabel("BASE COLORS (CLICK TO REPLACE IN CODE):"))
        self.color_scroll = QScrollArea(); self.color_scroll.setWidgetResizable(True); self.color_scroll.setFixedHeight(60)
        self.color_widget = QWidget(); self.color_layout = QHBoxLayout(self.color_widget); self.color_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.color_scroll.setWidget(self.color_widget); layout.addWidget(self.color_scroll)
        layout.addWidget(QLabel("HOVER OVERRIDES (CLICK TO SET HOVER COLOR):"))
        self.hover_scroll = QScrollArea(); self.hover_scroll.setWidgetResizable(True); self.hover_scroll.setFixedHeight(60)
        self.hover_widget = QWidget(); self.hover_layout = QHBoxLayout(self.hover_widget); self.hover_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.hover_scroll.setWidget(self.hover_widget); layout.addWidget(self.hover_scroll)
        
        self.color_timer = QTimer(); self.color_timer.setSingleShot(True)
        self.color_timer.timeout.connect(self.update_color_panel)
        self.color_timer.timeout.connect(self.update_preview)
        
        self.txt_input.textChanged.connect(lambda: self.color_timer.start(500))
        btn_box = QHBoxLayout()
        btn_save = QPushButton("SAVE SVG"); btn_save.setStyleSheet(f"background-color: {CP_GREEN}; color: black; font-weight: bold;"); btn_save.clicked.connect(self.save_and_close)
        btn_clear = QPushButton("CLEAR"); btn_clear.clicked.connect(lambda: self.txt_input.clear())
        btn_cancel = QPushButton("CANCEL"); btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_save); btn_box.addWidget(btn_clear); btn_box.addWidget(btn_cancel)
        layout.addLayout(btn_box)
        self.update_color_panel()
        self.update_preview()

    def update_preview(self):
        code = self.txt_input.toPlainText().strip()
        if not code:
            self.preview_label.clear()
            return
        try:
            pix = QPixmap(64, 64); pix.fill(Qt.GlobalColor.transparent)
            p = QPainter(pix); renderer = QSvgRenderer(QByteArray(code.encode('utf-8')))
            renderer.render(p); p.end()
            self.preview_label.setPixmap(pix)
        except:
            self.preview_label.setText("ERR")

    def update_color_panel(self):
        for lay in [self.color_layout, self.hover_layout]:
            while lay.count():
                item = lay.takeAt(0)
                if item.widget(): item.widget().deleteLater()
        svg = self.txt_input.toPlainText()
        colors = sorted(list(set(re.findall(r'#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3}', svg))), key=len, reverse=True)
        if not colors:
            for lay in [self.color_layout, self.hover_layout]:
                lay.addWidget(QLabel("None"))
        else:
            for c in colors:
                btn = QPushButton(); btn.setFixedSize(30, 30); btn.setStyleSheet(f"background-color: {c}; border: 1px solid {CP_DIM}; border-radius: 4px;")
                btn.clicked.connect(partial(self.pick_replacement_color, c)); self.color_layout.addWidget(btn)
                h_btn = QPushButton(); h_btn.setFixedSize(30, 30); hover_c = self.hover_map.get(c, c)
                h_btn.setStyleSheet(f"background-color: {hover_c}; border: 2px solid {CP_YELLOW if c in self.hover_map else CP_DIM}; border-radius: 4px;")
                h_btn.clicked.connect(partial(self.pick_hover_color, c)); self.hover_layout.addWidget(h_btn)
        self.color_layout.addStretch(); self.hover_layout.addStretch()

    def pick_hover_color(self, base_color):
        curr = self.hover_map.get(base_color, base_color)
        c = QColorDialog.getColor(QColor(curr), self, f"Select Hover Color for {base_color}")
        if c.isValid():
            self.hover_map[base_color] = c.name().upper(); self.update_color_panel()

    def pick_replacement_color(self, old_color):
        c = QColorDialog.getColor(QColor(old_color), self, "Select New Color")
        if c.isValid():
            new_color = c.name().upper()
            if old_color in self.hover_map: self.hover_map[new_color] = self.hover_map.pop(old_color)
            svg = self.txt_input.toPlainText(); pattern = re.compile(re.escape(old_color), re.IGNORECASE)
            self.txt_input.setPlainText(pattern.sub(new_color, svg)); self.update_color_panel()

    def save_and_close(self):
        self.svg_code = self.txt_input.toPlainText(); self.accept()

class IconLabel(QLabel):
    def __init__(self, text, btn_cfg, parent=None):
        super().__init__(None, parent)
        self.btn_cfg = btn_cfg or {}
        self._original_text = text
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self._is_hovered = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def text(self):
        return self._original_text

    def setText(self, t):
        self._original_text = t
        self.update()

    def sizeHint(self):
        cfg = self.btn_cfg
        has_icon = cfg.get("icon_path") and os.path.exists(cfg.get("icon_path"))
        has_svg = bool(cfg.get("svg_content", "").strip())
        has_nf = bool(cfg.get("nf_char", ""))
        
        if has_icon or has_svg or has_nf:
            w = cfg.get("icon_width", 0) or 24
            h = cfg.get("icon_height", 0) or 24
            m = self.contentsMargins()
            return QSize(w + m.left() + m.right(), h + m.top() + m.bottom())
        
        doc = QTextDocument()
        f = self.font()
        if "font" in cfg:
            font_cfg = cfg["font"]
            f = QFont(font_cfg[0], font_cfg[1])
            if len(font_cfg) > 2 and font_cfg[2] == "bold": f.setBold(True)
        doc.setDefaultFont(f)
        doc.setHtml(f"<div style='white-space: pre;'>{self._original_text}</div>")
        m = self.contentsMargins()
        return QSize(int(doc.idealWidth()) + m.left() + m.right(), int(doc.size().height()) + m.top() + m.bottom())

    def minimumSizeHint(self):
        return self.sizeHint()

    def enterEvent(self, event):
        self._is_hovered = True; self.update(); super().enterEvent(event)
    def leaveEvent(self, event):
        self._is_hovered = False; self.update(); super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        opt = QStyleOption()
        opt.initFrom(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, painter, self)
        
        rect = self.contentsRect()
        if rect.isEmpty(): return

        fg = self.palette().windowText().color().name()

        cfg = self.btn_cfg
        icon_pixmap = None
        draw_mode = 'text'

        icon_path = cfg.get("icon_path", "")
        svg_content = cfg.get("svg_content", "")
        nf_char = cfg.get("nf_char", "")

        try:
            if icon_path and os.path.exists(icon_path):
                icon_pixmap = QPixmap(icon_path)
                draw_mode = 'icon'
            elif svg_content and svg_content.strip():
                gen_w = cfg.get("icon_width", 0) or 64
                gen_h = cfg.get("icon_height", 0) or 64
                icon_pixmap = QPixmap(gen_w, gen_h); icon_pixmap.fill(Qt.GlobalColor.transparent)
                actual_svg = svg_content
                if self._is_hovered:
                    hmap = cfg.get("svg_hover_map", {})
                    for base_c, hover_c in hmap.items():
                        pattern = re.compile(re.escape(base_c), re.IGNORECASE)
                        actual_svg = pattern.sub(hover_c, actual_svg)
                p_svg = QPainter(icon_pixmap)
                renderer = QSvgRenderer(QByteArray(actual_svg.encode('utf-8')))
                renderer.render(p_svg); p_svg.end()
                draw_mode = 'icon'
            elif nf_char:
                gen_w = cfg.get("icon_width", 0) or 64
                gen_h = cfg.get("icon_height", 0) or 64
                icon_pixmap = QPixmap(gen_w, gen_h); icon_pixmap.fill(Qt.GlobalColor.transparent)
                p = QPainter(icon_pixmap); p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
                f = self.font()
                f.setPixelSize(int(min(gen_w, gen_h) * 0.8))
                p.setFont(f); p.setPen(QColor(fg)); p.drawText(icon_pixmap.rect(), Qt.AlignmentFlag.AlignCenter, nf_char); p.end()
                draw_mode = 'icon'
            else:
                draw_mode = 'text'

            if icon_pixmap and not icon_pixmap.isNull():
                custom_w = cfg.get("icon_width", 0)
                custom_h = cfg.get("icon_height", 0)
                if custom_w > 0 and custom_h > 0:
                    icon_pixmap = icon_pixmap.scaled(custom_w, custom_h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                elif custom_w > 0: icon_pixmap = icon_pixmap.scaledToWidth(custom_w, Qt.TransformationMode.SmoothTransformation)
                elif custom_h > 0: icon_pixmap = icon_pixmap.scaledToHeight(custom_h, Qt.TransformationMode.SmoothTransformation)
                else:
                    max_h = rect.height() - 4
                    if max_h > 0:
                        icon_pixmap = icon_pixmap.scaledToHeight(max_h, Qt.TransformationMode.SmoothTransformation)
        except: pass

        if draw_mode == 'icon' and icon_pixmap:
            x = rect.x() + (rect.width() - icon_pixmap.width()) // 2
            y = rect.y() + (rect.height() - icon_pixmap.height()) // 2
            painter.drawPixmap(x, y, icon_pixmap)
        else:
            text = self._original_text
            if not text: return
            doc = QTextDocument()
            f = self.font()
            if "font" in cfg:
                font_cfg = cfg["font"]
                f = QFont(font_cfg[0], font_cfg[1])
                if len(font_cfg) > 2 and font_cfg[2] == "bold": f.setBold(True)
            doc.setDefaultFont(f)
            doc.setHtml(f"<div style='color: {fg}; white-space: pre;'>{text}</div>")
            
            text_w = doc.idealWidth()
            text_h = doc.size().height()
            
            x = rect.x() + (rect.width() - text_w) / 2
            y = rect.y() + (rect.height() - text_h) / 2
            painter.translate(x, y)
            doc.drawContents(painter)


# ─── Helpers ──────────────────────────────────────────────────────────────────
def run_command(command, admin=False, hide=False, no_exit=True):
    executable = "pwsh"
    if admin:
        try:
            args = f"{'-NoExit ' if no_exit else ''}-Command \"{command}\""
            ctypes.windll.shell32.ShellExecuteW(None, "runas", executable, args, None, 1 if not hide else 0)
        except Exception as e:
            print(f"Admin run_command failed: {e}")
        return

    cmd_args = [executable]
    if no_exit:
        cmd_args.append("-NoExit")
    cmd_args.extend(["-Command", command])

    flags = 0
    if hide:
        flags |= subprocess.CREATE_NO_WINDOW
    else:
        flags |= subprocess.CREATE_NEW_CONSOLE

    try:
        subprocess.Popen(cmd_args, creationflags=flags)
    except Exception as e:
        print(f"run_command failed: {e}")

def handle_action(action_cfg):
    if not action_cfg:
        return
    atype  = action_cfg.get("type")
    cmd    = action_cfg.get("cmd")
    cwd    = action_cfg.get("cwd")
    admin  = action_cfg.get("admin", False)
    hide   = action_cfg.get("hide", False)
    
    # If admin and not already handled by run_command, handle here
    if admin and atype not in ["run_command"]:
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas",
                sys.executable if atype == "python" else "cmd.exe",
                f"/c {cmd}" if atype != "python" else cmd,
                cwd, 0 if hide else 1
            )
        except Exception as e:
            print(f"Admin launch failed: {e}")
        return

    flags = subprocess.CREATE_NO_WINDOW if hide else 0
    if atype == "url":
        import webbrowser; webbrowser.open(cmd); return
    if atype == "subprocess":
        subprocess.Popen(cmd, cwd=cwd, shell=True, creationflags=flags)
    elif atype == "run_command":
        run_command(cmd, admin=admin, hide=hide)
    elif atype == "python":
        subprocess.Popen([sys.executable, cmd], cwd=cwd, creationflags=flags)
    elif atype == "function":
        func_name = action_cfg.get("func")
        if func_name == "restart":      _app_restart()
        elif func_name == "close_window": _app_close()
        elif func_name == "force_shutdown": force_shutdown()
        elif func_name == "force_restart":  force_restart()

def _app_close():
    QApplication.instance().quit()

def _app_restart():
    subprocess.Popen([sys.executable] + sys.argv)
    QApplication.instance().quit()

def force_shutdown():
    r = QMessageBox.question(None, "Shutdown", "Are you sure you want to shutdown?")
    if r == QMessageBox.StandardButton.Yes:
        subprocess.run(["shutdown", "/s", "/f", "/t", "0"])

def force_restart():
    r = QMessageBox.question(None, "Restart", "Are you sure you want to restart?")
    if r == QMessageBox.StandardButton.Yes:
        subprocess.run(["shutdown", "/r", "/f", "/t", "0"])

def calculate_time_to_appear(t0):
    print(f"Time taken to appear: {time.time() - t0:.2f} seconds")

# ─── System info ──────────────────────────────────────────────────────────────
def get_cpu_ram_info():
    return psutil.cpu_percent(interval=None), psutil.virtual_memory().percent

def get_gpu_usage():
    if not _HAS_ADL:
        return 0
    try:
        return ADLManager.getInstance().getDevices()[0].getCurrentUsage()
    except Exception:
        return 0

def get_disk_info():
    return psutil.disk_usage('C:').percent, psutil.disk_usage('D:').percent

_net_last = {"sent": 0, "recv": 0}

def get_net_speed():
    io = psutil.net_io_counters()
    up   = (io.bytes_sent - _net_last["sent"]) / (1024 * 1024)
    down = (io.bytes_recv - _net_last["recv"]) / (1024 * 1024)
    _net_last["sent"] = io.bytes_sent
    _net_last["recv"] = io.bytes_recv
    return f"{up:.2f}", f"{down:.2f}"

def get_system_uptime():
    uptime = datetime.now().timestamp() - psutil.boot_time()
    h, rem = divmod(uptime, 3600)
    m, s   = divmod(rem, 60)
    return int(h), int(m), int(s)

def format_uptime():
    h, m, s = get_system_uptime()
    return f"\udb81\udf8c {h:02d}:{m:02d}:{s:02d}"


# ─── Edit GUI dialog ──────────────────────────────────────────────────────────
def open_edit_gui(item_cfg, category, index=None):
    config_now = load_config()
    dlg = QDialog()
    dlg.setWindowTitle(f"Edit — {item_cfg.get('id', 'Item')}")
    ew = config_now.get("edit_panel_width", 1000)
    eh = config_now.get("edit_panel_height", 700)
    dlg.setFixedSize(ew, eh)
    dlg.setStyleSheet(DIALOG_QSS)
    dlg.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
    
    screen_geo = QApplication.primaryScreen().availableGeometry()
    dlg.move(screen_geo.center().x() - ew // 2, screen_geo.center().y() - eh // 2)

    root_layout = QVBoxLayout(dlg)
    root_layout.setContentsMargins(10, 10, 10, 10)
    root_layout.setSpacing(8)

    title = QLabel(f"// EDIT :: {item_cfg.get('id', 'ITEM').upper()}")
    title.setStyleSheet(f"color: {CP_CYAN}; font-size: 13pt; font-weight: bold; padding: 4px 0;")
    root_layout.addWidget(title)

    panels = QHBoxLayout()
    panels.setSpacing(10)
    root_layout.addLayout(panels)

    # Left panel
    left_scroll = QScrollArea(); left_scroll.setWidgetResizable(True)
    left_w = QWidget(); left_layout = QVBoxLayout(left_w)
    left_layout.setSpacing(6); left_layout.setContentsMargins(6, 6, 6, 6)
    left_scroll.setWidget(left_w)
    l_weight = config_now.get("edit_left_weight", 1)
    panels.addWidget(left_scroll, l_weight)

    # 1. CORE SECTION (Top Section)
    grp_core = QGroupBox("CORE SETTINGS"); form_core = QVBoxLayout(); grp_core.setLayout(form_core)
    
    # Row 1: Text, Path, NF, SVG
    row1 = QWidget(); lay1 = QHBoxLayout(row1); lay1.setContentsMargins(0,0,0,0); lay1.setSpacing(10)
    text_le = QLineEdit(str(item_cfg.get("text", ""))); lay1.addWidget(QLabel("TEXT")); lay1.addWidget(text_le, 2)
    icon_path_le = QLineEdit(str(item_cfg.get("icon_path", ""))); lay1.addWidget(QLabel("PATH")); lay1.addWidget(icon_path_le, 3)
    nf_char_le = QLineEdit(str(item_cfg.get("nf_char", ""))); nf_char_le.setFixedWidth(40)
    lay1.addWidget(QLabel("NF")); lay1.addWidget(nf_char_le)

    svg_btn = QPushButton("SVG"); svg_btn.setFixedSize(50, 26)
    svg_btn.setStyleSheet("QPushButton { padding: 0px; }") # Remove large padding for this small button
    def _update_svg_preview(code):
        if not code:
            svg_btn.setText("SVG"); svg_btn.setIcon(QIcon())
            return
        try:
            pix = QPixmap(24, 24); pix.fill(Qt.GlobalColor.transparent)
            p = QPainter(pix); renderer = QSvgRenderer(QByteArray(code.encode('utf-8')))
            renderer.render(p); p.end()
            svg_btn.setText(""); svg_btn.setIcon(QIcon(pix)); svg_btn.setIconSize(QSize(20, 20))
        except: svg_btn.setText("ERR")
    _update_svg_preview(item_cfg.get("svg_content", ""))

    def _open_svg_dlg():
        dlg_svg = SvgInputDialog(item_cfg.get("svg_content", ""), item_cfg.get("svg_hover_map", {}))
        if dlg_svg.exec():
            item_cfg["svg_content"] = dlg_svg.svg_code
            item_cfg["svg_hover_map"] = dlg_svg.hover_map
            _update_svg_preview(dlg_svg.svg_code)
    svg_btn.clicked.connect(_open_svg_dlg)
    lay1.addWidget(svg_btn)
    form_core.addWidget(row1)

    # Row 2: W, H, GAP
    row2 = QWidget(); lay2 = QHBoxLayout(row2); lay2.setContentsMargins(0,0,0,0); lay2.setSpacing(10)
    icon_w_le = QLineEdit(str(item_cfg.get("icon_width", 0))); icon_w_le.setFixedWidth(40)
    icon_h_le = QLineEdit(str(item_cfg.get("icon_height", 0))); icon_h_le.setFixedWidth(40)
    icon_gap_le = QLineEdit(str(item_cfg.get("icon_gap", 4))); icon_gap_le.setFixedWidth(40)

    lay2.addWidget(QLabel("ICON SCALING:  W"));  lay2.addWidget(icon_w_le)
    lay2.addWidget(QLabel("H"));  lay2.addWidget(icon_h_le)
    lay2.addWidget(QLabel("GAP")); lay2.addWidget(icon_gap_le)
    
    icon_pos_cb = QComboBox(); icon_pos_cb.addItems(["left", "right", "top", "bottom", "center"])
    icon_pos_cb.setCurrentText(item_cfg.get("icon_position", "left"))
    lay2.addWidget(QLabel(" POS")); lay2.addWidget(icon_pos_cb); lay2.addStretch()
    form_core.addWidget(row2)

    left_layout.addWidget(grp_core)

    click_types = [("LEFT CLICK", "Button-1"), ("RIGHT CLICK", "Button-3"),
                   ("CTRL + LEFT", "Control-Button-1"), ("CTRL + RIGHT", "Control-Button-3")]
    
    first_bcfg = {}
    for _, bkey in click_types:
        bc = item_cfg.get("bindings", {}).get(bkey, {})
        if bc.get("type") == "popup":
            first_bcfg = bc; break

    _temp_colors = {
        "fg": item_cfg.get("fg", ""),
        "bg": item_cfg.get("bg", ""),
        "border_color": item_cfg.get("border_color", ""),
        "pop_bg": first_bcfg.get("bg_color", ""),
        "pop_border": first_bcfg.get("border_color", "")
    }

    def _set_color_btn(btn, col):
        if not col or col.lower() == "transparent":
            btn.setStyleSheet(f"background: transparent; color: {CP_TEXT}; border: 1px solid {CP_DIM};")
            return
        try:
            qcol = QColor(col)
            if qcol.alpha() == 0:
                btn.setStyleSheet(f"background: transparent; color: {CP_TEXT}; border: 1px solid {CP_DIM};")
            else:
                lc = qcol.lightness()
                btn.setStyleSheet(f"background: {col}; color: {'black' if lc > 128 else 'white'}; border: 1px solid {CP_DIM}; font-weight: bold;")
        except:
            btn.setStyleSheet(f"background: transparent; color: {CP_RED}; border: 1px solid {CP_RED};")

    def _pick_color(btn, temp_key):
        curr = _temp_colors[temp_key] or "#000000"
        qcurr = QColor(curr) if curr and curr != "transparent" else QColor(0,0,0,0)
        c = QColorDialog.getColor(qcurr, dlg, "Select Color", QColorDialog.ColorDialogOption.ShowAlphaChannel)
        if c.isValid():
            # Use HexArgb if it has transparency, else standard Hex
            hex_val = c.name(QColor.NameFormat.HexArgb).upper() if c.alpha() < 255 else c.name().upper()
            if c.alpha() == 0: hex_val = "transparent"
            _temp_colors[temp_key] = hex_val
            _set_color_btn(btn, hex_val)

    def _add_color_context(btn, temp_key):
        def show_menu(pos):
            menu = QMenu(); menu.setStyleSheet(DIALOG_QSS)
            act = menu.addAction("SET TRANSPARENT")
            if menu.exec(btn.mapToGlobal(pos)):
                _temp_colors[temp_key] = "transparent"
                _set_color_btn(btn, "transparent")
        btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        btn.customContextMenuRequested.connect(show_menu)
        btn.setToolTip("Left Click: Pick Color | Right Click: Set Transparent")

    # 2. APPEARANCE (Colors & Borders)
    grp_appear = QGroupBox("APPEARANCE"); form_appear = QFormLayout(); form_appear.setSpacing(6); grp_appear.setLayout(form_appear)
    
    text_le = QLineEdit(str(item_cfg.get("text", "")))
    form_appear.addRow("TEXT", text_le)
    
    fg_btn = QPushButton("FG"); fg_btn.setFixedWidth(60); _set_color_btn(fg_btn, _temp_colors["fg"])
    fg_btn.clicked.connect(lambda: _pick_color(fg_btn, "fg")); _add_color_context(fg_btn, "fg")
    
    bg_btn = QPushButton("BG"); bg_btn.setFixedWidth(60); _set_color_btn(bg_btn, _temp_colors["bg"])
    bg_btn.clicked.connect(lambda: _pick_color(bg_btn, "bg")); _add_color_context(bg_btn, "bg")
    
    col_row = QWidget(); col_lay = QHBoxLayout(col_row); col_lay.setContentsMargins(0,0,0,0); col_lay.setSpacing(10)
    col_lay.addWidget(fg_btn)
    col_lay.addWidget(bg_btn); col_lay.addStretch()
    form_appear.addRow("COLORS", col_row)

    id_le = QLineEdit(str(item_cfg.get("id", "")))
    form_appear.addRow("ID", id_le)
    
    border_px_le = QLineEdit(str(item_cfg.get("border", 0))); border_px_le.setFixedWidth(40)
    border_radius_le = QLineEdit(str(item_cfg.get("border_radius", 0))); border_radius_le.setFixedWidth(40)
    
    border_color_btn = QPushButton("BRD"); border_color_btn.setFixedWidth(60); _set_color_btn(border_color_btn, _temp_colors["border_color"])
    border_color_btn.clicked.connect(lambda: _pick_color(border_color_btn, "border_color")); _add_color_context(border_color_btn, "border_color")
    
    b_row = QWidget(); b_lay = QHBoxLayout(b_row); b_lay.setContentsMargins(0,0,0,0); b_lay.setSpacing(10)
    b_lay.addWidget(border_px_le); b_lay.addWidget(QLabel("RADIUS")); b_lay.addWidget(border_radius_le)
    b_lay.addWidget(QLabel("COLOR")); b_lay.addWidget(border_color_btn); b_lay.addStretch()
    
    form_appear.addRow("BORDER PX", b_row)

    width_le  = QLineEdit(str(item_cfg.get("width", 0)));  width_le.setFixedWidth(50)
    height_le = QLineEdit(str(item_cfg.get("height", 0))); height_le.setFixedWidth(50)
    dim_btn_row = QWidget(); dim_btn_lay = QHBoxLayout(dim_btn_row); dim_btn_lay.setContentsMargins(0,0,0,0); dim_btn_lay.setSpacing(10)
    dim_btn_lay.addWidget(width_le); dim_btn_lay.addWidget(QLabel("HEIGHT")); dim_btn_lay.addWidget(height_le); dim_btn_lay.addStretch()
    form_appear.addRow("WIDTH", dim_btn_row)

    left_layout.addWidget(grp_appear)

    # 3. FONT
    grp_font = QGroupBox("FONT"); form_font = QFormLayout(); form_font.setSpacing(6); grp_font.setLayout(form_font)
    
    # Load defaults from config if font not in item_cfg
    def_font = config_now.get("default_font", ["JetBrainsMono NFP", 16, "bold"])
    cur_font = item_cfg.get("font", def_font)
    
    font_family_cb = QComboBox(); font_family_cb.addItems(QFontDatabase.families())
    font_family_cb.setCurrentText(cur_font[0] if cur_font else "JetBrainsMono NFP")
    font_size_le = QLineEdit(str(cur_font[1]) if len(cur_font) > 1 else "16"); font_size_le.setFixedWidth(60)
    font_weight_cb = QComboBox(); font_weight_cb.addItems(["bold", "normal"])
    font_weight_cb.setCurrentText(cur_font[2] if len(cur_font) > 2 else "bold")

    f_row = QWidget(); f_lay = QHBoxLayout(f_row); f_lay.setContentsMargins(0,0,0,0); f_lay.setSpacing(10)
    f_lay.addWidget(font_size_le); f_lay.addWidget(QLabel("WEIGHT")); f_lay.addWidget(font_weight_cb); f_lay.addStretch()

    form_font.addRow("FAMILY", font_family_cb); form_font.addRow("SIZE", f_row)
    left_layout.addWidget(grp_font)

    grp_pad = QGroupBox("SPACING"); form_pad = QFormLayout(); form_pad.setSpacing(6); grp_pad.setLayout(form_pad)
    padx_left_le  = QLineEdit(str(item_cfg.get("padx_left", 1))); padx_left_le.setFixedWidth(40)
    padx_right_le = QLineEdit(str(item_cfg.get("padx_right", 1))); padx_right_le.setFixedWidth(40)
    pady_top_le   = QLineEdit(str(item_cfg.get("pady_top", 0))); pady_top_le.setFixedWidth(40)
    pady_bottom_le = QLineEdit(str(item_cfg.get("pady_bottom", 0))); pady_bottom_le.setFixedWidth(40)
    
    margin_left_le  = QLineEdit(str(item_cfg.get("margin_left", 0))); margin_left_le.setFixedWidth(40)
    margin_right_le = QLineEdit(str(item_cfg.get("margin_right", 0))); margin_right_le.setFixedWidth(40)
    margin_top_le   = QLineEdit(str(item_cfg.get("margin_top", 0))); margin_top_le.setFixedWidth(40)
    margin_bottom_le = QLineEdit(str(item_cfg.get("margin_bottom", 0))); margin_bottom_le.setFixedWidth(40)

    p_row = QWidget(); p_lay = QHBoxLayout(p_row); p_lay.setContentsMargins(0,0,0,0); p_lay.setSpacing(8)
    p_lay.addWidget(QLabel("L")); p_lay.addWidget(padx_left_le)
    p_lay.addWidget(QLabel("R")); p_lay.addWidget(padx_right_le)
    p_lay.addWidget(QLabel("T")); p_lay.addWidget(pady_top_le)
    p_lay.addWidget(QLabel("B")); p_lay.addWidget(pady_bottom_le); p_lay.addStretch()
    form_pad.addRow("PADDING", p_row)

    m_row = QWidget(); m_lay = QHBoxLayout(m_row); m_lay.setContentsMargins(0,0,0,0); m_lay.setSpacing(8)
    m_lay.addWidget(QLabel("L")); m_lay.addWidget(margin_left_le)
    m_lay.addWidget(QLabel("R")); m_lay.addWidget(margin_right_le)
    m_lay.addWidget(QLabel("T")); m_lay.addWidget(margin_top_le)
    m_lay.addWidget(QLabel("B")); m_lay.addWidget(margin_bottom_le); m_lay.addStretch()
    form_pad.addRow("MARGINS", m_row)
    
    left_layout.addWidget(grp_pad)

    grp_place = QGroupBox("PLACEMENT"); form_place = QFormLayout(); form_place.setSpacing(6); grp_place.setLayout(form_place)
    group_le = QLineEdit(category or "buttons_left")
    
    initial_idx = index
    if initial_idx is None:
        initial_idx = len(config_now.get(group_le.text(), []))
    # Show 1-based index to user
    index_le = QLineEdit(str(initial_idx + 1)); index_le.setFixedWidth(60)
    
    def _on_group_txt_changed(text):
        if index is None:
            c = load_config()
            lst = c.get(text, [])
            if isinstance(lst, list): index_le.setText(str(len(lst) + 1))
            else: index_le.setText("1")
    group_le.textChanged.connect(_on_group_txt_changed)
    
    p_row = QWidget(); p_lay = QHBoxLayout(p_row); p_lay.setContentsMargins(0,0,0,0); p_lay.setSpacing(10)
    p_lay.addWidget(group_le); p_lay.addWidget(QLabel("INDEX")); p_lay.addWidget(index_le); p_lay.addStretch()
    form_place.addRow("GROUP/CATEGORY", p_row)
    left_layout.addWidget(grp_place)
    left_layout.addStretch()

    # Right panel
    right_scroll = QScrollArea(); right_scroll.setWidgetResizable(True)
    right_w = QWidget(); right_layout = QVBoxLayout(right_w)
    right_layout.setSpacing(6); right_layout.setContentsMargins(6, 6, 6, 6)
    right_scroll.setWidget(right_w)
    r_weight = config_now.get("edit_right_weight", 2)
    panels.addWidget(right_scroll, r_weight)
    _ctrl_lbl = QLabel("CONTROLS"); _ctrl_lbl.setObjectName("section_label"); right_layout.addWidget(_ctrl_lbl)

    click_types = [("LEFT CLICK", "Button-1"), ("RIGHT CLICK", "Button-3"),
                   ("CTRL + LEFT", "Control-Button-1"), ("CTRL + RIGHT", "Control-Button-3")]
    binding_inputs = {}
    
    first_bcfg = {}
    for _, bkey in click_types:
        bc = item_cfg.get("bindings", {}).get(bkey, {})
        if bc.get("type") == "popup":
            first_bcfg = bc; break

    for label_text, bkey in click_types:
        grp = QGroupBox(label_text); form = QFormLayout(); form.setSpacing(4); grp.setLayout(form)
        bcfg = item_cfg.get("bindings", {}).get(bkey, {})
        cmd_le   = QLineEdit(bcfg.get("cmd", bcfg.get("func", "")))
        type_cb  = QComboBox(); type_cb.addItems(["subprocess", "run_command", "python", "function", "url", "popup"])
        type_cb.setCurrentText(bcfg.get("type", "subprocess"))
        hide_chk  = QCheckBox("Hide Terminal"); hide_chk.setChecked(bcfg.get("hide", False))
        admin_chk = QCheckBox("Run as Admin");  admin_chk.setChecked(bcfg.get("admin", False))
        chk_row = QWidget(); chk_layout = QHBoxLayout(chk_row); chk_layout.setContentsMargins(0,0,0,0)
        chk_layout.addWidget(hide_chk); chk_layout.addWidget(admin_chk); chk_layout.addStretch()
        form.addRow("CMD", cmd_le); form.addRow("TYPE", type_cb); form.addRow("", chk_row)
        right_layout.addWidget(grp)
        binding_inputs[bkey] = {"cmd": cmd_le, "type": type_cb, "hide": hide_chk, "admin": admin_chk}

    # Dedicated POPUP SETTINGS section
    grp_pop = QGroupBox("POPUP SETTINGS"); pop_lay = QVBoxLayout(); pop_lay.setSpacing(8); grp_pop.setLayout(pop_lay)
    row_limit_le = QLineEdit(str(first_bcfg.get("row_limit", 10))); row_limit_le.setFixedWidth(40)

    pop_bg_btn = QPushButton("BG"); pop_bg_btn.setFixedWidth(60); _set_color_btn(pop_bg_btn, _temp_colors["pop_bg"])
    pop_bg_btn.clicked.connect(lambda: _pick_color(pop_bg_btn, "pop_bg"))

    pop_border_btn = QPushButton("BRD"); pop_border_btn.setFixedWidth(60); _set_color_btn(pop_border_btn, _temp_colors["pop_border"])
    pop_border_btn.clicked.connect(lambda: _pick_color(pop_border_btn, "pop_border"))

    pop_border_px_le = QLineEdit(str(first_bcfg.get("border_px", 1))); pop_border_px_le.setFixedWidth(40)
    pop_trans_chk = QCheckBox("TRANS"); pop_trans_chk.setChecked(first_bcfg.get("transparent_bg", False))

    row_pop = QWidget(); lay_p = QHBoxLayout(row_pop); lay_p.setContentsMargins(0,0,0,0); lay_p.setSpacing(10)
    lay_p.addWidget(QLabel("LIMIT")); lay_p.addWidget(row_limit_le)
    lay_p.addWidget(pop_bg_btn); lay_p.addWidget(pop_border_btn)
    lay_p.addWidget(QLabel("PX")); lay_p.addWidget(pop_border_px_le)
    lay_p.addWidget(pop_trans_chk); lay_p.addStretch()
    pop_lay.addWidget(row_pop)

    right_layout.addWidget(grp_pop)


    def _check_popup_visibility():
        any_popup = False
        for bkey in binding_inputs:
            if binding_inputs[bkey]["type"].currentText() == "popup":
                any_popup = True; break
        grp_pop.setEnabled(any_popup)

    for bkey in binding_inputs:
        binding_inputs[bkey]["type"].currentTextChanged.connect(_check_popup_visibility)
    _check_popup_visibility()
    right_layout.addStretch()

    btn_row = QHBoxLayout()
    btn_save = QPushButton("SAVE"); btn_save.setObjectName("btn_save")
    btn_delete = QPushButton("DELETE"); btn_delete.setObjectName("btn_delete")
    btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
    btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
    btn_row.addWidget(btn_save); btn_row.addWidget(btn_delete)
    root_layout.addLayout(btn_row)

    def save():
        item_cfg["id"] = id_le.text()
        item_cfg["fg"] = _temp_colors["fg"]
        item_cfg["bg"] = _temp_colors["bg"]
        item_cfg["border_color"] = _temp_colors["border_color"]
        item_cfg["text"] = text_le.text()
        try:
            item_cfg["font"] = [font_family_cb.currentText(), int(font_size_le.text()), font_weight_cb.currentText()]
        except ValueError: pass
        try: item_cfg["border"] = int(border_px_le.text())
        except ValueError: pass
        try: item_cfg["border_radius"] = int(border_radius_le.text())
        except ValueError: pass
        try: item_cfg["width"]  = int(width_le.text())
        except ValueError: pass
        try: item_cfg["height"] = int(height_le.text())
        except ValueError: pass
        try: item_cfg["padx_left"]  = int(padx_left_le.text())
        except ValueError: pass
        try: item_cfg["padx_right"] = int(padx_right_le.text())
        except ValueError: pass
        try: item_cfg["pady_top"]  = int(pady_top_le.text())
        except ValueError: pass
        try: item_cfg["pady_bottom"] = int(pady_bottom_le.text())
        except ValueError: pass
        try: item_cfg["margin_left"]  = int(margin_left_le.text())
        except ValueError: pass
        try: item_cfg["margin_right"] = int(margin_right_le.text())
        except ValueError: pass
        try: item_cfg["margin_top"]  = int(margin_top_le.text())
        except ValueError: pass
        try: item_cfg["margin_bottom"] = int(margin_bottom_le.text())
        except ValueError: pass

        item_cfg["icon_path"] = icon_path_le.text()
        item_cfg["nf_char"]   = nf_char_le.text()
        try: item_cfg["icon_width"]  = int(icon_w_le.text())
        except ValueError: pass
        try: item_cfg["icon_height"] = int(icon_h_le.text())
        except ValueError: pass
        try: item_cfg["icon_gap"]    = int(icon_gap_le.text())
        except ValueError: pass
        item_cfg["icon_position"] = icon_pos_cb.currentText()

        new_bindings = {}
        for bkey, inputs in binding_inputs.items():
            cmd = inputs["cmd"].text()
            if not cmd: continue
            b_type = inputs["type"].currentText()
            new_bindings[bkey] = {"type": b_type, "hide": inputs["hide"].isChecked(), "admin": inputs["admin"].isChecked()}
            if b_type == "function": new_bindings[bkey]["func"] = cmd
            else:                    new_bindings[bkey]["cmd"]  = cmd
            if b_type == "popup":
                try: new_bindings[bkey]["row_limit"] = int(row_limit_le.text())
                except: new_bindings[bkey]["row_limit"] = 10
                new_bindings[bkey]["bg_color"] = _temp_colors["pop_bg"]
                new_bindings[bkey]["transparent_bg"] = pop_trans_chk.isChecked()
                new_bindings[bkey]["border_color"] = _temp_colors["pop_border"]
                try: new_bindings[bkey]["border_px"] = int(pop_border_px_le.text())
                except: new_bindings[bkey]["border_px"] = 1
        item_cfg["bindings"] = new_bindings
        new_category = group_le.text()
        try:
            # Convert 1-based GUI index back to 0-based list index
            new_index = max(0, int(index_le.text()) - 1)
        except ValueError:
            new_index = None
        
        config = load_config()
        # 1. Remove from old category/position first
        if category != new_category and category in config and isinstance(config[category], list) and index is not None:
            if 0 <= index < len(config[category]): config[category].pop(index)
        
        target = config.get(new_category, [])
        if not isinstance(target, list) and new_category not in ["static_bindings"]: target = []
        
        if isinstance(target, list):
            # 2. If moving within same category, remove old position first
            if category == new_category and index is not None and 0 <= index < len(target):
                target.pop(index)
            
            # 3. Insert at new 0-based position
            if new_index is not None:
                # Clamp to list bounds
                insert_pos = min(new_index, len(target))
                target.insert(insert_pos, item_cfg)
            else:
                target.append(item_cfg)
            config[new_category] = target
        else:
            if new_category == "static_bindings":
                flat = {k: v for k, v in item_cfg.items() if k != "bindings"}
                flat.update(item_cfg.get("bindings", {}))
                config[new_category][item_cfg["id"]] = flat
            else: config[new_category][item_cfg["id"]] = item_cfg
        save_config(config)
        r = QMessageBox.question(dlg, "Restart", "Settings saved. Restart GUI to apply?",
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        dlg.accept()
        if r == QMessageBox.StandardButton.Yes: _app_restart()

    def delete():
        r = QMessageBox.question(dlg, "Delete", f"Delete '{item_cfg.get('id', 'this item')}'?",
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if r != QMessageBox.StandardButton.Yes: return
        config = load_config()
        if category in config:
            if isinstance(config[category], list):
                if index is not None and 0 <= index < len(config[category]): config[category].pop(index)
                else:
                    item_id = item_cfg.get("id")
                    config[category] = [i for i in config[category] if i.get("id") != item_id]
            else:
                item_id = item_cfg.get("id")
                if item_id in config[category]: del config[category][item_id]
        save_config(config)
        r = QMessageBox.question(dlg, "Restart", "Item deleted. Restart GUI to apply?",
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        dlg.accept()
        if r == QMessageBox.StandardButton.Yes: _app_restart()

    btn_save.clicked.connect(save); btn_delete.clicked.connect(delete); dlg.show()


# ─── Rclone settings dialog ───────────────────────────────────────────────────
def open_rclone_settings():
    dlg = QDialog()
    dlg.setWindowTitle("Rclone Settings")
    dlg.resize(380, 200)
    dlg.setStyleSheet(DIALOG_QSS)
    layout = QVBoxLayout(dlg); layout.setContentsMargins(14, 14, 14, 14); layout.setSpacing(10)
    title = QLabel("// RCLONE SETTINGS")
    title.setStyleSheet(f"color: {CP_CYAN}; font-size: 15pt; font-weight: bold;")
    layout.addWidget(title)
    grp = QGroupBox("CHECK BEHAVIOUR"); form = QFormLayout(); form.setSpacing(8); grp.setLayout(form)
    cfg_now = load_config().get("rclone_settings", {"interval_min": 10, "simultaneous": True})
    interval_le = QLineEdit(str(cfg_now.get("interval_min", 10)))
    simul_chk = QCheckBox("Run simultaneously"); simul_chk.setChecked(bool(cfg_now.get("simultaneous", True)))
    form.addRow("INTERVAL (min)", interval_le); form.addRow("", simul_chk)
    layout.addWidget(grp)
    btn_save = QPushButton("SAVE"); btn_save.setObjectName("btn_save")
    btn_save.setCursor(Qt.CursorShape.PointingHandCursor); layout.addWidget(btn_save)
    def save():
        try: mins = int(interval_le.text())
        except ValueError: mins = 10
        config = load_config()
        config["rclone_settings"] = {"interval_min": mins, "simultaneous": simul_chk.isChecked()}
        save_config(config)
        dlg.accept()
    btn_save.clicked.connect(save); dlg.show()


# ─── Generic Popup Bar ────────────────────────────────────────────────────────
_active_popups = []

def close_all_popups():
    global _active_popups
    # Close in reverse order (children first)
    while _active_popups:
        p = _active_popups.pop()
        try:
            p.setParent(None)
            p.close()
        except: pass

class AppEventFilter(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            if _active_popups:
                pos = event.globalPosition().toPoint()
                # 1. If click is inside any active popup, keep them open
                in_popup = any(p.isVisible() and p.geometry().contains(pos) for p in _active_popups)
                if not in_popup:
                    # 2. Check if click is anywhere on our status bar or existing popups
                    w = QApplication.widgetAt(pos)
                    # We look for ANY widget that belongs to our UI system
                    if not (w and (w.window() == _main_window or isinstance(w.window(), GenericPopup))):
                        close_all_popups()
        elif event.type() == QEvent.Type.ApplicationDeactivate:
            close_all_popups()
        return False

class GenericPopup(QFrame):
    def __init__(self, parent, category, anchor_widget, row_limit=10, border_color=None, border_px=1, bg_color=None, transparent_bg=False):
        super().__init__(parent, Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        if transparent_bg:
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.category = category
        self.anchor_widget = anchor_widget
        self.row_limit = max(1, row_limit)
        bc = border_color or CP_RED
        bg = "transparent" if transparent_bg else (bg_color or "#1d2027")
        bpx = int(border_px)
        self.setStyleSheet(f"QFrame {{ background: {bg}; border: {bpx}px solid {bc}; }} QLabel {{ border: none; background: transparent; }}")
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(4, 2, 4, 2)
        self.layout.setSpacing(4)
        _active_popups.append(self)
        self.render_items()

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, painter, self)
        super().paintEvent(event)

    def closeEvent(self, event):
        if self in _active_popups:
            _active_popups.remove(self)
        super().closeEvent(event)

    def render_items(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        config = load_config()
        items = config.get(self.category, [])
        row, col = 0, 0
        for idx, cfg in enumerate(items):
            w = create_dynamic_button(None, cfg, self.category, idx)
            self.layout.addWidget(w, row, col)
            col += 1
            if col >= self.row_limit: col = 0; row += 1
        _add_st_cfg = config.get("static_bindings", {}).get("add_button", {})
        add_bt = IconLabel(_add_st_cfg.get("text", "+"), _add_st_cfg)
        if _add_st_cfg: _apply_static_style(add_bt, "add_button")
        else: add_bt.setStyleSheet(f"color: {CP_GREEN}; font-family: 'JetBrainsMono NFP'; font-size: 18pt; font-weight: bold; padding: 0 5px;")
        add_bt.setCursor(Qt.CursorShape.PointingHandCursor)
        _new_cfg = {"text": "SUB", "fg": "#ffffff", "bg": CP_BG, "id": f"sub_{int(time.time())}", "bindings": {}}
        def _add_click(e, cat=self.category, cfg=_new_cfg):
            if e.modifiers() & Qt.KeyboardModifier.ShiftModifier: _open_static_edit("add_button")
            else: open_edit_gui(cfg, cat)
        add_bt.mousePressEvent = _add_click
        self.layout.addWidget(add_bt, row, col)
        self.adjustSize()

def open_popup_bar(category, anchor_widget, row_limit=10, border_color=None, border_px=1, bg_color=None, transparent_bg=False):
    # Identify which popup this button belongs to
    parent_popup = None
    curr = anchor_widget.parent()
    while curr:
        if isinstance(curr, GenericPopup):
            parent_popup = curr; break
        curr = curr.parent()

    # Toggle Check: If this exact popup is already active in the chain
    for i, p in enumerate(_active_popups):
        if p.category == category and p.anchor_widget == anchor_widget:
            # Close this popup and all its children
            while len(_active_popups) > i:
                _active_popups.pop().close()
            return

    # Sibling switching / Hierarchy management
    if not parent_popup:
        close_all_popups() # Fresh start from StatusBar trigger
    else:
        # Close everything opened AFTER the popup that contains this button
        # This ensures that clicking "Radarr" closes "Sonarr" if they share the same parent
        try:
            idx = _active_popups.index(parent_popup)
            while len(_active_popups) > idx + 1:
                _active_popups.pop().close()
        except ValueError:
            close_all_popups()

    config = load_config()
    offset = int(config.get("popup_y_offset", 2))
    popup = GenericPopup(_main_window, category, anchor_widget, row_limit, border_color, border_px, bg_color, transparent_bg)
    gpos = anchor_widget.mapToGlobal(anchor_widget.rect().topLeft())
    cx = gpos.x() + anchor_widget.width() // 2 - popup.width() // 2
    popup.move(cx, gpos.y() - popup.height() - offset)
    popup.show()
    popup.setFocus()

# ─── Dynamic button factory ───────────────────────────────────────────────────
def create_dynamic_button(parent_layout, btn_cfg, category, index=None):
    _fg   = btn_cfg.get("fg", "") or "white"
    _bg   = btn_cfg.get("bg", "") or CP_BG
    text  = btn_cfg.get("text", "")
    font_cfg = btn_cfg.get("font", get_default_font())
    px_l  = int(btn_cfg.get("padx_left", 1))
    px_r  = int(btn_cfg.get("padx_right", 1))
    py_t  = int(btn_cfg.get("pady_top", 0))
    py_b  = int(btn_cfg.get("pady_bottom", 0))
    m_l   = int(btn_cfg.get("margin_left", 0))
    m_r   = int(btn_cfg.get("margin_right", 0))
    m_t   = int(btn_cfg.get("margin_top", 0))
    m_b   = int(btn_cfg.get("margin_bottom", 0))
    
    lbl = IconLabel(text, btn_cfg)
    bw, bh = btn_cfg.get("width", 0), btn_cfg.get("height", 0)
    if bw > 0: lbl.setFixedWidth(bw)
    if bh > 0: lbl.setFixedHeight(bh)
    fsize, fweight = font_cfg[1] if len(font_cfg) > 1 else 16, font_cfg[2] if len(font_cfg) > 2 else "bold"
    _border_px = int(btn_cfg.get("border", 0))
    _border_col = btn_cfg.get("border_color", "") or _bg
    _border_radius = int(btn_cfg.get("border_radius", 0))
    _border_css = f"border: {_border_px}px solid {_border_col};" if _border_px else "border: none;"
    lbl.setStyleSheet(f"color: {_fg}; background: {_bg}; font-family: '{font_cfg[0]}'; font-size: {fsize}pt; font-weight: {fweight}; {_border_css} border-radius: {_border_radius}px; margin-left: {m_l}px; margin-right: {m_r}px; margin-top: {m_t}px; margin-bottom: {m_b}px;")
    lbl.setContentsMargins(px_l, py_t, px_r, py_b)
    bindings = btn_cfg.get("bindings", {})
    
    def mousePressEvent(event):
        event.accept()

    def mouseReleaseEvent(event, _bindings=bindings, _cfg=btn_cfg, _cat=category, _idx=index, _lbl=lbl):
        if not _lbl.rect().contains(event.pos()): return
        mods, btn = event.modifiers(), event.button()
        if mods & Qt.KeyboardModifier.ShiftModifier: open_edit_gui(_cfg, _cat, _idx); return
        bkey = None
        if btn == Qt.MouseButton.LeftButton: bkey = "Control-Button-1" if mods & Qt.KeyboardModifier.ControlModifier else "Button-1"
        elif btn == Qt.MouseButton.RightButton: bkey = "Control-Button-3" if mods & Qt.KeyboardModifier.ControlModifier else "Button-3"
        if bkey and bkey in _bindings:
            action = _bindings[bkey]
            if action.get("type") == "popup": open_popup_bar(action.get("cmd", "popup_bar"), _lbl, action.get("row_limit", 10), action.get("border_color"), action.get("border_px", 1), action.get("bg_color"), action.get("transparent_bg", False))
            else: handle_action(action)
    
    lbl.mousePressEvent = mousePressEvent
    lbl.mouseReleaseEvent = mouseReleaseEvent
    if parent_layout is not None: parent_layout.addWidget(lbl)
    return lbl


# ─── Static binding helpers ───────────────────────────────────────────────────
def _open_static_edit(key):
    cfg = load_config()
    sb = cfg.get("static_bindings", {})
    entry = sb.get(key, {})
    _binding_keys = {k: v for k, v in entry.items() if "Button" in k}
    item = {"id": key, "text": key, "fg": entry.get("fg", ""), "bg": entry.get("bg", ""), "font": entry.get("font", get_default_font()), "border": entry.get("border", 0), "border_color": entry.get("border_color", ""), "border_radius": entry.get("border_radius", 0), "width": entry.get("width", 0), "height": entry.get("height", 0), "padx_left": entry.get("padx_left", 0), "padx_right": entry.get("padx_right", 0), "pady_top": entry.get("pady_top", 0), "pady_bottom": entry.get("pady_bottom", 0), "margin_left": entry.get("margin_left", 0), "margin_right": entry.get("margin_right", 0), "margin_top": entry.get("margin_top", 0), "margin_bottom": entry.get("margin_bottom", 0), "icon_path": entry.get("icon_path", ""), "nf_char": entry.get("nf_char", ""), "svg_content": entry.get("svg_content", ""), "svg_hover_map": entry.get("svg_hover_map", {}), "icon_width": entry.get("icon_width", 0), "icon_height": entry.get("icon_height", 0), "icon_gap": entry.get("icon_gap", 4), "icon_position": entry.get("icon_position", "left"), "bindings": _binding_keys}
    open_edit_gui(item, "static_bindings")

def _apply_static_style(widget, key):
    cfg = load_config().get("static_bindings", {}).get(key, {})
    if not cfg: return
    if isinstance(widget, IconLabel): widget.btn_cfg = cfg
    fg, bg = cfg.get("fg", "") or "white", cfg.get("bg", "") or "transparent"
    font = cfg.get("font", get_default_font())
    border_px, border_radius = int(cfg.get("border", 0)), int(cfg.get("border_radius", 0))
    border_col = cfg.get("border_color", "") or bg
    border_css = f"border: {border_px}px solid {border_col};" if border_px else "border: none;"
    px_l, px_r = int(cfg.get("padx_left", 0)), int(cfg.get("padx_right", 0))
    py_t, py_b = int(cfg.get("pady_top", 0)), int(cfg.get("pady_bottom", 0))
    m_l, m_r = int(cfg.get("margin_left", 0)), int(cfg.get("margin_right", 0))
    m_t, m_b = int(cfg.get("margin_top", 0)), int(cfg.get("margin_bottom", 0))
    bw, bh = cfg.get("width", 0), cfg.get("height", 0)
    if bw > 0: widget.setFixedWidth(bw)
    if bh > 0: widget.setFixedHeight(bh)
    fw = font[2] if len(font) > 2 else "bold"
    widget.setStyleSheet(f"color: {fg}; background: {bg}; font-family: '{font[0]}'; font-size: {font[1] if len(font)>1 else 16}pt; font-weight: {fw}; {border_css} border-radius: {border_radius}px; padding-left: {px_l}px; padding-right: {px_r}px; padding-top: {py_t}px; padding-bottom: {py_b}px; margin-left: {m_l}px; margin-right: {m_r}px; margin-top: {m_t}px; margin-bottom: {m_b}px;")

def _bind_static(lbl, key, default_cmd):
    cfg = load_config().get("static_bindings", {}).get(key, {"Button-1": {"type": "subprocess", "cmd": default_cmd}})
    
    def mousePressEvent(event):
        event.accept()

    def mouseReleaseEvent(event, _cfg=cfg, _key=key, _lbl=lbl):
        if not _lbl.rect().contains(event.pos()): return
        mods, btn = event.modifiers(), event.button()
        if mods & Qt.KeyboardModifier.ShiftModifier: _open_static_edit(_key); return
        bkey = None
        if btn == Qt.MouseButton.LeftButton: bkey = "Control-Button-1" if mods & Qt.KeyboardModifier.ControlModifier else "Button-1"
        elif btn == Qt.MouseButton.RightButton: bkey = "Control-Button-3" if mods & Qt.KeyboardModifier.ControlModifier else "Button-3"
        if bkey and bkey in _cfg: handle_action(_cfg[bkey])
    
    lbl.mousePressEvent = mousePressEvent
    lbl.mouseReleaseEvent = mouseReleaseEvent
    lbl.setCursor(Qt.CursorShape.PointingHandCursor); _apply_static_style(lbl, key)


# ─── CPU core bar widget ──────────────────────────────────────────────────────
BAR_WIDTH, BAR_HEIGHT = 8, 25
def _determine_bar_color(usage):
    if usage >= 90: return QColor("#8B0000")
    if usage >= 80: return QColor("#f12c2f")
    if usage >= 50: return QColor("#ff9282")
    return QColor("#14bcff")

class CpuCoreFrame(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._usages = psutil.cpu_percent(percpu=True)
        self.setFixedSize(len(self._usages) * (BAR_WIDTH + 2) + 4, BAR_HEIGHT + 4)
    def update_usages(self, usages): self._usages = usages; self.update()
    def paintEvent(self, event):
        painter = QPainter(self); painter.fillRect(self.rect(), QColor("#333333"))
        for i, usage in enumerate(self._usages):
            bar_h, color = int((usage / 100) * (BAR_HEIGHT / 2)), _determine_bar_color(usage)
            painter.fillRect(2 + i * (BAR_WIDTH + 2), 2 + (BAR_HEIGHT // 2) - bar_h, BAR_WIDTH, bar_h * 2, color)


# ─── Git status ───────────────────────────────────────────────────────────────
_git_queue = Queue()
def check_git_status(repo, q):
    if not os.path.exists(repo["path"]): q.put((repo["name"], repo["label"], "#000000")); return
    result = subprocess.run(["git", "status"], capture_output=True, text=True, cwd=repo["path"])
    color = "#00ff21" if "nothing to commit, working tree clean" in result.stdout else "#fe1616"
    q.put((repo["name"], repo["label"], color))

def _git_status_loop(repos, q):
    while True:
        for repo in repos: check_git_status(repo, q)
        time.sleep(5)

def git_backup(repos):
    commands = " ; ".join([f"{r['path']}\\scripts\\Github\\{r['name']}u.ps1" for r in repos])
    subprocess.Popen(["Start", "pwsh", "-NoExit", "-Command", f"& {{$host.UI.RawUI.WindowTitle='GiTSync' ; {commands} ; cd ~}}"], shell=True)

def delete_git_lock_files(repos):
    for repo in repos:
        lock_file = os.path.join(repo["path"], ".git", "index.lock")
        try:
            if os.path.exists(lock_file): os.remove(lock_file); print(f"Deleted: {lock_file}")
        except Exception as e: print(f"Error deleting {lock_file}: {e}")

def apply_git_style(lbl, cfg):
    fg, bg = cfg.get("fg", "") or "white", cfg.get("bg", "") or "transparent"
    font = cfg.get("font", get_default_font())
    bw, bh = cfg.get("width", 0), cfg.get("height", 0)
    if bw > 0: lbl.setFixedWidth(bw)
    if bh > 0: lbl.setFixedHeight(bh)
    fw = font[2] if len(font) > 2 else "bold"
    lbl.setStyleSheet(f"color: {fg}; background: {bg}; font-family: '{font[0]}'; font-size: {font[1] if len(font)>1 else 15}pt; font-weight: {fw}; border: none; background: transparent;")


# ─── Rclone ───────────────────────────────────────────────────────────────────
LOG_DIR = r"C:\Users\nahid\script_output\rclone"
os.makedirs(LOG_DIR, exist_ok=True)
rclone_status = {}
def _update_toggle_color_cb(toggle_lbl):
    if not rclone_status: return
    agg = CP_GREEN if all(c == CP_GREEN for c in rclone_status.values()) else CP_RED
    ss = toggle_lbl.styleSheet()
    if ss:
        new_ss = re.sub(r'color\s*:[^;]+;', f'color: {agg};', ss)
        if new_ss == ss: new_ss = ss.rstrip(';') + f'; color: {agg};'
        toggle_lbl.setStyleSheet(new_ss)
    else: toggle_lbl.setStyleSheet(f"color: {agg}; font-family: 'JetBrainsMono NFP'; font-size: 20pt; font-weight: bold;")

def check_and_update_rclone(cfg, toggle_lbl):
    def run():
        actual_cmd = cfg["cmd"].replace("src", cfg["src"]).replace("dst", cfg["dst"])
        with open(cfg["log"], "w") as f: subprocess.run(actual_cmd, shell=True, stdout=f, stderr=f)
        with open(cfg["log"], "r", encoding="utf-8", errors="ignore") as f: content = f.read()
        rclone_status[cfg.get("id", cfg["label"])] = CP_GREEN if "ERROR" not in content else CP_RED
        if _rclone_sig: _rclone_sig.update.emit(toggle_lbl, "")
        interval_ms = int(load_config().get("rclone_settings", {}).get("interval_min", 10)) * 60000
        QTimer.singleShot(interval_ms, lambda: check_and_update_rclone(cfg, toggle_lbl))
    threading.Thread(target=run, daemon=True).start()


# ─── Alarm / Timer ────────────────────────────────────────────────────────────
class TimerInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setStyleSheet(DIALOG_QSS)
        self.setFixedWidth(200)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8,8,8,8)
        lbl = QLabel("// SET MINUTES")
        lbl.setStyleSheet(f"color: {CP_CYAN}; font-weight: bold;")
        lay.addWidget(lbl)
        self.le = QLineEdit("1")
        self.le.setFocus()
        lay.addWidget(self.le)
        btn = QPushButton("START")
        btn.clicked.connect(self.accept)
        lay.addWidget(btn)
        self.le.returnPressed.connect(self.accept)

    def value(self):
        try: return float(self.le.text())
        except: return 0

class AlarmNotification(QDialog):
    def __init__(self, message="ALARM! TIME'S UP!"):
        super().__init__(None, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet(f"background-color: {CP_BG}; border: 5px solid {CP_RED};")
        self.resize(600, 300)
        layout = QVBoxLayout(self)
        self.lbl = QLabel(message)
        self.lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl.setStyleSheet(f"color: {CP_RED}; font-size: 36pt; font-weight: bold; border: none;")
        layout.addWidget(self.lbl)
        
        self.blink_timer = QTimer(self); self.blink_timer.timeout.connect(self._blink); self.blink_timer.start(500)
        self.state = True
        
        # Center on screen
        geo = QApplication.primaryScreen().geometry()
        self.move((geo.width() - 600) // 2, (geo.height() - 300) // 2)

    def _blink(self):
        self.state = not self.state
        color = CP_RED if self.state else CP_CYAN
        self.lbl.setStyleSheet(f"color: {color}; font-size: 36pt; font-weight: bold; border: none;")
        self.setStyleSheet(f"background-color: {CP_BG}; border: 5px solid {color};")

    def mousePressEvent(self, event):
        self.accept()

# ─── Main window ──────────────────────────────────────────────────────────────
class StatusBar(QMainWindow):
    def __init__(self):
        super().__init__()
        self._timer_active = False
        self._timer_seconds = 0
        self._last_timer_type = None # "alarm" or "shutdown"
        self._last_timer_mins = 0
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self._config = load_config()
        self._apply_geometry()
        border_frame = QFrame(); border_frame.setStyleSheet(f"QFrame {{ background: {CP_BG}; border: 1px solid {CP_RED}; }}")
        self.setCentralWidget(border_frame)
        inner = QWidget(border_frame); inner.setStyleSheet(f"background: {CP_BG}; border: none;")
        border_layout = QVBoxLayout(border_frame); border_layout.setContentsMargins(1, 1, 1, 1); border_layout.addWidget(inner)
        main_layout = QHBoxLayout(inner); main_layout.setContentsMargins(2, 1, 2, 1); main_layout.setSpacing(0)
        self._left_widget = QWidget(); self._left_layout = QHBoxLayout(self._left_widget); self._left_layout.setContentsMargins(0, 0, 0, 0); self._left_layout.setSpacing(0); self._left_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        main_layout.addWidget(self._left_widget, 1)
        self._right_widget = QWidget(); self._right_layout = QHBoxLayout(self._right_widget); self._right_layout.setContentsMargins(0, 0, 0, 0); self._right_layout.setSpacing(2); self._right_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        main_layout.addWidget(self._right_widget)
        self._build_left(); self._build_right(); self._apply_statusbar_style(); self._start_timers()

    def _apply_geometry(self):
        sb = self._config.get("statusbar", {})
        is_docked = sb.get("docked", False)
        hwnd = int(self.winId())
        
        screen_geo = QApplication.primaryScreen().geometry()
        sw = screen_geo.width()
        
        if is_docked:
            # AppBar docking (forced to top for stability)
            w, h = sw, int(sb.get("height", 39))
            self.setFixedSize(w, h)
            self.move(0, 0)
            register_appbar(hwnd)
            set_appbar_position(hwnd, w, h)
        else:
            unregister_appbar(hwnd)
            w, h = int(sb.get("width", 1920)), int(sb.get("height", 39))
            self.setFixedSize(w, h)
            x = sb.get("x", "center")
            if str(x).lower() == "center": x = (sw - w) // 2
            else: x = int(x)
            y = int(sb.get("y", 990))
            self.move(x, y)

    def closeEvent(self, event):
        unregister_appbar(int(self.winId()))
        super().closeEvent(event)

    def _build_left(self):
        ll = self._left_layout
        _uc = load_config().get("static_bindings", {}).get("uptime", {})
        self.uptime_label = IconLabel(format_uptime(), _uc)
        _ufg, _ufont_list = _uc.get("fg", "") or "#6bc0f8", _uc.get("font", get_default_font())
        self.uptime_label.setStyleSheet(f"color: {_ufg}; font-family: '{_ufont_list[0]}'; font-size: {_ufont_list[1]}pt; font-weight: {_ufont_list[2]};")
        
        def _uptime_release(event):
            if not self.uptime_label.rect().contains(event.pos()): return
            mods, btn = event.modifiers(), event.button()
            if mods & Qt.KeyboardModifier.ShiftModifier: _open_static_edit("uptime"); return
            
            if btn == Qt.MouseButton.LeftButton:
                subprocess.Popen("timedate.cpl", shell=True)
            elif btn == Qt.MouseButton.RightButton:
                self._show_timer_menu()
                
        self.uptime_label.mousePressEvent = lambda e: e.accept()
        self.uptime_label.mouseReleaseEvent = _uptime_release
        ll.addWidget(self.uptime_label)
        
        self._bl_page_size, self._bl_offset, self._bl_widgets = self._config.get("buttons_left_page_size", 10), 0, []
        prev_bt = IconLabel("«", {}); _apply_static_style(prev_bt, "pagination_prev"); prev_bt.mousePressEvent = lambda e: (_open_static_edit("pagination_prev") if e.modifiers() & Qt.KeyboardModifier.ShiftModifier else self._bl_prev()); ll.addWidget(prev_bt); self._bl_prev_bt = prev_bt
        self._bl_container = QWidget(); self._bl_container_layout = QHBoxLayout(self._bl_container); self._bl_container_layout.setContentsMargins(0, 0, 0, 0); self._bl_container_layout.setSpacing(0); ll.addWidget(self._bl_container)
        next_bt = IconLabel("»", {}); _apply_static_style(next_bt, "pagination_next"); next_bt.mousePressEvent = lambda e: (_open_static_edit("pagination_next") if e.modifiers() & Qt.KeyboardModifier.ShiftModifier else self._bl_next()); ll.addWidget(next_bt); self._bl_next_bt = next_bt
        self._bl_render()
        add_bt = IconLabel("+", {}); _apply_static_style(add_bt, "add_button"); add_bt.mousePressEvent = lambda e: (_open_static_edit("add_button") if e.modifiers() & Qt.KeyboardModifier.ShiftModifier else open_edit_gui({"text": "NEW", "fg": "#ffffff", "bg": CP_BG, "id": f"btn_{int(time.time())}", "bindings": {}}, "buttons_left")); ll.addWidget(add_bt)
        
        self._countdown_timer = QTimer(self); self._countdown_timer.timeout.connect(self._timer_tick)

    def _show_timer_menu(self):
        if self._timer_active:
            self._timer_active = False; self._countdown_timer.stop()
            self.uptime_label.setText(format_uptime()); return
            
        menu = QMenu(self); menu.setStyleSheet(DIALOG_QSS)
        a1 = menu.addAction("Countdown Alarm"); a2 = menu.addAction("Countdown Shutdown")
        if self._last_timer_type and self._last_timer_mins > 0:
            menu.addSeparator()
            a3 = menu.addAction(f"Rerun Last ({self._last_timer_mins}m {self._last_timer_type})")
        else: a3 = None
        
        action = menu.exec(self.uptime_label.mapToGlobal(QPoint(0, -menu.sizeHint().height())))
        if not action: return
        
        if action == a3:
            self._start_countdown(self._last_timer_type, self._last_timer_mins)
        else:
            mins, ok = QInputDialog.getDouble(self, "Timer", "Enter minutes:", 1, 0.1, 1440, 1)
            if ok: self._start_countdown("alarm" if action == a1 else "shutdown", mins)

    def _start_countdown(self, ttype, mins):
        self._timer_active = True; self._last_timer_type = ttype; self._last_timer_mins = mins
        self._timer_seconds = int(mins * 60)
        self._countdown_timer.start(1000); self._timer_tick()

    def _timer_tick(self):
        if not self._timer_active: return
        if self._timer_seconds <= 0:
            self._timer_active = False; self._countdown_timer.stop()
            self.uptime_label.setText(format_uptime())
            if self._last_timer_type == "alarm": AlarmNotification().exec()
            else: os.system("shutdown /s /f /t 1")
            return
        m, s = divmod(self._timer_seconds, 60)
        # Using the same icon or a simple [T] prefix for the countdown
        self.uptime_label.setText(f"\udb86\udee1 {m:02}:{s:02}")
        self._timer_seconds -= 1

    def _open_unified_settings(self):
        dlg = QDialog(self); dlg.setWindowTitle("Settings")
        sw, sh = self._config.get("settings_panel_width", 750), self._config.get("settings_panel_height", 500)
        dlg.resize(sw, sh)
        dlg.setStyleSheet(DIALOG_QSS)
        lay = QVBoxLayout(dlg); lay.setContentsMargins(12,12,12,12); lay.setSpacing(10); title = QLabel("// SETTINGS"); title.setStyleSheet(f"color: {CP_CYAN}; font-size: 15pt; font-weight: bold;"); lay.addWidget(title)
        
        # Scroll area for settings
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setStyleSheet("QScrollArea { border: none; }")
        scroll_w = QWidget(); scroll_lay = QVBoxLayout(scroll_w); scroll_lay.setContentsMargins(0,0,0,0); scroll_lay.setSpacing(10)
        scroll.setWidget(scroll_w); lay.addWidget(scroll)

        # Dual Panel Layout
        panels = QHBoxLayout(); panels.setSpacing(15); scroll_lay.addLayout(panels)
        left_col = QVBoxLayout(); left_col.setSpacing(10); panels.addLayout(left_col, 1)
        right_col = QVBoxLayout(); right_col.setSpacing(10); panels.addLayout(right_col, 1)

        # --- LEFT COLUMN ---
        grp1 = QGroupBox("BUTTON BAR"); form1 = QFormLayout(); grp1.setLayout(form1); size_le = QLineEdit(str(self._bl_page_size)); size_le.setFixedWidth(60); form1.addRow("VISIBLE BUTTONS", size_le); left_col.addWidget(grp1)

        grp_def = QGroupBox("NEW ITEM DEFAULTS"); form_def = QFormLayout(); grp_def.setLayout(form_def)
        dfont = self._config.get("default_font", ["JetBrainsMono NFP", 16, "bold"])
        df_family = QComboBox(); df_family.addItems(QFontDatabase.families()); df_family.setCurrentText(dfont[0])
        df_size = QLineEdit(str(dfont[1])); df_size.setFixedWidth(40)
        df_weight = QComboBox(); df_weight.addItems(["bold", "normal"]); df_weight.setCurrentText(dfont[2])
        form_def.addRow("FONT FAMILY", df_family)
        df_row = QWidget(); df_lay = QHBoxLayout(df_row); df_lay.setContentsMargins(0,0,0,0)
        df_lay.addWidget(df_size); df_lay.addWidget(QLabel("WT")); df_lay.addWidget(df_weight); df_lay.addStretch()
        form_def.addRow("SIZE / WT", df_row)
        left_col.addWidget(grp_def)
        
        grp2 = QGroupBox("RCLONE CHECKS"); form2 = QFormLayout(); grp2.setLayout(form2); rc = load_config().get("rclone_settings", {"interval_min": 10, "simultaneous": True}); interval_le, simul_chk = QLineEdit(str(rc.get("interval_min", 10))), QCheckBox("Run simultaneously"); interval_le.setFixedWidth(60); simul_chk.setChecked(bool(rc.get("simultaneous", True))); form2.addRow("INTERVAL (min)", interval_le); form2.addRow("", simul_chk); left_col.addWidget(grp2)

        grp_sw = QGroupBox("SETTINGS PANEL SIZE"); form_sw = QFormLayout(); grp_sw.setLayout(form_sw)
        sw_le, sh_le = QLineEdit(str(sw)), QLineEdit(str(sh))
        sw_le.setFixedWidth(60); sh_le.setFixedWidth(60)
        form_sw.addRow("WIDTH", sw_le)
        form_sw.addRow("HEIGHT", sh_le)
        left_col.addWidget(grp_sw)
        
        left_col.addStretch()

        # --- RIGHT COLUMN ---
        grp_edit = QGroupBox("EDIT PANEL SIZE"); form_edit = QFormLayout(); grp_edit.setLayout(form_edit)
        ew, eh = self._config.get("edit_panel_width", 1000), self._config.get("edit_panel_height", 700)
        ew_le, eh_le = QLineEdit(str(ew)), QLineEdit(str(eh))
        ew_le.setFixedWidth(60); eh_le.setFixedWidth(60)
        form_edit.addRow("WIDTH", ew_le)
        form_edit.addRow("HEIGHT", eh_le)
        
        lw = self._config.get("edit_left_weight", 1)
        rw = self._config.get("edit_right_weight", 2)
        lw_le, rw_le = QLineEdit(str(lw)), QLineEdit(str(rw))
        lw_le.setFixedWidth(40); rw_le.setFixedWidth(40)
        form_edit.addRow("LEFT WEIGHT", lw_le)
        form_edit.addRow("RIGHT WEIGHT", rw_le)
        right_col.addWidget(grp_edit)

        grp_sb = QGroupBox("STATUSBAR"); form_sb = QFormLayout(); grp_sb.setLayout(form_sb)
        _sb_cfg = self._config.get("statusbar", {})
        sb_bg_le, sb_border_le, sb_bpx_le = QLineEdit(_sb_cfg.get("bg", CP_BG)), QLineEdit(_sb_cfg.get("border_color", CP_RED)), QLineEdit(str(_sb_cfg.get("border_px", 1)))
        sb_w_le, sb_h_le = QLineEdit(str(_sb_cfg.get("width", 1920))), QLineEdit(str(_sb_cfg.get("height", 39)))
        sb_x_le, sb_y_le = QLineEdit(str(_sb_cfg.get("x", "center"))), QLineEdit(str(_sb_cfg.get("y", 990)))
        popup_y_le = QLineEdit(str(self._config.get("popup_y_offset", 2)))
        dock_chk = QCheckBox("DOCK (APPBAR)"); dock_chk.setChecked(_sb_cfg.get("docked", False))
        
        for le in [sb_bg_le, sb_border_le]: le.setFixedWidth(90)
        for le in [sb_bpx_le, sb_w_le, sb_h_le, sb_x_le, sb_y_le, popup_y_le]: le.setFixedWidth(70)

        form_sb.addRow("BG COLOR", sb_bg_le)
        form_sb.addRow("BORDER COLOR", sb_border_le)
        form_sb.addRow("BORDER PX", sb_bpx_le)
        
        geo_row = QWidget(); geo_lay = QHBoxLayout(geo_row); geo_lay.setContentsMargins(0,0,0,0)
        geo_lay.addWidget(QLabel("W")); geo_lay.addWidget(sb_w_le)
        geo_lay.addWidget(QLabel("H")); geo_lay.addWidget(sb_h_le); geo_lay.addStretch()
        form_sb.addRow("SIZE", geo_row)

        pos_row = QWidget(); pos_lay = QHBoxLayout(pos_row); pos_lay.setContentsMargins(0,0,0,0)
        pos_lay.addWidget(QLabel("X")); pos_lay.addWidget(sb_x_le)
        pos_lay.addWidget(QLabel("Y")); pos_lay.addWidget(sb_y_le); pos_lay.addStretch()
        form_sb.addRow("POSITION", pos_row)
        
        form_sb.addRow("POPUP Y OFFSET", popup_y_le)
        form_sb.addRow("", dock_chk)
        right_col.addWidget(grp_sb)
        right_col.addStretch()

        btn = QPushButton("SAVE"); btn.setObjectName("btn_save"); btn.setCursor(Qt.CursorShape.PointingHandCursor); lay.addWidget(btn)
        
        def _save():
            try:
                cfg = load_config()
                cfg["buttons_left_page_size"] = int(size_le.text())
                cfg["edit_panel_width"] = int(ew_le.text())
                cfg["edit_panel_height"] = int(eh_le.text())
                cfg["edit_left_weight"] = int(lw_le.text())
                cfg["edit_right_weight"] = int(rw_le.text())
                cfg["settings_panel_width"] = int(sw_le.text())
                cfg["settings_panel_height"] = int(sh_le.text())
                cfg["default_font"] = [df_family.currentText(), int(df_size.text()), df_weight.currentText()]
                cfg["rclone_settings"] = {"interval_min": int(interval_le.text()), "simultaneous": simul_chk.isChecked()}
                cfg["popup_y_offset"] = int(popup_y_le.text())
                
                # Statusbar Geo
                x_val = sb_x_le.text().strip()
                if x_val.lower() != "center":
                    try: x_val = int(x_val)
                    except: x_val = "center"
                
                cfg["statusbar"] = {
                    "bg": sb_bg_le.text() or CP_BG,
                    "border_color": sb_border_le.text() or CP_RED,
                    "border_px": int(sb_bpx_le.text()),
                    "width": int(sb_w_le.text()),
                    "height": int(sb_h_le.text()),
                    "x": x_val,
                    "y": int(sb_y_le.text()),
                    "docked": dock_chk.isChecked()
                }
                save_config(cfg); self._config = cfg; self._apply_statusbar_style(); self._apply_geometry(); dlg.accept(); self._bl_render()
            except ValueError as e:
                QMessageBox.warning(dlg, "Error", f"Invalid input: {e}")
        
        btn.clicked.connect(_save)
        
        # Center on screen
        screen_geo = QApplication.primaryScreen().availableGeometry()
        dlg.move(screen_geo.center().x() - dlg.width() // 2, screen_geo.center().y() - dlg.height() // 2)
        dlg.show()

    def _apply_statusbar_style(self):
        sb = self._config.get("statusbar", {}); bg, border_color, border_px = sb.get("bg", CP_BG) or CP_BG, sb.get("border_color", CP_RED) or CP_RED, int(sb.get("border_px", 1))
        self.setStyleSheet(GLOBAL_QSS + f"QMainWindow {{ border: {border_px}px solid {border_color}; }}")
        cf = self.centralWidget()
        if cf:
            cf.setStyleSheet(f"QFrame {{ background: {bg}; border: {border_px}px solid {border_color}; }}")
            inner = cf.layout().itemAt(0).widget() if cf.layout() and cf.layout().count() else None
            if inner: inner.setStyleSheet(f"background: {bg}; border: none;")
        for w in [self._left_widget, self._right_widget, self._bl_container]:
            if hasattr(w, "setStyleSheet"): w.setStyleSheet(f"background: {bg};")

    def _bl_render(self):
        while self._bl_container_layout.count():
            item = self._bl_container_layout.takeAt(0)
            if item.widget(): item.widget().setParent(None)
        self._bl_widgets.clear()
        config, items = load_config(), load_config().get("buttons_left", [])
        start, end = self._bl_offset, min(self._bl_offset + self._bl_page_size, len(items))
        for idx in range(start, end):
            w = create_dynamic_button(self._bl_container_layout, items[idx], "buttons_left", idx)
            w.setParent(self._bl_container); self._bl_widgets.append(w)
        _apply_static_style(self._bl_prev_bt, "pagination_prev"); _apply_static_style(self._bl_next_bt, "pagination_next")
        if self._bl_offset <= 0: self._bl_prev_bt.setStyleSheet(self._bl_prev_bt.styleSheet() + f" color: {CP_DIM};")
        if end >= len(items): self._bl_next_bt.setStyleSheet(self._bl_next_bt.styleSheet() + f" color: {CP_DIM};")

    def _bl_prev(self):
        if self._bl_offset > 0: self._bl_offset = max(0, self._bl_offset - self._bl_page_size); self._bl_render()
    def _bl_next(self):
        if self._bl_offset + self._bl_page_size < len(load_config().get("buttons_left", [])): self._bl_offset += self._bl_page_size; self._bl_render()

    def _build_git(self, ll):
        self._config = load_config(); repos = self._config.get("git_repos", []); self._git_labels = {}
        git_frame = QFrame(); git_frame.setStyleSheet(f"QFrame {{ border: 1px solid #888888; border-radius: 0px; background: transparent; }} QLabel {{ border: none; }}")
        git_row = QHBoxLayout(git_frame); git_row.setContentsMargins(4, 0, 4, 0); git_row.setSpacing(2); ll.addWidget(git_frame)
        bkup = QLabel("\udb80\udea2"); bkup.setStyleSheet(f"color: {CP_CYAN}; font-family: 'JetBrainsMono NFP'; font-size: 18pt; font-weight: bold;"); bkup.setCursor(Qt.CursorShape.PointingHandCursor); bkup.mousePressEvent = lambda e: git_backup(repos); git_row.addWidget(bkup)
        for idx, repo in enumerate(repos):
            lbl = IconLabel(repo["label"], repo); apply_git_style(lbl, repo); lbl.setContentsMargins(2, 0, 2, 0); p = repo["path"]
            def _make_click(path, _cfg, _idx):
                def click(event):
                    mods, btn = event.modifiers(), event.button()
                    if mods & Qt.KeyboardModifier.ShiftModifier: open_edit_gui(_cfg, "git_repos", _idx); return
                    if btn == Qt.MouseButton.LeftButton:
                        if mods & Qt.KeyboardModifier.ControlModifier: subprocess.Popen(f'explorer "{path}"', shell=True)
                        else: subprocess.Popen(["Start", "pwsh", "-NoExit", "-Command", f"& {{$host.UI.RawUI.WindowTitle='GiTSync' ; cd '{path}' ; gitter}}"], shell=True)
                    elif btn == Qt.MouseButton.RightButton:
                        if mods & Qt.KeyboardModifier.ControlModifier: subprocess.Popen(["Start", "pwsh", "-NoExit", "-Command", f"& {{$host.UI.RawUI.WindowTitle='Git Restore' ; cd '{path}' ; git restore . }}"], shell=True)
                        else: subprocess.Popen('start pwsh -NoExit -Command "lazygit"', cwd=path, shell=True)
                return click
            lbl.mousePressEvent = _make_click(p, repo, idx); git_row.addWidget(lbl); self._git_labels[repo["name"]] = lbl
        del_lbl = QLabel("\udb82\udde7"); del_lbl.setStyleSheet(f"color: white; font-family: 'JetBrainsMono NFP'; font-size: 18pt; font-weight: bold;"); del_lbl.setCursor(Qt.CursorShape.PointingHandCursor); del_lbl.mousePressEvent = lambda e: delete_git_lock_files(repos); git_row.addWidget(del_lbl)
        if repos: threading.Thread(target=_git_status_loop, args=(repos, _git_queue), daemon=True).start()

    def _toggle_rclone_popup(self):
        if self._rclone_popup and self._rclone_popup.isVisible(): self._rclone_popup.hide(); self._rclone_popup = None; return
        commands, popup = load_config().get("rclone_commands", {}), QFrame(self, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        popup.setStyleSheet(f"QFrame {{ background: #1d2027; border: 1px solid {CP_RED}; }} QLabel {{ border: none; background: transparent; }}")
        row = QHBoxLayout(popup); row.setContentsMargins(4, 2, 4, 2); row.setSpacing(4)
        for key, cfg in commands.items():
            if "id" not in cfg: cfg["id"] = key
            lbl = IconLabel(cfg["label"], cfg); _rid = cfg.get("id", cfg.get("label", key))
            cached = rclone_status.get(_rid); color = cached if cached else "white"
            lbl.setStyleSheet(f"color: {color}; font-family: 'JetBrainsMono NFP'; font-size: 16pt; font-weight: bold;")
            def _make_rclone_click(c):
                def click(event):
                    mods = event.modifiers()
                    if mods & Qt.KeyboardModifier.ShiftModifier: open_edit_gui(c, "rclone_commands")
                    elif mods & Qt.KeyboardModifier.ControlModifier:
                        if event.button() == Qt.MouseButton.LeftButton:
                            action = c.get("bindings", {}).get("Control-Button-1", {"type": "run_command", "cmd": c.get("left_click_cmd", "")}).copy()
                            if "cmd" in action: action["cmd"] = action["cmd"].replace("src", f'"{c.get("src", "")}"').replace("dst", f'"{c.get("dst", "")}"')
                            handle_action(action)
                        elif event.button() == Qt.MouseButton.RightButton:
                            action = c.get("bindings", {}).get("Control-Button-3", {"type": "run_command", "cmd": c.get("right_click_cmd", "")}).copy()
                            if "cmd" in action: action["cmd"] = action["cmd"].replace("src", f'"{c.get("src", "")}"').replace("dst", f'"{c.get("dst", "")}"')
                            handle_action(action)
                    else:
                        try: subprocess.Popen(["powershell", "-NoExit", "-Command", f'edit "{c["log"]}"'], creationflags=subprocess.CREATE_NEW_CONSOLE)
                        except Exception as ex: print(f"Error opening log: {ex}")
                return click
            lbl.mousePressEvent = _make_rclone_click(cfg); row.addWidget(lbl)
        popup.adjustSize(); gpos = self._rclone_toggle.mapToGlobal(self._rclone_toggle.rect().topLeft()); cx = gpos.x() + self._rclone_toggle.width() // 2 - popup.width() // 2
        offset = int(load_config().get("popup_y_offset", 2)); popup.move(cx, gpos.y() - popup.height() - offset); popup.show(); self._rclone_popup = popup

    def _build_right(self):
        rl = self._right_layout
        self._rclone_popup = None; _rc_cfg = load_config().get("static_bindings", {}).get("rclone_toggle", {})
        self._rclone_toggle = IconLabel("\uef2c", _rc_cfg); _apply_static_style(self._rclone_toggle, "rclone_toggle")
        if not _rc_cfg: self._rclone_toggle.setStyleSheet("color: white; font-family: 'JetBrainsMono NFP'; font-size: 20pt; font-weight: bold;")
        self._rclone_toggle.mousePressEvent = lambda e: (self._toggle_rclone_popup() if not e.modifiers() & Qt.KeyboardModifier.ShiftModifier else _open_static_edit("rclone_toggle"))
        rl.addWidget(self._rclone_toggle); self._build_git(rl)
        
        self.download_lb = IconLabel("", load_config().get("static_bindings", {}).get("download", {})); _bind_static(self.download_lb, "download", "sniffnet"); rl.addWidget(self.download_lb)
        self.upload_lb = IconLabel("", load_config().get("static_bindings", {}).get("upload", {})); _bind_static(self.upload_lb, "upload", "sniffnet"); rl.addWidget(self.upload_lb)
        self.lb_cpu = IconLabel("", load_config().get("static_bindings", {}).get("cpu", {})); _bind_static(self.lb_cpu, "cpu", r"C:\@delta\ms1\scripts\process\process_viewer.py"); rl.addWidget(self.lb_cpu)
        self.cpu_core_frame = CpuCoreFrame(); rl.addWidget(self.cpu_core_frame)
        self.lb_gpu = IconLabel("", load_config().get("static_bindings", {}).get("gpu", {})); _bind_static(self.lb_gpu, "gpu", "start ms-settings:display"); rl.addWidget(self.lb_gpu)
        self.lb_ram = IconLabel("", load_config().get("static_bindings", {}).get("ram", {})); _bind_static(self.lb_ram, "ram", "taskmgr"); rl.addWidget(self.lb_ram)
        self.lb_duc = IconLabel("", load_config().get("static_bindings", {}).get("drive_c", {})); _bind_static(self.lb_duc, "drive_c", "explorer C:\\"); rl.addWidget(self.lb_duc)
        self.lb_dud = IconLabel("", load_config().get("static_bindings", {}).get("drive_d", {})); _bind_static(self.lb_dud, "drive_d", "explorer D:\\"); rl.addWidget(self.lb_dud)
        _st_cfg = load_config().get("static_bindings", {}).get("settings", {}); settings_bt = IconLabel("⚙", _st_cfg); _apply_static_style(settings_bt, "settings")
        if not _st_cfg: settings_bt.setStyleSheet(f"color: {CP_DIM}; font-size: 12pt; background: transparent;")
        settings_bt.mousePressEvent = lambda e: (self._open_unified_settings() if not e.modifiers() & Qt.KeyboardModifier.ShiftModifier else _open_static_edit("settings")); rl.addWidget(settings_bt)
        for idx, btn_cfg in enumerate(self._config.get("buttons_right", [])): create_dynamic_button(rl, btn_cfg, "buttons_right", idx)

    def _apply_uptime_style(self, color=None):
        _uc = load_config().get("static_bindings", {}).get("uptime", {})
        _ufg = color if color else (_uc.get("fg", "") or "#6bc0f8")
        _ufont_list = _uc.get("font", get_default_font())
        self.uptime_label.setStyleSheet(f"color: {_ufg}; font-family: '{_ufont_list[0]}'; font-size: {_ufont_list[1]}pt; font-weight: {_ufont_list[2]};")

    def _show_timer_menu(self):
        if self._timer_active:
            self._timer_active = False; self._countdown_timer.stop()
            self.uptime_label.setText(format_uptime()); self._apply_uptime_style(); return
            
        menu = QMenu(self); menu.setStyleSheet(DIALOG_QSS)
        a1 = menu.addAction("Countdown Alarm"); a2 = menu.addAction("Countdown Shutdown")
        if self._last_timer_type and self._last_timer_mins > 0:
            menu.addSeparator()
            a3 = menu.addAction(f"Rerun Last ({self._last_timer_mins}m {self._last_timer_type})")
        else: a3 = None
        
        action = menu.exec(self.uptime_label.mapToGlobal(QPoint(0, -menu.sizeHint().height())))
        if not action: return
        
        if action == a3:
            self._start_countdown(self._last_timer_type, self._last_timer_mins)
        else:
            dlg = TimerInputDialog(self)
            gpos = self.uptime_label.mapToGlobal(self.uptime_label.rect().topLeft())
            offset = int(load_config().get("popup_y_offset", 2))
            dlg.move(gpos.x() + self.uptime_label.width() // 2 - 100, gpos.y() - 100 - offset)
            if dlg.exec():
                mins = dlg.value()
                if mins > 0: self._start_countdown("alarm" if action == a1 else "shutdown", mins)

    def _start_countdown(self, ttype, mins):
        self._timer_active = True; self._last_timer_type = ttype; self._last_timer_mins = mins
        self._timer_seconds = int(mins * 60)
        self._countdown_timer.start(1000); self._timer_tick()

    def _timer_tick(self):
        if not self._timer_active: return
        if self._timer_seconds <= 0:
            self._timer_active = False; self._countdown_timer.stop()
            self.uptime_label.setText(format_uptime()); self._apply_uptime_style()
            if self._last_timer_type == "alarm": AlarmNotification().exec()
            else: os.system("shutdown /s /f /t 1")
            return
        m, s = divmod(self._timer_seconds, 60)
        self.uptime_label.setText(f"\udb86\udee1 {m:02}:{s:02}")
        color = CP_YELLOW if self._last_timer_type == "alarm" else CP_RED
        self._apply_uptime_style(color)
        self._timer_seconds -= 1

    def _start_timers(self):
        self._uptime_timer = QTimer(self); self._uptime_timer.timeout.connect(self._update_uptime); self._uptime_timer.start(1000)
        self._info_timer = QTimer(self); self._info_timer.timeout.connect(self._update_info); self._info_timer.start(1000)
        self._core_timer = QTimer(self); self._core_timer.timeout.connect(self._update_cores); self._core_timer.start(1000)
        self._git_timer = QTimer(self); self._git_timer.timeout.connect(self._drain_git_queue); self._git_timer.start(100)
        commands, rclone_cfg = self._config.get("rclone_commands", {}), self._config.get("rclone_settings", {"simultaneous": True})
        if rclone_cfg.get("simultaneous", True):
            for key, cfg in commands.items():
                if "id" not in cfg: cfg["id"] = key
                check_and_update_rclone(cfg, self._rclone_toggle)
        else:
            def _seq(rem):
                if not rem: return
                k, c = rem[0]
                if "id" not in c: c["id"] = k
                check_and_update_rclone(c, self._rclone_toggle); QTimer.singleShot(100, lambda: _seq(rem[1:]))
            _seq(list(commands.items()))

    def _update_uptime(self):
        if not self._timer_active: self.uptime_label.setText(format_uptime())
    def _update_info(self):
        cpu, ram = get_cpu_ram_info(); gpu = get_gpu_usage(); dc, dd = get_disk_info(); up, down = get_net_speed()
        self.lb_cpu.setText(f"{cpu}%"); self.lb_ram.setText(f"{ram}%"); self.lb_gpu.setText(f"{gpu}%"); self.lb_duc.setText(f"\uf0a0  {dc}%"); self.lb_dud.setText(f"\uf0a0  {dd}%"); self.upload_lb.setText(f" ▲ {up} "); self.download_lb.setText(f" ▼ {down} ")
        cpu_f, ram_f, dc_f, dd_f, up_f, dn_f = float(cpu), float(ram), float(dc), float(dd), float(up), float(down)
        self.lb_cpu.setStyleSheet(f"color: {'black' if cpu_f > 80 else '#1b8af1'}; background: {'#14bcff' if cpu_f > 80 else CP_BG}; font-family: 'JetBrainsMono NFP'; font-size: 10pt; font-weight: bold; border: 1px solid #1b8af1;")
        self.lb_ram.setStyleSheet(f"color: {'black' if ram_f > 80 else '#f08d0c'}; background: {'#ff934b' if ram_f > 80 else CP_BG}; font-family: 'JetBrainsMono NFP'; font-size: 10pt; font-weight: bold; border: 1px solid #f08d0c;")
        self.lb_duc.setStyleSheet(f"color: white; background: {'#f12c2f' if dc_f > 90 else '#044568'}; font-family: 'JetBrainsMono NFP'; font-size: 10pt; font-weight: bold; border: 1px solid #1b8af1;")
        self.lb_dud.setStyleSheet(f"color: white; background: {'#f12c2f' if dd_f > 90 else '#044568'}; font-family: 'JetBrainsMono NFP'; font-size: 10pt; font-weight: bold; border: 1px solid #1b8af1;")
        def _ns(v): return f"color: {'black' if v>=0.1 else 'white'}; background: {'#32AB32' if v>=1.0 else ('#67D567' if v>=0.5 else ('#A8E4A8' if v>=0.1 else 'black'))};"
        base = "font-family: 'JetBrainsMono NFP'; font-size: 10pt; font-weight: bold;"
        self.upload_lb.setStyleSheet(_ns(up_f) + base); self.download_lb.setStyleSheet(_ns(dn_f) + base)

    def _update_cores(self): self.cpu_core_frame.update_usages(psutil.cpu_percent(percpu=True))
    def _drain_git_queue(self):
        try:
            while True:
                name, text, color = _git_queue.get_nowait()
                if name in self._git_labels:
                    self._git_labels[name].setText(text)
                    font = get_default_font()
                    self._git_labels[name].setStyleSheet(f"color: {color}; font-family: '{font[0]}'; font-size: {font[1]}pt; font-weight: {font[2]};")
        except Empty: pass

# ─── Entry point ──────────────────────────────────────────────────────────────
_main_window = None
if __name__ == "__main__":
    app = QApplication(sys.argv); app.setQuitOnLastWindowClosed(False); _rclone_sig = _RcloneSignal(); _rclone_sig.update.connect(lambda lbl, _: _update_toggle_color_cb(lbl)); app.setStyleSheet(GLOBAL_QSS)
    _filter = AppEventFilter(); app.installEventFilter(_filter)
    window = StatusBar(); _main_window = window; window.show(); calculate_time_to_appear(start_time); sys.exit(app.exec())
