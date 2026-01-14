import sys
import os
import json
import subprocess
import threading
import time
import shutil
import tempfile
import psutil
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QFrame, QScrollArea, QGridLayout, 
                             QDialog, QLineEdit, QCheckBox, QComboBox, QColorDialog, 
                             QFileDialog, QMessageBox, QMenu, QTextEdit, QRadioButton,
                             QButtonGroup, QProgressBar)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QPoint, QMimeData, QSize
from PyQt6.QtGui import QFont, QColor, QMouseEvent, QFontDatabase, QAction, QDrag, QCursor, QIcon, QPainter, QLinearGradient

# Configuration
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "script_launcher_config.json")
DEFAULT_CONFIG = {
    "settings": {
        "columns": 5,
        "font_family": "JetBrainsMono NFP",
        "font_size": 10,
        "bg_color": "#1d2027",
        "border_color": "#fe1616",
        "accent_color": "#26b2f3",
        "success_color": "#00ff21",
        "danger_color": "#fe1616",
        "show_github": True,
        "show_rclone": True,
        "show_system_stats": True,
        "always_on_top": True
    },
    "scripts": [
        {"name": "Explorer", "path": "explorer.exe"},
        {"name": "Task Mgr", "path": "taskmgr.exe"}
    ],
    "github_repos": [
        {"name": "ms1", "path": r"C:\Users\nahid\ms\ms1"},
        {"name": "db", "path": r"C:\Users\nahid\ms\db"},
        {"name": "test", "path": r"C:\Users\nahid\ms\test"}
    ],
    "rclone_folders": [
        {
            "name": "ms1",
            "src": "C:/Users/nahid/ms/ms1/",
            "dst": "o0:/ms1/",
            "label": "ms1",
            "cmd": 'rclone check src dst --fast-list --size-only --exclude ".git/**" --exclude "__pycache__/**"',
            "left_click_cmd": "rclone sync src dst -P --fast-list --exclude \".git/**\" --exclude \"__pycache__/**\"  --log-level INFO",
            "right_click_cmd": "rclone sync dst src -P --fast-list"
        }
    ]
}

class SystemMonitorThread(QThread):
    stats_updated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.last_net_sent = psutil.net_io_counters().bytes_sent
        self.last_net_recv = psutil.net_io_counters().bytes_recv
        self.last_time = time.time()

    def run(self):
        while self.running:
            try:
                cpu_percent = psutil.cpu_percent(interval=None)
                cpu_cores = psutil.cpu_percent(interval=None, percpu=True)
                ram_percent = psutil.virtual_memory().percent
                
                try:
                    disk_c = psutil.disk_usage('C:').percent
                    disk_d = psutil.disk_usage('D:').percent if os.path.exists('D:') else 0
                except:
                    disk_c = disk_d = 0
                
                current_time = time.time()
                dt = current_time - self.last_time
                if dt <= 0: dt = 1
                
                net_io = psutil.net_io_counters()
                sent_speed = (net_io.bytes_sent - self.last_net_sent) / dt
                recv_speed = (net_io.bytes_recv - self.last_net_recv) / dt
                
                self.last_net_sent = net_io.bytes_sent
                self.last_net_recv = net_io.bytes_recv
                self.last_time = current_time
                
                self.stats_updated.emit({
                    "cpu": cpu_percent,
                    "ram": ram_percent,
                    "disk_c": disk_c,
                    "disk_d": disk_d,
                    "up": sent_speed,
                    "down": recv_speed
                })
            except Exception as e:
                print(f"Monitor error: {e}")
            
            time.sleep(1)

    def stop(self):
        self.running = False

class StatusMonitorThread(QThread):
    status_updated = pyqtSignal(dict)
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.running = True

    def run(self):
        while self.running:
            results = {"github": {}, "rclone": {}}
            
            # Check Github
            if self.config["settings"].get("show_github", True) and "github_repos" in self.config:
                for repo in self.config["github_repos"]:
                    path = repo["path"]
                    if os.path.exists(path):
                        try:
                            res = subprocess.run(["git", "status", "--porcelain"], cwd=path, capture_output=True, text=True, timeout=2)
                            results["github"][repo["name"]] = "#00ff21" if not res.stdout.strip() else "#fe1616"
                        except:
                            results["github"][repo["name"]] = "#555555"
                    else:
                        results["github"][repo["name"]] = "#555555"
            
            # Check Rclone
            if self.config["settings"].get("show_rclone", True) and "rclone_folders" in self.config:
                for folder in self.config["rclone_folders"]:
                    src = os.path.expandvars(folder.get("src", ""))
                    if src:
                        results["rclone"][folder["name"]] = "#26b2f3" if os.path.exists(src) else "#555555"
            
            self.status_updated.emit(results)
            time.sleep(5)

    def stop(self):
        self.running = False

class ScriptButton(QPushButton):
    def __init__(self, script, parent_app):
        super().__init__(script["name"])
        self.script = script
        self.parent_app = parent_app
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setAcceptDrops(True)
        self.update_style()
        
    def update_style(self, hover=False):
        is_folder = self.script.get("type") == "folder"
        settings = self.parent_app.config["settings"]
        
        # Colors
        default_bg = "#2b2f38" if not is_folder else "#1a1c23"
        bg = self.script.get("color", default_bg)
        h_bg = self.script.get("hover_color", settings["accent_color"])
        
        text_color = self.script.get("text_color", "white" if not is_folder else "#ffd700")
        h_text_color = self.script.get("hover_text_color", "white")
        
        border_width = self.script.get("border_width", 0)
        border_color = self.script.get("border_color", "#fe1616")
        radius = self.script.get("corner_radius", 4)
        
        # Font
        font_family = self.script.get("font_family", settings.get("font_family", "JetBrainsMono NFP"))
        font_size = self.script.get("font_size", settings.get("font_size", 10))
        weight = "bold" if self.script.get("is_bold", False) or is_folder else "normal"
        style = "italic" if self.script.get("is_italic", False) else "normal"
        
        current_bg = h_bg if hover else bg
        current_text = h_text_color if hover else text_color
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {current_bg};
                color: {current_text};
                border: {border_width}px solid {border_color};
                border-radius: {radius}px;
                font-family: '{font_family}';
                font-size: {font_size}px;
                font-weight: {weight};
                font-style: {style};
                padding: 5px;
            }}
        """)
        
        # Dimensions
        c_span = self.script.get("col_span", 1)
        r_span = self.script.get("row_span", 1)
        
        custom_w = self.script.get("width", 0)
        custom_h = self.script.get("height", 0)
        
        # Fixed sizes if specified
        if custom_w > 0: self.setFixedWidth(custom_w)
        if custom_h > 0: self.setFixedHeight(custom_h)

    def enterEvent(self, event):
        self.update_style(hover=True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.update_style(hover=False)
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.MouseButton.LeftButton:
            if (event.pos() - self.drag_start_pos).manhattanLength() > QApplication.startDragDistance():
                drag = QDrag(self)
                mime = QMimeData()
                # Store the index or name
                mime.setText(self.script["name"])
                drag.setMimeData(mime)
                
                # Visual feedback
                pixmap = self.grab()
                drag.setPixmap(pixmap)
                drag.setHotSpot(event.pos())
                
                drag.exec(Qt.DropAction.MoveAction)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.KeyboardModifier.ControlModifier:
                # Ctrl+Left Click
                if self.script.get("ctrl_left_cmd"):
                    temp = self.script.copy()
                    temp["path"] = self.script["ctrl_left_cmd"]
                    self.parent_app.launch_script(temp)
                else:
                    self.parent_app.handle_script_click(self.script)
            else:
                self.parent_app.handle_script_click(self.script)
        elif event.button() == Qt.MouseButton.RightButton:
            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.KeyboardModifier.ControlModifier:
                # Ctrl+Right Click
                if self.script.get("ctrl_right_cmd"):
                    temp = self.script.copy()
                    temp["path"] = self.script["ctrl_right_cmd"]
                    self.parent_app.launch_script(temp)
                else:
                    self.show_context_menu(event.globalPosition().toPoint())
            else:
                self.show_context_menu(event.globalPosition().toPoint())
        super().mouseReleaseEvent(event)

    def show_context_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: #2b2f38;
                color: white;
                border: 1px solid {self.parent_app.config["settings"]["accent_color"]};
            }}
            QMenu::item:selected {{
                background-color: {self.parent_app.config["settings"]["accent_color"]};
            }}
        """)
        
        edit_act = menu.addAction("Edit / Stylize")
        dup_act = menu.addAction("Duplicate")
        cut_act = menu.addAction("Cut")
        
        move_up_act = None
        if self.parent_app.view_stack:
            move_up_act = menu.addAction("Move Up / Out")
            
        menu.addSeparator()
        del_act = menu.addAction("Delete")
        
        action = menu.exec(pos)
        
        if action == edit_act:
            self.parent_app.open_edit_dialog(self.script)
        elif action == dup_act:
            self.parent_app.duplicate_script(self.script)
        elif action == cut_act:
            self.parent_app.cut_script(self.script)
        elif action == move_up_act and move_up_act:
            self.parent_app.move_script_out(self.script)
        elif action == del_act:
            self.parent_app.remove_script(self.script)

