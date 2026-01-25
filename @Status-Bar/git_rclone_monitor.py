import sys
import os
import json
import subprocess
import threading
import time
from datetime import datetime
from PyQt6.QtWidgets import (
                             QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QLineEdit, QGroupBox, QScrollArea, 
                             QFileDialog, QDialog, QFormLayout, QMessageBox, QInputDialog,
                             QLayout, QLayoutItem, QSizePolicy, QFrame, QGraphicsDropShadowEffect,
                             QColorDialog, QSlider)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QRect, QPoint, QSize, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QFont, QFontMetrics, QColor, QIcon, QPainter, QLinearGradient

# --- CONFIGURATION & THEMES ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "projects_config.json")

DEFAULT_THEME = {
    "bg": "#050505",
    "panel": "#0d0d0d",
    "accent": "#00F0FF",
    "accent_glow": "#00F0FF",
    "text": "#E0E0E0",
    "subtext": "#808080",
    "red": "#FF003C",
    "green": "#00ff21",
    "yellow": "#FCEE0A",
    "dim": "#1a1a1a",
    "border": "#222222",
    "opacity": 0.95,
    "font_size": 13,
    "font_family": "JetBrainsMono NFP"
}

def load_full_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                config = DEFAULT_THEME.copy()
                if "theme" in data:
                    config.update(data["theme"])
                # Ensure we keep the projects
                config["git"] = data.get("git", [])
                config["rclone"] = data.get("rclone", [])
                return config
        except Exception as e:
            print(f"Error loading config: {e}")
    
    config = DEFAULT_THEME.copy()
    config["git"] = []
    config["rclone"] = []
    return config

def save_full_config(config):
    try:
        # Separate theme from projects
        projects_data = {
            "git": config.get("git", []),
            "rclone": config.get("rclone", []),
            "theme": {k: v for k, v in config.items() if k not in ["git", "rclone"]}
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(projects_data, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")

# --- CUSTOM WIDGETS ---

class GlowLabel(QLabel):
    def __init__(self, text, color="#00F0FF", glow_radius=10, font_size=12, parent=None):
        super().__init__(text, parent)
        self.color = color
        self.setStyleSheet(f"color: {color}; font-size: {font_size}pt; font-weight: bold; background: transparent;")
        
        self.glow = QGraphicsDropShadowEffect(self)
        self.glow.setBlurRadius(glow_radius)
        self.glow.setColor(QColor(color))
        self.glow.setOffset(0, 0)
        self.setGraphicsEffect(self.glow)

    def set_color(self, color):
        self.color = color
        self.setStyleSheet(f"color: {color}; background: transparent;")
        self.glow.setColor(QColor(color))

class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=-1, spacing=-1):
        super().__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)
        self.items = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.items.append(item)

    def count(self):
        return len(self.items)

    def itemAt(self, index):
        if 0 <= index < len(self.items):
            return self.items[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.items):
            return self.items.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self._do_layout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.items:
            size = size.expandedTo(item.minimumSize())
        size += QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
        return size

    def _do_layout(self, rect, test_only):
        l, t, r, b = self.getContentsMargins()
        effective_rect = rect.adjusted(+l, +t, -r, -b)
        x = effective_rect.x()
        y = effective_rect.y()
        line_height = 0

        for item in self.items:
            wid = item.widget()
            space_x = self.spacing()
            space_y = self.spacing()
            if wid:
                space_x += wid.style().layoutSpacing(QSizePolicy.ControlType.PushButton, QSizePolicy.ControlType.PushButton, Qt.Orientation.Horizontal)
                space_y += wid.style().layoutSpacing(QSizePolicy.ControlType.PushButton, QSizePolicy.ControlType.PushButton, Qt.Orientation.Vertical)

            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > effective_rect.right() and line_height > 0:
                x = effective_rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y() + b

# --- WORKERS ---

class WorkerSignals(QObject):
    finished = pyqtSignal(str, str, str) # id, type, status_color

