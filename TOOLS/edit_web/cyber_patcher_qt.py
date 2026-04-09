import sys
import os
import re
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QPlainTextEdit, 
                             QLineEdit, QFileDialog, QMessageBox, QFrame, QStackedWidget)
from PyQt6.QtCore import Qt, QProcess
from PyQt6.QtGui import QFont, QColor, QIcon

# CYBERPUNK THEME PALETTE (From THEME_GUIDE.md)
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

class CyberPatcherQt(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CYBER PATCHER v4.0")
        self.resize(1100, 850)
        
        # State
        self.project_root = os.getcwd()

        self.setup_ui()
        self.apply_theme()

    def apply_theme(self):
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            
            QFrame#Sidebar {{ 
                background-color: {CP_PANEL}; 
                border-right: 1px solid {CP_DIM};
            }}
            
            QLineEdit {{
                background-color: {CP_PANEL}; 
                color: {CP_CYAN}; 
                border: 1px solid {CP_DIM}; 
                padding: 6px;
                selection-background-color: {CP_CYAN};
                selection-color: black;
            }}
            QLineEdit:focus {{ border: 1px solid {CP_CYAN}; }}
            
            QPlainTextEdit {{
                background-color: {CP_PANEL}; 
                color: {CP_CYAN}; 
                border: 1px solid {CP_DIM}; 
                padding: 10px;
                font-size: 11pt;
            }}
            
            QPushButton {{
                background-color: {CP_DIM}; 
                border: 1px solid {CP_DIM}; 
                color: white; 
                padding: 10px; 
                font-weight: bold;
                border-radius: 0px;
            }}
            QPushButton:hover {{
                background-color: #2a2a2a; 
                border: 1px solid {CP_YELLOW}; 
                color: {CP_YELLOW};
            }}
            QPushButton:pressed {{
                background-color: {CP_YELLOW};
                color: black;
            }}
            
            #ApplyBtn {{
                background-color: {CP_RED};
                color: white;
                font-size: 12pt;
            }}
            #ApplyBtn:hover {{
                background-color: "#d92050";
                border: 1px solid white;
            }}
            
            QLabel#Logo {{
                color: {CP_YELLOW};
                font-weight: bold;
                font-size: 20pt;
            }}
            
            QScrollBar:vertical {{
                border: none;
                background: {CP_BG};
                width: 10px;
            }}
            QScrollBar::handle:vertical {{
                background: {CP_DIM};
                min-height: 20px;
            }}
        """)

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- SIDEBAR ---
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(280)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(20, 30, 20, 30)

        logo = QLabel("CYBER\nPATCHER")
        logo.setObjectName("Logo")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(logo)
        
        sidebar_layout.addSpacing(30)

        path_label = QLabel("PROJECT ROOT:")
        path_label.setStyleSheet(f"color: {CP_SUBTEXT}; font-weight: bold;")
        sidebar_layout.addWidget(path_label)

        self.root_input = QLineEdit(self.project_root)
        sidebar_layout.addWidget(self.root_input)

        browse_btn = QPushButton("BROWSE")
        browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_btn.clicked.connect(self.browse_root)
        sidebar_layout.addWidget(browse_btn)

        sidebar_layout.addSpacing(20)
        
        # Action Buttons
        prompt_btn = QPushButton("GENERATE PROMPT")
        prompt_btn.clicked.connect(self.generate_prompt)
        sidebar_layout.addWidget(prompt_btn)

        clean_btn = QPushButton("CLEAN BUFFER")
        clean_btn.clicked.connect(self.clean_buffer)
        sidebar_layout.addWidget(clean_btn)

        settings_btn = QPushButton("SETTINGS")
        settings_btn.clicked.connect(self.toggle_settings)
        sidebar_layout.addWidget(settings_btn)

        restart_btn = QPushButton("RESTART APP")
        restart_btn.clicked.connect(self.restart_app)
        sidebar_layout.addWidget(restart_btn)

        sidebar_layout.addStretch()

        self.apply_btn = QPushButton("🚀 APPLY CHANGES")
        self.apply_btn.setObjectName("ApplyBtn")
        self.apply_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.apply_btn.clicked.connect(self.apply_changes)
        sidebar_layout.addWidget(self.apply_btn)

        main_layout.addWidget(self.sidebar)

        # --- MAIN PANEL ---
        self.stack = QStackedWidget()
        
        # Editor Page
        editor_page = QWidget()
        editor_layout = QVBoxLayout(editor_page)
        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("Paste AI code here...")
        editor_layout.addWidget(QLabel("INPUT BUFFER:"))
        editor_layout.addWidget(self.editor)
        
        # Settings Page (Empty for now)
        settings_page = QWidget()
        settings_layout = QVBoxLayout(settings_page)
        settings_layout.addWidget(QLabel("SETTINGS PANEL"))
        settings_layout.addWidget(QLabel("Option customization coming soon..."))
        settings_layout.addStretch()
        
        self.stack.addWidget(editor_page)
        self.stack.addWidget(settings_page)
        
        main_layout.addWidget(self.stack)

    def browse_root(self):
        path = QFileDialog.getExistingDirectory(self, "Select Project Root")
        if path:
            self.project_root = path
            self.root_input.setText(path)

    def toggle_settings(self):
        if self.stack.currentIndex() == 0:
            self.stack.setCurrentIndex(1)
        else:
            self.stack.setCurrentIndex(0)

    def restart_app(self):
        QApplication.quit()
        # Relative path logic for restart
        subprocess.Popen([sys.executable, __file__])

    def clean_buffer(self):
        content = self.editor.toPlainText()
        content = re.sub(r"```[a-zA-Z]*\n", "", content)
        content = content.replace("```", "")
        self.editor.setPlainText(content.strip())

    def generate_prompt(self):
        prompt = f"""# Protocol: Cyber Patcher Implementation
