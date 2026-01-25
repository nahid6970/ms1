import sys
import os
import json
import subprocess
import threading
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QLineEdit, QGroupBox, QScrollArea, 
                             QFileDialog, QDialog, QFormLayout, QMessageBox, QInputDialog,
                             QLayout, QLayoutItem, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QRect, QPoint, QSize

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

# Get the directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "projects_config.json")

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

class WorkerSignals(QObject):
    finished = pyqtSignal(str, str, str) # id, type, status_color

class MonitorWorker(threading.Thread):
    def __init__(self, project_id, project_type, path, extra=None, cmd_pattern=None):
        super().__init__()
        self.project_id = project_id
        self.project_type = project_type
        self.path = path
        self.extra = extra
        self.cmd_pattern = cmd_pattern
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
        src = self.path
        dst = self.extra
        pattern = self.cmd_pattern if self.cmd_pattern else "rclone check src dst --fast-list --size-only"
        
        try:
            actual_cmd = pattern.replace("src", f'"{src}"').replace("dst", f'"{dst}"')
            res = subprocess.run(actual_cmd, shell=True, capture_output=True, text=True, timeout=30)
            
            # The logic in mypygui.py uses "ERROR" check in the log output
            if res.returncode == 0 and "ERROR" not in res.stdout + res.stderr:
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
        self.setFixedWidth(500)
        self.setStyleSheet(f"background-color: {CP_BG}; color: {CP_TEXT}; font-family: 'JetBrainsMono NFP';")
        
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.name_input = QLineEdit()
        self.label_input = QLineEdit()
        self.path_input = QLineEdit()
        self.browse_btn = QPushButton("BROWSE")
        self.browse_btn.clicked.connect(self.browse_path)
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_btn)
        
        form.addRow("NAME:", self.name_input)
        form.addRow("UI LABEL:", self.label_input)
        form.addRow("PATH/SRC:", path_layout)
        
        if mode == "rclone":
            self.dst_input = QLineEdit()
            self.cmd_input = QLineEdit("rclone check src dst --fast-list --size-only")
            self.l_cmd_input = QLineEdit("rclone sync src dst -P --fast-list --log-level INFO")
            self.r_cmd_input = QLineEdit("rclone sync dst src -P --fast-list")
            
            form.addRow("REMOTE/DST:", self.dst_input)
            form.addRow("CHECK CMD:", self.cmd_input)
            form.addRow("CTRL+L CMD:", self.l_cmd_input)
            form.addRow("CTRL+R CMD:", self.r_cmd_input)
        
        layout.addLayout(form)
        
        btns = QHBoxLayout()
        self.add_btn = QPushButton("ADD")
        self.add_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("CANCEL")
        self.cancel_btn.clicked.connect(self.reject)
        btns.addWidget(self.add_btn)
        btns.addWidget(self.cancel_btn)
        layout.addLayout(btns)
        
        inputs = [self.name_input, self.label_input, self.path_input]
        if mode == "rclone":
            inputs.extend([self.dst_input, self.cmd_input, self.l_cmd_input, self.r_cmd_input])
            
        for widget in inputs:
            widget.setStyleSheet(f"background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px;")

    def browse_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if path:
            self.path_input.setText(path)

    def get_data(self):
        data = {
            "name": self.name_input.text(),
            "label": self.label_input.text() if self.label_input.text() else self.name_input.text(),
            "path": self.path_input.text()
        }
        if self.mode == "rclone":
            data["dst"] = self.dst_input.text()
            data["cmd"] = self.cmd_input.text()
            data["left_click_cmd"] = self.l_cmd_input.text()
            data["right_click_cmd"] = self.r_cmd_input.text()
        return data

