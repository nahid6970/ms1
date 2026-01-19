import sys
import json
import os
import ctypes
import subprocess
import shutil
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QLineEdit, QGroupBox, QFormLayout, 
                             QDialog, QMessageBox, QScrollArea, QFrame, QComboBox, QSizePolicy, QFileDialog)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon, QColor

# ==========================================
# CYBERPUNK THEME PALETTE & STYLESHEET
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

# Global Stylesheet
STYLESHEET = f"""
    QMainWindow, QDialog {{
        background-color: {CP_BG};
    }}
    QWidget {{
        color: {CP_TEXT};
        font-family: 'Consolas';
        font-size: 10pt;
    }}
    
    /* INPUT FIELDS */
    QLineEdit, QSpinBox, QComboBox, QPlainTextEdit, QTextEdit {{
        background-color: {CP_PANEL};
        color: {CP_CYAN};
        border: 1px solid {CP_DIM};
        padding: 4px;
        selection-background-color: {CP_CYAN};
        selection-color: #000000;
    }}
    QLineEdit:focus, QComboBox:focus {{
        border: 1px solid {CP_CYAN};
    }}
    
    /* BUTTONS */
    QPushButton {{
        background-color: {CP_DIM};
        border: 1px solid {CP_DIM};
        color: white;
        padding: 6px 12px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: #2a2a2a;
        border: 1px solid {CP_YELLOW};
        color: {CP_YELLOW};
    }}
    QPushButton:pressed {{
        background-color: {CP_YELLOW};
        color: black;
    }}
    
    /* GROUP BOX */
    QGroupBox {{
        border: 1px solid {CP_DIM};
        margin-top: 10px;
        padding-top: 10px;
        font-weight: bold;
        color: {CP_YELLOW};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 5px;
    }}
    
    /* SCROLL AREA */
    QScrollArea {{
        background: transparent;
        border: none;
    }}
    QScrollBar:vertical {{
        border: none;
        background: {CP_PANEL};
        width: 10px;
        margin: 0px 0px 0px 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {CP_DIM};
        min-height: 20px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        background: none;
    }}
"""

# ==========================================
# HELPER CLASSES
# ==========================================

