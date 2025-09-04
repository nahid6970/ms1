import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, ttk
import os
import winreg
import json
import threading
import time

# Try to import customtkinter, fallback to regular tkinter if not available
try:
    import customtkinter as ctk
    CTK_AVAILABLE = True
    # Set appearance mode and color theme
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
except ImportError:
    CTK_AVAILABLE = False
    print("CustomTkinter not available, using standard tkinter")

def create_custom_border(parent):
    BORDER_FRAME = tk.Frame(parent, bg="#1d2027", bd=0, highlightthickness=1, highlightbackground="red")
    BORDER_FRAME.place(relwidth=1, relheight=1)
    return BORDER_FRAME

class ItemDialog:
    def __init__(self, parent, item=None):
        self.parent = parent
        self.item = item
        self.result = None
        
        if CTK_AVAILABLE:
            self.create_ctk_dialog()
        else:
            self.create_tk_dialog()
        
        if item:
            self.load_item_data()
        
        # Center the dialog
        self.center_window()
    
    def create_ctk_dialog(self):
        """Create modern dialog using CustomTkinter"""
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("Add New Item" if self.item is None else "Edit Item")
        self.dialog.geometry("500x450")
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Configure grid
        self.dialog.grid_columnconfigure(0, weight=1)
        
        # Main frame with compact padding
        main_frame = ctk.CTkFrame(self.dialog)
        main_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(main_frame, 
                                  text="Add New Item" if self.item is None else "Edit Item",
                                  font=ctk.CTkFont(size=16, weight="bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(15, 20))
        
        # Name field
        ctk.CTkLabel(main_frame, text="Name *", 
                    font=ctk.CTkFont(size=12, weight="bold")).grid(row=1, column=0, sticky="w", padx=15, pady=(5, 2))
        self.name_entry = ctk.CTkEntry(main_frame, placeholder_text="Enter item name", 
                                      font=ctk.CTkFont(size=11), height=28)
        self.name_entry.grid(row=2, column=0, columnspan=2, padx=15, pady=(0, 8), sticky="ew")
        
        # Type field
        ctk.CTkLabel(main_frame, text="Type", 
                    font=ctk.CTkFont(size=12, weight="bold")).grid(row=3, column=0, sticky="w", padx=15, pady=(5, 2))
        self.type_var = tk.StringVar(value="App")
        self.type_combo = ctk.CTkComboBox(main_frame, values=["App", "Command"], 
                                         variable=self.type_var, font=ctk.CTkFont(size=11), height=28)
        self.type_combo.grid(row=4, column=0, columnspan=2, padx=15, pady=(0, 8), sticky="ew")
        
        # Executable Type field
        ctk.CTkLabel(main_frame, text="Executable Type", 
                    font=ctk.CTkFont(size=12, weight="bold")).grid(row=5, column=0, sticky="w", padx=15, pady=(5, 2))
        self.executable_type_var = tk.StringVar(value="other")
        self.executable_type_combo = ctk.CTkComboBox(main_frame, 
                                                    values=["other", "pythonw", "pwsh", "cmd", "powershell", "ahk_v2"],
                                                    variable=self.executable_type_var, 
                                                    font=ctk.CTkFont(size=11), height=28,
                                                    command=self.on_executable_type_selected)
        self.executable_type_combo.grid(row=6, column=0, columnspan=2, padx=15, pady=(0, 8), sticky="ew")
        
        # Path field
        ctk.CTkLabel(main_frame, text="Path *", 
                    font=ctk.CTkFont(size=12, weight="bold")).grid(row=7, column=0, sticky="w", padx=15, pady=(5, 2))
        
        path_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        path_frame.grid(row=8, column=0, columnspan=2, padx=15, pady=(0, 8), sticky="ew")
        path_frame.grid_columnconfigure(0, weight=1)
        
        self.path_entry = ctk.CTkEntry(path_frame, placeholder_text="Enter executable path", 
                                      font=ctk.CTkFont(size=11), height=28)
        self.path_entry.grid(row=0, column=0, padx=(0, 8), sticky="ew")
        
        browse_btn = ctk.CTkButton(path_frame, text="Browse", command=self.browse_file,
                                  font=ctk.CTkFont(size=10), width=65, height=28)
        browse_btn.grid(row=0, column=1)
        
        # Arguments field
        ctk.CTkLabel(main_frame, text="Arguments", 
                    font=ctk.CTkFont(size=12, weight="bold")).grid(row=9, column=0, sticky="w", padx=15, pady=(5, 2))
        self.command_entry = ctk.CTkEntry(main_frame, placeholder_text="Command line arguments (optional)", 
                                         font=ctk.CTkFont(size=11), height=28)
        self.command_entry.grid(row=10, column=0, columnspan=2, padx=15, pady=(0, 15), sticky="ew")
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=11, column=0, columnspan=2, pady=(5, 15))
        
        save_btn = ctk.CTkButton(button_frame, text="Save", command=self.save_item,
                                font=ctk.CTkFont(size=12, weight="bold"), 
                                width=100, height=32)
        save_btn.pack(side=tk.LEFT, padx=8)
        
        cancel_btn = ctk.CTkButton(button_frame, text="Cancel", command=self.cancel,
                                  font=ctk.CTkFont(size=12), 
                                  width=100, height=32, fg_color="gray", hover_color="darkgray")
        cancel_btn.pack(side=tk.LEFT, padx=8)
    
    def create_tk_dialog(self):
        """Fallback to standard tkinter dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Add New Item" if self.item is None else "Edit Item")
        self.dialog.geometry("500x400")
        self.dialog.configure(bg="#2e2f3e")
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Name
        tk.Label(self.dialog, text="Name:", bg="#2e2f3e", fg="white", font=("Arial", 10)).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.name_entry = tk.Entry(self.dialog, width=50, font=("Arial", 10))
        self.name_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # Type
        tk.Label(self.dialog, text="Type:", bg="#2e2f3e", fg="white", font=("Arial", 10)).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.type_var = tk.StringVar(value="App")
        type_combo = ttk.Combobox(self.dialog, textvariable=self.type_var, values=["App", "Command"], state="readonly", width=47)
        type_combo.grid(row=1, column=1, padx=10, pady=5)
        
        # Path
        tk.Label(self.dialog, text="Path:", bg="#2e2f3e", fg="white", font=("Arial", 10)).grid(row=2, column=0, sticky="w", padx=10, pady=5)
        path_frame = tk.Frame(self.dialog, bg="#2e2f3e")
        path_frame.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        
        self.path_entry = tk.Entry(path_frame, width=40, font=("Arial", 10))
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_btn = tk.Button(path_frame, text="Browse", command=self.browse_file, bg="#4a4b5a", fg="white", font=("Arial", 8))
        browse_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Executable Type
        tk.Label(self.dialog, text="Executable Type:", bg="#2e2f3e", fg="white", font=("Arial", 10)).grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.executable_type_var = tk.StringVar(value="other")
        executable_type_combo = ttk.Combobox(self.dialog, textvariable=self.executable_type_var, values=["pythonw", "pwsh", "cmd", "powershell", "other"], state="readonly", width=47)
        executable_type_combo.grid(row=3, column=1, padx=10, pady=5)
        executable_type_combo.bind("<<ComboboxSelected>>", self.on_executable_type_selected)

        # Command/Arguments
        tk.Label(self.dialog, text="Arguments:", bg="#2e2f3e", fg="white", font=("Arial", 10)).grid(row=4, column=0, sticky="w", padx=10, pady=5)
        self.command_entry = tk.Entry(self.dialog, width=50, font=("Arial", 10))
        self.command_entry.grid(row=4, column=1, padx=10, pady=5)
        
        # Buttons
        button_frame = tk.Frame(self.dialog, bg="#2e2f3e")
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        tk.Button(button_frame, text="Save", command=self.save_item, bg="#4a4b5a", fg="white", font=("Arial", 10), width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=self.cancel, bg="#4a4b5a", fg="white", font=("Arial", 10), width=10).pack(side=tk.LEFT, padx=5)
    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select executable file",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")])
        if filename:
            if CTK_AVAILABLE:
                self.path_entry.delete(0, tk.END)
                self.path_entry.insert(0, filename)
            else:
                self.path_entry.delete(0, tk.END)
                self.path_entry.insert(0, filename)
    
    def on_executable_type_selected(self, choice=None):
        # Handle both CTK (choice parameter) and regular tkinter (event parameter)
        if choice is not None:
            selected_type = choice
        else:
            selected_type = self.executable_type_var.get()
            
        common_paths = {
            "pythonw": r"C:\Users\nahid\scoop\apps\python312\current\pythonw.exe",
            "pwsh": r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
            "cmd": r"C:\Windows\System32\cmd.exe",
            "powershell": r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
            "ahk_v2": r"C:\Program Files\AutoHotkey\v2\AutoHotkey.exe"
        }
        
        if selected_type in common_paths:
            if CTK_AVAILABLE:
                self.path_entry.delete(0, tk.END)
                self.path_entry.insert(0, common_paths[selected_type])
            else:
                self.path_entry.delete(0, tk.END)
                self.path_entry.insert(0, common_paths[selected_type])

    def load_item_data(self):
        if CTK_AVAILABLE:
            self.name_entry.insert(0, self.item["name"])
            self.type_var.set(self.item["type"])
            self.path_entry.insert(0, self.item["paths"][0])
            self.command_entry.insert(0, self.item.get("Command", ""))
            self.executable_type_var.set(self.item.get("ExecutableType", "other"))
        else:
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
    
    def destroy(self):
        self.dialog.destroy()
    
    def center_window(self):
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')

class StartupManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()  # Hide the window initially
        self.title("Startup Manager - PowerShell")
        self.configure(bg="#2e2f3e")
        self.geometry("1000x700")  # Set a larger default size for better scrolling
        self.minsize(800, 500)  # Set minimum window size
        self.resizable(True, True)  # Make window resizable
        
        self.json_file = os.path.join(os.path.dirname(__file__), "startup_items.json")
        self.items = self.filter_existing_items(self.load_items())  # Load and filter items
        self.item_widgets = {}  # Store references to item widgets for smooth updates
        self.is_refreshing = False  # Flag to prevent multiple simultaneous refreshes
        self.search_var = None  # Will be initialized in create_widgets
        self.search_entry = None
        self.commands_frame = None
        self.apps_frame = None
        self.commands_canvas = None
        self.apps_canvas = None
        
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
        # Configure root window to be resizable
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Main frame
        main_frame = tk.Frame(self, bg="#2e2f3e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure main frame grid weights
        main_frame.grid_rowconfigure(1, weight=1)  # Items frame row
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Management buttons frame
        button_frame = tk.Frame(main_frame, bg="#2e2f3e")
        button_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        button_frame.grid_columnconfigure(6, weight=1)  # Make space flexible after search box
        
        # First row of buttons
        tk.Button(button_frame, text="Add", command=self.add_new_item, 
                 bg="#4a4b5a", fg="white", font=("Arial", 9), width=8).grid(row=0, column=0, padx=2)
        
        self.refresh_btn = tk.Button(button_frame, text="Refresh", command=self.smooth_refresh, 
                                    bg="#4a4b5a", fg="white", font=("Arial", 9), width=8)
        self.refresh_btn.grid(row=0, column=1, padx=2)
        
        tk.Button(button_frame, text="Scan", command=self.scan_startup_folders, 
                 bg="#4a4b5a", fg="white", font=("Arial", 9), width=8).grid(row=0, column=2, padx=2)
        
        tk.Button(button_frame, text="Copy Reg", command=self.copy_registry_paths, 
                 bg="#4a4b5a", fg="white", font=("Arial", 9), width=8).grid(row=0, column=3, padx=2)
        
        tk.Button(button_frame, text="Del Match", command=self.delete_matching_shortcuts, 
                 bg="#d32f2f", fg="white", font=("Arial", 9), width=8).grid(row=0, column=4, padx=2)
        
        # Search frame - moved to left side after buttons
        search_frame = tk.Frame(button_frame, bg="#2e2f3e")
        search_frame.grid(row=0, column=5, padx=(10, 5))
        
        tk.Label(search_frame, text="Search:", bg="#2e2f3e", fg="white", 
                font=("Arial", 9)).pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_items)
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, 
                                   bg="#4a4b5a", fg="white", font=("Arial", 9), width=20)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        clear_btn = tk.Button(search_frame, text="✕", command=self.clear_search,
                            bg="#4a4b5a", fg="white", font=("Arial", 8), width=2)
        clear_btn.pack(side=tk.LEFT)
        
        # Status label for feedback - now on the far right with fixed position
        self.status_label = tk.Label(button_frame, text="Ready", bg="#2e2f3e", fg="#9ef959", 
                                    font=("Arial", 9))
        self.status_label.grid(row=0, column=7, padx=5, sticky="e")
        
        # Items frame
        self.items_frame = tk.Frame(main_frame, bg="#2e2f3e")
        self.items_frame.grid(row=1, column=0, sticky="nsew")
        
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
        
        # Configure grid weights for proper resizing
        self.items_frame.grid_columnconfigure(0, weight=1)  # Commands column
        self.items_frame.grid_columnconfigure(1, weight=0)  # Separator column (fixed width)
        self.items_frame.grid_columnconfigure(2, weight=1)  # Apps column
        self.items_frame.grid_rowconfigure(0, weight=0)     # Header row (fixed height)
        self.items_frame.grid_rowconfigure(1, weight=1)     # Content row (expandable)
        
        # Separate commands and apps
        commands = sorted([item for item in self.items if item["type"] == "Command"], key=lambda x: x["name"].lower())
        apps = sorted([item for item in self.items if item["type"] == "App"], key=lambda x: x["name"].lower())
        
        # Commands Section with scrollable frame
        self.create_scrollable_section("Commands", commands, column=0)
        
        # Vertical Separator
        separator = tk.Frame(self.items_frame, width=2, bg="#4a4b5a")
        separator.grid(row=0, column=1, rowspan=2, sticky="ns", padx=5)
        separator.grid_propagate(False)  # Maintain fixed width
        
        # Apps Section with scrollable frame
        self.create_scrollable_section("Apps", apps, column=2)

    def create_scrollable_section(self, section_name, items, column):
        # Section header
        header = tk.Label(self.items_frame, text=f"{section_name} ({len(items)})", 
                         font=("Helvetica", 10, "bold"), bg="#3a3c49", fg="#ffffff")
        header.grid(row=0, column=column, pady=5, sticky="ew", padx=5)
        
        # Create frame for scrollable content
        section_frame = tk.Frame(self.items_frame, bg="#2e2f3e")
        section_frame.grid(row=1, column=column, sticky="nsew", padx=5)
        section_frame.grid_rowconfigure(0, weight=1)
        section_frame.grid_columnconfigure(0, weight=1)
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(section_frame, bg="#2e2f3e", highlightthickness=0)
        scrollbar = ttk.Scrollbar(section_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#2e2f3e")
        
        # Configure scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Create window in canvas and configure it to expand with canvas width
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Bind canvas width changes to update scrollable_frame width
        def configure_scroll_frame(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Make scrollable_frame width match canvas width
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind('<Configure>', configure_scroll_frame)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Store references for filtering
        if section_name == "Commands":
            self.commands_frame = scrollable_frame
            self.commands_canvas = canvas
        else:
            self.apps_frame = scrollable_frame
            self.apps_canvas = canvas
        
        # Add items to scrollable frame
        for i, item in enumerate(items):
            self.create_item_widget_in_frame(item, i, scrollable_frame)
        
        # Configure grid weights for proper expansion
        scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
        
        # Bind mousewheel to scrollable_frame and all its children
        def bind_mousewheel_recursive(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel_recursive(child)
        
        bind_mousewheel_recursive(scrollable_frame)

    def create_item_widget_in_frame(self, item, row, parent_frame):
        frame = tk.Frame(parent_frame, bg="#2e2f3e", relief="solid", bd=1)
        frame.grid(row=row, column=0, padx=5, pady=2, sticky="ew")
        
        # Configure the parent frame to expand the item frames
        parent_frame.grid_columnconfigure(0, weight=1)
        
        # Main container with grid layout for better control
        main_container = tk.Frame(frame, bg="#2e2f3e")
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=3)
        main_container.grid_columnconfigure(1, weight=1)  # Name column expands
        
        # Checkbox icon
        checked = self.is_checked(item)
        icon_label = tk.Label(main_container, text="\uf205" if checked else "\uf204", 
                             font=("Jetbrainsmono nfp", 12, "bold"), 
                             fg="#9ef959" if checked else "gray", bg="#2e2f3e")
        icon_label.bind("<Button-1>", lambda event, item=item: self.toggle_startup_smooth(item))
        icon_label.grid(row=0, column=0, padx=(0, 5), sticky="nw")

        # Name label with wrapping
        name_label = tk.Label(main_container, text=item["name"], font=("Jetbrainsmono nfp", 10), bg="#2e2f3e", 
                             anchor="nw", justify=tk.LEFT, wraplength=200)  # Wrap at 200 pixels
        name_label.bind("<Button-1>", lambda event, item=item: self.launch_command(item))
        name_label.grid(row=0, column=1, padx=(0, 5), sticky="ew")
        
        self.update_label_color(name_label, checked)
        
        # Store widget references for smooth updates and filtering
        self.item_widgets[item["name"]] = {
            'icon': icon_label,
            'name': name_label,
            'frame': frame,
            'item_data': item
        }
        
        # Right side - edit and delete buttons (always visible)
        button_frame = tk.Frame(main_container, bg="#2e2f3e")
        button_frame.grid(row=0, column=2, sticky="ne")
        
        edit_btn = tk.Button(button_frame, text="Edit", command=lambda: self.edit_item(item),
                            bg="#4a4b5a", fg="white", font=("Arial", 8), width=6)
        edit_btn.pack(side=tk.LEFT, padx=2)
        
        delete_btn = tk.Button(button_frame, text="Delete", command=lambda: self.delete_item(item),
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
        self.wait_window(dialog.dialog)
        
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
        self.wait_window(dialog.dialog)
        
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

    def filter_items(self, *args):
        """Filter items based on search term"""
        search_term = self.search_var.get().lower()
        
        for item_name, widgets in self.item_widgets.items():
            frame = widgets.get('frame')
            item_data = widgets.get('item_data', {})
            
            if frame:
                # Check if item matches search term
                name_match = item_name.lower().find(search_term) != -1
                path_match = any(search_term in path.lower() for path in item_data.get('paths', []))
                command_match = search_term in item_data.get('Command', '').lower()
                
                if search_term == '' or name_match or path_match or command_match:
                    frame.grid()  # Show the item
                else:
                    frame.grid_remove()  # Hide the item
        
        # Update canvas scroll regions
        if hasattr(self, 'commands_canvas'):
            self.commands_canvas.configure(scrollregion=self.commands_canvas.bbox("all"))
        if hasattr(self, 'apps_canvas'):
            self.apps_canvas.configure(scrollregion=self.apps_canvas.bbox("all"))

    def clear_search(self):
        """Clear the search field"""
        self.search_var.set('')

    def scan_startup_folders(self):
        """Scan Windows startup folders for items"""
        try:
            startup_folders = [
                r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup",
                r"C:\Users\nahid\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"
            ]
            
            found_items = []
            existing_items = self.load_items()
            existing_names = {item["name"].lower() for item in existing_items}
            
            for folder in startup_folders:
                try:
                    if os.path.exists(folder):
                        files_in_folder = os.listdir(folder)
                        
                        for filename in files_in_folder:
                            file_path = os.path.join(folder, filename)
                            
                            # Skip directories and non-executable files
                            if os.path.isfile(file_path):
                                name, ext = os.path.splitext(filename)
                                
                                # Check if it's an executable type
                                if ext.lower() in ['.exe', '.bat', '.cmd', '.lnk', '.url']:
                                    # Skip if already exists in our items
                                    if name.lower() not in existing_names:
                                        actual_path = file_path
                                        command_args = ""
                                        executable_type = "other"
                                        
                                        # Handle shortcuts - simplified version
                                        if ext.lower() == '.lnk':
                                            # For now, just use the shortcut path as-is
                                            actual_path = file_path
                                            executable_type = "other"
                                        
                                        # Determine item type
                                        if ext.lower() == '.exe':
                                            item_type = "App"
                                        else:
                                            item_type = "Command"
                                        
                                        if os.path.exists(actual_path):
                                            found_items.append({
                                                "name": name,
                                                "type": item_type,
                                                "paths": [actual_path],
                                                "Command": command_args,
                                                "ExecutableType": executable_type
                                            })
                except Exception as e:
                    print(f"Error scanning folder {folder}: {e}")
                    continue
            
            if found_items:
                # Show dialog with found items
                result = messagebox.askyesno("Scan Results", 
                    f"Found {len(found_items)} new items in startup folders.\n\n"
                    f"Items: {', '.join([item['name'] for item in found_items[:5]])}"
                    f"{'...' if len(found_items) > 5 else ''}\n\n"
                    f"Add all items to the list?")
                
                if result:
                    # Add all found items
                    all_items = self.load_items()
                    all_items.extend(found_items)
                    self.save_items(all_items)
                    self.smooth_refresh()
                    self.show_status(f"Added {len(found_items)} items from startup folders", "#9ef959")
                else:
                    self.show_status("Scan completed - no items added", "#63dbff")
            else:
                self.show_status("No new items found in startup folders", "#63dbff")
                
        except Exception as e:
            self.show_status(f"Scan failed: {str(e)}", "#ff6b6b")

    def delete_matching_shortcuts(self):
        """Delete shortcuts from startup folders that match existing items"""
        try:
            # Get existing startup items
            existing_items = self.load_items()
            existing_names = {item["name"].lower() for item in existing_items}
            
            startup_folders = [
                r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup",
                r"C:\Users\nahid\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"
            ]
            
            deleted_shortcuts = []
            errors = []
            
            for folder in startup_folders:
                try:
                    if os.path.exists(folder):
                        for filename in os.listdir(folder):
                            if filename.lower().endswith('.lnk'):
                                file_path = os.path.join(folder, filename)
                                name = os.path.splitext(filename)[0]
                                
                                # Check if this shortcut matches an existing item
                                if name.lower() in existing_names:
                                    try:
                                        os.remove(file_path)
                                        deleted_shortcuts.append(name)
                                    except Exception as e:
                                        errors.append(f"Failed to delete {name}: {str(e)}")
                except Exception as e:
                    errors.append(f"Error scanning folder {folder}: {str(e)}")
            
            # Show results
            if deleted_shortcuts:
                message = f"Deleted {len(deleted_shortcuts)} matching shortcuts:\n\n"
                message += "\n".join(deleted_shortcuts[:10])  # Show first 10
                if len(deleted_shortcuts) > 10:
                    message += f"\n... and {len(deleted_shortcuts) - 10} more"
                
                if errors:
                    message += f"\n\nErrors: {len(errors)}"
                
                messagebox.showinfo("Delete Results", message)
                self.show_status(f"Deleted {len(deleted_shortcuts)} matching shortcuts", "#9ef959")
            else:
                self.show_status("No matching shortcuts found to delete", "#63dbff")
                
            if errors:
                error_msg = "\n".join(errors[:5])  # Show first 5 errors
                if len(errors) > 5:
                    error_msg += f"\n... and {len(errors) - 5} more errors"
                messagebox.showerror("Errors Occurred", error_msg)
                
        except Exception as e:
            self.show_status(f"Delete operation failed: {str(e)}", "#ff6b6b")

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