class MonitorWorker(threading.Thread):
    def __init__(self, project_id, project_type, path, extra=None, cmd_pattern=None, colors=None):
        super().__init__()
        self.project_id = project_id
        self.project_type = project_type
        self.path = path
        self.extra = extra
        self.cmd_pattern = cmd_pattern
        self.colors = colors or DEFAULT_THEME
        self.signals = WorkerSignals()
        self.daemon = True

    def run(self):
        if self.project_type == "git":
            self.check_git()
        else:
            self.check_rclone()

    def check_git(self):
        if not os.path.exists(self.path):
            self.signals.finished.emit(self.project_id, "git", self.colors["red"])
            return
        try:
            res = subprocess.run(["git", "status"], cwd=self.path, capture_output=True, text=True, timeout=10)
            if "nothing to commit, working tree clean" in res.stdout:
                self.signals.finished.emit(self.project_id, "git", self.colors["green"])
            else:
                self.signals.finished.emit(self.project_id, "git", self.colors["red"])
        except:
            self.signals.finished.emit(self.project_id, "git", self.colors["red"])

    def check_rclone(self):
        src = self.path
        dst = self.extra
        pattern = self.cmd_pattern if self.cmd_pattern else "rclone check src dst --fast-list --size-only"
        
        try:
            actual_cmd = pattern.replace("src", f'\"{src}\"').replace("dst", f'\"{dst}\"')
            res = subprocess.run(actual_cmd, shell=True, capture_output=True, text=True, timeout=30)
            
            if res.returncode == 0 and "ERROR" not in res.stdout + res.stderr:
                self.signals.finished.emit(self.project_id, "rclone", self.colors["green"])
            else:
                self.signals.finished.emit(self.project_id, "rclone", self.colors["red"])
        except:
            self.signals.finished.emit(self.project_id, "rclone", self.colors["red"])

# --- COMPONENTS ---

