import sys
import os
import winreg
import json
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
        self.resize(1200, 700)
        
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
            # PS profiles
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
            
            # CMD
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Command Processor", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "AutoRun", 0, winreg.REG_SZ, os.path.join(self.alias_dir, "aliases.cmd"))
            winreg.CloseKey(key)

            # Bash
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
                path_base = f"{parent_path}\\shell\\{name}" if parent_path else f"Software\Classes\*\shell\\{name}"
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

    def _delete_reg_key(self, hkey, path):
        try:
            key = winreg.OpenKey(hkey, path, 0, winreg.KEY_ALL_ACCESS)
            while True:
                try: self._delete_reg_key(key, winreg.EnumKey(key, 0))
                except OSError: break
            winreg.CloseKey(key)
            winreg.DeleteKey(hkey, path)
        except: pass

    def move_context_up(self): self._swap_sibling( -1)
    def move_context_down(self): self._swap_sibling( 1)

    def _swap_sibling(self, direction):
        row = self.context_table.currentRow()
        target = row + direction
        if target < 0 or target >= self.context_table.rowCount(): return
        
        p1 = self.context_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        p2 = self.context_table.item(target, 0).data(Qt.ItemDataRole.UserRole)
        if not p1 or not p2: return

        # Swap by renaming logic... simplified here as a message
        self.set_status("Moving keys requires recursive rename - Not implemented in this view", CP_ORANGE)

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
