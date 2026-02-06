import sys
import os
import json
import base64
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QGroupBox, QFormLayout,
    QScrollArea, QFrame, QMessageBox, QComboBox, QInputDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# CYBERPUNK THEME PALETTE
CP_BG = "#050505"
CP_PANEL = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN = "#00F0FF"
CP_RED = "#FF003C"
CP_GREEN = "#00ff21"
CP_DIM = "#3a3a3a"
CP_TEXT = "#E0E0E0"
CP_SUBTEXT = "#808080"

VAULT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vault.json")

class CryptoManager:
    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    @staticmethod
    def encrypt_data(data: str, password: str) -> dict:
        salt = os.urandom(16)
        key = CryptoManager.derive_key(password, salt)
        f = Fernet(key)
        encrypted_content = f.encrypt(data.encode())
        return {
            "salt": base64.b64encode(salt).decode('utf-8'),
            "data": encrypted_content.decode('utf-8')
        }

    @staticmethod
    def decrypt_data(encrypted_bundle: dict, password: str) -> str:
        try:
            salt = base64.b64decode(encrypted_bundle["salt"])
            data = encrypted_bundle["data"].encode()
            key = CryptoManager.derive_key(password, salt)
            f = Fernet(key)
            return f.decrypt(data).decode('utf-8')
        except Exception:
            return None

class PasswordEntry(QFrame):
    def __init__(self, username, password, parent=None):
        super().__init__(parent)
        self.username = username
        self.password = password
        self.init_ui()

    def init_ui(self):
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"border: 1px solid {CP_DIM}; background: {CP_PANEL}; margin: 2px; padding: 5px;")
        
        layout = QHBoxLayout(self)
        
        info_layout = QVBoxLayout()
        user_lbl = QLabel(f"USER: {self.username}")
        pass_lbl = QLabel(f"PASS: {'*' * len(self.password)}")
        user_lbl.setStyleSheet(f"color: {CP_TEXT}; border: none;")
        pass_lbl.setStyleSheet(f"color: {CP_SUBTEXT}; border: none;")
        info_layout.addWidget(user_lbl)
        info_layout.addWidget(pass_lbl)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        copy_user_btn = QPushButton("COPY USER")
        copy_pass_btn = QPushButton("COPY PASS")
        
        for btn in [copy_user_btn, copy_pass_btn]:
            btn.setFixedWidth(100)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
        copy_user_btn.clicked.connect(lambda: self.copy_to_clipboard(self.username))
        copy_pass_btn.clicked.connect(lambda: self.copy_to_clipboard(self.password))
        
        layout.addWidget(copy_user_btn)
        layout.addWidget(copy_pass_btn)

    def copy_to_clipboard(self, text):
        QApplication.clipboard().setText(text)

