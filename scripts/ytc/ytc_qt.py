import sys
import os
import re
import json
import subprocess
import threading
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QComboBox, QCheckBox, QRadioButton, QButtonGroup, 
                             QFileDialog, QMessageBox, QFrame, QScrollArea, QProgressBar, QSizePolicy)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt6.QtGui import QIcon

# --- Cyberpunk Palette ---
BG_COLOR = "#050a0e"
FG_COLOR = "#10161d" 
ACCENT_GREEN = "#00ff9f"
ACCENT_CYAN = "#00f0ff"
ACCENT_MAGENTA = "#ff003c"
TEXT_COLOR = "#e0e0e0"

STYLESHEET = f"""
QMainWindow {{
    background-color: {BG_COLOR};
}}
QWidget {{
    background-color: {BG_COLOR};
    color: {TEXT_COLOR};
    font-family: "Consolas", "Courier New", monospace;
    font-size: 10pt;
}}
QFrame {{
    background-color: {FG_COLOR};
    border: 1px solid #333;
    border-radius: 5px;
}}
QLabel {{
    background-color: transparent;
    color: {ACCENT_CYAN};
}}
QLabel#Header {{
    font-size: 18pt;
    font-weight: bold;
    color: {ACCENT_GREEN};
}}
QLabel#SectionTitle {{
    color: {ACCENT_MAGENTA};
    font-weight: bold;
}}
QLineEdit {{
    background-color: {BG_COLOR};
    border: 1px solid {ACCENT_CYAN};
    padding: 5px;
    color: {ACCENT_CYAN};
    selection-background-color: {ACCENT_MAGENTA};
}}
QPushButton {{
    background-color: {FG_COLOR};
    border: 1px solid {ACCENT_GREEN};
    color: {ACCENT_GREEN};
    padding: 8px;
    font-weight: bold;
}}
QPushButton:hover {{
    background-color: {ACCENT_GREEN};
    color: {BG_COLOR};
}}
QPushButton:disabled {{
    border-color: #555;
    color: #555;
}}
QComboBox {{
    background-color: {BG_COLOR};
    border: 1px solid {ACCENT_MAGENTA};
    padding: 5px;
}}
QComboBox::drop-down {{
    border: none;
}}
QComboBox QAbstractItemView {{
    background-color: {FG_COLOR};
    selection-background-color: {ACCENT_MAGENTA};
}}
QCheckBox {{
    color: {TEXT_COLOR};
}}
QCheckBox::indicator {{
    border: 1px solid {ACCENT_CYAN};
    background: {BG_COLOR};
}}
QCheckBox::indicator:checked {{
    background: {ACCENT_CYAN};
}}
QRadioButton {{
    color: {TEXT_COLOR};
}}
QRadioButton::indicator {{
    border: 1px solid {ACCENT_GREEN};
    border-radius: 6px;
    background: {BG_COLOR};
    width: 10px;
    height: 10px;
}}
QRadioButton::indicator:checked {{
    background: {ACCENT_GREEN};
}}
QProgressBar {{
    border: 1px solid {ACCENT_CYAN};
    border-radius: 0px;
    text-align: center;
    color: {BG_COLOR};
    background-color: {FG_COLOR};
}}
QProgressBar::chunk {{
    background-color: {ACCENT_CYAN};
}}
QComboBox QAbstractItemView {{
    background-color: {FG_COLOR};
    selection-background-color: {ACCENT_MAGENTA};
    outline: none;
    padding: 5px;
}}
"""

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ytc_qt_settings.json")

