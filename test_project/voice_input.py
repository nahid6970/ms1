import sys
import os
import json
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QTextEdit, QComboBox, QGroupBox, QCheckBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
import pyperclip
from pynput import keyboard

# CYBERPUNK PALETTE
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
            self.config = {"language": "en-US", "always_on_top": False, "auto_paste": False}
            self.save_config()
    
    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def init_ui(self):
        self.setWindowTitle("Voice Input")
        self.resize(500, 450)
        
        # Apply always on top from config
        if self.config.get("always_on_top", False):
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            
            QTextEdit {{
                background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 8px;
                selection-background-color: {CP_CYAN}; selection-color: #000000;
            }}
            
            QComboBox {{
                background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px;
            }}
            QComboBox:focus {{ border: 1px solid {CP_CYAN}; }}
            QComboBox::drop-down {{ border: none; }}
            QComboBox QAbstractItemView {{
                background-color: {CP_PANEL}; color: {CP_CYAN}; selection-background-color: {CP_CYAN}; selection-color: #000000;
            }}
            
            QPushButton {{
                background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 8px 16px; font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW};
            }}
            QPushButton:pressed {{
                background-color: {CP_YELLOW}; color: black;
            }}
            QPushButton:disabled {{
                background-color: #1a1a1a; color: #555555; border: 1px solid #1a1a1a;
            }}
            
            QGroupBox {{
                border: 1px solid {CP_DIM}; margin-top: 10px; padding-top: 10px; font-weight: bold; color: {CP_YELLOW};
            }}
            QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }}
            
            QLabel {{ color: {CP_TEXT}; }}
            
            QCheckBox {{
                spacing: 8px; color: {CP_TEXT};
            }}
            QCheckBox::indicator {{
                width: 14px; height: 14px; border: 1px solid {CP_DIM}; background: {CP_PANEL};
            }}
            QCheckBox::indicator:checked {{
                background: {CP_YELLOW}; border-color: {CP_YELLOW};
            }}
        """)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(10)
        
        # Status
        self.status_label = QLabel("READY")
        self.status_label.setStyleSheet(f"color: {CP_GREEN}; font-weight: bold; font-size: 12pt;")
        layout.addWidget(self.status_label)
        
        # Settings
        settings_group = QGroupBox("SETTINGS")
        settings_layout = QVBoxLayout()
        
        # Language
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Language:"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English (en-US)", "Bengali (bn-BD)"])
        self.lang_combo.setCurrentText("English (en-US)" if self.config["language"] == "en-US" else "Bengali (bn-BD)")
        self.lang_combo.currentTextChanged.connect(self.change_language)
        lang_layout.addWidget(self.lang_combo)
        settings_layout.addLayout(lang_layout)
        
        # Pin window
        self.pin_check = QCheckBox("📌 Always on Top")
        self.pin_check.setChecked(self.config.get("always_on_top", False))
        self.pin_check.stateChanged.connect(self.toggle_pin)
        settings_layout.addWidget(self.pin_check)
        
        # Auto paste
        self.paste_check = QCheckBox("⚡ Auto-paste to active window")
        self.paste_check.setChecked(self.config.get("auto_paste", False))
        self.paste_check.stateChanged.connect(self.toggle_auto_paste)
        settings_layout.addWidget(self.paste_check)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Output
        output_group = QGroupBox("OUTPUT")
        output_layout = QVBoxLayout()
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Consolas", 11))
        output_layout.addWidget(self.output_text)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.record_btn = QPushButton("🎤 RECORD")
        self.record_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.record_btn.clicked.connect(self.toggle_record)
        
        self.copy_btn = QPushButton("📋 COPY")
        self.copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_btn.clicked.connect(self.copy_text)
        
        self.clear_btn = QPushButton("🗑️ CLEAR")
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn.clicked.connect(self.clear_text)
        
        self.restart_btn = QPushButton("🔄 RESTART")
        self.restart_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.restart_btn.clicked.connect(self.restart_app)
        
        btn_layout.addWidget(self.record_btn)
        btn_layout.addWidget(self.copy_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addWidget(self.restart_btn)
        
        layout.addLayout(btn_layout)
    
    def setup_global_hotkey(self):
        def on_activate():
            self.toggle_record()
        
        def for_canonical(f):
            return lambda k: f(listener.canonical(k))
        
        hotkey = keyboard.HotKey(
            keyboard.HotKey.parse('<alt>+h'),
            on_activate)
        
        listener = keyboard.Listener(
            on_press=for_canonical(hotkey.press),
            on_release=for_canonical(hotkey.release))
        listener.start()
    
    def toggle_pin(self, state):
        self.config["always_on_top"] = bool(state)
        self.save_config()
        
        if state:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
        self.show()
    
    def toggle_auto_paste(self, state):
        self.config["auto_paste"] = bool(state)
        self.save_config()
    
    def change_language(self, text):
        self.config["language"] = "en-US" if "English" in text else "bn-BD"
        self.save_config()
        self.status_label.setText(f"LANGUAGE: {text.split()[0].upper()}")
        self.status_label.setStyleSheet(f"color: {CP_CYAN}; font-weight: bold; font-size: 12pt;")
    
    def toggle_record(self):
        if self.voice_thread and self.voice_thread.running:
            self.voice_thread.stop()
            self.record_btn.setText("🎤 RECORD")
            self.status_label.setText("STOPPED")
            self.status_label.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold; font-size: 12pt;")
        else:
            self.start_recording()
    
    def start_recording(self):
        self.status_label.setText("LISTENING...")
        self.status_label.setStyleSheet(f"color: {CP_RED}; font-weight: bold; font-size: 12pt;")
        self.record_btn.setText("⏹️ STOP")
        
        self.voice_thread = VoiceThread(self.config["language"])
        self.voice_thread.result.connect(self.on_result)
        self.voice_thread.error.connect(self.on_error)
        self.voice_thread.start()
    
    def on_result(self, text):
        self.output_text.append(text)
        self.status_label.setText("SUCCESS")
        self.status_label.setStyleSheet(f"color: {CP_GREEN}; font-weight: bold; font-size: 12pt;")
        self.record_btn.setText("🎤 RECORD")
        
        # Auto-paste if enabled
        if self.config.get("auto_paste", False):
            pyperclip.copy(text)
            import pyautogui
            pyautogui.hotkey('ctrl', 'v')
    
    def on_error(self, error):
        self.status_label.setText(f"ERROR: {error}")
        self.status_label.setStyleSheet(f"color: {CP_RED}; font-weight: bold; font-size: 12pt;")
        self.record_btn.setText("🎤 RECORD")
    
    def copy_text(self):
        text = self.output_text.toPlainText()
        if text:
            pyperclip.copy(text)
            self.status_label.setText("COPIED")
            self.status_label.setStyleSheet(f"color: {CP_GREEN}; font-weight: bold; font-size: 12pt;")
    
    def clear_text(self):
        self.output_text.clear()
        self.status_label.setText("CLEARED")
        self.status_label.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold; font-size: 12pt;")
    
    def restart_app(self):
        QApplication.quit()
        os.execv(sys.executable, [sys.executable] + sys.argv)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VoiceApp()
    window.show()
    sys.exit(app.exec())
