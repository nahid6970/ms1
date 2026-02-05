import os
import sys
import subprocess
import json
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QGridLayout, QFrame)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QFont, QCursor, QColor

# CYBERPUNK THEME PALETTE
CP_BG = "#050505"           # Main Window Background
CP_PANEL = "#111111"        # Panel/Input Background
CP_YELLOW = "#FCEE0A"       # Accent: Yellow
CP_CYAN = "#00F0FF"         # Accent: Cyan
CP_RED = "#FF003C"          # Accent: Red
CP_GREEN = "#00ff21"        # Accent: Green
CP_ORANGE = "#ff934b"       # Accent: Orange
CP_DIM = "#3a3a3a"          # Dimmed/Borders/Inactive
CP_TEXT = "#E0E0E0"         # Primary Text
CP_SUBTEXT = "#808080"      # Secondary Text

# Ensure relative paths for resources
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "editor_chooser.json")

def load_config():
    """Load editor configuration from JSON"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
    
    # Fallback if JSON is missing or broken
    return {
        "editors": [
            {"name": "NVIM", "color": CP_GREEN},
            {"name": "EDIT", "color": CP_CYAN},
            {"name": "Notepad++", "color": CP_GREEN}
        ],
        "viewers": [
            {"name": "CHROME", "color": CP_YELLOW}
        ]
    }

def open_with_editor(file_paths, editor):
    """Open file(s) with selected editor"""
    editor = editor.lower()
    if editor == "nvim":
        if isinstance(file_paths, list):
            files_args = ' '.join([f'"{fp}"' for fp in file_paths])
            subprocess.run(f'start cmd /k nvim -p {files_args}', shell=True)
        else:
            subprocess.run(['start', 'cmd', '/k', 'nvim', file_paths], shell=True)
    elif editor == "edit":
        if isinstance(file_paths, list):
            files_args = ' '.join([f'"{fp}"' for fp in file_paths])
            subprocess.run(f'start cmd /k edit {files_args}', shell=True)
        else:
            subprocess.run(['start', 'cmd', '/k', 'edit', file_paths], shell=True)
    elif editor == "notepad++":
        npp_path = "notepad++"
        possible_paths = [
            os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "Notepad++", "notepad++.exe"),
            os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "Notepad++", "notepad++.exe")
        ]
        for p in possible_paths:
            if os.path.exists(p):
                npp_path = f'"{p}"'
                break
                
        if isinstance(file_paths, list):
            for file_path in file_paths:
                subprocess.run(f'start "" {npp_path} "{file_path}"', shell=True)
        else:
            subprocess.run(f'start "" {npp_path} "{file_paths}"', shell=True)
    elif editor == "notepads":
        if isinstance(file_paths, list):
            for file_path in file_paths:
                subprocess.run(f'notepads "{file_path}"', shell=True)
        else:
            subprocess.run(f'notepads "{file_paths}"', shell=True)
    elif editor == "vscode":
        if isinstance(file_paths, list):
            for file_path in file_paths:
                subprocess.run(f'code "{file_path}"', shell=True)
        else:
            subprocess.run(f'code "{file_paths}"', shell=True)
    elif editor == "zed":
        if isinstance(file_paths, list):
            for file_path in file_paths:
                subprocess.run(f'zed "{file_path}"', shell=True)
        else:
            subprocess.run(f'zed "{file_paths}"', shell=True)
    elif editor == "antigravity":
        if isinstance(file_paths, list):
            for file_path in file_paths:
                subprocess.run(f'antigravity "{file_path}"', shell=True)
        else:
            subprocess.run(f'antigravity "{file_paths}"', shell=True)
    elif editor == "antigravity dir":
        if not isinstance(file_paths, list):
            file_paths = [file_paths]
        dirs_to_open = set()
        for fp in file_paths:
            if os.path.isfile(fp):
                dirs_to_open.add(os.path.dirname(fp))
            elif os.path.isdir(fp):
                dirs_to_open.add(fp)
        for d in dirs_to_open:
            subprocess.run(f'antigravity "{d}"', shell=True)
    elif editor == "chrome":
        if isinstance(file_paths, list):
            for file_path in file_paths:
                subprocess.run(f'start chrome "{file_path}"', shell=True)
        else:
            subprocess.run(f'start chrome "{file_paths}"', shell=True)
    elif editor == "photos":
        if isinstance(file_paths, list):
            for file_path in file_paths:
                subprocess.run(f'start ms-photos:viewer?fileName="{file_path}"', shell=True)
        else:
            subprocess.run(f'start ms-photos:viewer?fileName="{file_paths}"', shell=True)
    elif editor == "emacs":
        env = os.environ.copy()
        if 'APPDATA' in env:
             env['HOME'] = env['APPDATA']
        elif 'HOME' not in env:
             env['HOME'] = env['USERPROFILE']
        
        if isinstance(file_paths, list):
            files_args = ' '.join([f'"{fp}"' for fp in file_paths])
            subprocess.run(f'runemacs {files_args}', shell=True, env=env)
        else:
            subprocess.run(f'runemacs "{file_paths}"', shell=True, env=env)

class CyberButton(QPushButton):
    def __init__(self, text, bg_color, text_color=CP_BG, hover_bg=CP_BG, hover_text=None, border_color=CP_DIM):
        super().__init__(text)
        if hover_text is None:
            hover_text = bg_color
            
        style = f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {border_color};
                padding: 10px;
                font-family: 'Consolas';
                font-weight: bold;
                font-size: 11pt;
                border-radius: 0px;
                outline: none;
            }}
            QPushButton:hover {{
                background-color: {hover_bg};
                color: {hover_text};
                border: 1px solid {hover_text};
            }}
            QPushButton:focus {{
                background-color: {hover_bg};
                color: {hover_text};
                border: 2px solid {CP_YELLOW};
                padding: 9px;
            }}
            QPushButton:pressed {{
                background-color: {CP_TEXT};
                color: {CP_BG};
            }}
        """
        self.setStyleSheet(style)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def keyPressEvent(self, event):
        # Ignore arrow keys so they propagate to the parent EditorChooser
        if event.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Left, Qt.Key.Key_Right):
            event.ignore()
        else:
            super().keyPressEvent(event)

