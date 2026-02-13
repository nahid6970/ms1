import os
import sys
import subprocess
import json
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QGridLayout, QFrame, QLineEdit)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont

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

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXECUTOR_SCRIPT = os.path.join(SCRIPT_DIR, "executor.py")

class CyberButton(QPushButton):
    def __init__(self, text, bg_color, text_color=CP_BG, border_color=CP_DIM):
        super().__init__(text)
        hover_text = bg_color
        style = f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {border_color};
                padding: 12px;
                font-family: 'Consolas';
                font-weight: bold;
                font-size: 12pt;
                border-radius: 0px;
            }}
            QPushButton:hover {{
                background-color: {CP_BG};
                color: {hover_text};
                border: 1px solid {hover_text};
            }}
            QPushButton:focus {{
                background-color: {CP_BG};
                color: {hover_text};
                border: 2px solid {CP_YELLOW};
                padding: 11px;
            }}
        """
        self.setStyleSheet(style)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Left, Qt.Key.Key_Right):
            event.ignore()
        else:
            super().keyPressEvent(event)

class TerminalChooser(QWidget):
    def __init__(self, data_file):
        super().__init__()
        self.data_file = data_file
        
        # Load data from temp file
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        self.selection = data.get('selection', '')
        self.query = data.get('query', '')
        self.stored_shell = data.get('shell', 'pwsh')
        self.stored_dir = data.get('dir', '')
        
        # Strip markers from selection if present
        clean_selection = self.selection
        if clean_selection.startswith("* "): clean_selection = clean_selection[2:]
        elif clean_selection.startswith("  "): clean_selection = clean_selection[2:]
        
        self.command = clean_selection if clean_selection else self.query
        self.clean_selection = clean_selection
        
        self.buttons = []
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.init_ui()
        self.center_window()
        
        if self.buttons:
            found = False
            for btn in self.buttons:
                if btn.text().lower() == self.stored_shell.lower():
                    btn.setFocus()
                    found = True
                    break
            if not found:
                self.buttons[0].setFocus()
        
    def init_ui(self):
        self.main_frame = QFrame(self)
        self.main_frame.setObjectName("MainFrame")
        self.main_frame.setStyleSheet(f"#MainFrame {{ background-color: {CP_BG}; border: 2px solid {CP_ORANGE}; }} QLabel {{ color: {CP_TEXT}; font-family: 'Consolas'; }}")
        
        layout = QVBoxLayout(self.main_frame)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header_layout = QHBoxLayout()
        title_label = QLabel(f"// EXECUTE COMMAND")
        title_label.setStyleSheet(f"color: {CP_ORANGE}; font-weight: bold; font-size: 14pt;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        close_btn = QPushButton("X")
        close_btn.setFixedWidth(30)
        close_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        close_btn.setStyleSheet(f"QPushButton {{ background-color: transparent; color: {CP_RED}; border: 1px solid {CP_RED}; font-family: 'Consolas'; }} QPushButton:hover {{ background-color: {CP_RED}; color: {CP_BG}; }}")
        close_btn.clicked.connect(self.close)
        header_layout.addWidget(close_btn)
        layout.addLayout(header_layout)
        
        cmd_preview = QLabel(self.command if len(self.command) < 50 else self.command[:47] + "...")
        cmd_preview.setStyleSheet(f"color: {CP_CYAN}; font-style: italic; margin-bottom: 10px;")
        layout.addWidget(cmd_preview)
        
        layout.addWidget(QLabel(">> SELECT TERMINAL"))
        
        terminals = [
            ("CMD", CP_YELLOW),
            ("POWERSHELL", CP_CYAN),
            ("PWSH", CP_GREEN)
        ]
        
        grid = QGridLayout()
        grid.setSpacing(10)
        for i, (name, color) in enumerate(terminals):
            btn = CyberButton(name, color)
            btn.clicked.connect(lambda checked, n=name.lower(): self.handle_action(n))
            grid.addWidget(btn, 0, i)
            self.buttons.append(btn)
        
        layout.addLayout(grid)
        
        # Directory Input Section
        layout.addSpacing(15)
        layout.addWidget(QLabel(">> WORKING DIRECTORY"))
        self.dir_input = QLineEdit(self.stored_dir)
        self.dir_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {CP_PANEL};
                color: {CP_CYAN};
                border: 1px solid {CP_DIM};
                padding: 8px;
                font-family: 'Consolas';
                font-size: 10pt;
            }}
            QLineEdit:focus {{
                border: 1px solid {CP_CYAN};
            }}
        """)
        self.dir_input.textChanged.connect(self.update_dir_list)
        layout.addWidget(self.dir_input)
        
        self.dir_list_label = QLabel("")
        self.dir_list_label.setStyleSheet(f"color: {CP_DIM}; font-size: 9pt; margin-top: 5px;")
        layout.addWidget(self.dir_list_label)
        self.update_dir_list()
        
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(self.main_frame)
    
    def update_dir_list(self):
        dir_path = self.dir_input.text().strip()
        if dir_path and os.path.isdir(dir_path):
            try:
                items = [d for d in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, d))][:5]
                self.dir_list_label.setText(" | ".join(items) if items else "")
            except:
                self.dir_list_label.setText("")
        else:
            self.dir_list_label.setText("")
        
    def center_window(self):
        self.adjustSize()
        screen = QApplication.primaryScreen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
        
    def handle_action(self, shell):
        dir_path = self.dir_input.text().strip()
        # Launch executor.py with clean selection and directory
        subprocess.Popen(['python', EXECUTOR_SCRIPT, shell, self.clean_selection, self.query, self.stored_shell, dir_path])
        self.close()

    def keyPressEvent(self, event):
        current_widget = self.focusWidget()
        if current_widget in self.buttons:
            idx = self.buttons.index(current_widget)
            if event.key() == Qt.Key.Key_Right and idx < len(self.buttons) - 1:
                self.buttons[idx+1].setFocus()
            elif event.key() == Qt.Key.Key_Left and idx > 0:
                self.buttons[idx-1].setFocus()
            elif event.key() == Qt.Key.Key_Down:
                self.dir_input.setFocus()
            elif event.key() == Qt.Key.Key_Escape:
                self.close()
            elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                current_widget.click()
        elif current_widget == self.dir_input:
            if event.key() == Qt.Key.Key_Up:
                self.buttons[0].setFocus()
            elif event.key() == Qt.Key.Key_Escape:
                self.close()
            elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                # Trigger action on stored shell or first shell if enter pressed in input
                shell_to_use = self.stored_shell if self.stored_shell else "pwsh"
                self.handle_action(shell_to_use)
        else:
            super().keyPressEvent(event)

    def changeEvent(self, event):
        if event.type() == event.Type.ActivationChange and not self.isActiveWindow():
            self.close()
        super().changeEvent(event)
    
    def closeEvent(self, event):
        # Clean up temp file when closing
        if os.path.exists(self.data_file):
            try: os.remove(self.data_file)
            except: pass
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Consolas", 10))
    
    if len(sys.argv) > 1:
        data_file = sys.argv[1]
        if os.path.exists(data_file):
            window = TerminalChooser(data_file)
            window.show()
            window.activateWindow()
            window.raise_()
            sys.exit(app.exec())
