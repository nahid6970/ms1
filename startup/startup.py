import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, ttk
import os
import winreg
import json

def create_custom_border(parent):
    BORDER_FRAME = tk.Frame(parent, bg="#1d2027", bd=0, highlightthickness=1, highlightbackground="red")
    BORDER_FRAME.place(relwidth=1, relheight=1)
    return BORDER_FRAME

class ItemDialog(tk.Toplevel):
    def __init__(self, parent, item=None):
        super().__init__(parent)
        self.parent = parent
        self.item = item
        self.result = None
        
        self.title("Add New Item" if item is None else "Edit Item")
        self.geometry("500x300")
        self.configure(bg="#2e2f3e")
        self.resizable(False, False)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        
        if item:
            self.load_item_data()
        
        # Center the dialog
        self.center_window()
        
    def create_widgets(self):
        # Name
        tk.Label(self, text="Name:", bg="#2e2f3e", fg="white", font=("Arial", 10)).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.name_entry = tk.Entry(self, width=50, font=("Arial", 10))
        self.name_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # Type
        tk.Label(self, text="Type:", bg="#2e2f3e", fg="white", font=("Arial", 10)).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.type_var = tk.StringVar(value="App")
        type_combo = ttk.Combobox(self, textvariable=self.type_var, values=["App", "Command"], state="readonly", width=47)
        type_combo.grid(row=1, column=1, padx=10, pady=5)
        
        # Path
        tk.Label(self, text="Path:", bg="#2e2f3e", fg="white", font=("Arial", 10)).grid(row=2, column=0, sticky="w", padx=10, pady=5)
        path_frame = tk.Frame(self, bg="#2e2f3e")
        path_frame.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        
        self.path_entry = tk.Entry(path_frame, width=40, font=("Arial", 10))
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_btn = tk.Button(path_frame, text="Browse", command=self.browse_file, bg="#4a4b5a", fg="white", font=("Arial", 8))
        browse_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Executable Type
        tk.Label(self, text="Executable Type:", bg="#2e2f3e", fg="white", font=("Arial", 10)).grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.executable_type_var = tk.StringVar(value="other")
        executable_type_combo = ttk.Combobox(self, textvariable=self.executable_type_var, values=["pythonw", "pwsh", "cmd", "powershell", "other"], state="readonly", width=47)
        executable_type_combo.grid(row=3, column=1, padx=10, pady=5)
        executable_type_combo.bind("<<ComboboxSelected>>", self.on_executable_type_selected)

        # Command/Arguments
        tk.Label(self, text="Arguments:", bg="#2e2f3e", fg="white", font=("Arial", 10)).grid(row=4, column=0, sticky="w", padx=10, pady=5)
        self.command_entry = tk.Entry(self, width=50, font=("Arial", 10))
        self.command_entry.grid(row=4, column=1, padx=10, pady=5)
        
        # Buttons
        button_frame = tk.Frame(self, bg="#2e2f3e")
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        tk.Button(button_frame, text="Save", command=self.save_item, bg="#4a4b5a", fg="white", font=("Arial", 10), width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=self.cancel, bg="#4a4b5a", fg="white", font=("Arial", 10), width=10).pack(side=tk.LEFT, padx=5)
    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select executable file",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")])
        if filename:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, filename)
    
    def on_executable_type_selected(self, event):
        selected_type = self.executable_type_var.get()
        if selected_type == "pythonw":
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, r"C:\Users\nahid\scoop\apps\python312\current\pythonw.exe")
        elif selected_type == "pwsh":
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe")
        elif selected_type == "cmd":
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, r"C:\Windows\System32\cmd.exe")
        elif selected_type == "powershell":
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe")
        else:
            self.path_entry.delete(0, tk.END)
            # Clear the path if "other" is selected, or keep it as is if it's already a valid path
            if not os.path.exists(self.path_entry.get()):
                self.path_entry.insert(0, "")

    def load_item_data(self):
        self.name_entry.insert(0, self.item["name"])
        self.type_var.set(self.item["type"])
        self.path_entry.insert(0, self.item["paths"][0])
        self.command_entry.insert(0, self.item.get("Command", ""))
        self.executable_type_var.set(self.item.get("ExecutableType", "other"))
    
    def save_item(self):
        name = self.name_entry.get().strip()
        item_type = self.type_var.get()
        path = self.path_entry.get().strip()
        command = self.command_entry.get().strip()
        executable_type = self.executable_type_var.get()
        
        if not name or not path:
            messagebox.showerror("Error", "Name and Path are required!")
            return
        
        if not os.path.exists(path):
            messagebox.showerror("Error", "The specified path does not exist!")
            return
        
        self.result = {
            "name": name,
            "type": item_type,
            "paths": [path],
            "Command": command,
            "ExecutableType": executable_type
        }
        
        self.destroy()
    
    def cancel(self):
        self.destroy()
    
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

class StartupManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()  # Hide the window initially
        self.title("Startup Manager - PowerShell")
        self.configure(bg="#2e2f3e")
        
        self.json_file = os.path.join(os.path.dirname(__file__), "startup_items.json")
        self.items = self.filter_existing_items(self.load_items())  # Load and filter items
        
        self.create_widgets()
        self.center_window()
        self.attributes('-topmost', True)  # Set always on top
        self.deiconify()  # Show the window after fully initializing

    def load_items(self):
        """Load items from JSON file"""
        try:
            if os.path.exists(self.json_file):
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Create default JSON file if it doesn't exist
                default_items = []
                self.save_items(default_items)
                return default_items
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load items: {e}")
            return []

    def save_items(self, items=None):
        """Save items to JSON file"""
        if items is None:
            items = self.items
        
        try:
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(items, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save items: {e}")

    def filter_existing_items(self, items):
        """Filter out items with no valid paths."""
        filtered_items = []
        for item in items:
            for path in item["paths"]:
                if os.path.exists(path):
                    filtered_items.append({
                        "type": item["type"],
                        "name": item["name"],
                        "paths": [path],  # Use a list for compatibility
                        "Command": item.get("Command", ""),  # Include the Command field
                        "ExecutableType": item.get("ExecutableType", "other"), # Include the ExecutableType field
                    })
                    break  # Stop after the first valid path
        return filtered_items

    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self, bg="#2e2f3e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Management buttons frame
        button_frame = tk.Frame(main_frame, bg="#2e2f3e")
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Button(button_frame, text="Add New Item", command=self.add_new_item, 
                 bg="#4a4b5a", fg="white", font=("Arial", 10), width=15).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Refresh", command=self.refresh_items, 
                 bg="#4a4b5a", fg="white", font=("Arial", 10), width=15).pack(side=tk.LEFT, padx=5)
        
        # Items frame
        self.items_frame = tk.Frame(main_frame, bg="#2e2f3e")
        self.items_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_items_display()

    def create_items_display(self):
        # Clear existing widgets
        for widget in self.items_frame.winfo_children():
            widget.destroy()
        
        self.items_frame.grid_columnconfigure(0, weight=1)
        self.items_frame.grid_columnconfigure(2, weight=1)
        
        # Separate commands and apps
        commands = sorted([item for item in self.items if item["type"] == "Command"], key=lambda x: x["name"].lower())
        apps = sorted([item for item in self.items if item["type"] == "App"], key=lambda x: x["name"].lower())
        
        # Commands Section
        self.create_section("Commands", commands, column=0)
        
        # Vertical Separator
        separator = tk.Frame(self.items_frame, width=2, bg="#4a4b5a")
        separator.grid(row=1, column=1, rowspan=max(len(commands), len(apps)) + 1, sticky="ns")
        
        # Apps Section
        self.create_section("Apps", apps, column=2)

    def create_section(self, section_name, items, column):
        separator = tk.Label(self.items_frame, text=section_name, font=("Helvetica", 10, "bold"), 
                           bg="#3a3c49", fg="#ffffff")
        separator.grid(row=0, column=column, pady=5, sticky="ew")

        row = 1
        for item in items:
            self.create_item_widget(item, row, column)
            row += 1

    def create_item_widget(self, item, row, col):
        frame = tk.Frame(self.items_frame, bg="#2e2f3e")
        frame.grid(row=row, column=col, padx=5, pady=2, sticky="ew")
        
        # Left side - checkbox and name
        left_frame = tk.Frame(frame, bg="#2e2f3e")
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        checked = self.is_checked(item)
        
        icon_label = tk.Label(left_frame, text="\uf205" if checked else "\uf204", 
                             font=("Jetbrainsmono nfp", 12, "bold"), 
                             fg="#9ef959" if checked else "gray", bg="#2e2f3e")
        icon_label.bind("<Button-1>", lambda event, item=item: self.toggle_startup_and_refresh(item))
        icon_label.pack(side=tk.LEFT, padx=0)

        name_label = tk.Label(left_frame, text=item["name"], font=("Jetbrainsmono nfp", 10), bg="#2e2f3e")
        name_label.bind("<Button-1>", lambda event, item=item: self.launch_command(item))
        name_label.pack(side=tk.LEFT, padx=(5, 0))
        
        self.update_label_color(name_label, checked)
        
        # Right side - edit and delete buttons
        right_frame = tk.Frame(frame, bg="#2e2f3e")
        right_frame.pack(side=tk.RIGHT)
        
        edit_btn = tk.Button(right_frame, text="Edit", command=lambda: self.edit_item(item),
                            bg="#4a4b5a", fg="white", font=("Arial", 8), width=6)
        edit_btn.pack(side=tk.LEFT, padx=2)
        
        delete_btn = tk.Button(right_frame, text="Delete", command=lambda: self.delete_item(item),
                              bg="#d32f2f", fg="white", font=("Arial", 8), width=6)
        delete_btn.pack(side=tk.LEFT, padx=2)

    def add_new_item(self):
        dialog = ItemDialog(self)
        self.wait_window(dialog)
        
        if dialog.result:
            # Check if item with same name already exists
            if any(item["name"] == dialog.result["name"] for item in self.items):
                messagebox.showerror("Error", "An item with this name already exists!")
                return
            
            # Add the new item
            all_items = self.load_items()
            all_items.append(dialog.result)
            self.save_items(all_items)
            
            # Refresh the display
            self.refresh_items()
            messagebox.showinfo("Success", "Item added successfully!")

    def edit_item(self, item):
        dialog = ItemDialog(self, item)
        self.wait_window(dialog)
        
        if dialog.result:
            # Update the item in the JSON file
            all_items = self.load_items()
            for i, stored_item in enumerate(all_items):
                if stored_item["name"] == item["name"]:
                    all_items[i] = dialog.result
                    break
            
            self.save_items(all_items)
            self.refresh_items()
            messagebox.showinfo("Success", "Item updated successfully!")

    def delete_item(self, item):
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{item['name']}'?"):
            # Remove from registry if it exists
            if self.is_checked(item):
                self.remove_from_startup(item)
            
            # Remove from JSON file
            all_items = self.load_items()
            all_items = [stored_item for stored_item in all_items if stored_item["name"] != item["name"]]
            self.save_items(all_items)
            
            self.refresh_items()
            messagebox.showinfo("Success", "Item deleted successfully!")

    def refresh_items(self):
        self.items = self.filter_existing_items(self.load_items())
        self.create_items_display()

    def toggle_startup_and_refresh(self, item):
        self.toggle_startup(item)
        # Refresh the display to update colors
        self.create_items_display()

    def launch_command(self, item):
        # Retrieve the first path, the command, and the executable type
        path = item["paths"][0]
        command = item.get("Command", "")
        executable_type = item.get("ExecutableType", "other")
        
        full_command = ""
        if executable_type == "pythonw":
            full_command = f'"{path}" {command}'
        elif executable_type == "pwsh":
            full_command = f'"{path}" -Command {command}'
        elif executable_type == "cmd":
            full_command = f'"{path}" /c {command}'
        elif executable_type == "powershell":
            full_command = f'"{path}" -Command {command}'
        else: # other
            if command:
                full_command = f'"{path}" {command}'
            else:
                full_command = f'"{path}"'
        try:
            # Execute the command using os.system
            os.system(f'start "" {full_command}')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch {item['name']}: {e}")

    def is_checked(self, item):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_READ) as reg_key:
                try:
                    winreg.QueryValueEx(reg_key, item["name"])
                    return True
                except FileNotFoundError:
                    return False
        except WindowsError:
            return False

    def remove_from_startup(self, item):
        reg_path = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_ALL_ACCESS) as reg_key:
                winreg.DeleteValue(reg_key, item["name"])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove {item['name']} from startup: {e}")

    def toggle_startup(self, item):
        reg_path = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        try:
            if self.is_checked(item):
                # Remove from startup
                self.remove_from_startup(item)
            else:
                # Add to startup
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_ALL_ACCESS) as reg_key:
                    path = item["paths"][0]  # Use the first path in the list
                    command = item.get("Command", "")  # Get the command or an empty string
                    executable_type = item.get("ExecutableType", "other")

                    # Combine the path and command based on executable type
                    if executable_type == "pythonw":
                        full_command = f'"{path}" {command}'
                    elif executable_type == "pwsh":
                        full_command = f'"{path}" -Command {command}'
                    elif executable_type == "cmd":
                        full_command = f'"{path}" /c {command}'
                    elif executable_type == "powershell":
                        full_command = f'"{path}" -Command {command}'
                    else: # other
                        if command:
                            full_command = f'"{path}" {command}'
                        else:
                            full_command = f'"{path}"'
                    
                    winreg.SetValueEx(reg_key, item["name"], 0, winreg.REG_SZ, full_command)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to modify {item['name']} in startup: {e}")

    def update_label_color(self, label, checked):
        if checked:
            label.config(fg="#63dbff")
        else:
            label.config(fg="red")

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

if __name__ == "__main__":
    app = StartupManager()
    app.mainloop()