class AddLinkDialog(QDialog):
    def __init__(self, parent, on_save_callback, edit_data=None):
        super().__init__(parent)
        self.on_save_callback = on_save_callback
        self.edit_data = edit_data
        
        self.setWindowTitle("Edit Symlink" if edit_data else "Add New Symlink")
        self.resize(700, 350)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Title
        title = QLabel("Edit Entry" if edit_data else "New Entry")
        title.setStyleSheet(f"font-size: 14pt; font-weight: bold; color: {CP_YELLOW};")
        layout.addWidget(title)

        # Content Form
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setContentsMargins(0, 20, 0, 0) # Top margin only
        
        # Name
        self.name_entry = QLineEdit()
        self.name_entry.setPlaceholderText("e.g. My Project Data")
        form_layout.addRow("Name:", self.name_entry)

        # Type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["folder", "file"])
        form_layout.addRow("Type:", self.type_combo)

        # Target Path (Real)
        target_layout = QHBoxLayout()
        self.target_entry = QLineEdit()
        self.target_entry.setPlaceholderText("Absolute path to source")
        target_btn = QPushButton("📂 Target")
        target_btn.setFixedWidth(100)
        target_btn.setStyleSheet(f"color: white; border: 1px solid #3498db;") # Blueish override
        target_btn.clicked.connect(self.browse_target)
        target_layout.addWidget(target_btn)
        target_layout.addWidget(self.target_entry)
        form_layout.addRow("Target Path:", target_layout)

        # Fake Path (Link)
        fake_layout = QHBoxLayout()
        self.fake_entry = QLineEdit()
        self.fake_entry.setPlaceholderText("Where the link should be created")
        fake_btn = QPushButton("📂 Link")
        fake_btn.setFixedWidth(100)
        fake_btn.setStyleSheet(f"color: white; border: 1px solid #9b59b6;") # Purpleish override
        fake_btn.clicked.connect(self.browse_fake)
        fake_layout.addWidget(fake_btn)
        fake_layout.addWidget(self.fake_entry)
        form_layout.addRow("Link Path:", fake_layout)

        layout.addWidget(form_widget)
        
        # Spacer to push everything up
        layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Save Changes" if edit_data else "Create Entry")
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {CP_DIM}; 
                border: 1px solid {CP_GREEN}; 
                color: {CP_GREEN};
            }}
            QPushButton:hover {{
                background-color: {CP_GREEN}; 
                color: black;
            }}
        """)
        save_btn.clicked.connect(self.save_link)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

        # Pre-fill
        if edit_data:
            self.name_entry.setText(edit_data.get("name", ""))
            self.target_entry.setText(edit_data.get("target", ""))
            self.fake_entry.setText(edit_data.get("fake", ""))
            self.type_combo.setCurrentText(edit_data.get("type", "folder"))

    def browse_target(self):
        if self.type_combo.currentText() == "folder":
            path = QFileDialog.getExistingDirectory(self, "Select Target Folder")
        else:
            path, _ = QFileDialog.getOpenFileName(self, "Select Target File")
        if path:
            self.target_entry.setText(os.path.normpath(path))

    def browse_fake(self):
        if self.type_combo.currentText() == "folder":
            path = QFileDialog.getExistingDirectory(self, "Select Link Directory")
        else:
            path, _ = QFileDialog.getSaveFileName(self, "Select Link File Location")
        if path:
            self.fake_entry.setText(os.path.normpath(path))

    def save_link(self):
        name = self.name_entry.text().strip()
        target = self.target_entry.text().strip()
        fake = self.fake_entry.text().strip()
        link_type = self.type_combo.currentText()

        if not name or not target or not fake:
            QMessageBox.warning(self, "Incomplete", "Please fill all fields.")
            return

        self.on_save_callback(name, target, fake, link_type)
        self.accept()

# ==========================================
# MAIN APPLICATION
# ==========================================

class SymlinkManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cyberpunk Symlink Manager")
        self.resize(1000, 600)
        
        self.data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "links.json")
        self.links = self.load_data()

        # Central Widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # Header
        header_layout = QHBoxLayout()
        
        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("Search symlinks...")
        self.search_entry.textChanged.connect(self.refresh_ui)
        
        add_btn = QPushButton("➕ Add Link")
        add_btn.setFixedWidth(120)
        add_btn.setStyleSheet(f"border-color: {CP_GREEN}; color: {CP_GREEN};")
        add_btn.clicked.connect(self.open_add_dialog)

        header_layout.addWidget(self.search_entry)
        header_layout.addWidget(add_btn)
        main_layout.addLayout(header_layout)

        # Scroll Area for List
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_layout.setSpacing(10)
        self.scroll.setWidget(self.scroll_content)
        
        main_layout.addWidget(self.scroll)

        # Status Bar
        self.status_bar = QLabel("System Ready...")
        self.status_bar.setStyleSheet(f"color: {CP_SUBTEXT}; font-size: 9pt;")
        main_layout.addWidget(self.status_bar)

        self.refresh_ui()

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_data(self):
        with open(self.data_file, "w") as f:
            json.dump(self.links, f, indent=4)

    def open_add_dialog(self):
        AddLinkDialog(self, self.on_link_added).exec()

    def on_link_added(self, name, target, fake, link_type):
        self.links.append({
            "name": name,
            "target": target,
            "fake": fake,
            "type": link_type
        })
        self.search_entry.clear()
        self.save_data()
        self.refresh_ui()
        self.status_bar.setText(f"Added new entry: {name}")

    def is_junction(self, path):
        try:
            FILE_ATTRIBUTE_REPARSE_POINT = 0x0400
            attrs = ctypes.windll.kernel32.GetFileAttributesW(path)
            return bool(attrs != -1 and (attrs & FILE_ATTRIBUTE_REPARSE_POINT))
        except:
            return False

    def check_status(self, target, fake, link_type):
        if not os.path.exists(fake) and not os.path.lexists(fake):
            return "Missing Link", CP_YELLOW
        
        try:
            is_link = os.path.islink(fake) or (link_type == "folder" and self.is_junction(fake))
            
            if not is_link:
                return f"Not a {link_type} link", CP_ORANGE
            
            realpath = os.path.realpath(fake)
            target_norm = os.path.normpath(target).lower()
            real_norm = os.path.normpath(realpath).lower()

            if real_norm == target_norm:
                if os.path.exists(target):
                    return "Working", CP_GREEN
                else:
                    return "Broken Target", CP_RED
            else:
                return "Points Elsewhere", CP_ORANGE
        except Exception as e:
            return "Error", CP_RED

    def delete_link(self, index):
        link = self.get_filtered_links()[index]
        reply = QMessageBox.question(self, "Confirm", f"Delete entry '{link['name']}'?", 
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.links.remove(link)
            self.save_data()
            self.refresh_ui()
            self.status_bar.setText("Entry deleted.")

    def edit_link(self, index):
        link = self.get_filtered_links()[index]
        
        def on_save(name, target, fake, link_type):
            link["name"] = name
            link["target"] = target
            link["fake"] = fake
            link["type"] = link_type
            self.save_data()
            self.refresh_ui()
            self.status_bar.setText(f"Updated entry: {name}")

        AddLinkDialog(self, on_save, edit_data=link).exec()

    def open_folder(self, index):
        link = self.get_filtered_links()[index]
        path = os.path.normpath(link["fake"])
        try:
            subprocess.Popen(f'explorer /select,"{path}"')
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open folder:\n{str(e)}")

    def create_link(self, index):
        link = self.get_filtered_links()[index]
        target = os.path.normpath(link["target"])
        fake = os.path.normpath(link["fake"])
        link_type = link.get("type", "folder")

        if not os.path.exists(target):
            QMessageBox.critical(self, "Error", f"Target path does not exist:\n{target}")
            return

        # Handle existing
        if os.path.exists(fake) or os.path.lexists(fake):
            is_proper_link = os.path.islink(fake) or (link_type == "folder" and self.is_junction(fake))
            if not is_proper_link:
                 reply = QMessageBox.question(self, "File Exists", 
                                            f"A {link_type} already exists at location. Delete and replace?",
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                 if reply != QMessageBox.StandardButton.Yes:
                     return
            
            # Remove existing logic (FIXED LOGIC)
            try:
                if os.path.isdir(fake):
                    os.rmdir(fake)
                else:
                    os.remove(fake)
            except Exception as e:
                QMessageBox.critical(self, "Delete Error", f"Failed to remove existing file:\n{str(e)}")
                return

        # Create
        try:
            if link_type == "folder":
                cmd = f'mklink /J "{fake}" "{target}"'
            else:
                cmd = f'mklink "{fake}" "{target}"'
            
            result = subprocess.run(f'cmd /c {cmd}', capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                QMessageBox.information(self, "Success", "Link created successfully.")
            else:
                err = result.stderr.strip() or result.stdout.strip()
                if "privilege" in err.lower() or "access is denied" in err.lower():
                    # Admin retry
                    params = f'/c {cmd}'
                    ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd.exe", params, None, 1)
                    if ret > 32:
                        QMessageBox.information(self, "Admin Action", "Admin command issued. Check status.")
                    else:
                        QMessageBox.critical(self, "Error", "Failed to elevate privileges.")
                else:
                    QMessageBox.critical(self, "Error", f"Cmd failed:\n{err}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unexpected error:\n{str(e)}")
        
        self.refresh_ui()

    def get_filtered_links(self):
        query = self.search_entry.text().lower()
        return [l for l in self.links if query in l['name'].lower() or query in l['target'].lower() or query in l['fake'].lower()]

    def refresh_ui(self):
        # Clear list
        while self.scroll_layout.count():
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        filtered = self.get_filtered_links()
        
        if not filtered:
            lbl = QLabel("No entries found.")
            lbl.setStyleSheet(f"color: {CP_SUBTEXT}; font-style: italic;")
            self.scroll_layout.addWidget(lbl)
            return

        for i, link in enumerate(filtered):
            status_text, status_color = self.check_status(link["target"], link["fake"], link.get("type", "folder"))
            
            # Container
            item_frame = QFrame()
            item_frame.setStyleSheet(f"background-color: {CP_PANEL}; border-radius: 4px; border: 1px solid {CP_DIM};")
            item_layout = QHBoxLayout(item_frame)
            
            # Info
            info_layout = QVBoxLayout()
            name_lbl = QLabel(f"{link['name']}  <span style='color:{status_color}; font-size:9pt;'>({status_text})</span>")
            name_lbl.setStyleSheet("font-weight: bold; font-size: 11pt; border: none;")
            
            paths_lbl = QLabel(f"<span style='color:#3498db'>Target:</span> {link['target']}<br><span style='color:#9b59b6'>Link:</span> {link['fake']}")
            paths_lbl.setWordWrap(True)
            paths_lbl.setStyleSheet(f"color: {CP_SUBTEXT}; font-size: 9pt; border: none;")
            
            info_layout.addWidget(name_lbl)
            info_layout.addWidget(paths_lbl)
            item_layout.addLayout(info_layout, stretch=1)

            # Buttons
            btn_layout = QHBoxLayout()
            
            if status_text != "Working":
                fix_btn = QPushButton("🔗 Fix")
                fix_btn.setFixedSize(80, 30)
                fix_btn.setStyleSheet(f"border-color: {CP_CYAN}; color: {CP_CYAN};")
                fix_btn.clicked.connect(lambda checked, idx=i: self.create_link(idx))
                btn_layout.addWidget(fix_btn)

            open_btn = QPushButton("📂 Open")
            open_btn.setFixedSize(80, 30)
            open_btn.setStyleSheet(f"border-color: #9b59b6; color: #9b59b6;")
            open_btn.clicked.connect(lambda checked, idx=i: self.open_folder(idx))
            btn_layout.addWidget(open_btn)

            edit_btn = QPushButton("📝 Edit")
            edit_btn.setFixedSize(80, 30)
            edit_btn.setStyleSheet(f"border-color: {CP_ORANGE}; color: {CP_ORANGE};")
            edit_btn.clicked.connect(lambda checked, idx=i: self.edit_link(idx))
            btn_layout.addWidget(edit_btn)

            del_btn = QPushButton("🗑️")
            del_btn.setFixedSize(50, 30)
            del_btn.setStyleSheet(f"border-color: {CP_RED}; color: {CP_RED};")
            del_btn.clicked.connect(lambda checked, idx=i: self.delete_link(idx))
            btn_layout.addWidget(del_btn)

            item_layout.addLayout(btn_layout)
            self.scroll_layout.addWidget(item_frame)

        self.scroll_layout.addStretch()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    window = SymlinkManager()
    window.show()
    sys.exit(app.exec())
