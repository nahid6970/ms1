import sys
import json
import webbrowser
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout,
                             QLabel, QPushButton, QComboBox, QCheckBox, QMessageBox,
                             QDialog, QSpinBox, QFormLayout, QDialogButtonBox, QLineEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
import pyperclip
from pynput import keyboard as pynput_keyboard

CP_BG = "#050505"
CP_PANEL = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN = "#00F0FF"
CP_RED = "#FF003C"
CP_GREEN = "#00ff21"
CP_DIM = "#3a3a3a"
CP_TEXT = "#E0E0E0"

def paste_text(text):
    pyperclip.copy(text)
    import time; time.sleep(0.1)
    import pyautogui; pyautogui.hotkey('ctrl', 'v')


class VoiceThread(QThread):
    result = pyqtSignal(str)
    error  = pyqtSignal(str)

    def __init__(self, lang, phrase_time_limit):
        super().__init__()
        self.lang = lang
        self.phrase_time_limit = phrase_time_limit
        self.running = False

    def run(self):
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                self.running = True
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=self.phrase_time_limit)
                self.running = False
                self.result.emit(recognizer.recognize_google(audio, language=self.lang))
        except Exception as e:
            self.running = False
            self.error.emit(str(e))

    def stop(self):
        self.running = False


class SpaceStopThread(QThread):
    result = pyqtSignal(str)
    error  = pyqtSignal(str)

    def __init__(self, lang):
        super().__init__()
        self.lang = lang
        self.running = False
        self._stop = False

    def run(self):
        try:
            import speech_recognition as sr
            import io, wave, pyaudio
            CHUNK, FORMAT, CHANNELS, RATE = 1024, pyaudio.paInt16, 1, 16000
            p = pyaudio.PyAudio()
            stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                            input=True, frames_per_buffer=CHUNK)
            self.running = True
            frames = []
            while not self._stop:
                frames.append(stream.read(CHUNK, exception_on_overflow=False))
            stream.stop_stream(); stream.close()
            sample_width = p.get_sample_size(FORMAT)
            p.terminate()
            self.running = False
            buf = io.BytesIO()
            with wave.open(buf, 'wb') as wf:
                wf.setnchannels(CHANNELS); wf.setsampwidth(sample_width)
                wf.setframerate(RATE); wf.writeframes(b''.join(frames))
            buf.seek(0)
            recognizer = sr.Recognizer()
            with sr.AudioFile(buf) as source:
                audio = recognizer.record(source)
            self.result.emit(recognizer.recognize_google(audio, language=self.lang))
        except Exception as e:
            self.running = False
            self.error.emit(str(e))

    def stop(self):
        self._stop = True


class ContinuousThread(QThread):
    """Loops recognition, emitting each phrase immediately. Stop with .stop()."""
    result = pyqtSignal(str)
    error  = pyqtSignal(str)

    def __init__(self, lang, phrase_time_limit):
        super().__init__()
        self.lang = lang
        self.phrase_time_limit = phrase_time_limit
        self._stop = False

    def run(self):
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        while not self._stop:
            try:
                with sr.Microphone() as source:
                    audio = recognizer.listen(source, timeout=3, phrase_time_limit=self.phrase_time_limit)
                if self._stop:
                    break
                text = recognizer.recognize_google(audio, language=self.lang)
                if text:
                    self.result.emit(text)
            except sr.WaitTimeoutError:
                continue
            except Exception as e:
                if not self._stop:
                    self.error.emit(str(e))
                break

    def stop(self):
        self._stop = True


class VoiceApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.script_dir  = Path(__file__).parent
        self.config_file = self.script_dir / "voice_config.json"
        self.voice_thread = None
        self._continuous_thread = None
        self._live_recording = False
        self.load_config()
        self.init_ui()
        self.setup_global_hotkey()

    def load_config(self):
        if self.config_file.exists():
            with open(self.config_file) as f:
                self.config = json.load(f)
        else:
            self.config = {
                "language": "en-US", 
                "always_on_top": False,
                "x": 100,
                "y": 100,
                "border_color": CP_RED,
                "open_google": False
            }
            self.save_config()


    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def init_ui(self):
        self.setWindowTitle("Voice Input")
        self.setFixedSize(280, 46)
        
        # Set window position
        self.move(self.config.get("x", 100), self.config.get("y", 100))
        
        flags = Qt.WindowType.FramelessWindowHint
        if self.config.get("always_on_top"):
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)

        self.update_style()

        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setSpacing(4)
        layout.setContentsMargins(8, 2, 8, 2)

        self.status_btn = QPushButton("")
        self.status_btn.setObjectName("help")
        self.status_btn.setFixedWidth(24)
        self.status_btn.setEnabled(False) # Visual only
        self.status_btn.setStyleSheet(f"background-color: {CP_GREEN}; border: 1px solid {CP_GREEN}; padding: 0;")
        layout.addWidget(self.status_btn)

        self.lang_btn = QPushButton()
        self.lang_btn.setObjectName("lang")
        self.lang_btn.setFixedWidth(36)
        self.lang_btn.clicked.connect(self.toggle_language)
        self._update_lang_btn()
        layout.addWidget(self.lang_btn)

        self.record_btn = QPushButton("🎤 REC")
        self.record_btn.clicked.connect(self.toggle_record)
        layout.addWidget(self.record_btn)

        help_btn = QPushButton("?")
        help_btn.setObjectName("help"); help_btn.setFixedWidth(24)
        help_btn.clicked.connect(self.show_help)
        layout.addWidget(help_btn)

        settings_btn = QPushButton("⚙")
        settings_btn.setObjectName("help"); settings_btn.setFixedWidth(24)
        settings_btn.clicked.connect(self.show_settings)
        layout.addWidget(settings_btn)

        close_btn = QPushButton("✕")
        close_btn.setObjectName("help"); close_btn.setFixedWidth(24)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        if self.config.get("hide_record_btn"):
            self.record_btn.setVisible(False)
            self.setFixedSize(190, 46)

    def update_style(self):
        border_color = self.config.get("border_color", CP_RED)
        self.setStyleSheet(f"""
            QMainWindow {{ 
                background-color: {CP_BG}; 
                border: 2px solid {border_color};
            }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 9pt; }}
            QPushButton {{ background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 6px 12px; font-weight: bold; }}
            QPushButton:hover {{ background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }}
            QPushButton:pressed {{ background-color: {CP_YELLOW}; color: black; }}
            QPushButton#lang {{ background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; color: {CP_TEXT}; padding: 4px 4px; }}
            QPushButton#help {{ background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; color: {CP_CYAN}; font-weight: bold; padding: 0; max-height: 24px; }}
            QCheckBox {{ spacing: 6px; color: {CP_TEXT}; }}
            QCheckBox::indicator {{ width: 12px; height: 12px; border: 1px solid {CP_DIM}; background: {CP_PANEL}; }}
            QCheckBox::indicator:checked {{ background: {CP_YELLOW}; border-color: {CP_YELLOW}; }}
            QLineEdit {{ background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; color: {CP_TEXT}; padding: 4px; }}
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()
            # Update config with new position but don't save yet to avoid heavy disk IO
            self.config["x"] = self.x()
            self.config["y"] = self.y()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.save_config()
            event.accept()

    def show_help(self):
        QMessageBox.information(self, "Shortcut",
            "Global Hotkey: Alt + H\n"
            "SPC mode: Space stops recording\n"
            "Live mode: keeps recording until stopped")

    def show_settings(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        dialog.setStyleSheet(self.styleSheet())
        layout = QFormLayout(dialog)

        spin = QSpinBox(); spin.setRange(1, 300)
        spin.setValue(self.config.get("phrase_time_limit", 10)); spin.setSuffix(" sec")
        layout.addRow("Max speak time:", spin)

        # X Position
        x_spin = QSpinBox(); x_spin.setRange(0, 10000)
        x_spin.setValue(self.config.get("x", 100))
        layout.addRow("Window X:", x_spin)

        # Y Position
        y_spin = QSpinBox(); y_spin.setRange(0, 10000)
        y_spin.setValue(self.config.get("y", 100))
        layout.addRow("Window Y:", y_spin)

        # Border Color
        color_edit = QLineEdit()
        color_edit.setText(self.config.get("border_color", CP_RED))
        layout.addRow("Border Color (Hex):", color_edit)

        pin_check = QCheckBox()
        pin_check.setChecked(self.config.get("always_on_top", False))
        layout.addRow("Always on top:", pin_check)

        spc_check = QCheckBox()
        spc_check.setChecked(self.config.get("stop_mode", "auto") == "space")
        layout.addRow("Stop on Space (SPC mode):", spc_check)

        google_check = QCheckBox()
        google_check.setChecked(self.config.get("open_google", False))
        layout.addRow("Open in Google Search:", google_check)

        engine_combo = QComboBox()
        engine_combo.addItems(["Local (one phrase)", "Local (continuous live)"])
        idx = {"local": 0, "browser": 1}.get(self.config.get("engine", "local"), 0)
        engine_combo.setCurrentIndex(idx)
        layout.addRow("Mode:", engine_combo)

        hide_rec_check = QCheckBox()
        hide_rec_check.setChecked(self.config.get("hide_record_btn", False))
        layout.addRow("Hide record button:", hide_rec_check)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept); buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)

        if dialog.exec():
            self.config["phrase_time_limit"] = spin.value()
            
            # Update Position
            self.config["x"] = x_spin.value()
            self.config["y"] = y_spin.value()
            self.move(self.config["x"], self.config["y"])

            # Update Border Color
            self.config["border_color"] = color_edit.text()
            self.update_style()

            new_pin = pin_check.isChecked()
            if new_pin != self.config.get("always_on_top", False):
                self.config["always_on_top"] = new_pin
                flags = Qt.WindowType.FramelessWindowHint
                if new_pin: flags |= Qt.WindowType.WindowStaysOnTopHint
                self.setWindowFlags(flags)
                self.show()

            self.config["stop_mode"] = "space" if spc_check.isChecked() else "auto"
            self.config["open_google"] = google_check.isChecked()
            self.config["engine"] = ["local", "browser"][engine_combo.currentIndex()]
            new_hide = hide_rec_check.isChecked()
            if new_hide != self.config.get("hide_record_btn", False):
                self.config["hide_record_btn"] = new_hide
                self.record_btn.setVisible(not new_hide)
                self.setFixedSize(190 if new_hide else 280, 46)
            self.save_config()

    def setup_global_hotkey(self):
        def on_activate():
            self.toggle_record()

        def on_press(key):
            if key != pynput_keyboard.Key.space:
                return
            if isinstance(self.voice_thread, SpaceStopThread) and self.voice_thread.isRunning():
                self._finish_space_recording()
            elif self._live_recording:
                self._stop_continuous()

        def for_canonical(f):
            return lambda k: f(listener.canonical(k))

        hotkey = pynput_keyboard.HotKey(pynput_keyboard.HotKey.parse('<alt>+h'), on_activate)

        def combined_on_press(k):
            for_canonical(hotkey.press)(k)
            on_press(k)

        listener = pynput_keyboard.Listener(
            on_press=combined_on_press,
            on_release=for_canonical(hotkey.release))
        listener.start()

    def toggle_language(self):
        new_lang = "bn-BD" if self.config["language"] == "en-US" else "en-US"
        self.change_language(new_lang)

    def change_language(self, lang):
        self.config["language"] = lang
        self.save_config()
        self._update_lang_btn()

    def _update_lang_btn(self):
        is_en = self.config["language"] == "en-US"
        self.lang_btn.setText("EN" if is_en else "BN")
        color = CP_RED if is_en else CP_GREEN
        self.lang_btn.setStyleSheet(f"border: 2px solid {color}; color: {color}; font-weight: bold;")

    def toggle_record(self):
        if self.config.get("engine", "local") == "browser":
            if self._live_recording:
                self._stop_continuous()
            else:
                self._start_continuous()
            return

        if self.voice_thread and self.voice_thread.running:
            if self.config.get("stop_mode", "auto") == "space":
                self._finish_space_recording()
            else:
                self.voice_thread.stop()
                self._reset_record_btn()
                self._set_status(CP_YELLOW)
        else:
            self._start_single()

    def _start_single(self):
        self._set_status(CP_RED)
        if self.config.get("stop_mode", "auto") == "space":
            self.record_btn.setText("⏹️ SPC")
            self.voice_thread = SpaceStopThread(self.config["language"])
        else:
            self.record_btn.setText("⏹️ STOP")
            self.voice_thread = VoiceThread(self.config["language"], self.config.get("phrase_time_limit", 10))
        self.record_btn.setStyleSheet(f"background-color: {CP_RED}; color: white; border: 1px solid {CP_RED};")
        self.voice_thread.result.connect(self.on_result)
        self.voice_thread.error.connect(self.on_error)
        self.voice_thread.start()

    def _start_continuous(self):
        self._live_recording = True
        self._set_status(CP_RED)
        self.record_btn.setText("⏹️ LIVE")
        self.record_btn.setStyleSheet(f"background-color: {CP_RED}; color: white; border: 1px solid {CP_RED};")
        self._continuous_thread = ContinuousThread(
            self.config["language"], self.config.get("phrase_time_limit", 10))
        self._continuous_thread.result.connect(self.on_result)
        self._continuous_thread.error.connect(self.on_error)
        self._continuous_thread.finished.connect(self._on_continuous_finished)
        self._continuous_thread.start()

    def _stop_continuous(self):
        if self._continuous_thread and self._continuous_thread.isRunning():
            self._continuous_thread.stop()
        self._live_recording = False
        self._set_status(CP_YELLOW)
        self._reset_record_btn()

    def _on_continuous_finished(self):
        self._live_recording = False
        self._reset_record_btn()

    def _reset_record_btn(self):
        self.record_btn.setText("🎤 REC")
        self.record_btn.setStyleSheet(f"background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white;")

    def _set_status(self, color):
        self.status_btn.setText("")
        self.status_btn.setStyleSheet(f"background-color: {color}; border: 1px solid {color}; padding: 0;")

    def _finish_space_recording(self):
        if isinstance(self.voice_thread, SpaceStopThread):
            self.voice_thread.stop()
        self._reset_record_btn()
        self._set_status(CP_YELLOW)

    def on_result(self, text):
        paste_text(text)
        if self._live_recording:
            self._set_status(CP_GREEN)
            QTimer.singleShot(400, lambda: self._set_status(CP_RED) if self._live_recording else None)
        else:
            self._set_status(CP_GREEN)
            self._reset_record_btn()
            if self.config.get("open_google"):
                webbrowser.open(f"https://www.google.com/search?q={text}")

    def on_error(self, error):
        self._set_status(CP_RED)
        self._reset_record_btn()
        self._live_recording = False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VoiceApp()
    window.show()
    sys.exit(app.exec())
