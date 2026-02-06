import sys
import os
import json
import base64
import secrets
import string
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QGroupBox, QFormLayout,
    QScrollArea, QFrame, QMessageBox, QComboBox, QInputDialog,
    QCheckBox, QSlider, QDialog
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

VAULT_DIR = r"C:\@delta\db\password-manager"
VAULT_FILE = os.path.join(VAULT_DIR, "vault.json")

# Ensure the vault directory exists
if not os.path.exists(VAULT_DIR):
    try:
        os.makedirs(VAULT_DIR, exist_ok=True)
    except Exception:
        pass

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

class EditDialog(QDialog):
    def __init__(self, username, password, parent=None):
        super().__init__(parent)
        self.setWindowTitle("EDIT CREDENTIALS")
        self.setFixedWidth(350)
        self.init_ui(username, password)

    def init_ui(self, u, p):
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        self.u_input = QLineEdit(u)
        self.p_input = QLineEdit(p)
        form.addRow("USERNAME:", self.u_input)
        form.addRow("PASSWORD:", self.p_input)
        
        btns = QHBoxLayout()
        save_btn = QPushButton("UPDATE")
        cancel_btn = QPushButton("CANCEL")
        
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        btns.addWidget(save_btn)
        btns.addWidget(cancel_btn)
        
        layout.addLayout(form)
        layout.addLayout(btns)

    def get_data(self):
        return self.u_input.text(), self.p_input.text()

