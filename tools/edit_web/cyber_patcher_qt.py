import sys
import os
import re
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QPlainTextEdit, 
                             QLineEdit, QFileDialog, QMessageBox, QFrame, QStackedWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QIcon

# CYBERPUNK THEME PALETTE
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
        self.setWindowTitle("CYBER PATCHER v5.0 - RANGE EDITION")
        self.resize(1150, 900)
        self.project_root = os.getcwd()
        self.setup_ui()
        self.apply_theme()

    def apply_theme(self):
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            QFrame#Sidebar {{ background-color: {CP_PANEL}; border-right: 1px solid {CP_DIM}; }}
            QLineEdit {{ background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 6px; }}
            QLineEdit:focus {{ border: 1px solid {CP_CYAN}; }}
            QPlainTextEdit {{ background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 10px; font-size: 11pt; }}
            QPushButton {{ background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 10px; font-weight: bold; border-radius: 0px; }}
            QPushButton:hover {{ background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }}
            #ApplyBtn {{ background-color: {CP_RED}; color: white; font-size: 12pt; }}
            QLabel#Logo {{ color: {CP_YELLOW}; font-weight: bold; font-size: 20pt; }}
        """)

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(280)
        side_lay = QVBoxLayout(self.sidebar)
        
        logo = QLabel("CYBER\nPATCHER")
        logo.setObjectName("Logo")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        side_lay.addWidget(logo)
        
        side_lay.addSpacing(30)
        side_lay.addWidget(QLabel("PROJECT ROOT:"))
        self.root_input = QLineEdit(self.project_root)
        side_lay.addWidget(self.root_input)
        
        browse_btn = QPushButton("BROWSE")
        browse_btn.clicked.connect(self.browse_root)
        side_lay.addWidget(browse_btn)
        
        side_lay.addSpacing(20)
        prompt_btn = QPushButton("GENERATE PROMPT")
        prompt_btn.clicked.connect(self.generate_prompt)
        side_lay.addWidget(prompt_btn)

        clean_btn = QPushButton("CLEAN BUFFER")
        clean_btn.clicked.connect(self.clean_buffer)
        side_lay.addWidget(clean_btn)

        restart_btn = QPushButton("RESTART APP")
        restart_btn.clicked.connect(self.restart_app)
        side_lay.addWidget(restart_btn)

        side_lay.addStretch()
        self.apply_btn = QPushButton("🚀 APPLY CHANGES")
        self.apply_btn.setObjectName("ApplyBtn")
        self.apply_btn.clicked.connect(self.apply_changes)
        side_lay.addWidget(self.apply_btn)
        
        layout.addWidget(self.sidebar)

        # Editor
        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("Paste AI code here...")
        layout.addWidget(self.editor)

    def browse_root(self):
        path = QFileDialog.getExistingDirectory(self, "Select Project Root")
        if path: self.root_input.setText(path)

    def restart_app(self):
        QApplication.quit()
        subprocess.Popen([sys.executable, __file__])

    def clean_buffer(self):
        content = self.editor.toPlainText()
        content = re.sub(r"```[a-zA-Z]*\n", "", content)
        content = content.replace("```", "")
        self.editor.setPlainText(content.strip())

    def generate_prompt(self):
        prompt = f"""# Protocol: Cyber Patcher v5.0
Project Root: {self.root_input.text()}

1. USE RANGE BLOCKS for deleting/replacing large code chunks.
2. USE SEARCH/REPLACE for small targeted edits.

--- RANGE FORMAT (Best for large blocks) ---
FILE: path/file.py
RANGE START: <exact line starting the block>
RANGE END: <exact line ending the block>
REPLACE WITH:
<new code or leave empty to delete>
--- END RANGE ---

--- SEARCH/REPLACE FORMAT (Best for small edits) ---
FILE: path/file.py
<<<<<<< SEARCH
...
=======
...
>>>>>>> REPLACE
"""
        self.editor.setPlainText(prompt)

    def normalize(self, text):
        return "\n".join([line.strip() for line in text.splitlines()])

    def apply_changes(self):
        content = self.editor.toPlainText()
        root_path = Path(self.root_input.text())
        
        file_segments = re.split(r"(?:FILE:|--- FILE:)\s*([^\n-]+)(?:---|)\n", content)
        if len(file_segments) < 2:
            QMessageBox.warning(self, "No Headers", "No FILE: headers found.")
            return

        success, fail, log = 0, 0, []

        for i in range(1, len(file_segments), 2):
            rel_path = file_segments[i].strip().strip("`\"' ")
            seg_text = file_segments[i+1]
            full_path = root_path / rel_path
            
            # --- 1. RANGE PARSING ---
            range_pattern = re.compile(r"RANGE START:\s*(?P<start>.*?)\nRANGE END:\s*(?P<end>.*?)\nREPLACE WITH:\n(?P<with>.*?)\n--- END RANGE ---", re.DOTALL)
            range_matches = list(range_pattern.finditer(seg_text))
            
            # --- 2. SEARCH/REPLACE PARSING ---
            sr_pattern = re.compile(r"<<<<<<< SEARCH\n(.*?)\n=======\n(.*?)\n>>>>>>> REPLACE", re.DOTALL)
            sr_matches = list(sr_pattern.finditer(seg_text))

            if not range_matches and not sr_matches: continue

            if not full_path.exists():
                fail += 1; log.append(f"MISSING: {rel_path}"); continue

            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    file_text = f.read()
                    lines = file_text.splitlines()
                
                modified = False

                # Handle Range Matches
                for rm in range_matches:
                    start_anchor = rm.group("start").strip()
                    end_anchor = rm.group("end").strip()
                    new_code = rm.group("with")
                    
                    start_idx, end_idx = -1, -1
                    for idx, line in enumerate(lines):
                        if start_anchor in line and start_idx == -1: start_idx = idx
                        if end_anchor in line and start_idx != -1: end_idx = idx; break
                    
                    if start_idx != -1 and end_idx != -1:
                        # Replace lines from start_idx to end_idx
                        lines[start_idx:end_idx+1] = [new_code]
                        success += 1; modified = True; log.append(f"RANGE PATCHED: {rel_path}")
                    else:
                        fail += 1; log.append(f"RANGE MISMATCH: {rel_path} (Start/End not found)")

                # Handle S/R Matches
                if not modified: # If already modified by range, lines are now different. 
                    # Simpler for now: Either use Range OR S/R in one file segment. 
                    # Re-join lines for S/R
                    file_text_temp = "\n".join(lines)
                    for sm in sr_matches:
                        s, r = self.normalize(sm.group(1)), self.normalize(sm.group(2))
                        if s in self.normalize(file_text_temp):
                            # Fuzzy replace using normalized check but applying to temp text
                            # (Simplified exact match for now)
                            if sm.group(1) in file_text_temp:
                                file_text_temp = file_text_temp.replace(sm.group(1), sm.group(2), 1)
                                success += 1; modified = True; log.append(f"S/R PATCHED: {rel_path}")
                    if modified: lines = file_text_temp.splitlines()

                if modified:
                    le = "\r\n" if "\r\n" in file_text else "\n"
                    with open(full_path, "w", encoding="utf-8", newline=le) as f:
                        f.write("\n".join(lines))
            except Exception as e:
                fail += 1; log.append(f"CRITICAL: {rel_path} - {e}")

        QMessageBox.information(self, "Result", f"Success: {success}\nFail: {fail}\n\n" + "\n".join(log))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CyberPatcherQt()
    window.show()
    sys.exit(app.exec())
