import sys
import os
import re
import json
import subprocess
import threading
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QComboBox, QCheckBox, QRadioButton, QButtonGroup, 
                             QFileDialog, QMessageBox, QFrame, QScrollArea)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette

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
"""

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ytc_settings.json")

class Worker(QObject):
    finished = pyqtSignal()
    status_update = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    success = pyqtSignal(str)

    def __init__(self, url, save_dir, lang_selection, include_auto, output_format, cookie_method, browser, cookie_file):
        super().__init__()
        self.url = url
        self.save_dir = save_dir
        self.lang_selection = lang_selection
        self.include_auto = include_auto
        self.output_format = output_format
        self.cookie_method = cookie_method
        self.browser = browser
        self.cookie_file = cookie_file

    def run(self):
        try:
            import time
            start_time = time.time()

            command = ["yt-dlp", "--skip-download", "--write-subs", "-o", f"{self.save_dir}/%(title)s.%(ext)s"]
            
            # Language
            lang_code = "en.*"
            if self.lang_selection == "Bengali": lang_code = "bn"
            elif self.lang_selection == "All Available": lang_code = "all"
            command.extend(["--sub-langs", lang_code])

            if self.include_auto: command.append("--write-auto-subs")

            # Format
            dl_format = self.output_format if self.output_format != "txt" else "srt"
            command.extend(["--convert-subs", dl_format])

            # Auth
            if self.cookie_method == "browser":
                command.extend(["--cookies-from-browser", self.browser])
            elif self.cookie_method == "file" and self.cookie_file:
                command.extend(["--cookies", self.cookie_file])
            
            command.extend(["--extractor-args", "youtube:player_client=default"])
            command.append(self.url)

            # Subprocess
            process = subprocess.Popen(
                command, 
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
                    self.status_update.emit(line.strip()[-80:])
            
            stderr = process.communicate()[1]

            if process.returncode != 0:
                self.error_occurred.emit(f"Process failed:\n{stderr}")
                self.finished.emit()
                return

            # Post Processing for TXT
            msg = "Download Completed."
            if self.output_format == "txt":
                self.status_update.emit("CONVERTING TO RAW TEXT...")
                count = 0
                try:
                    for filename in os.listdir(self.save_dir):
                        if filename.endswith(".srt") or filename.endswith(".vtt"):
                           full_path = os.path.join(self.save_dir, filename)
                           if os.path.getmtime(full_path) > start_time - 5:
                               if self._convert_to_raw_text(full_path):
                                   count += 1
                    msg = f"Processed {count} file(s) to Raw Text."
                except Exception as e:
                    self.error_occurred.emit(f"Conversion Error: {e}")
                    return

            self.success.emit(msg)

        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            self.finished.emit()

    def _convert_to_raw_text(self, file_path):
        try:
            txt_path = os.path.splitext(file_path)[0] + ".txt"
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            clean_lines = []
            final_lines = []
            
            for line in lines:
                line = line.strip()
                if not line: continue
                if re.fullmatch(r'\d+', line): continue 
                if "-->" in line: continue 
                if line.startswith("WEBVTT") or line.startswith("Kind:") or line.startswith("Language:"): continue
                
                line = re.sub(r'<[^>]+>', '', line)
                line = re.sub(r'\d{2}:\d{2}:\d{2}[\.,]\d{3}', '', line)
                line = line.strip()
                if not line: continue

                if not clean_lines or clean_lines[-1] != line:
                     clean_lines.append(line)
            
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
            return True
        except Exception as e:
            print(e)
            return False


class SubliminalApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YT SUBLIMINAL // CYBER_QT")
        self.setGeometry(100, 100, 650, 750)
        self.settings = self.load_settings()

        # Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Header
        header = QLabel(">> SUBLIMINAL_DOWNLOADER_QT")
        header.setObjectName("Header")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)

        # URL Input
        url_layout = QHBoxLayout()
        url_label = QLabel("TARGET_URL:")
        url_label.setObjectName("SectionTitle")
        self.url_entry = QLineEdit()
        self.url_entry.setPlaceholderText("https://youtu.be/...")
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_entry)
        main_layout.addLayout(url_layout)

        # Settings Group (Frame)
        settings_frame = QFrame()
        settings_layout = QVBoxLayout(settings_frame)
        
        # Language
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("LANGUAGE_DATA:"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "Bengali", "All Available"])
        self.lang_combo.setCurrentText(self.settings.get("language", "English"))
        lang_layout.addWidget(self.lang_combo)
        settings_layout.addLayout(lang_layout)

        # Auto Subs
        self.auto_subs_check = QCheckBox("INCLUDE_AUTO_GENERATED_ARRAYS")
        if self.settings.get("auto_subs", False):
            self.auto_subs_check.setChecked(True)
        settings_layout.addWidget(self.auto_subs_check)

        # Formats
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("OUTPUT_FORMAT:"))
        self.format_group = QButtonGroup(self)
        
        self.radio_srt = QRadioButton("SRT")
        self.radio_vtt = QRadioButton("VTT")
        self.radio_txt = QRadioButton("RAW_TXT")
        
        self.format_group.addButton(self.radio_srt)
        self.format_group.addButton(self.radio_vtt)
        self.format_group.addButton(self.radio_txt)
        
        format_val = self.settings.get("format", "txt")
        if format_val == "srt": self.radio_srt.setChecked(True)
        elif format_val == "vtt": self.radio_vtt.setChecked(True)
        else: self.radio_txt.setChecked(True)

        format_layout.addWidget(self.radio_srt)
        format_layout.addWidget(self.radio_vtt)
        format_layout.addWidget(self.radio_txt)
        format_layout.addStretch()
        settings_layout.addLayout(format_layout)

        main_layout.addWidget(settings_frame)

        # Auth Group
        auth_frame = QFrame()
        auth_layout = QVBoxLayout(auth_frame)
        auth_layout.addWidget(QLabel("AUTH_PROTOCOL:"))

        self.auth_group = QButtonGroup(self)
        auth_opts = QHBoxLayout()
        self.radio_none = QRadioButton("NONE")
        self.radio_browser = QRadioButton("BROWSER")
        self.radio_file = QRadioButton("FILE")
        self.auth_group.addButton(self.radio_none)
        self.auth_group.addButton(self.radio_browser)
        self.auth_group.addButton(self.radio_file)
        
        saved_method = self.settings.get("cookie_method", "none")
        if saved_method == "browser": self.radio_browser.setChecked(True)
        elif saved_method == "file": self.radio_file.setChecked(True)
        else: self.radio_none.setChecked(True)

        auth_opts.addWidget(self.radio_none)
        auth_opts.addWidget(self.radio_browser)
        auth_opts.addWidget(self.radio_file)
        auth_layout.addLayout(auth_opts)

        # Dynamic Auth Fields
        self.browser_combo = QComboBox()
        self.browser_combo.addItems(["chrome", "firefox", "edge", "opera", "brave"])
        self.browser_combo.setCurrentText(self.settings.get("browser", "chrome"))
        
        self.file_layout = QHBoxLayout()
        self.cookie_path = QLineEdit()
        self.cookie_path.setPlaceholderText("Path to cookies.txt")
        self.cookie_path.setText(self.settings.get("cookie_file", ""))
        self.browse_btn = QPushButton("BROWSE")
        self.browse_btn.setFixedWidth(80)
        self.browse_btn.clicked.connect(self.browse_cookies)
        self.file_layout.addWidget(self.cookie_path)
        self.file_layout.addWidget(self.browse_btn)

        auth_layout.addWidget(self.browser_combo)
        auth_layout.addLayout(self.file_layout)
        
        main_layout.addWidget(auth_frame)

        # Logic for hiding dynamic fields
        self.auth_group.buttonClicked.connect(self.refresh_auth_ui)
        self.refresh_auth_ui()

        # Download Button
        self.dl_btn = QPushButton("[ INITIATE_DOWNLOAD ]")
        self.dl_btn.setFixedHeight(50)
        self.dl_btn.setObjectName("DownloadButton")
        self.dl_btn.clicked.connect(self.start_download)
        main_layout.addWidget(self.dl_btn)

        # Status
        self.status_label = QLabel("SYSTEM_READY")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)

    def refresh_auth_ui(self, btn=None):
        if self.radio_browser.isChecked():
            self.browser_combo.setVisible(True)
            self.cookie_path.setVisible(False)
            self.browse_btn.setVisible(False)
        elif self.radio_file.isChecked():
            self.browser_combo.setVisible(False)
            self.cookie_path.setVisible(True)
            self.browse_btn.setVisible(True)
        else:
            self.browser_combo.setVisible(False)
            self.cookie_path.setVisible(False)
            self.browse_btn.setVisible(False)

    def browse_cookies(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Select Cookie File", "", "Text Files (*.txt);;All Files (*)")
        if fname:
            self.cookie_path.setText(fname)

    def start_download(self):
        url = self.url_entry.text()
        if not url:
            QMessageBox.critical(self, "Error", "URL_MISSING")
            return

        initial_dir = self.settings.get("last_save_dir", "")
        if not os.path.exists(initial_dir): initial_dir = os.path.expanduser("~")
        save_dir = QFileDialog.getExistingDirectory(self, "Select Save Directory", initial_dir)
        
        if not save_dir: return
        
        self.settings["last_save_dir"] = save_dir
        self.save_settings()

        # Gather params
        lang = self.lang_combo.currentText()
        auto = self.auto_subs_check.isChecked()
        fmt = "txt"
        if self.radio_srt.isChecked(): fmt = "srt"
        elif self.radio_vtt.isChecked(): fmt = "vtt"
        
        cookie_method = "none"
        if self.radio_browser.isChecked(): cookie_method = "browser"
        elif self.radio_file.isChecked(): cookie_method = "file"

        # Worker
        self.thread = QThread()
        self.worker = Worker(
            url, save_dir, lang, auto, fmt, 
            cookie_method, self.browser_combo.currentText(), self.cookie_path.text()
        )
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.worker.status_update.connect(self.update_status)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.success.connect(self.on_success)
        
        self.dl_btn.setEnabled(False)
        self.dl_btn.setText("DOWNLOADING...")
        self.thread.start()

    def update_status(self, msg):
        self.status_label.setText(msg)

    def on_error(self, msg):
        QMessageBox.critical(self, "Error", msg)
        self.reset_ui()

    def on_success(self, msg):
        QMessageBox.information(self, "Success", msg)
        self.reset_ui()
    
    def reset_ui(self):
        self.dl_btn.setEnabled(True)
        self.dl_btn.setText("[ INITIATE_DOWNLOAD ]")
        self.status_label.setText("SYSTEM_READY")

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    return json.load(f)
            except: pass
        return {}

    def save_settings(self):
        self.settings["language"] = self.lang_combo.currentText()
        self.settings["auto_subs"] = self.auto_subs_check.isChecked()
        if self.radio_srt.isChecked(): self.settings["format"] = "srt"
        elif self.radio_vtt.isChecked(): self.settings["format"] = "vtt"
        else: self.settings["format"] = "txt"
        
        if self.radio_browser.isChecked(): self.settings["cookie_method"] = "browser"
        elif self.radio_file.isChecked(): self.settings["cookie_method"] = "file"
        else: self.settings["cookie_method"] = "none"
        
        self.settings["browser"] = self.browser_combo.currentText()
        self.settings["cookie_file"] = self.cookie_path.text()
        
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(self.settings, f)
        except: pass

    def closeEvent(self, event):
        self.save_settings()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    window = SubliminalApp()
    window.show()
    sys.exit(app.exec())
