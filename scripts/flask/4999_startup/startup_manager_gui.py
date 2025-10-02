import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import winreg
import subprocess
import threading
from datetime import datetime

class StartupManagerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Startup Manager - PowerShell Script Mode")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1e1e2e')
        
        # Initialize paths
        self.json_file = os.path.join(os.path.dirname(__file__), "startup_items.json")
        self.ps1_file = os.path.join(os.path.expanduser("~"), "Desktop", "myStartup.ps1")
        
        # Configure style
        self.setup_style()
        
        # Create main interface
        self.create_widgets()
        self.load_items()
        
    def setup_style(self):
        """Setup ttk styling for modern theme"""
        self.style = ttk.Style()
        
        # List all available themes
        available_themes = self.style.theme_names()
        print("Available TTK themes:")
        for i, theme in enumerate(available_themes):
            print(f"  {i+1}. {theme}")
        
        # Select your preferred theme here
        selected_theme = 'winnative'  # Change this to any theme from the list above
        
        # Fallback if the selected theme is not available
        if selected_theme not in available_themes:
            print(f"Theme '{selected_theme}' not available, falling back to 'clam'")
            selected_theme = 'alt'
        
        print(f"Selected theme: {selected_theme}")
        self.style.theme_use(selected_theme)
        
        # Modern color palette
        colors = {
            'bg_primary': '#1e1e2e',      # Dark purple-blue
            'bg_secondary': '#313244',    # Lighter purple-blue
            'bg_tertiary': '#45475a',     # Even lighter
            'accent_blue': '#89b4fa',     # Bright blue
            'accent_green': '#a6e3a1',    # Bright green
            'accent_red': '#f38ba8',      # Bright red/pink
            'accent_yellow': '#f9e2af',   # Bright yellow
            'accent_purple': '#cba6f7',   # Bright purple
            'text_primary': '#cdd6f4',    # Light text
            'text_secondary': '#bac2de',  # Slightly dimmer text
            'text_muted': '#6c7086'       # Muted text
        }
        
        # Configure base styles
        self.style.configure('TFrame', background=colors['bg_primary'])
        self.style.configure('TLabel', 
                           background=colors['bg_primary'], 
                           foreground=colors['text_primary'],
                           font=('Segoe UI', 9))
        
        # Modern button styling - no white backgrounds
        self.style.configure('TButton', 
                           background=colors['bg_secondary'],
                           foreground=colors['text_primary'],
                           borderwidth=1,
                           focuscolor='none',
                           relief='solid',
                           font=('Segoe UI', 9))
        self.style.map('TButton', 
                      background=[('active', colors['bg_tertiary']),
                                ('pressed', colors['bg_tertiary'])],
                      foreground=[('active', colors['accent_blue']),
                                ('pressed', colors['accent_purple'])])
        
        # Entry styling
        self.style.configure('TEntry', 
                           background=colors['bg_secondary'],
                           foreground=colors['text_primary'],
                           fieldbackground=colors['bg_secondary'],
                           borderwidth=1,
                           insertcolor=colors['accent_blue'],
                           font=('Segoe UI', 9))
        self.style.map('TEntry',
                      focuscolor=[('focus', colors['accent_blue'])])
        
        # Scrollbar styling
        self.style.configure('TScrollbar', 
                           background=colors['bg_secondary'],
                           troughcolor=colors['bg_primary'],
                           borderwidth=0,
                           arrowcolor=colors['text_secondary'])
        
        # Treeview styling - ensure no white backgrounds
        self.style.configure('Treeview', 
                           background=colors['bg_secondary'],
                           foreground=colors['text_primary'],
                           fieldbackground=colors['bg_secondary'],
                           borderwidth=0,
                           font=('Segoe UI', 9))
        self.style.configure('Treeview.Heading', 
                           background=colors['bg_tertiary'],
                           foreground=colors['text_primary'],
                           borderwidth=1,
                           font=('Segoe UI', 9, 'bold'))
        self.style.map('Treeview', 
                      background=[('selected', colors['bg_tertiary']),
                                ('focus', colors['bg_secondary']),
                                ('!focus', colors['bg_secondary'])],
                      foreground=[('selected', colors['accent_blue'])])
        self.style.map('Treeview.Heading',
                      background=[('active', colors['accent_purple'])])
        
        # Force treeview item backgrounds
        self.style.configure('Treeview.Item', 
                           background=colors['bg_secondary'],
                           foreground=colors['text_primary'])
        
        # Custom styles
        self.style.configure('Title.TLabel', 
                           font=('Segoe UI', 20, 'bold'), 
                           background=colors['bg_primary'], 
                           foreground=colors['accent_blue'])
        
        self.style.configure('Info.TLabel', 
                           font=('Segoe UI', 10), 
                           background=colors['bg_primary'], 
                           foreground=colors['text_muted'])
        
        self.style.configure('Status.TLabel', 
                           font=('Segoe UI', 9), 
                           background=colors['bg_primary'], 
                           foreground=colors['accent_yellow'])
        
        # Action button styles - colored backgrounds
        self.style.configure('Primary.TButton', 
                           background='#2d4f7c',  # Dark blue background
                           foreground=colors['accent_blue'],
                           borderwidth=1,
                           relief='solid',
                           font=('Segoe UI', 9, 'bold'))
        self.style.map('Primary.TButton',
                      background=[('active', '#3a5f8c')],
                      foreground=[('active', '#a3c7ff')])
        
        self.style.configure('Success.TButton', 
                           background='#2d5a3d',  # Dark green background
                           foreground=colors['accent_green'],
                           borderwidth=1,
                           relief='solid',
                           font=('Segoe UI', 9, 'bold'))
        self.style.map('Success.TButton',
                      background=[('active', '#3a6a4d')],
                      foreground=[('active', '#b6f3b1')])
        
        self.style.configure('Danger.TButton', 
                           background='#5a2d3d',  # Dark red background
                           foreground=colors['accent_red'],
                           borderwidth=1,
                           relief='solid',
                           font=('Segoe UI', 9, 'bold'))
        self.style.map('Danger.TButton',
                      background=[('active', '#6a3a4d')],
                      foreground=[('active', '#ff9bb8')])
        
        self.style.configure('Warning.TButton', 
                           background='#5a4d2d',  # Dark yellow background
                           foreground=colors['accent_yellow'],
                           borderwidth=1,
                           relief='solid',
                           font=('Segoe UI', 9, 'bold'))
        self.style.map('Warning.TButton',
                      background=[('active', '#6a5d3d')],
                      foreground=[('active', '#fff2bf')])
        
    def create_widgets(self):
        # Main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(
            self.main_frame, 
            text="Startup Manager", 
            style='Title.TLabel'
        )
        title_label.pack(pady=(10, 5))
        
        # Info label
        info_label = ttk.Label(
            self.main_frame,
            text=f"PowerShell Script: {self.ps1_file}",
            style='Info.TLabel'
        )
        info_label.pack(pady=(0, 10))
        
        # Control buttons frame
        controls_frame = ttk.Frame(self.main_frame)
        controls_frame.pack(fill="x", pady=(0, 10))
        
        # Control buttons using regular tkinter buttons for full control
        tk.Button(
            controls_frame, 
            text="➕ Add Item", 
            command=self.open_add_dialog,
            bg='#2d4f7c',  # Dark blue
            fg='#89b4fa',  # Light blue text
            font=('Segoe UI', 9, 'bold'),
            relief='solid',
            borderwidth=1,
            activebackground='#3a5f8c',
            activeforeground='#a3c7ff',
            width=15
        ).pack(side="left", padx=5)
        
        tk.Button(
            controls_frame, 
            text="🔄 Refresh", 
            command=self.load_items,
            bg='#313244',  # Default dark
            fg='#cdd6f4',  # Light text
            font=('Segoe UI', 9, 'bold'),
            relief='solid',
            borderwidth=1,
            activebackground='#45475a',
            activeforeground='#89b4fa',
            width=12
        ).pack(side="left", padx=5)
        
        tk.Button(
            controls_frame, 
            text="🔍 Scan Registry", 
            command=self.scan_registry,
            bg='#5a4d2d',  # Dark yellow
            fg='#f9e2af',  # Light yellow text
            font=('Segoe UI', 9, 'bold'),
            relief='solid',
            borderwidth=1,
            activebackground='#6a5d3d',
            activeforeground='#fff2bf',
            width=15
        ).pack(side="left", padx=5)
        
        tk.Button(
            controls_frame, 
            text="📄 Open PS1", 
            command=self.open_ps1_file,
            bg='#2d5a3d',  # Dark green
            fg='#a6e3a1',  # Light green text
            font=('Segoe UI', 9, 'bold'),
            relief='solid',
            borderwidth=1,
            activebackground='#3a6a4d',
            activeforeground='#b6f3b1',
            width=12
        ).pack(side="left", padx=5)
        
        # Search frame
        search_frame = ttk.Frame(controls_frame)
        search_frame.pack(side="right", padx=5)
        
        ttk.Label(search_frame, text="Search:").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_items)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=25)
        search_entry.pack(side="left", padx=5)
        
        # Main items frame with optimized scrolling
        items_container = ttk.Frame(self.main_frame)
        items_container.pack(fill="both", expand=True, pady=(0, 10))
        
        # Use Treeview for better performance with large lists
        self.tree = ttk.Treeview(items_container, columns=('status', 'name', 'command'), show='tree headings', height=20)
        
        # Configure treeview tags for alternating row colors
        self.tree.tag_configure('evenrow', background='#313244')
        self.tree.tag_configure('oddrow', background='#2a2a3a')
        
        # Configure columns
        self.tree.heading('#0', text='', anchor='w')
        self.tree.heading('status', text='Status', anchor='w')
        self.tree.heading('name', text='Name', anchor='w')
        self.tree.heading('command', text='Command', anchor='w')
        
        self.tree.column('#0', width=0, stretch=False)
        self.tree.column('status', width=80, stretch=False)
        self.tree.column('name', width=200, stretch=False)
        self.tree.column('command', width=400, stretch=True)
        
        # Configure treeview styling
        self.style.configure('Treeview', background='#404040', foreground='white', fieldbackground='#404040')
        self.style.configure('Treeview.Heading', background='#2b2b2b', foreground='white')
        self.style.map('Treeview', background=[('selected', '#007bff')])
        
        # Scrollbar for treeview
        tree_scrollbar = ttk.Scrollbar(items_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        tree_scrollbar.pack(side="right", fill="y")
        
        # Bind events
        self.tree.bind('<Double-1>', self.on_item_double_click)
        self.tree.bind('<Button-3>', self.on_item_right_click)
        self.tree.bind('<Return>', self.on_item_enter)
        
        # Context menu with modern styling - no white backgrounds
        self.context_menu = tk.Menu(self.root, tearoff=0, 
                                   bg='#313244', fg='#cdd6f4',
                                   activebackground='#45475a', activeforeground='#89b4fa',
                                   font=('Segoe UI', 9))
        self.context_menu.add_command(label="Toggle Enable/Disable", command=self.context_toggle)
        self.context_menu.add_command(label="Launch", command=self.context_launch)
        self.context_menu.add_command(label="Edit", command=self.context_edit)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete", command=self.context_delete)
        
        # Store items data for context menu
        self.items_data = {}
        
        # Status bar at bottom
        status_frame = ttk.Frame(self.main_frame)
        status_frame.pack(fill="x", pady=(5, 0))
        
        self.status_label = ttk.Label(status_frame, 
                                     text="✨ Ready - Right-click items for actions",
                                     style='Status.TLabel')
        self.status_label.pack(side="left", padx=10)
        
    def on_item_double_click(self, event):
        """Handle double-click on item"""
        item_id = self.tree.selection()[0] if self.tree.selection() else None
        if item_id and item_id in self.items_data:
            self.launch_item(self.items_data[item_id])
    
    def on_item_right_click(self, event):
        """Handle right-click on item"""
        item_id = self.tree.identify_row(event.y)
        if item_id:
            self.tree.selection_set(item_id)
            self.context_menu.post(event.x_root, event.y_root)
    
    def on_item_enter(self, event):
        """Handle Enter key on item"""
        item_id = self.tree.selection()[0] if self.tree.selection() else None
        if item_id and item_id in self.items_data:
            self.toggle_item_enabled(self.items_data[item_id])
    
    def context_toggle(self):
        """Context menu toggle"""
        item_id = self.tree.selection()[0] if self.tree.selection() else None
        if item_id and item_id in self.items_data:
            self.toggle_item_enabled(self.items_data[item_id])
    
    def context_launch(self):
        """Context menu launch"""
        item_id = self.tree.selection()[0] if self.tree.selection() else None
        if item_id and item_id in self.items_data:
            self.launch_item(self.items_data[item_id])
    
    def context_edit(self):
        """Context menu edit"""
        item_id = self.tree.selection()[0] if self.tree.selection() else None
        if item_id and item_id in self.items_data:
            self.open_edit_dialog(self.items_data[item_id])
    
    def context_delete(self):
        """Context menu delete"""
        item_id = self.tree.selection()[0] if self.tree.selection() else None
        if item_id and item_id in self.items_data:
            self.delete_item(self.items_data[item_id])
    

        
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
        """Filter items (no path validation needed)"""
        filtered_items = []
        for item in items:
            filtered_items.append({
                "name": item["name"],
                "command": item.get("command", ""),
                "enabled": item.get("enabled", False)
            })
        return filtered_items
    
    def generate_powershell_script(self):
        """Generate PowerShell script with enabled items"""
        items = self.load_items_from_json()
        enabled_items = [item for item in items if item.get("enabled", False)]
        
        script_content = """# Auto-generated startup script
# Generated by Startup Manager
Write-Host "Starting up applications..." -ForegroundColor Green

"""
        
        for item in enabled_items:
            command = item.get("command", "")
            name = item["name"]
            
            if command.strip():
                script_content += f"# {name}\n"
                script_content += "try {\n"
                script_content += f'    Write-Host "Executing {name}..." -ForegroundColor Yellow\n'
                script_content += f'    {command}\n'
                script_content += f'    Write-Host "{name} executed successfully" -ForegroundColor Green\n'
                script_content += "} catch {\n"
                script_content += f'    Write-Host "Failed to execute {name}: $_" -ForegroundColor Red\n'
                script_content += "}\n\n"
        
        script_content += 'Write-Host "Startup complete!" -ForegroundColor Green\n'
        
        try:
            with open(self.ps1_file, 'w', encoding='utf-8') as f:
                f.write(script_content)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate PowerShell script: {e}")
            return False
    
    def launch_item(self, item):
        """Launch an item by executing its command"""
        try:
            command = item.get("command", "")
            
            if command.strip():
                # Execute the command in PowerShell
                subprocess.run(["powershell", "-Command", command], shell=True)
                self.status_label.config(text=f"{item['name']} executed successfully")
            else:
                self.status_label.config(text=f"No command specified for {item['name']}")
                messagebox.showwarning("Warning", f"No command specified for {item['name']}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to execute {item['name']}: {e}")
    
    def add_item_to_tree(self, item):
        """Add an item to the treeview"""
        is_enabled = item.get("enabled", False)
        status_text = "✓ Enabled" if is_enabled else "✗ Disabled"
        
        # Truncate command for display
        cmd_text = item.get("command", "")
        if len(cmd_text) > 80:
            cmd_text = cmd_text[:77] + "..."
        
        # Determine row tag for alternating colors
        row_count = len(self.tree.get_children())
        row_tag = 'evenrow' if row_count % 2 == 0 else 'oddrow'
        
        # Insert item into tree with alternating row colors
        item_id = self.tree.insert('', 'end', values=(status_text, item["name"], cmd_text), tags=(row_tag,))
        
        # Store item data for context menu
        self.items_data[item_id] = item
        
        return item_id
    
    def toggle_item_enabled(self, item):
        """Toggle item enabled status"""
        items = self.load_items_from_json()
        
        # Find and update the item
        for stored_item in items:
            if stored_item["name"] == item["name"]:
                stored_item["enabled"] = not stored_item.get("enabled", False)
                break
        
        # Save items and regenerate script
        if self.save_items_to_json(items):
            self.generate_powershell_script()
            action = "enabled" if stored_item["enabled"] else "disabled"
            self.status_label.config(text=f"{item['name']} {action}")
            self.load_items()
        else:
            self.status_label.config(text=f"Failed to update {item['name']}")
            messagebox.showerror("Error", f"Failed to update {item['name']}")
    
    def delete_item(self, item):
        """Delete an item"""
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{item['name']}'?"):
            items = self.load_items_from_json()
            
            # Remove from items list
            items = [stored_item for stored_item in items if stored_item["name"] != item["name"]]
            
            if self.save_items_to_json(items):
                self.generate_powershell_script()
                self.status_label.config(text=f"{item['name']} deleted successfully")
                self.load_items()
            else:
                self.status_label.config(text=f"Failed to delete {item['name']}")
                messagebox.showerror("Error", f"Failed to delete {item['name']}")
    
    def load_items(self):
        """Load and display all items"""
        # Clear existing items
        for item_id in self.tree.get_children():
            self.tree.delete(item_id)
        self.items_data.clear()
        
        # Load items from JSON
        items = self.filter_existing_items(self.load_items_from_json())
        
        # Sort items by name
        items.sort(key=lambda x: x["name"].lower())
        
        # Add items to tree (much faster than creating widgets)
        if items:
            for item in items:
                self.add_item_to_tree(item)
        
        # Update window title with count
        enabled_count = sum(1 for item in items if item.get("enabled", False))
        self.root.title(f"Startup Manager - {enabled_count}/{len(items)} enabled")
    
    def filter_items(self, *args):
        """Filter items based on search text with debouncing"""
        # Cancel previous filter if it exists
        if hasattr(self, '_filter_after_id'):
            self.root.after_cancel(self._filter_after_id)
        
        # Schedule filter with small delay to reduce rapid updates
        self._filter_after_id = self.root.after(300, self._do_filter)
    
    def _do_filter(self):
        """Actually perform the filtering"""
        search_text = self.search_var.get().lower().strip()
        
        # If no search text, show all items
        if not search_text:
            self.load_items()
            return
        
        # Clear existing items
        for item_id in self.tree.get_children():
            self.tree.delete(item_id)
        self.items_data.clear()
        
        # Load and filter items
        items = self.filter_existing_items(self.load_items_from_json())
        
        filtered_items = []
        for item in items:
            if (search_text in item["name"].lower() or 
                search_text in item.get("command", "").lower()):
                filtered_items.append(item)
        
        # Add filtered items to tree
        if filtered_items:
            for item in filtered_items:
                self.add_item_to_tree(item)
    
    def open_add_dialog(self):
        """Open dialog to add new item"""
        AddEditDialog(self, "Add New Item")
    
    def open_edit_dialog(self, item):
        """Open dialog to edit existing item"""
        AddEditDialog(self, "Edit Item", item)
    
    def open_ps1_file(self):
        """Open the PowerShell script file"""
        try:
            if os.path.exists(self.ps1_file):
                os.startfile(self.ps1_file)
            else:
                messagebox.showinfo("Info", "PowerShell script not found. Enable some items first.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open PowerShell script: {e}")
    
    def scan_registry(self):
        """Scan Windows registry for startup items"""
        def scan_thread():
            found_items = []
            existing_items = self.load_items_from_json()
            existing_names = {item["name"].lower() for item in existing_items}
            
            # Scan registry
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ) as reg_key:
                    i = 0
                    while True:
                        try:
                            name, value, _ = winreg.EnumValue(reg_key, i)
                            if name.lower() not in existing_names:
                                # Parse the command to extract path and arguments
                                parts = value.split('"')
                                if len(parts) >= 2:
                                    path = parts[1]
                                    args = ' '.join(parts[2:]).strip()
                                else:
                                    path = value.split()[0]
                                    args = ' '.join(value.split()[1:])
                                
                                # Create a PowerShell command from the registry value
                                if args:
                                    ps_command = f'Start-Process -FilePath "{path}" -ArgumentList "{args}"'
                                else:
                                    ps_command = f'Start-Process -FilePath "{path}"'
                                
                                found_items.append({
                                    "name": name,
                                    "command": ps_command,
                                    "registry_value": value
                                })
                            i += 1
                        except WindowsError:
                            break
            except Exception as e:
                print(f"Error scanning registry: {e}")
            
            # Show results in main thread
            self.root.after(0, lambda: self.show_scan_results(found_items))
        
        # Run scan in background thread
        threading.Thread(target=scan_thread, daemon=True).start()
        messagebox.showinfo("Scanning", "Scanning Windows registry...")
    
    def show_scan_results(self, found_items):
        """Show scan results dialog"""
        if not found_items:
            messagebox.showinfo("Scan Complete", "No new items found in registry")
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
        self.dialog = tk.Toplevel(parent.root)
        self.dialog.title(title)
        self.dialog.geometry("600x250")
        self.dialog.configure(bg='#1e1e2e')
        self.dialog.transient(parent.root)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (250 // 2)
        self.dialog.geometry(f"600x250+{x}+{y}")
        
        # Configure style for dialog
        self.style = ttk.Style()
        
        self.create_widgets()
        
        if self.is_edit:
            self.populate_fields()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Name field
        ttk.Label(main_frame, text="Name:").pack(anchor="w", padx=10, pady=(10, 5))
        self.name_entry = ttk.Entry(main_frame, width=70)
        self.name_entry.pack(padx=10, pady=(0, 15))
        
        # Command field
        ttk.Label(main_frame, text="PowerShell Command:").pack(anchor="w", padx=10, pady=(0, 5))
        
        # Command examples
        examples_label = ttk.Label(
            main_frame,
            text="Examples: Start-Process 'notepad.exe' | python C:\\path\\to\\script.py | & 'C:\\Program Files\\App\\app.exe'",
            font=('Arial', 9),
            foreground="gray"
        )
        examples_label.pack(anchor="w", padx=10, pady=(0, 5))
        
        self.command_entry = ttk.Entry(main_frame, width=70)
        self.command_entry.pack(padx=10, pady=(0, 15))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        save_btn = ttk.Button(
            button_frame, 
            text="💾 Save", 
            command=self.save_item,
            width=12,
            style='Primary.TButton'
        )
        save_btn.pack(side="left", padx=10)
        
        cancel_btn = ttk.Button(
            button_frame, 
            text="❌ Cancel", 
            command=self.dialog.destroy,
            width=12
        )
        cancel_btn.pack(side="right", padx=10)
    
    def populate_fields(self):
        """Populate fields when editing"""
        if self.item:
            self.name_entry.insert(0, self.item["name"])
            self.command_entry.insert(0, self.item.get("command", ""))
    
    def save_item(self):
        """Save the item"""
        # Validate fields
        name = self.name_entry.get().strip()
        command = self.command_entry.get().strip()
        
        if not name or not command:
            messagebox.showerror("Error", "Name and Command are required")
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
            "command": command,
            "enabled": False  # New items start disabled
        }
        
        if self.is_edit:
            # Update existing item (preserve enabled status)
            for i, stored_item in enumerate(items):
                if stored_item["name"] == self.item["name"]:
                    new_item["enabled"] = stored_item.get("enabled", False)
                    items[i] = new_item
                    break
        else:
            # Add new item
            items.append(new_item)
        
        # Save items and regenerate script
        if self.parent.save_items_to_json(items):
            self.parent.generate_powershell_script()
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
        self.dialog = tk.Toplevel(parent.root)
        self.dialog.title(f"Registry Scan Results - {len(found_items)} items found")
        self.dialog.geometry("800x500")
        self.dialog.configure(bg='#1e1e2e')
        self.dialog.transient(parent.root)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"800x500+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text=f"Found {len(self.found_items)} items in Windows registry",
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=(10, 20))
        
        # Info label
        info_label = ttk.Label(
            main_frame,
            text="Select items to add to your startup list. They will be removed from registry.",
            font=('Arial', 10),
            foreground="orange"
        )
        info_label.pack(pady=(0, 20))
        
        # Create canvas and scrollbar for items
        items_container = ttk.Frame(main_frame)
        items_container.pack(fill="both", expand=True, pady=(0, 20))
        
        canvas = tk.Canvas(items_container, bg='#1e1e2e', highlightthickness=0)
        scrollbar = ttk.Scrollbar(items_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create checkboxes for each item
        self.item_vars = []
        for item in self.found_items:
            var = tk.BooleanVar(value=True)
            self.item_vars.append(var)
            
            item_frame = ttk.Frame(scrollable_frame)
            item_frame.pack(fill="x", padx=5, pady=2)
            
            checkbox = ttk.Checkbutton(
                item_frame,
                text=item['name'],
                variable=var
            )
            checkbox.pack(anchor="w", padx=10, pady=5)
            
            cmd_label = ttk.Label(
                item_frame,
                text=f"Command: {item['command']}",
                font=('Arial', 9),
                foreground="lightblue"
            )
            cmd_label.pack(anchor="w", padx=30, pady=2)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        select_all_btn = ttk.Button(
            button_frame,
            text="✅ Select All",
            command=self.select_all,
            width=15,
            style='Success.TButton'
        )
        select_all_btn.pack(side="left", padx=5)
        
        select_none_btn = ttk.Button(
            button_frame,
            text="❌ Select None",
            command=self.select_none,
            width=15
        )
        select_none_btn.pack(side="left", padx=5)
        
        add_btn = ttk.Button(
            button_frame,
            text="➕ Add Selected",
            command=self.add_selected,
            width=18,
            style='Primary.TButton'
        )
        add_btn.pack(side="right", padx=5)
        
        cancel_btn = ttk.Button(
            button_frame,
            text="❌ Cancel",
            command=self.dialog.destroy,
            width=12
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
        items_to_remove_from_registry = []
        
        for i, var in enumerate(self.item_vars):
            if var.get():
                item = self.found_items[i]
                selected_items.append({
                    "name": item["name"],
                    "command": item["command"],
                    "enabled": False  # Start disabled
                })
                items_to_remove_from_registry.append(item["name"])
        
        if not selected_items:
            messagebox.showwarning("Warning", "No items selected")
            return
        
        # Load existing items and add selected ones
        existing_items = self.parent.load_items_from_json()
        existing_items.extend(selected_items)
        
        # Save items
        if self.parent.save_items_to_json(existing_items):
            # Remove selected items from registry
            removed_count = 0
            for item_name in items_to_remove_from_registry:
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_ALL_ACCESS) as reg_key:
                        winreg.DeleteValue(reg_key, item_name)
                        removed_count += 1
                except Exception as e:
                    print(f"Failed to remove {item_name} from registry: {e}")
            
            self.parent.generate_powershell_script()
            messagebox.showinfo("Success", 
                f"Added {len(selected_items)} items successfully!\n"
                f"Removed {removed_count} items from registry.")
            self.dialog.destroy()
            self.parent.load_items()
        else:
            messagebox.showerror("Error", "Failed to save items")


if __name__ == "__main__":
    app = StartupManagerGUI()
    app.run()