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
from PyQt6.QtCore import Qt
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
        
        # Apply Cyberpunk Theme
        self.apply_theme()
        
        # Main Layout
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        # Status Bar
        self.status_label = QLabel("SYSTEM READY")
        self.status_label.setStyleSheet(f"color: {CP_GREEN}; font-weight: bold; padding: 5px;")
        
        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_alias_tab(), "ALIASES")
        self.tabs.addTab(self.create_context_tab(), "CONTEXT MENU")
        self.tabs.addTab(self.create_backup_tab(), "BACKUP/RESTORE")
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
        
        add_btn.clicked.connect(self.add_context_entry)
        add_group_btn.clicked.connect(self.add_context_group)
        edit_btn.clicked.connect(self.edit_context_entry)
        remove_btn.clicked.connect(self.remove_context_entry)
        up_btn.clicked.connect(self.move_context_up)
        down_btn.clicked.connect(self.move_context_down)
        refresh_btn.clicked.connect(self.load_context_entries)
        
        controls_layout.addWidget(add_btn)
        controls_layout.addWidget(add_group_btn)
        controls_layout.addWidget(edit_btn)
        controls_layout.addWidget(remove_btn)
        controls_layout.addWidget(up_btn)
        controls_layout.addWidget(down_btn)
        controls_layout.addWidget(refresh_btn)
        layout.addLayout(controls_layout)
        
        self.load_context_entries()
        return widget

    def create_backup_tab(self):
        """Create backup and restore tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        info = QLabel("💾 BACKUP & RESTORE CONFIGURATION")
        info.setStyleSheet(f"font-size: 14pt; color: {CP_YELLOW}; padding: 10px;")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)
        
        desc = QLabel("Export all command aliases and context menu entries to a JSON file.")
        desc.setStyleSheet(f"color: {CP_SUBTEXT}; padding: 10px;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        
        btn_layout = QHBoxLayout()
        backup_btn = QPushButton("📤 EXPORT TO data.json")
        import_btn = QPushButton("📥 IMPORT FROM data.json")
        
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

    def add_context_group(self):
        parent_path = ""
        row = self.context_table.currentRow()
        if row >= 0 and self.context_table.item(row, 1).text() == "GROUP":
            parent_path = self.context_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        name, ok = QInputDialog.getText(self, "Add Group", "Group Label:")
        if ok and name:
            path = rf"{parent_path}\shell\{name}" if parent_path else rf"Software\Classes\Directory\Background\shell\{name}"
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, path)
            winreg.SetValueEx(key, "MUIVerb", 0, winreg.REG_SZ, name)
            winreg.SetValueEx(key, "SubCommands", 0, winreg.REG_SZ, "")
            winreg.CreateKey(key, "shell")
            winreg.CloseKey(key)
            self.load_context_entries()

    def add_context_entry(self):
        row = self.context_table.currentRow()
        parent_path = ""
        if row >= 0 and self.context_table.item(row, 1).text() == "GROUP":
            parent_path = self.context_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        dialog = QDialog(self); dialog.setWindowTitle("Add Context Entry")
        layout = QVBoxLayout(dialog); form = QFormLayout()
        label_edit = QLineEdit(); cmd_edit = QTextEdit(); icon_edit = QLineEdit()
        form.addRow("Label:", label_edit); form.addRow("Command:", cmd_edit); form.addRow("Icon Path:", icon_edit)
        layout.addLayout(form)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(dialog.accept); btns.rejected.connect(dialog.reject); layout.addWidget(btns)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, cmd, icon = label_edit.text(), cmd_edit.toPlainText(), icon_edit.text()
            if name and cmd:
                path_base = f"{parent_path}\\shell\\{name}" if parent_path else f"Software\\Classes\\*\\shell\\{name}"
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, path_base)
                winreg.SetValueEx(key, "MUIVerb", 0, winreg.REG_SZ, name)
                if icon: winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icon)
                ckey = winreg.CreateKey(key, "command")
                winreg.SetValue(ckey, "", winreg.REG_SZ, cmd)
                winreg.CloseKey(ckey); winreg.CloseKey(key)
                self.load_context_entries()

    def edit_context_entry(self):
        row = self.context_table.currentRow()
        if row < 0: return
        path = self.context_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        type_text = self.context_table.item(row, 1).text()
        
        label = self.context_table.item(row, 0).text().replace("  ↳ ", "")
        cmd = self.context_table.item(row, 2).text()
        
        new_label, ok = QInputDialog.getText(self, "Edit Label", "Label:", text=label)
        if ok and new_label:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, "MUIVerb", 0, winreg.REG_SZ, new_label)
            if type_text == "ENTRY":
                new_cmd, ok2 = QInputDialog.getText(self, "Edit Command", "Command:", text=cmd)
                if ok2:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, f"{path}\\command", 0, winreg.KEY_SET_VALUE) as ckey:
                        winreg.SetValue(ckey, "", winreg.REG_SZ, new_cmd)
            self.load_context_entries()

    def remove_context_entry(self):
        row = self.context_table.currentRow()
        if row >= 0:
            path = self.context_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            if QMessageBox.question(self, "Confirm", "Delete this entry?") == QMessageBox.StandardButton.Yes:
                self._delete_reg_key(winreg.HKEY_CURRENT_USER, path)
                self.load_context_entries()

    def move_context_up(self):
        self._swap_logic(-1)

    def move_context_down(self):
        self._swap_logic(1)

    def _swap_logic(self, offset):
        row = self.context_table.currentRow()
        target = row + offset
        if target < 0 or target >= self.context_table.rowCount(): return
        
        p1 = self.context_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        p2 = self.context_table.item(target, 0).data(Qt.ItemDataRole.UserRole)
        if not p1 or not p2: return

        try:
            self._swap_registry_keys(p1, p2)
            self.load_context_entries()
            self.context_table.selectRow(target)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _swap_registry_keys(self, p1, p2):
        n1, n2 = p1.split('\\')[-1], p2.split('\\')[-1]
        parent = "\\".join(p1.split('\\')[:-1])
        temp = f"{parent}\\_TEMP_{datetime.now().microsecond}"
        self._copy_reg_key(winreg.HKEY_CURRENT_USER, p1, temp)
        self._delete_reg_key(winreg.HKEY_CURRENT_USER, p1)
        self._copy_reg_key(winreg.HKEY_CURRENT_USER, p2, p1)
        self._delete_reg_key(winreg.HKEY_CURRENT_USER, p2)
        self._copy_reg_key(winreg.HKEY_CURRENT_USER, temp, p2)
        self._delete_reg_key(winreg.HKEY_CURRENT_USER, temp)

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
        try:
            key = winreg.OpenKey(hkey, path, 0, winreg.KEY_ALL_ACCESS)
            while True:
                try: self._delete_reg_key(key, winreg.EnumKey(key, 0))
                except OSError: break
            winreg.CloseKey(key)
            winreg.DeleteKey(hkey, path)
        except: pass

    # ===== BACKUP / RESTORE METHODS =====
    def get_context_menu_data(self):
        data = {}
        bases = [("Directory\\Background\\shell", "Background"), ("Directory\\shell", "Folder"), ("*\\shell", "AllFiles")]
        for bp, s in bases:
            res = self._export_shell_keys(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\{bp}")
            if res: data[s] = res
        return data

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
                        for val in ["MUIVerb", "Icon", "SubCommands", "CommandFlags"]:
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

    def export_config(self):
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