class FetchWorker(QObject):
    finished = pyqtSignal(str, list, list) # title, video_formats, audio_formats
    error = pyqtSignal(str)
    
    def __init__(self, url, cookie_method, browser, cookie_file):
        super().__init__()
        self.url = url
        self.cookie_method = cookie_method
        self.browser = browser
        self.cookie_file = cookie_file

    def run(self):
        try:
            command = ["yt-dlp", "--dump-json"]
            
            # Auth
            if self.cookie_method == "browser":
                command.extend(["--cookies-from-browser", self.browser])
            elif self.cookie_method == "file" and self.cookie_file:
                command.extend(["--cookies", self.cookie_file])
            
            command.extend(["--extractor-args", "youtube:player_client=default"])
            command.append(self.url)

            process = subprocess.Popen(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                self.error.emit(stderr)
                return

            info = json.loads(stdout)
            formats = info.get("formats", [])
            
            v_fmts = [f for f in formats if f.get('vcodec') != 'none']
            a_fmts = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
            
            # Sort best to worst roughly
            v_fmts.reverse()
            a_fmts.reverse()
            
            title = info.get('title', 'Unknown Title')
            self.finished.emit(title, v_fmts, a_fmts)
        except Exception as e:
            self.error.emit(str(e))

class DownloadWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(str)
    error = pyqtSignal(str)
    success = pyqtSignal()

    def __init__(self, cmd):
        super().__init__()
        self.cmd = cmd

    def run(self):
        try:
            process = subprocess.Popen(
                self.cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    # Parse progress if possible, for now just raw line
                    line = line.strip()
                    # Strip ANSI
                    line = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', line)
                    self.progress.emit(line[-90:]) # Show parsing
            
            stderr = process.communicate()[1]
            if process.returncode == 0:
                self.success.emit()
            else:
                self.error.emit(stderr)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()

class YTCDownloaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YT VIDEO_LINKER // CYBER_QT")
        self.setGeometry(100, 100, 800, 700)
        self.settings = self.load_settings()

        # Layout
        central = QWidget()
        self.setCentralWidget(central)
        main = QVBoxLayout(central)
        main.setContentsMargins(25, 25, 25, 25)
        main.setSpacing(15)

        # Header
        self.head = QLabel("YT-DLP")
        self.head.setObjectName("Header")
        self.head.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main.addWidget(self.head)

        # URL
        url_box = QHBoxLayout()
        url_lbl = QLabel("TARGET_URL:")
        url_lbl.setObjectName("SectionTitle")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://...")
        self.fetch_btn = QPushButton("SCAN_METADATA")
        self.fetch_btn.clicked.connect(self.fetch_formats)
        
        url_box.addWidget(url_lbl)
        url_box.addWidget(self.url_input)
        url_box.addWidget(self.fetch_btn)
        main.addLayout(url_box)

        # Content Area (Scrollable if needed, but we fit in simple frames)
        
        # Formats Frame
        fmt_frame = QFrame()
        fmt_layout = QVBoxLayout(fmt_frame)
        
        # Video Fmt
        v_layout = QHBoxLayout()
        v_layout.addWidget(QLabel("VIDEO_STREAM:"))
        self.video_combo = QComboBox()
        self.video_combo.addItem("Best Video (Auto)", "best")
        v_layout.addWidget(self.video_combo, 1) # stretch
        fmt_layout.addLayout(v_layout)

        # Audio Fmt
        a_layout = QHBoxLayout()
        a_layout.addWidget(QLabel("AUDIO_STREAM:"))
        self.audio_combo = QComboBox()
        self.audio_combo.addItem("Best Audio (Auto)", "best")
        a_layout.addWidget(self.audio_combo, 1)
        fmt_layout.addLayout(a_layout)
        
        main.addWidget(fmt_frame)

        # Options Frame
        opt_frame = QFrame()
        opt_layout = QVBoxLayout(opt_frame)
        
        # Subtitles Config
        sub_layout = QHBoxLayout()
        self.sub_check = QCheckBox("DOWNLOAD_SUBTITLES")
        self.sub_check.stateChanged.connect(self.toggle_sub_ui)
        if self.settings.get("subtitles", False): self.sub_check.setChecked(True)
        
        sub_layout.addWidget(self.sub_check)
        
        sub_layout.addWidget(QLabel("LANG:"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "Bengali", "All"])
        self.lang_combo.setCurrentText(self.settings.get("sub_lang", "English"))
        self.lang_combo.setEnabled(self.sub_check.isChecked())
        sub_layout.addWidget(self.lang_combo)

        opt_layout.addLayout(sub_layout)
        main.addWidget(opt_frame)

        # Auth Frame
        auth_frame = QFrame()
        auth_layout = QVBoxLayout(auth_frame)
        
        auth_top = QHBoxLayout()
        auth_top.addWidget(QLabel("SECURITY_BYPASS:"))
        self.auth_group = QButtonGroup()
        
        self.r_none = QRadioButton("NONE")
        self.r_browser = QRadioButton("BROWSER_INJECT")
        self.r_file = QRadioButton("KEY_FILE")
        self.auth_group.addButton(self.r_none)
        self.auth_group.addButton(self.r_browser)
        self.auth_group.addButton(self.r_file)
        
        method = self.settings.get("auth_method", "none")
        if method == "browser": self.r_browser.setChecked(True)
        elif method == "file": self.r_file.setChecked(True)
        else: self.r_none.setChecked(True)
        
        auth_top.addWidget(self.r_none)
        auth_top.addWidget(self.r_browser)
        auth_top.addWidget(self.r_file)
        auth_top.addStretch()
        auth_layout.addLayout(auth_top)
        
        # Auth Details
        self.browser_combo = QComboBox()
        self.browser_combo.addItems(["chrome", "firefox", "edge", "opera", "brave"])
        self.browser_combo.setCurrentText(self.settings.get("browser", "chrome"))
        
        self.file_box = QHBoxLayout()
        self.file_path = QLineEdit()
        self.file_path.setText(self.settings.get("cookie_file", ""))
        self.browse_btn = QPushButton("BROWSE")
        self.browse_btn.setFixedWidth(80)
        self.browse_btn.clicked.connect(self.browse_cookie_file)
        self.file_box.addWidget(self.file_path)
        self.file_box.addWidget(self.browse_btn)

        auth_layout.addWidget(self.browser_combo)
        auth_layout.addLayout(self.file_box)
        
        main.addWidget(auth_frame)
        
        self.auth_group.buttonClicked.connect(self.refresh_auth)
        self.refresh_auth()

        # Action Area
        self.dl_btn = QPushButton("[ INITIALIZE_DOWNLOAD_SEQUENCE ]")
        self.dl_btn.setFixedHeight(50)
        self.dl_btn.clicked.connect(self.start_download)
        self.dl_btn.setObjectName("DownloadButton") 
        self.dl_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        main.addWidget(self.dl_btn)
        
        self.status = QLabel("SYSTEM_READY")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main.addWidget(self.status)

        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(5)
        main.addWidget(self.progress)

    def toggle_sub_ui(self):
        self.lang_combo.setEnabled(self.sub_check.isChecked())

    def refresh_auth(self):
        if self.r_browser.isChecked():
            self.browser_combo.setVisible(True)
            self.file_path.setVisible(False)
            self.browse_btn.setVisible(False)
        elif self.r_file.isChecked():
            self.browser_combo.setVisible(False)
            self.file_path.setVisible(True)
            self.browse_btn.setVisible(True)
        else:
            self.browser_combo.setVisible(False)
            self.file_path.setVisible(False)
            self.browse_btn.setVisible(False)

    def browse_cookie_file(self):
        f, _ = QFileDialog.getOpenFileName(self, "Select Cookies", "", "Text (*.txt)")
        if f: self.file_path.setText(f)

    def fetch_formats(self):
        url = self.url_input.text()
        if not url: return

        self.fetch_btn.setEnabled(False)
        self.status.setText("SCANNING_METADATA...")
        self.progress.setRange(0, 0) # Indeterminate

        # Props
        method = "none"
        if self.r_browser.isChecked(): method = "browser"
        elif self.r_file.isChecked(): method = "file"

        self.thread = QThread()
        self.worker = FetchWorker(url, method, self.browser_combo.currentText(), self.file_path.text())
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_fetch_success)
        self.worker.error.connect(self.on_fetch_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def format_size(self, bytes_val):
        if not bytes_val: return "N/A"
        try:
            val = float(bytes_val)
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if val < 1024:
                    return f"{val:.1f}{unit}"
                val /= 1024
            return f"{val:.1f}PB"
        except: return "N/A"

    def on_fetch_success(self, title, v_fmts, a_fmts):
        self.fetch_btn.setEnabled(True)
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.status.setText("METADATA_ACQUIRED")
        
        display_title = title
        if len(display_title) > 50:
            display_title = display_title[:47] + "..."
        self.head.setText(display_title)
        self.head.setToolTip(title)
        
        self.video_combo.clear()
        self.video_combo.addItem("Best Video (Auto)", "best")
        
        # Helper for safe access
        def get_val(d, k, default): return d.get(k) if d.get(k) is not None else default

        for f in v_fmts:
            res = get_val(f, 'resolution', 'N/A')
            ext = get_val(f, 'ext', '???').upper()
            fid = get_val(f, 'format_id', '?')
            fps = get_val(f, 'fps', 0)
            note = get_val(f, 'format_note', '')
            
            # Size
            fs = get_val(f, 'filesize', get_val(f, 'filesize_approx', 0))
            sz_str = self.format_size(fs)
            
            # Format: [EXT ] RES        @ FPS   | SIZE    | NOTE
            # Example: [MP4 ] 1920x1080  @ 60fps |  200MB  | 
            
            display = (f"[{ext:<4}] {str(res):<11} @ {str(fps):<5} | {sz_str:>8} | {note} (ID:{fid})")
            self.video_combo.addItem(display, fid)
        
        # Adjust view width for content
        self.video_combo.view().setMinimumWidth(len(display) * 9 if v_fmts else 400)

        self.audio_combo.clear()
        self.audio_combo.addItem("Best Audio (Auto)", "best")
        for f in a_fmts:
            ext = get_val(f, 'ext', '???').upper()
            abr = get_val(f, 'abr', 0)
            fid = get_val(f, 'format_id', '?')
            
            fs = get_val(f, 'filesize', get_val(f, 'filesize_approx', 0))
            sz_str = self.format_size(fs)
            
            # Align with video: 
            # Video: [EXT ] RES(11) @ FPS(5) (Total ~19 chars) | SIZE
            # Audio: [EXT ] BITRATE(19 chars)                  | SIZE
            
            abr_str = f"{int(abr)}kbps" if abr else "N/A"
            display = f"[{ext:<4}] {abr_str:<19} | {sz_str:>8} | (ID:{fid})"
            self.audio_combo.addItem(display, fid)

    def on_fetch_error(self, err):
        self.fetch_btn.setEnabled(True)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.status.setText("SCAN_FAILED")
        QMessageBox.warning(self, "Error", f"Fetch Error:\n{err}")

    def start_download(self):
        url = self.url_input.text()
        if not url: return
        
        init_dir = self.settings.get("last_dir", "")
        save_dir = QFileDialog.getExistingDirectory(self, "Save Directory", init_dir)
        if not save_dir: return

        self.settings["last_dir"] = save_dir
        self.save_settings()

        # Build Command
        cmd = ["yt-dlp"]
        
        # Formats
        v_id = self.video_combo.currentData()
        a_id = self.audio_combo.currentData()
        
        f_str = ""
        if v_id == "best" and a_id == "best": f_str = "bestvideo+bestaudio/best"
        elif v_id == "best": f_str = f"bestvideo+{a_id}"
        elif a_id == "best": f_str = f"{v_id}+bestaudio"
        else: f_str = f"{v_id}+{a_id}"
        
        cmd.extend(["-f", f_str])
        
        # Output
        cmd.extend(["-o", f"{save_dir}/%(title)s.%(ext)s"])
        
        # Subtitles
        if self.sub_check.isChecked():
            cmd.append("--write-subs")
            lang = self.lang_combo.currentText()
            if lang == "Bengali": cmd.extend(["--sub-langs", "bn"])
            elif lang == "All": cmd.extend(["--sub-langs", "all"])
            else: cmd.extend(["--sub-langs", "en.*"]) # English default
        
        # Auth
        if self.r_browser.isChecked():
            cmd.extend(["--cookies-from-browser", self.browser_combo.currentText()])
        elif self.r_file.isChecked() and self.file_path.text():
            cmd.extend(["--cookies", self.file_path.text()])
        
        cmd.extend(["--extractor-args", "youtube:player_client=default"])
        cmd.append(url)

        self.dl_btn.setEnabled(False)
        self.status.setText("DOWNLOADING...")
        self.progress.setRange(0, 0)

        self.thread = QThread()
        self.worker = DownloadWorker(cmd)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        
        self.worker.progress.connect(self.update_dl_status)
        self.worker.success.connect(self.on_dl_success)
        self.worker.error.connect(self.on_dl_error)
        
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def update_dl_status(self, msg):
        self.status.setText(msg)

    def on_dl_success(self):
        self.dl_btn.setEnabled(True)
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.status.setText("DOWNLOAD_COMPLETE")
        QMessageBox.information(self, "Success", "File(s) Acquired Successfully.")

    def on_dl_error(self, err):
        self.dl_btn.setEnabled(True)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.status.setText("DOWNLOAD_FAILED")
        QMessageBox.critical(self, "Failure", f"Error:\n{err}")

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
             try:
                 with open(SETTINGS_FILE, 'r') as f: return json.load(f)
             except: pass
        return {}

    def save_settings(self):
        self.settings["subtitles"] = self.sub_check.isChecked()
        self.settings["sub_lang"] = self.lang_combo.currentText()
        
        method = "none"
        if self.r_browser.isChecked(): method = "browser"
        elif self.r_file.isChecked(): method = "file"
        self.settings["auth_method"] = method
        self.settings["browser"] = self.browser_combo.currentText()
        self.settings["cookie_file"] = self.file_path.text()
        
        try:
            with open(SETTINGS_FILE, 'w') as f: json.dump(self.settings, f)
        except: pass

    def closeEvent(self, e):
        self.save_settings()
        e.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    window = YTCDownloaderApp()
    window.show()
    sys.exit(app.exec())
