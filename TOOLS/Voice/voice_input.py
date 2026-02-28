import sys
import os
import json
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QComboBox, QCheckBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
import pyperclip
from pynput import keyboard

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
    
    def __init__(self, lang):
        super().__init__()
        self.lang = lang
        self.running = False
        
    def run(self):
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                self.running = True
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                self.running = False
                text = recognizer.recognize_google(audio, language=self.lang)
                self.result.emit(text)
        except Exception as e:
            self.running = False
            self.error.emit(str(e))
    
    def stop(self):
        self.running = False

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
        self.setFixedSize(300, 50)
        
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
        
        layout.addWidget(QLabel("Lang:"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["en-US", "bn-BD"])
        self.lang_combo.setCurrentText(self.config["language"])
        self.lang_combo.currentTextChanged.connect(self.change_language)
        layout.addWidget(self.lang_combo)
        
        self.pin_check = QCheckBox("Pin")
        self.pin_check.setChecked(self.config.get("always_on_top", False))
        self.pin_check.stateChanged.connect(self.toggle_pin)
        layout.addWidget(self.pin_check)
        
        self.record_btn = QPushButton("🎤 REC")
        self.record_btn.clicked.connect(self.toggle_record)
        layout.addWidget(self.record_btn)
        
        layout.addStretch()
    
    def setup_global_hotkey(self):
        def on_activate():
            self.toggle_record()
        
        def for_canonical(f):
            return lambda k: f(listener.canonical(k))
        
        hotkey = keyboard.HotKey(keyboard.HotKey.parse('<alt>+h'), on_activate)
        listener = keyboard.Listener(on_press=for_canonical(hotkey.press), on_release=for_canonical(hotkey.release))
        listener.start()
    
    def toggle_pin(self, state):
        self.config["always_on_top"] = bool(state)
        self.save_config()
        if state:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
        self.show()
    
    def change_language(self, text):
        self.config["language"] = text
        self.save_config()
    
    def toggle_record(self):
        if self.voice_thread and self.voice_thread.running:
            self.voice_thread.stop()
            self.record_btn.setText("🎤 REC")
            self.status_label.setText("●")
            self.status_label.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold; font-size: 14pt;")
        else:
            self.start_recording()
    
    def start_recording(self):
        self.status_label.setText("●")
        self.status_label.setStyleSheet(f"color: {CP_RED}; font-weight: bold; font-size: 14pt;")
        self.record_btn.setText("⏹️ STOP")
        
        self.voice_thread = VoiceThread(self.config["language"])
        self.voice_thread.result.connect(self.on_result)
        self.voice_thread.error.connect(self.on_error)
        self.voice_thread.start()
    
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
