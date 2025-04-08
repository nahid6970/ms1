import sys
import psutil
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QSizePolicy,
)
from PyQt5.QtCore import Qt, QTimer, QTime, QThread, pyqtSignal
import subprocess
import datetime
import os
import time
import queue

class GitCheckerThread(QThread):
    status_updated = pyqtSignal(str, str, str)

    def __init__(self, git_path, parent=None):
        super().__init__(parent)
        self.git_path = git_path
        self.queue = queue.Queue()

    def check_git_status(self):
        if not os.path.exists(self.git_path):
            self.status_updated.emit(self.git_path, "Invalid path", "#000000")
            return
        try:
            os.chdir(self.git_path)
            git_status = subprocess.run(["git", "status"], capture_output=True, text=True, check=True)
            if "nothing to commit, working tree clean" in git_status.stdout:
                self.status_updated.emit(self.git_path, "✅", "#00ff21")
            else:
                self.status_updated.emit(self.git_path, "❌", "#fe1616")
        except subprocess.CalledProcessError as e:
            self.status_updated.emit(self.git_path, "Error", "#ff0000")
            print(f"Git error in {self.git_path}: {e}")
        except FileNotFoundError:
            self.status_updated.emit(self.git_path, "Git not found", "#ff0000")
            print(f"Git not found in {self.git_path}")
        except Exception as e:
            self.status_updated.emit(self.git_path, f"Exception: {e}", "#ff0000")
            print(f"An error occurred in {self.git_path}: {e}")

    def run(self):
        while True:
            self.check_git_status()
            time.sleep(1)

