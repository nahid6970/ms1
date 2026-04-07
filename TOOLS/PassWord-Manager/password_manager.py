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
    def __init__(self, entry, field_suggestions, parent=None):
        super().__init__(parent)
        self.setWindowTitle("EDIT CREDENTIALS")
        self.setFixedWidth(450)
        self.entry = entry.copy()
        self.field_suggestions = field_suggestions
        if "fields" not in self.entry:
            self.entry["fields"] = {}
        # Ensure Domain is in the fields by default for display
        if "Domain" not in self.entry["fields"]:
            self.entry["fields"]["Domain"] = ""
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        
        self.form = QFormLayout()
        self.u_input = QLineEdit(self.entry.get("u", ""))
        self.p_input = QLineEdit(self.entry.get("p", ""))
        self.form.addRow("USERNAME:", self.u_input)
        self.form.addRow("PASSWORD:", self.p_input)
        
        # Additional fields
        self.extra_fields_widgets = {}
        # We'll put Domain first if it exists
        if "Domain" in self.entry["fields"]:
             self.add_field_row("Domain", self.entry["fields"]["Domain"])
             
        for name, value in self.entry["fields"].items():
            if name != "Domain":
                self.add_field_row(name, value)

        self.layout.addLayout(self.form)

        # Add Field Section
        add_field_layout = QHBoxLayout()
        self.new_field_name = QLineEdit()
        self.new_field_name.setPlaceholderText("New Field Name")
        
        # Using clearer emoji-like icons
        add_field_btn = QPushButton("➕")
        add_field_btn.setFixedWidth(40)
        add_field_btn.setToolTip("Add new custom field")
        add_field_btn.clicked.connect(self.add_custom_field)
        
        self.suggest_btn = QPushButton("📋")
        self.suggest_btn.setFixedWidth(40)
        self.suggest_btn.setToolTip("Show suggested fields")
        self.suggest_btn.setStyleSheet(f"color: {CP_CYAN};")
        self.suggest_btn.clicked.connect(self.show_suggestions)
        
        add_field_layout.addWidget(QLabel("ADD FIELD:"))
        add_field_layout.addWidget(self.new_field_name)
        add_field_layout.addWidget(add_field_btn)
        add_field_layout.addWidget(self.suggest_btn)
        
        self.layout.addLayout(add_field_layout)
        
        btns = QHBoxLayout()
        save_btn = QPushButton("UPDATE")
        cancel_btn = QPushButton("CANCEL")
        
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        btns.addWidget(save_btn)
        btns.addWidget(cancel_btn)
        
        self.layout.addStretch()
        self.layout.addLayout(btns)

    def add_field_row(self, name, value):
        if name in self.extra_fields_widgets:
            return
            
        row_layout = QHBoxLayout()
        edit = QLineEdit(str(value))
        del_btn = QPushButton("X")
        del_btn.setFixedWidth(30)
        del_btn.setStyleSheet(f"color: {CP_RED};")
        
        self.extra_fields_widgets[name] = edit
        row_layout.addWidget(edit)
        row_layout.addWidget(del_btn)
        
        label = QLabel(f"{name.upper()}:")
        self.form.addRow(label, row_layout)
        
        def remove():
            self.form.removeRow(label)
            if name in self.extra_fields_widgets:
                del self.extra_fields_widgets[name]

        del_btn.clicked.connect(remove)

    def add_custom_field(self):
        name = self.new_field_name.text().strip()
        if name and name not in self.extra_fields_widgets and name.lower() not in ["u", "p"]:
            self.add_field_row(name, "")
            self.new_field_name.clear()
        elif not name:
            QMessageBox.warning(self, "WARN", "FIELD NAME CANNOT BE EMPTY")
        else:
            QMessageBox.warning(self, "WARN", "FIELD ALREADY EXISTS")

    def show_suggestions(self):
        from PyQt6.QtWidgets import QMenu
        from PyQt6.QtGui import QAction
        
        menu = QMenu(self)
        menu.setStyleSheet(f"background-color: {CP_PANEL}; color: {CP_TEXT}; border: 1px solid {CP_DIM};")
        
        for name in self.field_suggestions:
            if name not in self.extra_fields_widgets:
                action = QAction(name, self)
                action.triggered.connect(lambda checked, n=name: self.add_field_row(n, ""))
                menu.addAction(action)
        
        if menu.isEmpty():
            action = QAction("No suggestions", self)
            action.setEnabled(False)
            menu.addAction(action)
            
        menu.exec(self.suggest_btn.mapToGlobal(self.suggest_btn.rect().bottomLeft()))

    def get_data(self):
        data = {
            "u": self.u_input.text(),
            "p": self.p_input.text(),
            "fields": {name: edit.text() for name, edit in self.extra_fields_widgets.items()}
        }
        return data

