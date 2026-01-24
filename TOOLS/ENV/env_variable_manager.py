import sys
import os
import winreg
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QLineEdit, QGroupBox, QListWidget, 
                             QMessageBox, QInputDialog, QTabWidget, QTextEdit, QSplitter,
                             QListWidgetItem, QFormLayout, QTableWidget, QTableWidgetItem,
                             QHeaderView)
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
        
        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_path_tab(), "PATH MANAGER")
        self.tabs.addTab(self.create_env_tab(), "ENV VARIABLES")
        self.tabs.addTab(self.create_alias_tab(), "ALIASES")
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
                import json
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
            import json
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
