import sys
import subprocess
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QLabel, QPushButton, QComboBox, QGroupBox, 
                             QFormLayout, QTextEdit, QMessageBox, QHBoxLayout, 
                             QScrollArea, QFileDialog, QDialog, QLineEdit, QDialogButtonBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSettings
from PyQt6.QtGui import QCursor, QTextCursor

# ==========================================
# 1. THEME CONSTANTS (From THEME_GUIDE.md)
# ==========================================
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

# ==========================================
# 2. HELPER CLASSES
# ==========================================

class CyberButton(QPushButton):
    """Custom button based on Theme Guide Section 4"""
    def __init__(self, text, color=CP_DIM, hover_color=CP_YELLOW):
        super().__init__(text)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.default_style = f"""
            QPushButton {{
                background-color: {CP_DIM};
                color: white;
                border: 1px solid {CP_DIM};
                padding: 10px;
                border-radius: 0px;
                font-family: 'Consolas';
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2a2a2a;
                color: {hover_color};
                border: 1px solid {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {hover_color};
                color: black;
            }}
        """
        self.setStyleSheet(self.default_style)

# ==========================================
# 3. WORKER THREADS
# ==========================================

class WSLListOnlineWorker(QThread):
    """Fetches available ONLINE distros"""
    finished = pyqtSignal(list, str)

    def run(self):
        try:
            result = subprocess.run(["wsl", "--list", "--online"], capture_output=True, text=True, encoding='utf-16-le')
            if result.returncode == 0:
                lines = result.stdout.splitlines()
                distros = []
                start_parsing = False
                for line in lines:
                    clean_line = line.strip()
                    if "NAME" in clean_line and "FRIENDLY NAME" in clean_line:
                        start_parsing = True
                        continue
                    if start_parsing and clean_line:
                        parts = clean_line.split()
                        if parts:
                            distros.append(parts[0])
                self.finished.emit(distros, "")
            else:
                self.finished.emit([], f"Error fetching list: {result.stderr}")
        except Exception as e:
            self.finished.emit([], str(e))

class WSLListInstalledWorker(QThread):
    """Fetches CURRENTLY INSTALLED distros"""
    finished = pyqtSignal(list, str)

    def run(self):
        try:
            # wsl --list --quiet returns just names, but encoding is tricky. 
            # wsl --list --verbose is often cleaner but needs parsing.
            # Simple `wsl --list` usually works.
            result = subprocess.run(["wsl", "--list"], capture_output=True, text=True, encoding='utf-16-le')
            if result.returncode == 0:
                lines = result.stdout.splitlines()
                distros = []
                for line in lines:
                    clean = line.strip()
                    # Remove "Default" marker if present (e.g., "Ubuntu (Default)")
                    # Or specific status text. Usually `wsl --list` just lists them or has a header
                    if "Windows Subsystem for Linux Distributions" in clean or not clean:
                        continue
                    # Handle "(Default)" suffix
                    name = clean.split()[0] # Take first word (Distro Name)
                    if name:
                        distros.append(name)
                self.finished.emit(distros, "")
            else:
                self.finished.emit([], f"Error fetching installed: {result.stderr}")
        except Exception as e:
            self.finished.emit([], str(e))

class WSLInstallWorker(QThread):
    """Installs a distro"""
    log_signal = pyqtSignal(str)
    finished = pyqtSignal(bool)

    def __init__(self, distro_name):
        super().__init__()
        self.distro_name = distro_name

    def run(self):
        self.log_signal.emit(f"Starting installation for: {self.distro_name}...")
        try:
            cmd = f'start cmd /k "wsl --install -d {self.distro_name}"'
            subprocess.Popen(cmd, shell=True)
            self.log_signal.emit("Installation command launched in external terminal.")
            self.finished.emit(True)
        except Exception as e:
            self.log_signal.emit(f"Error launching install: {str(e)}")
            self.finished.emit(False)