class PasswordEntry(QFrame):
    edit_requested = pyqtSignal()
    delete_requested = pyqtSignal()
    
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
        
        self.edit_btn = QPushButton("EDIT")
        self.del_btn = QPushButton("DEL")
        self.del_btn.setStyleSheet(f"color: {CP_RED}; border-color: {CP_DIM};")
        copy_user_btn = QPushButton("COPY USER")
        copy_pass_btn = QPushButton("COPY PASS")
        
        for btn in [self.edit_btn, self.del_btn, copy_user_btn, copy_pass_btn]:
            if btn == self.del_btn: btn.setFixedWidth(40)
            elif btn == self.edit_btn: btn.setFixedWidth(60)
            else: btn.setFixedWidth(100)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
        self.edit_btn.clicked.connect(self.edit_requested.emit)
        self.del_btn.clicked.connect(self.delete_requested.emit)
        copy_user_btn.clicked.connect(lambda: self.copy_to_clipboard(self.username))
        copy_pass_btn.clicked.connect(lambda: self.copy_to_clipboard(self.password))
        
        layout.addWidget(self.edit_btn)
        layout.addWidget(self.del_btn)
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
            
            QCheckBox {{ spacing: 8px; color: {CP_TEXT}; }}
            QCheckBox::indicator {{ width: 14px; height: 14px; border: 1px solid {CP_DIM}; background: {CP_PANEL}; }}
            QCheckBox::indicator:checked {{ background: {CP_YELLOW}; border-color: {CP_YELLOW}; }}
            
            QSlider::groove:horizontal {{ border: 1px solid {CP_DIM}; height: 4px; background: {CP_PANEL}; margin: 2px 0; }}
            QSlider::handle:horizontal {{ background: {CP_CYAN}; border: 1px solid {CP_CYAN}; width: 10px; margin: -5px 0; }}
        """

    def toggle_generator(self):
        if self.gen_toggle_btn.isChecked():
            self.gen_toggle_btn.setText("▼ HIDE GENERATOR")
            self.gen_container.setVisible(True)
        else:
            self.gen_toggle_btn.setText("▶ SHOW GENERATOR")
            self.gen_container.setVisible(False)

    def generate_password(self):
        chars = string.ascii_lowercase
        if self.use_upper.isChecked(): chars += string.ascii_uppercase
        if self.use_nums.isChecked(): chars += string.digits
        if self.use_syms.isChecked(): chars += string.punctuation
        
        length = self.len_slider.value()
        password = "".join(secrets.choice(chars) for _ in range(length))
        self.p_input.setText(password)
        self.p_input.setEchoMode(QLineEdit.EchoMode.Normal) # Show it so user sees what was generated

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

        # Password Generator
        gen_grp = QGroupBox("PASSWORD GENERATOR")
        gen_main_layout = QVBoxLayout()
        
        self.gen_toggle_btn = QPushButton("▶ SHOW GENERATOR")
        self.gen_toggle_btn.setCheckable(True)
        self.gen_toggle_btn.clicked.connect(self.toggle_generator)
        self.gen_toggle_btn.setStyleSheet(f"text-align: left; color: {CP_CYAN}; border: none; background: transparent;")
        
        self.gen_container = QWidget()
        gen_layout = QVBoxLayout(self.gen_container)
        
        options_layout = QHBoxLayout()
        self.len_label = QLabel("LENGTH: 16")
        self.len_slider = QSlider(Qt.Orientation.Horizontal)
        self.len_slider.setRange(8, 64)
        self.len_slider.setValue(16)
        self.len_slider.valueChanged.connect(lambda v: self.len_label.setText(f"LENGTH: {v}"))
        
        self.use_nums = QCheckBox("123")
        self.use_syms = QCheckBox("!@#")
        self.use_upper = QCheckBox("ABC")
        self.use_nums.setChecked(True)
        self.use_syms.setChecked(True)
        self.use_upper.setChecked(True)
        
        options_layout.addWidget(self.len_label)
        options_layout.addWidget(self.len_slider)
        options_layout.addWidget(self.use_nums)
        options_layout.addWidget(self.use_syms)
        options_layout.addWidget(self.use_upper)
        
        gen_btn = QPushButton("GENERATE & FILL")
        gen_btn.clicked.connect(self.generate_password)
        
        gen_layout.addLayout(options_layout)
        gen_layout.addWidget(gen_btn)
        
        self.gen_container.setVisible(False)
        
        gen_main_layout.addWidget(self.gen_toggle_btn)
        gen_main_layout.addWidget(self.gen_container)
        gen_grp.setLayout(gen_main_layout)
        content_layout.addWidget(gen_grp)

        # Entries List
        self.scroll = QScrollArea()
        self.scroll_content = QWidget()
        self.entries_layout = QVBoxLayout(self.scroll_content)
        self.entries_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        self.scroll.setWidgetResizable(True)
        
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("SEARCH BY USERNAME...")
        self.search_input.textChanged.connect(self.load_entries)
        search_layout.addWidget(QLabel("VAULT ENTRIES:"))
        search_layout.addStretch()
        search_layout.addWidget(self.search_input)
        
        content_layout.addLayout(search_layout)
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
            self.p_input.setEchoMode(QLineEdit.EchoMode.Password) # Reset echo mode
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
        search_query = self.search_input.text().lower()
        
        if domain in self.vault_data:
            for i, entry in enumerate(self.vault_data[domain]):
                if search_query and search_query not in entry['u'].lower():
                    continue
                    
                widget = PasswordEntry(entry['u'], entry['p'])
                widget.edit_requested.connect(lambda idx=i: self.edit_entry(idx))
                widget.delete_requested.connect(lambda idx=i: self.delete_entry(idx))
                self.entries_layout.addWidget(widget)

    def delete_entry(self, index):
        domain = self.group_list.currentText()
        if QMessageBox.question(self, "CONFIRM", "DELETE THIS CREDENTIAL?", 
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            del self.vault_data[domain][index]
            self.save_vault()
            self.load_entries()

    def edit_entry(self, index):
        domain = self.group_list.currentText()
        entry = self.vault_data[domain][index]
        
        dlg = EditDialog(entry['u'], entry['p'], self)
        # Apply the same theme to dialog
        dlg.setStyleSheet(self.get_stylesheet())
        
        if dlg.exec():
            new_u, new_p = dlg.get_data()
            if new_u and new_p:
                self.vault_data[domain][index] = {"u": new_u, "p": new_p}
                self.save_vault()
                self.load_entries()
            else:
                QMessageBox.warning(self, "WARN", "FIELDS CANNOT BE EMPTY")

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