class EditorChooser(QWidget):
    def __init__(self, file_paths):
        super().__init__()
        self.file_paths = file_paths
        self.buttons = []
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.init_ui()
        self.center_window()
        
        # Focus the first button by default
        if self.buttons:
            self.buttons[0].setFocus()
        
    def init_ui(self):
        # Main Border Frame
        self.main_frame = QFrame(self)
        self.main_frame.setObjectName("MainFrame")
        self.main_frame.setStyleSheet(f"""
            #MainFrame {{
                background-color: {CP_BG};
                border: 2px solid {CP_CYAN};
            }}
            QLabel {{
                color: {CP_TEXT};
                font-family: 'Consolas';
            }}
        """)
        
        layout = QVBoxLayout(self.main_frame)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with Restart and Close
        header_layout = QHBoxLayout()
        
        file_count = len(self.file_paths)
        title_text = f"// CHOOSE ACTION [{file_count} FILE{'S' if file_count > 1 else ''}]"
        title_label = QLabel(title_text)
        title_label.setStyleSheet(f"color: {CP_CYAN}; font-weight: bold; font-size: 12pt;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Restart Button
        restart_btn = QPushButton("RESTART")
        restart_btn.setFixedWidth(80)
        restart_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        restart_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        restart_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {CP_ORANGE};
                border: 1px solid {CP_ORANGE};
                font-family: 'Consolas';
                font-size: 8pt;
                padding: 2px;
            }}
            QPushButton:hover {{
                background-color: {CP_ORANGE};
                color: {CP_BG};
            }}
        """)
        restart_btn.clicked.connect(self.restart_script)
        header_layout.addWidget(restart_btn)
        
        # Close Button
        close_btn = QPushButton("X")
        close_btn.setFixedWidth(30)
        close_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {CP_RED};
                border: 1px solid {CP_RED};
                font-family: 'Consolas';
                font-weight: bold;
                padding: 2px;
            }}
            QPushButton:hover {{
                background-color: {CP_RED};
                color: {CP_BG};
            }}
        """)
        close_btn.clicked.connect(self.close)
        header_layout.addWidget(close_btn)
        
        layout.addLayout(header_layout)
        
        # Editor Section
        layout.addWidget(QLabel(">> EDITORS"))
        
        config = load_config()
        editors_data = config.get("editors", [])
        self.num_editors = len(editors_data)
        
        editors_grid = QGridLayout()
        editors_grid.setSpacing(10)
        
        row, col = 0, 0
        max_cols = 3
        for item in editors_data:
            name = item.get("name", "Unknown")
            color = item.get("color", CP_CYAN)
            btn = CyberButton(name.upper(), color)
            btn.clicked.connect(lambda checked, n=name: self.handle_action(n))
            editors_grid.addWidget(btn, row, col)
            self.buttons.append(btn)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        layout.addLayout(editors_grid)
        
        # Viewer Section
        layout.addSpacing(10)
        layout.addWidget(QLabel(">> VIEWERS"))
        
        viewers_grid = QHBoxLayout()
        viewers_grid.setSpacing(10)
        
        for item in config.get("viewers", []):
            name = item.get("name", "Unknown")
            color = item.get("color", CP_CYAN)
            btn = CyberButton(name.upper(), color)
            btn.clicked.connect(lambda checked, n=name: self.handle_action(n))
            viewers_grid.addWidget(btn)
            self.buttons.append(btn)
        
        layout.addLayout(viewers_grid)
        
        # Status Bar
        layout.addStretch()
        status_label = QLabel("SYSTEM READY...")
        status_label.setStyleSheet(f"color: {CP_DIM}; font-size: 8pt;")
        layout.addWidget(status_label)
        
        # Main layout for the widget to hold the frame
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(self.main_frame)
        
    def center_window(self):
        self.adjustSize()
        screen = QApplication.primaryScreen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
        
    def handle_action(self, editor_name):
        open_with_editor(self.file_paths, editor_name)
        self.close()
        
    def restart_script(self):
        """Restart the current script"""
        os.execl(sys.executable, sys.executable, *sys.argv)

    def keyPressEvent(self, event):
        current_widget = self.focusWidget()
        if current_widget not in self.buttons:
            super().keyPressEvent(event)
            return
            
        idx = self.buttons.index(current_widget)
        grid_width = 3
        target_idx = idx
        
        if event.key() == Qt.Key.Key_Right:
            if idx + 1 < len(self.buttons):
                target_idx = idx + 1
        elif event.key() == Qt.Key.Key_Left:
            if idx - 1 >= 0:
                target_idx = idx - 1
        elif event.key() == Qt.Key.Key_Down:
            if idx < self.num_editors:
                # Inside or moving out of editor grid
                if idx + grid_width < self.num_editors:
                    target_idx = idx + grid_width
                else:
                    # Move to viewers row
                    viewer_start = self.num_editors
                    # Try to align with column or pick first viewer
                    col = idx % grid_width
                    target_idx = min(viewer_start + col, len(self.buttons) - 1)
        elif event.key() == Qt.Key.Key_Up:
            if idx >= self.num_editors:
                # In viewers, move to last row of editors
                viewer_idx = idx - self.num_editors
                last_row_start = ( (self.num_editors - 1) // grid_width ) * grid_width
                target_idx = min(last_row_start + viewer_idx, self.num_editors - 1)
            elif idx >= grid_width:
                # Inside editor grid, move up one row
                target_idx = idx - grid_width
        elif event.key() == Qt.Key.Key_Escape:
            self.close()
            return
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            current_widget.click()
            return

        if target_idx != idx:
            self.buttons[target_idx].setFocus()
        else:
            # Handle cases where we are at boundaries
            super().keyPressEvent(event)

    def changeEvent(self, event):
        if event.type() == event.Type.ActivationChange:
            if not self.isActiveWindow():
                self.close()
        super().changeEvent(event)

    def focusOutEvent(self, event):
        self.close()
        super().focusOutEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Global Font
    font = QFont("Consolas", 10)
    app.setFont(font)
    
    if len(sys.argv) > 1:
        file_paths = sys.argv[1:]
        window = EditorChooser(file_paths)
        window.show()
        window.activateWindow()
        window.raise_()
        sys.exit(app.exec())
    else:
        print("Usage: python editor_chooser.py <file_path> [<file_path2> ...]")