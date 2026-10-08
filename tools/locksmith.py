"""PyQt6 cyberpunk file-lock inspection and process manager."""
from __future__ import annotations

# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "PyQt6",
#     "psutil",
# ]
# ///

import importlib.util
import os
import shutil
import subprocess
import sys
import threading
import queue
import ctypes


DEPENDENCIES = (
    ("PyQt6", "PyQt6"),
    ("psutil", "psutil"),
)


def ensure_dependencies() -> None:
    """Install missing packages into the interpreter running this script."""
    missing = sorted({
        package
        for module, package in DEPENDENCIES
        if importlib.util.find_spec(module) is None
    })
    if not missing:
        return

    uv = shutil.which("uv")
    if uv:
        command = [uv, "pip", "install", "--python", sys.executable, *missing]
    else:
        command = [sys.executable, "-m", "pip", "install", *missing]

    try:
        subprocess.check_call(command)
    except (OSError, subprocess.CalledProcessError) as exc:
        packages = ", ".join(missing)
        raise RuntimeError(
            f"Dependency installation failed for {packages} "
            f"using interpreter {sys.executable}."
        ) from exc


ensure_dependencies()

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
import psutil


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

APP_STYLE = f"""
QMainWindow, QWidget {{
    background-color: {CP_BG}; color: {CP_TEXT}; font-family: Consolas;
}}
QFrame#panel, QFrame#process_item {{
    background-color: {CP_PANEL}; border: 1px solid {CP_DIM};
}}
QLineEdit {{
    background-color: {CP_BG}; color: {CP_CYAN}; border: 1px solid {CP_DIM};
    padding: 8px; font-size: 12px;
}}
QLineEdit:focus {{ border: 1px solid {CP_CYAN}; }}
QPushButton {{
    background-color: {CP_DIM}; color: white; border: none;
    padding: 8px 14px; font-weight: bold;
}}
QPushButton:hover {{ background-color: {CP_CYAN}; color: {CP_BG}; }}
QPushButton#admin {{ background-color: {CP_ORANGE}; color: black; }}
QPushButton#admin:hover {{ background-color: {CP_YELLOW}; }}
QPushButton#kill {{ background-color: {CP_DIM}; color: white; }}
QPushButton#kill:hover {{ background-color: {CP_RED}; color: white; }}
QScrollArea {{ border: none; background: transparent; }}
"""


class ProcessItem(QFrame):
    def __init__(self, proc, file_path, kill_callback, parent=None):
        super().__init__(parent)
        self.proc = proc
        self.kill_callback = kill_callback
        self.setObjectName("process_item")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        try:
            name, pid, username = proc.name(), proc.pid, proc.username()
        except Exception:
            name, pid, username = "Unknown", "???", "???"

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        info = QVBoxLayout()
        title = QLabel(f"{name} (PID: {pid})")
        title.setStyleSheet(f"color: {CP_CYAN}; font-size: 16px; font-weight: bold;")
        user = QLabel(f"User: {username}")
        user.setStyleSheet(f"color: {CP_SUBTEXT}; font-size: 12px;")
        locked = QLabel(f"Locking: {file_path}")
        locked.setWordWrap(True)
        locked.setStyleSheet(f"color: {CP_RED}; font-size: 12px;")
        info.addWidget(title)
        info.addWidget(user)
        info.addWidget(locked)
        layout.addLayout(info, 1)

        kill = QPushButton("KILL")
        kill.setObjectName("kill")
        kill.setFixedWidth(80)
        kill.clicked.connect(self.terminate_process)
        layout.addWidget(kill, 0, Qt.AlignmentFlag.AlignVCenter)

    def terminate_process(self):
        self.kill_callback(self.proc, self)


class LocksmithApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyLocksmith - File Lock Manager")
        self.resize(700, 600)
        self.setAcceptDrops(True)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(20, 20, 20, 10)
        root.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel("FILE LOCKSMITH")
        title.setStyleSheet(f"color: {CP_YELLOW}; font-size: 28px; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()
        restart = QPushButton("RESTART")
        restart.clicked.connect(self.restart_app)
        header.addWidget(restart)
        if not self.is_admin():
            admin = QPushButton("ADMIN RESTART")
            admin.setObjectName("admin")
            admin.clicked.connect(self.restart_admin)
            header.addWidget(admin)
        root.addLayout(header)

        search_panel = QFrame()
        search_panel.setObjectName("panel")
        search_layout = QHBoxLayout(search_panel)
        search_layout.setContentsMargins(15, 10, 15, 10)
        self.path_entry = QLineEdit()
        self.path_entry.setPlaceholderText("Drag folder here or use Browse...")
        search_layout.addWidget(self.path_entry, 1)
        browse = QPushButton("BROWSE")
        browse.clicked.connect(self.browse_path)
        search_layout.addWidget(browse)
        scan = QPushButton("SCAN LOCKS")
        scan.clicked.connect(self.start_scan)
        search_layout.addWidget(scan)
        root.addWidget(search_panel)

        self.status_label = QLabel("SYSTEM READY")
        self.status_label.setStyleSheet(f"color: {CP_SUBTEXT}; font-size: 12px;")
        root.addWidget(self.status_label)

        self.results_scroll = QScrollArea()
        self.results_scroll.setWidgetResizable(True)
        results = QWidget()
        self.results_layout = QVBoxLayout(results)
        self.results_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.results_scroll.setWidget(results)
        root.addWidget(self.results_scroll, 1)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            self.path_entry.setText(urls[0].toLocalFile())
            self.start_scan()
        event.acceptProposedAction()

    def is_admin(self):
        try:
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False

    def restart_admin(self):
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        QApplication.quit()

    def restart_app(self):
        os.execl(sys.executable, sys.executable, *sys.argv)

    def browse_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select folder")
        if not path:
            path, _ = QFileDialog.getOpenFileName(self, "Select file")
        if path:
            self.path_entry.setText(path)

    def set_status(self, text, color):
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"color: {color}; font-size: 12px;")

    def clear_results(self):
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def start_scan(self):
        target_path = self.path_entry.text().strip()
        if not target_path or not os.path.exists(target_path):
            self.set_status("INVALID PATH", CP_RED)
            return
        self.set_status("SCANNING PROCESSES...", CP_CYAN)
        self.clear_results()
        self.scan_queue = queue.Queue()
        threading.Thread(
            target=self.run_scan_thread,
            args=(target_path, self.scan_queue),
            daemon=True,
        ).start()
        QTimer.singleShot(100, self.check_scan_status)

    def check_scan_status(self):
        try:
            while True:
                msg_type, data = self.scan_queue.get_nowait()
                if msg_type == "progress":
                    self.set_status(data.upper(), CP_CYAN)
                elif msg_type == "done":
                    self.display_results(data)
                    return
        except queue.Empty:
            pass
        QTimer.singleShot(100, self.check_scan_status)

    def run_scan_thread(self, target_path, result_queue):
        target_path = os.path.abspath(target_path).lower()
        found_locks = []
        all_pids = list(psutil.pids())
        total = len(all_pids)
        for i, pid in enumerate(all_pids):
            if pid in {0, 4}:
                continue
            if i % 20 == 0:
                result_queue.put(("progress", f"Scanning process {i}/{total}..."))
            try:
                proc = psutil.Process(pid)
                matched_file = None
                try:
                    cwd = proc.cwd()
                    if cwd and self.is_subpath(cwd, target_path):
                        matched_file = cwd + " (Working Directory)"
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    pass
                if not matched_file:
                    try:
                        for opened in proc.open_files():
                            if self.is_subpath(opened.path, target_path):
                                matched_file = opened.path
                                break
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        pass
                if matched_file:
                    found_locks.append((proc, matched_file))
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                continue
            except Exception:
                continue
        result_queue.put(("done", found_locks))

    @staticmethod
    def is_subpath(path, target):
        path = os.path.abspath(path).lower()
        return path == target or path.startswith(target + os.sep)

    def display_results(self, locks):
        if not locks:
            self.set_status("NO LOCKS DETECTED", CP_RED)
            label = QLabel("No processes found locking this file/folder.")
            label.setStyleSheet(f"color: {CP_TEXT}; font-size: 16px;")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_layout.addWidget(label)
            return
        self.set_status(f"DETECTED {len(locks)} BLOCKING PROCESSES", CP_GREEN)
        for proc, file_path in locks:
            self.results_layout.addWidget(ProcessItem(proc, file_path, self.confirm_kill))

    def confirm_kill(self, proc, item_widget):
        try:
            name = proc.name()
            proc.kill()
            item_widget.deleteLater()
            self.set_status(f"TERMINATED {name.upper()}", CP_GREEN)
        except psutil.NoSuchProcess:
            item_widget.deleteLater()
        except psutil.AccessDenied:
            QMessageBox.critical(self, "Error", "Access Denied. Try running as Admin.")
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)
    window = LocksmithApp()
    window.show()
    sys.exit(app.exec())
