import sys
import json
import os
import shutil
import tempfile
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QScrollArea, QFrame, QLineEdit, QFileDialog,
    QMessageBox, QDialog, QGraphicsDropShadowEffect, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QColor, QFont, QIcon

# Crypto imports from Locker.py logic
from Cryptodome.Cipher import AES
from Cryptodome.Protocol.KDF import PBKDF2

# Constants
TARGET_DIR = r"C:\Users\nahid\AppData\Roaming\Antigravity\User\globalStorage"
FILES_TO_DELETE = ["state.vscdb", "state.vscdb.backup"]
JSON_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "profiles.json")

def derive_key(password, salt, key_length=32):
    return PBKDF2(password.encode(), salt, dkLen=key_length)

def decrypt_file_data(file_path, password):
    """Decrypts a file using the logic from Locker.py and returns the bytes."""
    try:
        with open(file_path, 'rb') as f:
            salt, tag, nonce, ciphertext = [f.read(x) for x in (16, 16, 16, -1)]
        
        key = derive_key(password, salt)
        cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        return plaintext
    except (ValueError, KeyError):
        raise Exception("Decryption failed. Incorrect password or corrupted file.")
    except Exception as e:
        raise Exception(f"Decryption error: {str(e)}")

class ProfileDialog(QDialog):
    def __init__(self, parent=None, profile=None):
        super().__init__(parent)
        self.profile = profile or {
            "name": "", 
            "path": "", 
            "active": False,
            "is_locked": False,
            "password": ""
        }
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Edit Profile" if self.profile["name"] else "Add Profile")
        self.setFixedWidth(450)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: white;
            }
            QLabel {
                color: #b0b0b0;
                font-size: 14px;
                margin-top: 10px;
            }
            QLineEdit {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 8px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #3d5afe;
            }
            QCheckBox {
                color: #b0b0b0;
                font-size: 14px;
                margin-top: 10px;
            }
            QPushButton {
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            #saveBtn {
                background-color: #3d5afe;
                color: white;
            }
            #saveBtn:hover {
                background-color: #536dfe;
            }
            #cancelBtn {
                background-color: #3d3d3d;
                color: white;
            }
            #cancelBtn:hover {
                background-color: #4d4d4d;
            }
            #browseBtn {
                background-color: #3d3d3d;
                color: white;
                padding: 8px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(25, 25, 25, 25)

        layout.addWidget(QLabel("Profile Name"))
        self.name_input = QLineEdit(self.profile["name"])
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Source Path"))
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit(self.profile["path"])
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.setObjectName("browseBtn")
        self.browse_btn.clicked.connect(self.browse_path)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_btn)
        layout.addLayout(path_layout)

        # Locker Integration
        self.lock_checkbox = QCheckBox("Files are encrypted (.enc)")
        self.lock_checkbox.setChecked(self.profile.get("is_locked", False))
        layout.addWidget(self.lock_checkbox)

        self.password_label = QLabel("Encryption Password")
        self.password_input = QLineEdit(self.profile.get("password", ""))
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        # Toggle password visibility based on checkbox
        self.lock_checkbox.toggled.connect(self.toggle_password_fields)
        self.toggle_password_fields(self.lock_checkbox.isChecked())

        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 20, 0, 0)
        self.save_btn = QPushButton("Save Profile")
        self.save_btn.setObjectName("saveBtn")
        self.save_btn.clicked.connect(self.save)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)

    def toggle_password_fields(self, checked):
        self.password_label.setVisible(checked)
        self.password_input.setVisible(checked)
        self.adjustSize()

    def browse_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Source Directory")
        if path:
            self.path_input.setText(path)

    def save(self):
        if not self.name_input.text() or not self.path_input.text():
            QMessageBox.warning(self, "Error", "Name and Path are required!")
            return
        
        if self.lock_checkbox.isChecked() and not self.password_input.text():
            QMessageBox.warning(self, "Error", "Password is required for encrypted files!")
            return

        self.profile["name"] = self.name_input.text()
        self.profile["path"] = self.path_input.text()
        self.profile["is_locked"] = self.lock_checkbox.isChecked()
        self.profile["password"] = self.password_input.text() if self.lock_checkbox.isChecked() else ""
        self.accept()

    def get_data(self):
        return self.profile

