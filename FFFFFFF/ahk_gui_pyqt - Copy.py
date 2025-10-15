import sys
import json
import os
import re
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QPushButton, QLineEdit, QCheckBox, QDialog,
                            QDialogButtonBox, QLabel, QTextEdit, QComboBox, QMessageBox,
                            QSplitter, QFrame, QTextBrowser, QMenu)
from PyQt6.QtCore import Qt, pyqtSignal, QSettings
from PyQt6.QtGui import QFont, QTextCursor

AHK_SCRIPT_PATH = "ahk_v2.ahk"
SHORTCUTS_JSON_PATH = "ahk_shortcuts.json"

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
        layout = QVBoxLayout()
        
        # Name
        layout.addWidget(QLabel("Name:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., Open Terminal, Version 1 Text")
        layout.addWidget(self.name_edit)
        
        # Category
        layout.addWidget(QLabel("Category:"))
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        existing_categories = self.get_existing_categories()
        self.category_combo.addItems(existing_categories)
        layout.addWidget(self.category_combo)
        
        # Description
        layout.addWidget(QLabel("Description:"))
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("Brief description of what this does")
        layout.addWidget(self.description_edit)
        
        # Enabled checkbox
        self.enabled_checkbox = QCheckBox("Enabled (include in generated script)")
        self.enabled_checkbox.setChecked(True)
        layout.addWidget(self.enabled_checkbox)
        
        if self.shortcut_type == "script":
            # Hotkey
            layout.addWidget(QLabel("Hotkey:"))
            self.hotkey_edit = QLineEdit()
            self.hotkey_edit.setPlaceholderText("e.g., !Space, ^!n, #x")
            layout.addWidget(self.hotkey_edit)
            
            # Action
            layout.addWidget(QLabel("Action:"))
            self.action_edit = QTextEdit()
            self.action_edit.setMaximumHeight(100)
            layout.addWidget(self.action_edit)
        else:
            # Trigger
            layout.addWidget(QLabel("Trigger (without ::):"))
            self.trigger_edit = QLineEdit()
            self.trigger_edit.setPlaceholderText("e.g., ;v1, ;run")
            layout.addWidget(self.trigger_edit)
            
            # Replacement
            layout.addWidget(QLabel("Replacement Text:"))
            self.replacement_edit = QTextEdit()
            self.replacement_edit.setMaximumHeight(100)
            layout.addWidget(self.replacement_edit)
        
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
                min-width: 48px;
                min-height: 48px;
                color: #61dafb;
            }
            QCheckBox::indicator {
                width: 0px;
                height: 0px;
            }
        """)
        top_layout.addWidget(self.category_toggle)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search shortcuts...")
        self.search_edit.textChanged.connect(self.update_display)
        top_layout.addWidget(self.search_edit)
        
        layout.addLayout(top_layout)
        
        # Text browser for HTML display
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(False)
        self.text_browser.anchorClicked.connect(self.handle_click)
        layout.addWidget(self.text_browser)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        colors_btn = QPushButton("Category Colors")
        colors_btn.setStyleSheet("background-color: #8e44ad; color: white;")
        colors_btn.clicked.connect(self.open_color_dialog)
        button_layout.addWidget(colors_btn)
        
        generate_btn = QPushButton("Generate AHK Script")
        generate_btn.setStyleSheet("background-color: #27ae60; color: white;")
        generate_btn.clicked.connect(self.generate_ahk_script)
        button_layout.addWidget(generate_btn)
        
        layout.addLayout(button_layout)
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
        
        elif url_str.startswith("edit://"):
            parts = url_str.replace("edit://", "").split("/")
            if len(parts) == 2:
                shortcut_type, index = parts
                index = int(index)
                
                # Set selected shortcut
                if shortcut_type == "script" and index < len(self.script_shortcuts):
                    self.selected_shortcut = self.script_shortcuts[index]
                    self.selected_type = "script"
                elif shortcut_type == "text" and index < len(self.text_shortcuts):
                    self.selected_shortcut = self.text_shortcuts[index]
                    self.selected_type = "text"
                
                # Open edit dialog
                self.edit_selected()
        
        elif url_str.startswith("delete://"):
            parts = url_str.replace("delete://", "").split("/")
            if len(parts) == 2:
                shortcut_type, index = parts
                index = int(index)
                
                # Set selected shortcut
                if shortcut_type == "script" and index < len(self.script_shortcuts):
                    self.selected_shortcut = self.script_shortcuts[index]
                    self.selected_type = "script"
                elif shortcut_type == "text" and index < len(self.text_shortcuts):
                    self.selected_shortcut = self.text_shortcuts[index]
                    self.selected_type = "text"
                
                # Delete the shortcut
                self.remove_selected()
    
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
                }
                .container { display: flex; gap: 20px; }
                .column { flex: 1; }
                .section-title { 
                    font-size: 18px; 
                    font-weight: bold; 
                    margin: 25px 0 8px 0; 
                    color: #61dafb;
                }
                .section-title:first-child {
                    margin-top: 5px;
                }
                .category-header { 
                    font-size: 16px; 
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
                    padding: 8px 12px; 
                    margin: 2px 0; 
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
                }
                .shortcut-separator { 
                    color: #32CD32; 
                    font-weight: bold; 
                    margin: 0 8px;
                }
                .shortcut-name { 
                    color: #ffffff; 
                }
                .shortcut-desc { 
                    color: #888; 
                    font-size: 12px; 
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
            <a href="edit://{shortcut_type}/{index}" style="text-decoration: none; margin-left: 8px;">
                <span style="color: #4d94ff; cursor: pointer; font-size: 16px;">●</span>
            </a>
            <a href="delete://{shortcut_type}/{index}" style="text-decoration: none; margin-left: 4px;">
                <span style="color: #ff4d4d; cursor: pointer; font-size: 16px;">●</span>
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
        
        # Store the current selection
        current_shortcut = self.selected_shortcut
        current_type = self.selected_type
        
        dialog = AddEditShortcutDialog(self, self.selected_type, self.selected_shortcut)
        dialog.exec()
        
        # Restore selection after dialog closes
        self.selected_shortcut = current_shortcut
        self.selected_type = current_type
        self.update_display()
    

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
        else:
            # User clicked No, so we need to refresh the display to maintain selection
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
                    output_lines.append(f"::{shortcut.get('trigger', '')}::{shortcut.get('replacement', '')}")
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