import sys
import json
import os
import re
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                            QWidget, QPushButton, QLineEdit, QCheckBox, QDialog,
                            QDialogButtonBox, QLabel, QTextEdit, QComboBox, QMessageBox,
                            QSplitter, QFrame, QTextBrowser, QMenu)
from PyQt6.QtCore import Qt, pyqtSignal, QSettings, QPoint, QSize
from PyQt6.QtGui import QFont, QTextCursor, QKeySequence

AHK_SCRIPT_PATH = "ahk_v2.ahk"
SHORTCUTS_JSON_PATH = "ahk_shortcuts.json"

class ShortcutBuilderPopup(QDialog):
    def __init__(self, parent=None, initial_value=""):
        super().__init__(parent)
        self.setWindowTitle("Shortcut Builder")
        self.setModal(True)
        self.setFixedWidth(400)
        self.setStyleSheet("background-color: #2b2b2b; color: white;")
        
        self.result_hotkey = initial_value
        self.mods = {"^": False, "!": False, "+": False, "#": False}
        self.main_key = ""
        
        self.parse_initial(initial_value)
        self.setup_ui()

    def parse_initial(self, value):
        if not value: return
        
        # Extract modifiers
        for mod in self.mods:
            if mod in value:
                self.mods[mod] = True
                value = value.replace(mod, "")
        
        self.main_key = value

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Preview
        self.preview_label = QLabel(self.get_formatted_preview())
        self.preview_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #61dafb; margin: 10px; qproperty-alignment: AlignCenter;")
        layout.addWidget(self.preview_label)
        
        # Modifiers
        mod_layout = QHBoxLayout()
        self.mod_buttons = {}
        mod_info = [("^", "Ctrl"), ("!", "Alt"), ("+", "Shift"), ("#", "Win")]
        for symbol, name in mod_info:
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setChecked(self.mods[symbol])
            btn.setStyleSheet("""
                QPushButton { background: #3d3d3d; border: 1px solid #555; padding: 10px; border-radius: 5px; }
                QPushButton:checked { background: #61dafb; color: black; border-color: #61dafb; }
            """)
            btn.toggled.connect(lambda checked, s=symbol: self.update_mod(s, checked))
            mod_layout.addWidget(btn)
            self.mod_buttons[symbol] = btn
        layout.addLayout(mod_layout)
        
        # Key Selector
        layout.addWidget(QLabel("Select Main Key:"))
        self.key_list = QComboBox()
        self.key_list.setEditable(True)
        self.common_keys = [
            "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", 
            "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
            "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
            "Space", "Enter", "Tab", "Esc", "Backspace", "Delete", "Insert", "Home", "End", "PgUp", "PgDn",
            "Up", "Down", "Left", "Right", "LButton", "RButton", "MButton", "WheelUp", "WheelDown",
            "[", "]", ";", "'", ",", ".", "/", "\\", "-", "=", "`"
        ]
        self.key_list.addItems(self.common_keys)
        
        # Search Box
        self.key_search = QLineEdit()
        self.key_search.setPlaceholderText("Search keys (e.g. 'space', 'f1', 'x')...")
        self.key_search.textChanged.connect(self.filter_keys)
        # Style search box
        self.key_search.setStyleSheet("padding: 8px; border-radius: 5px; background: #3d3d3d;")
        layout.addWidget(self.key_search)
        
        if self.main_key:
            self.key_list.setCurrentText(self.main_key)
        self.key_list.currentTextChanged.connect(self.update_key)
        layout.addWidget(self.key_list)
        
        # Quick access area (Flow layout style)
        layout.addWidget(QLabel("Quick Keys:"))
        quick_grid = QWidget()
        quick_layout = QHBoxLayout(quick_grid)
        quick_layout.setContentsMargins(0, 0, 0, 0)
        for k in ["Space", "Enter", "Tab", "Esc", "Up", "Down"]:
            btn = QPushButton(k)
            btn.setStyleSheet("padding: 5px; font-size: 12px;")
            btn.clicked.connect(lambda checked, val=k: self.key_list.setCurrentText(val))
            quick_layout.addWidget(btn)
        layout.addWidget(quick_grid)

        # OK/Cancel
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def update_mod(self, symbol, state):
        self.mods[symbol] = state
        self.update_preview()

    def update_key(self, key):
        self.main_key = key
        self.update_preview()

    def update_preview(self):
        self.preview_label.setText(self.get_formatted_preview())

    def get_formatted_preview(self):
        res = ""
        if self.mods["^"]: res += "Ctrl+"
        if self.mods["!"]: res += "Alt+"
        if self.mods["+"]: res += "Shift+"
        if self.mods["#"]: res += "Win+"
        res += self.main_key if self.main_key else "?"
        return res

    def get_final_ahk(self):
        res = ""
        if self.mods["^"]: res += "^"
        if self.mods["!"]: res += "!"
        if self.mods["+"]: res += "+"
        if self.mods["#"]: res += "#"
        res += self.main_key
        return res

    def filter_keys(self, text):
        text = text.lower().strip()
        if not text:
            # If search is cleared, don't change current selection unless it's empty
            return

        # Find all matching keys
        matches = [k for k in self.common_keys if text in k.lower()]
        
        if matches:
            # Automatically pick the best match (starts with text is better than just contains)
            best_match = next((k for k in matches if k.lower().startswith(text)), matches[0])
            self.key_list.setCurrentText(best_match)

class HotkeyLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_recording = False
        self.record_button = None

    def set_recording(self, state):
        if not state:
            return
            
        # Instead of recording, show the builder
        builder = ShortcutBuilderPopup(self, self.text())
        if builder.exec():
            self.setText(builder.get_final_ahk())
        
        # Always uncheck the button after the dialog closes
        if self.record_button:
            self.record_button.setChecked(False)

    def keyPressEvent(self, event):
        # We might still want to capture normal typing for manual entry
        super().keyPressEvent(event)

class AddEditShortcutDialog(QDialog):
    def __init__(self, parent, shortcut_type, shortcut_data=None):
        super().__init__(parent)
        self.parent_window = parent
        self.shortcut_type = shortcut_type
        self.shortcut_data = shortcut_data

        self.setWindowTitle(f"{'Edit' if shortcut_data else 'Add'} {shortcut_type.capitalize()} Shortcut")
        self.setModal(True)
        self.resize(500, 400)

        self.setup_ui()
        if shortcut_data:
            self.populate_fields()

    def setup_ui(self):
        # Create main layout
        layout = QVBoxLayout()
        
        # Create top layout for name, category, description
        top_layout = QHBoxLayout()
        
        # Left side - form fields
        form_layout = QVBoxLayout()
        
        # Name
        form_layout.addWidget(QLabel("Name:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., Open Terminal, Version 1 Text")
        form_layout.addWidget(self.name_edit)
        
        # Category
        form_layout.addWidget(QLabel("Category:"))
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        existing_categories = self.get_existing_categories()
        self.category_combo.addItems(existing_categories)
        self.category_combo.setCurrentText("General")
        form_layout.addWidget(self.category_combo)
        
        # Description
        form_layout.addWidget(QLabel("Description:"))
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("Brief description of what this does")
        form_layout.addWidget(self.description_edit)
        
        # Enabled checkbox
        self.enabled_checkbox = QCheckBox("Enabled (include in generated script)")
        self.enabled_checkbox.setChecked(True)
        form_layout.addWidget(self.enabled_checkbox)
        
        if self.shortcut_type == "script":
            # Hotkey
            form_layout.addWidget(QLabel("Hotkey:"))
            hotkey_row = QHBoxLayout()
            self.hotkey_edit = HotkeyLineEdit()
            self.hotkey_edit.setPlaceholderText("e.g., !Space, ^!n, #x")
            
            self.record_hotkey_btn = QPushButton("⌨")
            self.record_hotkey_btn.setCheckable(True)
            self.record_hotkey_btn.setFixedWidth(40)
            self.record_hotkey_btn.setStyleSheet("""
                QPushButton {
                    font-family: 'JetBrainsMono NFP', 'JetBrains Mono', monospace;
                    background-color: #3d3d3d;
                    border: 1px solid #555;
                    border-radius: 5px;
                    color: white;
                    font-size: 18px;
                }
                QPushButton:checked {
                    background-color: #61dafb;
                    color: black;
                    border-color: #61dafb;
                }
                QPushButton:hover {
                    background-color: #4d4d4d;
                    border-color: #61dafb;
                }
            """)
            self.record_hotkey_btn.setToolTip("Open Shortcut Builder")
            self.record_hotkey_btn.clicked.connect(lambda checked: self.hotkey_edit.set_recording(checked))
            self.hotkey_edit.record_button = self.record_hotkey_btn
            
            hotkey_row.addWidget(self.hotkey_edit)
            hotkey_row.addWidget(self.record_hotkey_btn)
            form_layout.addLayout(hotkey_row)
        else:
            # Trigger
            form_layout.addWidget(QLabel("Trigger (without ::):"))
            self.trigger_edit = QLineEdit()
            self.trigger_edit.setPlaceholderText("e.g., ;v1, ;run")
            form_layout.addWidget(self.trigger_edit)
        
        # Add form layout to top layout
        top_layout.addLayout(form_layout)
        
        # Right side - action/replacement with bigger height and width
        if self.shortcut_type == "script":
            # Action
            action_layout = QVBoxLayout()
            action_layout.addWidget(QLabel("Action:"))
            self.action_edit = QTextEdit()
            self.action_edit.setMinimumHeight(300)  # Bigger height
            self.action_edit.setMinimumWidth(400)   # Bigger width
            action_layout.addWidget(self.action_edit)
            top_layout.addLayout(action_layout)
        else:
            # Replacement
            replacement_layout = QVBoxLayout()
            replacement_layout.addWidget(QLabel("Replacement Text:"))
            self.replacement_edit = QTextEdit()
            self.replacement_edit.setMinimumHeight(300)  # Bigger height
            self.replacement_edit.setMinimumWidth(400)   # Bigger width
            replacement_layout.addWidget(self.replacement_edit)
            top_layout.addLayout(replacement_layout)
        
        layout.addLayout(top_layout)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept_dialog)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_existing_categories(self):
        categories = set()
        for shortcut in self.parent_window.script_shortcuts + self.parent_window.text_shortcuts:
            category = shortcut.get('category', '').strip()
            if category:
                categories.add(category)

        common_categories = ["System", "Navigation", "Text", "Media", "AutoHotkey", "General"]
        existing_sorted = sorted(categories)

        result = []
        for cat in common_categories:
            if cat in existing_sorted:
                result.append(cat)
                existing_sorted.remove(cat)
        result.extend(existing_sorted)
        return result

    def populate_fields(self):
        self.name_edit.setText(self.shortcut_data.get("name", ""))
        self.category_combo.setCurrentText(self.shortcut_data.get("category", ""))
        self.description_edit.setText(self.shortcut_data.get("description", ""))
        self.enabled_checkbox.setChecked(self.shortcut_data.get("enabled", True))

        if self.shortcut_type == "script":
            self.hotkey_edit.setText(self.shortcut_data.get("hotkey", ""))
            self.action_edit.setPlainText(self.shortcut_data.get("action", ""))
        else:
            self.trigger_edit.setText(self.shortcut_data.get("trigger", ""))
            self.replacement_edit.setPlainText(self.shortcut_data.get("replacement", ""))

    def accept_dialog(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Warning", "Name is required.")
            return

        category = self.category_combo.currentText().strip() or "General"
        description = self.description_edit.text().strip()
        enabled = self.enabled_checkbox.isChecked()

        if self.shortcut_type == "script":
            hotkey = self.hotkey_edit.text().strip()
            action = self.action_edit.toPlainText().strip()

            if not hotkey or not action:
                QMessageBox.warning(self, "Warning", "Both hotkey and action are required.")
                return

            shortcut_data = {
                "name": name,
                "category": category,
                "description": description,
                "hotkey": hotkey,
                "action": action,
                "enabled": enabled
            }
        else:
            trigger = self.trigger_edit.text().strip()
            replacement = self.replacement_edit.toPlainText().strip()

            if not trigger or not replacement:
                QMessageBox.warning(self, "Warning", "Both trigger and replacement are required.")
                return

            shortcut_data = {
                "name": name,
                "category": category,
                "description": description,
                "trigger": trigger,
                "replacement": replacement,
                "enabled": enabled
            }

        if self.shortcut_data:
            # Edit existing
            self.shortcut_data.update(shortcut_data)
        else:
            # Add new
            if self.shortcut_type == "script":
                self.parent_window.script_shortcuts.append(shortcut_data)
            else:
                self.parent_window.text_shortcuts.append(shortcut_data)

        self.parent_window.save_shortcuts_json()
        self.parent_window.update_display()
        self.accept()


class CategoryColorDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowTitle("Category Colors")
        self.setModal(True)
        self.resize(400, 500)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Category Colors"))

        # Color entries will be added dynamically
        self.color_entries = {}
        self.populate_colors(layout)

        # Buttons
        button_layout = QHBoxLayout()

        save_btn = QPushButton("Save Colors")
        save_btn.clicked.connect(self.save_colors)
        button_layout.addWidget(save_btn)

        reset_btn = QPushButton("Reset to Default")
        reset_btn.clicked.connect(self.reset_colors)
        button_layout.addWidget(reset_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def populate_colors(self, layout):
        # Get all categories
        all_categories = set()
        for shortcut in self.parent_window.script_shortcuts + self.parent_window.text_shortcuts:
            category = shortcut.get('category', 'General')
            if category:
                all_categories.add(category)

        for default_cat in self.parent_window.category_colors.keys():
            all_categories.add(default_cat)

        for category in sorted(all_categories):
            cat_layout = QHBoxLayout()

            current_color = self.parent_window.get_category_color(category)
            cat_label = QLabel(f"📁 {category}")
            cat_layout.addWidget(cat_label)

            color_edit = QLineEdit(current_color)
            color_edit.setPlaceholderText("e.g., #FF6B6B")
            cat_layout.addWidget(color_edit)

            self.color_entries[category] = color_edit
            layout.addLayout(cat_layout)

    def save_colors(self):
        for category, entry in self.color_entries.items():
            color = entry.text().strip()
            if color:
                self.parent_window.category_colors[category] = color

        self.parent_window.update_display()
        QMessageBox.information(self, "Success", "Category colors updated!")

    def reset_colors(self):
        default_colors = {
            "System": "#FF6B6B", "Navigation": "#4ECDC4", "Text": "#45B7D1",
            "Media": "#96CEB4", "AutoHotkey": "#FFEAA7", "General": "#DDA0DD",
            "Imported": "#FFA07A", "Tools": "#98D8C8", "Window": "#F7DC6F", "File": "#BB8FCE"
        }
        self.parent_window.category_colors.update(default_colors)
        self.close()
        CategoryColorDialog(self.parent_window).exec()


class AHKShortcutEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.script_shortcuts = []
        self.text_shortcuts = []
        self.category_colors = {
            "System": "#FF6B6B", "Navigation": "#4ECDC4", "Text": "#45B7D1",
            "Media": "#96CEB4", "AutoHotkey": "#FFEAA7", "General": "#DDA0DD",
            "Imported": "#FFA07A", "Tools": "#98D8C8", "Window": "#F7DC6F", "File": "#BB8FCE"
        }

        # Settings for remembering preferences
        self.settings = QSettings("AHKEditor", "ShortcutEditor")

        self.load_shortcuts_json()
        self.setup_ui()
        self.load_settings()
        self.update_display()

    def setup_ui(self):
        self.setWindowTitle("AutoHotkey Script Editor")
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        # Top controls
        top_layout = QHBoxLayout()

        # Add button with menu
        self.add_btn = QPushButton("+ Add")
        self.add_btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 8px 16px;")
        self.add_menu = QMenu()
        self.add_menu.addAction("Script Shortcut", lambda: self.open_add_dialog("script"))
        self.add_menu.addAction("Text Shortcut", lambda: self.open_add_dialog("text"))
        self.add_btn.setMenu(self.add_menu)
        top_layout.addWidget(self.add_btn)

        self.category_toggle = QCheckBox("\uf205")
        self.category_toggle.setChecked(True)
        self.category_toggle.toggled.connect(self.on_category_toggle)
        self.category_toggle.setToolTip("Group by Category")
        self.category_toggle.setStyleSheet("""
            QCheckBox {
                font-family: 'JetBrainsMono NFP', 'JetBrains Mono', monospace;
                font-size: 20px;
                padding: 12px;
                min-width: 0px;
                min-height: 48px;
                color: #61dafb;
            }
            QCheckBox::indicator {
                width: 0px;
                height: 0px;
            }
        """)
        top_layout.addWidget(self.category_toggle)

        # Color button
        self.colors_btn = QPushButton("Color")
        self.colors_btn.setStyleSheet("background-color: #8e44ad; color: white;")
        self.colors_btn.clicked.connect(self.open_color_dialog)
        self.colors_btn.setMaximumWidth(80)
        top_layout.addWidget(self.colors_btn)

        # Search with Record button
        self.search_container = QWidget()
        search_layout_inner = QHBoxLayout(self.search_container)
        search_layout_inner.setContentsMargins(0, 0, 0, 0)
        search_layout_inner.setSpacing(5)

        self.search_edit = HotkeyLineEdit()
        self.search_edit.setObjectName("search_edit")
        self.search_edit.setPlaceholderText("Search shortcuts...")
        self.search_edit.textChanged.connect(self.update_display)
        self.search_edit.setStyleSheet("border-radius: 10px; padding: 5px;")
        self.search_edit.setMinimumWidth(200)
        
        self.record_search_btn = QPushButton("⌨")
        self.record_search_btn.setCheckable(True)
        self.record_search_btn.setFixedWidth(40)
        self.record_search_btn.setToolTip("Record keys to search")
        self.record_search_btn.setStyleSheet("""
            QPushButton {
                font-family: 'JetBrainsMono NFP', 'JetBrains Mono', monospace;
                background-color: #3d3d3d;
                border: 1px solid #555;
                border-radius: 10px;
                color: white;
                font-size: 18px;
            }
            QPushButton:checked {
                background-color: #61dafb;
                color: black;
                border-color: #61dafb;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
                border-color: #61dafb;
            }
        """)
        self.record_search_btn.setToolTip("Open Shortcut Builder")
        self.record_search_btn.clicked.connect(lambda checked: self.search_edit.set_recording(checked))
        self.search_edit.record_button = self.record_search_btn

        search_layout_inner.addWidget(self.search_edit)
        search_layout_inner.addWidget(self.record_search_btn)
        top_layout.addWidget(self.search_container)

        # Generate button
        generate_btn = QPushButton("Generate AHK Script")
        generate_btn.setStyleSheet("background-color: #27ae60; color: black;")
        generate_btn.clicked.connect(self.generate_ahk_script)
        top_layout.addWidget(generate_btn)

        layout.addLayout(top_layout)

        # Text browser for HTML display
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(False)
        self.text_browser.anchorClicked.connect(self.handle_click)
        self.text_browser.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.text_browser.customContextMenuRequested.connect(self.show_context_menu)
        # Enable mouse tracking for double-click detection
        self.text_browser.setMouseTracking(True)
        self.text_browser.viewport().installEventFilter(self)
        layout.addWidget(self.text_browser)

        # Context menu for shortcuts
        self.context_menu = QMenu(self)
        self.edit_action = self.context_menu.addAction("Edit")
        self.remove_action = self.context_menu.addAction("Remove")
        self.edit_action.triggered.connect(self.edit_selected)
        self.remove_action.triggered.connect(self.remove_selected)

        central_widget.setLayout(layout)

        self.selected_shortcut = None
        self.selected_type = None

    def load_settings(self):
        """Load saved settings"""
        group_by_category = self.settings.value("group_by_category", True, type=bool)
        self.category_toggle.setChecked(group_by_category)

    def save_settings(self):
        """Save current settings"""
        self.settings.setValue("group_by_category", self.category_toggle.isChecked())

    def on_category_toggle(self):
        """Handle category toggle change"""
        # Update icon based on state
        if self.category_toggle.isChecked():
            self.category_toggle.setText("\uf205")  # Enabled icon
        else:
            self.category_toggle.setText("\uf204")  # Disabled icon

        self.save_settings()
        self.update_display()

    def closeEvent(self, event):
        """Save settings when closing"""
        self.save_settings()
        event.accept()

    def handle_click(self, url):
        """Handle clicks on shortcuts"""
        url_str = url.toString()
        if url_str.startswith("select://"):
            parts = url_str.replace("select://", "").split("/")
            if len(parts) == 2:
                shortcut_type, index = parts
                index = int(index)

                if shortcut_type == "script" and index < len(self.script_shortcuts):
                    self.selected_shortcut = self.script_shortcuts[index]
                    self.selected_type = "script"
                elif shortcut_type == "text" and index < len(self.text_shortcuts):
                    self.selected_shortcut = self.text_shortcuts[index]
                    self.selected_type = "text"

                # Update display to show selection
                self.update_display()

        elif url_str.startswith("toggle://"):
            parts = url_str.replace("toggle://", "").split("/")
            if len(parts) == 2:
                shortcut_type, index = parts
                index = int(index)

                # Toggle the enabled state
                if shortcut_type == "script" and index < len(self.script_shortcuts):
                    shortcut = self.script_shortcuts[index]
                    shortcut["enabled"] = not shortcut.get("enabled", True)
                elif shortcut_type == "text" and index < len(self.text_shortcuts):
                    shortcut = self.text_shortcuts[index]
                    shortcut["enabled"] = not shortcut.get("enabled", True)

                # Save and update display
                self.save_shortcuts_json()
                self.update_display()

    def show_context_menu(self, position):
        """Show context menu on right-click"""
        # Only show context menu if a shortcut is selected
        if self.selected_shortcut and self.selected_type:
            # Enable/disable actions based on selection
            self.edit_action.setEnabled(True)
            self.remove_action.setEnabled(True)
            self.context_menu.exec(self.text_browser.mapToGlobal(position))
        else:
            # Optionally show a disabled menu or no menu at all
            self.edit_action.setEnabled(False)
            self.remove_action.setEnabled(False)
            # For a cleaner UX, we won't show the menu if nothing is selected

    def eventFilter(self, obj, event):
        """Handle double-click events on the text browser"""
        if obj == self.text_browser.viewport() and event.type() == event.Type.MouseButtonDblClick:
            if event.button() == Qt.MouseButton.LeftButton:
                # Get the position of the click
                pos = event.pos()
                # Get the anchor at the click position
                anchor = self.text_browser.anchorAt(pos)
                
                if anchor:
                    # Handle the click to select the item first
                    from PyQt6.QtCore import QUrl
                    self.handle_click(QUrl(anchor))
                    # Then open the edit dialog
                    self.edit_selected()
                    
                return True  # Event handled
        return super().eventFilter(obj, event)

    def load_shortcuts_json(self):
        if os.path.exists(SHORTCUTS_JSON_PATH):
            try:
                with open(SHORTCUTS_JSON_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.script_shortcuts = data.get("script_shortcuts", [])
                    self.text_shortcuts = data.get("text_shortcuts", [])
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load shortcuts JSON: {e}")
                self.create_default_shortcuts()
        else:
            self.create_default_shortcuts()

    def create_default_shortcuts(self):
        self.script_shortcuts = [{
            "name": "Open Terminal", "category": "System", "description": "Opens PowerShell as admin",
            "hotkey": "!x", "enabled": True,
            "action": 'RunWait("pwsh -Command `"cd $env:USERPROFILE; Start-Process pwsh -Verb RunAs`"", , "Hide")'
        }]
        self.text_shortcuts = [
            {"name": "AHK Version 1", "category": "AutoHotkey", "description": "AutoHotkey v1 header",
             "trigger": ";v1", "replacement": "#Requires AutoHotkey v1.0", "enabled": True},
            {"name": "AHK Version 2", "category": "AutoHotkey", "description": "AutoHotkey v2 header",
             "trigger": ";v2", "replacement": "#Requires AutoHotkey v2.0", "enabled": True}
        ]

    def save_shortcuts_json(self):
        try:
            data = {"script_shortcuts": self.script_shortcuts, "text_shortcuts": self.text_shortcuts}
            with open(SHORTCUTS_JSON_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save shortcuts JSON: {e}")

    def get_category_color(self, category):
        return self.category_colors.get(category, "#B0B0B0")

    def update_display(self):
        # Save current scroll position
        scrollbar = self.text_browser.verticalScrollBar()
        scroll_position = scrollbar.value()

        search_query = self.search_edit.text().lower()
        group_by_category = self.category_toggle.isChecked()

        # Filter shortcuts
        filtered_script = [s for s in self.script_shortcuts
                          if search_query in f"{s.get('name', '')} {s.get('hotkey', '')} {s.get('description', '')} {s.get('category', '')}".lower()]
        filtered_text = [s for s in self.text_shortcuts
                        if search_query in f"{s.get('name', '')} {s.get('trigger', '')} {s.get('description', '')} {s.get('category', '')}".lower()]

        html = self.generate_html(filtered_script, filtered_text, group_by_category)
        self.text_browser.setHtml(html)

        # Restore scroll position after a brief delay to allow HTML to load
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(10, lambda: scrollbar.setValue(scroll_position))

    def generate_html(self, script_shortcuts, text_shortcuts, group_by_category):
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {
                    font-family: 'JetBrains Mono', 'Consolas', monospace;
                    margin: 20px;
                    background: #2b2b2b;
                    color: #ffffff;
                    font-size: 16px; /* Increased base font size */
                }
                .container { display: flex; gap: 20px; }
                .column { flex: 1; }
                .section-title {
                    font-size: 20px; /* Increased */
                    font-weight: bold;
                    margin: 25px 0 8px 0;
                    color: #61dafb;
                }
                .section-title:first-child {
                    margin-top: 5px;
                }
                .category-header {
                    font-size: 18px; /* Increased */
                    font-weight: bold;
                    margin: 25px 0 5px 0;
                    padding: 5px 10px;
                    border-radius: 5px;
                    background: #404040;
                }
                .category-header.first-in-section {
                    margin-top: 8px;
                }
                .shortcut-item {
                    padding: 10px 14px; /* Increased padding */
                    margin: 3px 0; /* Slightly increased margin */
                    border-radius: 5px;
                    cursor: pointer;
                    transition: background 0.2s;
                    border-left: 3px solid transparent;
                    display: flex;
                    align-items: center;
                }
                .shortcut-item:hover {
                    background: rgba(255,255,255,0.1);
                    border-left-color: #61dafb;
                }
                .shortcut-item.selected {
                    background: rgba(97, 218, 251, 0.2);
                    border-left-color: #61dafb;
                }
                .shortcut-key {
                    color: #ffffff;
                    font-weight: bold;
                    font-size: 16px; /* Increased */
                }
                .shortcut-separator {
                    color: #32CD32;
                    font-weight: bold;
                    margin: 0 8px;
                    font-size: 16px; /* Increased */
                }
                .shortcut-name {
                    color: #ffffff;
                    font-size: 16px; /* Increased */
                }
                .shortcut-desc {
                    color: #888;
                    font-size: 14px; /* Increased from 12px */
                }
                .status-enabled { color: #27ae60; }
                .status-disabled {
                    color: #e74c3c;
                    opacity: 0.6;
                }
                .indent { margin-left: 20px; }
                a { text-decoration: none; color: inherit; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="column">
                    <div class="section-title">Script Shortcuts</div>
        """

        if group_by_category:
            # Group script shortcuts by category
            script_categories = {}
            for shortcut in script_shortcuts:
                category = shortcut.get('category', 'General')
                if category not in script_categories:
                    script_categories[category] = []
                script_categories[category].append(shortcut)

            for i, category in enumerate(sorted(script_categories.keys())):
                color = self.get_category_color(category)
                first_class = " first-in-section" if i == 0 else ""
                html += f'<div class="category-header{first_class}" style="color: {color};">📁 {category}</div>'

                for shortcut in sorted(script_categories[category], key=lambda x: x.get('hotkey', '').lower()):
                    original_index = self.script_shortcuts.index(shortcut)
                    html += self.generate_shortcut_html(shortcut, "script", original_index, True)
        else:
            # Flat list
            for shortcut in sorted(script_shortcuts, key=lambda x: x.get('hotkey', '').lower()):
                original_index = self.script_shortcuts.index(shortcut)
                html += self.generate_shortcut_html(shortcut, "script", original_index, False)

        html += """
                </div>
                <div class="column">
                    <div class="section-title">Text Shortcuts</div>
        """

        if group_by_category:
            # Group text shortcuts by category
            text_categories = {}
            for shortcut in text_shortcuts:
                category = shortcut.get('category', 'General')
                if category not in text_categories:
                    text_categories[category] = []
                text_categories[category].append(shortcut)

            for i, category in enumerate(sorted(text_categories.keys())):
                color = self.get_category_color(category)
                first_class = " first-in-section" if i == 0 else ""
                html += f'<div class="category-header{first_class}" style="color: {color};">📁 {category}</div>'

                for shortcut in sorted(text_categories[category], key=lambda x: x.get('trigger', '').lower()):
                    original_index = self.text_shortcuts.index(shortcut)
                    html += self.generate_shortcut_html(shortcut, "text", original_index, True)
        else:
            # Flat list
            for shortcut in sorted(text_shortcuts, key=lambda x: x.get('trigger', '').lower()):
                original_index = self.text_shortcuts.index(shortcut)
                html += self.generate_shortcut_html(shortcut, "text", original_index, False)

        html += """
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def generate_shortcut_html(self, shortcut, shortcut_type, index, indented):
        enabled = shortcut.get('enabled', True)
        status = "✅" if enabled else "❌"
        status_class = "status-enabled" if enabled else "status-disabled"
        indent_class = "indent" if indented else ""

        # Check if this is the selected shortcut
        is_selected = (self.selected_shortcut == shortcut and self.selected_type == shortcut_type)
        selected_class = "selected" if is_selected else ""

        if shortcut_type == "script":
            key = shortcut.get('hotkey', '')
        else:
            key = shortcut.get('trigger', '')

        name = shortcut.get('name', 'Unnamed')
        description = shortcut.get('description', '')

        desc_html = f' <span class="shortcut-desc">({description[:25]}...)</span>' if len(description) > 25 else f' <span class="shortcut-desc">({description})</span>' if description else ''

        return f'''
        <div class="shortcut-item {indent_class} {status_class} {selected_class}">
            <a href="toggle://{shortcut_type}/{index}" style="text-decoration: none; margin-right: 8px;">
                <span class="{status_class}" style="cursor: pointer; font-size: 14px;">{status}</span>
            </a>
            <a href="select://{shortcut_type}/{index}" style="text-decoration: none; color: inherit; flex: 1;">
                <span class="shortcut-key">{key}</span>
                <span class="shortcut-separator">󰌌</span>
                <span class="shortcut-name">{name}</span>
                {desc_html}
            </a>
        </div>
        '''

    def open_add_dialog(self, shortcut_type):
        dialog = AddEditShortcutDialog(self, shortcut_type)
        dialog.exec()

    def edit_selected(self):
        if not self.selected_shortcut or not self.selected_type:
            QMessageBox.warning(self, "Warning", "Please select a shortcut to edit.")
            return

        dialog = AddEditShortcutDialog(self, self.selected_type, self.selected_shortcut)
        dialog.exec()


    def remove_selected(self):
        if not self.selected_shortcut or not self.selected_type:
            QMessageBox.warning(self, "Warning", "Please select a shortcut to remove.")
            return

        reply = QMessageBox.question(self, "Confirm", "Are you sure you want to remove this shortcut?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            if self.selected_type == "script":
                self.script_shortcuts.remove(self.selected_shortcut)
            else:
                self.text_shortcuts.remove(self.selected_shortcut)

            self.selected_shortcut = None
            self.selected_type = None
            self.save_shortcuts_json()
            self.update_display()

    def open_color_dialog(self):
        dialog = CategoryColorDialog(self)
        dialog.exec()

    def generate_ahk_script(self):
        try:
            output_lines = ["#Requires AutoHotkey v2.0", "#SingleInstance", "Persistent", ""]

            # Add enabled script shortcuts
            enabled_scripts = [s for s in self.script_shortcuts if s.get('enabled', True)]
            if enabled_scripts:
                output_lines.append(";! === SCRIPT SHORTCUTS ===")
                for shortcut in enabled_scripts:
                    output_lines.append(f";! {shortcut.get('name', 'Unnamed')}")
                    if shortcut.get('description'):
                        output_lines.append(f";! {shortcut.get('description')}")

                    action = shortcut.get('action', '')
                    hotkey = shortcut.get('hotkey', '')

                    if '\n' in action:
                        output_lines.append(f"{hotkey}:: {{")
                        for line in action.split('\n'):
                            if line.strip():
                                output_lines.append(f"    {line}")
                        output_lines.append("}")
                    else:
                        output_lines.append(f"{hotkey}::{action}")
                    output_lines.append("")

            # Add enabled text shortcuts
            enabled_texts = [s for s in self.text_shortcuts if s.get('enabled', True)]
            if enabled_texts:
                output_lines.append(";! === TEXT SHORTCUTS ===")
                for shortcut in enabled_texts:
                    output_lines.append(f";! {shortcut.get('name', 'Unnamed')}")
                    if shortcut.get('description'):
                        output_lines.append(f";! {shortcut.get('description')}")
                    
                    replacement = shortcut.get('replacement', '')
                    trigger = shortcut.get('trigger', '')
                    
                    if '\n' in replacement:
                        # TR mode (Text + Raw) + Escaping starting ( to avoid parser confusion
                        output_lines.append(f":TR:{trigger}::")
                        output_lines.append("(")
                        # If a line starts with (, AHK thinks it's a new continuation section.
                        # We must escape it with a backtick.
                        cleaned = "\n".join(["`" + line if line.startswith("(") else line for line in replacement.split("\n")])
                        output_lines.append(cleaned)
                        output_lines.append(")")
                    else:
                        output_lines.append(f":T:{trigger}::{replacement}")
                    output_lines.append("")

            output_file = "generated_shortcuts.ahk"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(output_lines))

            QMessageBox.information(self, "Success", f"AHK script generated successfully as '{output_file}'!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate AHK script: {e}")


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look

    # Set application font
    font = QFont("JetBrains Mono", 10)
    app.setFont(font)

    window = AHKShortcutEditor()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
