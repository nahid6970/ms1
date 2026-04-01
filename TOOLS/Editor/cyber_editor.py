import sys
import os
import json
import subprocess
import ctypes
import tempfile
from datetime import datetime

# --- PyQt6 Imports ---
try:
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                                 QPlainTextEdit, QLabel, QPushButton, QFileDialog, QDialog,
                                 QFormLayout, QLineEdit, QComboBox, QStatusBar, QMessageBox,
                                 QFrame, QSplitter, QTextEdit)
    from PyQt6.QtCore import Qt, QRect, QSize, pyqtSignal, QTimer
    from PyQt6.QtGui import (QPainter, QTextFormat, QColor, QFont, QAction, QIcon,
                             QTextCursor, QKeySequence, QPalette)
except ImportError:
    print("PyQt6 is required. Please install it using 'pip install PyQt6'")
    sys.exit(1)

# --- THEME CONSTANTS (From THEME_GUIDE.md) ---
CP_BG = "#050505"           # Main Background
CP_PANEL = "#111111"        # Input background
CP_YELLOW = "#FCEE0A"       # Accent Yellow
CP_CYAN = "#00F0FF"         # Accent Cyan
CP_RED = "#FF003C"          # Accent Red
CP_GREEN = "#00ff21"        # Accent Green
CP_DIM = "#3a3a3a"          # Borders/Dimmed text
CP_TEXT = "#E0E0E0"         # Primary Text
CP_SUBTEXT = "#808080"      # Secondary Text

THEMES = {
    "CyberYellow": {"accent": CP_YELLOW, "name": "Cyber Yellow"},
    "CyberCyan":   {"accent": CP_CYAN,   "name": "Cyber Cyan"},
    "CyberRed":    {"accent": CP_RED,    "name": "Cyber Red"}
}

# --- Settings Manager ---
class SettingsManager:
    def __init__(self):
        # Use relative paths for settings in the same folder
        self.filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "editor_settings.json")
        self.settings = {
            "width": 1000,
            "height": 700,
            "theme": "CyberYellow",
            "font_size": 10,
            "last_file": ""
        }
        self.load()

    def load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    self.settings.update(data)
            except Exception as e:
                print(f"Error loading settings: {e}")

    def save(self):
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

# --- UI Components ---

