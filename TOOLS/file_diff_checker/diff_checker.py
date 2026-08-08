import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QLineEdit, QGroupBox, QFormLayout, 
                             QFileDialog, QTextEdit, QDialog, QCheckBox)
from PyQt6.QtCore import Qt

# CYBERPUNK THEME PALETTE
CP_BG = "#050505"
CP_PANEL = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN = "#00F0FF"
CP_RED = "#FF003C"
CP_GREEN = "#00ff21"
CP_DIM = "#3a3a3a"
CP_TEXT = "#E0E0E0"

# File extensions treated as text (compared only when "text files only" is enabled)
TEXT_EXTENSIONS = {
    '.json', '.txt', '.html', '.htm', '.xml', '.yaml', '.yml', '.csv', '.tsv',
    '.md', '.ini', '.cfg', '.conf', '.log', '.toml', '.sql', '.env',
    '.py', '.js', '.ts', '.jsx', '.tsx', '.css', '.scss', '.sass', '.less',
    '.bat', '.cmd', '.sh', '.ps1', '.rb', '.go', '.java', '.c', '.cpp', '.h',
    '.cs', '.php', '.swift', '.kt', '.rs', '.vue', '.svelte', '.json5', '.lock'
}

# Filenames without a useful extension that should still count as text
TEXT_FILENAMES = {'.gitignore', '.dockerignore', '.editorconfig', '.npmrc', 'dockerfile'}

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(300, 200)
        self.setStyleSheet(self.parent().styleSheet())
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Settings (Empty)"))
        btn = QPushButton("CLOSE")
        btn.clicked.connect(self.accept)
        layout.addStretch()
        layout.addWidget(btn)

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cyberpunk Folder Scanner")
        self.resize(800, 600)
        
        # Apply Global Theme
        self.setStyleSheet(f"""
            QMainWindow, QDialog {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            
            QLineEdit, QTextEdit {{
                background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px;
                selection-background-color: {CP_CYAN}; selection-color: #000000;
            }}
            QLineEdit:focus, QTextEdit:focus {{ border: 1px solid {CP_CYAN}; }}
            
            QPushButton {{
                background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 6px 12px; font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW};
            }}
            QPushButton:pressed {{
                background-color: {CP_YELLOW}; color: black;
            }}
            
            QCheckBox {{ color: {CP_TEXT}; spacing: 8px; }}
            QCheckBox::indicator {{
                width: 16px; height: 16px; border: 1px solid {CP_DIM}; background-color: {CP_PANEL};
            }}
            QCheckBox::indicator:hover {{ border: 1px solid {CP_CYAN}; }}
            QCheckBox::indicator:checked {{
                background-color: {CP_YELLOW}; border: 1px solid {CP_YELLOW};
            }}
            
            QGroupBox {{
                border: 1px solid {CP_DIM}; margin-top: 10px; padding-top: 10px; font-weight: bold; color: {CP_YELLOW};
            }}
            QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }}
            
            QScrollBar:vertical {{ background: {CP_BG}; width: 10px; margin: 0px; }}
            QScrollBar::handle:vertical {{ background: {CP_CYAN}; min-height: 20px; border-radius: 5px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; background: none; }}
            
            QScrollBar:horizontal {{ background: {CP_BG}; height: 10px; margin: 0px; }}
            QScrollBar::handle:horizontal {{ background: {CP_CYAN}; min-width: 20px; border-radius: 5px; }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0px; background: none; }}
        """)

        self.snapshot = {}
        
        # Layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Top bar: Restart & Settings
        top_bar = QHBoxLayout()
        self.btn_restart = QPushButton("↺ RESTART")
        self.btn_restart.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_restart.clicked.connect(self.restart_app)
        
        self.btn_settings = QPushButton("⚙ SETTINGS")
        self.btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_settings.clicked.connect(self.open_settings)
        
        top_bar.addStretch()
        top_bar.addWidget(self.btn_settings)
        top_bar.addWidget(self.btn_restart)
        layout.addLayout(top_bar)

        # Folder Selection
        grp = QGroupBox("DIRECTORY SCANNER")
        form = QFormLayout()
        
        self.folder_input = QLineEdit()
        # Default to current directory
        self.folder_input.setText(os.path.dirname(__file__))
        self.btn_browse = QPushButton("BROWSE")
        self.btn_browse.clicked.connect(self.browse_folder)
        
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(self.btn_browse)
        
        form.addRow("Target Folder:", folder_layout)

        self.only_text_files = QCheckBox("Only compare text files (json, txt, html, xml, csv, md, code, ...)")
        self.only_text_files.setChecked(True)
        self.only_text_files.setCursor(Qt.CursorShape.PointingHandCursor)
        self.only_text_files.setToolTip("Only take snapshots and compare files with text extensions (json, txt, html, etc.).")
        form.addRow("", self.only_text_files)
        grp.setLayout(form)
        layout.addWidget(grp)
        
        # Actions
        action_layout = QHBoxLayout()
        self.btn_scan = QPushButton("TAKE SNAPSHOT")
        self.btn_scan.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_scan.clicked.connect(self.take_snapshot)
        
        self.btn_check = QPushButton("CHECK CHANGES")
        self.btn_check.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_check.clicked.connect(self.check_changes)
        
        action_layout.addWidget(self.btn_scan)
        action_layout.addWidget(self.btn_check)
        layout.addLayout(action_layout)
        
        # Output
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        layout.addWidget(self.output_area)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder:
            self.folder_input.setText(folder)

    def is_text_file(self, path):
        """Return True if the file has a text extension / is a known text filename."""
        name = os.path.basename(path).lower()
        return os.path.splitext(name)[1] in TEXT_EXTENSIONS or name in TEXT_FILENAMES

    def get_file_state(self, folder, text_only=False):
        state = {}
        for root, dirs, files in os.walk(folder):
            for f in files:
                filepath = os.path.join(root, f)
                if text_only and not self.is_text_file(filepath):
                    continue
                try:
                    state[filepath] = os.path.getmtime(filepath)
                except Exception:
                    pass
        return state

    def take_snapshot(self):
        folder = self.folder_input.text()
        if not os.path.isdir(folder):
            self.log(f"<span style='color:{CP_RED};'>ERROR: Invalid directory.</span>")
            return
            
        # Remember which filter mode the snapshot was taken with
        self.text_only_enabled = self.only_text_files.isChecked()
        self.snapshot = self.get_file_state(folder, text_only=self.text_only_enabled)
        mode = "text files only" if self.text_only_enabled else "all files"
        self.log(f"Snapshot taken for {len(self.snapshot)} files ({mode}) in {folder}.")

    def check_changes(self):
        folder = self.folder_input.text()
        if not os.path.isdir(folder):
            self.log(f"<span style='color:{CP_RED};'>ERROR: Invalid directory.</span>")
            return
            
        if not self.snapshot:
            self.log(f"<span style='color:{CP_RED};'>ERROR: No snapshot found. Please take a snapshot first.</span>")
            return
            
        # Use the same filter mode the snapshot was taken with so the sets match
        if hasattr(self, 'text_only_enabled') and self.only_text_files.isChecked() != self.text_only_enabled:
            self.log(f"<span style='color:{CP_YELLOW};'>Note: text-file filter changed since the snapshot; using the snapshot's setting.</span>")
        
        current_state = self.get_file_state(folder, text_only=getattr(self, 'text_only_enabled', False))
        
        added = []
        modified = []
        deleted = []
        
        for path, mtime in current_state.items():
            if path not in self.snapshot:
                added.append(path)
            elif self.snapshot[path] != mtime:
                modified.append(path)
                
        for path in self.snapshot:
            if path not in current_state:
                deleted.append(path)
                
        if not added and not modified and not deleted:
            self.log(f"<span style='color:{CP_YELLOW};'>No changes detected.</span>")
        else:
            self.log("<br>--- CHANGES DETECTED ---")
            for f in added:
                self.log(f"<span style='color:{CP_GREEN};'>[ADDED]</span> {f}")
            for f in modified:
                self.log(f"<span style='color:{CP_CYAN};'>[MODIFIED]</span> {f}")
            for f in deleted:
                self.log(f"<span style='color:{CP_RED};'>[DELETED]</span> {f}")
        
        # Update snapshot to current so sequential checks work
        self.snapshot = current_state

    def log(self, message):
        self.output_area.append(message)

    def restart_app(self):
        os.execv(sys.executable, [sys.executable] + sys.argv)
        
    def open_settings(self):
        dlg = SettingsDialog(self)
        dlg.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())
