import sys
import os
import winreg
import json
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QLineEdit, QGroupBox, QListWidget, 
                             QMessageBox, QInputDialog, QTabWidget, QTextEdit, QSplitter,
                             QListWidgetItem, QFormLayout, QTableWidget, QTableWidgetItem,
                             QHeaderView, QFileDialog, QDialog, QDialogButtonBox)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QFontDatabase

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
        self.setWindowTitle("ENV VARIABLE MANAGER v1.0")
        self.resize(1200, 700)
        
        # Apply Cyberpunk Theme
        self.apply_theme()
        
        # Main Layout
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        # Status Bar (create before tabs)
        self.status_label = QLabel("SYSTEM READY")
        self.status_label.setStyleSheet(f"color: {CP_GREEN}; font-weight: bold; padding: 5px;")
        
        # Initialize Scripts Directory
        self.scripts_dir = os.path.join(os.path.expanduser("~"), ".env_manager", "scripts")
        os.makedirs(self.scripts_dir, exist_ok=True)
        
        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_path_tab(), "PATH MANAGER")
        self.tabs.addTab(self.create_env_tab(), "ENV VARIABLES")
        self.tabs.addTab(self.create_alias_tab(), "ALIASES")
        self.tabs.addTab(self.create_scripts_tab(), "SCRIPTS")
        self.tabs.addTab(self.create_context_tab(), "CONTEXT MENU")
        self.tabs.addTab(self.create_backup_tab(), "BACKUP/RESTORE")
        main_layout.addWidget(self.tabs)
        
        # Add status bar at bottom
        main_layout.addWidget(self.status_label)
    
    def apply_theme(self):
        """Apply cyberpunk theme to the application"""
        # Try to find the best match for JetBrainsMono NFP
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
            QLineEdit:focus, QTextEdit:focus {{ border: 1px solid {CP_CYAN}; }}
            
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
            QPushButton:pressed {{
                background-color: {CP_YELLOW};
                color: black;
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
            QListWidget::item:hover {{
                background-color: {CP_DIM};
            }}
            
            QHeaderView::section {{
                background-color: {CP_DIM};
                color: {CP_YELLOW};
                padding: 5px;
                border: 1px solid {CP_BG};
                font-weight: bold;
            }}
            
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
            QTabBar::tab:hover {{
                color: {CP_CYAN};
            }}
        """)
    
    def create_path_tab(self):
        """Create PATH environment variable manager tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Scope Selection
        scope_group = QGroupBox("SCOPE")
        scope_layout = QHBoxLayout()
        self.path_user_btn = QPushButton("USER")
        self.path_system_btn = QPushButton("SYSTEM")
        self.path_user_btn.clicked.connect(lambda: self.load_path_vars("user"))
        self.path_system_btn.clicked.connect(lambda: self.load_path_vars("system"))
        scope_layout.addWidget(self.path_user_btn)
        scope_layout.addWidget(self.path_system_btn)
        scope_group.setLayout(scope_layout)
        layout.addWidget(scope_group)
        
        # Path List
        list_group = QGroupBox("PATH ENTRIES")
        list_layout = QVBoxLayout()
        self.path_list = QListWidget()
        list_layout.addWidget(self.path_list)
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        # Controls
        controls_layout = QHBoxLayout()
        add_btn = QPushButton("➕ ADD")
        edit_btn = QPushButton("✏️ EDIT")
        remove_btn = QPushButton("❌ REMOVE")
        up_btn = QPushButton("⬆️ MOVE UP")
        down_btn = QPushButton("⬇️ MOVE DOWN")
        refresh_btn = QPushButton("🔄 REFRESH")
        cleanup_btn = QPushButton("🧹 CLEANUP PATH")
        
        add_btn.clicked.connect(self.add_path_entry)
        edit_btn.clicked.connect(self.edit_path_entry)
        remove_btn.clicked.connect(self.remove_path_entry)
        up_btn.clicked.connect(self.move_path_up)
        down_btn.clicked.connect(self.move_path_down)
        refresh_btn.clicked.connect(lambda: self.load_path_vars(self.current_path_scope))
        cleanup_btn.clicked.connect(self.cleanup_path)
        
        controls_layout.addWidget(add_btn)
        controls_layout.addWidget(edit_btn)
        controls_layout.addWidget(remove_btn)
        controls_layout.addWidget(up_btn)
        controls_layout.addWidget(down_btn)
        controls_layout.addWidget(refresh_btn)
        controls_layout.addWidget(cleanup_btn)
        layout.addLayout(controls_layout)
        
        # Initialize
        self.current_path_scope = "user"
        self.load_path_vars("user")
        
        return widget
    
    def create_env_tab(self):
        """Create general environment variables manager tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Scope Selection
        scope_group = QGroupBox("SCOPE")
        scope_layout = QHBoxLayout()
        self.env_user_btn = QPushButton("USER")
        self.env_system_btn = QPushButton("SYSTEM")
        self.env_user_btn.clicked.connect(lambda: self.load_env_vars("user"))
        self.env_system_btn.clicked.connect(lambda: self.load_env_vars("system"))
        scope_layout.addWidget(self.env_user_btn)
        scope_layout.addWidget(self.env_system_btn)
        scope_group.setLayout(scope_layout)
        layout.addWidget(scope_group)
        
        # Variable Table
        list_group = QGroupBox("ENVIRONMENT VARIABLES")
        list_layout = QVBoxLayout()
        self.env_table = QTableWidget()
        self.env_table.setColumnCount(2)
        self.env_table.setHorizontalHeaderLabels(["Variable Name", "Value"])
        self.env_table.horizontalHeader().setStretchLastSection(True)
        self.env_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.env_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.env_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        list_layout.addWidget(self.env_table)
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        # Controls
        controls_layout = QHBoxLayout()
        add_btn = QPushButton("➕ ADD")
        edit_btn = QPushButton("✏️ EDIT")
        remove_btn = QPushButton("❌ REMOVE")
        refresh_btn = QPushButton("🔄 REFRESH")
        
        add_btn.clicked.connect(self.add_env_var)
        edit_btn.clicked.connect(self.edit_env_var)
        remove_btn.clicked.connect(self.remove_env_var)
        refresh_btn.clicked.connect(lambda: self.load_env_vars(self.current_env_scope))
        
        controls_layout.addWidget(add_btn)
        controls_layout.addWidget(edit_btn)
        controls_layout.addWidget(remove_btn)
        controls_layout.addWidget(refresh_btn)
        layout.addLayout(controls_layout)
        
        # Initialize
        self.current_env_scope = "user"
        self.load_env_vars("user")
        
        return widget
    
    def create_alias_tab(self):
        """Create command aliases manager tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        info = QLabel("💡 Aliases work in CMD, PowerShell & Git Bash via auto-load scripts")
        info.setStyleSheet(f"color: {CP_CYAN}; padding: 5px;")
        layout.addWidget(info)
        
        # Alias List
        list_group = QGroupBox("COMMAND ALIASES")
        list_layout = QVBoxLayout()
        self.alias_list = QListWidget()
        list_layout.addWidget(self.alias_list)
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        # Controls
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
        
        # Alias storage
        self.aliases = {}
        self.alias_dir = os.path.join(os.path.expanduser("~"), ".aliases")
        os.makedirs(self.alias_dir, exist_ok=True)
        self.load_aliases()
        
        return widget
    
    # ===== PATH METHODS =====
    
    def load_path_vars(self, scope):
        """Load PATH variable entries"""
        self.current_path_scope = scope
        self.path_list.clear()
        
        try:
            hkey = winreg.HKEY_CURRENT_USER if scope == "user" else winreg.HKEY_LOCAL_MACHINE
            subkey = r"Environment" if scope == "user" else r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
            
            with winreg.OpenKey(hkey, subkey, 0, winreg.KEY_READ) as key:
                try:
                    path_value, _ = winreg.QueryValueEx(key, "Path")
                except FileNotFoundError:
                    # Path might be named PATH or not exist
                    try:
                        path_value, _ = winreg.QueryValueEx(key, "PATH")
                    except FileNotFoundError:
                        path_value = ""
            
            paths = [p.strip() for p in path_value.split(';') if p.strip()]
            for path in paths:
                self.path_list.addItem(path)
            
            self.set_status(f"Loaded {len(paths)} PATH entries from {scope.upper()}", CP_GREEN)
        except Exception as e:
            self.set_status(f"Error loading PATH: {str(e)}", CP_RED)
    
    def save_path_vars(self):
        """Save PATH variable entries"""
        try:
            paths = [self.path_list.item(i).text() for i in range(self.path_list.count())]
            path_value = ';'.join(paths)
            
            hkey = winreg.HKEY_CURRENT_USER if self.current_path_scope == "user" else winreg.HKEY_LOCAL_MACHINE
            subkey = r"Environment" if self.current_path_scope == "user" else r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
            
            with winreg.OpenKey(hkey, subkey, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, path_value)
            
            # Broadcast change
            self.broadcast_env_change()
            self.set_status(f"PATH saved to {self.current_path_scope.upper()}", CP_GREEN)
        except PermissionError:
            self.set_status("Permission denied! Run as Administrator for SYSTEM scope", CP_RED)
        except Exception as e:
            self.set_status(f"Error saving PATH: {str(e)}", CP_RED)
    
    def add_path_entry(self):
        """Add new PATH entry"""
        text, ok = QInputDialog.getText(self, "Add PATH Entry", "Enter path:")
        if ok and text:
            self.path_list.addItem(text)
            self.save_path_vars()
    
    def edit_path_entry(self):
        """Edit selected PATH entry"""
        current = self.path_list.currentItem()
        if current:
            text, ok = QInputDialog.getText(self, "Edit PATH Entry", "Edit path:", 
                                           text=current.text())
            if ok and text:
                current.setText(text)
                self.save_path_vars()
    
    def remove_path_entry(self):
        """Remove selected PATH entry"""
        current = self.path_list.currentRow()
        if current >= 0:
            reply = QMessageBox.question(self, "Confirm", "Remove this PATH entry?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.path_list.takeItem(current)
                self.save_path_vars()
    
    def move_path_up(self):
        """Move PATH entry up"""
        current = self.path_list.currentRow()
        if current > 0:
            item = self.path_list.takeItem(current)
            self.path_list.insertItem(current - 1, item)
            self.path_list.setCurrentRow(current - 1)
            self.save_path_vars()
    
    def move_path_down(self):
        """Move PATH entry down"""
        current = self.path_list.currentRow()
        if current < self.path_list.count() - 1:
            item = self.path_list.takeItem(current)
            self.path_list.insertItem(current + 1, item)
            self.path_list.setCurrentRow(current + 1)
            self.save_path_vars()

    def cleanup_path(self):
        """Remove duplicates and non-existent folders from PATH"""
        paths = [self.path_list.item(i).text() for i in range(self.path_list.count())]
        initial_count = len(paths)
        
        # 1. Remove duplicates while preserving order
        seen = set()
        clean_paths = []
        duplicates_removed = 0
        for p in paths:
            if p.lower() not in seen:
                clean_paths.append(p)
                seen.add(p.lower())
            else:
                duplicates_removed += 1
        
        # 2. Check for non-existent folders
        valid_paths = []
        invalid_removed = 0
        invalid_list = []
        
        for p in clean_paths:
            # Expand environment variables like %USERPROFILE% for checking
            expanded = os.path.expandvars(p)
            if os.path.exists(expanded):
                valid_paths.append(p)
            else:
                invalid_removed += 1
                invalid_list.append(p)
        
        if duplicates_removed == 0 and invalid_removed == 0:
            QMessageBox.information(self, "Cleanup", "PATH is already clean!")
            return
            
        msg = f"Cleanup Summary:\n\n- Duplicates removed: {duplicates_removed}\n- Invalid paths found: {invalid_removed}"
        if invalid_list:
            msg += "\n\nInvalid entries that will be removed:\n" + "\n".join(invalid_list[:10])
            if len(invalid_list) > 10: msg += "\n..."
            
        msg += "\n\nApply these changes?"
        
        reply = QMessageBox.question(self, "Confirm Cleanup", msg,
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.path_list.clear()
            for p in valid_paths:
                self.path_list.addItem(p)
            self.save_path_vars()
            self.set_status(f"PATH cleaned: Removed {duplicates_removed + invalid_removed} entries", CP_GREEN)
    
    # ===== ENV VARIABLE METHODS =====
    
    def load_env_vars(self, scope):
        """Load environment variables"""
        self.current_env_scope = scope
        self.env_table.setRowCount(0)
        
        try:
            if scope == "user":
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_READ)
            else:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                    r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                                    0, winreg.KEY_READ)
            
            i = 0
            vars_loaded = []
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    
                    # Add row to table
                    row = self.env_table.rowCount()
                    self.env_table.insertRow(row)
                    
                    # Name column
                    name_item = QTableWidgetItem(name)
                    name_item.setForeground(Qt.GlobalColor.white)
                    self.env_table.setItem(row, 0, name_item)
                    
                    # Value column
                    value_item = QTableWidgetItem(str(value))
                    value_item.setForeground(Qt.GlobalColor.white)
                    self.env_table.setItem(row, 1, value_item)
                    
                    vars_loaded.append(name)
                    i += 1
                except OSError:
                    break
            
            winreg.CloseKey(key)
            self.set_status(f"Loaded {len(vars_loaded)} variables from {scope.upper()}", CP_GREEN)
        except Exception as e:
            self.set_status(f"Error loading variables: {str(e)}", CP_RED)
    
    def add_env_var(self):
        """Add new environment variable"""
        name, ok1 = QInputDialog.getText(self, "Add Variable", "Variable name:")
        if ok1 and name:
            value, ok2 = QInputDialog.getText(self, "Add Variable", f"Value for {name}:")
            if ok2:
                try:
                    hkey = winreg.HKEY_CURRENT_USER if self.current_env_scope == "user" else winreg.HKEY_LOCAL_MACHINE
                    subkey = r"Environment" if self.current_env_scope == "user" else r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
                    
                    with winreg.OpenKey(hkey, subkey, 0, winreg.KEY_SET_VALUE) as key:
                        winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)
                    
                    self.broadcast_env_change()
                    self.load_env_vars(self.current_env_scope)
                    self.set_status(f"Added {name}", CP_GREEN)
                except PermissionError:
                    self.set_status("Permission denied! Run as Administrator", CP_RED)
                except Exception as e:
                    self.set_status(f"Error: {str(e)}", CP_RED)
    
    def edit_env_var(self):
        """Edit selected environment variable"""
        current_row = self.env_table.currentRow()
        if current_row >= 0:
            name_item = self.env_table.item(current_row, 0)
            value_item = self.env_table.item(current_row, 1)
            if not name_item or not value_item:
                return
                
            name = name_item.text()
            old_value = value_item.text()
            
            value, ok = QInputDialog.getText(self, "Edit Variable", f"New value for {name}:",
                                            text=old_value)
            if ok:
                try:
                    hkey = winreg.HKEY_CURRENT_USER if self.current_env_scope == "user" else winreg.HKEY_LOCAL_MACHINE
                    subkey = r"Environment" if self.current_env_scope == "user" else r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
                    
                    with winreg.OpenKey(hkey, subkey, 0, winreg.KEY_SET_VALUE) as key:
                        winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)
                    
                    self.broadcast_env_change()
                    self.load_env_vars(self.current_env_scope)
                    self.set_status(f"Updated {name}", CP_GREEN)
                except PermissionError:
                    self.set_status("Permission denied! Run as Administrator", CP_RED)
                except Exception as e:
                    self.set_status(f"Error: {str(e)}", CP_RED)
    
    def remove_env_var(self):
        """Remove selected environment variable"""
        current_row = self.env_table.currentRow()
        if current_row >= 0:
            name_item = self.env_table.item(current_row, 0)
            if not name_item:
                return
            name = name_item.text()
            
            reply = QMessageBox.question(self, "Confirm", f"Delete variable '{name}'?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    hkey = winreg.HKEY_CURRENT_USER if self.current_env_scope == "user" else winreg.HKEY_LOCAL_MACHINE
                    subkey = r"Environment" if self.current_env_scope == "user" else r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
                    
                    with winreg.OpenKey(hkey, subkey, 0, winreg.KEY_SET_VALUE) as key:
                        winreg.DeleteValue(key, name)
                    
                    self.broadcast_env_change()
                    self.load_env_vars(self.current_env_scope)
                    self.set_status(f"Deleted {name}", CP_GREEN)
                except PermissionError:
                    self.set_status("Permission denied! Run as Administrator", CP_RED)
                except Exception as e:
                    self.set_status(f"Error: {str(e)}", CP_RED)
    
    # ===== ALIAS METHODS =====
    
    def load_aliases(self):
        """Load command aliases from a JSON file"""
        self.alias_list.clear()
        alias_file = os.path.join(self.alias_dir, "aliases.json")
        
        try:
            if os.path.exists(alias_file):
                with open(alias_file, 'r') as f:
                    self.aliases = json.load(f)
            else:
                # Create default aliases
                self.aliases = {
                    "ll": "ls -la",
                    "gs": "git status",
                    "ga": "git add",
                    "gc": "git commit",
                    "gp": "git push",
                    "gl": "git log --oneline",
                    "cls": "clear",
                }
                self.save_aliases()
            
            for name, command in self.aliases.items():
                self.alias_list.addItem(f"{name} → {command}")
            
            self.set_status(f"Loaded {len(self.aliases)} aliases", CP_GREEN)
        except Exception as e:
            self.set_status(f"Error loading aliases: {str(e)}", CP_RED)
    
    def save_aliases(self):
        """Save aliases to JSON file and generate loader scripts"""
        alias_file = os.path.join(self.alias_dir, "aliases.json")
        try:
            with open(alias_file, 'w') as f:
                json.dump(self.aliases, f, indent=2)
            
            # Generate loader scripts
            self.generate_cmd_loader()
            self.generate_powershell_loader()
            self.generate_bash_loader()
            
            self.set_status("Aliases saved & scripts generated", CP_GREEN)
        except Exception as e:
            self.set_status(f"Error saving aliases: {str(e)}", CP_RED)
    
    def generate_cmd_loader(self):
        """Generate CMD/doskey loader script"""
        loader_path = os.path.join(self.alias_dir, "aliases.cmd")
        try:
            with open(loader_path, 'w') as f:
                f.write("@echo off\n")
                f.write("REM Auto-generated alias loader for CMD\n")
                for name, command in self.aliases.items():
                    f.write(f"doskey {name}={command}\n")
        except Exception as e:
            print(f"Error generating CMD loader: {e}")
    
    def generate_powershell_loader(self):
        """Generate PowerShell loader script"""
        loader_path = os.path.join(self.alias_dir, "aliases.ps1")
        try:
            with open(loader_path, 'w', encoding='utf-8') as f:
                f.write("# Auto-generated alias loader for PowerShell\n")
                for name, command in self.aliases.items():
                    # PowerShell functions for complex commands
                    f.write(f"function {name} {{ {command} @args }}\n")
        except Exception as e:
            print(f"Error generating PowerShell loader: {e}")
    
    def generate_bash_loader(self):
        """Generate Bash loader script (for Git Bash, WSL, etc)"""
        loader_path = os.path.join(self.alias_dir, "aliases.sh")
        try:
            with open(loader_path, 'w') as f:
                f.write("#!/bin/bash\n")
                f.write("# Auto-generated alias loader for Bash\n")
                for name, command in self.aliases.items():
                    f.write(f"alias {name}='{command}'\n")
        except Exception as e:
            print(f"Error generating Bash loader: {e}")
    
    def setup_auto_load(self):
        """Setup automatic alias loading for all shells"""
        try:
            # Setup PowerShell profiles (both Windows PowerShell and PowerShell 7+)
            ps_profiles = [
                os.path.join(os.path.expanduser("~"), 
                            "Documents", "WindowsPowerShell", "Microsoft.PowerShell_profile.ps1"),
                os.path.join(os.path.expanduser("~"), 
                            "Documents", "PowerShell", "Microsoft.PowerShell_profile.ps1")
            ]
            
            loader_line = f". '{os.path.join(self.alias_dir, 'aliases.ps1')}'\n"
            ps_setup_count = 0
            
            for ps_profile in ps_profiles:
                try:
                    os.makedirs(os.path.dirname(ps_profile), exist_ok=True)
                    
                    # Read existing profile
                    existing = ""
                    if os.path.exists(ps_profile):
                        with open(ps_profile, 'r', encoding='utf-8') as f:
                            existing = f.read()
                    
                    # Add loader if not present
                    if loader_line.strip() not in existing and "aliases.ps1" not in existing:
                        with open(ps_profile, 'a', encoding='utf-8') as f:
                            f.write(f"\n# Auto-load aliases from env manager\n{loader_line}")
                        ps_setup_count += 1
                except Exception as e:
                    print(f"PowerShell profile setup failed for {ps_profile}: {e}")
            
            # Setup CMD auto-load via registry (AutoRun)
            cmd_setup = False
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                    r"Software\Microsoft\Command Processor", 
                                    0, winreg.KEY_SET_VALUE)
                cmd_loader = os.path.join(self.alias_dir, "aliases.cmd")
                winreg.SetValueEx(key, "AutoRun", 0, winreg.REG_SZ, cmd_loader)
                winreg.CloseKey(key)
                cmd_setup = True
            except Exception as e:
                print(f"CMD AutoRun setup failed: {e}")
            
            # Setup Bash (.bashrc)
            bash_setup = False
            bashrc = os.path.join(os.path.expanduser("~"), ".bashrc")
            bash_loader_line = f"source ~/.aliases/aliases.sh\n"
            
            try:
                existing_bash = ""
                if os.path.exists(bashrc):
                    with open(bashrc, 'r') as f:
                        existing_bash = f.read()
                
                if bash_loader_line.strip() not in existing_bash and "aliases.sh" not in existing_bash:
                    with open(bashrc, 'a') as f:
                        f.write(f"\n# Auto-load aliases\n{bash_loader_line}")
                    bash_setup = True
            except Exception as e:
                print(f"Bash setup failed: {e}")
            
            msg = "✅ Auto-load setup complete!\n\n"
            if ps_setup_count > 0:
                msg += f"✓ PowerShell: {ps_setup_count} profile(s) configured\n"
            if cmd_setup:
                msg += "✓ CMD: Registry AutoRun configured\n"
            if bash_setup:
                msg += "✓ Bash: .bashrc configured\n"
            msg += f"\n📁 Alias files: {self.alias_dir}\n\n"
            msg += "⚠️ Restart your shells to apply changes!"
            
            QMessageBox.information(self, "Setup Complete", msg)
            self.set_status("Auto-load configured for all shells", CP_GREEN)
            
        except Exception as e:
            self.set_status(f"Setup error: {str(e)}", CP_RED)
            QMessageBox.warning(self, "Error", f"Setup failed: {str(e)}")
    
    def apply_all_aliases(self):
        """Apply aliases to current session"""
        try:
            # Apply to current CMD session
            for name, command in self.aliases.items():
                os.system(f'doskey {name}={command}')
            
            self.set_status(f"Applied {len(self.aliases)} aliases to current session", CP_GREEN)
        except Exception as e:
            self.set_status(f"Error applying aliases: {str(e)}", CP_RED)
    
    def add_alias(self):
        """Add new command alias"""
        name, ok1 = QInputDialog.getText(self, "Add Alias", "Alias name:")
        if ok1 and name:
            command, ok2 = QInputDialog.getText(self, "Add Alias", f"Command for '{name}':")
            if ok2 and command:
                self.aliases[name] = command
                self.save_aliases()
                self.load_aliases()
    
    def edit_alias(self):
        """Edit selected alias"""
        current = self.alias_list.currentItem()
        if current:
            text = current.text()
            if " → " in text:
                old_name, old_command = text.split(" → ", 1)
                
                # Step 1: Edit Name
                new_name, ok1 = QInputDialog.getText(self, "Edit Alias", "Alias Name (Shortcut):",
                                                    text=old_name)
                if ok1 and new_name:
                    # Step 2: Edit Command
                    new_command, ok2 = QInputDialog.getText(self, "Edit Alias", f"Command for '{new_name}':",
                                                      text=old_command)
                    if ok2 and new_command:
                        # Update aliases
                        if new_name != old_name and old_name in self.aliases:
                            del self.aliases[old_name]
                        
                        self.aliases[new_name] = new_command
                        self.save_aliases()
                        self.load_aliases()
    
    def remove_alias(self):
        """Remove selected alias"""
        current = self.alias_list.currentItem()
        if current:
            text = current.text()
            if " → " in text:
                name = text.split(" → ", 1)[0]
                reply = QMessageBox.question(self, "Confirm", f"Delete alias '{name}'?",
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    if name in self.aliases:
                        del self.aliases[name]
                        self.save_aliases()
                        self.load_aliases()
    
    # ===== CONTEXT MENU METHODS =====

    def create_context_tab(self):
        """Create tab for Windows Right-Click Context Menu customization"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Menu Table
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
        
        # Controls
        controls_layout = QHBoxLayout()
        add_btn = QPushButton("➕ ADD ENTRY")
        add_group_btn = QPushButton("📁 ADD GROUP")
        sep_btn = QPushButton("➖ SEPARATOR")
        icon_btn = QPushButton("🖼️ SET ICON")
        edit_btn = QPushButton("✏️ EDIT")
        remove_btn = QPushButton("❌ REMOVE")
        up_btn = QPushButton("⬆️ MOVE UP")
        down_btn = QPushButton("⬇️ MOVE DOWN")
        refresh_btn = QPushButton("🔄 REFRESH")
        
        add_btn.clicked.connect(self.add_context_entry)
        add_group_btn.clicked.connect(self.add_context_group)
        sep_btn.clicked.connect(self.add_context_separator)
        icon_btn.clicked.connect(self.set_context_icon)
        edit_btn.clicked.connect(self.edit_context_entry)
        remove_btn.clicked.connect(self.remove_context_entry)
        up_btn.clicked.connect(self.move_context_up)
        down_btn.clicked.connect(self.move_context_down)
        refresh_btn.clicked.connect(self.load_context_entries)
        
        controls_layout.addWidget(add_btn)
        controls_layout.addWidget(add_group_btn)
        controls_layout.addWidget(sep_btn)
        controls_layout.addWidget(icon_btn)
        controls_layout.addWidget(edit_btn)
        controls_layout.addWidget(remove_btn)
        controls_layout.addWidget(up_btn)
        controls_layout.addWidget(down_btn)
        controls_layout.addWidget(refresh_btn)
        layout.addLayout(controls_layout)
        
        # Initialize
        self.load_context_entries()
        
        return widget

    def load_context_entries(self):
        """Load context menu entries from registry"""
        self.context_table.setRowCount(0)
        
        # Only scan HKCU (user-created entries) to avoid duplicates and confusion
        # Scan both Software\Classes paths (HKCU) for user entries
        self._scan_shell_keys_hkcu(r"Software\Classes\Directory\shell", "Folder", winreg.HKEY_CURRENT_USER)
        self._scan_shell_keys_hkcu(r"Software\Classes\Directory\Background\shell", "Background", winreg.HKEY_CURRENT_USER)
        self._scan_shell_keys_hkcu(r"Software\Classes\*\shell", "All Files", winreg.HKEY_CURRENT_USER)

    def _scan_shell_keys_hkcu(self, base_path, scope_label, hkey, indent=""):
        """Recursive helper to scan for context menu items and groups in HKCU only"""
        try:
            key = winreg.OpenKey(hkey, base_path, 0, winreg.KEY_READ)
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    # Skip standard Windows entries
                    if subkey_name.lower() in ["cmd", "powershell", "anycode", "wsl"]:
                        i += 1
                        continue
                        
                    full_path = f"{base_path}\\{subkey_name}"
                    
                    # Try to get Label (from MUIVerb or default value)
                    label = subkey_name
                    icon = ""
                    is_sep = False
                    try:
                        subkey = winreg.OpenKey(hkey, full_path, 0, winreg.KEY_READ)
                        try:
                            label, _ = winreg.QueryValueEx(subkey, "MUIVerb")
                        except:
                            try:
                                val = winreg.QueryValue(subkey, "")
                                if val: label = val
                            except: pass
                        
                        # Check for Icon
                        try:
                            icon, _ = winreg.QueryValueEx(subkey, "Icon")
                        except: pass

                        # Check for Separator flag
                        try:
                            flags, _ = winreg.QueryValueEx(subkey, "CommandFlags")
                            if flags & 0x20: # 0x20 is separator before
                                is_sep = True
                        except: pass

                        winreg.CloseKey(subkey)
                    except: pass

                    # Check if it has a command (it's a leaf node)
                    cmd = ""
                    is_group = False
                    try:
                        cmd_key = winreg.OpenKey(hkey, f"{full_path}\\command", 0, winreg.KEY_READ)
                        cmd, _ = winreg.QueryValueEx(cmd_key, "")
                        winreg.CloseKey(cmd_key)
                    except:
                        # No command key? Check if it has a 'shell' subkey (it's a group)
                        try:
                            shell_key = winreg.OpenKey(hkey, f"{full_path}\\shell", 0, winreg.KEY_READ)
                            winreg.CloseKey(shell_key)
                            is_group = True
                            cmd = "(Cascading Menu)"
                        except:
                            # It might just be an empty/broken entry
                            pass

                    # Add to table
                    row = self.context_table.rowCount()
                    self.context_table.insertRow(row)
                    
                    # Store the internal path in the item data for editing/removal
                    display_label = f"{indent}{label}"
                    if is_sep: display_label = f"{indent}--- SEPARATOR ---"
                    
                    label_item = QTableWidgetItem(f"{display_label}")
                    # Store both the path and scope for proper deletion
                    label_item.setData(Qt.ItemDataRole.UserRole, full_path)
                    label_item.setData(Qt.ItemDataRole.UserRole + 1, scope_label)
                    
                    self.context_table.setItem(row, 0, label_item)
                    self.context_table.setItem(row, 1, QTableWidgetItem("GROUP" if is_group else "ENTRY"))
                    self.context_table.setItem(row, 2, QTableWidgetItem(cmd))
                    
                    # If it's a group, recurse
                    if is_group:
                        self._scan_shell_keys_hkcu(f"{full_path}\\shell", scope_label, hkey, indent + "  ↳ ")
                        
                    i += 1
                except OSError:
                    break
            winreg.CloseKey(key)
        except Exception as e:
            # Key doesn't exist yet, which is fine
            pass

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

        name, ok = QInputDialog.getText(self, "Add Context Group", "Group Label:")
        if ok and name:
            try:
                if parent_path:
                    # Nested group - parent_path is already in HKCU format
                    path = rf"{parent_path}\shell\{name}"
                    self._create_group_entry(path)
                else:
                    # Top level group - only create in Background (right-click on folder background)
                    # This avoids duplicate entries in the list
                    self._create_group_entry(rf"Software\Classes\Directory\Background\shell\{name}")

                self.load_context_entries()
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

        name, ok1 = QInputDialog.getText(self, "Add Context Entry", "Menu Label (e.g. 'Open Terminal Here'):")
        if ok1 and name:
            cmd, ok2 = QInputDialog.getText(self, "Add Context Entry", f"Command to execute for '{name}':\n(Use %V for current directory)")
            if ok2 and cmd:
                # Auto-fix common placeholder mistakes
                cmd = cmd.replace("{path}", "\"%V\"").replace("%1", "\"%V\"")
                
                try:
                    if parent_path:
                        # Add as child of selected group
                        # parent_path is already in HKCU format (Software\Classes\...)
                        self._create_reg_entry(rf"{parent_path}\shell\{name}", cmd)
                        
                        self.load_context_entries()
                        self.set_status(f"Added context menu entry: {name} to group", CP_GREEN)
                    else:
                        # Add to top level - only Background to avoid duplicates
                        self._create_reg_entry(rf"Software\Classes\Directory\Background\shell\{name}", cmd)
                        
                        self.load_context_entries()
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
        
        # Get current label (MUIVerb) from registry
        old_label = old_name
        old_icon = ""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, old_full_path, 0, winreg.KEY_READ)
            try:
                old_label, _ = winreg.QueryValueEx(key, "MUIVerb")
            except:
                pass
            try:
                old_icon, _ = winreg.QueryValueEx(key, "Icon")
            except:
                pass
            winreg.CloseKey(key)
        except:
            pass
        
        # Create dialog with form layout
        from PyQt6.QtWidgets import QDialog, QDialogButtonBox
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Context Entry")
        dialog.setMinimumWidth(500)
        dialog_layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        
        # Label field (what user sees in context menu)
        label_edit = QLineEdit(old_label)
        form_layout.addRow("Display Label:", label_edit)
        
        # Command field (only for ENTRY type)
        cmd_edit = None
        if type_text == "ENTRY":
            cmd_edit = QLineEdit(old_cmd)
            form_layout.addRow("Command:", cmd_edit)
        
        # Icon field
        icon_layout = QHBoxLayout()
        icon_edit = QLineEdit(old_icon)
        icon_browse = QPushButton("Browse...")
        icon_browse.clicked.connect(lambda: self._browse_icon(icon_edit))
        icon_layout.addWidget(icon_edit)
        icon_layout.addWidget(icon_browse)
        form_layout.addRow("Icon Path:", icon_layout)
        
        dialog_layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        dialog_layout.addWidget(button_box)
        
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        new_label = label_edit.text().strip()
        new_cmd = cmd_edit.text().strip() if cmd_edit else "(Cascading Menu)"
        new_icon = icon_edit.text().strip()
        
        if not new_label:
            return
            
        if type_text == "ENTRY" and new_cmd:
            new_cmd = new_cmd.replace("{path}", "\"%V\"").replace("%1", "\"%V\"")

        try:
            # Update the existing entry (don't rename the key, just update MUIVerb)
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, old_full_path, 0, winreg.KEY_SET_VALUE) as key:
                # Update the display label
                winreg.SetValueEx(key, "MUIVerb", 0, winreg.REG_SZ, new_label)
                
                # Set icon if provided
                if new_icon:
                    winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, new_icon)
                elif old_icon and not new_icon:
                    # Remove icon if cleared
                    try:
                        winreg.DeleteValue(key, "Icon")
                    except:
                        pass
            
            # Update command if it's an entry
            if type_text == "ENTRY" and new_cmd:
                cmd_path = f"{old_full_path}\\command"
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, cmd_path, 0, winreg.KEY_SET_VALUE) as cmd_key:
                    winreg.SetValue(cmd_key, "", winreg.REG_SZ, new_cmd)
                
            self.load_context_entries()
            self.set_status(f"Updated context menu entry: {new_label}", CP_GREEN)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update entry: {str(e)}")

    def _copy_reg_key(self, hkey, src, dst):
        """Helper to recursively copy a registry key"""
        try:
            with winreg.OpenKey(hkey, src, 0, winreg.KEY_READ) as src_key:
                # Copy values
                with winreg.CreateKey(hkey, dst) as dst_key:
                    i = 0
                    while True:
                        try:
                            name, value, type = winreg.EnumValue(src_key, i)
                            winreg.SetValueEx(dst_key, name, 0, type, value)
                            i += 1
                        except OSError: 
                            break
                
                # Copy subkeys
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(src_key, i)
                        self._copy_reg_key(hkey, f"{src}\\{subkey_name}", f"{dst}\\{subkey_name}")
                        i += 1
                    except OSError: 
                        break
        except Exception as e:
            print(f"Error copying registry key {src} to {dst}: {e}")
    
    def _browse_icon(self, line_edit):
        """Helper to browse for icon file"""
        icon_path, _ = QFileDialog.getOpenFileName(self, "Select Icon File", "", 
                                                  "Icons (*.ico *.exe *.dll);;All Files (*.*)")
        if icon_path:
            line_edit.setText(icon_path)

    def _create_reg_entry(self, path, command):
        """Helper to create registry keys for context menu in HKCU"""
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, path)
        label = path.split('\\')[-1]
        winreg.SetValue(key, "", winreg.REG_SZ, label) 
        
        cmd_key = winreg.CreateKey(key, "command")
        winreg.SetValue(cmd_key, "", winreg.REG_SZ, command)
        
        winreg.CloseKey(cmd_key)
        winreg.CloseKey(key)

    def remove_context_entry(self):
        """Remove a context menu entry"""
        row = self.context_table.currentRow()
        if row >= 0:
            full_path = self.context_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            scope_label = self.context_table.item(row, 0).data(Qt.ItemDataRole.UserRole + 1)
            # Extract label for display
            display_name = self.context_table.item(row, 0).text().split('[')[0].strip()
            
            reply = QMessageBox.question(self, "Confirm", f"Remove '{display_name}' and all its sub-items?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    # Delete from HKCU (where we store user entries)
                    self._delete_reg_key(winreg.HKEY_CURRENT_USER, full_path)
                    
                    self.load_context_entries()
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

    # ===== SCRIPT MANAGEMENT METHODS =====

    def create_scripts_tab(self):
        """Create tab for creating and managing custom scripts"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left Side: Script List
        list_container = QWidget()
        list_layout = QVBoxLayout(list_container)
        
        self.script_list = QListWidget()
        self.script_list.itemClicked.connect(self.load_script_content)
        list_layout.addWidget(QLabel("📜 SCRIPTS"))
        list_layout.addWidget(self.script_list)
        
        list_btns = QHBoxLayout()
        new_btn = QPushButton("🆕 NEW")
        del_btn = QPushButton("🗑️ DELETE")
        new_btn.clicked.connect(self.create_new_script)
        del_btn.clicked.connect(self.delete_script)
        list_btns.addWidget(new_btn)
        list_btns.addWidget(del_btn)
        list_layout.addLayout(list_btns)
        
        # Right Side: Editor
        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        
        self.script_editor = QTextEdit()
        self.script_editor.setPlaceholderText("Write your script here (Python, Batch, etc.)...")
        
        self.script_name_label = QLabel("No script selected")
        self.script_name_label.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold;")
        
        editor_layout.addWidget(self.script_name_label)
        editor_layout.addWidget(self.script_editor)
        
        editor_btns = QHBoxLayout()
        save_btn = QPushButton("💾 SAVE SCRIPT")
        ctx_btn = QPushButton("🖱️ ADD TO CONTEXT MENU")
        save_btn.clicked.connect(self.save_current_script)
        ctx_btn.clicked.connect(self.add_script_to_context)
        
        save_btn.setStyleSheet(f"background-color: {CP_PANEL}; border: 1px solid {CP_GREEN}; color: {CP_GREEN};")
        ctx_btn.setStyleSheet(f"background-color: {CP_PANEL}; border: 1px solid {CP_CYAN}; color: {CP_CYAN};")
        
        editor_btns.addWidget(save_btn)
        editor_btns.addWidget(ctx_btn)
        editor_layout.addLayout(editor_btns)
        
        splitter.addWidget(list_container)
        splitter.addWidget(editor_container)
        splitter.setStretchFactor(1, 2)
        
        layout.addWidget(splitter)
        
        # Load initial list
        self.load_scripts_list()
        
        return widget

    def load_scripts_list(self):
        """Reload list of scripts from disk"""
        self.script_list.clear()
        if os.path.exists(self.scripts_dir):
            for file in os.listdir(self.scripts_dir):
                if os.path.isfile(os.path.join(self.scripts_dir, file)):
                    self.script_list.addItem(file)

    def load_script_content(self, item):
        """Load selected script into editor"""
        name = item.text()
        path = os.path.join(self.scripts_dir, name)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.script_editor.setPlainText(f.read())
            self.script_name_label.setText(f"EDITING: {name}")
            self.current_editing_script = name
        except Exception as e:
            self.set_status(f"Error loading script: {e}", CP_RED)

    def save_current_script(self):
        """Save editor content to file"""
        if not hasattr(self, 'current_editing_script') or not self.current_editing_script:
            self.create_new_script()
            return
            
        path = os.path.join(self.scripts_dir, self.current_editing_script)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.script_editor.toPlainText())
            self.set_status(f"Saved {self.current_editing_script}", CP_GREEN)
        except Exception as e:
            self.set_status(f"Save failed: {e}", CP_RED)

    def create_new_script(self):
        """Create a new script file"""
        name, ok = QInputDialog.getText(self, "New Script", "Filename (e.g. clean_temp.bat):")
        if ok and name:
            path = os.path.join(self.scripts_dir, name)
            if os.path.exists(path):
                QMessageBox.warning(self, "Warning", "File already exists!")
                return
            
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write("")
                self.load_scripts_list()
                # Select it
                items = self.script_list.findItems(name, Qt.MatchFlag.MatchExactly)
                if items:
                    self.script_list.setCurrentItem(items[0])
                    self.load_script_content(items[0])
            except Exception as e:
                self.set_status(f"Creation failed: {e}", CP_RED)

    def delete_script(self):
        """Delete selected script"""
        current = self.script_list.currentItem()
        if current:
            name = current.text()
            reply = QMessageBox.question(self, "Confirm", f"Delete '{name}' permanently?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    os.remove(os.path.join(self.scripts_dir, name))
                    self.load_scripts_list()
                    self.script_editor.clear()
                    self.script_name_label.setText("No script selected")
                    self.current_editing_script = None
                    self.set_status(f"Deleted {name}", CP_GREEN)
                except Exception as e:
                    self.set_status(f"Delete failed: {e}", CP_RED)

    def add_script_to_context(self):
        """Quickly add current script to context menu"""
        if not hasattr(self, 'current_editing_script') or not self.current_editing_script:
            QMessageBox.warning(self, "Error", "No script selected!")
            return
            
        name = self.current_editing_script
        path = os.path.join(self.scripts_dir, name)
        
        # Determine command based on extension
        # Use %1 as it works for both files and directories
        cmd = ""
        if name.endswith(".py"):
            cmd = f'python.exe "{path}" "%1"'
        elif name.endswith(".bat") or name.endswith(".cmd"):
            cmd = f'"{path}" "%1"'
        elif name.endswith(".ps1"):
            cmd = f'powershell.exe -ExecutionPolicy Bypass -File "{path}" "%1"'
        else:
            cmd = f'"{path}" "%1"'
            
        label, ok = QInputDialog.getText(self, "Context Menu Label", 
                                        "Menu Label for this script:", 
                                        text=f"Run {name}")
        if ok and label:
            try:
                # Register for Files (*), Folders (Directory), and Background
                self._create_reg_entry(rf"Software\Classes\*\shell\{label}", cmd)
                self._create_reg_entry(rf"Software\Classes\Directory\shell\{label}", cmd)
                self._create_reg_entry(rf"Software\Classes\Directory\Background\shell\{label}", cmd)
                
                self.load_context_entries()
                QMessageBox.information(self, "Success", f"'{label}' added to context menu for files and folders.")
            except PermissionError:
                QMessageBox.critical(self, "Error", "Permission Denied. Run as Admin.")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    # ===== BACKUP / RESTORE METHODS =====

    def create_backup_tab(self):
        """Create backup and restore tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        info = QLabel("💾 BACKUP & RESTORE SYSTEM CONFIGURATION")
        info.setStyleSheet(f"font-size: 14pt; color: {CP_YELLOW}; padding: 10px;")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)
        
        desc = QLabel("Export all environment variables, PATH entries, aliases, scripts, and context menu entries to a JSON file.\n"
                      "Warning: Restoring from backup will overwrite existing settings.")
        desc.setStyleSheet(f"color: {CP_SUBTEXT}; padding: 10px;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        
        btn_layout = QHBoxLayout()
        backup_btn = QPushButton("📤 EXPORT TO JSON")
        import_btn = QPushButton("📥 IMPORT FROM JSON")
        
        backup_btn.setMinimumHeight(60)
        import_btn.setMinimumHeight(60)
        
        backup_btn.setStyleSheet(f"background-color: {CP_PANEL}; border: 2px solid {CP_CYAN}; color: {CP_CYAN}; font-size: 12pt;")
        import_btn.setStyleSheet(f"background-color: {CP_PANEL}; border: 2px solid {CP_ORANGE}; color: {CP_ORANGE}; font-size: 12pt;")
        
        backup_btn.clicked.connect(self.export_config)
        import_btn.clicked.connect(self.import_config)
        
        btn_layout.addWidget(backup_btn)
        btn_layout.addWidget(import_btn)
        layout.addLayout(btn_layout)
        
        layout.addStretch()
        
        return widget

    def get_all_registry_vars(self, hkey, subkey):
        """Helper to get all vars from a registry key"""
        vars_dict = {}
        try:
            key = winreg.OpenKey(hkey, subkey, 0, winreg.KEY_READ)
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    vars_dict[name] = value
                    i += 1
                except OSError:
                    break
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Error reading registry {subkey}: {e}")
        return vars_dict

    def get_context_menu_data(self):
        """Collect all custom context menu entries for backup with full structure"""
        context_data = {}
        
        # Scan HKCU (user-created entries) to get everything we manage
        bases = [
            ("Directory\\Background\\shell", "Background"),
            ("Directory\\shell", "Folder"),
            ("*\\shell", "AllFiles")
        ]
        
        for base_path, scope in bases:
            full_base = f"Software\\Classes\\{base_path}"
            try:
                entries = self._export_shell_keys(winreg.HKEY_CURRENT_USER, full_base)
                if entries:
                    context_data[scope] = entries
            except:
                pass
        
        return context_data
    
    def _export_shell_keys(self, hkey, base_path):
        """Recursively export shell keys with all properties"""
        entries = {}
        
        try:
            key = winreg.OpenKey(hkey, base_path, 0, winreg.KEY_READ)
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    # Skip standard Windows entries
                    if subkey_name.lower() in ["cmd", "powershell", "anycode", "wsl"]:
                        i += 1
                        continue
                    
                    full_path = f"{base_path}\\{subkey_name}"
                    entry_data = {}
                    
                    # Get all properties
                    try:
                        subkey = winreg.OpenKey(hkey, full_path, 0, winreg.KEY_READ)
                        
                        # Get MUIVerb (display label)
                        try:
                            entry_data["MUIVerb"], _ = winreg.QueryValueEx(subkey, "MUIVerb")
                        except:
                            pass
                        
                        # Get Icon
                        try:
                            entry_data["Icon"], _ = winreg.QueryValueEx(subkey, "Icon")
                        except:
                            pass
                        
                        # Get SubCommands (for groups)
                        try:
                            entry_data["SubCommands"], _ = winreg.QueryValueEx(subkey, "SubCommands")
                        except:
                            pass
                        
                        # Get CommandFlags
                        try:
                            entry_data["CommandFlags"], _ = winreg.QueryValueEx(subkey, "CommandFlags")
                        except:
                            pass
                        
                        winreg.CloseKey(subkey)
                    except:
                        pass
                    
                    # Check if it has a command (it's a leaf entry)
                    try:
                        cmd_key = winreg.OpenKey(hkey, f"{full_path}\\command", 0, winreg.KEY_READ)
                        cmd_value, _ = winreg.QueryValueEx(cmd_key, "")
                        entry_data["command"] = cmd_value
                        winreg.CloseKey(cmd_key)
                    except:
                        pass
                    
                    # Check if it has a shell subkey (it's a group with children)
                    try:
                        shell_path = f"{full_path}\\shell"
                        shell_key = winreg.OpenKey(hkey, shell_path, 0, winreg.KEY_READ)
                        winreg.CloseKey(shell_key)
                        # Recursively get children
                        entry_data["children"] = self._export_shell_keys(hkey, shell_path)
                    except:
                        pass
                    
                    entries[subkey_name] = entry_data
                    i += 1
                except OSError:
                    break
            winreg.CloseKey(key)
        except:
            pass
        
        return entries
    
    def _import_shell_entries(self, hkey, base_path, entries):
        """Recursively import shell entries with all properties"""
        for name, data in entries.items():
            full_path = f"{base_path}\\{name}"
            
            try:
                # Create the key
                key = winreg.CreateKey(hkey, full_path)
                
                # Set MUIVerb if present
                if "MUIVerb" in data:
                    winreg.SetValueEx(key, "MUIVerb", 0, winreg.REG_SZ, data["MUIVerb"])
                
                # Set Icon if present
                if "Icon" in data:
                    winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, data["Icon"])
                
                # Set SubCommands if present (for groups)
                if "SubCommands" in data:
                    winreg.SetValueEx(key, "SubCommands", 0, winreg.REG_SZ, data["SubCommands"])
                
                # Set CommandFlags if present
                if "CommandFlags" in data:
                    winreg.SetValueEx(key, "CommandFlags", 0, winreg.REG_DWORD, data["CommandFlags"])
                
                winreg.CloseKey(key)
                
                # Create command subkey if present
                if "command" in data:
                    cmd_key = winreg.CreateKey(hkey, f"{full_path}\\command")
                    winreg.SetValue(cmd_key, "", winreg.REG_SZ, data["command"])
                    winreg.CloseKey(cmd_key)
                
                # Recursively import children if present
                if "children" in data and data["children"]:
                    shell_key = winreg.CreateKey(hkey, f"{full_path}\\shell")
                    winreg.CloseKey(shell_key)
                    self._import_shell_entries(hkey, f"{full_path}\\shell", data["children"])
                    
            except Exception as e:
                print(f"Error importing {name}: {e}")

    def export_config(self):
        """Export all settings to JSON (Fixed to data.json)"""
        # Save in the same directory as the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, "data.json")
            
        try:
            # Collect scripts
            scripts_data = {}
            if os.path.exists(self.scripts_dir):
                for name in os.listdir(self.scripts_dir):
                    p = os.path.join(self.scripts_dir, name)
                    if os.path.isfile(p):
                        try:
                            with open(p, 'r', encoding='utf-8') as f:
                                scripts_data[name] = f.read()
                        except: pass

            # Get context menu data with error handling
            context_menu_data = {}
            try:
                context_menu_data = self.get_context_menu_data()
            except Exception as e:
                print(f"Warning: Could not export context menu data: {e}")
                context_menu_data = {}

            config = {
                "version": "1.3",
                "timestamp": datetime.now().isoformat(),
                "user_env": self.get_all_registry_vars(winreg.HKEY_CURRENT_USER, r"Environment"),
                "system_env": self.get_all_registry_vars(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"),
                "aliases": self.aliases,
                "context_menu": context_menu_data,
                "scripts": scripts_data
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            
            self.set_status(f"Exported to data.json", CP_GREEN)
            QMessageBox.information(self, "Success", f"Configuration exported to:\n{file_path}")
        except Exception as e:
            self.set_status(f"Export failed: {str(e)}", CP_RED)
            QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")

    def import_config(self):
        """Import settings from data.json (Fixed)"""
        # Look in the same directory as the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, "data.json")
        
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "Error", f"data.json not found at:\n{file_path}")
            return
            
        try:
            with open(file_path, 'r') as f:
                config = json.load(f)
            
            # Basic validation
            if "user_env" not in config and "system_env" not in config and "aliases" not in config and "context_menu" not in config and "scripts" not in config:
                raise ValueError("Invalid configuration file format.")
            
            reply = QMessageBox.question(self, "Confirm Import", 
                                        "This will overwrite existing environment variables, aliases, context menu entries, and scripts. Continue?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply != QMessageBox.StandardButton.Yes:
                return

            # Import User Env
            if "user_env" in config:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_SET_VALUE)
                for name, value in config["user_env"].items():
                    winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, str(value))
                winreg.CloseKey(key)

            # Import System Env (might need admin)
            if "system_env" in config:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                        r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 
                                        0, winreg.KEY_SET_VALUE)
                    for name, value in config["system_env"].items():
                        winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, str(value))
                    winreg.CloseKey(key)
                except PermissionError:
                    QMessageBox.warning(self, "Permission Denied", "Could not import System variables. Please run as Administrator.")

            # Import Aliases
            if "aliases" in config:
                self.aliases.update(config["aliases"])
                self.save_aliases()

            # Import Context Menu
            if "context_menu" in config:
                try:
                    for scope, entries in config["context_menu"].items():
                        # Determine base path based on scope
                        if scope == "Background":
                            base_path = r"Software\Classes\Directory\Background\shell"
                        elif scope == "Folder":
                            base_path = r"Software\Classes\Directory\shell"
                        elif scope == "AllFiles":
                            base_path = r"Software\Classes\*\shell"
                        else:
                            continue
                        
                        # Import entries recursively
                        self._import_shell_entries(winreg.HKEY_CURRENT_USER, base_path, entries)
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Could not import Context Menu entries: {str(e)}")

            # Import Scripts
            if "scripts" in config:
                os.makedirs(self.scripts_dir, exist_ok=True)
                for name, content in config["scripts"].items():
                    p = os.path.join(self.scripts_dir, name)
                    try:
                        with open(p, 'w', encoding='utf-8') as f:
                            f.write(content)
                    except: pass
                self.load_scripts_list()

            self.broadcast_env_change()
            self.load_path_vars(self.current_path_scope)
            self.load_env_vars(self.current_env_scope)
            self.load_aliases()
            self.load_context_entries()
            
            self.set_status("Configuration imported successfully", CP_GREEN)
            QMessageBox.information(self, "Import Success", "Configuration imported and applied.\nYou may need to restart your shell.")
            
        except Exception as e:
            self.set_status(f"Import failed: {str(e)}", CP_RED)
            QMessageBox.critical(self, "Error", f"Failed to import: {str(e)}")
    
    # ===== UTILITY METHODS =====
    
    def broadcast_env_change(self):
        """Notify Windows of environment variable changes"""
        try:
            import win32gui
            import win32con
            # Use SendMessageTimeout to avoid hanging if an application is unresponsive
            # HWND_BROADCAST = 0xFFFF, WM_SETTINGCHANGE = 0x001A
            win32gui.SendMessageTimeout(
                win32con.HWND_BROADCAST, 
                win32con.WM_SETTINGCHANGE, 
                0, 
                "Environment", 
                win32con.SMTO_ABORTIFHUNG, 
                1000, # 1 second timeout
                None
            )
        except Exception:
            # pywin32 not installed or other error, changes will apply after restart
            pass
    
    def set_status(self, message, color=CP_TEXT):
        """Update status bar"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {color}; font-weight: bold; padding: 5px;")


def main():
    app = QApplication(sys.argv)
    
    # Diagnostic: Print available JetBrains fonts
    jb_fonts = [f for f in QFontDatabase.families() if "JetBrains" in f]
    if jb_fonts:
        print(f"DEBUG: Found JetBrains fonts: {', '.join(jb_fonts)}")
    else:
        print("DEBUG: No JetBrains fonts found in system!")

    # Try to set JetBrainsMono NFP as the default font
    font_name = "JetBrainsMono NFP"
    font = QFont(font_name, 10)
    
    # Check if font is actually available, otherwise it might fallback to system default
    if font_name not in QFontDatabase.families():
        # Fallback to similar names if the exact one isn't found
        for family in QFontDatabase.families():
            if "JetBrainsMono" in family and "NFP" in family:
                font = QFont(family, 10)
                break
    
    app.setFont(font)
    
    window = EnvVariableManager()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
