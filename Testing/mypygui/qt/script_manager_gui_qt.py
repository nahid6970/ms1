import sys
import os
import json
import subprocess
import shutil
import shlex
from functools import partial
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QScrollArea, 
                             QFrame, QMessageBox, QGridLayout, QSizePolicy)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QFont, QCursor, QColor, QDesktopServices, QAction
from PyQt6.QtCore import QUrl

# -----------------------------------------------------------------------------
# CYBERPUNK THEME PALETTE (From startup.py)
# -----------------------------------------------------------------------------
CP_BG = "#050505"           # Main Background (almost black)
CP_PANEL = "#111111"        # Panel Background
CP_YELLOW = "#FCEE0A"       # Cyber Yellow (Primary Accent)
CP_CYAN = "#00F0FF"         # Neon Cyan (Secondary Accent)
CP_RED = "#FF003C"          # Neon Red (Error/Delete)
CP_DIM = "#3a3a3a"          # Dimmed/Inactive
CP_TEXT = "#E0E0E0"         # Main Text
CP_SUBTEXT = "#808080"      # Sub Text

# Config Path
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "script_launcher_config.json")

# -----------------------------------------------------------------------------
# UI COMPONENTS
# -----------------------------------------------------------------------------

class CyberButton(QPushButton):
    """
    A Cyberpunk-styled button that matches the design in startup.py.
    """
    def __init__(self, text, parent=None, color=CP_YELLOW, is_outlined=False, font_size=10, is_folder=False):
        super().__init__(text, parent)
        self.color = color
        self.is_outlined = is_outlined
        self.is_folder = is_folder
        self.setFont(QFont("Consolas", font_size, QFont.Weight.Bold))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.setMinimumHeight(45) # Match approx height from tk config
        self.update_style()

    def update_style(self):
        # Folder styling distinction
        if self.is_folder:
            base_bg = CP_PANEL
            border_col = self.color
        else:
            base_bg = CP_BG if self.is_outlined else self.color
            border_col = self.color

        if self.is_outlined:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {self.color};
                    border: 2px solid {self.color};
                    padding: 5px 15px;
                    font-family: 'Consolas';
                    border-radius: 0px;
                }}
                QPushButton:hover {{
                    background-color: {self.color};
                    color: {CP_BG};
                }}
            """)
        else:
            # Solid style
            fg_color = CP_BG
            bg_color = self.color
            
            # Special case for folder-like "block" look
            if self.is_folder:
                fg_color = self.color
                bg_color = CP_PANEL
                
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg_color};
                    color: {fg_color};
                    border: { "1px solid " + self.color if self.is_folder else "none"};
                    padding: 5px 15px;
                    font-family: 'Consolas';
                    border-radius: 0px;
                }}
                QPushButton:hover {{
                    background-color: {CP_BG};
                    color: {self.color};
                    border: 1px solid {self.color};
                }}
            """)