class WSLBackupWorker(QThread):
    """Backs up a distro to a .tar file"""
    log_signal = pyqtSignal(str)
    finished = pyqtSignal(bool)

    def __init__(self, distro_name, file_path):
        super().__init__()
        self.distro_name = distro_name
        self.file_path = file_path

    def run(self):
        self.log_signal.emit(f"Backing up {self.distro_name} to {self.file_path}...")
        self.log_signal.emit("This may take a while depending on size...")
        try:
            # CREATE_NO_WINDOW flag to keep it cleaner, or just run normally
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            cmd = ["wsl", "--export", self.distro_name, self.file_path]
            process = subprocess.run(cmd, capture_output=True, text=True) # default encoding usually fine for wsl export
            
            if process.returncode == 0:
                self.log_signal.emit(f"Backup SUCCESS: {self.file_path}")
                self.finished.emit(True)
            else:
                self.log_signal.emit(f"Backup FAILED: {process.stderr}")
                self.finished.emit(False)
        except Exception as e:
            self.log_signal.emit(f"Backup Exception: {str(e)}")
            self.finished.emit(False)

class WSLRestoreWorker(QThread):
    """Restores/Imports a distro from a .tar file"""
    log_signal = pyqtSignal(str)
    finished = pyqtSignal(bool)

    def __init__(self, distro_name, install_path, tar_path):
        super().__init__()
        self.distro_name = distro_name
        self.install_path = install_path
        self.tar_path = tar_path

    def run(self):
        self.log_signal.emit(f"Restoring {self.distro_name} from {self.tar_path}...")
        self.log_signal.emit(f"Installing to: {self.install_path}")
        try:
            # wsl --import <Distro> <InstallLocation> <FileName>
            cmd = ["wsl", "--import", self.distro_name, self.install_path, self.tar_path]
            process = subprocess.run(cmd, capture_output=True, text=True)
            
            if process.returncode == 0:
                self.log_signal.emit(f"Restore SUCCESS: {self.distro_name} is ready.")
                self.finished.emit(True)
            else:
                self.log_signal.emit(f"Restore FAILED: {process.stderr}")
                self.finished.emit(False)
        except Exception as e:
            self.log_signal.emit(f"Restore Exception: {str(e)}")
            self.finished.emit(False)

# ==========================================
# 4. DIALOGS
# ==========================================

class SettingsDialog(QDialog):
    def __init__(self, parent=None, current_path=""):
        super().__init__(parent)
        self.setWindowTitle("CONFIGURATION")
        self.resize(500, 150)
        self.setStyleSheet(parent.styleSheet()) # Inherit theme
        
        layout = QVBoxLayout(self)
        
        grp = QGroupBox("DEFAULT BACKUP LOCATION")
        form = QFormLayout()
        
        self.path_edit = QLineEdit(current_path)
        self.btn_browse = CyberButton("BROWSE", hover_color=CP_CYAN)
        self.btn_browse.clicked.connect(self.browse_folder)
        
        form.addRow(self.path_edit)
        form.addRow(self.btn_browse)
        grp.setLayout(form)
        
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        
        # Style buttons (hacky but works for QDialogButtonBox in this theme context)
        for btn in btns.buttons():
            btn.setStyleSheet(f"background-color: {CP_DIM}; color: white; border: 1px solid {CP_DIM}; padding: 5px;")

        layout.addWidget(grp)
        layout.addWidget(btns)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Backup Folder")
        if folder:
            self.path_edit.setText(folder)

    def get_path(self):
        return self.path_edit.text()

# ==========================================
# 5. MAIN APPLICATION
# ==========================================

class WSLManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WSL CYBER-MANAGER v2.0")
        self.resize(900, 800)
        
        # Persistent Settings
        self.settings = QSettings("CyberCorp", "WSLManager")
        
        self.apply_theme()
        self.init_ui()
        
        # Initial Loads
        self.load_online_distros()
        self.load_installed_distros()

    def get_backup_path(self):
        val = self.settings.value("backup_path", "")
        if not val:
            return os.getcwd()
        return val

    def apply_theme(self):
        self.setStyleSheet(f"""
            QMainWindow, QDialog {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            
            QLineEdit, QSpinBox, QComboBox, QPlainTextEdit, QTextEdit {{
                background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px;
                selection-background-color: {CP_CYAN}; selection-color: #000000;
            }}
            QLineEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QComboBox:focus {{ border: 1px solid {CP_CYAN}; }}
            
            QComboBox QAbstractItemView {{
                background-color: {CP_PANEL}; color: {CP_TEXT}; border: 1px solid {CP_DIM};
                selection-background-color: {CP_CYAN}; selection-color: black;
            }}
            
            QGroupBox {{
                border: 1px solid {CP_DIM}; margin-top: 10px; padding-top: 10px; font-weight: bold; color: {CP_YELLOW};
            }}
            QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }}
            
            QScrollArea {{ background: transparent; border: none; }}
        """)

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(15)
        
        # --- HEADER ---
        header_layout = QHBoxLayout()
        title = QLabel("WSL DISTRIBUTION MANAGER")
        title.setStyleSheet(f"font-size: 16pt; font-weight: bold; color: {CP_CYAN}; letter-spacing: 2px;")
        
        btn_settings = CyberButton("SETTINGS", hover_color=CP_CYAN)
        btn_settings.setFixedWidth(100)
        btn_settings.clicked.connect(self.open_settings)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(btn_settings)
        layout.addLayout(header_layout)

        # --- SECTION 1: INSTALL NEW ---
        grp_install = QGroupBox("INSTALL NEW DISTRO")
        layout_install = QHBoxLayout()
        
        self.combo_online = QComboBox()
        self.combo_online.addItem("Scanning...", "none")
        self.combo_online.setEnabled(False)
        
        self.btn_install = CyberButton("INSTALL", hover_color=CP_GREEN)
        self.btn_install.clicked.connect(self.install_distro)
        self.btn_install.setEnabled(False)

        layout_install.addWidget(QLabel("Online:"))
        layout_install.addWidget(self.combo_online, 1)
        layout_install.addWidget(self.btn_install)
        grp_install.setLayout(layout_install)
        layout.addWidget(grp_install)

        # --- SECTION 2: MANAGE INSTALLED (BACKUP) ---
        grp_local = QGroupBox("LOCAL MANAGEMENT")
        layout_local = QFormLayout()
        
        self.combo_installed = QComboBox()
        self.combo_installed.addItem("Scanning...", "none")
        self.combo_installed.setEnabled(False)
        
        # Backup Actions
        backup_layout = QHBoxLayout()
        self.btn_refresh_local = CyberButton("REFRESH", hover_color=CP_TEXT)
        self.btn_refresh_local.clicked.connect(self.load_installed_distros)
        
        self.btn_backup = CyberButton("BACKUP DISTRO", hover_color=CP_ORANGE)
        self.btn_backup.clicked.connect(self.backup_distro)
        self.btn_backup.setEnabled(False)
        
        backup_layout.addWidget(self.btn_refresh_local)
        backup_layout.addWidget(self.btn_backup)
        
        layout_local.addRow("Installed:", self.combo_installed)
        layout_local.addRow("", backup_layout)
        grp_local.setLayout(layout_local)
        layout.addWidget(grp_local)

        # --- SECTION 3: RESTORE ---
        grp_restore = QGroupBox("RESTORE FROM BACKUP")
        layout_restore = QHBoxLayout()
        self.btn_restore = CyberButton("RESTORE ARCHIVE (.tar)", hover_color=CP_RED)
        self.btn_restore.clicked.connect(self.restore_distro)
        layout_restore.addWidget(self.btn_restore)
        grp_restore.setLayout(layout_restore)
        layout.addWidget(grp_restore)

        # --- LOG ---
        grp_log = QGroupBox("SYSTEM LOG")
        log_l = QVBoxLayout()
        self.text_log = QTextEdit()
        self.text_log.setReadOnly(True)
        self.text_log.setStyleSheet(f"color: {CP_TEXT}; font-family: 'Consolas'; font-size: 9pt;")
        log_l.addWidget(self.text_log)
        grp_log.setLayout(log_l)
        layout.addWidget(grp_log)

    # --- LOGIC ---

    def log(self, message, color=CP_TEXT):
        from datetime import datetime
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        colored_msg = f'<span style="color:{CP_SUBTEXT};">{timestamp}</span> <span style="color:{color};">{message}</span>'
        self.text_log.append(colored_msg)
        self.text_log.moveCursor(QTextCursor.MoveOperation.End)

    def open_settings(self):
        dlg = SettingsDialog(self, self.get_backup_path())
        if dlg.exec():
            new_path = dlg.get_path()
            self.settings.setValue("backup_path", new_path)
            self.log(f"Configuration saved. Backup path: {new_path}", CP_YELLOW)

    # --- LOADERS ---

    def load_online_distros(self):
        self.worker_online = WSLListOnlineWorker()
        self.worker_online.finished.connect(self.on_online_loaded)
        self.worker_online.start()

    def on_online_loaded(self, distros, error):
        self.combo_online.clear()
        if error:
            self.combo_online.addItem("Error")
            self.log(error, CP_RED)
        else:
            self.combo_online.addItems(distros)
            self.combo_online.setEnabled(True)
            self.btn_install.setEnabled(True)

    def load_installed_distros(self):
        self.combo_installed.clear()
        self.combo_installed.addItem("Scanning...")
        self.combo_installed.setEnabled(False)
        self.btn_backup.setEnabled(False)
        
        self.worker_local = WSLListInstalledWorker()
        self.worker_local.finished.connect(self.on_installed_loaded)
        self.worker_local.start()

    def on_installed_loaded(self, distros, error):
        self.combo_installed.clear()
        if error:
            self.log(error, CP_RED)
        elif not distros:
            self.combo_installed.addItem("No distros found")
        else:
            self.combo_installed.addItems(distros)
            self.combo_installed.setEnabled(True)
            self.btn_backup.setEnabled(True)
            self.log(f"Found {len(distros)} installed distributions.", CP_GREEN)

    # --- ACTIONS ---

    def install_distro(self):
        distro = self.combo_online.currentText()
        if distro and distro != "Scanning...":
             self.worker_install = WSLInstallWorker(distro)
             self.worker_install.log_signal.connect(lambda s: self.log(s, CP_CYAN))
             self.worker_install.finished.connect(lambda b: self.load_installed_distros()) # Refresh local after install
             self.worker_install.start()

    def backup_distro(self):
        distro = self.combo_installed.currentText()
        if not distro or distro == "Scanning...": return
        
        base_path = self.get_backup_path()
        default_filename = os.path.join(base_path, f"{distro}_backup.tar")
        
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Backup As", default_filename, "Tar Files (*.tar)")
        
        if file_path:
            self.worker_backup = WSLBackupWorker(distro, file_path)
            self.worker_backup.log_signal.connect(lambda s: self.log(s, CP_ORANGE))
            self.worker_backup.finished.connect(lambda b: self.log("Backup Task Ended", CP_TEXT))
            self.worker_backup.start()

    def restore_distro(self):
        base_path = self.get_backup_path()
        tar_path, _ = QFileDialog.getOpenFileName(self, "Select Backup File", base_path, "Tar Files (*.tar)")
        
        if not tar_path: return

        # Need to ask for new Name and Install Path
        # Simple Input Dialogs for now, ideally a custom dialog but this works
        from PyQt6.QtWidgets import QInputDialog
        
        name, ok1 = QInputDialog.getText(self, "Restore Distro", "Enter unique name for new distro (e.g. Ubuntu-Restored):")
        if not ok1 or not name: return
        
        install_loc = QFileDialog.getExistingDirectory(self, "Select Install Directory")
        if not install_loc: return
        
        # Confirm
        full_install_path = os.path.join(install_loc, name)
        
        self.worker_restore = WSLRestoreWorker(name, full_install_path, tar_path)
        self.worker_restore.log_signal.connect(lambda s: self.log(s, CP_RED))
        self.worker_restore.finished.connect(lambda b: self.load_installed_distros())
        self.worker_restore.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WSLManagerApp()
    window.show()
    sys.exit(app.exec())