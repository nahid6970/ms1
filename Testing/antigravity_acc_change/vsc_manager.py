import sys
import json
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QScrollArea, QFrame, QLineEdit, QFileDialog,
    QMessageBox, QDialog, QGraphicsDropShadowEffect, QCheckBox, 
    QDateTimeEdit, QComboBox, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QTimer, QDateTime, QDate, QTime
from PyQt6.QtGui import QColor, QFont, QIcon

# Crypto imports from Locker.py logic
# Ensure pycryptodome is installed: pip install pycryptodome
from Cryptodome.Cipher import AES
from Cryptodome.Protocol.KDF import PBKDF2

# Constants
TARGET_DIR = r"C:\Users\nahid\ms\ms1\Testing\Test"
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
            "password": "",
            "timer_enabled": False,
            "target_time": None # ISO format string
        }
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Edit Profile" if self.profile["name"] else "Add Profile")
        self.setFixedWidth(500)
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
            QLineEdit, QDateTimeEdit, QComboBox {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 8px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus, QDateTimeEdit:focus {
                border: 1px solid #3d5afe;
            }
            QCheckBox, QRadioButton {
                color: #b0b0b0;
                font-size: 14px;
                margin-top: 5px;
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

        # --- Locker Integration ---
        self.lock_checkbox = QCheckBox("Files are encrypted (.enc)")
        self.lock_checkbox.setChecked(self.profile.get("is_locked", False))
        layout.addWidget(self.lock_checkbox)

        self.password_label = QLabel("Encryption Password")
        self.password_input = QLineEdit(self.profile.get("password", ""))
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        
        # --- Timer Integration ---
        self.timer_checkbox = QCheckBox("Enable Countdown Timer")
        self.timer_checkbox.setChecked(self.profile.get("timer_enabled", False))
        layout.addWidget(self.timer_checkbox)
        
        self.timer_frame = QFrame()
        timer_layout = QVBoxLayout(self.timer_frame)
        timer_layout.setContentsMargins(0, 0, 0, 0)
        
        # 12/24 Hour format toggle
        format_layout = QHBoxLayout()
        self.radio_12h = QRadioButton("12-Hour")
        self.radio_24h = QRadioButton("24-Hour")
        self.radio_24h.setChecked(True) # Default
        self.radio_group = QButtonGroup(self)
        self.radio_group.addButton(self.radio_12h)
        self.radio_group.addButton(self.radio_24h)
        self.radio_group.buttonClicked.connect(self.update_time_format)
        
        format_layout.addWidget(QLabel("Format:"))
        format_layout.addWidget(self.radio_12h)
        format_layout.addWidget(self.radio_24h)
        format_layout.addStretch()
        timer_layout.addLayout(format_layout)
        
        timer_layout.addWidget(QLabel("Set Target Date & Time"))
        self.dt_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.dt_edit.setCalendarPopup(True)
        if self.profile.get("target_time"):
            self.dt_edit.setDateTime(QDateTime.fromString(self.profile["target_time"], Qt.DateFormat.ISODate))
        else:
            self.dt_edit.setDateTime(QDateTime.currentDateTime().addSecs(3600)) # Default +1h

        timer_layout.addWidget(self.dt_edit)
        layout.addWidget(self.timer_frame)

        # Signal connections
        self.lock_checkbox.toggled.connect(self.toggle_password_fields)
        self.timer_checkbox.toggled.connect(self.toggle_timer_fields)
        
        # Initial State
        self.toggle_password_fields(self.lock_checkbox.isChecked())
        self.toggle_timer_fields(self.timer_checkbox.isChecked())
        self.update_time_format()

        # Action Buttons
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

    def toggle_timer_fields(self, checked):
        self.timer_frame.setVisible(checked)
        self.adjustSize()

    def update_time_format(self):
        if self.radio_12h.isChecked():
            self.dt_edit.setDisplayFormat("dd MMM yyyy h:mm ap")
        else:
            self.dt_edit.setDisplayFormat("dd MMM yyyy HH:mm")

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
        
        self.profile["timer_enabled"] = self.timer_checkbox.isChecked()
        if self.timer_checkbox.isChecked():
            # Save as ISO format
            self.profile["target_time"] = self.dt_edit.dateTime().toString(Qt.DateFormat.ISODate)
        else:
            self.profile["target_time"] = None
            
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
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.init_ui()
        
        if self.profile.get("timer_enabled"):
            self.timer.start(1000)
            self.update_countdown() # Initial call

    def init_ui(self):
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setObjectName("profileCard")
        
        # Initial styling call (will be updated by timer)
        self.update_style()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Info Layout
        info_layout = QVBoxLayout()
        
        # Name Row
        name_row = QHBoxLayout()
        self.name_label = QLabel(self.profile["name"])
        self.name_label.setObjectName("nameLabel")
        name_row.addWidget(self.name_label)
        
        if self.profile.get("is_locked"):
            lock_label = QLabel("🔒")
            lock_label.setObjectName("lockIcon")
            name_row.addWidget(lock_label)
            
        # Countdown Label
        self.countdown_label = QLabel("")
        self.countdown_label.setObjectName("countdownLabel")
        self.countdown_label.setVisible(False)
        name_row.addWidget(self.countdown_label)
        
        name_row.addStretch()
        
        # Path Label
        self.path_label = QLabel(self.profile["path"])
        self.path_label.setObjectName("pathLabel")
        
        info_layout.addLayout(name_row)
        info_layout.addWidget(self.path_label)
        
        layout.addLayout(info_layout, 1)

        # Right side Action
        if self.profile.get("active", False):
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

    def update_countdown(self):
        target_str = self.profile.get("target_time")
        if not target_str:
            self.countdown_label.setVisible(False)
            return

        target_dt = QDateTime.fromString(target_str, Qt.DateFormat.ISODate)
        now_dt = QDateTime.currentDateTime()
        
        secs_left = now_dt.secsTo(target_dt)
        
        if secs_left > 0:
            days = secs_left // 86400
            hours = (secs_left % 86400) // 3600
            minutes = (secs_left % 3600) // 60
            
            time_str = ""
            if days > 0: time_str += f"{days}d "
            if hours > 0: time_str += f"{hours}h "
            time_str += f"{minutes}m" # Always show minutes, even if 0 if hours exist
            if time_str == "": time_str = "< 1m" # Minimal representation
            
            self.countdown_label.setText(f"⏳ {time_str}")
            self.countdown_label.setVisible(True)
            self.update_style(active_timer=True)
        else:
            self.countdown_label.setText("⏰ Expired")
            self.countdown_label.setVisible(True)
            self.update_style(active_timer=False)
            self.timer.stop()

    def update_style(self, active_timer=False):
        is_active = self.profile.get("active", False)
        
        # Base colors
        card_bg = "#1e1e1e"
        border = "1px solid #333333"
        hover_bg = "#252525"
        
        if is_active:
            # Blue Active Theme
            style = """
                #profileCard {
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2a2e42, stop:1 #1e2235);
                    border: 2px solid #3d5afe;
                    border-radius: 12px;
                }
            """
        elif active_timer:
            # Red Tint Theme for Active Counter
            style = """
                #profileCard {
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3c1e1e, stop:1 #2b1414);
                    border: 1px solid #ff5252;
                    border-radius: 12px;
                }
                #profileCard:hover {
                    background-color: #4a2525;
                }
            """
        else:
            # Default
            style = """
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
            
        self.setStyleSheet(style + """
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
                margin-left: 5px;
            }
            QLabel#countdownLabel {
                color: #ff5252;
                font-weight: bold;
                font-size: 13px;
                margin-left: 10px;
                background-color: #2b1414;
                padding: 2px 6px;
                border-radius: 4px;
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
            
            d_name = item
            is_encrypted_file = item.endswith(".enc")
            
            if is_locked and is_encrypted_file:
                # Remove .enc extension for target
                d_name = item[:-4]
            
            d = os.path.join(TARGET_DIR, d_name)

            if os.path.isfile(s):
                if is_locked and is_encrypted_file:
                    decrypted_data = decrypt_file_data(s, password)
                    with open(d, 'wb') as f:
                        f.write(decrypted_data)
                else:
                    shutil.copy2(s, d)
            elif os.path.isdir(s):
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
