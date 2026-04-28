import sys
import os
import json
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QLabel, QScrollArea, QFrame, QMenu, QAction, QVBoxLayout)
from PyQt5.QtCore import Qt, QSize, QPoint, QRect, QPropertyAnimation, QEasingCurve, pyqtSignal, QTimer, QMimeData, QUrl
from PyQt5.QtGui import QPainter, QPainterPath, QColor, QFont, QIcon, QBrush, QPen, QCursor, QDrag

# CYBERPUNK THEME PALETTE
CP_BG = "#050505"
CP_PANEL = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN = "#00F0FF"
CP_RED = "#FF003C"
CP_DIM = "#3a3a3a"
CP_TEXT = "#E0E0E0"
CP_SUBTEXT = "#808080"

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "md_launcher_config.json")

def load_config():
    default = {"md_folder": "C:/@delta/ms1/Testing/edu", "window_width_percent": 0.8}
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return {**default, **json.load(f)}
    except: pass
    return default

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

class MDCard(QFrame):
    clicked = pyqtSignal()
    
    def __init__(self, file_path, width=150, height=200, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.w = width
        self.h = height
        self.is_selected = False
        self.setFixedSize(self.w, self.h)
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        
        # Icon/Symbol
        self.icon_label = QLabel("📄")
        self.icon_label.setFont(QFont("Segoe UI Emoji", 40))
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("background: transparent; color: " + CP_CYAN)
        
        # Name
        self.name_label = QLabel(self.file_name)
        self.name_label.setFont(QFont("Consolas", 10, QFont.Bold))
        self.name_label.setWordWrap(True)
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setStyleSheet("background: transparent; color: " + CP_TEXT)
        
        layout.addStretch()
        layout.addWidget(self.icon_label)
        layout.addWidget(self.name_label)
        layout.addStretch()

        self.setStyleSheet(f"""
            MDCard {{
                background-color: {CP_PANEL};
                border: 1px solid {CP_DIM};
                border-radius: 10px;
            }}
            MDCard:hover {{
                border: 1px solid {CP_CYAN};
                background-color: #1a1a1a;
            }}
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_pos = event.pos()
            self.clicked.emit()

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        if (event.pos() - self.drag_start_pos).manhattanLength() < QApplication.startDragDistance():
            return

        drag = QDrag(self)
        mime_data = QMimeData()
        
        # Add file path to mime data
        url = QUrl.fromLocalFile(os.path.abspath(self.file_path))
        mime_data.setUrls([url])
        drag.setMimeData(mime_data)
        
        # Visual feedback during drag
        drag.exec_(Qt.CopyAction)

    def set_selected(self, selected):
        self.is_selected = selected
        if selected:
            self.setStyleSheet(f"MDCard {{ background-color: #222; border: 2px solid {CP_YELLOW}; border-radius: 10px; }}")
        else:
            self.setStyleSheet(f"MDCard {{ background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; border-radius: 10px; }}")

class MDLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.block_close = False
        self.cards = []
        self.current_idx = 0

        # Window Setup
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        screen = QApplication.primaryScreen().geometry()
        self.win_w = int(screen.width() * self.config.get("window_width_percent", 0.8))
        self.win_h = 280
        self.setGeometry((screen.width() - self.win_w) // 2, 10, self.win_w, self.win_h)
        
        # UI Setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #111, stop:1 #050505);
            border: 1px solid {CP_DIM};
            border-radius: 15px;
        """)
        
        self.layout_main = QVBoxLayout(self.central_widget)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("CYBER MD LAUNCHER")
        title.setFont(QFont("Consolas", 12, QFont.Bold))
        title.setStyleSheet(f"color: {CP_YELLOW}; border: none; background: transparent;")
        
        folder_label = QLabel(f"Source: {self.config['md_folder']}")
        folder_label.setFont(QFont("Consolas", 8))
        folder_label.setStyleSheet(f"color: {CP_SUBTEXT}; border: none; background: transparent;")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(folder_label)
        self.layout_main.addLayout(header_layout)

        # Scroll Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent;")
        self.scroll_layout = QHBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)
        self.scroll_layout.setSpacing(15)
        self.scroll_layout.setAlignment(Qt.AlignLeft)
        
        self.scroll.setWidget(self.scroll_content)
        self.layout_main.addWidget(self.scroll)
        
        # Footer hints
        footer = QLabel("Drag cards to other windows | [ESC] Close | [Ctrl+O] Change Folder")
        footer.setFont(QFont("Consolas", 8))
        footer.setStyleSheet(f"color: {CP_DIM}; border: none; background: transparent;")
        self.layout_main.addWidget(footer)

        self.scan_files()
        
        # Focus Timer - delayed start so window can gain focus first
        self.focus_timer = QTimer(self)
        self.focus_timer.timeout.connect(self.check_focus)
        QTimer.singleShot(500, lambda: self.focus_timer.start(100))

    def scan_files(self):
        # Clear existing
        for i in reversed(range(self.scroll_layout.count())): 
            self.scroll_layout.itemAt(i).widget().setParent(None)
        self.cards = []
        
        folder = self.config["md_folder"]
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
            
        md_files = []
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.endswith(".md"):
                    md_files.append(os.path.join(root, file))
        
        for i, path in enumerate(md_files):
            card = MDCard(path)
            card.clicked.connect(lambda idx=i: self.set_index(idx))
            self.scroll_layout.addWidget(card)
            self.cards.append(card)
            
        if self.cards:
            self.set_index(0)

    def set_index(self, idx):
        if not self.cards: return
        self.current_idx = max(0, min(idx, len(self.cards) - 1))
        for i, card in enumerate(self.cards):
            card.set_selected(i == self.current_idx)
        self.ensure_visible()

    def ensure_visible(self):
        hbar = self.scroll.horizontalScrollBar()
        item_w = 150 + 15
        target_x = self.current_idx * item_w
        
        self.anim = QPropertyAnimation(hbar, b"value")
        self.anim.setDuration(300)
        self.anim.setEndValue(target_x - 50)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.start()

    def check_focus(self):
        if self.block_close: return
        if not self.isActiveWindow():
            self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_Left:
            self.set_index(self.current_idx - 1)
        elif event.key() == Qt.Key_Right:
            self.set_index(self.current_idx + 1)
        elif event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_O:
            self.change_folder()

    def change_folder(self):
        from PyQt5.QtWidgets import QFileDialog
        self.block_close = True
        folder = QFileDialog.getExistingDirectory(self, "Select MD Folder", self.config["md_folder"])
        self.block_close = False
        if folder:
            self.config["md_folder"] = folder
            save_config(self.config)
            self.scan_files()
            self.activateWindow()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        hbar = self.scroll.horizontalScrollBar()
        hbar.setValue(hbar.value() - delta)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    launcher = MDLauncher()
    launcher.show()
    launcher.activateWindow()
    launcher.raise_()
    sys.exit(app.exec_())
