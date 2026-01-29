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
    border-radius: 4px;
    padding: 2px 5px;
    min-height: 22px;
}}
QComboBox::drop-down {{
    border: none;
    width: 20px;
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

SETTINGS_FILE = r"C:\@delta\output\yt-dlp\youtube-dlp.json"

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

    def __init__(self, cmd, save_dir, convert_to_txt=False, time_range=None):
        super().__init__()
        self.cmd = cmd
        self.save_dir = save_dir
        self.convert_to_txt = convert_to_txt
        self.time_range = time_range  # (start_seconds, end_seconds) or None

    def run(self):
        try:
            import time
            start_time = time.time()

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
                    line = line.strip()
                    # Strip ANSI
                    line = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', line)
                    self.progress.emit(line[-90:])
            
            stderr = process.communicate()[1]
            if process.returncode == 0:
                if self.convert_to_txt:
                    self.progress.emit("CONVERTING_TO_RAW_TEXT...")
                    self._process_raw_text(start_time)
                self.success.emit()
            else:
                self.error.emit(stderr)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()

    def _process_raw_text(self, start_time):
        try:
            for filename in os.listdir(self.save_dir):
                if filename.endswith(".srt") or filename.endswith(".vtt"):
                    full_path = os.path.join(self.save_dir, filename)
                    # Modify check: if created/modified after start_time
                    if os.path.getmtime(full_path) > start_time - 5:
                        self._convert_file(full_path)
        except Exception as e:
            print(f"Conversion processing error: {e}")

    def _convert_file(self, file_path):
        try:
            txt_path = os.path.splitext(file_path)[0] + ".txt"
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            clean_lines = []
            final_lines = []
            
            # Parse subtitle entries with timestamps
            entries = []
            current_entry = {"start": 0, "end": 0, "text": ""}
            
            for line in lines:
                line = line.strip()
                if not line: continue
                
                # Check for timestamp line
                if "-->" in line:
                    # Parse timestamps (format: HH:MM:SS,mmm --> HH:MM:SS,mmm)
                    try:
                        time_parts = line.split("-->")
                        start_str = time_parts[0].strip()
                        end_str = time_parts[1].strip()
                        
                        current_entry["start"] = self._parse_subtitle_time(start_str)
                        current_entry["end"] = self._parse_subtitle_time(end_str)
                    except:
                        continue
                elif re.fullmatch(r'\d+', line):
                    # Subtitle index number - save previous entry if exists
                    if current_entry["text"]:
                        entries.append(current_entry.copy())
                        current_entry = {"start": 0, "end": 0, "text": ""}
                elif not line.startswith("WEBVTT") and not line.startswith("Kind:") and not line.startswith("Language:"):
                    # This is subtitle text
                    line = re.sub(r'<[^>]+>', '', line)
                    line = line.strip()
                    if line:
                        if current_entry["text"]:
                            current_entry["text"] += " " + line
                        else:
                            current_entry["text"] = line
            
            # Add last entry
            if current_entry["text"]:
                entries.append(current_entry)
            
            # Filter by time range if specified
            if self.time_range:
                start_sec, end_sec = self.time_range
                filtered_entries = []
                for entry in entries:
                    # Include if subtitle overlaps with requested range
                    if entry["end"] >= start_sec and entry["start"] <= end_sec:
                        filtered_entries.append(entry)
                entries = filtered_entries
            
            # Extract text from entries
            for entry in entries:
                text = entry["text"]
                if not clean_lines or clean_lines[-1] != text:
                    clean_lines.append(text)
            
            # Simple Rolling Fix
            for line in clean_lines:
                if final_lines and line.startswith(final_lines[-1]):
                    final_lines[-1] = line
                else:
                    final_lines.append(line)

            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(final_lines))
            
            try: os.remove(file_path)
            except: pass
        except Exception as e:
            print(e)
    
    def _parse_subtitle_time(self, time_str):
        """Convert subtitle timestamp to seconds (HH:MM:SS,mmm or HH:MM:SS.mmm)"""
        try:
            # Replace comma with dot for milliseconds
            time_str = time_str.replace(',', '.')
            # Split by dot to separate seconds and milliseconds
            parts = time_str.split('.')
            time_part = parts[0]
            
            # Split time part
            time_components = time_part.split(':')
            if len(time_components) == 3:
                hours, minutes, seconds = map(int, time_components)
                return hours * 3600 + minutes * 60 + seconds
            elif len(time_components) == 2:
                minutes, seconds = map(int, time_components)
                return minutes * 60 + seconds
            else:
                return int(time_components[0])
        except:
            return 0

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
        self.url_input.setText(self.settings.get("last_url", ""))
        self.url_input.textChanged.connect(self.extract_time_from_url)
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

        # Mode Selection
        mode_box = QHBoxLayout()
        mode_box.addWidget(QLabel("OPERATION_MODE:"))
        self.mode_group = QButtonGroup()
        self.r_video = QRadioButton("VIDEO_DOWNLOAD")
        self.r_subs = QRadioButton("SUBTITLES_ONLY")
        self.mode_group.addButton(self.r_video)
        self.mode_group.addButton(self.r_subs)
        self.r_video.setChecked(True)
        self.mode_group.buttonClicked.connect(self.toggle_mode_ui)
        
        mode_box.addWidget(self.r_video)
        mode_box.addWidget(self.r_subs)
        mode_box.addStretch()
        fmt_layout.addLayout(mode_box)
        
        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background-color: {ACCENT_CYAN}; max-height: 1px;")
        fmt_layout.addWidget(sep)
        
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
        sub_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.sub_check = QCheckBox("DOWNLOAD_SUBTITLES")
        self.sub_check.stateChanged.connect(self.toggle_sub_ui)
        sub_layout.addWidget(self.sub_check)
        
        sub_layout.addWidget(QLabel("LANG:"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "Bengali", "Hindi", "All"])
        self.lang_combo.setCurrentText(self.settings.get("sub_lang", "English"))
        self.lang_combo.setEnabled(self.sub_check.isChecked())
        sub_layout.addWidget(self.lang_combo)

        # Extra Sub Options (Format & Auto)
        self.sub_extras = QWidget()
        extra_layout = QVBoxLayout(self.sub_extras)
        extra_layout.setContentsMargins(10, 0, 0, 0)
        extra_layout.setSpacing(8)
        
        # First row: Format and Auto-gen
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("FMT:"))
        self.sub_fmt = QComboBox()
        self.sub_fmt.addItems(["SRT", "VTT", "TXT (Raw)"])
        self.sub_fmt.setCurrentText(self.settings.get("sub_fmt", "SRT"))
        row1.addWidget(self.sub_fmt)
        
        self.auto_sub = QCheckBox("INCLUDE_AUTO_GEN")
        self.auto_sub.setChecked(self.settings.get("auto_sub", False))
        row1.addWidget(self.auto_sub)
        row1.addStretch()
        extra_layout.addLayout(row1)
        
        # Second row: Timeline selection
        row2 = QHBoxLayout()
        self.timeline_check = QCheckBox("TIMELINE_RANGE")
        self.timeline_check.setChecked(self.settings.get("use_timeline", False))
        self.timeline_check.stateChanged.connect(self.toggle_timeline_ui)
        row2.addWidget(self.timeline_check)
        
        row2.addWidget(QLabel("START:"))
        self.start_time = QLineEdit()
        self.start_time.setPlaceholderText("0:00 or 3062")
        self.start_time.setFixedWidth(100)
        self.start_time.setText(self.settings.get("start_time", ""))
        row2.addWidget(self.start_time)
        
        row2.addWidget(QLabel("END:"))
        self.end_time = QLineEdit()
        self.end_time.setPlaceholderText("5:30 or 3428")
        self.end_time.setFixedWidth(100)
        self.end_time.setText(self.settings.get("end_time", ""))
        row2.addWidget(self.end_time)
        row2.addStretch()
        extra_layout.addLayout(row2)
        
        self.sub_extras.setVisible(False) # Hidden by default (Video mode)
        sub_layout.addWidget(self.sub_extras)
        
        # Initialize timeline UI state
        self.toggle_timeline_ui()

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
        self.progress.setFixedHeight(5)
        main.addWidget(self.progress)
        
        # Initialize State Safely
        mode = self.settings.get("mode", "video")
        if mode == "subs": self.r_subs.setChecked(True)
        else: self.r_video.setChecked(True)
        self.toggle_mode_ui()

    def toggle_sub_ui(self):
        self.lang_combo.setEnabled(self.sub_check.isChecked())
    
    def toggle_timeline_ui(self):
        enabled = self.timeline_check.isChecked()
        self.start_time.setEnabled(enabled)
        self.end_time.setEnabled(enabled)
    
    def extract_time_from_url(self):
        """Extract timestamp from YouTube URL (e.g., ?t=3040 or &t=3040)"""
        url = self.url_input.text()
        if not url:
            return
        
        # Look for t= parameter in URL
        match = re.search(r'[?&]t=(\d+)', url)
        if match:
            seconds = int(match.group(1))
            # Only auto-fill if start_time is empty or if we're in subs mode
            if not self.start_time.text() or self.r_subs.isChecked():
                self.start_time.setText(str(seconds))
                # Auto-enable timeline checkbox in subs mode
                if self.r_subs.isChecked():
                    self.timeline_check.setChecked(True)
                    self.toggle_timeline_ui()

    def toggle_mode_ui(self):
        is_video = self.r_video.isChecked()
        
        # Video/Audio combos
        self.video_combo.setEnabled(is_video)
        self.audio_combo.setEnabled(is_video)
        
        # Sub options
        if is_video:
            self.sub_check.setText("DOWNLOAD_SUBTITLES")
            self.sub_check.setEnabled(True)
            self.sub_check.setChecked(self.settings.get("subtitles", False))
            self.sub_extras.setVisible(False)
            self.toggle_sub_ui()
        else:
            self.sub_check.setText("DOWNLOAD_SUBTITLES (FORCED)")
            self.sub_check.setChecked(True)
            self.sub_check.setEnabled(False) # Always checked in sub mode
            self.lang_combo.setEnabled(True)
            self.sub_extras.setVisible(True)

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
        
        # Extract timestamp from URL if present (e.g., ?t=3040 or &t=3040)
        self.extract_timestamp_from_url(url)

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
        convert_txt = False
        time_range = None

        if self.r_subs.isChecked():
            # Subtitle Only Mode
            cmd.append("--skip-download")
            cmd.append("--write-subs")
            
            if self.auto_sub.isChecked():
                cmd.append("--write-auto-subs")
            
            fmt_sel = self.sub_fmt.currentText()
            if "TXT" in fmt_sel:
                cmd.extend(["--convert-subs", "srt"]) # Download srt first
                convert_txt = True
            elif "SRT" in fmt_sel:
                 cmd.extend(["--convert-subs", "srt"])
            elif "VTT" in fmt_sel:
                 cmd.extend(["--convert-subs", "vtt"])

            lang = self.lang_combo.currentText()
            if lang == "Bengali": cmd.extend(["--sub-langs", "bn"])
            elif lang == "Hindi": cmd.extend(["--sub-langs", "hi"])
            elif lang == "All": cmd.extend(["--sub-langs", "all"])
            else: cmd.extend(["--sub-langs", "en.*"])
            
            # Timeline range
            if self.timeline_check.isChecked():
                start = self.parse_time(self.start_time.text())
                end = self.parse_time(self.end_time.text())
                
                # Note: --download-sections doesn't work for subtitles
                # We'll filter in post-processing instead
                time_range = (start if start is not None else 0, 
                             end if end is not None else float('inf'))

        else:
            # Video Mode
            # Formats
            v_id = self.video_combo.currentData()
            a_id = self.audio_combo.currentData()
            
            f_str = ""
            if v_id == "best" and a_id == "best": f_str = "bestvideo+bestaudio/best"
            elif v_id == "best": f_str = f"bestvideo+{a_id}"
            elif a_id == "best": f_str = f"{v_id}+bestaudio"
            else: f_str = f"{v_id}+{a_id}"
            
            cmd.extend(["-f", f_str])
            
            # Subtitles
            if self.sub_check.isChecked():
                cmd.append("--write-subs")
                lang = self.lang_combo.currentText()
                if lang == "Bengali": cmd.extend(["--sub-langs", "bn"])
                elif lang == "Hindi": cmd.extend(["--sub-langs", "hi"])
                elif lang == "All": cmd.extend(["--sub-langs", "all"])
                else: cmd.extend(["--sub-langs", "en.*"]) # English default
        
        # Output
        cmd.extend(["-o", f"{save_dir}/%(title)s.%(ext)s"])
        
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
        self.worker = DownloadWorker(cmd, save_dir, convert_txt, time_range)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        
        self.worker.progress.connect(self.update_dl_status)
        self.worker.success.connect(self.on_dl_success)
        self.worker.error.connect(self.on_dl_error)
        
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()
    
    def parse_time(self, time_str):
        """Convert time string to seconds. Accepts formats: '3062', '51:02', '1:30:45'"""
        if not time_str or not time_str.strip():
            return None
        
        time_str = time_str.strip()
        
        # If it's just a number (seconds)
        if time_str.isdigit():
            return int(time_str)
        
        # If it contains colons (MM:SS or HH:MM:SS)
        if ':' in time_str:
            parts = time_str.split(':')
            try:
                if len(parts) == 2:  # MM:SS
                    return int(parts[0]) * 60 + int(parts[1])
                elif len(parts) == 3:  # HH:MM:SS
                    return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            except ValueError:
                return None
        
        return None
    
    def extract_timestamp_from_url(self, url):
        """Extract timestamp from YouTube URL (e.g., ?t=3040 or &t=3040) and populate start time field"""
        import re
        
        # Match ?t=XXXX or &t=XXXX
        match = re.search(r'[?&]t=(\d+)', url)
        if match:
            timestamp = match.group(1)
            # Only set if timeline checkbox is checked or if start field is empty
            if self.r_subs.isChecked():
                self.timeline_check.setChecked(True)
                self.start_time.setText(timestamp)
                self.toggle_timeline_ui()

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
        self.settings["mode"] = "subs" if self.r_subs.isChecked() else "video"
        self.settings["subtitles"] = self.sub_check.isChecked()
        self.settings["sub_lang"] = self.lang_combo.currentText()
        self.settings["sub_fmt"] = self.sub_fmt.currentText()
        self.settings["auto_sub"] = self.auto_sub.isChecked()
        self.settings["use_timeline"] = self.timeline_check.isChecked()
        self.settings["start_time"] = self.start_time.text()
        self.settings["end_time"] = self.end_time.text()
        self.settings["last_url"] = self.url_input.text()
        
        method = "none"
        if self.r_browser.isChecked(): method = "browser"
        elif self.r_file.isChecked(): method = "file"
        self.settings["auth_method"] = method
        self.settings["browser"] = self.browser_combo.currentText()
        self.settings["cookie_file"] = self.file_path.text()
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
            with open(SETTINGS_FILE, 'w') as f: json.dump(self.settings, f, indent=2)
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
