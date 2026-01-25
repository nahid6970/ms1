import sys
import os
import json
import subprocess
import threading
import time
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QGroupBox,
    QScrollArea,
    QFileDialog,
    QDialog,
    QFormLayout,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject

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

CONFIG_FILE = "projects_config.json"

class WorkerSignals(QObject):
    finished = pyqtSignal(str, str, str) # id, type, status_color

class MonitorWorker(threading.Thread):
    def __init__(self, project_id, project_type, path, extra=None):
        super().__init__()
        self.project_id = project_id
        self.project_type = project_type
        self.path = path
        self.extra = extra
        self.signals = WorkerSignals()
        self.daemon = True

    def run(self):
        if self.project_type == "git":
            self.check_git()
        else:
            self.check_rclone()

    def check_git(self):
        if not os.path.exists(self.path):
            self.signals.finished.emit(self.project_id, "git", CP_RED)
            return
        try:
            res = subprocess.run(["git", "status"], cwd=self.path, capture_output=True, text=True, timeout=10)
            if "nothing to commit, working tree clean" in res.stdout:
                self.signals.finished.emit(self.project_id, "git", CP_GREEN)
            else:
                self.signals.finished.emit(self.project_id, "git", CP_RED)
        except:
            self.signals.finished.emit(self.project_id, "git", CP_RED)

    def check_rclone(self):
        # extra is dst
        src = self.path
        dst = self.extra
        try:
            # Using size-only for speed as in mypygui.py
            cmd = ["rclone", "check", src, dst, "--fast-list", "--size-only"]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if res.returncode == 0:
                self.signals.finished.emit(self.project_id, "rclone", CP_GREEN)
            else:
                self.signals.finished.emit(self.project_id, "rclone", CP_RED)
        except:
            self.signals.finished.emit(self.project_id, "rclone", CP_RED)

class AddProjectDialog(QDialog):
    def __init__(self, mode="git", parent=None):
        super().__init__(parent)
        self.mode = mode
        self.setWindowTitle(f"ADD NEW {mode.upper()} PROJECT")
        self.setFixedWidth(400)
        self.setStyleSheet(f"background-color: {CP_BG}; color: {CP_TEXT}; font-family: 'Consolas';")
        
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.name_input = QLineEdit()
        self.path_input = QLineEdit()
        self.browse_btn = QPushButton("BROWSE")
        self.browse_btn.clicked.connect(self.browse_path)
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_btn)
        
        form.addRow("NAME:", self.name_input)
        form.addRow("PATH/SRC:", path_layout)
        
        if mode == "rclone":
            self.dst_input = QLineEdit()
            form.addRow("REMOTE/DST:", self.dst_input)
        
        layout.addLayout(form)
        
        btns = QHBoxLayout()
        self.add_btn = QPushButton("ADD")
        self.add_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("CANCEL")
        self.cancel_btn.clicked.connect(self.reject)
        btns.addWidget(self.add_btn)
        btns.addWidget(self.cancel_btn)
        layout.addLayout(btns)
        
        for widget in [self.name_input, self.path_input]:
            widget.setStyleSheet(f"background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px;")
        if mode == "rclone":
            self.dst_input.setStyleSheet(f"background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px;")

    def browse_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if path:
            self.path_input.setText(path)

    def get_data(self):
        data = {
            "name": self.name_input.text(),
            "path": self.path_input.text()
        }
        if self.mode == "rclone":
            data["dst"] = self.dst_input.text()
        return data

