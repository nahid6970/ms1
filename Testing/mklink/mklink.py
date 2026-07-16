#!/usr/bin/env python3
import sys
import json
import os
import ctypes
import subprocess
import shutil
import re

def normalize_path(path):
    if not path:
        return path
    if os.name != 'nt':
        # Convert backslashes to forward slashes
        path = path.replace('\\', '/')
        # Translate Windows user profile prefix to home directory
        user_home = os.path.expanduser('~')
        path = re.sub(r'^[a-zA-Z]:/Users/[^/]+', user_home, path)
        # Translate remaining drive letters to home or root
        path = re.sub(r'^[a-zA-Z]:/', user_home + '/', path)
        path = re.sub(r'^[a-zA-Z]:', user_home, path)
    else:
        path = os.path.normpath(path)
    return path

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QLineEdit, QGroupBox, QFormLayout, 
                             QDialog, QMessageBox, QScrollArea, QFrame, QComboBox, QSizePolicy, QFileDialog, QMenu, QCheckBox)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon, QColor, QCursor

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
    
    /* SCROLL AREA & SCROLLBARS */
    QScrollArea {{
        background: transparent;
        border: none;
    }}
    QScrollBar:vertical {{
        border: 1px solid #3a3a3a;
        background: #111111;
        width: 10px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: #00F0FF;
        min-height: 20px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: #FCEE0A;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        background: none;
        height: 0px;
    }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: none;
    }}

    QScrollBar:horizontal {{
        border: 1px solid #3a3a3a;
        background: #111111;
        height: 10px;
        margin: 0px;
    }}
    QScrollBar::handle:horizontal {{
        background: #00F0FF;
        min-width: 20px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: #FCEE0A;
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        background: none;
        width: 0px;
    }}
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
        background: none;
    }}
    
    /* MENU */
    QMenu {{
        background-color: {CP_PANEL};
        border: 1px solid {CP_DIM};
        color: {CP_TEXT};
    }}
    QMenu::item {{
        padding: 8px 25px;
    }}
    QMenu::item:selected {{
        background-color: {CP_DIM};
        color: {CP_YELLOW};
    }}
