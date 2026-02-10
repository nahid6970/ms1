import sys
import os
import winreg
import json
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QLineEdit, QGroupBox, QListWidget, 
                             QMessageBox, QInputDialog, QTabWidget, QTextEdit, QSplitter,
                             QListWidgetItem, QFormLayout, QTableWidget, QTableWidgetItem,
                             QHeaderView, QFileDialog)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont

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
        
        # Title
        title = QLabel("⚡ ENVIRONMENT VARIABLE CONTROL PANEL ⚡")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"font-size: 16pt; font-weight: bold; color: {CP_YELLOW}; padding: 10px;")
        main_layout.addWidget(title)
        
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
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            
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
        
        add_btn.clicked.connect(self.add_path_entry)
        edit_btn.clicked.connect(self.edit_path_entry)
        remove_btn.clicked.connect(self.remove_path_entry)
        up_btn.clicked.connect(self.move_path_up)
        down_btn.clicked.connect(self.move_path_down)
        refresh_btn.clicked.connect(lambda: self.load_path_vars(self.current_path_scope))
        
        controls_layout.addWidget(add_btn)
        controls_layout.addWidget(edit_btn)
        controls_layout.addWidget(remove_btn)
        controls_layout.addWidget(up_btn)
        controls_layout.addWidget(down_btn)
        controls_layout.addWidget(refresh_btn)
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
            if scope == "user":
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_READ)
            else:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                    r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                                    0, winreg.KEY_READ)
            
            path_value, _ = winreg.QueryValueEx(key, "Path")
            winreg.CloseKey(key)
            
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
            
            if self.current_path_scope == "user":
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, 
                                    winreg.KEY_SET_VALUE)
            else:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                    r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                                    0, winreg.KEY_SET_VALUE)
            
            winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, path_value)
            winreg.CloseKey(key)
            
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
                    if self.current_env_scope == "user":
                        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0,
                                            winreg.KEY_SET_VALUE)
                    else:
                        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                            r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                                            0, winreg.KEY_SET_VALUE)
                    
                    winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)
                    winreg.CloseKey(key)
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
            name = self.env_table.item(current_row, 0).text()
            old_value = self.env_table.item(current_row, 1).text()
            
            value, ok = QInputDialog.getText(self, "Edit Variable", f"New value for {name}:",
                                            text=old_value)
            if ok:
                try:
                    if self.current_env_scope == "user":
                        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0,
                                            winreg.KEY_SET_VALUE)
                    else:
                        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                            r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                                            0, winreg.KEY_SET_VALUE)
                    
                    winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)
                    winreg.CloseKey(key)
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
            name = self.env_table.item(current_row, 0).text()
            
            reply = QMessageBox.question(self, "Confirm", f"Delete variable '{name}'?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    if self.current_env_scope == "user":
                        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0,
                                            winreg.KEY_SET_VALUE)
                    else:
                        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                            r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                                            0, winreg.KEY_SET_VALUE)
                    
                    winreg.DeleteValue(key, name)
                    winreg.CloseKey(key)
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
        
        info = QLabel("🖱️ SHELL CONTEXT MENU MANAGER")
        info.setStyleSheet(f"font-size: 14pt; color: {CP_CYAN}; padding: 10px;")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)
        
        desc = QLabel("Add custom actions to the Windows Explorer right-click menu (Background & Folders).")
        desc.setStyleSheet(f"color: {CP_SUBTEXT}; padding: 5px;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        
        # Menu Table
        list_group = QGroupBox("CONTEXT MENU ENTRIES")
        list_layout = QVBoxLayout()
        self.context_table = QTableWidget()
        self.context_table.setColumnCount(3)
        self.context_table.setHorizontalHeaderLabels(["Menu Label", "Type", "Command / Script"])
        self.context_table.horizontalHeader().setStretchLastSection(True)
        self.context_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        list_layout.addWidget(self.context_table)
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        # Controls
        controls_layout = QHBoxLayout()
        add_btn = QPushButton("➕ ADD ENTRY")
        add_group_btn = QPushButton("📁 ADD GROUP")
        edit_btn = QPushButton("✏️ EDIT")
        remove_btn = QPushButton("❌ REMOVE")
        refresh_btn = QPushButton("🔄 REFRESH")
        
        add_btn.clicked.connect(self.add_context_entry)
        add_group_btn.clicked.connect(self.add_context_group)
        edit_btn.clicked.connect(self.edit_context_entry)
        remove_btn.clicked.connect(self.remove_context_entry)
        refresh_btn.clicked.connect(self.load_context_entries)
        
        controls_layout.addWidget(add_btn)
        controls_layout.addWidget(add_group_btn)
        controls_layout.addWidget(edit_btn)
        controls_layout.addWidget(remove_btn)
        controls_layout.addWidget(refresh_btn)
        layout.addLayout(controls_layout)
        layout.addLayout(controls_layout)
        
        # Initialize
        self.load_context_entries()
        
        return widget

    def load_context_entries(self):
        """Load context menu entries from registry"""
        self.context_table.setRowCount(0)
        
        # Scan both folder right-click and background right-click
        # We use HKCR for a complete view, but HKCU entries will be what we manage
        self._scan_shell_keys(r"Directory\shell", "Folder")
        self._scan_shell_keys(r"Directory\Background\shell", "Background")

    def _scan_shell_keys(self, base_path, scope_label, indent=""):
        """Recursive helper to scan for context menu items and groups"""
        try:
            key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, base_path, 0, winreg.KEY_READ)
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
                    try:
                        subkey = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, full_path, 0, winreg.KEY_READ)
                        try:
                            label, _ = winreg.QueryValueEx(subkey, "MUIVerb")
                        except:
                            try:
                                val = winreg.QueryValue(subkey, "")
                                if val: label = val
                            except: pass
                        winreg.CloseKey(subkey)
                    except: pass

                    # Check if it has a command (it's a leaf node)
                    cmd = ""
                    is_group = False
                    try:
                        cmd_key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, f"{full_path}\\command", 0, winreg.KEY_READ)
                        cmd, _ = winreg.QueryValueEx(cmd_key, "")
                        winreg.CloseKey(cmd_key)
                    except:
                        # No command key? Check if it has a 'shell' subkey (it's a group)
                        try:
                            shell_key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, f"{full_path}\\shell", 0, winreg.KEY_READ)
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
                    label_item = QTableWidgetItem(f"{indent}{label} [{scope_label}]")
                    label_item.setData(Qt.ItemDataRole.UserRole, full_path)
                    
                    self.context_table.setItem(row, 0, label_item)
                    self.context_table.setItem(row, 1, QTableWidgetItem("GROUP" if is_group else "ENTRY"))
                    self.context_table.setItem(row, 2, QTableWidgetItem(cmd))
                    
                    # If it's a group, recurse
                    if is_group:
                        self._scan_shell_keys(f"{full_path}\\shell", scope_label, indent + "  ↳ ")
                        
                    i += 1
                except OSError:
                    break
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Error scanning {base_path}: {e}")

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
                    # Nested group
                    # We must write to HKCU version of the path
                    hkcu_base = parent_path.replace("Directory\\", "Software\\Classes\\Directory\\")
                    path = rf"{hkcu_base}\shell\{name}"
                else:
                    # Top level groups (add to both locations)
                    self._create_group_entry(rf"Software\Classes\Directory\shell\{name}")
                    self._create_group_entry(rf"Software\Classes\Directory\Background\shell\{name}")
                    path = "" # Already handled

                if path:
                    self._create_group_entry(path)

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
                        hkcu_base = parent_path.replace("Directory\\", "Software\\Classes\\Directory\\")
                        self._create_reg_entry(rf"{hkcu_base}\shell\{name}", cmd)
                    else:
                        # Add to top level (both locations)
                        self._create_reg_entry(rf"Software\Classes\Directory\shell\{name}", cmd)
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
        # Extract name from path
        old_name = old_full_path.split('\\')[-1]
        type_text = self.context_table.item(row, 1).text()
        old_cmd = self.context_table.item(row, 2).text()
        
        # Edit Name
        new_name, ok1 = QInputDialog.getText(self, "Edit Context Entry", "Menu Label:", text=old_name)
        if not ok1 or not new_name:
            return
            
        if type_text == "ENTRY":
            # Edit Command
            new_cmd, ok2 = QInputDialog.getText(self, "Edit Context Entry", "Command:", text=old_cmd)
            if not ok2 or not new_cmd:
                return
            # Auto-fix common placeholder mistakes
            new_cmd = new_cmd.replace("{path}", "\"%V\"").replace("%1", "\"%V\"")
        else:
            new_cmd = "(Cascading Menu)"
            
        if new_name == old_name and new_cmd == old_cmd:
            return # No changes

        try:
            # We must work with HKCU path
            hkcu_path = old_full_path.replace("Directory\\", "Software\\Classes\\Directory\\")
            parent_path = "\\".join(hkcu_path.split('\\')[:-1])
            new_hkcu_path = f"{parent_path}\\{new_name}"

            if type_text == "ENTRY":
                self._create_reg_entry(new_hkcu_path, new_cmd)
            else:
                self._create_group_entry(new_hkcu_path)
            
            # If name changed, delete old keys
            if new_name != old_name:
                self._delete_reg_key(winreg.HKEY_CURRENT_USER, hkcu_path)
                
            self.load_context_entries()
            self.set_status(f"Updated context menu entry: {new_name}", CP_GREEN)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update entry: {str(e)}")

    def _create_reg_entry(self, path, command):
        """Helper to create registry keys for context menu in HKCU"""
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, path)
        winreg.SetValue(key, "", winreg.REG_SZ, "") 
        
        cmd_key = winreg.CreateKey(key, "command")
        winreg.SetValue(cmd_key, "", winreg.REG_SZ, command)
        
        winreg.CloseKey(cmd_key)
        winreg.CloseKey(key)

    def remove_context_entry(self):
        """Remove a context menu entry"""
        row = self.context_table.currentRow()
        if row >= 0:
            full_path = self.context_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            # Extract label for display
            display_name = self.context_table.item(row, 0).text().split('[')[0].strip()
            
            reply = QMessageBox.question(self, "Confirm", f"Remove '{display_name}' and all its sub-items?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    # Convert HKCR path to HKCU path for deletion
                    hkcu_path = full_path.replace("Directory\\", "Software\\Classes\\Directory\\")
                    self._delete_reg_key(winreg.HKEY_CURRENT_USER, hkcu_path)
                    
                    self.load_context_entries()
                    self.set_status(f"Removed {display_name}", CP_GREEN)
                except Exception as e:
                    self.set_status(f"Error removing entry: {str(e)}", CP_RED)

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
        cmd = ""
        if name.endswith(".py"):
            cmd = f'python "{path}" "%V"'
        elif name.endswith(".bat") or name.endswith(".cmd"):
            cmd = f'"{path}" "%V"'
        elif name.endswith(".ps1"):
            cmd = f'powershell -ExecutionPolicy Bypass -File "{path}" "%V"'
        else:
            cmd = f'"{path}" "%V"'
            
        label, ok = QInputDialog.getText(self, "Context Menu Label", 
                                        "Menu Label for this script:", 
                                        text=f"Run {name}")
        if ok and label:
            try:
                self._create_reg_entry(rf"Directory\shell\{label}", cmd)
                self._create_reg_entry(rf"Directory\Background\shell\{label}", cmd)
                self.load_context_entries()
                QMessageBox.information(self, "Success", f"'{label}' added to context menu.")
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
        """Collect all custom context menu entries for backup"""
        entries = {}
        paths = [r"Directory\Background\shell", r"Directory\shell"]
        for base_path in paths:
            try:
                key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, base_path, 0, winreg.KEY_READ)
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        if subkey_name.lower() in ["cmd", "powershell", "anycode"]:
                            i += 1
                            continue
                        try:
                            cmd_key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, f"{base_path}\\{subkey_name}\\command", 0, winreg.KEY_READ)
                            cmd_value, _ = winreg.QueryValueEx(cmd_key, "")
                            winreg.CloseKey(cmd_key)
                            entries[subkey_name] = cmd_value
                        except:
                            pass
                        i += 1
                    except OSError:
                        break
                winreg.CloseKey(key)
            except:
                pass
        return entries

    def export_config(self):
        """Export all settings to JSON (Fixed to data.json)"""
        file_path = os.path.join(os.getcwd(), "data.json")
            
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

            config = {
                "version": "1.2",
                "timestamp": datetime.now().isoformat(),
                "user_env": self.get_all_registry_vars(winreg.HKEY_CURRENT_USER, r"Environment"),
                "system_env": self.get_all_registry_vars(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"),
                "aliases": self.aliases,
                "context_menu": self.get_context_menu_data(),
                "scripts": scripts_data
            }
            
            with open(file_path, 'w') as f:
                json.dump(config, f, indent=4)
            
            self.set_status(f"Auto-exported to data.json", CP_GREEN)
        except Exception as e:
            self.set_status(f"Export failed: {str(e)}", CP_RED)
            QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")

    def import_config(self):
        """Import settings from data.json (Fixed)"""
        file_path = os.path.join(os.getcwd(), "data.json")
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "Error", "data.json not found in current directory.")
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
                    for name, cmd in config["context_menu"].items():
                        self._create_reg_entry(rf"Directory\shell\{name}", cmd)
                        self._create_reg_entry(rf"Directory\Background\shell\{name}", cmd)
                except PermissionError:
                    QMessageBox.warning(self, "Permission Denied", "Could not import Context Menu entries. Please run as Administrator.")

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
            win32gui.SendMessage(win32con.HWND_BROADCAST, win32con.WM_SETTINGCHANGE, 0, "Environment")
        except ImportError:
            # pywin32 not installed, changes will apply after restart
            pass
    
    def set_status(self, message, color=CP_TEXT):
        """Update status bar"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {color}; font-weight: bold; padding: 5px;")


def main():
    app = QApplication(sys.argv)
    
    # Set application font
    font = QFont("Consolas", 10)
    app.setFont(font)
    
    window = EnvVariableManager()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
