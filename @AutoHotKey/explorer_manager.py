import sys
import os
import subprocess
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QScrollArea, 
                             QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor, QIcon

# CYBERPUNK THEME PALETTE (from THEME_GUIDE.md)
CP_BG = "#050505"           # Main Background
CP_PANEL = "#111111"        # Panel Background
CP_DIM = "#3a3a3a"          # Dimmed elements
CP_TEXT = "#E0E0E0"         # Primary text
CP_SUBTEXT = "#808080"      # Secondary text
CP_YELLOW = "#FCEE0A"       # Primary accent
CP_CYAN = "#00F0FF"         # Secondary accent
CP_RED = "#FF003C"          # Error/Delete
CP_GREEN = "#00FF00"        # Success

class PathItem(QFrame):
    def __init__(self, path, on_click):
        super().__init__()
        self.path = path
        self.on_click = on_click
        
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {CP_PANEL};
                border: 1px solid {CP_DIM};
                border-radius: 4px;
                margin: 2px;
            }}
            QFrame:hover {{
                border-color: {CP_CYAN};
                background-color: #1a1a1a;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        
        # Path Label
        self.label = QLabel(path)
        self.label.setStyleSheet(f"color: {CP_TEXT}; font-family: 'Consolas'; font-size: 11pt; border: none;")
        self.label.setWordWrap(True)
        layout.addWidget(self.label, stretch=1)
        
        # Open Button
        self.open_btn = QPushButton("OPEN")
        self.open_btn.setFixedWidth(80)
        self.open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.open_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {CP_CYAN};
                color: {CP_BG};
                font-weight: bold;
                border: none;
                border-radius: 2px;
                padding: 4px;
            }}
            QPushButton:hover {{
                background-color: {CP_YELLOW};
            }}
        """)
        self.open_btn.clicked.connect(lambda: self.on_click(self.path))
        layout.addWidget(self.open_btn)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.on_click(self.path)

class ExplorerManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EXPLORER // MANAGER")
        self.resize(700, 500)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {CP_BG};
                border: 2px solid {CP_CYAN};
            }}
            QWidget {{
                color: {CP_TEXT};
                font-family: 'Consolas';
            }}
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background: {CP_BG};
                width: 10px;
            }}
            QScrollBar::handle:vertical {{
                background: {CP_DIM};
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {CP_CYAN};
            }}
        """)
        
        central = QWidget()
        self.setCentralWidget(central)
        self.layout = QVBoxLayout(central)
        self.layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("SYSTEM // OPEN EXPLORERS")
        title.setStyleSheet(f"color: {CP_CYAN}; font-size: 14pt; font-weight: bold; letter-spacing: 2px;")
        header.addWidget(title)
        header.addStretch()
        
        close_app_btn = QPushButton("✕")
        close_app_btn.setFixedSize(30, 30)
        close_app_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {CP_RED};
                font-size: 16pt;
                font-weight: bold;
                border: none;
            }}
            QPushButton:hover {{
                color: white;
                background-color: {CP_RED};
            }}
        """)
        close_app_btn.clicked.connect(self.close)
        header.addWidget(close_app_btn)
        self.layout.addLayout(header)
        
        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"background-color: {CP_CYAN}; max-height: 2px; margin-bottom: 10px;")
        self.layout.addWidget(line)
        
        # Scroll Area for paths
        self.scroll = QScrollArea()
        self.scroll_content = QWidget()
        self.paths_layout = QVBoxLayout(self.scroll_content)
        self.paths_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        self.scroll.setWidgetResizable(True)
        self.layout.addWidget(self.scroll)
        
        # Footer
        footer = QHBoxLayout()
        self.refresh_btn = QPushButton("REFRESH SCAN")
        self.refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {CP_YELLOW};
                border: 1px solid {CP_YELLOW};
                padding: 8px 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {CP_YELLOW};
                color: {CP_BG};
            }}
        """)
        self.refresh_btn.clicked.connect(self.scan_and_close)
        footer.addWidget(self.refresh_btn)
        
        footer.addStretch()
        
        self.status_lbl = QLabel("Ready")
        self.status_lbl.setStyleSheet(f"color: {CP_SUBTEXT}; font-size: 9pt;")
        footer.addWidget(self.status_lbl)
        
        self.layout.addLayout(footer)

        # Initial scan
        self.scan_and_close()

    def get_explorer_paths(self):
        """Uses PowerShell to get all open Explorer paths robustly."""
        ps_script = '(New-Object -ComObject Shell.Application).Windows() | ForEach-Object { try { $_.Document.Folder.Self.Path } catch { $_.LocationURL } }'
        try:
            result = subprocess.run(['powershell', '-Command', ps_script], 
                                     capture_output=True, text=True, check=True)
            paths = [line.strip() for line in result.stdout.splitlines() if line.strip()]
            # Filter unique paths and remove non-file paths (like "This PC" which might show up as URL)
            unique_paths = []
            for p in paths:
                if p.startswith('file:///'):
                    p = p.replace('file:///', '').replace('/', '\\')
                if p and p not in unique_paths and (os.path.exists(p) or p == "This PC"):
                    unique_paths.append(p)
            return unique_paths
        except Exception as e:
            print(f"Error getting paths: {e}")
            return []

    def close_explorer_windows(self):
        """Uses PowerShell to close all open Explorer windows."""
        ps_script = '(New-Object -ComObject Shell.Application).Windows() | ForEach-Object { if ($_.Name -eq "Windows Explorer" -or $_.Name -eq "File Explorer") { $_.Quit() } }'
        try:
            subprocess.run(['powershell', '-Command', ps_script], check=True)
        except Exception as e:
            print(f"Error closing windows: {e}")

    def scan_and_close(self):
        self.status_lbl.setText("Scanning...")
        QApplication.processEvents()
        
        paths = self.get_explorer_paths()
        if paths:
            self.close_explorer_windows()
            self.update_path_list(paths)
            self.status_lbl.setText(f"Found {len(paths)} locations.")
        else:
            self.update_path_list([])
            self.status_lbl.setText("No active explorers found.")

    def update_path_list(self, paths):
        # Clear existing
        while self.paths_layout.count():
            child = self.paths_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        if not paths:
            empty_lbl = QLabel("NO ACTIVE EXPLORER WINDOWS DETECTED")
            empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_lbl.setStyleSheet(f"color: {CP_DIM}; margin-top: 50px; font-size: 12pt;")
            self.paths_layout.addWidget(empty_lbl)
            return

        for path in paths:
            item = PathItem(path, self.open_path)
            self.paths_layout.addWidget(item)

    def open_path(self, path):
        try:
            if path == "This PC":
                subprocess.run(['explorer.exe', 'shell:MyComputerFolder'])
            else:
                os.startfile(path)
            self.close() # Close manager after opening
        except Exception as e:
            self.status_lbl.setText(f"Error: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExplorerManager()
    window.show()
    sys.exit(app.exec())