"""

# ==========================================
# HELPER CLASSES
# ==========================================

class SelectiveFileDialog(QDialog):
    """Dialog to select individual files from a target folder for symlink."""
    def __init__(self, parent, target_path, previously_selected=None, previously_excluded=None):
        super().__init__(parent)
        self.setWindowTitle("Select Files to Symlink")
        self.resize(800, 600)
        self.setModal(True)
        self.result_files = None  # Will hold list of selected relative paths

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Title
        title = QLabel("📋 Select Files to Symlink")
        title.setStyleSheet(f"font-size: 14pt; font-weight: bold; color: {CP_YELLOW};")
        layout.addWidget(title)

        # Folder info
        folder_lbl = QLabel(f"Scanning: {target_path}")
        folder_lbl.setStyleSheet(f"color: {CP_CYAN}; font-size: 9pt;")
        folder_lbl.setWordWrap(True)
        layout.addWidget(folder_lbl)

        # Search / filter
        filter_layout = QHBoxLayout()
        self.filter_entry = QLineEdit()
        self.filter_entry.setPlaceholderText("Filter files...")
        self.filter_entry.textChanged.connect(self._apply_filter)
        filter_layout.addWidget(self.filter_entry)

        select_all_btn = QPushButton("Select All")
        select_all_btn.setFixedWidth(100)
        select_all_btn.setStyleSheet(f"color: {CP_GREEN}; border-color: {CP_GREEN};")
        select_all_btn.clicked.connect(self._select_all)
        filter_layout.addWidget(select_all_btn)

        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.setFixedWidth(110)
        deselect_all_btn.setStyleSheet(f"color: {CP_RED}; border-color: {CP_RED};")
        deselect_all_btn.clicked.connect(self._deselect_all)
        filter_layout.addWidget(deselect_all_btn)

        layout.addLayout(filter_layout)

        # Count label
        self.count_lbl = QLabel("")
        self.count_lbl.setStyleSheet(f"color: {CP_SUBTEXT}; font-size: 9pt;")
        layout.addWidget(self.count_lbl)

        # Scroll area with checkboxes
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet(f"QScrollArea {{ border: 1px solid {CP_DIM}; background: {CP_BG}; }}")
        self.scroll_content = QWidget()
        self.scroll_vlayout = QVBoxLayout(self.scroll_content)
        self.scroll_vlayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_vlayout.setSpacing(2)
        self.scroll.setWidget(self.scroll_content)
        layout.addWidget(self.scroll)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        apply_btn = QPushButton("Apply Selection")
        apply_btn.setStyleSheet(f"""
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
        apply_btn.clicked.connect(self._apply)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(apply_btn)
        layout.addLayout(btn_layout)

        # Scan files
        self.checkboxes = []  # list of (relative_path, QCheckBox)
        self._scan_files(target_path, previously_selected, previously_excluded)
        self._update_count()

    def _scan_files(self, target_path, previously_selected, previously_excluded):
        if not os.path.isdir(target_path):
            lbl = QLabel("⚠ Target path is not a valid directory.")
            lbl.setStyleSheet(f"color: {CP_RED};")
            self.scroll_vlayout.addWidget(lbl)
            return

        all_files = []
        for root, dirs, files in os.walk(target_path):
            for fname in files:
                full = os.path.join(root, fname)
                rel = os.path.relpath(full, target_path)
                all_files.append(rel)

        all_files.sort(key=str.lower)

        if not all_files:
            lbl = QLabel("No files found in this directory.")
            lbl.setStyleSheet(f"color: {CP_SUBTEXT};")
            self.scroll_vlayout.addWidget(lbl)
            return

        # Determine checked state:
        # If previously_selected exists, only those are checked.
        # If previously_excluded exists, everything except those is checked.
        # Otherwise, all checked by default.
        for rel in all_files:
            cb = QCheckBox(rel)
            cb.setStyleSheet(f"""
                QCheckBox {{
                    color: {CP_TEXT};
                    padding: 3px 5px;
                    border: none;
                }}
                QCheckBox:hover {{
                    color: {CP_CYAN};
                }}
                QCheckBox::indicator {{
                    width: 14px;
                    height: 14px;
                    border: 1px solid {CP_DIM};
                    background: {CP_PANEL};
                }}
                QCheckBox::indicator:checked {{
                    background: {CP_CYAN};
                    border-color: {CP_CYAN};
                }}
            """)

            if previously_selected is not None:
                cb.setChecked(rel in previously_selected)
            elif previously_excluded is not None:
                cb.setChecked(rel not in previously_excluded)
            else:
                cb.setChecked(True)

            cb.stateChanged.connect(self._update_count)
            self.scroll_vlayout.addWidget(cb)
            self.checkboxes.append((rel, cb))

    def _apply_filter(self, text):
        text = text.lower()
        for rel, cb in self.checkboxes:
            cb.setVisible(text in rel.lower())

    def _select_all(self):
        for rel, cb in self.checkboxes:
            if cb.isVisible():
                cb.setChecked(True)

    def _deselect_all(self):
        for rel, cb in self.checkboxes:
            if cb.isVisible():
                cb.setChecked(False)

    def _update_count(self):
        total = len(self.checkboxes)
        selected = sum(1 for _, cb in self.checkboxes if cb.isChecked())
        self.count_lbl.setText(f"{selected} / {total} files selected")

    def _apply(self):
        self.result_files = [rel for rel, cb in self.checkboxes if cb.isChecked()]
        self.accept()


