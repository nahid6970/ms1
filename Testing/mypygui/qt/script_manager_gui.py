import sys
import os
import json
import shutil
import subprocess
import threading
import time
import psutil
from datetime import datetime
from functools import partial

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QPushButton, QLineEdit, 
    QScrollArea, QFrame, QMessageBox, QDialog, 
    QComboBox, QFileDialog, QSplitter, QMenu, 
    QGridLayout, QProgressBar, QCheckBox, QColorDialog
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize, QThread, QMimeData, QPoint
from PyQt6.QtGui import QFont, QColor, QPalette, QCursor, QAction, QDrag, QPixmap, QPainter, QPen, QBrush

# --- Configuration & Constants ---
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "script_launcher_config.json")

# Cyberpunk Palette (from startup.py)
CP_BG = "#050505"           # Main Background
CP_PANEL = "#111111"        # Panel Background
CP_YELLOW = "#FCEE0A"       # Cyber Yellow
CP_CYAN = "#00F0FF"         # Neon Cyan
CP_RED = "#FF003C"          # Neon Red
CP_DIM = "#3a3a3a"          # Dimmed/Inactive
CP_TEXT = "#E0E0E0"         # Main Text
CP_SUBTEXT = "#808080"      # Sub Text
CP_GREEN = "#00FF21"        # Success Green
CP_ORANGE = "#ff934b"       # Warning Orange

DEFAULT_CONFIG = {
    "settings": {
        "columns": 5,
        "font_family": "Consolas",
        "font_size": 10,
        "bg_color": CP_BG,
        "accent_color": CP_CYAN,
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
            "left_click_cmd": 'rclone sync src dst -P --fast-list --exclude ".git/**" --exclude "__pycache__/**"  --log-level INFO',
            "right_click_cmd": "rclone sync dst src -P --fast-list"
        },
        {
            "name": "Photos",
            "src": "C:/Users/nahid/Pictures/",
            "dst": "o0:/Pictures/",
            "label": "\uf03e",
            "cmd": 'rclone check src dst --fast-list --size-only --exclude ".globalTrash/**" --exclude ".stfolder/**" --exclude ".stfolder (1)/**"',
            "left_click_cmd": 'rclone sync src dst -P --fast-list --track-renames --exclude ".globalTrash/**" --exclude ".stfolder/**" --log-level INFO',
            "right_click_cmd": "rclone sync dst src -P --fast-list"
        },
        {
            "name": "msBackups",
            "label": "\udb85\ude32",
            "src": "C:/Users/nahid/ms/msBackups",
            "dst": "o0:/msBackups",
            "cmd": "rclone check src dst --fast-list --size-only"
        },
        {
            "name": "software",
            "label": "\uf40e",
            "src": "D:/software",
            "dst": "gu:/software",
            "cmd": "rclone check src dst --fast-list --size-only"
        },
        {
            "name": "song",
            "label": "\uec1b",
            "src": "D:/song",
            "dst": "gu:/song",
            "cmd": "rclone check src dst --fast-list --size-only"
        }
    ]
}

# --- Styled Components ---

class CyberButton(QPushButton):
    def __init__(self, text, parent=None, color=CP_YELLOW, is_outlined=False, font_size=10):
        super().__init__(text, parent)
        self.color = color
        self.is_outlined = is_outlined
        self.setFont(QFont("Consolas", font_size, QFont.Weight.Bold))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_style()

    def update_style(self):
        if self.is_outlined:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {self.color};
                    border: 2px solid {self.color};
                    padding: 5px;
                    font-family: 'Consolas';
                }}
                QPushButton:hover {{
                    background-color: {self.color};
                    color: {CP_BG};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.color};
                    color: {CP_BG};
                    border: none;
                    padding: 5px;
                    font-family: 'Consolas';
                }}
                QPushButton:hover {{
                    background-color: {CP_BG};
                    color: {self.color};
                    border: 1px solid {self.color};
                }}
            """)

class CyberInput(QLineEdit):
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setFont(QFont("Consolas", 10))
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: {CP_PANEL};
                color: {CP_YELLOW};
                border: 1px solid {CP_DIM};
                padding: 5px;
                font-family: 'Consolas';
            }}
            QLineEdit:focus {{
                border: 1px solid {CP_CYAN};
            }}
        """)

