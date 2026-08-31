import sys
import os
import winreg
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                             QGroupBox, QFormLayout, QTextEdit, QMessageBox, QDialog,
                             QComboBox)
from PyQt6.QtCore import Qt

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

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙ SETTINGS")
        self.resize(300, 200)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {CP_BG}; border: 1px solid {CP_CYAN}; }}
            QLabel {{ color: {CP_TEXT}; font-family: 'Consolas'; }}
            QPushButton {{
                background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 6px 12px; font-weight: bold; font-family: 'Consolas';
            }}
            QPushButton:hover {{
                background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW};
            }}
        """)
        layout = QVBoxLayout(self)
        lbl = QLabel("⚙ CUSTOM SETTINGS\n\nNo configurable options needed for this utility.\nSettings are empty by default.")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn = QPushButton("CLOSE")
        btn.clicked.connect(self.accept)
        layout.addWidget(lbl)
        layout.addWidget(btn)
        layout.addWidget(btn)

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Helium Incognito Setup Utility")
        self.resize(750, 520)
        
        # Apply Global Theme
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            
            QLineEdit, QTextEdit {{
                background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 6px;
            }}
            QLineEdit:focus, QTextEdit:focus {{ border: 1px solid {CP_CYAN}; }}
            
            QComboBox {{
                background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 6px; font-weight: bold;
            }}
            QComboBox:focus {{ border: 1px solid {CP_CYAN}; }}
            QComboBox::drop-down {{
                border: 0px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {CP_CYAN};
                width: 0;
                height: 0;
                margin-right: 10px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {CP_PANEL};
                color: {CP_CYAN};
                selection-background-color: {CP_DIM};
                selection-color: {CP_YELLOW};
                border: 1px solid {CP_CYAN};
            }}

            QPushButton {{
                background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 10px 18px; font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW};
            }}
            QPushButton:pressed {{
                background-color: {CP_YELLOW}; color: black;
            }}
            
            QGroupBox {{
                border: 1px solid {CP_DIM}; margin-top: 15px; padding-top: 15px; font-weight: bold; color: {CP_YELLOW};
            }}
            QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }}
        """)

        # Main Layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header Banner
        header = QLabel("⚡ HELIUM INCOGNITO REDIRECTOR ⚡")
        header.setStyleSheet(f"color: {CP_CYAN}; font-size: 16pt; font-weight: bold;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Subtitle
        subtitle = QLabel("System-wide protocol utility for Windows Terminal & Command Line links")
        subtitle.setStyleSheet(f"color: {CP_SUBTEXT}; font-size: 9pt;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        # Status Group Box
        status_grp = QGroupBox("SYSTEM STATUS")
        status_layout = QFormLayout(status_grp)
        status_layout.setContentsMargins(15, 20, 15, 15)
        status_layout.setHorizontalSpacing(20)
        status_layout.setVerticalSpacing(12)
        
        self.browser_combo = QComboBox()
        self.browser_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.progid_label = QLabel("Detecting...")
        self.progid_label.setStyleSheet(f"color: {CP_CYAN}; font-weight: bold;")
        
        self.incognito_status_label = QLabel("Detecting...")
        self.incognito_status_label.setStyleSheet("font-weight: bold;")
        
        self.cmd_view = QTextEdit()
        self.cmd_view.setReadOnly(True)
        self.cmd_view.setFixedHeight(60)
        
        status_layout.addRow("Select Browser:", self.browser_combo)
        status_layout.addRow("Browser ProgID:", self.progid_label)
        status_layout.addRow("Incognito Mode:", self.incognito_status_label)
        status_layout.addRow("Launch Command:", self.cmd_view)
        
        layout.addWidget(status_grp)

        # Actions Group Box
        actions_grp = QGroupBox("REGISTRY CONTROL")
        actions_layout = QHBoxLayout(actions_grp)
        actions_layout.setContentsMargins(15, 20, 15, 15)
        actions_layout.setSpacing(15)
        
        self.btn_enable = QPushButton("⚡ ENABLE INCOGNITO MODE")
        self.btn_enable.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_enable.setStyleSheet(f"""
            QPushButton {{
                border: 1px solid {CP_GREEN};
                color: {CP_GREEN};
                background-color: #0c1a0e;
            }}
            QPushButton:hover {{
                background-color: {CP_GREEN};
                color: black;
            }}
        """)
        self.btn_enable.clicked.connect(self.enable_incognito)
        
        self.btn_disable = QPushButton("❌ DISABLE INCOGNITO MODE")
        self.btn_disable.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_disable.setStyleSheet(f"""
            QPushButton {{
                border: 1px solid {CP_RED};
                color: {CP_RED};
                background-color: #21070c;
            }}
            QPushButton:hover {{
                background-color: {CP_RED};
                color: black;
            }}
        """)
        self.btn_disable.clicked.connect(self.disable_incognito)
        
        actions_layout.addWidget(self.btn_enable)
        actions_layout.addWidget(self.btn_disable)
        layout.addWidget(actions_grp)

        # Footer Toolbar
        footer_layout = QHBoxLayout()
        
        btn_restart = QPushButton("↺ RESTART")
        btn_restart.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_restart.setStyleSheet(f"color: {CP_YELLOW}; border-color: {CP_DIM};")
        btn_restart.clicked.connect(self.restart_app)
        
        btn_settings = QPushButton("⚙ SETTINGS")
        btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_settings.setStyleSheet(f"color: {CP_CYAN}; border-color: {CP_DIM};")
        btn_settings.clicked.connect(self.open_settings)
        
        self.console_msg = QLabel("Ready")
        self.console_msg.setStyleSheet(f"color: {CP_SUBTEXT};")
        
        footer_layout.addWidget(btn_restart)
        footer_layout.addWidget(btn_settings)
        footer_layout.addStretch()
        footer_layout.addWidget(self.console_msg)
        
        layout.addLayout(footer_layout)

        # Populate and connect combobox
        self.browsers_list = self.get_installed_browsers()
        for b in self.browsers_list:
            self.browser_combo.addItem(b["name"], b)
        self.browser_combo.currentIndexChanged.connect(self.refresh_status)

        # Initial Refresh
        self.refresh_status()

    def get_http_progid(self):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice") as key:
                prog_id, _ = winreg.QueryValueEx(key, "ProgId")
                return prog_id
        except OSError:
            return None

    def get_installed_browsers(self):
        browsers = []
        # Add a default entry for System Default
        default_progid = self.get_http_progid()
        default_name = f"System Default ({default_progid})" if default_progid else "System Default"
        browsers.append({"name": default_name, "prog_id": default_progid, "is_default": True})

        # Known common fallbacks to ensure they are available even if scanning has issues
        common_browsers = {
            "ChromeHTML": "Google Chrome",
            "MSEdgeHTM": "Microsoft Edge",
            "FirefoxHTML": "Mozilla Firefox",
            "BraveHTML": "Brave Browser",
            "OperaStable": "Opera Browser"
        }

        found_progids = set()
        if default_progid:
            found_progids.add(default_progid)

        # Registry locations for browsers
        reg_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Clients\StartMenuInternet"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Clients\StartMenuInternet")
        ]

        for hkey, base_path in reg_paths:
            try:
                with winreg.OpenKey(hkey, base_path) as key:
                    info = winreg.QueryInfoKey(key)
                    for i in range(info[0]): # subkeys count
                        subkey_name = winreg.EnumKey(key, i)
                        try:
                            # Try to get the friendly name
                            with winreg.OpenKey(hkey, fr"{base_path}\{subkey_name}") as subkey:
                                friendly_name, _ = winreg.QueryValueEx(subkey, "")
                            
                            # Try to get the ProgID from Capabilities
                            assoc_path = fr"{base_path}\{subkey_name}\Capabilities\URLAssociations"
                            with winreg.OpenKey(hkey, assoc_path) as assoc_key:
                                prog_id, _ = winreg.QueryValueEx(assoc_key, "http")
                                if prog_id and prog_id not in found_progids:
                                    browsers.append({"name": friendly_name, "prog_id": prog_id, "is_default": False})
                                    found_progids.add(prog_id)
                        except OSError:
                            continue
            except OSError:
                continue

        # Add common fallbacks if not already found/added
        for prog_id, name in common_browsers.items():
            if prog_id not in found_progids:
                if self.get_progid_command(prog_id):
                    browsers.append({"name": name, "prog_id": prog_id, "is_default": False})
                    found_progids.add(prog_id)

        return browsers

    def get_selected_progid(self):
        idx = self.browser_combo.currentIndex()
        if idx < 0:
            return self.get_http_progid()
        data = self.browser_combo.itemData(idx)
        if data and data.get("is_default"):
            return self.get_http_progid()
        return data.get("prog_id") if data else self.get_http_progid()

    def get_progid_command(self, prog_id):
        try:
            path = fr"Software\Classes\{prog_id}\shell\open\command"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path) as key:
                value, _ = winreg.QueryValueEx(key, "")
                return value
        except OSError:
            try:
                with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, fr"{prog_id}\shell\open\command") as key:
                    value, _ = winreg.QueryValueEx(key, "")
                    return value
            except OSError:
                return None

    def parse_command(self, cmd_str):
        cmd_str = cmd_str.strip()
        if cmd_str.startswith('"'):
            end_quote_idx = cmd_str.find('"', 1)
            if end_quote_idx != -1:
                exe = cmd_str[1:end_quote_idx]
                args = cmd_str[end_quote_idx+1:].strip()
                return exe, args
        parts = cmd_str.split(' ', 1)
        if len(parts) > 1:
            return parts[0], parts[1]
        return parts[0], ""

    def get_private_flag(self, exe_path):
        exe_name = os.path.basename(exe_path).lower()
        if "chrome" in exe_name or "brave" in exe_name:
            return "--incognito"
        elif "edge" in exe_name or "msedge" in exe_name:
            return "-inprivate"
        elif "firefox" in exe_name or "librewolf" in exe_name or "waterfox" in exe_name:
            return "-private-window"
        elif "opera" in exe_name:
            return "--private"
        else:
            return "--incognito"

    def refresh_status(self):
        prog_id = self.get_selected_progid()
        if not prog_id:
            self.progid_label.setText("Not Found")
            self.incognito_status_label.setText("UNKNOWN")
            self.incognito_status_label.setStyleSheet(f"color: {CP_RED}; font-weight: bold;")
            self.cmd_view.setText("")
            return

        self.progid_label.setText(prog_id)
        cmd_str = self.get_progid_command(prog_id)
        if not cmd_str:
            self.incognito_status_label.setText("COMMAND NOT FOUND")
            self.incognito_status_label.setStyleSheet(f"color: {CP_RED}; font-weight: bold;")
            self.cmd_view.setText("")
            return

        self.cmd_view.setText(cmd_str)
        exe, args = self.parse_command(cmd_str)
        arg_tokens = args.split()
        
        flag = self.get_private_flag(exe)
        all_flags = ["--incognito", "-inprivate", "--inprivate", "-private-window", "--private-window", "--private", "-private"]
        is_active = any(f in arg_tokens for f in all_flags)
        
        if is_active:
            self.incognito_status_label.setText(f"ACTIVE ({flag.upper().strip('-')})")
            self.incognito_status_label.setStyleSheet(f"color: {CP_GREEN}; font-weight: bold;")
        else:
            self.incognito_status_label.setText("INACTIVE (NORMAL)")
            self.incognito_status_label.setStyleSheet(f"color: {CP_ORANGE}; font-weight: bold;")

    def write_registry_value(self, prog_id, value):
        path = fr"Software\Classes\{prog_id}\shell\open\command"
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, path)
            with key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, value)
            return True
        except OSError as e:
            QMessageBox.critical(self, "Registry Error", f"Failed to update registry:\n{str(e)}")
            return False

    def enable_incognito(self):
        prog_id = self.get_selected_progid()
        if not prog_id:
            QMessageBox.warning(self, "Warning", "Could not identify selected browser ProgID.")
            return

        cmd_str = self.get_progid_command(prog_id)
        if not cmd_str:
            QMessageBox.warning(self, "Warning", f"No launch command found for {prog_id}.")
            return

        exe, args = self.parse_command(cmd_str)
        arg_tokens = args.split()
        flag = self.get_private_flag(exe)
        
        # Clean any other known private flags first to avoid conflicts
        all_flags = ["--incognito", "-inprivate", "--inprivate", "-private-window", "--private-window", "--private", "-private"]
        arg_tokens = [t for t in arg_tokens if t.lower() not in all_flags]
        
        arg_tokens.insert(0, flag)
        new_args = " ".join(arg_tokens)
        new_value = f'"{exe}" {new_args}'

        if self.write_registry_value(prog_id, new_value):
            self.console_msg.setText(f"Status: Private mode enabled ({flag})")
            self.console_msg.setStyleSheet(f"color: {CP_GREEN};")
            self.refresh_status()

    def disable_incognito(self):
        prog_id = self.get_selected_progid()
        if not prog_id:
            QMessageBox.warning(self, "Warning", "Could not identify selected browser ProgID.")
            return

        cmd_str = self.get_progid_command(prog_id)
        if not cmd_str:
            QMessageBox.warning(self, "Warning", f"No launch command found for {prog_id}.")
            return

        exe, args = self.parse_command(cmd_str)
        arg_tokens = args.split()
        
        # Clean all known private flags
        all_flags = ["--incognito", "-inprivate", "--inprivate", "-private-window", "--private-window", "--private", "-private"]
        arg_tokens = [t for t in arg_tokens if t.lower() not in all_flags]
        
        new_args = " ".join(arg_tokens)
        new_value = f'"{exe}" {new_args}'

        if self.write_registry_value(prog_id, new_value):
            self.console_msg.setText("Status: Private mode disabled")
            self.console_msg.setStyleSheet(f"color: {CP_ORANGE};")
            self.refresh_status()

    def restart_app(self):
        os.execv(sys.executable, [sys.executable] + sys.argv)

    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())