# -----------------------------------------------------------------------------
# LOGIC & MAIN WINDOW
# -----------------------------------------------------------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SCRIPT // MANAGER_V2.0_QT")
        self.resize(1000, 700)
        self.setStyleSheet(f"QMainWindow {{ background-color: {CP_BG}; }}")
        
        self.config = {}
        self.view_stack = [] # For folder navigation
        
        self.load_config()
        self.setup_ui()
        self.refresh_grid()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding='utf-8') as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                self.config = {"scripts": []}
        else:
            self.config = {"scripts": []}

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main Layout
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)

        # --- HEADER ---
        header_layout = QHBoxLayout()
        self.title_lbl = QLabel("SCRIPT // MANAGER")
        self.title_lbl.setFont(QFont("Consolas", 16, QFont.Weight.Bold))
        self.title_lbl.setStyleSheet(f"color: {CP_YELLOW}; letter-spacing: 2px;")
        
        self.back_btn = CyberButton("<< BACK", color=CP_RED, is_outlined=True)
        self.back_btn.setFixedWidth(100)
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.setVisible(False)

        header_layout.addWidget(self.back_btn)
        header_layout.addWidget(self.title_lbl)
        header_layout.addStretch()
        
        # Reload Button
        reload_btn = CyberButton("RELOAD", color=CP_CYAN, is_outlined=True)
        reload_btn.setFixedWidth(100)
        reload_btn.clicked.connect(self.reload_config)
        header_layout.addWidget(reload_btn)

        self.main_layout.addLayout(header_layout)

        # --- GRID AREA ---
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{ background: transparent; border: none; }}
            QWidget {{ background: transparent; }}
            QScrollBar:vertical {{ background: {CP_BG}; width: 8px; }}
            QScrollBar::handle:vertical {{ background: {CP_DIM}; }}
        """)

        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(15)
        self.grid_layout.setContentsMargins(0, 0, 10, 0) # Right margin for scrollbar
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll_area.setWidget(self.grid_container)
        self.main_layout.addWidget(scroll_area)

    def reload_config(self):
        self.load_config()
        self.refresh_grid()
        self.update_status("SYSTEM RELOADED")

    def refresh_grid(self):
        # Clear existing items
        for i in reversed(range(self.grid_layout.count())): 
            self.grid_layout.itemAt(i).widget().setParent(None)

        # Determine current scripts to show
        if self.view_stack:
            current_folder = self.view_stack[-1]
            scripts = current_folder.get("scripts", [])
            title = f"SCRIPT // MANAGER // {current_folder.get('name', 'UNKNOWN').upper()}"
            self.back_btn.setVisible(True)
        else:
            scripts = self.config.get("scripts", [])
            title = "SCRIPT // MANAGER // ROOT"
            self.back_btn.setVisible(False)
        
        self.title_lbl.setText(title)

        # Populate Grid
        columns = 4 # Default columns
        
        row, col = 0, 0
        for script in scripts:
            name = script.get("name", "Unnamed")
            s_type = script.get("type", "script")
            
            # Determine Color based on config or default
            color = CP_YELLOW
            if s_type == "folder":
                color = CP_CYAN
            elif "color" in script:
                # Basic hex check
                c = script["color"]
                if c.startswith("#"): color = c
            
            # Create Button
            btn = CyberButton(name, color=color, is_outlined=True, is_folder=(s_type=="folder"))
            
            # Tooltip
            tooltip = ""
            if s_type == "folder":
                tooltip = f"Folder: {len(script.get('scripts', []))} items"
            else:
                path = script.get("path", "")
                tooltip = f"Path: {path}"
            btn.setToolTip(tooltip)

            # Click Handler
            # We use partial to capture the specific script dict
            btn.clicked.connect(partial(self.handle_click, script))

            # Add to Grid
            # Handle Col Span (basic implementation)
            colspan = script.get("col_span", 1)
            rowspan = script.get("row_span", 1)
            
            # Find next available cell (Basic implementation assumes sequential fill)
            # A true grid packing algorithm is complex, we'll stick to simple flow for now
            # If col + colspan > columns, move to next row
            if col + colspan > columns:
                row += 1
                col = 0
            
            self.grid_layout.addWidget(btn, row, col, rowspan, colspan)
            
            col += colspan
            if col >= columns:
                row += 1
                col = 0

    def handle_click(self, script):
        s_type = script.get("type", "script")
        if s_type == "folder":
            self.view_stack.append(script)
            self.refresh_grid()
        else:
            self.launch_script(script)

    def go_back(self):
        if self.view_stack:
            self.view_stack.pop()
            self.refresh_grid()

    def launch_script(self, script):
        name = script.get("name", "Unknown")
        path = script.get("path", "")
        hide = script.get("hide_terminal", False)
        
        if not path:
            self.update_status(f"ERROR: No path for {name}")
            return

        # Expand vars
        path = os.path.expandvars(path)
        
        if not os.path.exists(path) and not any(path.endswith(ext) for ext in [".exe", ".cmd", ".bat"]):
             # Check if it's a command on PATH
             if not shutil.which(path):
                 self.update_status(f"ERROR: File not found: {path}", is_error=True)
                 # Try running anyway in case it's a system command not on path (rare) or alias
                 # return

        try:
            cwd = os.path.dirname(path) if os.path.isfile(path) else None
            
            if path.endswith(".py"):
                exe = "pythonw" if hide else "python"
                # Use current python env logic
                python_path = sys.executable
                if hide:
                    python_path = python_path.replace("python.exe", "pythonw.exe")
                
                subprocess.Popen([python_path, path], cwd=cwd)
                
            elif path.endswith(".ps1"):
                # PowerShell
                ps_exe = "pwsh" if shutil.which("pwsh") else "powershell"
                cmd = [ps_exe, "-ExecutionPolicy", "Bypass", "-File", path]
                if hide:
                    cmd = [ps_exe, "-WindowStyle", "Hidden", "-ExecutionPolicy", "Bypass", "-File", path]
                subprocess.Popen(cmd, cwd=cwd)
                
            else:
                # Standard Executable
                if hide:
                    # Use START /B or similar? Or creation flags
                    # subprocess.CREATE_NO_WINDOW = 0x08000000
                    subprocess.Popen(path, cwd=cwd, creationflags=0x08000000, shell=True)
                else:
                     subprocess.Popen(path, cwd=cwd, shell=True)

            self.update_status(f"LAUNCHED: {name}")

        except Exception as e:
            self.update_status(f"FAILED: {e}", is_error=True)
            print(e)

    def update_status(self, text, is_error=False):
        # Simply print to console for now or show message box if critical
        print(f"STATUS: {text}")
        if is_error:
            QMessageBox.warning(self, "Execution Error", text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Generic Font
    app.setFont(QFont("Consolas", 10))
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