class ItemRow(QWidget):
    def __init__(self, parent=None, link_type="folder", target="", fake="", selected_files=None, excluded_files=None):
        super().__init__(parent)
        self.selected_files = selected_files  # list of relative paths or None
        self.excluded_files = excluded_files  # list of excluded relative paths or None
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 5, 0, 5)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["folder", "file", "selective"])
        self.type_combo.setCurrentText(link_type)
        self.type_combo.setFixedWidth(100)
        self.type_combo.currentTextChanged.connect(self.update_combo_style)
        self.type_combo.currentTextChanged.connect(self._on_type_changed)
        
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

        # Select Files button (only visible for "selective" type)
        self.select_files_btn = QPushButton("📋 Select")
        self.select_files_btn.setFixedWidth(80)
        self.select_files_btn.setStyleSheet(f"color: {CP_CYAN}; border-color: {CP_CYAN};")
        self.select_files_btn.clicked.connect(self.open_selective_dialog)
        self.select_files_btn.setVisible(link_type == "selective")
        
        self.remove_btn = QPushButton("❌")
        self.remove_btn.setFixedWidth(30)
        self.remove_btn.setStyleSheet(f"color: {CP_RED}; border-color: {CP_RED};")
        
        self.layout.addWidget(self.type_combo)
        self.layout.addWidget(self.target_entry)
        self.layout.addWidget(target_btn)
        self.layout.addWidget(self.fake_entry)
        self.layout.addWidget(fake_btn)
        self.layout.addWidget(self.select_files_btn)
        self.layout.addWidget(self.remove_btn)
        
        # Set initial style
        self.update_combo_style(self.type_combo.currentText())

    def _on_type_changed(self, text):
        self.select_files_btn.setVisible(text == "selective")
        if text != "selective":
            self.selected_files = None
            self.excluded_files = None

    def update_combo_style(self, text):
        if text == "folder":
            self.type_combo.setStyleSheet("background-color: #FCEE0A; color: black; font-weight: bold; border: 1px solid #3a3a3a;")
        elif text == "selective":
            self.type_combo.setStyleSheet(f"background-color: {CP_CYAN}; color: black; font-weight: bold; border: 1px solid #3a3a3a;")
        else:
            self.type_combo.setStyleSheet("background-color: #FFFFFF; color: black; font-weight: bold; border: 1px solid #3a3a3a;")

    def browse_target(self):
        current_type = self.type_combo.currentText()
        if current_type == "file":
            path, _ = QFileDialog.getOpenFileName(self, "Select Target File")
        else:  # folder or selective
            path = QFileDialog.getExistingDirectory(self, "Select Target Folder")
        if path:
            self.target_entry.setText(os.path.normpath(path))

    def browse_fake(self):
        current_type = self.type_combo.currentText()
        if current_type == "file":
            path, _ = QFileDialog.getSaveFileName(self, "Select Link File Location")
        else:  # folder or selective
            path = QFileDialog.getExistingDirectory(self, "Select Link Directory")
        if path:
            self.fake_entry.setText(os.path.normpath(path))

    def open_selective_dialog(self):
        target = self.target_entry.text().strip()
        if not target:
            QMessageBox.warning(self, "No Target", "Please set a target folder first.")
            return
        if not os.path.isdir(target):
            QMessageBox.warning(self, "Invalid Target", f"Target is not a valid directory:\n{target}")
            return

        dlg = SelectiveFileDialog(
            self,
            target,
            previously_selected=self.selected_files,
            previously_excluded=self.excluded_files
        )
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.result_files is not None:
            self.selected_files = dlg.result_files
            # Also compute excluded list for persistence
            all_files = []
            for root, dirs, files in os.walk(target):
                for fname in files:
                    full = os.path.join(root, fname)
                    rel = os.path.relpath(full, target)
                    all_files.append(rel)
            self.excluded_files = [f for f in all_files if f not in self.selected_files]
            count = len(self.selected_files)
            self.select_files_btn.setText(f"📋 {count} sel")
            self.select_files_btn.setToolTip(f"{count} files selected for symlink")

    def get_data(self):
        data = {
            "type": self.type_combo.currentText(),
            "target": self.target_entry.text().strip(),
            "fake": self.fake_entry.text().strip()
        }
        if self.type_combo.currentText() == "selective":
            if self.selected_files is not None:
                data["selected_files"] = self.selected_files
            if self.excluded_files is not None:
                data["excluded_files"] = self.excluded_files
        return data