class CPUMonitor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System Info")
        self.setGeometry(0, 0, 1920, 40)
        self.setFixedSize(1920, 40)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("") # Remove inline style

        # --- Git Status Section ---
        self.bkup_label = QLabel("\udb80\udea2")
        self.bkup_label.setObjectName("bkupLabel")
        self.bkup_label.setFont(self.get_font("JetBrainsMono NFP", 18, "bold"))
        self.bkup_label.setCursor(Qt.PointingHandCursor)
        self.bkup_label.mousePressEvent = self.git_backup  # Use mousePressEvent for simplicity

        self.status_ms1 = QLabel("")
        self.status_ms1.setObjectName("statusMs1")
        self.status_ms1.setFont(self.get_font("JetBrainsMono NFP", 10, "bold"))
        self.status_ms1.setCursor(Qt.PointingHandCursor)
        self.status_ms1.mousePressEvent = self.git_backup_ms1
        self.status_ms1.setContextMenuPolicy(Qt.CustomContextMenu)
        self.status_ms1.customContextMenuRequested.connect(lambda pos: self.show_git_changes("C:\\ms1"))

        self.status_ms2 = QLabel("")
        self.status_ms2.setObjectName("statusMs2")
        self.status_ms2.setFont(self.get_font("JetBrainsMono NFP", 10, "bold"))
        self.status_ms2.setCursor(Qt.PointingHandCursor)
        self.status_ms2.mousePressEvent = self.git_backup_ms2
        self.status_ms2.setContextMenuPolicy(Qt.CustomContextMenu)
        self.status_ms2.customContextMenuRequested.connect(lambda pos: self.show_git_changes("C:\\ms2"))

        self.status_ms3 = QLabel("")
        self.status_ms3.setObjectName("statusMs3")
        self.status_ms3.setFont(self.get_font("JetBrainsMono NFP", 10, "bold"))
        self.status_ms3.setCursor(Qt.PointingHandCursor)
        self.status_ms3.mousePressEvent = self.git_backup_ms3
        self.status_ms3.setContextMenuPolicy(Qt.CustomContextMenu)
        self.status_ms3.customContextMenuRequested.connect(lambda pos: self.show_git_changes("C:\\ms3"))

        self.del_git_ignore = QLabel("\udb82\udde7")
        self.del_git_ignore.setObjectName("delGitIgnore")
        self.del_git_ignore.setFont(self.get_font("JetBrainsMono NFP", 18, "bold"))
        self.del_git_ignore.setCursor(Qt.PointingHandCursor)
        self.del_git_ignore.mousePressEvent = self.delete_git_lock_files

        left_layout = QHBoxLayout()
        left_layout.setContentsMargins(5, 0, 5, 0)
        left_layout.setSpacing(5)
        left_layout.addWidget(self.bkup_label)
        left_layout.addWidget(self.status_ms1)
        left_layout.addWidget(self.status_ms2)
        left_layout.addWidget(self.status_ms3)
        left_layout.addWidget(self.del_git_ignore)

        self.left_widget = QWidget()
        self.left_widget.setLayout(left_layout)
        self.left_widget.setObjectName("leftWidget")

        # --- Center Section ---
        self.clock_label = QLabel()
        self.clock_label.setAlignment(Qt.AlignCenter)
        self.clock_label.setObjectName("clockLabel")
        self.clock_label.setStyleSheet("font-size: 16px;")
        self.update_clock()

        # --- Right Section ---
        self.cpu_label = QLabel("CPU: 0%")
        self.ram_label = QLabel("RAM: 0%")
        self.cpu_label.setAlignment(Qt.AlignCenter)
        self.ram_label.setAlignment(Qt.AlignCenter)
        self.cpu_label.setObjectName("cpuLabel")
        self.ram_label.setObjectName("ramLabel")
        self.cpu_label.setStyleSheet("font-size: 16px; margin: 0 3px;")
        self.ram_label.setStyleSheet("font-size: 16px; margin: 0 3px;")

        right_layout = QHBoxLayout()
        right_layout.setContentsMargins(5, 0, 5, 0)
        right_layout.setSpacing(5)
        right_layout.addWidget(self.cpu_label)
        right_layout.addWidget(self.ram_label)

        self.right_widget = QWidget()
        self.right_widget.setLayout(right_layout)
        self.right_widget.setObjectName("rightWidget")

        # --- Main Layout ---
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.addWidget(self.left_widget)
        self.main_layout.addWidget(self.clock_label, stretch=1)
        self.main_layout.addWidget(self.right_widget)

        self.setLayout(self.main_layout)

        # --- Timers ---
        self.cpu_ram_timer = QTimer()
        self.cpu_ram_timer.timeout.connect(self.update_cpu_ram_usage)
        self.cpu_ram_timer.start(1000)

        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(100)

        # --- Git Status Threads ---
        self.git_threads = []
        git_paths = ["C:\\ms1", "C:\\ms2", "C:\\ms3"]
        status_labels = [self.status_ms1, self.status_ms2, self.status_ms3]
        for i, path in enumerate(git_paths):
            thread = GitCheckerThread(path)
            thread.status_updated.connect(lambda git_path, text, color: self.update_git_status(git_path, text, color))
            thread.start()
            self.git_threads.append(thread)

        # --- Apply Stylesheet ---
        self.apply_stylesheet()

    def get_font(self, family, pointSize, weight="normal"):
        from PyQt5.QtGui import QFont
        font = QFont(family, pointSize)
        if weight == "bold":
            font.setBold(True)
        return font

    def update_git_status(self, git_path, text, color):
        if git_path == "C:\\ms1":
            self.status_ms1.setText(text)
            self.status_ms1.setStyleSheet(f"color: {color};")
        elif git_path == "C:\\ms2":
            self.status_ms2.setText(text)
            self.status_ms2.setStyleSheet(f"color: {color};")
        elif git_path == "C:\\ms3":
            self.status_ms3.setText(text)
            self.status_ms3.setStyleSheet(f"color: {color};")

    def git_backup(self, event):
        subprocess.Popen(["Start", "pwsh",  "-NoExit", "-Command", "& {$host.UI.RawUI.WindowTitle='GiTSync' ; C:\\ms1\\scripts\\Github\\ms1u.ps1 ; C:\\ms1\\scripts\\Github\\ms2u.ps1 ; C:\\ms1\\scripts\\Github\\ms3u.ps1 ; cd ~}"], shell=True)

    def git_backup_ms1(self, event):
        subprocess.Popen(["Start", "pwsh",  "-NoExit", "-Command", "& {$host.UI.RawUI.WindowTitle='GiTSync' ; cd C:/ms1/ ; gitter}"], shell=True)

    def git_restore_ms1(self):
        subprocess.Popen(["Start", "pwsh",  "-NoExit", "-Command", "& {$host.UI.RawUI.WindowTitle='Git Restore' ; cd C:/ms1/ ; git restore . }"], shell=True)

    def git_backup_ms2(self, event):
        subprocess.Popen(["Start", "pwsh",  "-NoExit", "-Command", "& {$host.UI.RawUI.WindowTitle='GiTSync' ; cd C:/ms2/ ; gitter}"], shell=True)

    def git_restore_ms2(self):
        subprocess.Popen(["Start", "pwsh",  "-NoExit", "-Command", "& {$host.UI.RawUI.WindowTitle='Git Restore' ; cd C:/ms2/ ; git restore . }"], shell=True)

    def git_backup_ms3(self, event):
        subprocess.Popen(["Start", "pwsh",  "-NoExit", "-Command", "& {$host.UI.RawUI.WindowTitle='GiTSync' ; cd C:/ms3/ ; gitter}"], shell=True)

    def show_git_changes(self, git_path):
        if not os.path.exists(git_path):
            print("Invalid path")
            return
        try:
            os.chdir(git_path)
            subprocess.Popen(["cmd", "/c", "start", "cmd", "/k", "git status && git diff --stat"], shell=True)
        except FileNotFoundError:
            print("Error: Cannot find the specified path.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def delete_git_lock_files(self, event):
        files_to_delete = [
            r'C:\ms1\.git\index.lock',
            r'C:\ms2\.git\index.lock',
            r'C:\ms3\.git\index.lock'
        ]
        for file in files_to_delete:
            try:
                if os.path.exists(file):
                    os.remove(file)
                    print(f"Deleted: {file}")
                else:
                    print(f"File not found: {file}")
            except Exception as e:
                print(f"Error deleting {file}: {e}")

    def apply_stylesheet(self):
        try:
            with open("C:\\ms1\\pyqt\\customize\\style.css", "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print("Stylesheet file not found: customize/style.css")

    def update_cpu_ram_usage(self):
        cpu_percent = int(psutil.cpu_percent())
        ram_info = psutil.virtual_memory()
        ram_percent = int(ram_info.percent)
        self.cpu_label.setText(f"CPU: {cpu_percent}%")
        self.ram_label.setText(f"RAM: {ram_percent}%")

    def update_clock(self):
        now = datetime.datetime.now()
        current_time = now.strftime("%I:%M:%S %p")
        self.clock_label.setText(current_time)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    cpu_monitor = CPUMonitor()
    cpu_monitor.show()
    sys.exit(app.exec_())