class ProjectWidget(QWidget):
    def __init__(self, project_id, name, p_type, path, extra=None, parent=None):
        super().__init__(parent)
        self.project_id = project_id
        self.p_type = p_type
        self.name = name
        self.path = path
        self.extra = extra # dst for rclone
        self.log_dir = r"C:\Users\nahid\script_output\rclone"
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet(f"color: {CP_DIM}; font-size: 14pt;")
        
        self.name_label = QLabel(name)
        self.name_label.setStyleSheet(f"font-weight: bold; color: {CP_TEXT};")
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(self.get_tooltip())
        
        layout.addWidget(self.status_indicator)
        layout.addWidget(self.name_label)
        layout.addStretch()
        
        self.setStyleSheet(f"QWidget:hover {{ background-color: {CP_PANEL}; }}")

    def get_tooltip(self):
        if self.p_type == "git":
            return "L-Click: Gitter | Ctrl+L: Explorer | R-Click: Lazygit | Ctrl+R: Git Restore"
        else:
            return "L-Click: View Log | Ctrl+L: Sync Push | Ctrl+R: Sync Pull"

    def mousePressEvent(self, event):
        modifiers = event.modifiers()
        is_ctrl = modifiers & Qt.KeyboardModifier.ControlModifier
        
        if event.button() == Qt.MouseButton.LeftButton:
            if self.p_type == "git":
                if is_ctrl:
                    subprocess.Popen(f'explorer "{self.path.replace("/", "\\")}"', shell=True)
                else:
                    subprocess.Popen(f'start pwsh -NoExit -Command "& {{$host.UI.RawUI.WindowTitle=\'GiTSync\' ; cd \'{self.path}\' ; gitter}}"', shell=True)
            else: # rclone
                if is_ctrl:
                    cmd = f'rclone sync "{self.path}" "{self.extra}" -P --fast-list --log-level INFO'
                    subprocess.Popen(f'start pwsh -NoExit -Command "{cmd}"', shell=True)
                else:
                    log_path = os.path.join(self.log_dir, f"{self.name}_check.log")
                    if os.path.exists(log_path):
                        subprocess.Popen(["powershell", "-NoExit", "-Command", f'edit "{log_path}"'], creationflags=subprocess.CREATE_NEW_CONSOLE)
                    else:
                        print(f"Log not found: {log_path}")

        elif event.button() == Qt.MouseButton.RightButton:
            if self.p_type == "git":
                if is_ctrl:
                    subprocess.Popen(f'start pwsh -NoExit -Command "& {{$host.UI.RawUI.WindowTitle=\'Git Restore\' ; cd \'{self.path}\' ; git restore .}}"', shell=True)
                else:
                    subprocess.Popen('start pwsh -NoExit -Command "lazygit"', cwd=self.path, shell=True)
            else: # rclone
                if is_ctrl:
                    cmd = f'rclone sync "{self.extra}" "{self.path}" -P --fast-list'
                    subprocess.Popen(f'start pwsh -NoExit -Command "{cmd}"', shell=True)

    def update_status(self, color):
        self.status_indicator.setStyleSheet(f"color: {color}; font-size: 14pt;")



class GitRcloneMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CYBER_MONITOR v1.0")
        self.resize(600, 800)
        self.projects = {"git": [], "rclone": []}
        self.load_config()
        
        self.init_ui()
        
        # Timer for periodic checks (every 5 minutes)
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_all)
        self.timer.start(300000) 
        
        # Initial check
        QTimer.singleShot(1000, self.refresh_all)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    self.projects = json.load(f)
            except:
                pass

    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.projects, f, indent=4)

    def init_ui(self):
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            QGroupBox {{
                border: 1px solid {CP_DIM}; margin-top: 15px; padding-top: 10px; font-weight: bold; color: {CP_YELLOW};
            }}
            QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }}
            QScrollArea {{ background: transparent; border: none; }}
            QLineEdit {{
                background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px;
            }}
            QPushButton#MainBtn {{
                background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 10px; font-weight: bold;
            }}
            QPushButton#MainBtn:hover {{
                border: 1px solid {CP_CYAN}; color: {CP_CYAN};
            }}
        """)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        header = QLabel("SYSTEM MONITORING INTERFACE")
        header.setStyleSheet(f"font-size: 16pt; color: {CP_CYAN}; font-weight: bold; margin-bottom: 10px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)
        
        # GIT SECTION
        self.git_group = QGroupBox("GIT_REPOSITORIES")
        self.git_layout = QVBoxLayout()
        self.git_scroll = QScrollArea()
        self.git_container = QWidget()
        self.git_list_layout = QVBoxLayout(self.git_container)
        self.git_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.git_scroll.setWidget(self.git_container)
        self.git_scroll.setWidgetResizable(True)
        
        self.git_layout.addWidget(self.git_scroll)
        self.add_git_btn = QPushButton("+ ADD GIT REPO")
        self.add_git_btn.setObjectName("MainBtn")
        self.add_git_btn.clicked.connect(lambda: self.show_add_dialog("git"))
        self.git_layout.addWidget(self.add_git_btn)
        self.git_group.setLayout(self.git_layout)
        main_layout.addWidget(self.git_group)
        
        # RCLONE SECTION
        self.rclone_group = QGroupBox("RCLONE_SYNC_TASKS")
        self.rclone_layout = QVBoxLayout()
        self.rclone_scroll = QScrollArea()
        self.rclone_container = QWidget()
        self.rclone_list_layout = QVBoxLayout(self.rclone_container)
        self.rclone_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.rclone_scroll.setWidget(self.rclone_container)
        self.rclone_scroll.setWidgetResizable(True)
        
        self.rclone_layout.addWidget(self.rclone_scroll)
        self.add_rclone_btn = QPushButton("+ ADD RCLONE TASK")
        self.add_rclone_btn.setObjectName("MainBtn")
        self.add_rclone_btn.clicked.connect(lambda: self.show_add_dialog("rclone"))
        self.rclone_layout.addWidget(self.add_rclone_btn)
        self.rclone_group.setLayout(self.rclone_layout)
        main_layout.addWidget(self.rclone_group)
        
        # FOOTER
        footer = QHBoxLayout()
        self.refresh_btn = QPushButton("FORCE REFRESH")
        self.refresh_btn.clicked.connect(self.refresh_all)
        self.refresh_btn.setStyleSheet(f"background-color: {CP_RED}; color: white; font-weight: bold; padding: 5px;")
        footer.addStretch()
        footer.addWidget(self.refresh_btn)
        main_layout.addLayout(footer)
        
        self.project_widgets = {}
        self.populate_lists()

    def populate_lists(self):
        # Clear existing
        for i in reversed(range(self.git_list_layout.count())):
            self.git_list_layout.itemAt(i).widget().setParent(None)
        for i in reversed(range(self.rclone_list_layout.count())):
            self.rclone_list_layout.itemAt(i).widget().setParent(None)
        
        self.project_widgets = {"git": {}, "rclone": {}}
        
        for idx, p in enumerate(self.projects["git"]):
            pid = f"git_{idx}"
            w = ProjectWidget(pid, p["name"], "git", p["path"])
            self.git_list_layout.addWidget(w)
            self.project_widgets["git"][pid] = w
            
        for idx, p in enumerate(self.projects["rclone"]):
            pid = f"rclone_{idx}"
            w = ProjectWidget(pid, p["name"], "rclone", p["path"], p["dst"])
            self.rclone_list_layout.addWidget(w)
            self.project_widgets["rclone"][pid] = w

    def show_add_dialog(self, mode):
        dialog = AddProjectDialog(mode, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data["name"] and data["path"]:
                self.projects[mode].append(data)
                self.save_config()
                self.populate_lists()
                self.refresh_all()

    def refresh_all(self):
        for pid, w in self.project_widgets["git"].items():
            w.update_status(CP_DIM)
            worker = MonitorWorker(pid, "git", w.path)
            worker.signals.finished.connect(self.on_check_finished)
            worker.start()
            
        for pid, w in self.project_widgets["rclone"].items():
            w.update_status(CP_DIM)
            worker = MonitorWorker(pid, "rclone", w.path, w.extra)
            worker.signals.finished.connect(self.on_check_finished)
            worker.start()

    def on_check_finished(self, pid, p_type, color):
        if pid in self.project_widgets[p_type]:
            self.project_widgets[p_type][pid].update_status(color)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GitRcloneMonitor()
    window.show()
    sys.exit(app.exec())
