import sys
import os
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QScrollArea, 
                             QFrame)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt6.QtSvg import QSvgRenderer

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

# Simple SVG Icon String (Cyberpunk style hex/folder)
SVG_ICON = """
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M22 19V9C22 7.89543 21.1046 7 20 7H11L9 5H4C2.89543 5 2 5.89543 2 7V19C2 20.1046 2.89543 21 4 21H20C21.1046 21 22 20.1046 22 19Z" stroke="#00F0FF" stroke-width="2"/>
<path d="M7 13L10 16L17 9" stroke="#FCEE0A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
"""

class PathItem(QFrame):
    def __init__(self, path, on_click):
        super().__init__()
        self.path = path
        self.on_click = on_click
        
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {CP_PANEL};
                border: 1px solid {CP_DIM};
                border-radius: 0px;
                margin: 2px;
            }}
            QFrame:hover {{
                border-color: {CP_CYAN};
                background-color: #1a1a1a;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Path Label
        self.label = QLabel(path)
        self.label.setStyleSheet(f"color: {CP_TEXT}; font-family: 'Consolas'; font-size: 11pt; border: none; background: transparent;")
        self.label.setWordWrap(True)
        layout.addWidget(self.label, stretch=1)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.on_click(self.path)

class ExplorerManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EXPLORER // MANAGER")
        self.resize(700, 500)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        
        # For window dragging
        self.dragPos = QPoint()
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {CP_BG};
                border: 2px solid {CP_CYAN};
            }}
            QWidget {{
                color: {CP_TEXT};
                font-family: 'Consolas';
                border-radius: 0px;
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
        
        # Header (Draggable Area)
        self.header = QWidget()
        self.header.setFixedHeight(40)
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # SVG Icon
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(24, 24)
        renderer = QSvgRenderer(SVG_ICON.encode('utf-8'))
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        self.icon_label.setPixmap(pixmap)
        header_layout.addWidget(self.icon_label)
        
        title = QLabel("SYSTEM // OPEN EXPLORERS")
        title.setStyleSheet(f"color: {CP_CYAN}; font-size: 14pt; font-weight: bold; letter-spacing: 2px; margin-left: 10px;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Minimize Button
        self.min_btn = QPushButton("—")
        self.min_btn.setFixedSize(30, 30)
        self.min_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {CP_YELLOW};
                font-weight: bold;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {CP_DIM};
            }}
        """)
        self.min_btn.clicked.connect(self.showMinimized)
        header_layout.addWidget(self.min_btn)
        
        # Close Button
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {CP_RED};
                font-size: 14pt;
                font-weight: bold;
                border: none;
            }}
            QPushButton:hover {{
                color: white;
                background-color: {CP_RED};
            }}
        """)
        self.close_btn.clicked.connect(self.close)
        header_layout.addWidget(self.close_btn)
        
        self.layout.addWidget(self.header)
        
        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"background-color: {CP_CYAN}; max-height: 2px; margin-bottom: 10px; border: none;")
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
                border-radius: 0px;
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

    # Window Dragging Methods
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Check what widget was clicked
            widget = self.childAt(event.position().toPoint())
            
            # Determine if the click is in a draggable area:
            # 1. Clicking the window background (widget is None or central widget)
            # 2. Clicking the header area (excluding buttons)
            
            is_interactive = False
            curr = widget
            while curr:
                if isinstance(curr, (PathItem, QPushButton)):
                    is_interactive = True
                    break
                curr = curr.parentWidget()
            
            if not is_interactive:
                self.dragPos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
            else:
                # Let the interactive widget handle the event
                super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and not self.dragPos.isNull():
            self.move(event.globalPosition().toPoint() - self.dragPos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.dragPos = QPoint()
        super().mouseReleaseEvent(event)

    def get_explorer_paths(self):
        ps_script = '(New-Object -ComObject Shell.Application).Windows() | ForEach-Object { try { $_.Document.Folder.Self.Path } catch { $_.LocationURL } }'
        try:
            result = subprocess.run(['powershell', '-Command', ps_script], 
                                     capture_output=True, text=True, check=True,
                                     creationflags=subprocess.CREATE_NO_WINDOW)
            paths = [line.strip() for line in result.stdout.splitlines() if line.strip()]
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
        """Uses PowerShell to close all open Explorer windows aggressively."""
        ps_script = """
        $shell = New-Object -ComObject Shell.Application;
        # Multi-pass attempt to ensure all windows close
        for($i=0; $i -lt 2; $i++) {
            $windows = @($shell.Windows());
            foreach($w in $windows) {
                if ($w.Name -match "Explorer") {
                    try { $w.Quit() } catch {}
                }
            }
            if ($i -lt 1) { Start-Sleep -m 200 }
        }
        """
        try:
            subprocess.run(['powershell', '-Command', ps_script], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
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
            self.status_lbl.setText(f"Opened: {os.path.basename(path) if path != 'This PC' else path}")
        except Exception as e:
            self.status_lbl.setText(f"Error: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExplorerManager()
    window.show()
    sys.exit(app.exec())