class ProjectWidget(QWidget):
    def __init__(self, project_id, name, p_type, path, extra=None, parent=None, config=None):
        super().__init__(parent)
        self.project_id = project_id
        self.p_type = p_type
        self.name = name
        self.path = path
        self.extra = extra # dst for rclone
        self.config = config or {}
        self.log_dir = r"C:\Users\nahid\script_output\rclone"
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        label_text = self.config.get("label", name)
        self.name_label = QLabel(f"⟳ {label_text}")
        self.name_label.setStyleSheet(f"font-weight: bold; color: {CP_DIM}; font-size: 10pt; font-family: 'JetBrainsMono NFP'; border: none; background: transparent;")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setWordWrap(False) # Keep it single line for compactness
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(self.get_tooltip())
        
        layout.addWidget(self.name_label)

        # Added padding to the widget to prevent border clipping
        self.setStyleSheet(f"""
            ProjectWidget {{ 
                background-color: {CP_PANEL}; 
                border: 1px solid {CP_DIM}; 
                border-radius: 4px; 
                margin: 2px;
            }}
            ProjectWidget:hover {{ 
                border: 1px solid {CP_CYAN}; 
            }}
        """)
        self.setFixedHeight(34)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

    def sizeHint(self):
        # Dynamic width based on text
        width = self.name_label.fontMetrics().boundingRect(self.name_label.text()).width() + 30
        return QSize(max(width, 80), 34)

    def get_tooltip(self):
        if self.p_type == "git":
            return f"Path: {self.path}\\nL-Click: Gitter | Ctrl+L: Explorer | R-Click: Lazygit | Ctrl+R: Git Restore"
        else:
            return f"Src: {self.path}\\nDst: {self.extra}\\nL-Click: View Log | Ctrl+L: Sync Push | Ctrl+R: Sync Pull"

    def mousePressEvent(self, event):
        modifiers = event.modifiers()
        is_ctrl = modifiers & Qt.KeyboardModifier.ControlModifier
        
        if event.button() == Qt.MouseButton.LeftButton:
            if self.p_type == "git":
                if is_ctrl:
                    subprocess.Popen(f'explorer "{self.path.replace("/", "\\")}"', shell=True)
                else:
                    self.run_gitter()
            else: # rclone
                if is_ctrl:
                    pattern = self.config.get("left_click_cmd", "rclone sync src dst -P --fast-list --log-level INFO")
                    cmd = pattern.replace("src", f'"{self.path}"').replace("dst", f'"{self.extra}"')
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
                    pattern = self.config.get("right_click_cmd", "rclone sync dst src -P --fast-list")
                    cmd = pattern.replace("src", f'"{self.path}"').replace("dst", f'"{self.extra}"')
                    subprocess.Popen(f'start pwsh -NoExit -Command "{cmd}"', shell=True)

    def run_gitter(self):
        msg, ok = QInputDialog.getText(self, "GIT COMMIT", "Enter commit message (Leave empty for 'Auto-commit'):")
        if not ok:
            return
        
        commit_msg = msg.replace("'", "''") if msg.strip() else "Auto-commit"
        
        # Mimic the gitter function logic and output
        # Using a single string with semicolons for the pwsh command
        pwsh_logic = (
            f"cd '{self.path}'; "
            "Write-Host '--- GIT STATUS ---' -ForegroundColor Cyan; "
            "git status; "
            "Write-Host '--- STAGING & COMMITTING ---' -ForegroundColor Cyan; "
            "git add .; "
            f"git commit -m '{commit_msg}'; "
            "Write-Host '--- PUSHING ---' -ForegroundColor Cyan; "
            "git push; "
            "Write-Host '--- COMPLETE ---' -ForegroundColor Green; "
            "Write-Host 'G I T T E R' -ForegroundColor Green -BackgroundColor Black; "
            "Write-Host 'SUCCESSFULLY SYNCED' -ForegroundColor Green;"
        )
        
        full_cmd = f'start pwsh -NoExit -Command "{pwsh_logic}"'
        subprocess.Popen(full_cmd, shell=True)

    def update_status(self, color):
        if color == CP_GREEN:
            sym = "✓"
        elif color == CP_RED:
            sym = "✗"
        else:
            sym = "⟳"
        
        label_text = self.config.get("label", self.name)
        self.name_label.setText(f"{sym} {label_text}")
        self.name_label.setStyleSheet(f"font-weight: bold; color: {color}; font-size: 10pt; font-family: 'JetBrainsMono NFP'; border: none; background: transparent;")
        self.updateGeometry()



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
        self.projects = {"git": [], "rclone": []}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.projects["git"] = data.get("git", [])
                        self.projects["rclone"] = data.get("rclone", [])
            except Exception as e:
                print(f"Error loading config: {e}")

    def save_config(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.projects, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def init_ui(self):
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'JetBrainsMono NFP'; font-size: 9pt; }}
            QGroupBox {{
                border: 1px solid {CP_DIM}; margin-top: 12px; padding-top: 8px; font-weight: bold; color: {CP_YELLOW};
            }}
            QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }}
            QScrollArea {{ background: transparent; border: none; }}
            QLineEdit {{
                background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px; font-family: 'JetBrainsMono NFP';
            }}
            QPushButton#MainBtn {{
                background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 8px; font-weight: bold; font-family: 'JetBrainsMono NFP';
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
        self.git_list_layout = FlowLayout(self.git_container, 5, 5)
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
        self.rclone_list_layout = FlowLayout(self.rclone_container, 5, 5)
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
            item = self.git_list_layout.itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)
        for i in reversed(range(self.rclone_list_layout.count())): 
            item = self.rclone_list_layout.itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)
        
        self.project_widgets = {"git": {}, "rclone": {}}
        
        for idx, p in enumerate(self.projects["git"]):
            pid = f"git_{idx}"
            path = p["path"]
            if not os.path.isabs(path):
                path = os.path.join(SCRIPT_DIR, path)
            w = ProjectWidget(pid, p["name"], "git", path, config=p)
            self.git_list_layout.addWidget(w)
            self.project_widgets["git"][pid] = w
            
        for idx, p in enumerate(self.projects["rclone"]):
            pid = f"rclone_{idx}"
            path = p["path"]
            if not os.path.isabs(path):
                path = os.path.join(SCRIPT_DIR, path)
            w = ProjectWidget(pid, p["name"], "rclone", path, p["dst"], config=p)
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
            cmd_pattern = w.config.get("cmd")
            worker = MonitorWorker(pid, "rclone", w.path, w.extra, cmd_pattern)
            worker.signals.finished.connect(self.on_check_finished)
            worker.start()

    def on_check_finished(self, pid, p_type, color):
        if p_type in self.project_widgets and pid in self.project_widgets[p_type]:
            self.project_widgets[p_type][pid].update_status(color)
        
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GitRcloneMonitor()
    window.show()
    sys.exit(app.exec())