class ClickableLabel(QLabel):
    clicked = pyqtSignal(QMouseEvent)
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
    def mousePressEvent(self, event):
        self.clicked.emit(event)
        super().mousePressEvent(event)

class EditDialog(QDialog):
    def __init__(self, script, parent_app):
        super().__init__(parent_app)
        self.script = script
        self.parent_app = parent_app
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.color_map = {
            "color": self.script.get("color", "#2b2f38"),
            "text_color": self.script.get("text_color", "white"),
            "hover_color": self.script.get("hover_color", "#26b2f3"),
            "hover_text_color": self.script.get("hover_text_color", "white"),
            "border_color": self.script.get("border_color", "#fe1616")
        }
        self.init_ui()
        # Ensure geometry is updated before centering
        self.adjustSize()
        self.center_to_parent()
        
    def center_to_parent(self):
        if self.parent_app:
            p_geo = self.parent_app.geometry()
            # Calculate position to center the dialog over the parent
            target_x = p_geo.x() + (p_geo.width() - self.width()) // 2
            target_y = p_geo.y() + (p_geo.height() - self.height()) // 2
            self.move(target_x, target_y)

    def init_ui(self):
        self.setObjectName("EditDialog")
        # Fixed height to fit inside main window (650)
        self.setFixedSize(900 if self.script.get("type") != "folder" else 500, 600)
        accent = self.parent_app.config['settings']['accent_color']
        border = self.parent_app.config['settings']['border_color']
        
        self.setStyleSheet(f"""
            QDialog#EditDialog {{
                background-color: #1d2027;
                border: 2px solid {border};
                border-radius: 8px;
            }}
            QLabel {{
                color: #888888; 
                font-size: 10px;
                font-weight: bold;
                border: none;
                background: transparent;
                font-family: 'Segoe UI Semibold';
                text-transform: uppercase;
            }}
            QLineEdit, QComboBox, QTextEdit {{
                background-color: #252830;
                color: #ffffff;
                border: 1px solid #333;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', 'JetBrainsMono NFP';
                font-size: 12px;
            }}
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {{
                border: 1px solid {accent};
                background-color: #2b2f38;
            }}
            QCheckBox, QRadioButton {{
                color: #dddddd;
                border: none;
                spacing: 12px;
                font-size: 11px;
                font-family: 'Segoe UI';
            }}
            QCheckBox::indicator, QRadioButton::indicator {{
                width: 18px;
                height: 18px;
                background-color: #252830;
                border: 1px solid #444;
                border-radius: 3px;
            }}
            QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
                background-color: {accent};
                border: 1px solid {accent};
            }}
            QPushButton#SaveBtn {{
                background-color: #10b153;
                color: white;
                font-weight: bold;
                font-size: 13px;
                border: none;
                border-radius: 6px;
                letter-spacing: 2px;
            }}
            QPushButton#SaveBtn:hover {{
                background-color: #14d363;
            }}
            QPushButton#CloseBtn {{
                color: #555;
                border: none;
                font-size: 20px;
                background: transparent;
            }}
            QPushButton#CloseBtn:hover {{
                color: #ffffff;
                background-color: #fe1616;
                border-radius: 4px;
            }}
            QFrame#GroupFrame {{
                border: 1px solid #333;
                border-left: 3px solid {accent};
                border-radius: 4px;
                margin-top: 8px;
                background: rgba(255, 255, 255, 0.02);
            }}
            QPushButton#BrowseBtn {{
                background-color: #3a3f4b;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton#BrowseBtn:hover {{
                background-color: #4a4f5b;
            }}
            QPushButton#ColorBtn {{
                color: white;
                font-size: 10px;
                font-weight: bold;
                border-radius: 4px;
                border: 1px solid #444;
                padding: 10px;
                min-height: 25px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 25)
        layout.setSpacing(15)
        
        # Header
        header = QHBoxLayout()
        title_text = f"EDIT {self.script['type'].upper()}: {self.script['name'].upper()}"
        title = QLabel(title_text)
        title.setStyleSheet(f"color: {accent}; font-weight: bold; font-size: 18px; letter-spacing: 1px;")
        header.addWidget(title)
        
        header.addStretch()
        
        close_btn = QPushButton("✕")
        close_btn.setObjectName("CloseBtn")
        close_btn.setFixedSize(35, 35)
        close_btn.clicked.connect(self.reject)
        header.addWidget(close_btn)
        layout.addLayout(header)

        # Main Scrollable Content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        # Custom Scrollbar styling
        scroll.verticalScrollBar().setStyleSheet(f"""
            QScrollBar:vertical {{ border: none; background: transparent; width: 8px; }}
            QScrollBar::handle:vertical {{ background: {accent}; border-radius: 4px; min-height: 20px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
        """)
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        content_vlayout = QVBoxLayout(scroll_content)
        content_vlayout.setContentsMargins(0, 0, 5, 0)
        content_vlayout.setSpacing(15)

        # Outer horizontal layout for panels
        content_hlayout = QHBoxLayout()
        content_hlayout.setSpacing(20)
        
        # Left Panel (All Settings)
        left_panel = QVBoxLayout()
        left_panel.setSpacing(15)
        
        # Basic Info Group
        basic_group = QFrame()
        basic_group.setObjectName("GroupFrame")
        basic_layout = QGridLayout(basic_group)
        basic_layout.setContentsMargins(20, 20, 20, 20)
        basic_layout.setSpacing(12)
        
        basic_layout.addWidget(QLabel("LABEL NAME"), 0, 0)
        self.name_edit = QLineEdit(self.script["name"])
        basic_layout.addWidget(self.name_edit, 0, 1)
        
        if self.script.get("type") != "folder":
            basic_layout.addWidget(QLabel("SCRIPT PATH"), 1, 0)
            path_row = QHBoxLayout()
            self.path_edit = QLineEdit(self.script.get("path", ""))
            path_row.addWidget(self.path_edit)
            browse_btn = QPushButton("...")
            browse_btn.setObjectName("BrowseBtn")
            browse_btn.setFixedSize(40, 32)
            browse_btn.clicked.connect(self.browse_path)
            path_row.addWidget(browse_btn)
            basic_layout.addLayout(path_row, 1, 1)
            
            cb_layout = QHBoxLayout()
            cb_layout.setSpacing(25)
            self.hide_terminal = QCheckBox("HIDE TERMINAL")
            self.hide_terminal.setChecked(self.script.get("hide_terminal", False))
            cb_layout.addWidget(self.hide_terminal)
            
            self.no_exit = QCheckBox("NO EXIT")
            self.no_exit.setChecked(self.script.get("keep_open", False))
            cb_layout.addWidget(self.no_exit)
            
            self.kill_win = QCheckBox("KILL MAIN")
            self.kill_win.setChecked(self.script.get("kill_window", False))
            cb_layout.addWidget(self.kill_win)
            cb_layout.addStretch()
            basic_layout.addLayout(cb_layout, 2, 0, 1, 2)
            
            basic_layout.addWidget(QLabel("CTRL+L ACTION"), 3, 0)
            self.ctrl_l_edit = QLineEdit(self.script.get("ctrl_left_cmd", ""))
            basic_layout.addWidget(self.ctrl_l_edit, 3, 1)
            
            basic_layout.addWidget(QLabel("CTRL+R ACTION"), 4, 0)
            self.ctrl_r_edit = QLineEdit(self.script.get("ctrl_right_cmd", ""))
            basic_layout.addWidget(self.ctrl_r_edit, 4, 1)
        
        left_panel.addWidget(basic_group)
        
        # Typography Group
        typo_group = QFrame()
        typo_group.setObjectName("GroupFrame")
        typo_layout = QGridLayout(typo_group)
        typo_layout.setContentsMargins(20, 20, 20, 20)
        typo_layout.setSpacing(12)
        typo_layout.addWidget(QLabel("FONT FAMILY"), 0, 0)
        self.font_combo = QComboBox()
        self.font_combo.addItems(sorted(QFontDatabase.families()))
        self.font_combo.setCurrentText(self.script.get("font_family", self.parent_app.config["settings"]["font_family"]))
        typo_layout.addWidget(self.font_combo, 0, 1)
        
        typo_layout.addWidget(QLabel("FONT SIZE"), 1, 0)
        self.size_edit = QLineEdit(str(self.script.get("font_size", self.parent_app.config["settings"]["font_size"])))
        typo_layout.addWidget(self.size_edit, 1, 1)
        
        font_style_row = QHBoxLayout()
        self.is_bold = QCheckBox("BOLD")
        self.is_bold.setChecked(self.script.get("is_bold", False))
        font_style_row.addWidget(self.is_bold)
        self.is_italic = QCheckBox("ITALIC")
        self.is_italic.setChecked(self.script.get("is_italic", False))
        font_style_row.addWidget(self.is_italic)
        typo_layout.addLayout(font_style_row, 2, 0, 1, 2)
        left_panel.addWidget(typo_group)

        # Colors Group
        color_group = QFrame()
        color_group.setObjectName("GroupFrame")
        color_layout = QGridLayout(color_group)
        color_layout.setContentsMargins(20, 20, 20, 20)
        color_layout.setSpacing(15)
        
        self.btn_bg = self.create_color_btn("BUTTON BACKGROUND", "color")
        color_layout.addWidget(self.btn_bg, 0, 0)
        self.btn_text = self.create_color_btn("TEXT COLOR", "text_color")
        color_layout.addWidget(self.btn_text, 0, 1)
        self.btn_hv_bg = self.create_color_btn("HOVER BACKGROUND", "hover_color")
        color_layout.addWidget(self.btn_hv_bg, 1, 0)
        self.btn_hv_text = self.create_color_btn("HOVER TEXT COLOR", "hover_text_color")
        color_layout.addWidget(self.btn_hv_text, 1, 1)
        left_panel.addWidget(color_group)

        # Layout Dimensions Group
        dim_group = QFrame()
        dim_group.setObjectName("GroupFrame")
        dim_layout = QGridLayout(dim_group)
        dim_layout.setContentsMargins(20, 20, 20, 20)
        dim_layout.setSpacing(12)
        
        dim_layout.addWidget(QLabel("WIDTH"), 0, 0)
        self.width_edit = QLineEdit(str(self.script.get("width", 0)))
        dim_layout.addWidget(self.width_edit, 0, 1)
        dim_layout.addWidget(QLabel("HEIGHT"), 0, 2)
        self.height_edit = QLineEdit(str(self.script.get("height", 0)))
        dim_layout.addWidget(self.height_edit, 0, 3)
        
        dim_layout.addWidget(QLabel("COL SPAN"), 1, 0)
        self.cspan_edit = QLineEdit(str(self.script.get("col_span", 1)))
        dim_layout.addWidget(self.cspan_edit, 1, 1)
        dim_layout.addWidget(QLabel("ROW SPAN"), 1, 2)
        self.rspan_edit = QLineEdit(str(self.script.get("row_span", 1)))
        dim_layout.addWidget(self.rspan_edit, 1, 3)
        
        dim_layout.addWidget(QLabel("RADIUS"), 2, 0)
        self.radius_edit = QLineEdit(str(self.script.get("corner_radius", 4)))
        dim_layout.addWidget(self.radius_edit, 2, 1)
        dim_layout.addWidget(QLabel("BORDER"), 2, 2)
        self.bwidth_edit = QLineEdit(str(self.script.get("border_width", 0)))
        dim_layout.addWidget(self.bwidth_edit, 2, 3)
        
        self.btn_border = self.create_color_btn("BORDER COLOR", "border_color")
        dim_layout.addWidget(self.btn_border, 3, 0, 1, 4)
        left_panel.addWidget(dim_group)

        content_hlayout.addLayout(left_panel, 1)
        
        # Right Panel (Inline Script) - Only if not a folder
        if self.script.get("type") != "folder":
            right_panel = QVBoxLayout()
            right_panel.setSpacing(15)
            
            inline_group = QFrame()
            inline_group.setObjectName("GroupFrame")
            inline_layout = QVBoxLayout(inline_group)
            inline_layout.setContentsMargins(20, 20, 20, 20)
            inline_layout.setSpacing(15)
            
            inline_layout.addWidget(QLabel("EXECUTION MODE"))
            mode_row = QHBoxLayout()
            self.mode_file = QRadioButton("FILE PATH")
            self.mode_inline = QRadioButton("INLINE SCRIPT")
            mode_group = QButtonGroup(self)
            mode_group.addButton(self.mode_file)
            mode_group.addButton(self.mode_inline)
            
            if self.script.get("use_inline", False): self.mode_inline.setChecked(True)
            else: self.mode_file.setChecked(True)
            
            mode_row.addWidget(self.mode_file)
            mode_row.addWidget(self.mode_inline)
            inline_layout.addLayout(mode_row)
            
            inline_layout.addWidget(QLabel("INLINE ENGINE"))
            self.inline_type = QComboBox()
            self.inline_type.addItems(["cmd", "pwsh", "powershell"])
            self.inline_type.setCurrentText(self.script.get("inline_type", "cmd"))
            inline_layout.addWidget(self.inline_type)
            
            inline_layout.addWidget(QLabel("SCRIPT CONTENT"))
            self.inline_script = QTextEdit()
            self.inline_script.setPlainText(self.script.get("inline_script", ""))
            self.inline_script.setAcceptRichText(False)
            self.inline_script.setPlaceholderText("Enter commands here...")
            inline_layout.addWidget(self.inline_script)
            
            right_panel.addWidget(inline_group)
            content_hlayout.addLayout(right_panel, 1)
            
        content_vlayout.addLayout(content_hlayout)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        save_btn = QPushButton("APPLY CHANGES")
        save_btn.setObjectName("SaveBtn")
        save_btn.setFixedHeight(50)
        save_btn.clicked.connect(self.save)
        layout.addWidget(save_btn)

    def create_color_btn(self, text, key):
        btn = QPushButton(text)
        btn.setObjectName("ColorBtn")
        color = self.script.get(key, "#2b2f38")
        btn.setStyleSheet(f"background-color: {color};")
        btn.clicked.connect(lambda: self.pick_color(key, btn))
        return btn

    def pick_color(self, key, btn):
        color = QColorDialog.getColor(QColor(self.color_map[key]), self)
        if color.isValid():
            hex_color = color.name()
            self.color_map[key] = hex_color
            btn.setStyleSheet(f"background-color: {hex_color};")

    def browse_path(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Script")
        if path:
            self.path_edit.setText(path)

    def save(self):
        self.script["name"] = self.name_edit.text()
        if self.script.get("type") != "folder":
            self.script["path"] = self.path_edit.text()
            self.script["hide_terminal"] = self.hide_terminal.isChecked()
            self.script["keep_open"] = self.no_exit.isChecked()
            self.script["kill_window"] = self.kill_win.isChecked()
            self.script["ctrl_left_cmd"] = self.ctrl_l_edit.text()
            self.script["ctrl_right_cmd"] = self.ctrl_r_edit.text()
            self.script["use_inline"] = self.mode_inline.isChecked()
            self.script["inline_type"] = self.inline_type.currentText()
            self.script["inline_script"] = self.inline_script.toPlainText()
        
        self.script["font_family"] = self.font_combo.currentText()
        try: self.script["font_size"] = int(self.size_edit.text())
        except: pass
        self.script["is_bold"] = self.is_bold.isChecked()
        self.script["is_italic"] = self.is_italic.isChecked()
        
        for k, v in self.color_map.items():
            self.script[k] = v
            
        try: self.script["width"] = int(self.width_edit.text())
        except: pass
        try: self.script["height"] = int(self.height_edit.text())
        except: pass
        try: self.script["col_span"] = int(self.cspan_edit.text())
        except: pass
        try: self.script["row_span"] = int(self.rspan_edit.text())
        except: pass
        try: self.script["corner_radius"] = int(self.radius_edit.text())
        except: pass
        try: self.script["border_width"] = int(self.bwidth_edit.text())
        except: pass
        
        self.accept()
        self.parent_app.save_config()
        self.parent_app.refresh_grid()

class SettingsDialog(QDialog):
    def __init__(self, parent_app):
        super().__init__(parent_app)
        self.parent_app = parent_app
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.init_ui()
        self.adjustSize()
        self.center_to_parent()

    def center_to_parent(self):
        if self.parent_app:
            p_geo = self.parent_app.geometry()
            target_x = p_geo.x() + (p_geo.width() - self.width()) // 2
            target_y = p_geo.y() + (p_geo.height() - self.height()) // 2
            self.move(target_x, target_y)
        
    def init_ui(self):
        self.setObjectName("SettingsDialog")
        # Reduced height to 550 to fit inside main window (650)
        self.setFixedSize(500, 550)
        accent = self.parent_app.config['settings']['accent_color']
        border = self.parent_app.config['settings']['border_color']
        
        self.setStyleSheet(f"""
            QDialog#SettingsDialog {{
                background-color: #1d2027;
                border: 2px solid {border};
                border-radius: 8px;
            }}
            QLabel {{
                color: #888888; 
                font-size: 10px;
                font-weight: bold;
                border: none;
                font-family: 'Segoe UI Semibold';
                text-transform: uppercase;
            }}
            QLineEdit {{
                background-color: #252830;
                color: white;
                border: 1px solid #333;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }}
            QLineEdit:focus {{
                border: 1px solid {accent};
            }}
            QCheckBox {{
                color: #dddddd;
                border: none;
                spacing: 12px;
                font-size: 11px;
                font-family: 'Segoe UI';
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                background-color: #252830;
                border: 1px solid #444;
                border-radius: 4px;
            }}
            QCheckBox::indicator:checked {{
                background-color: {accent};
                border: 1px solid {accent};
            }}
            QPushButton#SaveBtn {{
                background-color: #10b153;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border: none;
                border-radius: 6px;
                letter-spacing: 2px;
            }}
            QPushButton#SaveBtn:hover {{
                background-color: #14d363;
            }}
            QPushButton#CloseBtn {{
                color: #555;
                border: none;
                font-size: 20px;
                background: transparent;
            }}
            QPushButton#CloseBtn:hover {{
                color: #ffffff;
                background-color: #fe1616;
                border-radius: 4px;
            }}
            QFrame#GroupFrame {{
                border: 1px solid #333;
                border-left: 3px solid {accent};
                border-radius: 4px;
                margin-top: 12px;
                background: rgba(255, 255, 255, 0.02);
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 30)
        layout.setSpacing(15)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("GLOBAL SETTINGS")
        title.setStyleSheet(f"color: {accent}; font-weight: bold; font-size: 18px; letter-spacing: 1px;")
        header.addWidget(title)
        
        header.addStretch()
        
        close_btn = QPushButton("✕")
        close_btn.setObjectName("CloseBtn")
        close_btn.setFixedSize(35, 35)
        close_btn.clicked.connect(self.reject)
        header.addWidget(close_btn)
        layout.addLayout(header)
        
        # Grid Config Group
        grid_group = QFrame()
        grid_group.setObjectName("GroupFrame")
        grid_l = QVBoxLayout(grid_group)
        grid_l.setContentsMargins(20, 20, 20, 20)
        grid_l.setSpacing(15)
        grid_l.addWidget(QLabel("GRID CONFIGURATION"))
        
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("BUTTONS PER ROW"))
        self.cols_edit = QLineEdit(str(self.parent_app.config["settings"]["columns"]))
        row1.addWidget(self.cols_edit)
        grid_l.addLayout(row1)
        
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("GLOBAL FONT SIZE"))
        self.fsize_edit = QLineEdit(str(self.parent_app.config["settings"].get("font_size", 10)))
        row2.addWidget(self.fsize_edit)
        grid_l.addLayout(row2)
        layout.addWidget(grid_group)
        
        # Window Behavior Group
        win_group = QFrame()
        win_group.setObjectName("GroupFrame")
        win_l = QVBoxLayout(win_group)
        win_l.setContentsMargins(20, 20, 20, 20)
        win_l.setSpacing(15)
        win_l.addWidget(QLabel("WINDOW BEHAVIOR"))
        self.always_on_top = QCheckBox("ALWAYS ON TOP")
        self.always_on_top.setChecked(self.parent_app.config["settings"].get("always_on_top", True))
        win_l.addWidget(self.always_on_top)
        layout.addWidget(win_group)
        
        # Widgets Toggle Group
        widget_group = QFrame()
        widget_group.setObjectName("GroupFrame")
        widget_l = QVBoxLayout(widget_group)
        widget_l.setContentsMargins(20, 20, 20, 20)
        widget_l.setSpacing(15)
        widget_l.addWidget(QLabel("INTERFACE PANELS"))
        
        self.show_github = QCheckBox("GITHUB STATUS")
        self.show_github.setChecked(self.parent_app.config["settings"].get("show_github", True))
        widget_l.addWidget(self.show_github)
        
        self.show_rclone = QCheckBox("RCLONE STATUS")
        self.show_rclone.setChecked(self.parent_app.config["settings"].get("show_rclone", True))
        widget_l.addWidget(self.show_rclone)
        
        self.show_stats = QCheckBox("SYSTEM MONITOR (CPU/RAM/DISK/NET)")
        self.show_stats.setChecked(self.parent_app.config["settings"].get("show_system_stats", True))
        widget_l.addWidget(self.show_stats)
        layout.addWidget(widget_group)
        
        layout.addStretch()
        
        save_btn = QPushButton("SAVE SETTINGS")
        save_btn.setObjectName("SaveBtn")
        save_btn.setFixedHeight(50)
        save_btn.clicked.connect(self.save)
        layout.addWidget(save_btn)
        
    def save(self):
        try: self.parent_app.config["settings"]["columns"] = int(self.cols_edit.text())
        except: pass
        try: self.parent_app.config["settings"]["font_size"] = int(self.fsize_edit.text())
        except: pass
        self.parent_app.config["settings"]["always_on_top"] = self.always_on_top.isChecked()
        self.parent_app.config["settings"]["show_github"] = self.show_github.isChecked()
        self.parent_app.config["settings"]["show_rclone"] = self.show_rclone.isChecked()
        self.parent_app.config["settings"]["show_system_stats"] = self.show_stats.isChecked()
        
        self.accept()
        self.parent_app.save_config()
        self.parent_app.refresh_grid()
        
        # Update always on top instantly
        flags = self.parent_app.windowFlags()
        if self.parent_app.config["settings"]["always_on_top"]:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        else:
            flags &= ~Qt.WindowType.WindowStaysOnTopHint
        self.parent_app.setWindowFlags(flags)
        self.parent_app.show()

class ScriptLauncherApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.load_config()
        self.view_stack = []
        self.clipboard_script = None
        self.drag_start_pos = QPoint()
        
        self.init_ui()
        self.start_monitoring()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    self.config = json.load(f)
            except:
                self.config = DEFAULT_CONFIG.copy()
        else:
            self.config = DEFAULT_CONFIG.copy()

    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)

    def init_ui(self):
        self.setWindowTitle("Script Manager")
        self.setFixedSize(950, 650)
        
        # Frameless and Styling
        if self.config["settings"].get("always_on_top", True):
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.main_widget = QWidget()
        self.main_widget.setObjectName("MainWidget")
        self.main_widget.setStyleSheet(f"""
            QWidget#MainWidget {{
                background-color: {self.config["settings"]["bg_color"]};
                border: 2px solid {self.config["settings"]["border_color"]};
            }}
            QLabel {{
                border: none;
            }}
        """)
        self.setCentralWidget(self.main_widget)
        self.set_window_icon()
        
        self.layout = QVBoxLayout(self.main_widget)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        self.header = QFrame()
        self.header.setFixedHeight(40)
        self.header_layout = QHBoxLayout(self.header)
        self.header_layout.setContentsMargins(10, 0, 10, 0)
        
        self.back_btn = QPushButton("❮")
        self.back_btn.setFixedSize(30, 30)
        self.back_btn.setStyleSheet("color: #fe1616; font-weight: bold; border: none; font-size: 14px;")
        self.back_btn.clicked.connect(self.exit_folder)
        self.back_btn.hide()
        self.header_layout.addWidget(self.back_btn)
        
        self.title_lbl = QLabel("SCRIPT MANAGER 🚀")
        self.title_lbl.setStyleSheet(f"color: {self.config['settings']['accent_color']}; font-weight: bold; font-size: 14px;")
        self.header_layout.addWidget(self.title_lbl)
        
        self.header_layout.addStretch()
        
        add_btn = QPushButton("+")
        add_btn.setFixedSize(30, 30)
        add_btn.setStyleSheet("QPushButton { color: #888; font-size: 18px; border: none; } QPushButton:hover { color: white; background-color: #10b153; }")
        add_btn.clicked.connect(self.add_script_dialog)
        self.header_layout.addWidget(add_btn)
        
        settings_btn = QPushButton("⚙")
        settings_btn.setFixedSize(30, 30)
        settings_btn.setStyleSheet("QPushButton { color: #888; font-size: 18px; border: none; } QPushButton:hover { color: white; background-color: #3a3f4b; }")
        settings_btn.clicked.connect(self.open_settings)
        self.header_layout.addWidget(settings_btn)
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("QPushButton { color: #888; font-size: 18px; border: none; } QPushButton:hover { color: white; background-color: #fe1616; }")
        close_btn.clicked.connect(self.close)
        self.header_layout.addWidget(close_btn)
        
        self.layout.addWidget(self.header)
        
        # Status / Stats Widgets
        stats_layout = QHBoxLayout()
        
        # Github
        if self.config["settings"].get("show_github", True):
            self.github_frame = QFrame()
            self.github_frame.setStyleSheet("QFrame { border: 1px solid #333; padding: 5px; } QLabel { border: none; font-size: 10px; }")
            self.github_layout = QHBoxLayout(self.github_frame)
            self.repo_widgets = {}
            for repo in self.config["github_repos"]:
                repo_lbl = ClickableLabel(repo["name"])
                repo_lbl.setStyleSheet("color: #555; font-weight: bold;")
                repo_path = repo["path"]
                repo_lbl.clicked.connect(lambda e, p=repo_path: self.on_git_click(e, p))
                self.github_layout.addWidget(repo_lbl)
                self.repo_widgets[repo["name"]] = repo_lbl
            stats_layout.addWidget(self.github_frame)
            
        # Rclone
        if self.config["settings"].get("show_rclone", True):
            self.rclone_frame = QFrame()
            self.rclone_frame.setStyleSheet("QFrame { border: 1px solid #333; padding: 5px; } QLabel { border: none; font-size: 10px; }")
            self.rclone_layout = QHBoxLayout(self.rclone_frame)
            self.folder_widgets = {}
            for folder in self.config["rclone_folders"]:
                f_lbl = ClickableLabel(folder.get("label", folder["name"]))
                f_lbl.setStyleSheet("color: #26b2f3; font-weight: bold;")
                f_lbl.clicked.connect(lambda e, f=folder: self.on_rclone_click(e, f))
                self.rclone_layout.addWidget(f_lbl)
                self.folder_widgets[folder["name"]] = f_lbl
            stats_layout.addWidget(self.rclone_frame)
            
        self.layout.addLayout(stats_layout)
        
        # System Stats
        if self.config["settings"].get("show_system_stats", True):
            self.sys_layout = QHBoxLayout()
            self.sys_layout.setSpacing(5)
            
            # CPU
            self.cpu_frame = QFrame()
            self.cpu_frame.setStyleSheet("QFrame { border: 1px solid #333; border-radius: 3px; background: transparent; }")
            cpu_l = QHBoxLayout(self.cpu_frame)
            cpu_l.setContentsMargins(5, 2, 5, 2)
            cpu_l.addWidget(QLabel("CPU"))
            self.cpu_bar = QProgressBar()
            self.cpu_bar.setFixedHeight(6)
            self.cpu_bar.setTextVisible(False)
            self.cpu_bar.setStyleSheet("QProgressBar { background-color: #333; border: none; } QProgressBar::chunk { background-color: #14bcff; }")
            cpu_l.addWidget(self.cpu_bar)
            self.cpu_lbl = QLabel("0%")
            self.cpu_lbl.setStyleSheet("color: #14bcff; font-weight: bold; border: none;")
            cpu_l.addWidget(self.cpu_lbl)
            self.sys_layout.addWidget(self.cpu_frame)
            
            # RAM
            self.ram_frame = QFrame()
            self.ram_frame.setStyleSheet("QFrame { border: 1px solid #333; border-radius: 3px; background: transparent; }")
            ram_l = QHBoxLayout(self.ram_frame)
            ram_l.setContentsMargins(5, 2, 5, 2)
            ram_l.addWidget(QLabel("RAM"))
            self.ram_bar = QProgressBar()
            self.ram_bar.setFixedHeight(6)
            self.ram_bar.setTextVisible(False)
            self.ram_bar.setStyleSheet("QProgressBar { background-color: #333; border: none; } QProgressBar::chunk { background-color: #ff934b; }")
            ram_l.addWidget(self.ram_bar)
            self.ram_lbl = QLabel("0%")
            self.ram_lbl.setStyleSheet("color: #ff934b; font-weight: bold; border: none;")
            ram_l.addWidget(self.ram_lbl)
            self.sys_layout.addWidget(self.ram_frame)

            # Disk C
            self.disk_c_frame = QFrame()
            self.disk_c_frame.setStyleSheet("QFrame { border: 1px solid #333; border-radius: 3px; background: transparent; }")
            disk_c_l = QHBoxLayout(self.disk_c_frame)
            disk_c_l.setContentsMargins(5, 2, 5, 2)
            disk_c_l.addWidget(QLabel("C:"))
            self.disk_c_bar = QProgressBar()
            self.disk_c_bar.setFixedHeight(6)
            self.disk_c_bar.setTextVisible(False)
            self.disk_c_bar.setStyleSheet("QProgressBar { background-color: #333; border: none; } QProgressBar::chunk { background-color: #044568; }")
            disk_c_l.addWidget(self.disk_c_bar)
            self.disk_c_lbl = QLabel("0%")
            self.disk_c_lbl.setStyleSheet("color: white; border: none;")
            disk_c_l.addWidget(self.disk_c_lbl)
            self.sys_layout.addWidget(self.disk_c_frame)

            # Disk D
            self.disk_d_frame = QFrame()
            self.disk_d_frame.setStyleSheet("QFrame { border: 1px solid #333; border-radius: 3px; background: transparent; }")
            disk_d_l = QHBoxLayout(self.disk_d_frame)
            disk_d_l.setContentsMargins(5, 2, 5, 2)
            disk_d_l.addWidget(QLabel("D:"))
            self.disk_d_bar = QProgressBar()
            self.disk_d_bar.setFixedHeight(6)
            self.disk_d_bar.setTextVisible(False)
            self.disk_d_bar.setStyleSheet("QProgressBar { background-color: #333; border: none; } QProgressBar::chunk { background-color: #044568; }")
            disk_d_l.addWidget(self.disk_d_bar)
            self.disk_d_lbl = QLabel("0%")
            self.disk_d_lbl.setStyleSheet("color: white; border: none;")
            disk_d_l.addWidget(self.disk_d_lbl)
            self.sys_layout.addWidget(self.disk_d_frame)
            
            # Net
            self.net_frame = QFrame()
            self.net_frame.setStyleSheet("QFrame { border: 1px solid #333; border-radius: 3px; background: transparent; }")
            net_l = QHBoxLayout(self.net_frame)
            net_l.setContentsMargins(5, 2, 5, 2)
            self.up_lbl = QLabel("▲ 0.0")
            self.up_lbl.setStyleSheet("color: #00ff21; border: none;")
            net_l.addWidget(self.up_lbl)
            self.down_lbl = QLabel("▼ 0.0")
            self.down_lbl.setStyleSheet("color: #26b2f3; border: none;")
            net_l.addWidget(self.down_lbl)
            self.sys_layout.addWidget(self.net_frame)
            
            self.layout.addLayout(self.sys_layout)

        # Scrollable Grid Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.grid_container = QWidget()
        self.grid_container.setAcceptDrops(True)
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(10)
        self.scroll.setWidget(self.grid_container)
        self.layout.addWidget(self.scroll)
        
        # Drag movement for frameless window
        self.header.mousePressEvent = self.headerPressEvent
        self.header.mouseMoveEvent = self.headerMoveEvent
        
        self.refresh_grid()

    def headerPressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def headerMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_start_pos)

    def refresh_grid(self):
        # Clear existing
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        scripts = self.view_stack[-1]["scripts"] if self.view_stack else self.config["scripts"]
        cols = self.view_stack[-1].get("grid_columns", 0) if self.view_stack else 0
        if cols == 0: cols = self.config["settings"]["columns"]
        
        if self.view_stack:
            self.title_lbl.setText(f" ❯ {self.view_stack[-1]['name'].upper()}")
            self.back_btn.show()
        else:
            self.title_lbl.setText("SCRIPT MANAGER 🚀")
            self.back_btn.hide()
            
        # Grid placement logic
        occupied = set()
        for i, s in enumerate(scripts):
            btn = ScriptButton(s, self)
            
            r_span = s.get("row_span", 1)
            c_span = s.get("col_span", 1)
            
            # Find spot
            found = False
            for r in range(100):
                for c in range(cols):
                    if (r, c) not in occupied:
                        # Check span
                        fits = True
                        for rs in range(r_span):
                            for cs in range(c_span):
                                if c + cs >= cols or (r + rs, c + cs) in occupied:
                                    fits = False
                                    break
                            if not fits: break
                        
                        if fits:
                            for rs in range(r_span):
                                for cs in range(c_span):
                                    occupied.add((r + rs, c + cs))
                            self.grid_layout.addWidget(btn, r, c, r_span, c_span)
                            found = True
                            break
                if found: break

    def start_monitoring(self):
        self.sys_thread = SystemMonitorThread()
        self.sys_thread.stats_updated.connect(self.update_stats)
        self.sys_thread.start()
        
        self.status_thread = StatusMonitorThread(self.config)
        self.status_thread.status_updated.connect(self.update_status)
        self.status_thread.start()

    def update_stats(self, stats):
        if hasattr(self, 'cpu_bar'):
            self.cpu_bar.setValue(int(stats["cpu"]))
            self.cpu_lbl.setText(f"{int(stats['cpu'])}%")
            self.ram_bar.setValue(int(stats["ram"]))
            self.ram_lbl.setText(f"{int(stats['ram'])}%")
            
            self.disk_c_bar.setValue(int(stats["disk_c"]))
            self.disk_c_lbl.setText(f"{int(stats['disk_c'])}%")
            if hasattr(self, 'disk_d_bar'):
                self.disk_d_bar.setValue(int(stats["disk_d"]))
                self.disk_d_lbl.setText(f"{int(stats['disk_d'])}%")
            
            up = stats["up"] / 1024 # KB/s
            down = stats["down"] / 1024
            if up > 1024: self.up_lbl.setText(f"▲ {up/1024:.1f} M")
            else: self.up_lbl.setText(f"▲ {up:.1f} K")
            
            if down > 1024: self.down_lbl.setText(f"▼ {down/1024:.1f} M")
            else: self.down_lbl.setText(f"▼ {down:.1f} K")

    def on_git_click(self, event, path):
        modifiers = QApplication.keyboardModifiers()
        if event.button() == Qt.MouseButton.LeftButton:
            if modifiers == Qt.KeyboardModifier.ControlModifier:
                 subprocess.Popen(f'explorer "{path}"', shell=True)
            else:
                 subprocess.Popen(["Start", "pwsh", "-NoExit", "-Command", f"& {{$host.UI.RawUI.WindowTitle='GiTSync' ; cd {path.replace(os.sep, '/')} ; gitter}}"], shell=True)
        elif event.button() == Qt.MouseButton.RightButton:
            if modifiers == Qt.KeyboardModifier.ControlModifier:
                 subprocess.Popen(["Start", "pwsh", "-NoExit", "-Command", f"& {{$host.UI.RawUI.WindowTitle='Git Restore' ; cd {path.replace(os.sep, '/')} ; git restore . }}"], shell=True)
            else:
                 subprocess.Popen('start pwsh -NoExit -Command "lazygit"', cwd=path, shell=True)

    def on_rclone_click(self, event, folder):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.KeyboardModifier.ControlModifier:
            if event.button() == Qt.MouseButton.LeftButton:
                self.on_rclone_sync(folder, "left")
            elif event.button() == Qt.MouseButton.RightButton:
                self.on_rclone_sync(folder, "right")
        else:
            # Open local source
            src = os.path.expandvars(folder["src"])
            if os.path.exists(src):
                subprocess.Popen(f'explorer "{src}"', shell=True)

    def on_rclone_sync(self, folder, direction):
        src = folder["src"]
        dst = folder["dst"]
        cmd = folder.get("left_click_cmd", f"rclone sync src dst -P --fast-list") if direction == "left" else folder.get("right_click_cmd", f"rclone sync dst src -P --fast-list")
        cmd = cmd.replace("src", f'"{src}"').replace("dst", f'"{dst}"')
        subprocess.Popen(["Start", "pwsh", "-NoExit", "-Command", f"& {{$host.UI.RawUI.WindowTitle='Rclone Sync' ; {cmd}}}"], shell=True)

    def set_window_icon(self):
        try:
            from PIL import Image, ImageDraw
            import io
            image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            draw.ellipse([20, 20, 44, 60], fill='#26b2f3', outline='#0d8c42', width=2)
            draw.polygon([32, 10, 20, 25, 44, 25], fill='#fe1616')
            draw.ellipse([27, 30, 37, 40], fill='#1d2027')
            draw.ellipse([29, 32, 35, 38], fill='#26b2f3')
            
            byte_io = io.BytesIO()
            image.save(byte_io, 'PNG')
            icon = QIcon()
            pixmap = QIcon(QIcon.fromTheme("rocket")).pixmap(64,64) # Try theme first
            # Or just set our custom one
            from PyQt6.QtGui import QPixmap
            pm = QPixmap()
            pm.loadFromData(byte_io.getvalue())
            self.setWindowIcon(QIcon(pm))
        except:
            pass

    def update_status(self, results):
        if "github" in results:
            for name, color in results["github"].items():
                if name in self.repo_widgets:
                    self.repo_widgets[name].setStyleSheet(f"color: {color}; font-weight: bold;")
        if "rclone" in results:
             for name, color in results["rclone"].items():
                if name in self.folder_widgets:
                    self.folder_widgets[name].setStyleSheet(f"color: {color}; font-weight: bold;")

    def handle_script_click(self, script):
        if script.get("type") == "folder":
            self.view_stack.append(script)
            self.refresh_grid()
        else:
            self.launch_script(script)

    def exit_folder(self):
        if self.view_stack:
            self.view_stack.pop()
            self.refresh_grid()

    def launch_script(self, script_obj):
        hide = script_obj.get("hide_terminal", False)
        keep_open = script_obj.get("keep_open", False)
        
        if script_obj.get("use_inline", False) and script_obj.get("inline_script"):
            self.launch_inline_script(script_obj)
            return

        path = os.path.expandvars(script_obj.get("path", ""))
        if not path: return
        
        cflags = subprocess.CREATE_NEW_CONSOLE
        if hide: cflags = 0x08000000 # CREATE_NO_WINDOW
        
        try:
            script_dir = os.path.dirname(path) if os.path.isfile(path) else None
            
            if os.path.isfile(path):
                if path.endswith(".py"):
                    python_exe = "pythonw" if hide else "python"
                    if not hide and keep_open:
                        subprocess.Popen(f'start "" cmd /k {python_exe} "{path}"', shell=True, cwd=script_dir, creationflags=cflags)
                    else:
                        subprocess.Popen([python_exe, path], cwd=script_dir, creationflags=cflags)
                elif path.lower().endswith(".ps1"):
                    ps_bin = "pwsh" if shutil.which("pwsh") else "powershell"
                    if hide:
                        ps_args = [ps_bin, "-WindowStyle", "Hidden", "-ExecutionPolicy", "Bypass", "-NoProfile", "-File", path]
                        subprocess.Popen(ps_args, cwd=script_dir, creationflags=cflags)
                    else:
                        no_exit = "-NoExit" if keep_open else ""
                        cmd_str = f'start "" "{ps_bin}" {no_exit} -ExecutionPolicy Bypass -Command "& \\"{path}\\""'
                        subprocess.Popen(cmd_str, shell=True, cwd=script_dir, creationflags=cflags)
                else:
                    if not hide and keep_open:
                         subprocess.Popen(f'start "" cmd /k "{path}"', shell=True, cwd=script_dir, creationflags=cflags)
                    else:
                         subprocess.Popen(f'start "" "{path}"', shell=True, cwd=script_dir, creationflags=cflags)
            else:
                if not hide and keep_open:
                     subprocess.Popen(f'start "" cmd /k "{path}"', shell=True, creationflags=cflags)
                else:
                     subprocess.Popen(path, shell=True, creationflags=cflags)
                     
            if script_obj.get("kill_window", False):
                self.close()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to launch: {e}")

    def launch_inline_script(self, script_obj):
        inline_script = script_obj.get("inline_script", "")
        inline_type = script_obj.get("inline_type", "cmd")
        hide = script_obj.get("hide_terminal", False)
        keep_open = script_obj.get("keep_open", False)
        
        cflags = subprocess.CREATE_NEW_CONSOLE
        if hide: cflags = 0x08000000
        
        try:
            ext_map = {"cmd": ".bat", "pwsh": ".ps1", "powershell": ".ps1"}
            ext = ext_map.get(inline_type, ".bat")
            
            with tempfile.NamedTemporaryFile(mode='w', suffix=ext, delete=False, encoding='utf-8') as f:
                f.write(inline_script)
                temp_path = f.name
            
            if inline_type in ["pwsh", "powershell"]:
                ps_bin = "pwsh" if inline_type == "pwsh" and shutil.which("pwsh") else "powershell"
                if hide:
                    ps_args = [ps_bin, "-WindowStyle", "Hidden", "-ExecutionPolicy", "Bypass", "-NoProfile", "-File", temp_path]
                    subprocess.Popen(ps_args, creationflags=cflags)
                else:
                    no_exit = "-NoExit" if keep_open else ""
                    cmd_str = f'start "" "{ps_bin}" {no_exit} -ExecutionPolicy Bypass -Command "& \\"{temp_path}\\""'
                    subprocess.Popen(cmd_str, shell=True, creationflags=cflags)
            else:
                if not hide and keep_open:
                    subprocess.Popen(f'start "" cmd /k "{temp_path}"', shell=True, creationflags=cflags)
                else:
                    subprocess.Popen(f'start "" cmd /c "{temp_path}"', shell=True, creationflags=cflags)
            
            if script_obj.get("kill_window", False):
                self.close()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to execute: {e}")

    def duplicate_script(self, script):
        new_s = script.copy()
        new_s["name"] += " (Copy)"
        scripts = self.view_stack[-1]["scripts"] if self.view_stack else self.config["scripts"]
        scripts.append(new_s)
        self.save_config()
        self.refresh_grid()

    def cut_script(self, script):
        self.clipboard_script = script.copy()
        scripts = self.view_stack[-1]["scripts"] if self.view_stack else self.config["scripts"]
        if script in scripts:
            scripts.remove(script)
            self.save_config()
            self.refresh_grid()

    def paste_script(self):
        if self.clipboard_script:
            scripts = self.view_stack[-1]["scripts"] if self.view_stack else self.config["scripts"]
            scripts.append(self.clipboard_script.copy())
            self.save_config()
            self.refresh_grid()

    def move_script_out(self, script):
        if not self.view_stack: return
        current_list = self.view_stack[-1]["scripts"]
        parent_list = self.view_stack[-2]["scripts"] if len(self.view_stack) > 1 else self.config["scripts"]
        if script in current_list:
            current_list.remove(script)
            parent_list.append(script)
            self.save_config()
            self.refresh_grid()

    def remove_script(self, script):
        if QMessageBox.question(self, "Confirm", f"Remove '{script['name']}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            scripts = self.view_stack[-1]["scripts"] if self.view_stack else self.config["scripts"]
            if script in scripts:
                scripts.remove(script)
                self.save_config()
                self.refresh_grid()

    def open_edit_dialog(self, script):
        dlg = EditDialog(script, self)
        dlg.exec()

    def add_script_dialog(self):
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background-color: #2b2f38; color: white; border: 1px solid #fe1616; }")
        
        add_s = menu.addAction("📄 New Script")
        add_f = menu.addAction("📁 New Folder")
        if self.clipboard_script:
            paste_act = menu.addAction(f"📋 Paste '{self.clipboard_script['name']}'")
        else:
            paste_act = None
            
        action = menu.exec(QCursor.pos())
        
        scripts = self.view_stack[-1]["scripts"] if self.view_stack else self.config["scripts"]
        
        if action == add_s:
            path, _ = QFileDialog.getOpenFileName(self, "Select Script")
            if path:
                name = os.path.basename(path)
                scripts.append({"name": name, "path": path, "type": "script"})
                self.save_config()
                self.refresh_grid()
        elif action == add_f:
            scripts.append({"name": "New Folder", "type": "folder", "scripts": []})
            self.save_config()
            self.refresh_grid()
        elif action == paste_act and paste_act:
            self.paste_script()

    def open_settings(self):
        dlg = SettingsDialog(self)
        dlg.exec()

    # Drag and Drop to Reorder / Move into folders
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        name = event.mimeData().text()
        scripts = self.view_stack[-1]["scripts"] if self.view_stack else self.config["scripts"]
        
        # Find dragged script
        dragged_idx = -1
        for i, s in enumerate(scripts):
            if s["name"] == name:
                dragged_idx = i
                break
        
        if dragged_idx == -1: return

        # Find drop target
        pos = event.position().toPoint()
        widget = self.childAt(pos)
        while widget and not isinstance(widget, ScriptButton):
            widget = widget.parentWidget()
            
        if isinstance(widget, ScriptButton):
            target_idx = -1
            for i, s in enumerate(scripts):
                if s["name"] == widget.script["name"]:
                    target_idx = i
                    break
            
            if target_idx != -1 and target_idx != dragged_idx:
                if widget.script.get("type") == "folder":
                    # Move into folder
                    if dragged_idx < target_idx:
                        item = scripts.pop(dragged_idx)
                    else:
                        item = scripts.pop(dragged_idx)
                    
                    if item == widget.script: return # Recursion
                    
                    if QMessageBox.question(self, "Move Item", f"Move '{item['name']}' into '{widget.script['name']}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
                        if "scripts" not in widget.script: widget.script["scripts"] = []
                        widget.script["scripts"].append(item)
                    else:
                        # Put it back
                        scripts.insert(dragged_idx, item)
                        return
                else:
                    # Swap/Reorder
                    item = scripts.pop(dragged_idx)
                    scripts.insert(target_idx, item)
                
                self.save_config()
                self.refresh_grid()
                event.acceptProposedAction()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScriptLauncherApp()
    window.show()
    sys.exit(app.exec())