class PasswordEntry(QFrame):
    edit_requested = pyqtSignal()
    delete_requested = pyqtSignal()
    
    def __init__(self, entry, domain, parent=None):
        super().__init__(parent)
        self.entry = entry
        self.domain = domain
        self.is_expanded = False
        self.init_ui()

    def init_ui(self):
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"border: 1px solid {CP_DIM}; background: {CP_PANEL}; margin: 2px; padding: 5px;")
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(0)

        # Top Row: Info and Main Actions
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(5, 5, 5, 5)
        
        info_layout = QVBoxLayout()
        # Show domain in entry if it's from search
        domain_str = f" [{self.domain}]" if self.domain else ""
        user_lbl = QLabel(f"USER: {self.entry.get('u', '')}{domain_str}")
        pass_lbl = QLabel(f"PASS: {'*' * len(self.entry.get('p', ''))}")
        user_lbl.setStyleSheet(f"color: {CP_TEXT}; border: none; font-weight: bold;")
        pass_lbl.setStyleSheet(f"color: {CP_SUBTEXT}; border: none;")
        info_layout.addWidget(user_lbl)
        info_layout.addWidget(pass_lbl)
        
        top_layout.addLayout(info_layout)
        top_layout.addStretch()
        
        self.edit_btn = QPushButton("EDIT")
        self.del_btn = QPushButton("DEL")
        self.del_btn.setStyleSheet(f"color: {CP_RED}; border-color: {CP_DIM};")
        copy_user_btn = QPushButton("USER")
        copy_pass_btn = QPushButton("PASS")
        
        for btn in [self.edit_btn, self.del_btn, copy_user_btn, copy_pass_btn]:
            if btn == self.del_btn: btn.setFixedWidth(40)
            elif btn == self.edit_btn: btn.setFixedWidth(50)
            else: btn.setFixedWidth(55)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
        self.edit_btn.clicked.connect(self.edit_requested.emit)
        self.del_btn.clicked.connect(self.delete_requested.emit)
        copy_user_btn.clicked.connect(lambda: self.copy_to_clipboard(self.entry.get('u', '')))
        copy_pass_btn.clicked.connect(lambda: self.copy_to_clipboard(self.entry.get('p', '')))
        
        top_layout.addWidget(copy_user_btn)
        top_layout.addWidget(copy_pass_btn)
        top_layout.addWidget(self.edit_btn)
        top_layout.addWidget(self.del_btn)
        
        self.main_layout.addWidget(top_widget)

        # Toggle Button Row (Below the main info)
        toggle_container = QWidget()
        toggle_layout = QHBoxLayout(toggle_container)
        toggle_layout.setContentsMargins(0, 0, 0, 0)
        
        self.toggle_btn = QPushButton("▼ SHOW DETAILS ▼")
        self.toggle_btn.setStyleSheet(f"""
            QPushButton {{
                border: none; 
                color: {CP_SUBTEXT}; 
                font-size: 8pt; 
                background: transparent;
            }}
            QPushButton:hover {{
                color: {CP_CYAN};
            }}
        """)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.clicked.connect(self.toggle_expand)
        
        toggle_layout.addStretch()
        toggle_layout.addWidget(self.toggle_btn)
        toggle_layout.addStretch()
        
        self.main_layout.addWidget(toggle_container)

        # Expanded Area
        self.extra_widget = QWidget()
        self.extra_layout = QFormLayout(self.extra_widget)
        self.extra_layout.setContentsMargins(20, 5, 20, 10)
        self.extra_widget.setVisible(False)
        
        fields = self.entry.get("fields", {})
        for name, value in fields.items():
            lbl = QLabel(f"{name.upper()}:")
            lbl.setStyleSheet(f"color: {CP_YELLOW}; border: none;")
            val_lbl = QLineEdit(str(value))
            val_lbl.setReadOnly(True)
            val_lbl.setStyleSheet(f"background: {CP_BG}; border: 1px solid {CP_DIM}; color: {CP_TEXT}; padding: 2px;")
            
            copy_btn = QPushButton("COPY")
            copy_btn.setFixedWidth(50)
            copy_btn.setStyleSheet("font-size: 8pt; padding: 2px;")
            copy_btn.clicked.connect(lambda checked, v=value: self.copy_to_clipboard(str(v)))
            
            row = QHBoxLayout()
            row.addWidget(val_lbl)
            row.addWidget(copy_btn)
            
            self.extra_layout.addRow(lbl, row)

        self.main_layout.addWidget(self.extra_widget)

    def toggle_expand(self):
        self.is_expanded = not self.is_expanded
        self.toggle_btn.setText("▲ HIDE DETAILS ▲" if self.is_expanded else "▼ SHOW DETAILS ▼")
        self.extra_widget.setVisible(self.is_expanded)

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
        
        # Global Search
        sidebar_layout.addWidget(QLabel("GLOBAL SEARCH:"))
        self.global_search = QLineEdit()
        self.global_search.setPlaceholderText("SEARCH ALL FIELDS...")
        self.global_search.setStyleSheet(f"border-color: {CP_CYAN};")
        self.global_search.textChanged.connect(self.load_entries)
        sidebar_layout.addWidget(self.global_search)
        
        sidebar_layout.addSpacing(10)
        sidebar_layout.addWidget(QLabel("SELECT DOMAIN:"))
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
        add_vbox = QVBoxLayout()
        add_form = QFormLayout()
        self.u_input = QLineEdit()
        self.p_input = QLineEdit()
        self.d_input = QLineEdit()
        self.p_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.d_input.setPlaceholderText("Optional Domain (e.g. google.com)")
        
        add_form.addRow("USERNAME:", self.u_input)
        add_form.addRow("PASSWORD:", self.p_input)
        add_form.addRow("DOMAIN:", self.d_input)
        
        add_vbox.addLayout(add_form)
        
        add_btn = QPushButton("SAVE TO VAULT")
        add_btn.clicked.connect(self.save_entry)
        add_vbox.addWidget(add_btn)
        
        add_grp.setLayout(add_vbox)
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
        search_layout.addWidget(QLabel("VAULT ENTRIES:"))
        search_layout.addStretch()
        
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
        domain_grp = self.group_list.currentText()
        if not domain_grp:
            QMessageBox.warning(self, "WARN", "SELECT OR CREATE A DOMAIN FIRST")
            return
            
        u = self.u_input.text()
        p = self.p_input.text()
        d = self.d_input.text().strip()
        
        if u and p:
            fields = {}
            if d:
                fields["Domain"] = d
                
            self.vault_data[domain_grp].append({"u": u, "p": p, "fields": fields})
            self.u_input.clear()
            self.p_input.clear()
            self.d_input.clear()
            self.p_input.setEchoMode(QLineEdit.EchoMode.Password) # Reset echo mode
            self.save_vault()
            self.load_entries()
        else:
            QMessageBox.warning(self, "WARN", "FIELDS CANNOT BE EMPTY")

    def get_all_field_names(self):
        names = set()
        # Default common fields
        names.update(["Note", "Phone", "Domain"])
        for group in self.vault_data.values():
            for entry in group:
                fields = entry.get("fields", {})
                names.update(fields.keys())
        return sorted(list(names))

    def load_entries(self):
        # Clear existing
        while self.entries_layout.count():
            item = self.entries_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        current_domain = self.group_list.currentText()
        global_search = self.global_search.text().lower()
        
        # Determine which domains to search
        search_scope = {}
        if global_search:
            # Global search looks through EVERYTHING
            search_scope = self.vault_data
        elif current_domain in self.vault_data:
            # Show current domain if no global search
            search_scope = {current_domain: self.vault_data[current_domain]}
        
        for domain, entries in search_scope.items():
            for i, entry in enumerate(entries):
                # Search logic: check all available text fields
                all_text = [
                    entry.get('u', '').lower(),
                    entry.get('p', '').lower(),
                    domain.lower()
                ]
                for f_val in entry.get('fields', {}).values():
                    all_text.append(str(f_val).lower())
                
                combined_text = " ".join(all_text)
                
                # Apply filter
                if global_search and global_search not in combined_text:
                    continue
                
                widget = PasswordEntry(entry, domain)
                widget.edit_requested.connect(lambda d=domain, idx=i: self.edit_specific_entry(d, idx))
                widget.delete_requested.connect(lambda d=domain, idx=i: self.delete_specific_entry(d, idx))
                self.entries_layout.addWidget(widget)

    def delete_specific_entry(self, domain, index):
        if QMessageBox.question(self, "CONFIRM", f"DELETE THIS CREDENTIAL FROM {domain}?", 
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            del self.vault_data[domain][index]
            self.save_vault()
            self.load_entries()

    def edit_specific_entry(self, domain, index):
        entry = self.vault_data[domain][index]
        suggestions = self.get_all_field_names()
        
        dlg = EditDialog(entry, suggestions, self)
        dlg.setStyleSheet(self.get_stylesheet())
        
        if dlg.exec():
            new_data = dlg.get_data()
            if new_data["u"] and new_data["p"]:
                self.vault_data[domain][index] = new_data
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