class ProfileCard(QFrame):
    clicked = pyqtSignal(dict)
    edit_clicked = pyqtSignal(dict)
    delete_clicked = pyqtSignal(dict)

    def __init__(self, profile):
        super().__init__()
        self.profile = profile
        self.init_ui()

    def init_ui(self):
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setObjectName("profileCard")
        
        is_active = self.profile.get("active", False)
        is_locked = self.profile.get("is_locked", False)
        
        active_style = """
            #profileCard {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2a2e42, stop:1 #1e2235);
                border: 2px solid #3d5afe;
                border-radius: 12px;
            }
        """ if is_active else """
            #profileCard {
                background-color: #1e1e1e;
                border: 1px solid #333333;
                border-radius: 12px;
            }
            #profileCard:hover {
                background-color: #252525;
                border: 1px solid #444444;
            }
        """

        self.setStyleSheet(active_style + """
            QLabel#nameLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QLabel#pathLabel {
                color: #808080;
                font-size: 12px;
            }
            QLabel#lockIcon {
                color: #e06c75;
                font-size: 14px;
            }
            QPushButton#actionBtn {
                background-color: transparent;
                color: #b0b0b0;
                border: none;
                font-size: 14px;
            }
            QPushButton#actionBtn:hover {
                color: white;
            }
            QPushButton#activateBtn {
                background-color: #3d5afe;
                color: white;
                border-radius: 6px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton#activateBtn:disabled {
                background-color: #2d2d2d;
                color: #666666;
            }
            #statusLabel {
                color: #3d5afe;
                font-weight: bold;
                font-size: 12px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Info Layout
        info_layout = QVBoxLayout()
        
        name_row = QHBoxLayout()
        self.name_label = QLabel(self.profile["name"])
        self.name_label.setObjectName("nameLabel")
        name_row.addWidget(self.name_label)
        
        if is_locked:
            lock_label = QLabel("🔒 Locked")
            lock_label.setObjectName("lockIcon")
            name_row.addWidget(lock_label)
        
        name_row.addStretch()
        
        self.path_label = QLabel(self.profile["path"])
        self.path_label.setObjectName("pathLabel")
        
        info_layout.addLayout(name_row)
        info_layout.addWidget(self.path_label)
        
        layout.addLayout(info_layout, 1)

        # Status or Activate button
        if is_active:
            status_label = QLabel("ACTIVE")
            status_label.setObjectName("statusLabel")
            layout.addWidget(status_label)
        else:
            self.activate_btn = QPushButton("Activate")
            self.activate_btn.setObjectName("activateBtn")
            self.activate_btn.clicked.connect(lambda: self.clicked.emit(self.profile))
            layout.addWidget(self.activate_btn)

        # Edit/Delete Buttons
        self.edit_btn = QPushButton("✎")
        self.edit_btn.setObjectName("actionBtn")
        self.edit_btn.clicked.connect(lambda: self.edit_clicked.emit(self.profile))
        
        self.delete_btn = QPushButton("✕")
        self.delete_btn.setObjectName("actionBtn")
        self.delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self.profile))

        layout.addWidget(self.edit_btn)
        layout.addWidget(self.delete_btn)

class VSCodeStateManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.profiles = []
        self.load_profiles()
        self.init_ui()

    def load_profiles(self):
        if os.path.exists(JSON_FILE):
            try:
                with open(JSON_FILE, 'r') as f:
                    self.profiles = json.load(f)
            except:
                self.profiles = []
        else:
            self.profiles = []

    def save_profiles(self):
        with open(JSON_FILE, 'w') as f:
            json.dump(self.profiles, f, indent=4)

    def init_ui(self):
        self.setWindowTitle("VS Code State Manager & Unlocker")
        self.setMinimumSize(650, 750)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            #scrollWidget {
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #121212;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #333333;
                min-height: 20px;
                border-radius: 5px;
            }
            #headerLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                padding: 20px;
            }
            #addBtn {
                background-color: #3d5afe;
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                margin: 20px;
            }
            #addBtn:hover {
                background-color: #536dfe;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("Profiles")
        header_label.setObjectName("headerLabel")
        
        self.add_btn = QPushButton("+ Add Profile")
        self.add_btn.setObjectName("addBtn")
        self.add_btn.clicked.connect(self.add_profile)
        
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(self.add_btn)
        main_layout.addLayout(header_layout)

        # Scroll Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_widget.setObjectName("scrollWidget")
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_layout.setSpacing(15)
        
        self.scroll.setWidget(self.scroll_widget)
        main_layout.addWidget(self.scroll)

        self.refresh_list()

    def refresh_list(self):
        for i in reversed(range(self.scroll_layout.count())): 
            widget = self.scroll_layout.itemAt(i).widget()
            if widget: widget.setParent(None)

        if not self.profiles:
            empty_label = QLabel("No profiles added yet. Click '+ Add Profile' to start.")
            empty_label.setStyleSheet("color: #666666; font-style: italic; margin-top: 50px;")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.scroll_layout.addWidget(empty_label)
            return

        for profile in self.profiles:
            card = ProfileCard(profile)
            card.clicked.connect(self.activate_profile)
            card.edit_clicked.connect(self.edit_profile)
            card.delete_clicked.connect(self.delete_profile)
            self.scroll_layout.addWidget(card)

    def add_profile(self):
        dialog = ProfileDialog(self)
        if dialog.exec():
            new_profile = dialog.get_data()
            new_profile["active"] = False
            self.profiles.append(new_profile)
            self.save_profiles()
            self.refresh_list()

    def edit_profile(self, profile):
        dialog = ProfileDialog(self, profile.copy())
        if dialog.exec():
            updated_profile = dialog.get_data()
            index = self.profiles.index(profile)
            self.profiles[index] = updated_profile
            self.save_profiles()
            self.refresh_list()

    def delete_profile(self, profile):
        reply = QMessageBox.question(self, 'Delete Profile', 
                                    f"Are you sure you want to delete '{profile['name']}'?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.profiles.remove(profile)
            self.save_profiles()
            self.refresh_list()

    def activate_profile(self, profile):
        try:
            # Execute activation with decryption if needed
            self.execute_activation(profile)
            
            # Update status
            for p in self.profiles:
                p["active"] = (p == profile)
            
            self.save_profiles()
            self.refresh_list()
            
            QMessageBox.information(self, "Success", f"Profile '{profile['name']}' activated successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to activate: {str(e)}")

    def execute_activation(self, profile):
        source_path = profile["path"]
        is_locked = profile.get("is_locked", False)
        password = profile.get("password", "")

        if not os.path.exists(source_path):
            raise Exception(f"Source path does not exist: {source_path}")

        if not os.path.exists(TARGET_DIR):
            os.makedirs(TARGET_DIR)

        # Delete target files
        for filename in FILES_TO_DELETE:
            target_file = os.path.join(TARGET_DIR, filename)
            if os.path.exists(target_file):
                os.remove(target_file)

        # Copy and Decrypt if necessary
        for item in os.listdir(source_path):
            s = os.path.join(source_path, item)
            
            # Determine destination filename
            d_name = item
            is_encrypted_file = item.endswith(".enc")
            
            if is_locked and is_encrypted_file:
                # Remove .enc extension for target
                d_name = item[:-4]
            
            d = os.path.join(TARGET_DIR, d_name)

            if os.path.isfile(s):
                if is_locked and is_encrypted_file:
                    # Decrypt in memory and write to target
                    decrypted_data = decrypt_file_data(s, password)
                    with open(d, 'wb') as f:
                        f.write(decrypted_data)
                else:
                    # Normal copy
                    shutil.copy2(s, d)
            elif os.path.isdir(s):
                # Recursive directory copy (not decrypting within subdirs for now as per usual vscdb structure)
                if os.path.exists(d):
                    shutil.rmtree(d)
                shutil.copytree(s, d)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = VSCodeStateManager()
    window.show()
    sys.exit(app.exec())
