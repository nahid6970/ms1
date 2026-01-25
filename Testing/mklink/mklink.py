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
        border-radius: 0px;
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
        border-radius: 0px;
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

class ItemRow(QWidget):
    def __init__(self, parent=None, link_type="folder", target="", fake=""):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 5, 0, 5)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["folder", "file"])
        self.type_combo.setCurrentText(link_type)
        self.type_combo.setFixedWidth(80)
        
        self.target_entry = QLineEdit(target)
        self.target_entry.setPlaceholderText("Target Path")
        
        target_btn = QPushButton("📂")
        target_btn.setFixedWidth(30)
        target_btn.clicked.connect(self.browse_target)
        
        self.fake_entry = QLineEdit(fake)
        self.fake_entry.setPlaceholderText("Link Path")
        
        fake_btn = QPushButton("📂")
        fake_btn.setFixedWidth(30)
        fake_btn.clicked.connect(self.browse_fake)
        
        self.remove_btn = QPushButton("❌")
        self.remove_btn.setFixedWidth(30)
        self.remove_btn.setStyleSheet(f"color: {CP_RED}; border-color: {CP_RED};")
        
        self.layout.addWidget(self.type_combo)
        self.layout.addWidget(self.target_entry)
        self.layout.addWidget(target_btn)
        self.layout.addWidget(self.fake_entry)
        self.layout.addWidget(fake_btn)
        self.layout.addWidget(self.remove_btn)

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

    def get_data(self):
        return {
            "type": self.type_combo.currentText(),
            "target": self.target_entry.text().strip(),
            "fake": self.fake_entry.text().strip()
        }