class ScriptButton(QPushButton):
    """
    The main grid button.
    Supports Drag & Drop, Right Click Context Menu, and Custom Styling.
    """
    def __init__(self, script_data, index, parent=None):
        super().__init__(parent)
        self.script = script_data
        self.index = index
        self.parent_window = parent
        
        # Text and Font
        self.setText(self.script.get("name", "Unknown"))
        font_family = self.script.get("font_family", "Consolas")
        font_size = self.script.get("font_size", 10)
        is_bold = self.script.get("is_bold", False) or self.script.get("type") == "folder"
        is_italic = self.script.get("is_italic", False)
        
        font = QFont(font_family, font_size)
        font.setBold(is_bold)
        font.setItalic(is_italic)
        self.setFont(font)
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(self.sizePolicy().Policy.Expanding, self.sizePolicy().Policy.Expanding)
        
        # Dimensions (min size)
        w = self.script.get("width", 0)
        h = self.script.get("height", 0)
        if w > 0: self.setFixedWidth(w)
        if h > 0: self.setFixedHeight(h)
        if w == 0 and h == 0:
            self.setMinimumHeight(50)

        # Style
        self.bg_color = self.script.get("color", "#2b2f38" if self.script.get("type") != "folder" else "#1a1c23")
        self.text_color = self.script.get("text_color", "white" if self.script.get("type") != "folder" else "#ffd700")
        self.hover_bg = self.script.get("hover_color", CP_CYAN)
        self.hover_text = self.script.get("hover_text_color", "white")
        self.border_color = self.script.get("border_color", CP_RED)
        self.border_width = self.script.get("border_width", 0)
        self.radius = self.script.get("corner_radius", 4)
        
        self.apply_style()
        
        # Enable Drag
        self.setAcceptDrops(True)

    def apply_style(self):
        border_str = f"border: {self.border_width}px solid {self.border_color};" if self.border_width > 0 else "border: none;"
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.bg_color};
                color: {self.text_color};
                border-radius: {self.radius}px;
                {border_str}
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {self.hover_bg};
                color: {self.hover_text};
            }}
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return
            
        drag = QDrag(self)
        mime_data = QMimeData()
        # We pass the index and the object ID as text to verify source
        mime_data.setText(f"{self.index}")
        drag.setMimeData(mime_data)
        
        # Create a pixmap for dragging
        pixmap = QPixmap(self.size())
        self.render(pixmap)
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())
        
        drag.exec(Qt.DropAction.MoveAction)

    def dragEnterEvent(self, event):
        if event.source() == self:
            event.ignore()
            return
        event.acceptProposedAction()

    def dropEvent(self, event):
        source_idx = int(event.mimeData().text())
        target_idx = self.index
        
        if source_idx != target_idx:
            self.parent_window.handle_drop(source_idx, target_idx)
            event.acceptProposedAction()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{ background-color: {CP_PANEL}; color: {CP_TEXT}; border: 1px solid {CP_DIM}; }}
            QMenu::item {{ padding: 5px 20px; }}
            QMenu::item:selected {{ background-color: {CP_CYAN}; color: {CP_BG}; }}
        """)
        
        edit_action = QAction("Edit / Stylize", self)
        edit_action.triggered.connect(lambda: self.parent_window.open_edit_dialog(self.script))
        menu.addAction(edit_action)
        
        dup_action = QAction("Duplicate", self)
        dup_action.triggered.connect(lambda: self.parent_window.duplicate_script(self.script))
        menu.addAction(dup_action)
        
        cut_action = QAction("Cut", self)
        cut_action.triggered.connect(lambda: self.parent_window.cut_script(self.script))
        menu.addAction(cut_action)
        
        if self.parent_window.view_stack:
            move_out_action = QAction("Move Up / Out", self)
            move_out_action.triggered.connect(lambda: self.parent_window.move_script_out(self.script))
            menu.addAction(move_out_action)
            
        menu.addSeparator()
        
        del_action = QAction("Delete", self)
        del_action.triggered.connect(lambda: self.parent_window.remove_script(self.script))
        menu.addAction(del_action)
        
        menu.exec(event.globalPos())

# --- Worker Threads ---

class SystemStatsWorker(QThread):
    stats_updated = pyqtSignal(float, float, float, float, float, float, list) # cpu, ram, c, d, up, down, cores

    def __init__(self):
        super().__init__()
        self.running = True
        self.last_net = psutil.net_io_counters()

    def run(self):
        while self.running:
            try:
                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent
                
                # Disk
                c_usage = psutil.disk_usage('C:').percent
                d_usage = 0
                if os.path.exists('D:'):
                    try: d_usage = psutil.disk_usage('D:').percent
                    except: pass
                
                # Net
                net = psutil.net_io_counters()
                sent = (net.bytes_sent - self.last_net.bytes_sent) / (1024 * 1024)
                recv = (net.bytes_recv - self.last_net.bytes_recv) / (1024 * 1024)
                self.last_net = net
                
                # Cores
                cores = psutil.cpu_percent(percpu=True)
                
                self.stats_updated.emit(cpu, ram, c_usage, d_usage, sent, recv, cores)
                time.sleep(1)
            except Exception as e:
                print(f"Stats error: {e}")
                time.sleep(1)

    def stop(self):
        self.running = False
        self.wait()

class GitWorker(QThread):
    repo_updated = pyqtSignal(str, str) # name, status

    def __init__(self, repos):
        super().__init__()
        self.repos = repos
        self.running = True

    def run(self):
        while self.running:
            for repo in self.repos:
                path = repo["path"]
                status = "unknown"
                if os.path.exists(path):
                    try:
                        if os.path.isdir(os.path.join(path, ".git")):
                            # Run git status
                            res = subprocess.run(["git", "status", "--porcelain"], 
                                               cwd=path, capture_output=True, text=True, 
                                               timeout=5, creationflags=subprocess.CREATE_NO_WINDOW)
                            status = "clean" if not res.stdout.strip() else "dirty"
                        else:
                            status = "no_git"
                    except:
                        status = "error"
                else:
                    status = "missing"
                
                self.repo_updated.emit(repo["name"], status)
            
            # Sleep 5 seconds between full checks
            for _ in range(50):
                if not self.running: break
                time.sleep(0.1)

    def stop(self):
        self.running = False
        self.wait()

class RcloneWorker(QThread):
    folder_updated = pyqtSignal(str, bool) # name, is_ok

    def __init__(self, folders):
        super().__init__()
        self.folders = folders
        self.running = True
        self.log_dir = os.path.expanduser(r"~\script_output\rclone")
        os.makedirs(self.log_dir, exist_ok=True)

    def run(self):
        while self.running:
            threads = []
            for folder in self.folders:
                t = threading.Thread(target=self.check_folder, args=(folder,))
                t.daemon = True
                t.start()
                threads.append(t)
            
            for t in threads: t.join()
            
            # Sleep 10 mins
            for _ in range(600):
                if not self.running: break
                time.sleep(1)

    def check_folder(self, folder):
        name = folder["name"]
        raw_cmd = folder.get("cmd", "rclone check src dst --fast-list --size-only")
        cmd = raw_cmd.replace("src", folder["src"]).replace("dst", folder["dst"])
        log_file = os.path.join(self.log_dir, f"{name}_check.log")
        
        try:
            with open(log_file, "w") as f:
                subprocess.run(cmd, shell=True, stdout=f, stderr=f, timeout=120, creationflags=subprocess.CREATE_NO_WINDOW)
            
            # Read log to determine success
            with open(log_file, "r") as f:
                content = f.read()
            
            # Simple heuristic: if 'ERROR' in log, it failed. 
            # Note: rclone check returns non-zero if differences found, but we want to know if *sync* is needed or if *error* occurred.
            # Usually 'Differences: 0' means synced.
            is_ok = "0 differences found" in content and "ERROR" not in content
            self.folder_updated.emit(name, is_ok)
        except:
            self.folder_updated.emit(name, False)

    def stop(self):
        self.running = False
        self.wait()

# --- Main Application ---

class ScriptManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = DEFAULT_CONFIG.copy()
        self.load_config()
        
        self.view_stack = []
        self.clipboard_script = None
        self.workers = []
        
        self.setWindowTitle("SCRIPT MANAGER // CP_V2")
        self.resize(950, 700)
        self.setup_ui()
        self.start_workers()

        if self.config["settings"].get("always_on_top", True):
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    loaded = json.load(f)
                    # Merge logic
                    for k, v in loaded.items():
                        if k in self.config and isinstance(self.config[k], dict) and isinstance(v, dict):
                            self.config[k].update(v)
                        else:
                            self.config[k] = v
            except:
                pass
        self.save_config()

    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)

    def setup_ui(self):
        # Main Widget
        central = QWidget()
        central.setStyleSheet(f"background-color: {CP_BG};")
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 1. Header
        header = QHBoxLayout()
        
        self.back_btn = CyberButton("❮", color=CP_RED, parent=self, is_outlined=True)
        self.back_btn.setFixedWidth(40)
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.hide()
        header.addWidget(self.back_btn)
        
        self.title_lbl = QLabel("SCRIPT MANAGER 🚀")
        self.title_lbl.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        self.title_lbl.setStyleSheet(f"color: {CP_YELLOW};")
        header.addWidget(self.title_lbl)
        
        header.addStretch()
        
        add_btn = CyberButton("+", color=CP_GREEN, is_outlined=True)
        add_btn.setFixedSize(40, 30)
        add_btn.clicked.connect(self.open_add_dialog)
        header.addWidget(add_btn)
        
        settings_btn = CyberButton("⚙", color=CP_TEXT, is_outlined=True)
        settings_btn.setFixedSize(40, 30)
        settings_btn.clicked.connect(self.open_settings)
        header.addWidget(settings_btn)
        
        main_layout.addLayout(header)

        # 2. Status Section (Git / Rclone)
        self.status_container = QFrame()
        self.status_container.setStyleSheet(f"background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; border-radius: 4px;")
        status_layout = QHBoxLayout(self.status_container)
        status_layout.setContentsMargins(5, 5, 5, 5)
        
        # Git Status
        if self.config["settings"].get("show_github", True):
            git_frame = QVBoxLayout()
            git_lbl = QLabel("GITHUB STATUS")
            git_lbl.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
            git_lbl.setStyleSheet(f"color: {CP_SUBTEXT};")
            git_frame.addWidget(git_lbl)
            
            self.git_widgets = {}
            git_items_layout = QHBoxLayout()
            for repo in self.config["github_repos"]:
                f = QFrame()
                f.setStyleSheet(f"background-color: {CP_DIM}; border-radius: 3px;")
                fl = QHBoxLayout(f)
                fl.setContentsMargins(5, 2, 5, 2)
                
                ind = QLabel("●")
                ind.setStyleSheet(f"color: {CP_SUBTEXT};")
                name = QLabel(repo["name"])
                name.setStyleSheet("color: white; font-weight: bold;")
                
                # Click handlers for git
                # Since QLabel doesn't have clicked signal, use simple transparent button overlay or mousePressEvent
                # For simplicity, let's wrap in a customized frame or button
                # We'll stick to a simple button for the name
                btn = QPushButton(repo["name"])
                btn.setStyleSheet("border: none; color: white; font-weight: bold; text-align: left;")
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                # Left click: Git Gitter (custom)
                # Ctrl+Left: Explorer
                # Right: LazyGit
                # Ctrl+Right: Restore
                # Since QPushButton doesn't support all that natively easily without subclass, we'll just connect clicked for now
                btn.clicked.connect(partial(self.handle_git_click, repo, "gitter"))
                btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                btn.customContextMenuRequested.connect(partial(self.handle_git_context, repo, btn))
                
                fl.addWidget(ind)
                fl.addWidget(btn)
                git_items_layout.addWidget(f)
                self.git_widgets[repo["name"]] = ind
            
            git_items_layout.addStretch()
            git_frame.addLayout(git_items_layout)
            status_layout.addLayout(git_frame, stretch=1)

        # Rclone Status
        if self.config["settings"].get("show_rclone", True):
            rclone_frame = QVBoxLayout()
            rc_lbl = QLabel("DRIVE STATUS")
            rc_lbl.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
            rc_lbl.setStyleSheet(f"color: {CP_SUBTEXT};")
            rclone_frame.addWidget(rc_lbl)
            
            self.rclone_widgets = {}
            rc_items_layout = QHBoxLayout()
            for folder in self.config["rclone_folders"]:
                f = QFrame()
                f.setStyleSheet(f"background-color: {CP_DIM}; border-radius: 3px;")
                fl = QHBoxLayout(f)
                fl.setContentsMargins(5, 2, 5, 2)
                
                ind = QLabel("●")
                ind.setStyleSheet(f"color: {CP_SUBTEXT};")
                
                btn = QPushButton(folder.get("label", folder["name"]))
                btn.setStyleSheet("border: none; color: white; font-weight: bold;")
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.clicked.connect(partial(self.handle_rclone_click, folder))
                
                fl.addWidget(ind)
                fl.addWidget(btn)
                rc_items_layout.addWidget(f)
                self.rclone_widgets[folder["name"]] = ind
            
            rc_items_layout.addStretch()
            rclone_frame.addLayout(rc_items_layout)
            status_layout.addLayout(rclone_frame, stretch=1)

        main_layout.addWidget(self.status_container)

        # 3. System Stats
        if self.config["settings"].get("show_system_stats", True):
            self.stats_frame = QFrame()
            self.stats_frame.setStyleSheet(f"background-color: {CP_PANEL}; border-top: 2px solid {CP_CYAN};")
            stats_layout = QHBoxLayout(self.stats_frame)
            stats_layout.setContentsMargins(10, 5, 10, 5)
            
            # Helper to make stat widget
            def make_stat(label):
                c = QVBoxLayout()
                l = QLabel(label)
                l.setFont(QFont("Consolas", 8))
                l.setStyleSheet(f"color: {CP_SUBTEXT};")
                v = QLabel("0%")
                v.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
                v.setStyleSheet(f"color: {CP_CYAN};")
                c.addWidget(l)
                c.addWidget(v)
                return c, v

            _, self.cpu_lbl = make_stat("CPU")
            stats_layout.addLayout(_)
            
            _, self.ram_lbl = make_stat("RAM")
            stats_layout.addLayout(_)
            
            _, self.disk_lbl = make_stat("DISK (C)")
            stats_layout.addLayout(_)
            
            _, self.net_lbl = make_stat("NET (MB/s)")
            stats_layout.addLayout(_)
            
            main_layout.addWidget(self.stats_frame)

        # 4. Grid Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"background-color: transparent; border: none;")
        
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(10)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll.setWidget(self.grid_container)
        main_layout.addWidget(scroll, stretch=1)

        # Initial Refresh
        self.refresh_grid()

    def start_workers(self):
        # 1. System Stats
        if self.config["settings"].get("show_system_stats", True):
            self.sys_worker = SystemStatsWorker()
            self.sys_worker.stats_updated.connect(self.update_stats_ui)
            self.sys_worker.start()
            self.workers.append(self.sys_worker)
            
        # 2. Git
        if self.config["settings"].get("show_github", True):
            self.git_worker = GitWorker(self.config["github_repos"])
            self.git_worker.repo_updated.connect(self.update_git_ui)
            self.git_worker.start()
            self.workers.append(self.git_worker)
            
        # 3. Rclone
        if self.config["settings"].get("show_rclone", True):
            self.rc_worker = RcloneWorker(self.config["rclone_folders"])
            self.rc_worker.folder_updated.connect(self.update_rclone_ui)
            self.rc_worker.start()
            self.workers.append(self.rc_worker)

    def closeEvent(self, event):
        for w in self.workers:
            w.stop()
        super().closeEvent(event)

    # --- UI Update Slots ---

    def update_stats_ui(self, cpu, ram, c, d, up, down, cores):
        self.cpu_lbl.setText(f"{int(cpu)}%")
        self.cpu_lbl.setStyleSheet(f"color: {self.get_stat_color(cpu)};")
        
        self.ram_lbl.setText(f"{int(ram)}%")
        self.ram_lbl.setStyleSheet(f"color: {self.get_stat_color(ram)};")
        
        self.disk_lbl.setText(f"{int(c)}%")
        self.disk_lbl.setStyleSheet(f"color: {self.get_stat_color(c)};")
        
        self.net_lbl.setText(f"▲{up:.1f} ▼{down:.1f}")

    def get_stat_color(self, val):
        if val > 90: return CP_RED
        if val > 70: return CP_ORANGE
        return CP_CYAN

    def update_git_ui(self, name, status):
        if name in self.git_widgets:
            color = CP_SUBTEXT
            if status == "clean": color = CP_GREEN
            elif status == "dirty": color = CP_YELLOW
            elif status == "error": color = CP_RED
            self.git_widgets[name].setStyleSheet(f"color: {color}; font-size: 14px;")

    def update_rclone_ui(self, name, is_ok):
        if name in self.rclone_widgets:
            color = CP_GREEN if is_ok else CP_RED
            self.rclone_widgets[name].setStyleSheet(f"color: {color}; font-size: 14px;")

    # --- Grid Logic ---

    def refresh_grid(self):
        # Clear layout
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        current_scripts = self.view_stack[-1]["scripts"] if self.view_stack else self.config["scripts"]
        
        # Determine columns
        cols = self.config["settings"]["columns"]
        if self.view_stack and "grid_columns" in self.view_stack[-1]:
            c = self.view_stack[-1]["grid_columns"]
            if c > 0: cols = c
            
        # Update Title
        if self.view_stack:
            self.title_lbl.setText(f"❯ {self.view_stack[-1]['name'].upper()}")
            self.back_btn.show()
        else:
            self.title_lbl.setText("SCRIPT MANAGER 🚀")
            self.back_btn.hide()

        # Place Items
        # Simple auto-flow logic handled by QGridLayout? 
        # No, QGridLayout needs explicit row/col. We need to calculate availability for spanning.
        
        occupied = set() # (row, col)
        
        def is_free(r, c, rs, cs):
            for i in range(rs):
                for j in range(cs):
                    if c + j >= cols: return False
                    if (r + i, c + j) in occupied: return False
            return True
        
        def mark_occupied(r, c, rs, cs):
            for i in range(rs):
                for j in range(cs):
                    occupied.add((r + i, c + j))
                    
        for idx, script in enumerate(current_scripts):
            btn = ScriptButton(script, idx, self)
            btn.clicked.connect(partial(self.handle_script_click, script))
            
            col_span = script.get("col_span", 1)
            row_span = script.get("row_span", 1)
            
            # Find spot
            r, c = 0, 0
            while True:
                found = False
                for try_c in range(cols):
                    if is_free(r, try_c, row_span, col_span):
                        c = try_c
                        found = True
                        break
                if found: break
                r += 1
            
            mark_occupied(r, c, row_span, col_span)
            self.grid_layout.addWidget(btn, r, c, row_span, col_span)

    def handle_script_click(self, script):
        if script.get("type") == "folder":
            self.view_stack.append(script)
            self.refresh_grid()
        else:
            self.launch_script(script)

    def go_back(self):
        if self.view_stack:
            self.view_stack.pop()
            self.refresh_grid()

    def handle_drop(self, source_idx, target_idx):
        scripts = self.view_stack[-1]["scripts"] if self.view_stack else self.config["scripts"]
        
        if 0 <= source_idx < len(scripts) and 0 <= target_idx < len(scripts):
            item = scripts.pop(source_idx)
            scripts.insert(target_idx, item)
            self.save_config()
            self.refresh_grid()

    # --- Script Execution ---

    def launch_script(self, script):
        hide = script.get("hide_terminal", False)
        path = script.get("path", "")
        
        # Check inline
        if script.get("use_inline", False) and script.get("inline_script"):
            self.run_inline(script)
            return
            
        if not path: return

        try:
            path = os.path.expandvars(path)
            cwd = os.path.dirname(path) if os.path.isfile(path) else None
            
            flags = subprocess.CREATE_NO_WINDOW if hide else subprocess.CREATE_NEW_CONSOLE
            
            if path.endswith(".py"):
                exe = "pythonw" if hide else "python"
                subprocess.Popen([exe, path], cwd=cwd, creationflags=flags)
            elif path.endswith(".ps1"):
                exe = "pwsh" if shutil.which("pwsh") else "powershell"
                if hide:
                    subprocess.Popen([exe, "-WindowStyle", "Hidden", "-File", path], cwd=cwd, creationflags=flags)
                else:
                    cmd = f'start "" "{exe}" -NoExit -ExecutionPolicy Bypass -File "{path}"'
                    subprocess.Popen(cmd, shell=True, cwd=cwd)
            else:
                # General EXE or command
                if hide:
                    subprocess.Popen(path, shell=True, cwd=cwd, creationflags=flags)
                else:
                    subprocess.Popen(f'start "" "{path}"', shell=True, cwd=cwd)
                    
            if script.get("kill_window", False):
                self.close()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to launch:\n{e}")

    def run_inline(self, script):
        # Simplified inline runner using temp file
        import tempfile
        code = script.get("inline_script", "")
        stype = script.get("inline_type", "cmd")
        hide = script.get("hide_terminal", False)
        
        ext = ".ps1" if stype in ["pwsh", "powershell"] else ".bat"
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix=ext, delete=False, encoding='utf-8') as f:
                f.write(code)
                tmp_path = f.name
            
            flags = subprocess.CREATE_NO_WINDOW if hide else subprocess.CREATE_NEW_CONSOLE
            
            if stype in ["pwsh", "powershell"]:
                 exe = "pwsh" if shutil.which("pwsh") else "powershell"
                 if hide:
                     subprocess.Popen([exe, "-WindowStyle", "Hidden", "-File", tmp_path], creationflags=flags)
                 else:
                     subprocess.Popen(f'start "" "{exe}" -NoExit -ExecutionPolicy Bypass -File "{tmp_path}"', shell=True)
            else:
                if hide:
                     subprocess.Popen(tmp_path, shell=True, creationflags=flags)
                else:
                     subprocess.Popen(f'start "" cmd /k "{tmp_path}"', shell=True)
                     
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Inline execution failed:\n{e}")

    # --- Git / Rclone Handlers ---

    def handle_git_click(self, repo, action):
        path = repo["path"]
        try:
            if action == "gitter":
                # Assuming gitter is a known command or alias
                cmd = f"& {{cd {path} ; gitter}}"
                subprocess.Popen(["start", "pwsh", "-NoExit", "-Command", cmd], shell=True)
        except Exception as e:
            print(e)
            
    def handle_git_context(self, repo, widget, pos):
        menu = QMenu(self)
        menu.addAction("Explorer", lambda: os.startfile(repo["path"]))
        menu.addAction("LazyGit", lambda: subprocess.Popen('start pwsh -Command "lazygit"', cwd=repo["path"], shell=True))
        menu.exec(widget.mapToGlobal(pos))

    def handle_rclone_click(self, folder):
        # Open log file
        log = os.path.join(os.path.expanduser(r"~\script_output\rclone"), f"{folder['name']}_check.log")
        if os.path.exists(log):
            os.startfile(log)

    # --- Dialogs (Edit, Add, Settings) ---
    
    def open_add_dialog(self):
        # Simplified add dialog
        d = QDialog(self)
        d.setWindowTitle("ADD ITEM")
        d.setStyleSheet(f"background-color: {CP_BG}; color: {CP_TEXT};")
        l = QVBoxLayout(d)
        
        name = CyberInput("Name", d)
        l.addWidget(name)
        
        type_cb = QComboBox()
        type_cb.addItems(["Script", "Folder"])
        type_cb.setStyleSheet(f"background-color: {CP_PANEL}; color: {CP_TEXT}; border: 1px solid {CP_DIM}; padding: 5px;")
        l.addWidget(type_cb)
        
        path = CyberInput("Path (if script)", d)
        l.addWidget(path)
        
        btn = CyberButton("CREATE", color=CP_GREEN)
        btn.clicked.connect(d.accept)
        l.addWidget(btn)
        
        if d.exec():
            scripts = self.view_stack[-1]["scripts"] if self.view_stack else self.config["scripts"]
            new_item = {
                "name": name.text(),
                "type": "folder" if type_cb.currentText() == "Folder" else "script",
            }
            if new_item["type"] == "script":
                new_item["path"] = path.text()
            else:
                new_item["scripts"] = []
                
            scripts.append(new_item)
            self.save_config()
            self.refresh_grid()

    def remove_script(self, script):
        if QMessageBox.question(self, "Delete", f"Remove {script['name']}?") == QMessageBox.StandardButton.Yes:
            scripts = self.view_stack[-1]["scripts"] if self.view_stack else self.config["scripts"]
            if script in scripts:
                scripts.remove(script)
                self.save_config()
                self.refresh_grid()

    def open_edit_dialog(self, script):
        # Create a comprehensive edit dialog similar to original
        d = QDialog(self)
        d.setWindowTitle(f"EDIT // {script['name']}")
        d.resize(500, 600)
        d.setStyleSheet(f"background-color: {CP_BG}; color: {CP_TEXT};")
        
        layout = QVBoxLayout(d)
        
        # Name
        layout.addWidget(QLabel("NAME"))
        name_inp = CyberInput(script['name'])
        name_inp.setText(script['name'])
        layout.addWidget(name_inp)
        
        # Path
        path_inp = None
        if script.get("type") != "folder":
            layout.addWidget(QLabel("PATH"))
            path_inp = CyberInput(script.get('path', ''))
            path_inp.setText(script.get('path', ''))
            layout.addWidget(path_inp)
            
            # Toggles
            cb_hide = QCheckBox("Hide Terminal")
            cb_hide.setChecked(script.get("hide_terminal", False))
            cb_hide.setStyleSheet(f"color: {CP_SUBTEXT};")
            layout.addWidget(cb_hide)
            
        # Styling
        layout.addWidget(QLabel("STYLING"))
        
        # Color Pickers
        def pick_col(key, btn):
            col = QColorDialog.getColor(QColor(script.get(key, "#ffffff")), d)
            if col.isValid():
                script[key] = col.name()
                btn.setStyleSheet(f"background-color: {col.name()}; border: none;")

        h_cols = QHBoxLayout()
        btn_col = QPushButton("BG Color")
        btn_col.setStyleSheet(f"background-color: {script.get('color', '#2b2f38')};")
        btn_col.clicked.connect(lambda: pick_col('color', btn_col))
        h_cols.addWidget(btn_col)
        
        btn_txt = QPushButton("Text Color")
        btn_txt.setStyleSheet(f"background-color: {script.get('text_color', 'white')};")
        btn_txt.clicked.connect(lambda: pick_col('text_color', btn_txt))
        h_cols.addWidget(btn_txt)
        layout.addLayout(h_cols)
        
        # Size
        h_size = QHBoxLayout()
        w_inp = CyberInput("Width (0=Auto)")
        w_inp.setText(str(script.get("width", 0)))
        h_size.addWidget(w_inp)
        
        h_inp = CyberInput("Height (0=Auto)")
        h_inp.setText(str(script.get("height", 0)))
        h_size.addWidget(h_inp)
        layout.addLayout(h_size)
        
        # Spanning
        h_span = QHBoxLayout()
        cs_inp = CyberInput("Col Span")
        cs_inp.setText(str(script.get("col_span", 1)))
        h_span.addWidget(cs_inp)
        
        rs_inp = CyberInput("Row Span")
        rs_inp.setText(str(script.get("row_span", 1)))
        h_span.addWidget(rs_inp)
        layout.addLayout(h_span)

        # Save
        save_btn = CyberButton("SAVE", color=CP_YELLOW)
        def save():
            script['name'] = name_inp.text()
            if path_inp:
                script['path'] = path_inp.text()
                script['hide_terminal'] = cb_hide.isChecked()
            
            try: script['width'] = int(w_inp.text())
            except: script['width'] = 0
            try: script['height'] = int(h_inp.text())
            except: script['height'] = 0
            try: script['col_span'] = int(cs_inp.text())
            except: script['col_span'] = 1
            try: script['row_span'] = int(rs_inp.text())
            except: script['row_span'] = 1
            
            self.save_config()
            self.refresh_grid()
            d.accept()
            
        save_btn.clicked.connect(save)
        layout.addWidget(save_btn)
        
        d.exec()

    def open_settings(self):
        d = QDialog(self)
        d.setWindowTitle("SETTINGS")
        d.setStyleSheet(f"background-color: {CP_BG}; color: {CP_TEXT};")
        l = QVBoxLayout(d)
        
        cols_inp = CyberInput("Columns")
        cols_inp.setText(str(self.config["settings"]["columns"]))
        l.addWidget(QLabel("Grid Columns:"))
        l.addWidget(cols_inp)
        
        top_cb = QCheckBox("Always on Top")
        top_cb.setChecked(self.config["settings"].get("always_on_top", True))
        top_cb.setStyleSheet(f"color: {CP_TEXT};")
        l.addWidget(top_cb)
        
        btn = CyberButton("SAVE", color=CP_CYAN)
        def save():
            try: self.config["settings"]["columns"] = int(cols_inp.text())
            except: pass
            self.config["settings"]["always_on_top"] = top_cb.isChecked()
            self.save_config()
            
            if self.config["settings"]["always_on_top"]:
                self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
            else:
                self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
            self.show()
            self.refresh_grid()
            d.accept()
            
        btn.clicked.connect(save)
        l.addWidget(btn)
        d.exec()

    def duplicate_script(self, script):
        new = script.copy()
        new['name'] += " (Copy)"
        scripts = self.view_stack[-1]["scripts"] if self.view_stack else self.config["scripts"]
        scripts.append(new)
        self.save_config()
        self.refresh_grid()

    def cut_script(self, script):
        self.clipboard_script = script.copy()
        self.remove_script(script)

    def move_script_out(self, script):
        if not self.view_stack: return
        # Move from current to parent
        current_list = self.view_stack[-1]["scripts"]
        if script in current_list:
            current_list.remove(script)
            
            # Find parent list
            if len(self.view_stack) > 1:
                parent_list = self.view_stack[-2]["scripts"]
            else:
                parent_list = self.config["scripts"]
            
            parent_list.append(script)
            self.save_config()
            self.refresh_grid()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ScriptManagerApp()
    window.show()
    sys.exit(app.exec())