class CyberButton(QPushButton):
    """Premium Styled Button as per GUIDE"""
    def __init__(self, text, accent=CP_YELLOW, parent=None):
        super().__init__(text, parent)
        self.accent = accent
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.apply_style()

    def set_accent(self, accent):
        self.accent = accent
        self.apply_style()

    def apply_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {CP_PANEL};
                color: {CP_TEXT};
                border: 1px solid {CP_DIM};
                font-family: 'Consolas';
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 0px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: #1a1a1a;
                border: 1px solid {self.accent};
                color: {self.accent};
            }}
            QPushButton:pressed {{
                background-color: {self.accent};
                color: black;
            }}
        """)

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)

class CodeEditor(QPlainTextEdit):
    """Enhanced Editor with Line Numbers and Highlighting"""
    def __init__(self, accent=CP_YELLOW):
        super().__init__()
        self.accent = accent
        self.line_number_area = LineNumberArea(self)

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        self.set_accent(accent)
        self.update_line_number_area_width(0)
        self.highlight_current_line()

        self.setFont(QFont('Consolas', 10))
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        
    def set_accent(self, accent):
        self.accent = accent
        # Syncing Line Color
        self.highlight_current_line()

    def line_number_area_width(self):
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        return 10 + self.fontMetrics().horizontalAdvance('9') * digits

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(CP_PANEL))

        block = self.firstVisibleBlock()
        block_num = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_num + 1)
                is_current = (block_num == self.textCursor().blockNumber())
                painter.setPen(QColor(self.accent if is_current else CP_DIM))
                
                # Highlight bg slightly for current line number
                if is_current:
                    f = painter.font()
                    f.setBold(True)
                    painter.setFont(f)
                else:
                    f = painter.font()
                    f.setBold(False)
                    painter.setFont(f)

                painter.drawText(0, int(top), self.line_number_area.width() - 5, 
                                 self.fontMetrics().height(), Qt.AlignmentFlag.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_num += 1

    def highlight_current_line(self):
        extra_selections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor(self.accent)
            line_color.setAlpha(25)
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        self.setExtraSelections(extra_selections)
        self.line_number_area.update()

# --- Main App ---

class SettingsDialog(QDialog):
    def __init__(self, parent, mgr):
        super().__init__(parent)
        self.mgr = mgr
        self.setWindowTitle("SYSTEM_SETTINGS")
        self.setModal(True)
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        self.w_edit = QLineEdit(str(self.mgr.settings["width"]))
        self.h_edit = QLineEdit(str(self.mgr.settings["height"]))
        
        self.theme_sel = QComboBox()
        for t_id, t_info in THEMES.items():
            self.theme_sel.addItem(t_info["name"], t_id)
        
        idx = self.theme_sel.findData(self.mgr.settings["theme"])
        self.theme_sel.setCurrentIndex(max(0, idx))
        
        form.addRow("UI_WIDTH:", self.w_edit)
        form.addRow("UI_HEIGHT:", self.h_edit)
        form.addRow("COLOR_THEME:", self.theme_sel)
        
        layout.addLayout(form)
        
        # Add space for more features later as requested
        self.more_box = QFrame()
        self.more_box.setFrameShape(QFrame.Shape.StyledPanel)
        more_layout = QVBoxLayout(self.more_box)
        more_layout.addWidget(QLabel("// Reserved for future modules..."))
        layout.addWidget(self.more_box)

        btns = QHBoxLayout()
        self.save_btn = CyberButton("APPLY & SAVE", accent=THEMES[self.mgr.settings["theme"]]["accent"])
        self.save_btn.clicked.connect(self.do_save)
        self.cancel_btn = CyberButton("ABORT", accent=CP_RED)
        self.cancel_btn.clicked.connect(self.reject)
        
        btns.addWidget(self.save_btn)
        btns.addWidget(self.cancel_btn)
        layout.addLayout(btns)

    def apply_theme(self):
        accent = THEMES[self.mgr.settings["theme"]]["accent"]
        self.setStyleSheet(f"""
            QDialog {{ background-color: {CP_BG}; border: 2px solid {accent}; }}
            QLabel {{ color: {CP_TEXT}; font-family: 'Consolas'; font-weight: bold; text-transform: uppercase; }}
            QLineEdit, QComboBox {{
                background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 6px;
                font-family: 'Consolas'; font-size: 11pt;
            }}
            QLineEdit:focus {{ border: 1px solid {accent}; }}
            QComboBox QAbstractItemView {{
                background-color: {CP_PANEL}; color: {CP_TEXT}; selection-background-color: {accent}; selection-color: black;
            }}
            QFrame {{ border: 1px dashed {CP_DIM}; margin: 10px 0; }}
        """)

    def do_save(self):
        try:
            self.mgr.settings["width"] = int(self.w_edit.text())
            self.mgr.settings["height"] = int(self.h_edit.text())
            self.mgr.settings["theme"] = self.theme_sel.currentData()
            self.mgr.save()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "SYSTEM_ERR", f"INVALID INPUT: {e}")

class MainWindow(QMainWindow):
    def __init__(self, initial_file=None, buffer_file=None):
        super().__init__()
        self.mgr = SettingsManager()
        self.current_file = initial_file
        self.is_admin = self.check_admin()
        
        self.setup_ui()
        self.apply_theme_global()
        
        # Load Content
        if initial_file:
            self.load_file(initial_file)
            if buffer_file and os.path.exists(buffer_file):
                try:
                    with open(buffer_file, 'r', encoding='utf-8') as f:
                        self.editor.setPlainText(f.read())
                    os.remove(buffer_file)
                    self.statusBar().showMessage(f"STATUS: RECOVERED_BUFFER_LOADED [{datetime.now().strftime('%H:%M:%S')}]")
                except: pass

    def check_admin(self):
        try: return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except: return False

    def setup_ui(self):
        self.setWindowTitle(f"CYBER_EDITOR // {'[SUPERUSER]' if self.is_admin else '[USER]'}")
        self.resize(self.mgr.settings["width"], self.mgr.settings["height"])
        
        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QVBoxLayout(central)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        # Nav Bar
        self.nav_layout = QHBoxLayout()
        
        self.btn_open = CyberButton("OPEN_FILE")
        self.btn_save = CyberButton("SAVE_CACHE")
        self.btn_restart = CyberButton("RELOAD_APP")
        self.btn_settings = CyberButton("SYSTEM_CFG")
        
        self.btn_open.clicked.connect(self.on_open)
        self.btn_save.clicked.connect(self.on_save)
        self.btn_restart.clicked.connect(self.on_restart)
        self.btn_settings.clicked.connect(self.on_settings)
        
        self.nav_layout.addWidget(self.btn_open)
        self.nav_layout.addWidget(self.btn_save)
        self.nav_layout.addStretch()
        
        if not self.is_admin:
            self.btn_admin = CyberButton("ELEVATE_ACCESS", accent=CP_RED)
            self.btn_admin.clicked.connect(self.on_elevate)
            self.nav_layout.addWidget(self.btn_admin)
            
        self.nav_layout.addWidget(self.btn_restart)
        self.nav_layout.addWidget(self.btn_settings)
        
        self.main_layout.addLayout(self.nav_layout)
        
        # Editor
        self.editor = CodeEditor()
        self.main_layout.addWidget(self.editor)
        
        # Status Bar
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("SYSTEM READY...")

    def apply_theme_global(self):
        theme_key = self.mgr.settings["theme"]
        accent = THEMES[theme_key]["accent"]
        
        # Update Editor
        self.editor.set_accent(accent)
        
        # Update Nav Buttons
        self.btn_open.set_accent(accent)
        self.btn_save.set_accent(accent)
        self.btn_restart.set_accent(accent)
        self.btn_settings.set_accent(accent)
        if not self.is_admin: self.btn_admin.set_accent(CP_RED)

        # Main Stylesheet
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            
            QPlainTextEdit {{
                background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 8px;
                selection-background-color: {accent}; selection-color: black;
                font-family: 'Consolas'; font-size: 11pt;
            }}
            QPlainTextEdit:focus {{ border: 1px solid {accent}; }}
            
            QStatusBar {{ background: {CP_PANEL}; color: {CP_SUBTEXT}; border-top: 1px solid {CP_DIM}; font-size: 9pt; }}
        """)

    def on_open(self):
        path, _ = QFileDialog.getOpenFileName(self, "SYSTEM_LINK_FILE", "", "All Files (*)")
        if path: self.load_file(path)

    def load_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.editor.setPlainText(f.read())
            self.current_file = path
            self.setWindowTitle(f"CYBER_EDITOR // {os.path.basename(path)} // {'[ROOT]' if self.is_admin else '[USER]'}")
            self.statusBar().showMessage(f"STATUS: FILE_CONNECTED [{path}]")
        except Exception as e:
            QMessageBox.critical(self, "LINK_ERR", f"COULD NOT READ: {e}")

    def on_save(self):
        if not self.current_file:
            path, _ = QFileDialog.getSaveFileName(self, "ESTABLISH_PERSISTENCE", "", "All Files (*)")
            if not path: return
            self.current_file = path
            
        try:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            self.statusBar().showMessage(f"STATUS: DATA_STREAMS_SYNCED // {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            QMessageBox.warning(self, "SYNC_ERR", f"PERMISSION DENIED: {e}\nTRY ELEVATING ACCESS.")

    def on_restart(self):
        QApplication.quit()
        subprocess.Popen([sys.executable] + sys.argv)

    def on_settings(self):
        dlg = SettingsDialog(self, self.mgr)
        if dlg.exec():
            self.apply_theme_global()
            self.resize(self.mgr.settings["width"], self.mgr.settings["height"])

    def on_elevate(self):
        # Save state to buffer
        buf_path = os.path.join(tempfile.gettempdir(), "cyber_edit_lock.tmp")
        try:
            with open(buf_path, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            
            script = os.path.abspath(sys.argv[0])
            params = f'"{script}"'
            if self.current_file:
                params += f' --file "{self.current_file}"'
            params += f' --buffer "{buf_path}"'
            
            # Execute with 'runas'
            ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
            if ret > 32: QApplication.quit()
            else: QMessageBox.warning(self, "AUTH_ERR", "ELEVATION_FAILED: ACCESS_DENIED")
        except Exception as e:
            QMessageBox.critical(self, "INTERNAL_ERR", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Arg parsing
    initial_file = None
    buffer_file = None
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--file" and i + 1 < len(args):
            initial_file = args[i+1]; i += 2
        elif args[i] == "--buffer" and i + 1 < len(args):
            buffer_file = args[i+1]; i += 2
        else:
            if not initial_file: initial_file = args[i]
            i += 1

    window = MainWindow(initial_file, buffer_file)
    window.show()
    sys.exit(app.exec())
