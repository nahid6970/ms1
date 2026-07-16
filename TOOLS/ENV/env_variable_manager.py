import sys
import os
import winreg
import json
import re
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QLineEdit, QGroupBox, QListWidget, 
                             QMessageBox, QInputDialog, QTabWidget, QTextEdit, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, 
                             QDialog, QDialogButtonBox, QFormLayout)
from PyQt6.QtCore import Qt, QByteArray
from PyQt6.QtGui import QFont, QFontDatabase, QColor

# CYBERPUNK THEME PALETTE
CP_BG = "#050505"
CP_PANEL = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN = "#00F0FF"
CP_RED = "#FF003C"
CP_GREEN = "#00ff21"
CP_ORANGE = "#ff934b"
CP_DIM = "#3a3a3a"
CP_TEXT = "#E0E0E0"
CP_SUBTEXT = "#808080"

class EnvVariableManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ALIAS & CONTEXT MANAGER v1.0")
        self.resize(1300, 750)
        
        # Initialize Icons Directory
        self.icons_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon")
        os.makedirs(self.icons_dir, exist_ok=True)
        
        # Apply Cyberpunk Theme
        self.apply_theme()
        
        # Main Layout
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        # Top Bar (Header + Settings button)
        top_bar = QHBoxLayout()
        title_label = QLabel("ALIAS & CONTEXT MANAGER")
        title_label.setStyleSheet(f"font-size: 14pt; font-weight: bold; color: {CP_YELLOW};")
        settings_btn = QPushButton("⚙️ SETTINGS")
        settings_btn.setStyleSheet(f"background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; color: {CP_YELLOW}; padding: 5px 15px; font-weight: bold;")
        settings_btn.clicked.connect(self.show_settings)
        
        top_bar.addWidget(title_label)
        top_bar.addStretch()
        top_bar.addWidget(settings_btn)
        main_layout.addLayout(top_bar)
        
        # Status Bar
        self.status_label = QLabel("SYSTEM READY")
        self.status_label.setStyleSheet(f"color: {CP_GREEN}; font-weight: bold; padding: 5px;")
        
        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_alias_tab(), "ALIASES")
        self.tabs.addTab(self.create_context_tab(), "CONTEXT MENU")
        main_layout.addWidget(self.tabs)
        
        # Add status bar at bottom
        main_layout.addWidget(self.status_label)
    
    def apply_theme(self):
        """Apply cyberpunk theme to the application"""
        target_font = "JetBrainsMono NFP"
        for family in QFontDatabase.families():
            if "JetBrainsMono" in family and ("NFP" in family or "NF" in family or "Nerd Font" in family):
                target_font = family
                break
                
        self.setStyleSheet(f"""
            * {{ font-family: '{target_font}', 'JetBrainsMono NFP', 'Consolas'; }}
            QMainWindow {{ background-color: {CP_BG}; }}
            QWidget {{ 
                color: {CP_TEXT}; 
                font-family: '{target_font}', 'JetBrainsMono NFP';
                font-size: 10pt; 
            }}
            QLabel, QPushButton, QLineEdit, QTextEdit, QListWidget, QTableWidget, QGroupBox, QTabBar::tab {{
                font-family: '{target_font}', 'JetBrainsMono NFP';
            }}
            
            QLineEdit, QTextEdit {{
                background-color: {CP_PANEL}; 
                color: {CP_CYAN}; 
                border: 1px solid {CP_DIM}; 
                padding: 6px;
                selection-background-color: {CP_CYAN};
                selection-color: #000000;
            }}
            
            QPushButton {{
                background-color: {CP_DIM}; 
                border: 1px solid {CP_DIM}; 
                color: white; 
                padding: 8px 16px; 
                font-weight: bold;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: #2a2a2a; 
                border: 1px solid {CP_YELLOW}; 
                color: {CP_YELLOW};
            }}
            
            QListWidget, QTableWidget {{
                background-color: {CP_PANEL};
                color: {CP_TEXT};
                border: 1px solid {CP_DIM};
                padding: 5px;
                gridline-color: {CP_DIM};
            }}
            QListWidget::item:selected, QTableWidget::item:selected {{
                background-color: {CP_CYAN};
                color: {CP_BG};
            }}
            
            QHeaderView::section {{
                background-color: {CP_DIM};
                color: {CP_YELLOW};
                padding: 5px;
                border: 1px solid {CP_BG};
            }}
            
            QGroupBox {{
                border: 1px solid {CP_DIM}; 
                margin-top: 10px; 
                padding-top: 10px; 
                font-weight: bold; 
                color: {CP_YELLOW};
            }}
            
            QTabWidget::pane {{
                border: 1px solid {CP_DIM};
                background-color: {CP_BG};
            }}
            QTabBar::tab {{
                background-color: {CP_PANEL};
                color: {CP_TEXT};
                padding: 10px 20px;
                border: 1px solid {CP_DIM};
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {CP_DIM};
                color: {CP_YELLOW};
                border-bottom: 2px solid {CP_YELLOW};
            }}
        """)

    def create_alias_tab(self):
        """Create command aliases manager tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        info = QLabel("💡 Aliases work in CMD, PowerShell & Git Bash via auto-load scripts")
        info.setStyleSheet(f"color: {CP_CYAN}; padding: 5px;")
        layout.addWidget(info)
        
        list_group = QGroupBox("COMMAND ALIASES")
        list_layout = QVBoxLayout()
        self.alias_list = QListWidget()
        list_layout.addWidget(self.alias_list)
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        controls_layout = QHBoxLayout()
        add_btn = QPushButton("➕ ADD ALIAS")
        edit_btn = QPushButton("✏️ EDIT")
        remove_btn = QPushButton("❌ REMOVE")
        apply_btn = QPushButton("⚡ APPLY ALL")
        refresh_btn = QPushButton("🔄 REFRESH")
        setup_btn = QPushButton("🔧 AUTO-SETUP")
        
        add_btn.clicked.connect(self.add_alias)
        edit_btn.clicked.connect(self.edit_alias)
        remove_btn.clicked.connect(self.remove_alias)
        apply_btn.clicked.connect(self.apply_all_aliases)
        refresh_btn.clicked.connect(self.load_aliases)
        setup_btn.clicked.connect(self.setup_auto_load)
        
        controls_layout.addWidget(add_btn)
        controls_layout.addWidget(edit_btn)
        controls_layout.addWidget(remove_btn)
        controls_layout.addWidget(apply_btn)
        controls_layout.addWidget(refresh_btn)
        controls_layout.addWidget(setup_btn)
        layout.addLayout(controls_layout)
        
        self.aliases = {}
        self.alias_dir = os.path.join(os.path.expanduser("~"), ".aliases")
        os.makedirs(self.alias_dir, exist_ok=True)
        self.load_aliases()
        
        return widget

    def create_context_tab(self):
        """Create tab for Windows Right-Click Context Menu customization"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        list_group = QGroupBox("CONTEXT MENU ENTRIES")
        list_layout = QVBoxLayout()
        self.context_table = QTableWidget()
        self.context_table.setColumnCount(3)
        self.context_table.setHorizontalHeaderLabels(["Menu Label", "Type", "Command / Script"])
        self.context_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.context_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.context_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.context_table.setColumnWidth(0, 300)
        self.context_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.context_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        list_layout.addWidget(self.context_table)
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        controls_layout = QHBoxLayout()
        add_btn = QPushButton("➕ ADD ENTRY")
        add_group_btn = QPushButton("📁 ADD GROUP")
        edit_btn = QPushButton("✏️ EDIT")
        remove_btn = QPushButton("❌ REMOVE")
        up_btn = QPushButton("⬆️ MOVE UP")
        down_btn = QPushButton("⬇️ MOVE DOWN")
        refresh_btn = QPushButton("🔄 REFRESH")
        apply_svg_btn = QPushButton("⚡ APPLY SVGS")
        
        add_btn.clicked.connect(self.add_context_entry)
        add_group_btn.clicked.connect(self.add_context_group)
        edit_btn.clicked.connect(self.edit_context_entry)
        remove_btn.clicked.connect(self.remove_context_entry)
        up_btn.clicked.connect(self.move_context_up)
        down_btn.clicked.connect(self.move_context_down)
        refresh_btn.clicked.connect(self.load_context_entries)
        apply_svg_btn.clicked.connect(self.apply_svg_icons)
        
        controls_layout.addWidget(add_btn)
        controls_layout.addWidget(add_group_btn)
        controls_layout.addWidget(edit_btn)
        controls_layout.addWidget(remove_btn)
        controls_layout.addWidget(up_btn)
        controls_layout.addWidget(down_btn)
        controls_layout.addWidget(refresh_btn)
        controls_layout.addWidget(apply_svg_btn)
        layout.addLayout(controls_layout)
        
        self.load_context_entries()
        return widget

    def show_settings(self):
        """Show settings dialog"""
        from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLabel
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        dialog.setMinimumWidth(400)
        layout = QVBoxLayout(dialog)
        
        title = QLabel("⚙️ SYSTEM SETTINGS")
        title.setStyleSheet(f"font-size: 12pt; font-weight: bold; color: {CP_YELLOW}; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Import button
        import_btn = QPushButton("📥 IMPORT FROM data.json")
        import_btn.setMinimumHeight(40)
        import_btn.setStyleSheet(f"background-color: {CP_PANEL}; border: 1px solid {CP_ORANGE}; color: {CP_ORANGE}; font-weight: bold;")
        import_btn.clicked.connect(lambda: [self.import_config(), dialog.accept()])
        layout.addWidget(import_btn)
        
        layout.addSpacing(10)
        
        # We can add other useful things in future here
        future_placeholder = QLabel("Additional settings can be added here in the future.")
        future_placeholder.setStyleSheet(f"color: {CP_SUBTEXT}; font-style: italic;")
        layout.addWidget(future_placeholder)
        
        layout.addStretch()
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.exec()

    # ===== ALIAS METHODS =====
    def load_aliases(self):
        self.alias_list.clear()
        alias_file = os.path.join(self.alias_dir, "aliases.json")
        try:
            if os.path.exists(alias_file):
                with open(alias_file, 'r') as f:
                    self.aliases = json.load(f)
            else:
                self.aliases = {"ll": "ls -la", "gs": "git status", "ga": "git add", "gc": "git commit", "gp": "git push", "gl": "git log --oneline", "cls": "clear"}
                self.save_aliases()
            for name, command in self.aliases.items():
                self.alias_list.addItem(f"{name} → {command}")
            self.set_status(f"Loaded {len(self.aliases)} aliases", CP_GREEN)
        except Exception as e:
            self.set_status(f"Error loading aliases: {str(e)}", CP_RED)

    def save_aliases(self):
        alias_file = os.path.join(self.alias_dir, "aliases.json")
        try:
            with open(alias_file, 'w') as f:
                json.dump(self.aliases, f, indent=2)
            self.generate_cmd_loader()
            self.generate_powershell_loader()
            self.generate_bash_loader()
            self.export_config(silent=True)
            self.set_status("Aliases saved & scripts generated", CP_GREEN)
        except Exception as e:
            self.set_status(f"Error saving aliases: {str(e)}", CP_RED)

    def generate_cmd_loader(self):
        loader_path = os.path.join(self.alias_dir, "aliases.cmd")
        with open(loader_path, 'w') as f:
            f.write("@echo off\nREM Auto-generated alias loader for CMD\n")
            for name, command in self.aliases.items():
                f.write(f"doskey {name}={command}\n")

    def generate_powershell_loader(self):
        loader_path = os.path.join(self.alias_dir, "aliases.ps1")
        with open(loader_path, 'w', encoding='utf-8') as f:
            f.write("# Auto-generated alias loader for PowerShell\n")
            for name, command in self.aliases.items():
                f.write(f"function {name} {{ {command} @args }}\n")

    def generate_bash_loader(self):
        loader_path = os.path.join(self.alias_dir, "aliases.sh")
        with open(loader_path, 'w') as f:
            f.write("#!/bin/bash\n# Auto-generated alias loader for Bash\n")
            for name, command in self.aliases.items():
                f.write(f"alias {name}='{command}'\n")

    def setup_auto_load(self):
        try:
            ps_profiles = [
                os.path.join(os.path.expanduser("~"), "Documents", "WindowsPowerShell", "Microsoft.PowerShell_profile.ps1"),
                os.path.join(os.path.expanduser("~"), "Documents", "PowerShell", "Microsoft.PowerShell_profile.ps1")
            ]
            loader_line = f". '{os.path.join(self.alias_dir, 'aliases.ps1')}'\n"
            for ps_profile in ps_profiles:
                os.makedirs(os.path.dirname(ps_profile), exist_ok=True)
                existing = ""
                if os.path.exists(ps_profile):
                    with open(ps_profile, 'r', encoding='utf-8') as f: existing = f.read()
                if loader_line.strip() not in existing:
                    with open(ps_profile, 'a', encoding='utf-8') as f:
                        f.write(f"\n# Auto-load aliases\n{loader_line}")
            
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Command Processor", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "AutoRun", 0, winreg.REG_SZ, os.path.join(self.alias_dir, "aliases.cmd"))
            winreg.CloseKey(key)

            bashrc = os.path.join(os.path.expanduser("~"), ".bashrc")
            bash_loader_line = f"source ~/.aliases/aliases.sh\n"
            existing_bash = ""
            if os.path.exists(bashrc):
                with open(bashrc, 'r') as f: existing_bash = f.read()
            if bash_loader_line.strip() not in existing_bash:
                with open(bashrc, 'a') as f: f.write(f"\n# Auto-load aliases\n{bash_loader_line}")

            QMessageBox.information(self, "Setup Complete", "Auto-load setup complete for CMD, PS, and Bash.")
        except Exception as e:
            self.set_status(f"Setup error: {str(e)}", CP_RED)

    def apply_all_aliases(self):
        for name, command in self.aliases.items():
            os.system(f'doskey {name}={command}')
        self.set_status(f"Applied {len(self.aliases)} aliases to current session", CP_GREEN)

    def add_alias(self):
        name, ok1 = QInputDialog.getText(self, "Add Alias", "Alias name:")
        if ok1 and name:
            command, ok2 = QInputDialog.getText(self, "Add Alias", f"Command for '{name}':")
            if ok2 and command:
                self.aliases[name] = command
                self.save_aliases(); self.load_aliases()

    def edit_alias(self):
        current = self.alias_list.currentItem()
        if current and " → " in current.text():
            old_name, old_command = current.text().split(" → ", 1)
            new_name, ok1 = QInputDialog.getText(self, "Edit Alias", "Alias Name:", text=old_name)
            if ok1 and new_name:
                new_command, ok2 = QInputDialog.getText(self, "Edit Alias", f"Command for '{new_name}':", text=old_command)
                if ok2 and new_command:
                    if new_name != old_name: del self.aliases[old_name]
                    self.aliases[new_name] = new_command
                    self.save_aliases(); self.load_aliases()

    def remove_alias(self):
        current = self.alias_list.currentItem()
        if current and " → " in current.text():
            name = current.text().split(" → ", 1)[0]
            if QMessageBox.question(self, "Confirm", f"Delete alias '{name}'?") == QMessageBox.StandardButton.Yes:
                if name in self.aliases:
                    del self.aliases[name]
                    self.save_aliases(); self.load_aliases()

    # ===== CONTEXT MENU METHODS =====
    def load_context_entries(self):
        self.context_table.setRowCount(0)
        self._add_scope_header("FOLDERS")
        self._scan_shell_keys_hkcu(r"Software\Classes\Directory\shell", "Folder", winreg.HKEY_CURRENT_USER)
        self._add_scope_header("BACKGROUND")
        self._scan_shell_keys_hkcu(r"Software\Classes\Directory\Background\shell", "Background", winreg.HKEY_CURRENT_USER)
        self._add_scope_header("FILES")
        self._scan_shell_keys_hkcu(r"Software\Classes\*\shell", "All Files", winreg.HKEY_CURRENT_USER)

    def _add_scope_header(self, title):
        row = self.context_table.rowCount()
        self.context_table.insertRow(row)
        item = QTableWidgetItem(title)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setBackground(QColor(CP_DIM))
        item.setForeground(QColor(CP_YELLOW))
        item.setFlags(Qt.ItemFlag.NoItemFlags)
        self.context_table.setItem(row, 0, item)
        self.context_table.setSpan(row, 0, 1, 3)

    def _scan_shell_keys_hkcu(self, base_path, scope_label, hkey, indent=""):
        try:
            key = winreg.OpenKey(hkey, base_path, 0, winreg.KEY_READ)
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    if subkey_name.lower() in ["cmd", "powershell", "anycode", "wsl"]:
                        i += 1; continue
                    full_path = f"{base_path}\\{subkey_name}"
                    label = subkey_name
                    is_group = False
                    cmd = ""
                    try:
                        subkey = winreg.OpenKey(hkey, full_path, 0, winreg.KEY_READ)
                        try: label, _ = winreg.QueryValueEx(subkey, "MUIVerb")
                        except: pass
                        winreg.CloseKey(subkey)
                        
                        cmd_key = winreg.OpenKey(hkey, f"{full_path}\\command", 0, winreg.KEY_READ)
                        cmd, _ = winreg.QueryValueEx(cmd_key, "")
                        winreg.CloseKey(cmd_key)
                    except:
                        try:
                            sk = winreg.OpenKey(hkey, f"{full_path}\\shell", 0, winreg.KEY_READ)
                            winreg.CloseKey(sk); is_group = True; cmd = "(Cascading Menu)"
                        except: pass
                    
                    row = self.context_table.rowCount()
                    self.context_table.insertRow(row)
                    item = QTableWidgetItem(f"{indent}{label}")
                    item.setData(Qt.ItemDataRole.UserRole, full_path)
                    self.context_table.setItem(row, 0, item)
                    self.context_table.setItem(row, 1, QTableWidgetItem("GROUP" if is_group else "ENTRY"))
                    self.context_table.setItem(row, 2, QTableWidgetItem(cmd))
                    
                    if is_group: self._scan_shell_keys_hkcu(f"{full_path}\\shell", scope_label, hkey, indent + "  ↳ ")
                    i += 1
                except OSError: break
            winreg.CloseKey(key)
        except: pass

    def add_context_separator(self):
        """Add a separator before the next item or as a standalone"""
        parent_path = ""
        row = self.context_table.currentRow()
        if row >= 0:
            type_text = self.context_table.item(row, 1).text()
            if type_text == "GROUP":
                parent_path = self.context_table.item(row, 0).data(Qt.ItemDataRole.UserRole)

        name = f"Sep_{datetime.now().strftime('%H%M%S')}"
        try:
            if parent_path:
                hkcu_base = parent_path.replace("Directory\\", "Software\\Classes\\Directory\\")
                self._create_separator_entry(rf"{hkcu_base}\shell\{name}")
            else:
                self._create_separator_entry(rf"Software\Classes\Directory\shell\{name}")
                self._create_separator_entry(rf"Software\Classes\Directory\Background\shell\{name}")
            
            self.load_context_entries()
            self.export_config(silent=True)
            self.set_status("Separator added", CP_GREEN)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _create_separator_entry(self, path):
        """Helper to create registry separator"""
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, path)
        winreg.SetValueEx(key, "CommandFlags", 0, winreg.REG_DWORD, 0x20) # 0x20 = Separator
        winreg.CloseKey(key)

    def set_context_icon(self):
        """Set icon for selected context menu item"""
        row = self.context_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Select an item first!")
            return
            
        full_path = self.context_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        icon_path, _ = QFileDialog.getOpenFileName(self, "Select Icon File", "", 
                                                  "Icons (*.ico *.exe *.dll);;All Files (*.*)")
        if icon_path:
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, full_path, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icon_path)
                winreg.CloseKey(key)
                
                self.load_context_entries()
                self.set_status("Icon updated", CP_GREEN)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def add_context_group(self):
        """Add a new cascading menu group"""
        # Check if a group is selected to add a sub-group
        parent_path = ""
        row = self.context_table.currentRow()
        if row >= 0:
            type_text = self.context_table.item(row, 1).text()
            if type_text == "GROUP":
                parent_path = self.context_table.item(row, 0).data(Qt.ItemDataRole.UserRole)

        from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QCheckBox
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Context Group")
        dialog_layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        label_edit = QLineEdit()
        label_edit.setPlaceholderText("e.g. 'My AI Tools'")
        form_layout.addRow("Group Label:", label_edit)
        
        dialog_layout.addLayout(form_layout)
        
        # Scope selection (only if not adding to a group)
        scope_group = None
        cb_files = cb_folders = cb_background = None
        if not parent_path:
            scope_group = QGroupBox("Where should this group appear?")
            scope_layout = QVBoxLayout()
            cb_files = QCheckBox("Files")
            cb_folders = QCheckBox("Folders")
            cb_background = QCheckBox("Folder Background")
            cb_files.setChecked(True)
            scope_layout.addWidget(cb_files)
            scope_layout.addWidget(cb_folders)
            scope_layout.addWidget(cb_background)
            scope_group.setLayout(scope_layout)
            dialog_layout.addWidget(scope_group)
            
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        dialog_layout.addWidget(buttons)
        
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
            
        name = label_edit.text().strip()
        if not name:
            return
            
        try:
            if parent_path:
                # Nested group - parent_path is already in HKCU format
                path = rf"{parent_path}\shell\{name}"
                self._create_group_entry(path)
            else:
                if cb_files.isChecked():
                    self._create_group_entry(rf"Software\Classes\*\shell\{name}")
                if cb_folders.isChecked():
                    self._create_group_entry(rf"Software\Classes\Directory\shell\{name}")
                if cb_background.isChecked():
                    self._create_group_entry(rf"Software\Classes\Directory\Background\shell\{name}")
            self.load_context_entries()
            self.export_config(silent=True)
            self.set_status(f"Added context group: {name}", CP_GREEN)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add group: {str(e)}")

    def _create_group_entry(self, path):
        """Helper to create a cascading menu group in registry"""
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, path)
        # Get the leaf name for the label
        label = path.split('\\')[-1]
        winreg.SetValueEx(key, "MUIVerb", 0, winreg.REG_SZ, label)
        winreg.SetValueEx(key, "SubCommands", 0, winreg.REG_SZ, "")
        winreg.CreateKey(key, "shell")
        winreg.CloseKey(key)

    def add_context_entry(self):
        """Add a new right-click context menu entry"""
        # Check if a group is selected to add a child entry
        parent_path = ""
        row = self.context_table.currentRow()
        if row >= 0:
            type_text = self.context_table.item(row, 1).text()
            if type_text == "GROUP":
                parent_path = self.context_table.item(row, 0).data(Qt.ItemDataRole.UserRole)

        # Create dialog with all fields
        from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QCheckBox
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Context Entry")
        dialog.setMinimumWidth(700)
        dialog_layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        
        # Menu label
        label_edit = QLineEdit()
        label_edit.setPlaceholderText("e.g. 'Open Terminal Here'")
        form_layout.addRow("Menu Label:", label_edit)
        
        # Command
        cmd_layout = QHBoxLayout()
        cmd_edit = QTextEdit()
        cmd_edit.setPlaceholderText("Use %V for directory, %1 for file path")
        cmd_edit.setMaximumHeight(60)
        cmd_layout.addWidget(cmd_edit)
        
        help_btn = QPushButton("💡 Help")
        help_btn.setToolTip("Click to see detailed command guides for CMD, PowerShell, WT, and more!")
        help_btn.setFixedWidth(70)
        help_btn.clicked.connect(self.show_command_help)
        cmd_layout.addWidget(help_btn)
        
        form_layout.addRow("Command:", cmd_layout)
        
        # SVG Icon Code
        svg_edit = QTextEdit()
        svg_edit.setPlaceholderText("Paste raw SVG XML code here (e.g. <svg ...> ... </svg>)")
        svg_edit.setMaximumHeight(100)
        form_layout.addRow("SVG Icon Code:", svg_edit)
        
        dialog_layout.addLayout(form_layout)
        
        # Scope selection (only if not adding to a group)
        scope_group = None
        cb_files = cb_folders = cb_background = None
        if not parent_path:
            scope_group = QGroupBox("Where should this appear?")
            scope_layout = QVBoxLayout()
            
            cb_files = QCheckBox("Files (right-click on any file)")
            cb_folders = QCheckBox("Folders (right-click on folder)")
            cb_background = QCheckBox("Folder Background (right-click on empty space)")
            
            cb_files.setChecked(True)
            
            scope_layout.addWidget(cb_files)
            scope_layout.addWidget(cb_folders)
            scope_layout.addWidget(cb_background)
            scope_group.setLayout(scope_layout)
            dialog_layout.addWidget(scope_group)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        dialog_layout.addWidget(buttons)
        
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        name = label_edit.text().strip()
        cmd = cmd_edit.toPlainText().strip()
        svg_content = svg_edit.toPlainText().strip()
        
        if not name or not cmd:
            QMessageBox.warning(self, "Error", "Label and Command are required!")
            return
            
        icon = ""
        if svg_content:
            compiled_ico = self.compile_svg_to_ico(svg_content, name)
            if compiled_ico:
                icon = compiled_ico
        else:
            svg_content = None
        
        try:
            if parent_path:
                # Add as child of selected group
                self._create_reg_entry(rf"{parent_path}\shell\{name}", cmd, icon, svg_content)
                self.load_context_entries()
                self.export_config(silent=True)
                self.set_status(f"Added context menu entry: {name} to group", CP_GREEN)
            else:
                # Create entries based on selection
                if cb_files.isChecked():
                    self._create_reg_entry(rf"Software\Classes\*\shell\{name}", cmd, icon, svg_content)
                if cb_folders.isChecked():
                    self._create_reg_entry(rf"Software\Classes\Directory\shell\{name}", cmd, icon, svg_content)
                if cb_background.isChecked():
                    self._create_reg_entry(rf"Software\Classes\Directory\Background\shell\{name}", cmd, icon, svg_content)
                
                self.load_context_entries()
                self.export_config(silent=True)
                self.set_status(f"Added context menu entry: {name}", CP_GREEN)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add entry: {str(e)}")

    def edit_context_entry(self):
        """Edit selected context menu entry"""
        row = self.context_table.currentRow()
        if row < 0:
            return
            
        old_full_path = self.context_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        old_name = old_full_path.split('\\')[-1]
        type_text = self.context_table.item(row, 1).text()
        old_cmd = self.context_table.item(row, 2).text()
        
        # Get current label (MUIVerb) and IconSVG from registry
        old_label = old_name
        old_svg = ""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, old_full_path, 0, winreg.KEY_READ)
            try:
                old_label, _ = winreg.QueryValueEx(key, "MUIVerb")
            except:
                pass
            try:
                old_svg, _ = winreg.QueryValueEx(key, "IconSVG")
            except:
                pass
            winreg.CloseKey(key)
        except:
            pass
        
        # Create dialog with form layout
        from PyQt6.QtWidgets import QDialog, QDialogButtonBox
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Context Entry")
        dialog.setMinimumWidth(700)
        dialog_layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        
        # Label field (what user sees in context menu)
        label_edit = QLineEdit(old_label)
        form_layout.addRow("Display Label:", label_edit)
        
        # Command field (only for ENTRY type)
        cmd_edit = None
        if type_text == "ENTRY":
            cmd_layout = QHBoxLayout()
            cmd_edit = QTextEdit()
            cmd_edit.setPlainText(old_cmd)
            cmd_edit.setMaximumHeight(60)
            cmd_layout.addWidget(cmd_edit)
            
            help_btn = QPushButton("💡 Help")
            help_btn.setToolTip("Click to see detailed command guides for CMD, PowerShell, WT, and more!")
            help_btn.setFixedWidth(70)
            help_btn.clicked.connect(self.show_command_help)
            cmd_layout.addWidget(help_btn)
            
            form_layout.addRow("Command:", cmd_layout)
        
        # SVG Icon Code field
        svg_edit = QTextEdit()
        svg_edit.setPlainText(old_svg)
        svg_edit.setPlaceholderText("Paste raw SVG XML code here (e.g. <svg ...> ... </svg>)")
        svg_edit.setMaximumHeight(100)
        form_layout.addRow("SVG Icon Code:", svg_edit)
        
        dialog_layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        dialog_layout.addWidget(button_box)
        
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        new_label = label_edit.text().strip()
        new_cmd = cmd_edit.toPlainText().strip() if cmd_edit else "(Cascading Menu)"
        svg_content = svg_edit.toPlainText().strip()
        
        if not new_label:
            return
            
        if type_text == "ENTRY" and new_cmd:
            new_cmd = new_cmd.replace("{path}", "\"%V\"").replace("%1", "\"%V\"")

        new_icon = ""
        if svg_content:
            compiled_ico = self.compile_svg_to_ico(svg_content, new_label)
            if compiled_ico:
                new_icon = compiled_ico
        else:
            svg_content = None

        try:
            # Update the existing entry (don't rename the key, just update MUIVerb)
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, old_full_path, 0, winreg.KEY_SET_VALUE) as key:
                # Update the display label
                winreg.SetValueEx(key, "MUIVerb", 0, winreg.REG_SZ, new_label)
                
                # Set icon if provided
                if new_icon:
                    winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, new_icon)
                else:
                    # Remove icon if cleared
                    try:
                        winreg.DeleteValue(key, "Icon")
                    except:
                        pass
                
                # Set IconSVG if provided
                if svg_content:
                    winreg.SetValueEx(key, "IconSVG", 0, winreg.REG_SZ, svg_content)
                else:
                    try:
                        winreg.DeleteValue(key, "IconSVG")
                    except:
                        pass
            
            # Update command if it's an entry
            if type_text == "ENTRY" and new_cmd:
                cmd_path = f"{old_full_path}\\command"
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, cmd_path, 0, winreg.KEY_SET_VALUE) as cmd_key:
                    winreg.SetValue(cmd_key, "", winreg.REG_SZ, new_cmd)
                
            self.load_context_entries()
            self.export_config(silent=True)
            self.set_status(f"Updated context menu entry: {new_label}", CP_GREEN)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update entry: {str(e)}")

    def _browse_icon(self, line_edit):
        """Helper to browse for icon file"""
        icon_path, _ = QFileDialog.getOpenFileName(self, "Select Icon File", "", 
                                                  "Icons (*.ico *.exe *.dll *.svg);;All Files (*.*)")
        if icon_path:
            line_edit.setText(icon_path)

    def _create_reg_entry(self, path, command, icon="", svg_content=None):
        """Helper to create registry keys for context menu in HKCU"""
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, path)
        label = path.split('\\')[-1]
        winreg.SetValue(key, "", winreg.REG_SZ, label)
        
        # Set icon if provided
        if icon:
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icon)
        if svg_content:
            winreg.SetValueEx(key, "IconSVG", 0, winreg.REG_SZ, svg_content)
        
        cmd_key = winreg.CreateKey(key, "command")
        winreg.SetValue(cmd_key, "", winreg.REG_SZ, command)
        
        winreg.CloseKey(cmd_key)
        winreg.CloseKey(key)

    def remove_context_entry(self):
        """Remove a context menu entry"""
        row = self.context_table.currentRow()
        if row >= 0:
            full_path = self.context_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            display_name = self.context_table.item(row, 0).text().split('[')[0].strip()
            
            reply = QMessageBox.question(self, "Confirm", f"Remove '{display_name}' and all its sub-items?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    # Delete from HKCU (where we store user entries)
                    self._delete_reg_key(winreg.HKEY_CURRENT_USER, full_path)
                    
                    self.load_context_entries()
                    self.export_config(silent=True)
                    self.set_status(f"Removed {display_name}", CP_GREEN)
                except Exception as e:
                    self.set_status(f"Error removing entry: {str(e)}", CP_RED)

    def move_context_up(self):
        """Move context menu entry up in order by swapping with previous entry"""
        row = self.context_table.currentRow()
        if row <= 0:
            QMessageBox.warning(self, "Error", "Cannot move up - already at top or no selection!")
            return
        
        # Get current and previous items
        current_path = self.context_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        prev_row = row - 1
        
        # Skip indented items (children) - only swap siblings at same level
        current_indent = self.context_table.item(row, 0).text().count("↳")
        prev_indent = self.context_table.item(prev_row, 0).text().count("↳")
        
        if current_indent != prev_indent:
            QMessageBox.warning(self, "Error", "Cannot swap items at different nesting levels!")
            return
            
        prev_path = self.context_table.item(prev_row, 0).data(Qt.ItemDataRole.UserRole)
        
        try:
            # Swap by renaming keys
            self._swap_registry_keys(current_path, prev_path)
            self.load_context_entries()
            self.export_config(silent=True)
            self.context_table.selectRow(prev_row)
            self.set_status("Moved entry up", CP_GREEN)
        except Exception as e:
            self.set_status(f"Error moving entry: {str(e)}", CP_RED)
            QMessageBox.critical(self, "Error", f"Failed to move entry: {str(e)}")

    def move_context_down(self):
        """Move context menu entry down in order by swapping with next entry"""
        row = self.context_table.currentRow()
        if row < 0 or row >= self.context_table.rowCount() - 1:
            QMessageBox.warning(self, "Error", "Cannot move down - already at bottom or no selection!")
            return
        
        # Get current and next items
        current_path = self.context_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        next_row = row + 1
        
        # Skip indented items (children) - only swap siblings at same level
        current_indent = self.context_table.item(row, 0).text().count("↳")
        next_indent = self.context_table.item(next_row, 0).text().count("↳")
        
        if current_indent != next_indent:
            QMessageBox.warning(self, "Error", "Cannot swap items at different nesting levels!")
            return
            
        next_path = self.context_table.item(next_row, 0).data(Qt.ItemDataRole.UserRole)
        
        try:
            # Swap by renaming keys
            self._swap_registry_keys(current_path, next_path)
            self.load_context_entries()
            self.export_config(silent=True)
            self.context_table.selectRow(next_row)
            self.set_status("Moved entry down", CP_GREEN)
        except Exception as e:
            self.set_status(f"Error moving entry: {str(e)}", CP_RED)
            QMessageBox.critical(self, "Error", f"Failed to move entry: {str(e)}")
    
    def _swap_registry_keys(self, path1, path2):
        """Swap two registry keys by renaming them"""
        import time
        
        # Extract key names
        name1 = path1.split('\\')[-1]
        name2 = path2.split('\\')[-1]
        parent = "\\".join(path1.split('\\')[:-1])
        
        # Use temporary name to avoid conflicts
        temp_name = f"_TEMP_SWAP_{int(time.time())}"
        temp_path = f"{parent}\\{temp_name}"
        
        # Step 1: Rename path1 to temp
        self._copy_reg_key(winreg.HKEY_CURRENT_USER, path1, temp_path)
        self._delete_reg_key(winreg.HKEY_CURRENT_USER, path1)
        
        # Step 2: Rename path2 to path1's name
        new_path1 = f"{parent}\\{name1}"
        self._copy_reg_key(winreg.HKEY_CURRENT_USER, path2, new_path1)
        self._delete_reg_key(winreg.HKEY_CURRENT_USER, path2)
        
        # Step 3: Rename temp to path2's name
        new_path2 = f"{parent}\\{name2}"
        self._copy_reg_key(winreg.HKEY_CURRENT_USER, temp_path, new_path2)
        self._delete_reg_key(winreg.HKEY_CURRENT_USER, temp_path)

    def _copy_reg_key(self, hkey, src, dst):
        with winreg.OpenKey(hkey, src, 0, winreg.KEY_READ) as skey:
            with winreg.CreateKey(hkey, dst) as dkey:
                i = 0
                while True:
                    try:
                        n, v, t = winreg.EnumValue(skey, i)
                        winreg.SetValueEx(dkey, n, 0, t, v); i += 1
                    except OSError: break
            i = 0
            while True:
                try:
                    sn = winreg.EnumKey(skey, i)
                    self._copy_reg_key(hkey, f"{src}\\{sn}", f"{dst}\\{sn}"); i += 1
                except OSError: break

    def _delete_reg_key(self, hkey, path):
        """Helper to delete registry key and all subkeys"""
        try:
            # First delete subkeys
            key = winreg.OpenKey(hkey, path, 0, winreg.KEY_ALL_ACCESS)
            try:
                while True:
                    subkey = winreg.EnumKey(key, 0)
                    self._delete_reg_key(key, subkey)
            except OSError:
                pass
            winreg.CloseKey(key)
            # Then delete the key itself
            winreg.DeleteKey(hkey, path)
        except FileNotFoundError:
            pass # Already gone

    # ===== BACKUP / RESTORE METHODS =====
    def get_context_menu_data(self):
        data = {}
        bases = [("Directory\\Background\\shell", "Background"), ("Directory\\shell", "Folder"), ("*\\shell", "AllFiles")]
        for bp, s in bases:
            res = self._export_shell_keys(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\{bp}")
            if res: data[s] = res
        return data

    def compile_svg_to_ico(self, svg_content_or_path, ico_name):
        """Compiles SVG code or file to a local .ico file and returns the path"""
        from PyQt6.QtGui import QPainter, QPixmap
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtCore import QByteArray, Qt
        
        ico_path = os.path.join(self.icons_dir, f"{ico_name}.ico")
        try:
            renderer = QSvgRenderer()
            if os.path.exists(svg_content_or_path):
                renderer.load(svg_content_or_path)
            else:
                renderer.load(QByteArray(svg_content_or_path.encode('utf-8')))
            
            # Render at 32x32 for high quality shell icon
            pixmap = QPixmap(32, 32)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()
            
            pixmap.save(ico_path, "ICO")
            return ico_path
        except Exception as e:
            print(f"Error compiling SVG to ICO: {e}")
            return None

    def apply_svg_icons(self):
        """Scan all context menu registry entries, compile IconSVG to .ico, and update their registry Icon paths"""
        bases = [r"Software\Classes\Directory\Background\shell", r"Software\Classes\Directory\shell", r"Software\Classes\*\shell"]
        count = 0
        for base in bases:
            count += self._process_svg_keys(winreg.HKEY_CURRENT_USER, base)
        self.load_context_entries()
        QMessageBox.information(self, "Success", f"Compiled and applied {count} SVG icons to context menus.")

    def _process_svg_keys(self, hkey, path):
        count = 0
        try:
            key = winreg.OpenKey(hkey, path, 0, winreg.KEY_READ)
            i = 0
            while True:
                try:
                    sn = winreg.EnumKey(key, i)
                    fp = f"{path}\\{sn}"
                    svg_content = None
                    try:
                        with winreg.OpenKey(hkey, fp, 0, winreg.KEY_READ) as sk:
                            try:
                                svg_content, _ = winreg.QueryValueEx(sk, "IconSVG")
                            except:
                                pass
                    except:
                        pass
                    
                    if svg_content:
                        compiled_ico = self.compile_svg_to_ico(svg_content, sn)
                        if compiled_ico:
                            with winreg.OpenKey(hkey, fp, 0, winreg.KEY_SET_VALUE) as sk:
                                winreg.SetValueEx(sk, "Icon", 0, winreg.REG_SZ, compiled_ico)
                            count += 1
                    
                    # Recursively check subkeys
                    try:
                        winreg.OpenKey(hkey, f"{fp}\\shell", 0, winreg.KEY_READ)
                        count += self._process_svg_keys(hkey, f"{fp}\\shell")
                    except:
                        pass
                    
                    i += 1
                except OSError:
                    break
            winreg.CloseKey(key)
        except:
            pass
        return count

    def _export_shell_keys(self, hkey, path):
        entries = {}
        try:
            key = winreg.OpenKey(hkey, path, 0, winreg.KEY_READ)
            i = 0
            while True:
                try:
                    sn = winreg.EnumKey(key, i)
                    if sn.lower() in ["cmd", "powershell", "anycode", "wsl"]: i += 1; continue
                    fp = f"{path}\\{sn}"; ed = {}
                    with winreg.OpenKey(hkey, fp, 0, winreg.KEY_READ) as sk:
                        for val in ["MUIVerb", "Icon", "SubCommands", "CommandFlags", "IconSVG"]:
                            try: ed[val], _ = winreg.QueryValueEx(sk, val)
                            except: pass
                    try:
                        with winreg.OpenKey(hkey, f"{fp}\\command", 0, winreg.KEY_READ) as ck:
                            ed["command"], _ = winreg.QueryValueEx(ck, "")
                    except: pass
                    try:
                        winreg.OpenKey(hkey, f"{fp}\\shell", 0, winreg.KEY_READ)
                        ed["children"] = self._export_shell_keys(hkey, f"{fp}\\shell")
                    except: pass
                    entries[sn] = ed; i += 1
                except OSError: break
            winreg.CloseKey(key)
        except: pass
        return entries

    def _import_shell_entries(self, hkey, path, entries):
        for n, d in entries.items():
            fp = f"{path}\\{n}"
            key = winreg.CreateKey(hkey, fp)
            
            icon_path = d.get("Icon", "")
            svg_content = d.get("IconSVG", None)
            if svg_content:
                compiled_ico = self.compile_svg_to_ico(svg_content, n)
                if compiled_ico:
                    icon_path = compiled_ico
            
            for k in ["MUIVerb", "SubCommands"]:
                if k in d: winreg.SetValueEx(key, k, 0, winreg.REG_SZ, d[k])
            if icon_path:
                winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icon_path)
            if svg_content:
                winreg.SetValueEx(key, "IconSVG", 0, winreg.REG_SZ, svg_content)
            if "CommandFlags" in d: winreg.SetValueEx(key, "CommandFlags", 0, winreg.REG_DWORD, d["CommandFlags"])
            winreg.CloseKey(key)
            if "command" in d:
                with winreg.CreateKey(hkey, f"{fp}\\command") as ck: winreg.SetValue(ck, "", winreg.REG_SZ, d["command"])
            if "children" in d:
                winreg.CreateKey(hkey, f"{fp}\\shell")
                self._import_shell_entries(hkey, f"{fp}\\shell", d["children"])

    def export_config(self, silent=False):
        path = os.path.join(os.path.dirname(__file__), "data.json")
        try:
            config = {
                "version": "1.3",
                "timestamp": datetime.now().isoformat(),
                "aliases": self.aliases,
                "context_menu": self.get_context_menu_data()
            }
            with open(path, 'w', encoding='utf-8') as f: json.dump(config, f, indent=4)
            self.set_status("Exported to data.json", CP_GREEN)
            if not silent:
                QMessageBox.information(self, "Success", f"Exported to {path}")
        except Exception as e:
            self.set_status("Export failed", CP_RED)

    def import_config(self):
        path = os.path.join(os.path.dirname(__file__), "data.json")
        if not os.path.exists(path): return
        try:
            with open(path, 'r', encoding='utf-8') as f: config = json.load(f)
            
            # User path remapping
            cur_user = os.path.basename(os.path.expanduser("~"))
            def remap(item, old, new):
                if isinstance(item, dict): return {k: remap(v, old, new) for k, v in item.items()}
                if isinstance(item, str): return item.replace(f"C:\\Users\\{old}", f"C:\\Users\\{new}").replace(f"C:/Users/{old}", f"C:/Users/{new}")
                return item
            
            # Simple check for old users
            m = re.search(r'C:\\Users\\([^\\]+)', json.dumps(config), re.I)
            if m and m.group(1).lower() != cur_user.lower():
                config = remap(config, m.group(1), cur_user)

            if "aliases" in config:
                self.aliases.update(config["aliases"])
                self.save_aliases()
            if "context_menu" in config:
                for s, ent in config["context_menu"].items():
                    bp = {"Background": r"Directory\Background\shell", "Folder": r"Directory\shell", "AllFiles": r"*\shell"}.get(s)
                    if bp: self._import_shell_entries(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\{bp}", ent)
            
            self.load_aliases(); self.load_context_entries()
            self.set_status("Imported successfully", CP_GREEN)
        except Exception as e:
            self.set_status(f"Import failed: {e}", CP_RED)

    def _import_shell_entries(self, hkey, path, entries):
        for n, d in entries.items():
            fp = f"{path}\\{n}"
            key = winreg.CreateKey(hkey, fp)
            for k in ["MUIVerb", "Icon", "SubCommands"]:
                if k in d: winreg.SetValueEx(key, k, 0, winreg.REG_SZ, d[k])
            if "CommandFlags" in d: winreg.SetValueEx(key, "CommandFlags", 0, winreg.REG_DWORD, d["CommandFlags"])
            winreg.CloseKey(key)
            if "command" in d:
                with winreg.CreateKey(hkey, f"{fp}\\command") as ck: winreg.SetValue(ck, "", winreg.REG_SZ, d["command"])
            if "children" in d:
                winreg.CreateKey(hkey, f"{fp}\\shell")
                self._import_shell_entries(hkey, f"{fp}\\shell", d["children"])

    def show_command_help(self):
        """Show a detailed help guide dialog for context menu commands"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QDialogButtonBox
        dialog = QDialog(self)
        dialog.setWindowTitle("Command Guide & Examples")
        dialog.setMinimumSize(750, 600)
        
        layout = QVBoxLayout(dialog)
        
        browser = QTextBrowser()
        # Enable HTML styling
        html_content = f"""
        <style>
            body {{
                background-color: {CP_BG};
                color: {CP_TEXT};
                font-size: 10pt;
            }}
            h2 {{
                color: {CP_YELLOW};
                border-bottom: 1px solid {CP_DIM};
                padding-bottom: 5px;
            }}
            h3 {{
                color: {CP_CYAN};
                margin-top: 15px;
            }}
            code {{
                background-color: {CP_PANEL};
                color: {CP_ORANGE};
                padding: 2px 5px;
                border-radius: 3px;
                font-weight: bold;
            }}
            pre {{
                background-color: {CP_PANEL};
                color: {CP_CYAN};
                padding: 10px;
                border: 1px solid {CP_DIM};
                border-radius: 5px;
                white-space: pre-wrap;
            }}
            ul {{
                margin-left: 20px;
            }}
            li {{
                margin-bottom: 5px;
            }}
        </style>
        <h2>💡 Right-Click Context Menu Command Guide</h2>
        
        <h3>1. Directory Path Variables</h3>
        <ul>
            <li><code>%V</code> : The primary path to use. It represents the directory you right-clicked on, or the current folder path if right-clicking on empty background space.</li>
            <li><code>%1</code> : The path of the specific selected file or folder. Use this when the item applies specifically to a file selection.</li>
        </ul>
        
        <h3>2. CMD (Command Prompt) Examples</h3>
        <ul>
            <li><b>Run command and keep CMD window open</b>:<br>
            <pre>cmd.exe /k "your-command"</pre></li>
            <li><b>Start CMD directly in the target directory</b>:<br>
            <pre>cmd.exe /k "cd /d \\"%V\\""</pre></li>
            <li><b>Run a script in target folder and keep open</b>:<br>
            <pre>cmd.exe /k "cd /d \\"%V\\" && python my_script.py"</pre></li>
        </ul>
        
        <h3>3. PowerShell / pwsh Examples</h3>
        <ul>
            <li><b>Run command in PowerShell Core (pwsh) and keep open</b>:<br>
            <pre>pwsh.exe -NoExit -Command "your-command"</pre></li>
            <li><b>Open pwsh directly in the target directory</b>:<br>
            <pre>pwsh.exe -WorkingDirectory "%V" -NoExit</pre></li>
            <li><b>Open standard PowerShell in the target directory</b>:<br>
            <pre>powershell.exe -NoExit -Command "Set-Location '%V'"</pre></li>
            <li><b>Run script and keep PowerShell open</b>:<br>
            <pre>pwsh.exe -WorkingDirectory "%V" -NoExit -Command "& './my_script.ps1'"</pre></li>
        </ul>
        
        <h3>4. Windows Terminal (wt) Integration</h3>
        <ul>
            <li><b>Open new tab in Windows Terminal at current directory (default profile)</b>:<br>
            <pre>wt.exe -d "%V"</pre></li>
            <li><b>Open a specific shell (e.g. pwsh) in Windows Terminal keeping it open</b>:<br>
            <pre>wt.exe -d "%V" nt pwsh.exe -NoExit -Command "echo 'Hello!'"</pre></li>
            <li><b>Open command prompt (CMD) in Windows Terminal</b>:<br>
            <pre>wt.exe -d "%V" nt cmd.exe /k "echo 'CMD tab'"</pre></li>
            <li><b>Run multiple command tabs or panes side-by-side</b>:<br>
            <pre>wt.exe -d "%V" nt pwsh.exe ; split-pane -d "%V" -H cmd.exe</pre></li>
        </ul>
        """
        browser.setHtml(html_content)
        layout.addWidget(browser)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.exec()

    def set_status(self, message, color=CP_TEXT):
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {color}; font-weight: bold; padding: 5px;")

def main():
    app = QApplication(sys.argv)
    window = EnvVariableManager()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