Project Root Area: {self.root_input.text()}

Provide ALL changes inside ONE single Markdown code block.

Format:
FILE: relative/path/to/file.py
<<<<<<< SEARCH
(exact original lines)
=======
(new code)
>>>>>>> REPLACE
"""
        self.editor.setPlainText(prompt)

    def normalize_text(self, text):
        return "\n".join([line.rstrip() for line in text.splitlines()])

    def apply_changes(self):
        content = self.editor.toPlainText()
        root_path = Path(self.root_input.text())
        
        if not root_path.exists():
            QMessageBox.critical(self, "Error", "Invalid Project Root!")
            return

        # Split content by FILE: header OR --- FILE: header
        file_segments = re.split(r"(?:FILE:|--- FILE:)\s*([^\n-]+)(?:---|)\n", content)
        
        if len(file_segments) < 2:
            QMessageBox.warning(self, "No Blocks", "No FILE: headers found.")
            return

        success_count = 0
        fail_count = 0
        log = []

        for i in range(1, len(file_segments), 2):
            rel_path = file_segments[i].strip().strip("`\"' ")
            blocks_text = file_segments[i+1]
            full_path = root_path / rel_path
            
            p1 = re.compile(r"<<<<<<< SEARCH\n(.*?)\n=======\n(.*?)\n>>>>>>> REPLACE", re.DOTALL)
            p2 = re.compile(r"DELETE:\n(.*?)\nADD:\n(.*?)\n--- END FILE ---", re.DOTALL)
            
            matches = list(p1.finditer(blocks_text)) + list(p2.finditer(blocks_text))
            if not matches: continue

            # File reading
            file_text_raw = ""
            file_text_norm = ""
            line_ending = "\n"
            exists = full_path.exists()
            
            if exists:
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        file_text_raw = f.read()
                        file_text_norm = self.normalize_text(file_text_raw)
                        line_ending = "\r\n" if "\r\n" in file_text_raw else "\n"
                except Exception as e:
                    log.append(f"ERR: Read {rel_path} - {e}")
                    fail_count += 1
                    continue
            
            modified = False
            for m in matches:
                search_str = self.normalize_text(m.group(1))
                replace_str = self.normalize_text(m.group(2))
                
                # Failsafe: Remove markers accidentally present in replace_str
                for marker in ["<<<<<<< SEARCH", "=======", ">>>>>>> REPLACE"]:
                    if marker in replace_str:
                        replace_str = replace_str.replace(marker, f"# [CLEANED {marker}]")

                # New file
                if not search_str.strip() and not exists:
                    try:
                        full_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(full_path, "w", encoding="utf-8") as f:
                            f.write(replace_str)
                        success_count += 1
                        log.append(f"CREATE: {rel_path}")
                        exists = True
                        file_text_norm = replace_str
                        modified = True
                        continue
                    except Exception as e:
                        fail_count += 1
                        log.append(f"ERR: Create {rel_path} - {e}")
                        continue

                # Patch
                if search_str in file_text_norm:
                    file_text_norm = file_text_norm.replace(search_str, replace_str, 1)
                    success_count += 1
                    modified = True
                    log.append(f"PATCH: {rel_path}")
                else:
                    fail_count += 1
                    log.append(f"MATCH FAIL: {rel_path}")

            if modified:
                try:
                    with open(full_path, "w", encoding="utf-8", newline=line_ending) as f:
                        f.write(file_text_norm)
                except Exception as e:
                    log.append(f"WRITE ERR: {rel_path} - {e}")

        summary = f"Success: {success_count}\nFail: {fail_count}\n\n" + "\n".join(log)
        QMessageBox.information(self, "Results", summary)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CyberPatcherQt()
    window.show()
    sys.exit(app.exec())