class ProjectCard(QFrame):
    def __init__(self, project_id, name, p_type, path, theme, extra=None, config=None, parent=None):
        super().__init__(parent)
        self.project_id = project_id
        self.p_type = p_type
        self.name = name
        self.path = path
        self.theme = theme
        self.extra = extra # dst for rclone
        self.config = config or {}
        self.log_dir = r"C:\Users\nahid\script_output\rclone"
        
        self.setObjectName("ProjectCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)
        
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)

        # Status indicator (left border replacement)
        self.status_bar = QFrame()
        self.status_bar.setFixedWidth(4)
        self.status_bar.setStyleSheet(f"background-color: {self.theme['dim']}; border-radius: 2px;")
        layout.addWidget(self.status_bar)

        # Content info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        label_text = self.config.get("label", self.name)
        self.name_label = QLabel(label_text)
        self.name_label.setStyleSheet(f"color: {self.theme['text']}; font-weight: bold; font-size: {self.theme['font_size']}pt; background: transparent;")
        
        self.path_label = QLabel(os.path.basename(self.path))
        self.path_label.setStyleSheet(f"color: {self.theme['subtext']}; font-size: {self.theme['font_size']-4}pt; background: transparent;")
        
        info_layout.addWidget(self.name_label)
        info_layout.addWidget(self.path_label)
        layout.addLayout(info_layout)
        
        layout.addStretch()

        # Type indicator
        type_icon = "\udb80\udf1b" if self.p_type == "git" else "\udb81\udc9d" # Git vs Cloud icons
        self.type_label = QLabel(type_icon)
        self.type_label.setStyleSheet(f"color: {self.theme['dim']}; font-size: 14pt; background: transparent;")
        layout.addWidget(self.type_label)

        self.update_style(False)

    def update_style(self, hovered):
        bg = "#1a1a1a" if hovered else self.theme['panel']
        border = self.theme['accent'] if hovered else self.theme['border']
        self.setStyleSheet(f"""
            #ProjectCard {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 4px;
            }}
        """)

    def enterEvent(self, event):
        self.update_style(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.update_style(False)
        super().leaveEvent(event)

    def update_status(self, color):
        self.status_bar.setStyleSheet(f"background-color: {color}; border-radius: 2px;")
        # Apply glow to status bar
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(10)
        glow.setColor(QColor(color))
        glow.setOffset(0, 0)
        self.status_bar.setGraphicsEffect(glow)
        
        self.type_label.setStyleSheet(f"color: {color}; font-size: 14pt; background: transparent;")

    def sizeHint(self):
        fm = QFontMetrics(self.name_label.font())
        text_width = fm.horizontalAdvance(self.name_label.text())
        width = max(text_width + 100, 150)
        return QSize(width, 50)

    def mousePressEvent(self, event):
        modifiers = event.modifiers()
        is_ctrl = modifiers & Qt.KeyboardModifier.ControlModifier
        is_shift = modifiers & Qt.KeyboardModifier.ShiftModifier
        
        if event.button() == Qt.MouseButton.RightButton and is_shift:
            self.parent().parent().parent().parent().parent().delete_project(self.project_id, self.p_type)
            return
        
        if event.button() == Qt.MouseButton.LeftButton:
            if self.p_type == "git":
                if is_ctrl:
                    subprocess.Popen(f'explorer "{self.path.replace("/", "\\")}"', shell=True)
                else:
                    self.run_gitter()
            else: # rclone
                if is_ctrl:
                    pattern = self.config.get("left_click_cmd", "rclone sync src dst -P --fast-list --log-level INFO")
                    cmd = pattern.replace("src", f'\"{self.path}\"').replace("dst", f'\"{self.extra}\"')
                    subprocess.Popen(f'start pwsh -NoExit -Command "{cmd}"', shell=True)
                else:
                    log_path = os.path.join(self.log_dir, f"{self.name}_check.log")
                    if os.path.exists(log_path):
                        subprocess.Popen(["powershell", "-NoExit", "-Command", f'edit "{log_path}"'], creationflags=subprocess.CREATE_NEW_CONSOLE)

        elif event.button() == Qt.MouseButton.RightButton:
            if self.p_type == "git":
                if is_ctrl:
                    subprocess.Popen(f'start pwsh -NoExit -Command "& {{ $host.UI.RawUI.WindowTitle=\'Git Restore\' ; cd \'{self.path}\' ; git restore .}}"', shell=True)
                else:
                    subprocess.Popen('start pwsh -NoExit -Command "lazygit"', cwd=self.path, shell=True)
            else: # rclone
                if is_ctrl:
                    pattern = self.config.get("right_click_cmd", "rclone sync dst src -P --fast-list")
                    cmd = pattern.replace("src", f'\"{self.path}\"').replace("dst", f'\"{self.extra}\"')
                    subprocess.Popen(f'start pwsh -NoExit -Command "{cmd}"', shell=True)

    def run_gitter(self):
        msg, ok = QInputDialog.getText(self, "GIT COMMIT", "Enter commit message:")
        if not ok: return
        commit_msg = msg if msg.strip() else "Auto-commit"
        pwsh_logic = f"cd '{self.path}'; git add .; git commit -m '{commit_msg}'; git push;"
        subprocess.Popen(f'start pwsh -NoExit -Command "{pwsh_logic}"', shell=True)

# --- DIALOGS ---

class SettingsDialog(QDialog):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme.copy()
        self.setWindowTitle("SYSTEM SETTINGS")
        self.setFixedWidth(450)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {self.theme['bg']}; color: {self.theme['text']}; font-family: '{self.theme['font_family']}'; }}
            QLabel {{ color: {self.theme['subtext']}; }}
            QLineEdit {{ background-color: {self.theme['panel']}; color: {self.theme['accent']}; border: 1px solid {self.theme['dim']}; padding: 5px; }}
            QPushButton {{ background-color: {self.theme['dim']}; border: 1px solid {self.theme['dim']}; color: white; padding: 8px; font-weight: bold; }}
            QPushButton:hover {{ border: 1px solid {self.theme['accent']}; color: {self.theme['accent']}; }}
        """)
        
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.font_family_input = QLineEdit(self.theme['font_family'])
        self.font_size_input = QLineEdit(str(self.theme['font_size']))
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(50, 100)
        self.opacity_slider.setValue(int(self.theme['opacity'] * 100))
        
        self.accent_btn = QPushButton("PICK COLOR")
        self.accent_btn.clicked.connect(self.pick_accent)
        self.update_accent_btn()
        
        form.addRow("FONT FAMILY:", self.font_family_input)
        form.addRow("FONT SIZE:", self.font_size_input)
        form.addRow("WINDOW OPACITY:", self.opacity_slider)
        form.addRow("ACCENT COLOR:", self.accent_btn)
        
        layout.addLayout(form)
        
        btns = QHBoxLayout()
        reset_btn = QPushButton("RESET")
        reset_btn.clicked.connect(self.reset_defaults)
        save_btn = QPushButton("SAVE")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("CANCEL")
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(reset_btn)
        btns.addStretch()
        btns.addWidget(save_btn)
        btns.addWidget(cancel_btn)
        layout.addLayout(btns)

    def update_accent_btn(self):
        self.accent_btn.setStyleSheet(f"background-color: {self.theme['accent']}; color: black; font-weight: bold; border: none;")

    def pick_accent(self):
        color = QColorDialog.getColor(QColor(self.theme['accent']), self)
        if color.isValid():
            self.theme['accent'] = color.name()
            self.theme['accent_glow'] = color.name()
            self.update_accent_btn()

    def reset_defaults(self):
        self.theme.update(DEFAULT_THEME)
        self.font_family_input.setText(self.theme['font_family'])
        self.font_size_input.setText(str(self.theme['font_size']))
        self.opacity_slider.setValue(int(self.theme['opacity'] * 100))
        self.update_accent_btn()

    def get_settings(self):
        try:
            self.theme['font_family'] = self.font_family_input.text()
            self.theme['font_size'] = int(self.font_size_input.text())
            self.theme['opacity'] = self.opacity_slider.value() / 100.0
            return self.theme
        except:
            return None

class AddProjectDialog(QDialog):
    def __init__(self, mode, theme, parent=None):
        super().__init__(parent)
        self.mode = mode
        self.theme = theme
        self.setWindowTitle(f"ADD {mode.upper()}")
        self.setFixedWidth(500)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {theme['bg']}; color: {theme['text']}; font-family: '{theme['font_family']}'; }}
            QLineEdit {{ background-color: {theme['panel']}; color: {theme['accent']}; border: 1px solid {theme['dim']}; padding: 5px; }}
            QPushButton {{ background-color: {theme['dim']}; border: 1px solid {theme['dim']}; color: white; padding: 6px; }}
        """)
        
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.name_input = QLineEdit()
        self.label_input = QLineEdit()
        self.path_input = QLineEdit()
        browse_btn = QPushButton("...")
        browse_btn.setFixedWidth(30)
        browse_btn.clicked.connect(self.browse_path)
        
        path_box = QHBoxLayout()
        path_box.addWidget(self.path_input)
        path_box.addWidget(browse_btn)
        
        form.addRow("NAME:", self.name_input)
        form.addRow("LABEL:", self.label_input)
        form.addRow("PATH:", path_box)
        
        if mode == "rclone":
            self.dst_input = QLineEdit()
            self.cmd_input = QLineEdit("rclone check src dst --fast-list --size-only")
            form.addRow("REMOTE:", self.dst_input)
            form.addRow("COMMAND:", self.cmd_input)
        
        layout.addLayout(form)
        
        btns = QHBoxLayout()
        add_btn = QPushButton("CONFIRM")
        add_btn.clicked.connect(self.accept)
        layout.addWidget(add_btn)

    def browse_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if path: self.path_input.setText(path)

    def get_data(self):
        data = {
            "name": self.name_input.text(),
            "label": self.label_input.text() or self.name_input.text(),
            "path": self.path_input.text()
        }
        if self.mode == "rclone":
            data["dst"] = self.dst_input.text()
            data["cmd"] = self.cmd_input.text()
        return data

