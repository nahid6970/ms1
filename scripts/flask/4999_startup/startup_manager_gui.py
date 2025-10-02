import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os
import winreg
import subprocess
import threading
from datetime import datetime

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class StartupManagerGUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Startup Manager")
        self.root.geometry("1200x800")
        
        # Initialize startup manager
        self.json_file = os.path.join(os.path.dirname(__file__), "startup_items.json")
        
        # Create main interface
        self.create_widgets()
        self.load_items()
        
    def create_widgets(self):
        # Main container
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            self.main_frame, 
            text="Startup Manager", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        
        # Control buttons frame
        controls_frame = ctk.CTkFrame(self.main_frame)
        controls_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Control buttons
        ctk.CTkButton(
            controls_frame, 
            text="Add Item", 
            command=self.open_add_dialog,
            width=100
        ).pack(side="left", padx=5, pady=10)
        
        ctk.CTkButton(
            controls_frame, 
            text="Refresh", 
            command=self.load_items,
            width=100
        ).pack(side="left", padx=5, pady=10)
        
        ctk.CTkButton(
            controls_frame, 
            text="Scan Folders", 
            command=self.scan_startup_folders,
            width=100
        ).pack(side="left", padx=5, pady=10)
        
        # Search frame
        search_frame = ctk.CTkFrame(controls_frame)
        search_frame.pack(side="right", padx=5, pady=10)
        
        ctk.CTkLabel(search_frame, text="Search:").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_items)
        search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var, width=200)
        search_entry.pack(side="left", padx=5)
        
        # Create notebook for tabs
        self.notebook = ctk.CTkTabview(self.main_frame)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Create tabs (we'll update titles in load_items)
        self.commands_tab = self.notebook.add("Commands")
        self.apps_tab = self.notebook.add("Applications")
        
        # Create scrollable frames for each tab
        self.commands_frame = ctk.CTkScrollableFrame(self.commands_tab)
        self.commands_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.apps_frame = ctk.CTkScrollableFrame(self.apps_tab)
        self.apps_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
    def load_items_from_json(self):
        """Load items from JSON file"""
        try:
            if os.path.exists(self.json_file):
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return []
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load items: {e}")
            return []
    
    def save_items_to_json(self, items):
        """Save items to JSON file"""
        try:
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(items, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save items: {e}")
            return False
    
    def filter_existing_items(self, items):
        """Filter out items with no valid paths"""
        filtered_items = []
        for item in items:
            for path in item["paths"]:
                if os.path.exists(path):
                    filtered_items.append({
                        "type": item["type"],
                        "name": item["name"],
                        "paths": [path],
                        "Command": item.get("Command", ""),
                        "ExecutableType": item.get("ExecutableType", "other"),
                    })
                    break
        return filtered_items
    
    def is_startup_enabled(self, item):
        """Check if item is in Windows startup registry"""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ) as reg_key:
                try:
                    winreg.QueryValueEx(reg_key, item["name"])
                    return True
                except FileNotFoundError:
                    return False
        except WindowsError:
            return False
    
    def toggle_startup(self, item):
        """Toggle startup status of an item"""
        reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            if self.is_startup_enabled(item):
                # Remove from startup
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_ALL_ACCESS) as reg_key:
                    winreg.DeleteValue(reg_key, item["name"])
                return {"success": True, "action": "disabled"}
            else:
                # Add to startup
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_ALL_ACCESS) as reg_key:
                    path = item["paths"][0]
                    command = item.get("Command", "")
                    executable_type = item.get("ExecutableType", "other")

                    # Build command based on executable type
                    if executable_type == "pythonw":
                        full_command = f'"{path}" {command}'
                    elif executable_type == "pwsh":
                        full_command = f'"{path}" -Command {command}'
                    elif executable_type == "cmd":
                        full_command = f'"{path}" /c {command}'
                    elif executable_type == "powershell":
                        full_command = f'"{path}" -Command {command}'
                    elif executable_type == "ahk_v2":
                        full_command = f'"C:\\Program Files\\AutoHotkey\\v2\\AutoHotkey.exe" "{path}" {command}'
                    else:
                        if command:
                            full_command = f'"{path}" {command}'
                        else:
                            full_command = f'"{path}"'
                    
                    winreg.SetValueEx(reg_key, item["name"], 0, winreg.REG_SZ, full_command)
                return {"success": True, "action": "enabled"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def launch_item(self, item):
        """Launch an item"""
        try:
            path = item["paths"][0]
            command = item.get("Command", "")
            executable_type = item.get("ExecutableType", "other")
            
            if executable_type == "pythonw":
                full_command = f'"{path}" {command}'
            elif executable_type == "pwsh":
                full_command = f'"{path}" -Command {command}'
            elif executable_type == "cmd":
                full_command = f'"{path}" /c {command}'
            elif executable_type == "powershell":
                full_command = f'"{path}" -Command {command}'
            elif executable_type == "ahk_v2":
                full_command = f'"C:\\Program Files\\AutoHotkey\\v2\\AutoHotkey.exe" "{path}" {command}'
            else:
                if command:
                    full_command = f'"{path}" {command}'
                else:
                    full_command = f'"{path}"'
            
            os.system(f'start "" {full_command}')
            messagebox.showinfo("Success", f"{item['name']} launched successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch {item['name']}: {e}")
    
    def create_item_widget(self, parent, item):
        """Create a widget for a single startup item"""
        # Main item frame
        item_frame = ctk.CTkFrame(parent)
        item_frame.pack(fill="x", padx=5, pady=5)
        
        # Top row with name and controls
        top_frame = ctk.CTkFrame(item_frame)
        top_frame.pack(fill="x", padx=10, pady=5)
        
        # Item name and status
        name_frame = ctk.CTkFrame(top_frame)
        name_frame.pack(side="left", fill="x", expand=True)
        
        # Status indicator and name
        status_frame = ctk.CTkFrame(name_frame)
        status_frame.pack(side="left", padx=5, pady=5)
        
        is_enabled = self.is_startup_enabled(item)
        status_color = "green" if is_enabled else "red"
        status_text = "●" if is_enabled else "○"
        
        status_label = ctk.CTkLabel(
            status_frame, 
            text=status_text, 
            text_color=status_color,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        status_label.pack(side="left", padx=5)
        
        name_label = ctk.CTkLabel(
            status_frame, 
            text=item["name"], 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        name_label.pack(side="left", padx=5)
        
        # Control buttons
        buttons_frame = ctk.CTkFrame(top_frame)
        buttons_frame.pack(side="right", padx=5)
        
        # Toggle button
        toggle_btn = ctk.CTkButton(
            buttons_frame,
            text="Disable" if is_enabled else "Enable",
            command=lambda: self.toggle_item_startup(item, item_frame),
            width=80,
            fg_color="red" if is_enabled else "green"
        )
        toggle_btn.pack(side="left", padx=2, pady=5)
        
        # Launch button
        launch_btn = ctk.CTkButton(
            buttons_frame,
            text="Launch",
            command=lambda: self.launch_item(item),
            width=80
        )
        launch_btn.pack(side="left", padx=2, pady=5)
        
        # Edit button
        edit_btn = ctk.CTkButton(
            buttons_frame,
            text="Edit",
            command=lambda: self.open_edit_dialog(item),
            width=60
        )
        edit_btn.pack(side="left", padx=2, pady=5)
        
        # Delete button
        delete_btn = ctk.CTkButton(
            buttons_frame,
            text="Delete",
            command=lambda: self.delete_item(item),
            width=60,
            fg_color="red"
        )
        delete_btn.pack(side="left", padx=2, pady=5)
        
        # Details frame (collapsible)
        details_frame = ctk.CTkFrame(item_frame)
        details_frame.pack(fill="x", padx=10, pady=(0, 5))
        
        # Path
        path_label = ctk.CTkLabel(
            details_frame, 
            text=f"Path: {item['paths'][0]}", 
            font=ctk.CTkFont(size=10),
            anchor="w"
        )
        path_label.pack(fill="x", padx=5, pady=2)
        
        # Command/Args
        if item.get("Command"):
            cmd_label = ctk.CTkLabel(
                details_frame, 
                text=f"Args: {item['Command']}", 
                font=ctk.CTkFont(size=10),
                anchor="w"
            )
            cmd_label.pack(fill="x", padx=5, pady=2)
        
        # Executable type
        type_label = ctk.CTkLabel(
            details_frame, 
            text=f"Type: {item.get('ExecutableType', 'other')}", 
            font=ctk.CTkFont(size=10),
            anchor="w"
        )
        type_label.pack(fill="x", padx=5, pady=2)
        
        return item_frame
    
    def toggle_item_startup(self, item, item_frame):
        """Toggle startup status and refresh the item widget"""
        result = self.toggle_startup(item)
        if result["success"]:
            messagebox.showinfo("Success", f"{item['name']} {result['action']}")
            # Refresh the display
            self.load_items()
        else:
            messagebox.showerror("Error", f"Failed to toggle {item['name']}: {result.get('error', 'Unknown error')}")
    
    def delete_item(self, item):
        """Delete an item"""
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{item['name']}'?"):
            items = self.load_items_from_json()
            
            # Remove from startup if enabled
            if self.is_startup_enabled(item):
                self.toggle_startup(item)
            
            # Remove from items list
            items = [stored_item for stored_item in items if stored_item["name"] != item["name"]]
            
            if self.save_items_to_json(items):
                messagebox.showinfo("Success", f"{item['name']} deleted successfully")
                self.load_items()
            else:
                messagebox.showerror("Error", f"Failed to delete {item['name']}")
    
    def load_items(self):
        """Load and display all items"""
        # Load items from JSON
        items = self.filter_existing_items(self.load_items_from_json())
        
        # Separate commands and apps
        commands = [item for item in items if item["type"] == "Command"]
        apps = [item for item in items if item["type"] == "App"]
        
        # Sort items by name
        commands.sort(key=lambda x: x["name"].lower())
        apps.sort(key=lambda x: x["name"].lower())
        
        # Calculate counts for tab titles
        enabled_commands = sum(1 for item in commands if self.is_startup_enabled(item))
        enabled_apps = sum(1 for item in apps if self.is_startup_enabled(item))
        
        # Store current tab
        try:
            current_tab = self.notebook.get()
        except:
            current_tab = "Commands"
        
        # Destroy and recreate notebook with updated titles
        self.notebook.destroy()
        self.notebook = ctk.CTkTabview(self.main_frame)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Recreate tabs with updated titles
        self.commands_tab = self.notebook.add(f"Commands ({enabled_commands}/{len(commands)})")
        self.apps_tab = self.notebook.add(f"Applications ({enabled_apps}/{len(apps)})")
        
        # Recreate scrollable frames
        self.commands_frame = ctk.CTkScrollableFrame(self.commands_tab)
        self.commands_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.apps_frame = ctk.CTkScrollableFrame(self.apps_tab)
        self.apps_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create widgets for commands
        if commands:
            for item in commands:
                self.create_item_widget(self.commands_frame, item)
        else:
            no_commands_label = ctk.CTkLabel(
                self.commands_frame, 
                text="No commands configured", 
                font=ctk.CTkFont(size=14)
            )
            no_commands_label.pack(pady=20)
        
        # Create widgets for apps
        if apps:
            for item in apps:
                self.create_item_widget(self.apps_frame, item)
        else:
            no_apps_label = ctk.CTkLabel(
                self.apps_frame, 
                text="No applications configured", 
                font=ctk.CTkFont(size=14)
            )
            no_apps_label.pack(pady=20)
        
        # Try to restore the previous tab selection
        try:
            if "Commands" in current_tab:
                self.notebook.set(f"Commands ({enabled_commands}/{len(commands)})")
            elif "Applications" in current_tab:
                self.notebook.set(f"Applications ({enabled_apps}/{len(apps)})")
        except:
            pass  # If restoration fails, just use default
    
    def filter_items(self, *args):
        """Filter items based on search text"""
        search_text = self.search_var.get().lower()
        
        # If no search text, show all items
        if not search_text:
            self.load_items()
            return
        
        # Clear existing items
        for widget in self.commands_frame.winfo_children():
            widget.destroy()
        for widget in self.apps_frame.winfo_children():
            widget.destroy()
        
        # Load and filter items
        items = self.filter_existing_items(self.load_items_from_json())
        
        filtered_items = []
        for item in items:
            if (search_text in item["name"].lower() or 
                search_text in item["paths"][0].lower() or 
                search_text in item.get("Command", "").lower()):
                filtered_items.append(item)
        
        # Separate filtered commands and apps
        commands = [item for item in filtered_items if item["type"] == "Command"]
        apps = [item for item in filtered_items if item["type"] == "App"]
        
        # Create widgets for filtered items
        for item in commands:
            self.create_item_widget(self.commands_frame, item)
        for item in apps:
            self.create_item_widget(self.apps_frame, item)
        
        # Show "no results" if nothing found
        if not commands:
            no_results_label = ctk.CTkLabel(
                self.commands_frame, 
                text=f"No commands match '{search_text}'", 
                font=ctk.CTkFont(size=14)
            )
            no_results_label.pack(pady=20)
        
        if not apps:
            no_results_label = ctk.CTkLabel(
                self.apps_frame, 
                text=f"No applications match '{search_text}'", 
                font=ctk.CTkFont(size=14)
            )
            no_results_label.pack(pady=20)
    
    def open_add_dialog(self):
        """Open dialog to add new item"""
        AddEditDialog(self, "Add New Item")
    
    def open_edit_dialog(self, item):
        """Open dialog to edit existing item"""
        AddEditDialog(self, "Edit Item", item)
    
    def scan_startup_folders(self):
        """Scan Windows startup folders for items"""
        def scan_thread():
            startup_folders = [
                r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup",
                os.path.expanduser(r"~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup")
            ]
            
            found_items = []
            existing_items = self.load_items_from_json()
            existing_names = {item["name"].lower() for item in existing_items}
            
            for folder in startup_folders:
                try:
                    if os.path.exists(folder):
                        for filename in os.listdir(folder):
                            file_path = os.path.join(folder, filename)
                            
                            if os.path.isfile(file_path):
                                name, ext = os.path.splitext(filename)
                                
                                if ext.lower() in ['.exe', '.bat', '.cmd', '.lnk', '.url']:
                                    if name.lower() not in existing_names:
                                        item_type = "App" if ext.lower() == '.exe' else "Command"
                                        found_items.append({
                                            "name": name,
                                            "type": item_type,
                                            "path": file_path,
                                            "command": "",
                                            "executable_type": "other"
                                        })
                except Exception as e:
                    print(f"Error scanning folder {folder}: {e}")
            
            # Show results in main thread
            self.root.after(0, lambda: self.show_scan_results(found_items))
        
        # Run scan in background thread
        threading.Thread(target=scan_thread, daemon=True).start()
        messagebox.showinfo("Scanning", "Scanning startup folders...")
    
    def show_scan_results(self, found_items):
        """Show scan results dialog"""
        if not found_items:
            messagebox.showinfo("Scan Complete", "No new items found in startup folders")
            return
        
        ScanResultsDialog(self, found_items)
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()


class AddEditDialog:
    def __init__(self, parent, title, item=None):
        self.parent = parent
        self.item = item
        self.is_edit = item is not None
        
        # Create dialog window
        self.dialog = ctk.CTkToplevel(parent.root)
        self.dialog.title(title)
        self.dialog.geometry("500x400")
        self.dialog.transient(parent.root)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"500x400+{x}+{y}")
        
        self.create_widgets()
        
        if self.is_edit:
            self.populate_fields()
    
    def create_widgets(self):
        # Main frame
        main_frame = ctk.CTkFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Name field
        ctk.CTkLabel(main_frame, text="Name:").pack(anchor="w", padx=10, pady=(10, 5))
        self.name_entry = ctk.CTkEntry(main_frame, width=400)
        self.name_entry.pack(padx=10, pady=(0, 10))
        
        # Type field
        ctk.CTkLabel(main_frame, text="Type:").pack(anchor="w", padx=10, pady=(0, 5))
        self.type_var = tk.StringVar(value="App")
        type_frame = ctk.CTkFrame(main_frame)
        type_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkRadioButton(type_frame, text="Application", variable=self.type_var, value="App").pack(side="left", padx=10, pady=5)
        ctk.CTkRadioButton(type_frame, text="Command", variable=self.type_var, value="Command").pack(side="left", padx=10, pady=5)
        
        # Executable Type field
        ctk.CTkLabel(main_frame, text="Executable Type:").pack(anchor="w", padx=10, pady=(0, 5))
        self.exec_type_var = tk.StringVar(value="other")
        self.exec_type_combo = ctk.CTkComboBox(
            main_frame, 
            values=["other", "pythonw", "pwsh", "cmd", "powershell", "ahk_v2"],
            variable=self.exec_type_var,
            width=400
        )
        self.exec_type_combo.pack(padx=10, pady=(0, 10))
        
        # Path field
        path_frame = ctk.CTkFrame(main_frame)
        path_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(path_frame, text="Path:").pack(anchor="w", pady=(10, 5))
        path_entry_frame = ctk.CTkFrame(path_frame)
        path_entry_frame.pack(fill="x", pady=(0, 10))
        
        self.path_entry = ctk.CTkEntry(path_entry_frame, width=320)
        self.path_entry.pack(side="left", padx=(10, 5), pady=5)
        
        browse_btn = ctk.CTkButton(
            path_entry_frame, 
            text="Browse", 
            command=self.browse_file,
            width=60
        )
        browse_btn.pack(side="right", padx=(5, 10), pady=5)
        
        # Command/Arguments field
        ctk.CTkLabel(main_frame, text="Arguments/Command:").pack(anchor="w", padx=10, pady=(0, 5))
        self.command_entry = ctk.CTkEntry(main_frame, width=400)
        self.command_entry.pack(padx=10, pady=(0, 10))
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=10, pady=20)
        
        save_btn = ctk.CTkButton(
            button_frame, 
            text="Save", 
            command=self.save_item,
            width=100
        )
        save_btn.pack(side="left", padx=10)
        
        cancel_btn = ctk.CTkButton(
            button_frame, 
            text="Cancel", 
            command=self.dialog.destroy,
            width=100
        )
        cancel_btn.pack(side="right", padx=10)
    
    def populate_fields(self):
        """Populate fields when editing"""
        if self.item:
            self.name_entry.insert(0, self.item["name"])
            self.type_var.set(self.item["type"])
            self.exec_type_var.set(self.item.get("ExecutableType", "other"))
            self.path_entry.insert(0, self.item["paths"][0])
            self.command_entry.insert(0, self.item.get("Command", ""))
    
    def browse_file(self):
        """Open file browser"""
        filename = filedialog.askopenfilename(
            title="Select executable file",
            filetypes=[
                ("Executable files", "*.exe"),
                ("Python files", "*.py"),
                ("PowerShell files", "*.ps1"),
                ("Batch files", "*.bat;*.cmd"),
                ("AutoHotkey files", "*.ahk"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, filename)
    
    def save_item(self):
        """Save the item"""
        # Validate fields
        name = self.name_entry.get().strip()
        path = self.path_entry.get().strip()
        
        if not name or not path:
            messagebox.showerror("Error", "Name and Path are required")
            return
        
        if not os.path.exists(path):
            messagebox.showerror("Error", "The specified path does not exist")
            return
        
        # Load existing items
        items = self.parent.load_items_from_json()
        
        # Check for duplicate names (except when editing the same item)
        if not self.is_edit or name != self.item["name"]:
            if any(item["name"] == name for item in items):
                messagebox.showerror("Error", "An item with this name already exists")
                return
        
        # Create new item data
        new_item = {
            "name": name,
            "type": self.type_var.get(),
            "paths": [path],
            "Command": self.command_entry.get().strip(),
            "ExecutableType": self.exec_type_var.get()
        }
        
        if self.is_edit:
            # Update existing item
            for i, stored_item in enumerate(items):
                if stored_item["name"] == self.item["name"]:
                    items[i] = new_item
                    break
        else:
            # Add new item
            items.append(new_item)
        
        # Save items
        if self.parent.save_items_to_json(items):
            action = "updated" if self.is_edit else "added"
            messagebox.showinfo("Success", f"Item {action} successfully!")
            self.dialog.destroy()
            self.parent.load_items()
        else:
            messagebox.showerror("Error", f"Failed to save item")


class ScanResultsDialog:
    def __init__(self, parent, found_items):
        self.parent = parent
        self.found_items = found_items
        
        # Create dialog window
        self.dialog = ctk.CTkToplevel(parent.root)
        self.dialog.title(f"Scan Results - {len(found_items)} items found")
        self.dialog.geometry("600x400")
        self.dialog.transient(parent.root)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"600x400+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame
        main_frame = ctk.CTkFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame, 
            text=f"Found {len(self.found_items)} new items in startup folders",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Scrollable frame for items
        self.items_frame = ctk.CTkScrollableFrame(main_frame)
        self.items_frame.pack(fill="both", expand=True, padx=10, pady=(0, 20))
        
        # Create checkboxes for each item
        self.item_vars = []
        for item in self.found_items:
            var = tk.BooleanVar(value=True)
            self.item_vars.append(var)
            
            item_frame = ctk.CTkFrame(self.items_frame)
            item_frame.pack(fill="x", padx=5, pady=2)
            
            checkbox = ctk.CTkCheckBox(
                item_frame,
                text=f"{item['name']} ({item['type']})",
                variable=var
            )
            checkbox.pack(side="left", padx=10, pady=5)
            
            path_label = ctk.CTkLabel(
                item_frame,
                text=item['path'],
                font=ctk.CTkFont(size=10),
                text_color="gray"
            )
            path_label.pack(side="left", padx=10, pady=5)
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        select_all_btn = ctk.CTkButton(
            button_frame,
            text="Select All",
            command=self.select_all,
            width=100
        )
        select_all_btn.pack(side="left", padx=5)
        
        select_none_btn = ctk.CTkButton(
            button_frame,
            text="Select None",
            command=self.select_none,
            width=100
        )
        select_none_btn.pack(side="left", padx=5)
        
        add_btn = ctk.CTkButton(
            button_frame,
            text="Add Selected",
            command=self.add_selected,
            width=100
        )
        add_btn.pack(side="right", padx=5)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.dialog.destroy,
            width=100
        )
        cancel_btn.pack(side="right", padx=5)
    
    def select_all(self):
        for var in self.item_vars:
            var.set(True)
    
    def select_none(self):
        for var in self.item_vars:
            var.set(False)
    
    def add_selected(self):
        # Get selected items
        selected_items = []
        for i, var in enumerate(self.item_vars):
            if var.get():
                item = self.found_items[i]
                selected_items.append({
                    "name": item["name"],
                    "type": item["type"],
                    "paths": [item["path"]],
                    "Command": item["command"],
                    "ExecutableType": item["executable_type"]
                })
        
        if not selected_items:
            messagebox.showwarning("Warning", "No items selected")
            return
        
        # Load existing items and add selected ones
        existing_items = self.parent.load_items_from_json()
        existing_items.extend(selected_items)
        
        # Save items
        if self.parent.save_items_to_json(existing_items):
            messagebox.showinfo("Success", f"Added {len(selected_items)} items successfully!")
            self.dialog.destroy()
            self.parent.load_items()
        else:
            messagebox.showerror("Error", "Failed to save items")


if __name__ == "__main__":
    app = StartupManagerGUI()
    app.run()