class LoginWindow(QWidget):
    authenticated = pyqtSignal(str, dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("VAULT ACCESS")
        self.setFixedSize(400, 200)
        self.setStyleSheet(self.get_stylesheet())
        self.init_ui()

    def get_stylesheet(self):
        return f"""
            QWidget {{ background-color: {CP_BG}; color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            QLineEdit {{ background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 8px; }}
            QPushButton {{ background-color: {CP_DIM}; color: white; border: 1px solid {CP_DIM}; padding: 10px; font-weight: bold; }}
            QPushButton:hover {{ border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }}
        """

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("ENTER MASTER PASSWORD")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.returnPressed.connect(self.attempt_login)
        
        login_btn = QPushButton("ACCESS SYSTEM")
        login_btn.clicked.connect(self.attempt_login)
        
        layout.addWidget(QLabel("CYBER-VAULT v1.0"))
        layout.addWidget(self.pass_input)
        layout.addWidget(login_btn)
        layout.addStretch()

    def attempt_login(self):
        password = self.pass_input.text()
        if not password:
            return

        if not os.path.exists(VAULT_FILE):
            # Create new vault
            initial_data = {}
            self.authenticated.emit(password, initial_data)
            return

        try:
            with open(VAULT_FILE, "r") as f:
                encrypted_bundle = json.load(f)
            
            decrypted = CryptoManager.decrypt_data(encrypted_bundle, password)
            if decrypted is not None:
                self.authenticated.emit(password, json.loads(decrypted))
            else:
                QMessageBox.critical(self, "ERROR", "ACCESS DENIED: INVALID KEY")
        except Exception as e:
            QMessageBox.critical(self, "ERROR", f"VAULT CORRUPTED: {str(e)}")

class MainWindow(QMainWindow):
    def __init__(self, master_password, vault_data):
        super().__init__()
        self.master_password = master_password
        self.vault_data = vault_data # { "Domain": [{"u": "...", "p": "..."}, ...] }
        
        self.setWindowTitle("CYBER-VAULT MANAGER")
        self.resize(900, 700)
        self.setStyleSheet(self.get_stylesheet())
        self.init_ui()

    def get_stylesheet(self):
        return f"""
            QMainWindow {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            QLineEdit, QComboBox {{
                background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 6px; 
            }}
            QLineEdit:focus {{ border: 1px solid {CP_CYAN}; }}
            QPushButton {{
                background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 8px 15px; font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW};
            }}
            QGroupBox {{
                border: 1px solid {CP_DIM}; margin-top: 15px; padding-top: 15px; font-weight: bold; color: {CP_YELLOW};
            }}
            QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }}
            QScrollArea {{ border: none; background: transparent; }}
        """

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        # Left Sidebar: Group Management
        sidebar = QVBoxLayout()
        sidebar_grp = QGroupBox("DOMAINS / GROUPS")
        sidebar_layout = QVBoxLayout()
        
        self.group_list = QComboBox()
        self.refresh_groups()
        self.group_list.currentTextChanged.connect(self.load_entries)
        
        add_group_btn = QPushButton("+ NEW GROUP")
        add_group_btn.clicked.connect(self.add_group)
        
        sidebar_layout.addWidget(self.group_list)
        sidebar_layout.addWidget(add_group_btn)
        sidebar_layout.addStretch()
        
        restart_btn = QPushButton("↺ RESTART")
        restart_btn.setStyleSheet(f"color: {CP_RED}; border-color: {CP_RED};")
        restart_btn.clicked.connect(self.restart_app)
        sidebar_layout.addWidget(restart_btn)
        
        sidebar_grp.setLayout(sidebar_layout)
        sidebar.addWidget(sidebar_grp)
        main_layout.addLayout(sidebar, 1)

        # Right Side: Entries
        content_layout = QVBoxLayout()
        
        # Entry Addition
        add_grp = QGroupBox("ADD NEW CREDENTIAL")
        add_form = QFormLayout()
        self.u_input = QLineEdit()
        self.p_input = QLineEdit()
        self.p_input.setEchoMode(QLineEdit.EchoMode.Password)
        add_form.addRow("USERNAME:", self.u_input)
        add_form.addRow("PASSWORD:", self.p_input)
        
        add_btn = QPushButton("SAVE TO VAULT")
        add_btn.clicked.connect(self.save_entry)
        add_form.addRow(add_btn)
        add_grp.setLayout(add_form)
        content_layout.addWidget(add_grp)

        # Entries List
        self.scroll = QScrollArea()
        self.scroll_content = QWidget()
        self.entries_layout = QVBoxLayout(self.scroll_content)
        self.entries_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        self.scroll.setWidgetResizable(True)
        
        content_layout.addWidget(QLabel("VAULT ENTRIES:"))
        content_layout.addWidget(self.scroll)
        
        main_layout.addLayout(content_layout, 3)
        
        self.load_entries()

    def refresh_groups(self):
        current = self.group_list.currentText()
        self.group_list.clear()
        groups = sorted(list(self.vault_data.keys()))
        self.group_list.addItems(groups)
        if current in groups:
            self.group_list.setCurrentText(current)

    def add_group(self):
        name, ok = QInputDialog.getText(self, "NEW GROUP", "ENTER DOMAIN NAME:")
        if ok and name:
            if name not in self.vault_data:
                self.vault_data[name] = []
                self.refresh_groups()
                self.group_list.setCurrentText(name)
                self.save_vault()

    def save_entry(self):
        domain = self.group_list.currentText()
        if not domain:
            QMessageBox.warning(self, "WARN", "SELECT OR CREATE A DOMAIN FIRST")
            return
            
        u = self.u_input.text()
        p = self.p_input.text()
        
        if u and p:
            self.vault_data[domain].append({"u": u, "p": p})
            self.u_input.clear()
            self.p_input.clear()
            self.save_vault()
            self.load_entries()
        else:
            QMessageBox.warning(self, "WARN", "FIELDS CANNOT BE EMPTY")

    def load_entries(self):
        # Clear existing
        while self.entries_layout.count():
            item = self.entries_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        domain = self.group_list.currentText()
        if domain in self.vault_data:
            for entry in self.vault_data[domain]:
                widget = PasswordEntry(entry['u'], entry['p'])
                self.entries_layout.addWidget(widget)

    def save_vault(self):
        data_str = json.dumps(self.vault_data)
        encrypted_bundle = CryptoManager.encrypt_data(data_str, self.master_password)
        with open(VAULT_FILE, "w") as f:
            json.dump(encrypted_bundle, f)

    def restart_app(self):
        os.execv(sys.executable, ['python'] + sys.argv)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    login = LoginWindow()
    main_win = None

    def start_main(pw, data):
        global main_win
        login.hide()
        main_win = MainWindow(pw, data)
        main_win.show()

    login.authenticated.connect(start_main)
    login.show()
    
    sys.exit(app.exec())