# --- MAIN WINDOW ---

class GitRcloneMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = load_full_config()
        self.theme = self.config
        
        self.setWindowTitle("CYBER_MONITOR_X")
        self.resize(550, 850)
        self.setWindowOpacity(self.theme.get("opacity", 0.95))
        
        self.drag_pos = QPoint()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.init_ui()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_all)
        self.timer.start(300000) 
        QTimer.singleShot(1000, self.refresh_all)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def init_ui(self):
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: transparent; }}
            #MainContainer {{
                background-color: {self.theme['bg']};
                border: 1px solid {self.theme['accent']};
                border-radius: 10px;
            }}
            QWidget {{ color: {self.theme['text']}; font-family: '{self.theme['font_family']}'; }}
            QScrollArea {{ background: transparent; border: none; }}
            QGroupBox {{
                border: 1px solid {self.theme['border']};
                margin-top: 15px;
                padding-top: 10px;
                font-weight: bold;
                color: {self.theme['accent']};
                text-transform: uppercase;
                letter-spacing: 2px;
            }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 5px; }}
        """)
        
        central = QWidget()
        central.setObjectName("MainContainer")
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Header
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        self.title_label = GlowLabel("NEURAL_LINK_MONITOR", self.theme['accent'], 15, 18)
        self.status_summary = QLabel("ALL SYSTEMS NOMINAL")
        self.status_summary.setStyleSheet(f"color: {self.theme['subtext']}; font-size: 8pt; letter-spacing: 1px;")
        title_box.addWidget(self.title_label)
        title_box.addWidget(self.status_summary)
        
        header.addLayout(title_box)
        header.addStretch()
        
        self.settings_btn = QPushButton("\udb84\udf3e") # Gear icon
        self.settings_btn.setFixedSize(40, 40)
        self.settings_btn.clicked.connect(self.show_settings)
        self.settings_btn.setStyleSheet(f"background: {self.theme['dim']}; border-radius: 20px; font-size: 16pt; color: {self.theme['accent']}; border: none;")
        header.addWidget(self.settings_btn)

        self.close_btn = QPushButton("\u2715") # X icon
        self.close_btn.setFixedSize(40, 40)
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setStyleSheet(f"background: {self.theme['red']}; border-radius: 20px; font-size: 14pt; color: white; border: none; margin-left: 5px;")
        header.addWidget(self.close_btn)
        
        main_layout.addLayout(header)

        # GIT Section
        git_group = QGroupBox("Git Infrastructure")
        git_layout = QVBoxLayout()
        scroll_git = QScrollArea()
        scroll_git.setWidgetResizable(True)
        self.git_container = QWidget()
        self.git_flow = FlowLayout(self.git_container, 5, 8)
        scroll_git.setWidget(self.git_container)
        git_layout.addWidget(scroll_git)
        
        add_git = QPushButton("+ INITIALIZE REPO")
        add_git.clicked.connect(lambda: self.show_add_dialog("git"))
        add_git.setStyleSheet(f"background: {self.theme['panel']}; border: 1px dashed {self.theme['dim']}; color: {self.theme['subtext']}; padding: 5px;")
        git_layout.addWidget(add_git)
        
        git_group.setLayout(git_layout)
        main_layout.addWidget(git_group)

        # RCLONE Section
        rclone_group = QGroupBox("Cloud Sync Nodes")
        rclone_layout = QVBoxLayout()
        scroll_rc = QScrollArea()
        scroll_rc.setWidgetResizable(True)
        self.rc_container = QWidget()
        self.rc_flow = FlowLayout(self.rc_container, 5, 8)
        scroll_rc.setWidget(self.rc_container)
        rclone_layout.addWidget(scroll_rc)
        
        add_rc = QPushButton("+ DEPLOY NODE")
        add_rc.clicked.connect(lambda: self.show_add_dialog("rclone"))
        add_rc.setStyleSheet(f"background: {self.theme['panel']}; border: 1px dashed {self.theme['dim']}; color: {self.theme['subtext']}; padding: 5px;")
        rclone_layout.addWidget(add_rc)
        
        rclone_group.setLayout(rclone_layout)
        main_layout.addWidget(rclone_group)

        # Footer
        footer = QHBoxLayout()
        self.last_refresh = QLabel("LAST SCAN: NEVER")
        self.last_refresh.setStyleSheet(f"color: {self.theme['subtext']}; font-size: 7pt;")
        
        refresh_btn = QPushButton("RUN SYSTEM DIAGNOSTICS")
        refresh_btn.clicked.connect(self.refresh_all)
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme['accent']};
                color: black;
                font-weight: bold;
                padding: 10px;
                border-radius: 2px;
            }}
            QPushButton:hover {{
                background-color: white;
            }}
        """)
        
        footer.addWidget(self.last_refresh)
        footer.addStretch()
        footer.addWidget(refresh_btn)
        main_layout.addLayout(footer)

        self.project_widgets = {"git": {}, "rclone": {}}
        self.populate_lists()

    def populate_lists(self):
        # Clear
        for i in reversed(range(self.git_flow.count())):
            self.git_flow.itemAt(i).widget().setParent(None)
        for i in reversed(range(self.rc_flow.count())):
            self.rc_flow.itemAt(i).widget().setParent(None)
            
        self.project_widgets = {"git": {}, "rclone": {}}
        
        for idx, p in enumerate(self.config.get("git", [])):
            pid = f"git_{idx}"
            w = ProjectCard(pid, p["name"], "git", p["path"], self.theme, config=p)
            self.git_flow.addWidget(w)
            self.project_widgets["git"][pid] = w
            
        for idx, p in enumerate(self.config.get("rclone", [])):
            pid = f"rclone_{idx}"
            w = ProjectCard(pid, p["name"], "rclone", p["path"], self.theme, extra=p.get("dst"), config=p)
            self.rc_flow.addWidget(w)
            self.project_widgets["rclone"][pid] = w

    def show_settings(self):
        dialog = SettingsDialog(self.theme, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_theme = dialog.get_settings()
            if new_theme:
                # Update config with new theme values
                for k, v in new_theme.items():
                    self.config[k] = v
                save_full_config(self.config)
                self.theme = self.config
                self.setWindowOpacity(self.theme['opacity'])
                self.init_ui()
                self.populate_lists()
                self.refresh_all()

    def show_add_dialog(self, mode):
        dialog = AddProjectDialog(mode, self.theme, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data["name"]:
                self.config[mode].append(data)
                save_full_config(self.config)
                self.populate_lists()
                self.refresh_all()

    def delete_project(self, project_id, p_type):
        idx = int(project_id.split("_")[1])
        if 0 <= idx < len(self.config[p_type]):
            del self.config[p_type][idx]
            save_full_config(self.config)
            self.populate_lists()

    def refresh_all(self):
        self.last_refresh.setText("SCANNING...")
        self.status_summary.setText("SCANNING INFRASTRUCTURE...")
        
        for pid, w in self.project_widgets["git"].items():
            w.update_status(self.theme["dim"])
            worker = MonitorWorker(pid, "git", w.path, colors=self.theme)
            worker.signals.finished.connect(self.on_check_finished)
            worker.start()
            
        for pid, w in self.project_widgets["rclone"].items():
            w.update_status(self.theme["dim"])
            worker = MonitorWorker(pid, "rclone", w.path, w.extra, w.config.get("cmd"), colors=self.theme)
            worker.signals.finished.connect(self.on_check_finished)
            worker.start()
        
        now = datetime.now().strftime("%H:%M:%S")
        self.last_refresh.setText(f"LAST SCAN: {now}")

    def on_check_finished(self, pid, p_type, color):
        if pid in self.project_widgets[p_type]:
            self.project_widgets[p_type][pid].update_status(color)
            
        # Update global status summary if any red
        any_error = False
        for type_widgets in self.project_widgets.values():
            for w in type_widgets.values():
                # This is a bit hacky to check color
                if "background-color: #FF003C" in w.status_bar.styleSheet():
                    any_error = True
                    break
        
        if any_error:
            self.status_summary.setText("CRITICAL: DISCREPANCIES DETECTED")
            self.status_summary.setStyleSheet(f"color: {self.theme['red']}; font-size: 8pt; letter-spacing: 1px;")
        else:
            self.status_summary.setText("ALL SYSTEMS NOMINAL")
            self.status_summary.setStyleSheet(f"color: {self.theme['subtext']}; font-size: 8pt; letter-spacing: 1px;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GitRcloneMonitor()
    window.show()
    sys.exit(app.exec())