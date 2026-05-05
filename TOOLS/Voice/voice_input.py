import sys
import os
import json
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QComboBox, QCheckBox, QMessageBox, QDialog, QSpinBox, QFormLayout, QDialogButtonBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
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

class VoiceThread(QThread):
    result = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, lang, phrase_time_limit, stop_on_space=False):
        super().__init__()
        self.lang = lang
        self.phrase_time_limit = phrase_time_limit
        self.stop_on_space = stop_on_space
        self.running = False
        self._stopper = None

    def run(self):
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                self.running = True
                if self.stop_on_space:
                    # Record until stop() is called (space pressed), no silence cutoff
                    self._stopper = recognizer.listen_in_background(source, self._bg_callback)
                else:
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=self.phrase_time_limit)
                    self.running = False
                    text = recognizer.recognize_google(audio, language=self.lang)
                    self.result.emit(text)
        except Exception as e:
            self.running = False
            self.error.emit(str(e))

    def _bg_callback(self, recognizer, audio):
        pass  # not used; we collect manually

    def stop(self):
        self.running = False

    def stop_and_recognize(self):
        """Called when space is pressed in SPC mode — stops background and recognizes."""
        self.running = False
        if self._stopper:
            self._stopper(wait_for_stop=False)
            self._stopper = None


class SpaceStopThread(QThread):
    """Records audio until stop_event is set, then emits result."""
    result = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, lang):
        super().__init__()
        self.lang = lang
        self.running = False
        self._stop = False

    def run(self):
        try:
            import speech_recognition as sr
            import io
            import wave
            import pyaudio

            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 16000

            p = pyaudio.PyAudio()
            stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                            input=True, frames_per_buffer=CHUNK)
            self.running = True
            frames = []
            while not self._stop:
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)
            stream.stop_stream()
            stream.close()
            p.terminate()
            self.running = False

            # Build WAV in memory
            buf = io.BytesIO()
            with wave.open(buf, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))
            buf.seek(0)

            recognizer = sr.Recognizer()
            with sr.AudioFile(buf) as source:
                audio = recognizer.record(source)
            text = recognizer.recognize_google(audio, language=self.lang)
            self.result.emit(text)
        except Exception as e:
            self.running = False
            self.error.emit(str(e))

    def stop(self):
        self._stop = True


class VoiceApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.script_dir = Path(__file__).parent
        self.config_file = self.script_dir / "voice_config.json"
        self.voice_thread = None
        self.load_config()
        self.init_ui()
        self.setup_global_hotkey()
        
    def load_config(self):
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {"language": "en-US", "always_on_top": False}
            self.save_config()
    
    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def init_ui(self):
        self.setWindowTitle("Voice Input")
        self.setFixedSize(345, 50)
        
        if self.config.get("always_on_top", False):
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 9pt; }}
            QComboBox {{ background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 3px; }}
            QComboBox::drop-down {{ border: none; }}
            QComboBox QAbstractItemView {{ background-color: {CP_PANEL}; color: {CP_CYAN}; selection-background-color: {CP_CYAN}; selection-color: #000000; }}
            QPushButton {{ background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 6px 12px; font-weight: bold; }}
            QPushButton:hover {{ background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }}
            QPushButton:pressed {{ background-color: {CP_YELLOW}; color: black; }}
            QPushButton#lang {{ background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; color: {CP_TEXT}; padding: 4px 8px; }}
            QPushButton#lang:checked {{ border: 2px solid {CP_GREEN}; color: {CP_GREEN}; }}
            QPushButton#help {{ background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; color: {CP_CYAN}; font-weight: bold; padding: 0; max-height: 24px; }}
            QPushButton#mode {{ background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; color: {CP_TEXT}; padding: 4px 6px; font-size: 8pt; }}
            QPushButton#mode:checked {{ border: 2px solid {CP_YELLOW}; color: {CP_YELLOW}; }}
            QCheckBox {{ spacing: 6px; color: {CP_TEXT}; }}
            QCheckBox::indicator {{ width: 12px; height: 12px; border: 1px solid {CP_DIM}; background: {CP_PANEL}; }}
            QCheckBox::indicator:checked {{ background: {CP_YELLOW}; border-color: {CP_YELLOW}; }}
        """)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setSpacing(6)
        layout.setContentsMargins(8, 5, 8, 5)
        
        self.status_label = QLabel("●")
        self.status_label.setStyleSheet(f"color: {CP_GREEN}; font-weight: bold; font-size: 14pt;")
        layout.addWidget(self.status_label)
        
        self.en_btn = QPushButton("EN")
        self.en_btn.setObjectName("lang")
        self.en_btn.setCheckable(True)
        self.en_btn.setChecked(self.config["language"] == "en-US")
        self.en_btn.clicked.connect(lambda: self.change_language("en-US"))
        layout.addWidget(self.en_btn)
        
        self.bd_btn = QPushButton("BD")
        self.bd_btn.setObjectName("lang")
        self.bd_btn.setCheckable(True)
        self.bd_btn.setChecked(self.config["language"] == "bn-BD")
        self.bd_btn.clicked.connect(lambda: self.change_language("bn-BD"))
        layout.addWidget(self.bd_btn)
        
        self.pin_check = QCheckBox("Pin")
        self.pin_check.setChecked(self.config.get("always_on_top", False))
        self.pin_check.stateChanged.connect(self.toggle_pin)
        layout.addWidget(self.pin_check)

        # Stop mode toggle: AUTO vs SPC
        self.mode_btn = QPushButton("AUTO")
        self.mode_btn.setObjectName("mode")
        self.mode_btn.setCheckable(True)
        self.mode_btn.setChecked(self.config.get("stop_mode", "auto") == "space")
        self.mode_btn.setText("SPC" if self.mode_btn.isChecked() else "AUTO")
        self.mode_btn.clicked.connect(self.toggle_stop_mode)
        layout.addWidget(self.mode_btn)
        
        self.record_btn = QPushButton("🎤 REC")
        self.record_btn.clicked.connect(self.toggle_record)
        layout.addWidget(self.record_btn)
        
        help_btn = QPushButton("?")
        help_btn.setObjectName("help")
        help_btn.setFixedWidth(24)
        help_btn.clicked.connect(self.show_help)
        layout.addWidget(help_btn)

        settings_btn = QPushButton("⚙")
        settings_btn.setObjectName("help")
        settings_btn.setFixedWidth(24)
        settings_btn.clicked.connect(self.show_settings)
        layout.addWidget(settings_btn)

    def toggle_stop_mode(self):
        is_space = self.mode_btn.isChecked()
        self.mode_btn.setText("SPC" if is_space else "AUTO")
        self.config["stop_mode"] = "space" if is_space else "auto"
        self.save_config()
    
    def show_help(self):
        QMessageBox.information(self, "Shortcut", "Global Hotkey: Alt + H\nSPC mode: press Space to stop recording")

    def show_settings(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        dialog.setStyleSheet(self.styleSheet())
        layout = QFormLayout(dialog)
        spin = QSpinBox()
        spin.setRange(1, 300)
        spin.setValue(self.config.get("phrase_time_limit", 10))
        spin.setSuffix(" sec")
        layout.addRow("Max speak time (AUTO):", spin)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        if dialog.exec():
            self.config["phrase_time_limit"] = spin.value()
            self.save_config()

    def setup_global_hotkey(self):
        def on_activate():
            self.toggle_record()

        def on_press(key):
            # Space stops recording in SPC mode
            if (self.config.get("stop_mode", "auto") == "space"
                    and self.voice_thread and self.voice_thread.running
                    and key == pynput_keyboard.Key.space):
                self.voice_thread.stop()
                self._finish_space_recording()

        def for_canonical(f):
            return lambda k: f(listener.canonical(k))
        
        hotkey = pynput_keyboard.HotKey(pynput_keyboard.HotKey.parse('<alt>+h'), on_activate)
        listener = pynput_keyboard.Listener(
            on_press=lambda k: (for_canonical(hotkey.press)(k), on_press(k)),
            on_release=for_canonical(hotkey.release)
        )
        listener.start()
    
    def toggle_pin(self, state):
        self.config["always_on_top"] = bool(state)
        self.save_config()
        if state:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
        self.show()
    
    def change_language(self, lang):
        self.config["language"] = lang
        self.save_config()
        self.en_btn.setChecked(lang == "en-US")
        self.bd_btn.setChecked(lang == "bn-BD")
    
    def toggle_record(self):
        if self.voice_thread and self.voice_thread.running:
            if self.config.get("stop_mode", "auto") == "space":
                self.voice_thread.stop()
                self._finish_space_recording()
            else:
                self.voice_thread.stop()
                self.record_btn.setText("🎤 REC")
                self.status_label.setText("●")
                self.status_label.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold; font-size: 14pt;")
        else:
            self.start_recording()
    
    def start_recording(self):
        self.status_label.setText("●")
        self.status_label.setStyleSheet(f"color: {CP_RED}; font-weight: bold; font-size: 14pt;")

        if self.config.get("stop_mode", "auto") == "space":
            self.record_btn.setText("⏹️ SPC")
            self.voice_thread = SpaceStopThread(self.config["language"])
        else:
            self.record_btn.setText("⏹️ STOP")
            self.voice_thread = VoiceThread(self.config["language"], self.config.get("phrase_time_limit", 10))

        self.voice_thread.result.connect(self.on_result)
        self.voice_thread.error.connect(self.on_error)
        self.voice_thread.start()

    def _finish_space_recording(self):
        """Stop SpaceStopThread and let it recognize."""
        if isinstance(self.voice_thread, SpaceStopThread):
            self.voice_thread.stop()
        self.record_btn.setText("🎤 REC")
        self.status_label.setText("●")
        self.status_label.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold; font-size: 14pt;")

    def on_result(self, text):
        self.status_label.setText("●")
        self.status_label.setStyleSheet(f"color: {CP_GREEN}; font-weight: bold; font-size: 14pt;")
        self.record_btn.setText("🎤 REC")
        
        pyperclip.copy(text)
        import time
        time.sleep(0.1)
        import pyautogui
        pyautogui.hotkey('ctrl', 'v')
    
    def on_error(self, error):
        self.status_label.setText("✕")
        self.status_label.setStyleSheet(f"color: {CP_RED}; font-weight: bold; font-size: 14pt;")
        self.record_btn.setText("🎤 REC")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VoiceApp()
    window.show()
    sys.exit(app.exec())