class AddLinkDialog(QDialog):
    def __init__(self, parent, on_save_callback, edit_data=None):
        super().__init__(parent)
        self.on_save_callback = on_save_callback
        self.edit_data = edit_data
        
        self.setWindowTitle("Edit Entry" if edit_data else "Add New Entry")
        self.resize(850, 500)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Title
        title = QLabel("Edit Entry" if edit_data else "New Entry")
        title.setStyleSheet(f"font-size: 14pt; font-weight: bold; color: {CP_YELLOW};")
        layout.addWidget(title)

        # Name
        name_layout = QHBoxLayout()
        name_lbl = QLabel("Entry Name:")
        name_lbl.setFixedWidth(100)
        name_layout.addWidget(name_lbl)
        self.name_entry = QLineEdit()
        self.name_entry.setPlaceholderText("e.g. My Project Bundle")
        if edit_data:
            self.name_entry.setText(edit_data.get("name", ""))
        name_layout.addWidget(self.name_entry)
        layout.addLayout(name_layout)

        # Items Header
        items_header = QHBoxLayout()
        items_header.addWidget(QLabel("Linked Items:"))
        add_item_btn = QPushButton("➕ Add Item")
        add_item_btn.setFixedWidth(120)
        add_item_btn.setStyleSheet(f"color: {CP_CYAN}; border-color: {CP_CYAN};")
        add_item_btn.clicked.connect(self.add_empty_row)
        items_header.addStretch()
        items_header.addWidget(add_item_btn)
        layout.addLayout(items_header)

        # Scroll Area for Items
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet(f"QScrollArea {{ border: 1px solid {CP_DIM}; background: {CP_BG}; }}")
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        layout.addWidget(self.scroll)

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

        # Rows management
        self.rows = []
        if edit_data:
            items = edit_data.get("items", [])
            if not items and "target" in edit_data: # Fallback for old format
                items = [{
                    "type": edit_data.get("type", "folder"),
                    "target": edit_data.get("target", ""),
                    "fake": edit_data.get("fake", "")
                }]
            for item in items:
                self.add_row(item.get("type", "folder"), item.get("target", ""), item.get("fake", ""))
        else:
            self.add_empty_row()

    def add_row(self, link_type="folder", target="", fake=""):
        row = ItemRow(link_type=link_type, target=target, fake=fake)
        row.remove_btn.clicked.connect(lambda: self.remove_row(row))
        self.scroll_layout.addWidget(row)
        self.rows.append(row)

    def add_empty_row(self):
        self.add_row()

    def remove_row(self, row):
        if len(self.rows) > 1:
            self.rows.remove(row)
            row.deleteLater()
        else:
            QMessageBox.warning(self, "Warning", "At least one item is required.")

    def save_link(self):
        name = self.name_entry.text().strip()
        if not name:
            QMessageBox.warning(self, "Incomplete", "Please enter a name for the entry.")
            return
        
        items = []
        for row in self.rows:
            data = row.get_data()
            if not data["target"] or not data["fake"]:
                QMessageBox.warning(self, "Incomplete", "Please fill all paths for all items.")
                return
            items.append(data)

        if not items:
            QMessageBox.warning(self, "Incomplete", "Please add at least one item.")
            return

        self.on_save_callback(name, items)
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
                    data = json.load(f)
                    # Migration logic for old single-item format
                    for entry in data:
                        if "items" not in entry:
                            entry["items"] = [{
                                "type": entry.get("type", "folder"),
                                "target": entry.get("target", ""),
                                "fake": entry.get("fake", "")
                            }]
                            # Clean up old keys if desired, though not strictly necessary
                            for k in ["target", "fake", "type"]:
                                if k in entry: del entry[k]
                    return data
            except:
                return []
        return []

    def save_data(self):
        with open(self.data_file, "w") as f:
            json.dump(self.links, f, indent=4)

    def open_add_dialog(self):
        AddLinkDialog(self, self.on_link_added).exec()

    def on_link_added(self, name, items):
        self.links.append({
            "name": name,
            "items": items
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

    def check_status(self, entry):
        items = entry.get("items", [])
        if not items:
            return "No items", CP_DIM

        statuses = []
        for item in items:
            target = item.get("target", "")
            fake = item.get("fake", "")
            link_type = item.get("type", "folder")
            
            if not os.path.exists(fake) and not os.path.lexists(fake):
                statuses.append(("Missing Link", CP_YELLOW))
                continue
            
            try:
                is_link = os.path.islink(fake) or (link_type == "folder" and self.is_junction(fake))
                if not is_link:
                    statuses.append((f"Not a {link_type} link", CP_ORANGE))
                    continue
                
                realpath = os.path.realpath(fake)
                target_norm = os.path.normpath(target).lower()
                real_norm = os.path.normpath(realpath).lower()

                if real_norm == target_norm:
                    if os.path.exists(target):
                        statuses.append(("Working", CP_GREEN))
                    else:
                        statuses.append(("Broken Target", CP_RED))
                else:
                    statuses.append(("Points Elsewhere", CP_ORANGE))
            except:
                statuses.append(("Error", CP_RED))

        # Determine aggregate status
        colors = [s[1] for s in statuses]
        if all(c == CP_GREEN for c in colors):
            return "Working", CP_GREEN
        if any(c == CP_RED for c in colors):
            return "Critical Error", CP_RED
        if any(c == CP_ORANGE for c in colors):
            return "Issue Detected", CP_ORANGE
        return "Partial/Missing", CP_YELLOW

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
        
        def on_save(name, items):
            link["name"] = name
            link["items"] = items
            self.save_data()
            self.refresh_ui()
            self.status_bar.setText(f"Updated entry: {name}")

        AddLinkDialog(self, on_save, edit_data=link).exec()

    def open_both_folders(self, index):
        link_entry = self.get_filtered_links()[index]
        try:
            for item in link_entry.get("items", []):
                target = os.path.normpath(item["target"])
                fake = os.path.normpath(item["fake"])
                subprocess.Popen(f'explorer /select,"{target}"')
                subprocess.Popen(f'explorer /select,"{fake}"')
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open folders:\n{str(e)}")

    def create_link(self, index):
        link_entry = self.get_filtered_links()[index]
        items = link_entry.get("items", [])
        
        success_count = 0
        for item in items:
            target = os.path.normpath(item["target"])
            fake = os.path.normpath(item["fake"])
            link_type = item.get("type", "folder")

            if not os.path.exists(target):
                QMessageBox.critical(self, "Error", f"Target path does not exist:\n{target}")
                continue

            # Handle existing
            if os.path.exists(fake) or os.path.lexists(fake):
                is_proper_link = os.path.islink(fake) or (link_type == "folder" and self.is_junction(fake))
                if not is_proper_link:
                     reply = QMessageBox.question(self, "File Exists", 
                                                f"A {link_type} already exists at {fake}. Delete and replace?",
                                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                     if reply != QMessageBox.StandardButton.Yes:
                         continue
                
                try:
                    if os.path.isdir(fake) and not os.path.islink(fake) and not self.is_junction(fake):
                        shutil.rmtree(fake)
                    else:
                        if os.path.isdir(fake): os.rmdir(fake)
                        else: os.remove(fake)
                except Exception as e:
                    QMessageBox.critical(self, "Delete Error", f"Failed to remove existing file:\n{str(e)}")
                    continue

            # Create
            try:
                if link_type == "folder":
                    cmd = f'mklink /J "{fake}" "{target}"'
                else:
                    cmd = f'mklink "{fake}" "{target}"'
                
                result = subprocess.run(f'cmd /c {cmd}', capture_output=True, text=True, shell=True)
                
                if result.returncode == 0:
                    success_count += 1
                else:
                    err = result.stderr.strip() or result.stdout.strip()
                    if "privilege" in err.lower() or "access is denied" in err.lower():
                        params = f'/c {cmd}'
                        ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd.exe", params, None, 1)
                        if ret > 32:
                            success_count += 1
                        else:
                            QMessageBox.critical(self, "Error", "Failed to elevate privileges.")
                    else:
                        QMessageBox.critical(self, "Error", f"Cmd failed for {fake}:\n{err}")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Unexpected error:\n{str(e)}")
        
        if success_count == len(items):
            QMessageBox.information(self, "Success", f"All {len(items)} links created successfully.")
        
        self.refresh_ui()

    def get_filtered_links(self):
        query = self.search_entry.text().lower()
        return [l for l in self.links if query in l['name'].lower()]

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

        for i, link_entry in enumerate(filtered):
            status_text, status_color = self.check_status(link_entry)
            
            # Container
            item_frame = QFrame()
            item_frame.setStyleSheet(f"background-color: {CP_PANEL}; border-radius: 0px; border: 1px solid {CP_DIM};")
            item_layout = QHBoxLayout(item_frame)
            
            # Info
            info_layout = QVBoxLayout()
            name_lbl = QLabel(f"<html>{link_entry['name']}  <span style='color:{status_color}; font-size:9pt;'>({status_text})</span></html>")
            name_lbl.setTextFormat(Qt.TextFormat.RichText)
            name_lbl.setStyleSheet("font-weight: bold; font-size: 11pt; border: none;")
            info_layout.addWidget(name_lbl)

            # Details (multi-item paths)
            paths_text = "<html>"
            for item in link_entry.get("items", []):
                paths_text += f"<span style='color:#3498db'>[{item['type'][0].upper()}] Target:</span> {item['target']}<br><span style='color:#9b59b6'>Link:</span> {item['fake']}<br>"
            paths_text += "</html>"
            
            paths_lbl = QLabel(paths_text)
            paths_lbl.setTextFormat(Qt.TextFormat.RichText)
            paths_lbl.setWordWrap(True)
            paths_lbl.setStyleSheet(f"color: {CP_SUBTEXT}; font-size: 8pt; border: none; padding-top: 5px;")
            info_layout.addWidget(paths_lbl)
            
            item_layout.addLayout(info_layout, stretch=1)

            # Buttons
            btn_layout = QHBoxLayout()
            
            if status_text != "Working":
                fix_btn = QPushButton("🔗 Fix All")
                fix_btn.setFixedSize(90, 30)
                fix_btn.setStyleSheet(f"""
                    QPushButton {{ border-color: {CP_CYAN}; color: {CP_CYAN}; }}
                    QPushButton:hover {{ background-color: {CP_CYAN}; color: black; }}
                """)
                fix_btn.clicked.connect(lambda checked, idx=i: self.create_link(idx))
                btn_layout.addWidget(fix_btn)

            # Open Both Button
            open_btn = QPushButton("📂 Open All")
            open_btn.setFixedSize(90, 30)
            open_btn.setStyleSheet(f"""
                QPushButton {{ border-color: #9b59b6; color: #9b59b6; }}
                QPushButton:hover {{ background-color: #9b59b6; color: black; }}
            """)
            open_btn.clicked.connect(lambda checked, idx=i: self.open_both_folders(idx))
            btn_layout.addWidget(open_btn)

            edit_btn = QPushButton("📝 Edit")
            edit_btn.setFixedSize(80, 30)
            edit_btn.setStyleSheet(f"""
                QPushButton {{ border-color: {CP_ORANGE}; color: {CP_ORANGE}; }}
                QPushButton:hover {{ background-color: {CP_ORANGE}; color: black; }}
            """)
            edit_btn.clicked.connect(lambda checked, idx=i: self.edit_link(idx))
            btn_layout.addWidget(edit_btn)

            del_btn = QPushButton("🗑️")
            del_btn.setFixedSize(50, 30)
            del_btn.setStyleSheet(f"""
                QPushButton {{ border-color: {CP_RED}; color: {CP_RED}; }}
                QPushButton:hover {{ background-color: {CP_RED}; color: black; }}
            """)
            del_btn.clicked.connect(lambda checked, idx=i: self.delete_link(idx))
            btn_layout.addWidget(del_btn)

            item_layout.addLayout(btn_layout)
            self.scroll_layout.addWidget(item_frame)

        self.scroll_layout.addStretch()

        self.scroll_layout.addStretch()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    window = SymlinkManager()
    window.show()
    sys.exit(app.exec())
