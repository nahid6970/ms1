import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, ttk
import os
import winreg
import json
import threading
import time

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
        self.item_widgets = {}  # Store references to item widgets for smooth updates
        self.is_refreshing = False  # Flag to prevent multiple simultaneous refreshes
        
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

    def copy_registry_paths(self):
        """Copy main registry path to clipboard"""
        try:
            # Main registry path for startup items
            registry_path = "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
            
            # Copy to clipboard
            self.clipboard_clear()
            self.clipboard_append(registry_path)
            self.update()  # Ensure clipboard is updated
            
            self.show_status("Registry path copied to clipboard", "#9ef959")
            
        except Exception as e:
            self.show_status(f"Failed to copy registry path: {e}", "#ff6b6b")

    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self, bg="#2e2f3e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Management buttons frame
        button_frame = tk.Frame(main_frame, bg="#2e2f3e")
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Button(button_frame, text="Add New Item", command=self.add_new_item, 
                 bg="#4a4b5a", fg="white", font=("Arial", 10), width=15).pack(side=tk.LEFT, padx=5)
        
        self.refresh_btn = tk.Button(button_frame, text="Refresh", command=self.smooth_refresh, 
                                    bg="#4a4b5a", fg="white", font=("Arial", 10), width=15)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Add Copy Registry Paths button
        copy_btn = tk.Button(button_frame, text="Copy Registry Path", command=self.copy_registry_paths, 
                           bg="#4a4b5a", fg="white", font=("Arial", 10), width=18)
        copy_btn.pack(side=tk.LEFT, padx=5)
        
        # Status label for feedback
        self.status_label = tk.Label(button_frame, text="Ready", bg="#2e2f3e", fg="#9ef959", 
                                    font=("Arial", 9))
        self.status_label.pack(side=tk.RIGHT, padx=5)
        
        # Items frame
        self.items_frame = tk.Frame(main_frame, bg="#2e2f3e")
        self.items_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_items_display()

    def show_status(self, message, color="#9ef959", duration=2000):
        """Show status message with optional color and duration"""
        self.status_label.config(text=message, fg=color)
        if duration > 0:
            self.after(duration, lambda: self.status_label.config(text="Ready", fg="#9ef959"))

    def smooth_refresh(self):
        """Perform smooth refresh with visual feedback"""
        if self.is_refreshing:
            return
        
        self.is_refreshing = True
        self.refresh_btn.config(state="disabled", text="Refreshing...")
        self.show_status("Refreshing items...", "#63dbff", 0)
        
        # Use threading to prevent UI freezing
        def refresh_thread():
            try:
                # Small delay to show feedback
                time.sleep(0.1)
                
                # Update items data
                new_items = self.filter_existing_items(self.load_items())
                
                # Schedule UI update on main thread
                self.after(0, lambda: self.complete_refresh(new_items))
                
            except Exception as e:
                self.after(0, lambda: self.handle_refresh_error(e))
        
        # Start refresh in background thread
        threading.Thread(target=refresh_thread, daemon=True).start()

    def complete_refresh(self, new_items):
        """Complete the refresh process on the main thread"""
        try:
            # Check if items have actually changed
            if self.items_have_changed(new_items):
                self.items = new_items
                self.fade_and_rebuild()
                self.show_status("Items refreshed successfully!", "#9ef959")
            else:
                # Just update the visual states without rebuilding
                self.update_item_states()
                self.show_status("Items are up to date", "#63dbff")
                
        except Exception as e:
            self.handle_refresh_error(e)
        finally:
            self.is_refreshing = False
            self.refresh_btn.config(state="normal", text="Refresh")

    def handle_refresh_error(self, error):
        """Handle refresh errors"""
        self.show_status(f"Refresh failed: {str(error)}", "#ff6b6b")
        self.is_refreshing = False
        self.refresh_btn.config(state="normal", text="Refresh")

    def items_have_changed(self, new_items):
        """Check if items have actually changed"""
        if len(self.items) != len(new_items):
            return True
        
        # Compare items by name and paths
        current_items_set = {(item["name"], tuple(item["paths"])) for item in self.items}
        new_items_set = {(item["name"], tuple(item["paths"])) for item in new_items}
        
        return current_items_set != new_items_set

    def fade_and_rebuild(self):
        """Fade out and rebuild the items display"""
        # Fade out effect
        self.animate_fade_out(self.items_frame, callback=self.rebuild_items_display)

    def animate_fade_out(self, widget, steps=5, callback=None):
        """Simple fade out animation by adjusting widget state"""
        def fade_step(step):
            if step > 0:
                # Gradually reduce opacity by disabling widgets
                for child in widget.winfo_children():
                    if hasattr(child, 'configure'):
                        try:
                            child.configure(state='disabled')
                        except:
                            pass
                self.after(30, lambda: fade_step(step - 1))
            else:
                if callback:
                    callback()

        fade_step(steps)

    def rebuild_items_display(self):
        """Rebuild the items display with fade in effect"""
        self.create_items_display()
        self.animate_fade_in(self.items_frame)

    def animate_fade_in(self, widget, steps=5):
        """Simple fade in animation by re-enabling widgets"""
        def fade_step(step):
            if step < steps:
                # Gradually restore widgets
                for child in widget.winfo_children():
                    if hasattr(child, 'configure'):
                        try:
                            child.configure(state='normal')
                        except:
                            pass
                self.after(30, lambda: fade_step(step + 1))

        fade_step(0)

    def update_item_states(self):
        """Update only the visual states of existing items without rebuilding"""
        for item_name, widgets in self.item_widgets.items():
            # Find the current item data
            current_item = next((item for item in self.items if item["name"] == item_name), None)
            if current_item:
                icon_label = widgets.get('icon')
                name_label = widgets.get('name')
                
                if icon_label and name_label:
                    checked = self.is_checked(current_item)
                    
                    # Update icon
                    icon_label.config(text="\uf205" if checked else "\uf204",
                                    fg="#9ef959" if checked else "gray")
                    
                    # Update name color
                    self.update_label_color(name_label, checked)

    def create_items_display(self):
        # Clear existing widgets and widget references
        for widget in self.items_frame.winfo_children():
            widget.destroy()
        self.item_widgets.clear()
        
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
        icon_label.bind("<Button-1>", lambda event, item=item: self.toggle_startup_smooth(item))
        icon_label.pack(side=tk.LEFT, padx=0)

        name_label = tk.Label(left_frame, text=item["name"], font=("Jetbrainsmono nfp", 10), bg="#2e2f3e")
        name_label.bind("<Button-1>", lambda event, item=item: self.launch_command(item))
        name_label.pack(side=tk.LEFT, padx=(5, 0))
        
        self.update_label_color(name_label, checked)
        
        # Store widget references for smooth updates
        self.item_widgets[item["name"]] = {
            'icon': icon_label,
            'name': name_label,
            'frame': frame
        }
        
        # Right side - edit and delete buttons
        right_frame = tk.Frame(frame, bg="#2e2f3e")
        right_frame.pack(side=tk.RIGHT)
        
        edit_btn = tk.Button(right_frame, text="Edit", command=lambda: self.edit_item(item),
                            bg="#4a4b5a", fg="white", font=("Arial", 8), width=6)
        edit_btn.pack(side=tk.LEFT, padx=2)
        
        delete_btn = tk.Button(right_frame, text="Delete", command=lambda: self.delete_item(item),
                              bg="#d32f2f", fg="white", font=("Arial", 8), width=6)
        delete_btn.pack(side=tk.LEFT, padx=2)

    def toggle_startup_smooth(self, item):
        """Toggle startup with smooth visual feedback"""
        # Show immediate feedback
        widgets = self.item_widgets.get(item["name"], {})
        icon_label = widgets.get('icon')
        name_label = widgets.get('name')
        
        if icon_label:
            # Show loading state
            icon_label.config(text="⟳", fg="#63dbff")
            self.show_status(f"Updating {item['name']}...", "#63dbff", 0)
        
        # Perform the toggle operation
        def toggle_operation():
            try:
                self.toggle_startup(item)
                # Update UI on main thread
                self.after(0, lambda: self.complete_toggle_update(item, True))
            except Exception as e:
                self.after(0, lambda: self.complete_toggle_update(item, False, str(e)))
        
        # Run in background thread
        threading.Thread(target=toggle_operation, daemon=True).start()

    def complete_toggle_update(self, item, success, error_msg=None):
        """Complete the toggle update on the main thread"""
        widgets = self.item_widgets.get(item["name"], {})
        icon_label = widgets.get('icon')
        name_label = widgets.get('name')
        
        if success:
            # Update the visual state
            checked = self.is_checked(item)
            
            if icon_label:
                icon_label.config(text="\uf205" if checked else "\uf204",
                                fg="#9ef959" if checked else "gray")
            
            if name_label:
                self.update_label_color(name_label, checked)
            
            status_msg = f"{item['name']} {'enabled' if checked else 'disabled'}"
            self.show_status(status_msg, "#9ef959")
        else:
            # Restore original state and show error
            if icon_label:
                checked = self.is_checked(item)
                icon_label.config(text="\uf205" if checked else "\uf204",
                                fg="#9ef959" if checked else "gray")
            
            self.show_status(f"Failed to update {item['name']}: {error_msg}", "#ff6b6b")

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
            
            # Smooth refresh
            self.smooth_refresh()
            self.show_status("Item added successfully!", "#9ef959")

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
            self.smooth_refresh()
            self.show_status("Item updated successfully!", "#9ef959")

    def delete_item(self, item):
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{item['name']}'?"):
            # Remove from registry if it exists
            if self.is_checked(item):
                self.remove_from_startup(item)
            
            # Remove from JSON file
            all_items = self.load_items()
            all_items = [stored_item for stored_item in all_items if stored_item["name"] != item["name"]]
            self.save_items(all_items)
            
            self.smooth_refresh()
            self.show_status("Item deleted successfully!", "#9ef959")

    def refresh_items(self):
        """Legacy refresh method - now calls smooth_refresh"""
        self.smooth_refresh()

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
            self.show_status(f"Launched {item['name']}", "#9ef959")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch {item['name']}: {e}")
            self.show_status(f"Failed to launch {item['name']}", "#ff6b6b")

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