class AddLinkDialog(QDialog):
    def __init__(self, parent, on_save_callback, edit_data=None):
        super().__init__(parent)
        self.on_save_callback = on_save_callback
        self.edit_data = edit_data
        
        self.setWindowTitle("Edit Entry" if edit_data else "Add New Entry")
        self.resize(1200, 500)
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

        # Copy Toggle
        self.copy_chk = QCheckBox("Copy Mode (No Symlinks)")
        self.copy_chk.setStyleSheet(f"color: {CP_CYAN}; font-weight: bold; margin-left: 20px;")
        if edit_data:
            self.copy_chk.setChecked(edit_data.get("copy_mode", False))
        name_layout.addWidget(self.copy_chk)

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
                self.add_row(
                    item.get("type", "folder"),
                    item.get("target", ""),
                    item.get("fake", ""),
                    item.get("selected_files"),
                    item.get("excluded_files")
                )
        else:
            self.add_empty_row()

    def add_row(self, link_type="folder", target="", fake="", selected_files=None, excluded_files=None):
        row = ItemRow(link_type=link_type, target=target, fake=fake,
                      selected_files=selected_files, excluded_files=excluded_files)
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

        copy_mode = self.copy_chk.isChecked()
        self.on_save_callback(name, items, copy_mode)
        self.accept()

# ==========================================
# MAIN APPLICATION
# ==========================================

class SymlinkManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cyberpunk Symlink Manager")
        self.resize(1300, 600)
        
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
                        for item in entry.get("items", []):
                            item["target"] = normalize_path(item["target"])
                            item["fake"] = normalize_path(item["fake"])
                    return data
            except:
                return []
        return []

    def save_data(self):
        with open(self.data_file, "w") as f:
            json.dump(self.links, f, indent=4)

    def open_add_dialog(self):
        AddLinkDialog(self, self.on_link_added).exec()

    def on_link_added(self, name, items, copy_mode):
        self.links.append({
            "name": name,
            "items": items,
            "copy_mode": copy_mode
        })
        self.search_entry.clear()
        self.save_data()
        self.refresh_ui()
        self.status_bar.setText(f"Added new entry: {name}")

    def is_junction(self, path):
        if os.name != 'nt':
            return os.path.islink(path)
        try:
            FILE_ATTRIBUTE_REPARSE_POINT = 0x0400
            attrs = ctypes.windll.kernel32.GetFileAttributesW(path)
            return bool(attrs != -1 and (attrs & FILE_ATTRIBUTE_REPARSE_POINT))
        except:
            return False

    def check_status(self, entry):
        items = entry.get("items", [])
        copy_mode = entry.get("copy_mode", False)
        
        if not items:
            return "No items", CP_DIM

        statuses = []
        for item in items:
            target = item.get("target", "")
            fake = item.get("fake", "")
            link_type = item.get("type", "folder")
            
            # SELECTIVE TYPE: check individual file symlinks
            if link_type == "selective":
                selected = item.get("selected_files", [])
                if not selected:
                    statuses.append(("No files selected", CP_YELLOW))
                    continue
                sel_working = 0
                sel_missing = 0
                sel_broken = 0
                for rel in selected:
                    link_path = os.path.join(fake, rel)
                    if not os.path.exists(link_path) and not os.path.lexists(link_path):
                        sel_missing += 1
                    elif os.path.islink(link_path):
                        realpath = os.path.realpath(link_path)
                        expected = os.path.normpath(os.path.join(target, rel)).lower()
                        if os.path.normpath(realpath).lower() == expected and os.path.exists(link_path):
                            sel_working += 1
                        else:
                            sel_broken += 1
                    else:
                        sel_broken += 1
                if sel_working == len(selected):
                    statuses.append(("Working", CP_GREEN))
                elif sel_missing == len(selected):
                    statuses.append(("Missing Links", CP_YELLOW))
                elif sel_broken > 0:
                    statuses.append(("Issue Detected", CP_ORANGE))
                else:
                    statuses.append(("Partial", CP_YELLOW))
                continue

            # COPY MODE LOGIC
            if copy_mode:
                if os.path.exists(fake) and not os.path.lexists(fake):
                    # Normal file/folder exists (good)
                    statuses.append(("Copied", CP_GREEN))
                elif os.path.islink(fake) or self.is_junction(fake):
                    statuses.append(("Is Link (Mode: Copy)", CP_ORANGE))
                elif not os.path.exists(fake):
                    statuses.append(("Missing", CP_YELLOW))
                continue
            
            # LINK MODE LOGIC
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
        
        def on_save(name, items, copy_mode):
            link["name"] = name
            link["items"] = items
            link["copy_mode"] = copy_mode
            self.save_data()
            self.refresh_ui()
            self.status_bar.setText(f"Updated entry: {name}")

        AddLinkDialog(self, on_save, edit_data=link).exec()

    def open_both_folders(self, index):
        link_entry = self.get_filtered_links()[index]
        items = link_entry.get("items", [])
        
        if not items:
            return

        if len(items) == 1:
            self._open_item_paths(items[0]["target"], items[0]["fake"])
        else:
            menu = QMenu(self)
            for item in items:
                name = os.path.basename(item["target"]) or item["target"]
                action = menu.addAction(f"[{item['type'][0].upper()}] {name}")
                # Use default arguments in lambda to capture current values of item
                action.triggered.connect(lambda checked, t=item["target"], f=item["fake"]: self._open_item_paths(t, f))
            
            menu.exec(QCursor.pos())

    def _open_item_paths(self, target, fake):
        target = os.path.normpath(target)
        fake = os.path.normpath(fake)
        try:
            if os.name == 'nt':
                # We use explorer /select to highlight the file/folder in its parent
                subprocess.Popen(f'explorer /select,"{target}"')
                subprocess.Popen(f'explorer /select,"{fake}"')
            else:
                for path in [target, fake]:
                    if hasattr(os, 'startfile'):
                        os.startfile(path)
                    else:
                        open_path = path if os.path.isdir(path) else os.path.dirname(path)
                        subprocess.Popen(['xdg-open', open_path])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open folders:\n{str(e)}")

    def create_link(self, index):
        link_entry = self.get_filtered_links()[index]
        items = link_entry.get("items", [])
        copy_mode = link_entry.get("copy_mode", False)
        
        if not items:
            return

        # 1. PRE-CHECK FOR CONFLICTS
        conflicts = []
        for item in items:
            fake = os.path.normpath(item["fake"])
            if os.path.exists(fake) or os.path.lexists(fake):
                conflicts.append(fake)
        
        if conflicts:
            msg = f"The following {len(conflicts)} item(s) already exist:\n\n"
            msg += "\n".join([f"• {c}" for c in conflicts[:10]])
            if len(conflicts) > 10:
                msg += f"\n... and {len(conflicts)-10} more."
            msg += "\n\nOverwrite all and proceed?"
            
            reply = QMessageBox.question(self, "Conflict Detected", msg, 
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return

        # 2. EXECUTION
        success_count = 0
        error_logs = []
        
        for item in items:
            target = os.path.normpath(item["target"])
            fake = os.path.normpath(item["fake"])
            link_type = item.get("type", "folder")

            if not os.path.exists(target):
                error_logs.append(f"Target missing: {target}")
                continue

            # SELECTIVE TYPE: symlink each selected file individually
            if link_type == "selective":
                selected = item.get("selected_files", [])
                if not selected:
                    error_logs.append(f"No files selected for selective link: {target}")
                    continue
                for rel in selected:
                    src = os.path.normpath(os.path.join(target, rel))
                    dst = os.path.normpath(os.path.join(fake, rel))
                    if not os.path.exists(src):
                        error_logs.append(f"Source file missing: {src}")
                        continue
                    # Remove existing
                    try:
                        if os.path.exists(dst) or os.path.lexists(dst):
                            os.remove(dst)
                    except Exception as e:
                        error_logs.append(f"Failed to remove {dst}: {str(e)}")
                        continue
                    # Ensure parent dir
                    try:
                        parent = os.path.dirname(dst)
                        if parent and not os.path.exists(parent):
                            os.makedirs(parent, exist_ok=True)
                    except Exception as e:
                        error_logs.append(f"Failed to create dirs for {dst}: {str(e)}")
                        continue
                    # Create symlink
                    try:
                        if os.name == 'nt':
                            cmd = f'mklink "{dst}" "{src}"'
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
                                        error_logs.append(f"Elevation failed for: {dst}")
                                else:
                                    error_logs.append(f"Cmd failed for {dst}: {err}")
                        else:
                            os.symlink(src, dst)
                            success_count += 1
                    except Exception as e:
                        error_logs.append(f"Selective symlink failed for {dst}: {str(e)}")
                continue

            # Remove existing if any (permission already granted above)
            try:
                if os.path.exists(fake) or os.path.lexists(fake):
                    if os.path.isdir(fake) and not os.path.islink(fake) and not self.is_junction(fake):
                        shutil.rmtree(fake)
                    else:
                        if os.path.isdir(fake): os.rmdir(fake)
                        else: os.remove(fake)
            except Exception as e:
                error_logs.append(f"Failed to remove {fake}: {str(e)}")
                continue

            # Create
            try:
                # Ensure parent directory exists
                parent_dir = os.path.dirname(fake)
                if parent_dir and not os.path.exists(parent_dir):
                    os.makedirs(parent_dir, exist_ok=True)

                if copy_mode:
                    if os.path.isdir(target):
                        shutil.copytree(target, fake, dirs_exist_ok=True)
                    else:
                        shutil.copy2(target, fake)
                    success_count += 1
                else:
                    if os.name == 'nt':
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
                                    error_logs.append(f"Elevation failed for: {fake}")
                            else:
                                error_logs.append(f"Cmd failed for {fake}: {err}")
                    else:
                        try:
                            os.symlink(target, fake)
                            success_count += 1
                        except Exception as sym_err:
                            error_logs.append(f"Symlink creation failed for {fake}: {str(sym_err)}")
            except Exception as e:
                error_logs.append(f"Unexpected error for {fake}: {str(e)}")
        
        # 3. SUMMARY REPORT
        if error_logs:
            report = f"Processed {len(items)} items:\n"
            report += f"✅ Success: {success_count}\n"
            report += f"❌ Failed: {len(error_logs)}\n\n"
            report += "Errors:\n" + "\n".join([f"• {e}" for e in error_logs])
            
            # Show in a scrollable message box if it's long
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Operation Results")
            msg_box.setText(f"Completed with {len(error_logs)} errors.")
            msg_box.setInformativeText("See details below.")
            msg_box.setDetailedText(report)
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.exec()
        else:
            op = "copied" if copy_mode else "linked"
            QMessageBox.information(self, "Success", f"All {len(items)} items {op} successfully.")
        
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
                type_letter = item['type'][0].upper()
                extra = ""
                if item['type'] == 'selective':
                    sel_count = len(item.get('selected_files', []))
                    extra = f" <span style='color:{CP_CYAN};'>({sel_count} files)</span>"
                paths_text += f"<span style='color:#3498db'>[{type_letter}] Target:</span> {item['target']}{extra}<br><span style='color:#9b59b6'>Link:</span> {item['fake']}<br>"
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
                fix_btn.setFixedSize(110, 30)
                fix_btn.setStyleSheet(f"""
                    QPushButton {{ border-color: {CP_CYAN}; color: {CP_CYAN}; }}
                    QPushButton:hover {{ background-color: {CP_CYAN}; color: black; }}
                """)
                fix_btn.clicked.connect(lambda checked, idx=i: self.create_link(idx))
                btn_layout.addWidget(fix_btn)

            # Open Both Button
            open_btn = QPushButton("📂 Open")
            open_btn.setFixedSize(80, 30)
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    window = SymlinkManager()
    window.show()
    sys.exit(app.exec())
