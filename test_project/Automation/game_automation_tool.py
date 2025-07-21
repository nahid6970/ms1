import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json
import os
import threading
import time
import pyautogui
import pygetwindow as gw
from datetime import datetime
from pathlib import Path

# Try to import keyboard module, fallback if not available
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False

class GameAutomationTool:
    def __init__(self, root):
        self.root = root
        self.root.title("PyAutoGUI Game Automation Tool - Shadow Fight 3")
        self.root.geometry("1200x800")
        self.root.configure(bg="#2b2b2b")
        
        # Initialize data structures
        self.events_data = {}
        self.stop_flags = {}
        self.threads = {}
        self.config_file = "sf3_automation_config.json"
        self.target_window = "LDPlayer"
        
        # Setup GUI
        self.setup_gui()
        
        # Load existing config
        self.load_config()
        self.setup_menu()
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_gui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg="#2b2b2b")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left Panel - Event Management
        left_frame = tk.Frame(main_frame, bg="#2b2b2b", width=400)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        left_frame.pack_propagate(False)
        
        # Event Management Section
        event_label = tk.Label(left_frame, text="Events", bg="#2b2b2b", fg="white", font=("Arial", 12, "bold"))
        event_label.pack(anchor="w", pady=(0, 5))
        
        # Event selection frame
        event_select_frame = tk.Frame(left_frame, bg="#2b2b2b")
        event_select_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Event dropdown
        self.selected_event = tk.StringVar()
        self.event_dropdown = ttk.Combobox(
            event_select_frame, 
            textvariable=self.selected_event, 
            state="readonly",
            width=25
        )
        self.event_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.event_dropdown.bind("<<ComboboxSelected>>", self.on_event_select)
        
        # Add event button with + icon
        add_event_btn = tk.Button(
            event_select_frame, 
            text="+ Add", 
            command=self.add_event, 
            bg="#4CAF50", 
            fg="white",
            width=6
        )
        add_event_btn.pack(side=tk.RIGHT)
        
        # Event management buttons
        event_btn_frame = tk.Frame(left_frame, bg="#2b2b2b")
        event_btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Button(event_btn_frame, text="Delete Event", command=self.delete_event, bg="#f44336", fg="white").pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(event_btn_frame, text="Rename Event", command=self.rename_event, bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(event_btn_frame, text="Duplicate Event", command=self.duplicate_event, bg="#FF9800", fg="white").pack(side=tk.LEFT)
        
        # Image Management Section
        image_label = tk.Label(left_frame, text="Images", bg="#2b2b2b", fg="white", font=("Arial", 12, "bold"))
        image_label.pack(anchor="w", pady=(10, 5))
        
        # Image listbox with scrollbar
        image_frame = tk.Frame(left_frame, bg="#2b2b2b")
        image_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.image_listbox = tk.Listbox(image_frame, bg="#404040", fg="white", selectbackground="#555555")
        image_scrollbar = tk.Scrollbar(image_frame, orient=tk.VERTICAL, command=self.image_listbox.yview)
        self.image_listbox.config(yscrollcommand=image_scrollbar.set)
        
        self.image_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        image_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Image buttons
        image_btn_frame = tk.Frame(left_frame, bg="#2b2b2b")
        image_btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Button(image_btn_frame, text="Add Image", command=self.add_image, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(image_btn_frame, text="Edit Image", command=self.edit_image, bg="#FF9800", fg="white").pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(image_btn_frame, text="Delete Image", command=self.delete_image, bg="#f44336", fg="white").pack(side=tk.LEFT)
        
        # Control Panel
        control_frame = tk.Frame(left_frame, bg="#2b2b2b")
        control_frame.pack(fill=tk.X, pady=(20, 0))
        
        control_label = tk.Label(control_frame, text="Event Control", bg="#2b2b2b", fg="white", font=("Arial", 12, "bold"))
        control_label.pack(anchor="w", pady=(0, 10))
        
        self.control_buttons_frame = tk.Frame(control_frame, bg="#2b2b2b")
        self.control_buttons_frame.pack(fill=tk.X)
        
        # Right Panel - Status and Info
        right_frame = tk.Frame(main_frame, bg="#2b2b2b")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Status Section
        status_label = tk.Label(right_frame, text="Status & Information", bg="#2b2b2b", fg="white", font=("Arial", 12, "bold"))
        status_label.pack(anchor="w", pady=(0, 10))
        
        # Status text area
        status_frame = tk.Frame(right_frame, bg="#2b2b2b")
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        self.status_text = tk.Text(status_frame, bg="#404040", fg="white", wrap=tk.WORD, height=20)
        status_text_scrollbar = tk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.config(yscrollcommand=status_text_scrollbar.set)
        
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        status_text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Utility buttons
        util_frame = tk.Frame(right_frame, bg="#2b2b2b")
        util_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(util_frame, text="Screenshot", command=self.take_screenshot, bg="#9C27B0", fg="white").pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(util_frame, text="Get Mouse Position", command=self.get_mouse_position, bg="#607D8B", fg="white").pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(util_frame, text="Test Image", command=self.test_image_recognition, bg="#795548", fg="white").pack(side=tk.LEFT)
        
        # Initialize display
        self.refresh_event_list()
        self.refresh_control_buttons()
        
    def setup_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_config)
        file_menu.add_command(label="Open", command=self.open_config)
        file_menu.add_command(label="Save", command=self.save_config)
        file_menu.add_separator()
        file_menu.add_command(label="Export", command=self.export_config)
        file_menu.add_command(label="Import", command=self.import_config)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Window Settings", command=self.window_settings)
        tools_menu.add_command(label="List Windows", command=self.list_windows)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Help", command=self.show_help)   

    def add_event(self):
        """Add a new event"""
        name = simpledialog.askstring("Add Event", "Enter event name:")
        if name and name not in self.events_data:
            self.events_data[name] = {
                "images": [],
                "enabled": True
            }
            self.stop_flags[name] = False
            self.refresh_event_list()
            self.refresh_control_buttons()
            self.save_config()
            self.log_status(f"Added event: {name}")
        elif name in self.events_data:
            messagebox.showerror("Error", "Event name already exists!")
    
    def delete_event(self):
        """Delete selected event"""
        event_name = self.selected_event.get()
        if not event_name:
            messagebox.showwarning("Warning", "Please select an event to delete.")
            return
        
        if messagebox.askyesno("Confirm Delete", f"Delete event '{event_name}'?"):
            # Stop the event if running
            if event_name in self.threads and self.threads[event_name].is_alive():
                self.stop_event(event_name)
            
            del self.events_data[event_name]
            if event_name in self.stop_flags:
                del self.stop_flags[event_name]
            if event_name in self.threads:
                del self.threads[event_name]
            
            self.refresh_event_list()
            self.refresh_control_buttons()
            self.refresh_image_list()
            self.save_config()
            self.log_status(f"Deleted event: {event_name}")
    
    def rename_event(self):
        """Rename selected event"""
        old_name = self.selected_event.get()
        if not old_name:
            messagebox.showwarning("Warning", "Please select an event to rename.")
            return
        
        new_name = simpledialog.askstring("Rename Event", f"Enter new name for '{old_name}':", initialvalue=old_name)
        
        if new_name and new_name != old_name:
            if new_name in self.events_data:
                messagebox.showerror("Error", "Event name already exists!")
                return
            
            # Stop the event if running
            if old_name in self.threads and self.threads[old_name].is_alive():
                self.stop_event(old_name)
            
            # Rename the event
            self.events_data[new_name] = self.events_data.pop(old_name)
            self.stop_flags[new_name] = self.stop_flags.pop(old_name, False)
            if old_name in self.threads:
                self.threads[new_name] = self.threads.pop(old_name)
            
            self.refresh_event_list()
            self.refresh_control_buttons()
            self.save_config()
            self.log_status(f"Renamed event: {old_name} -> {new_name}")
    
    def duplicate_event(self):
        """Duplicate selected event"""
        old_name = self.selected_event.get()
        if not old_name:
            messagebox.showwarning("Warning", "Please select an event to duplicate.")
            return
        
        new_name = simpledialog.askstring("Duplicate Event", f"Enter name for duplicate of '{old_name}':", initialvalue=f"{old_name}_copy")
        
        if new_name and new_name != old_name:
            if new_name in self.events_data:
                messagebox.showerror("Error", "Event name already exists!")
                return
            
            # Create a deep copy of the event data
            import copy
            self.events_data[new_name] = copy.deepcopy(self.events_data[old_name])
            self.stop_flags[new_name] = False
            
            self.refresh_event_list()
            self.refresh_control_buttons()
            self.save_config()
            self.log_status(f"Duplicated event: {old_name} -> {new_name}")
    
    def add_image(self):
        """Add image to selected event with popup configuration"""
        event_name = self.selected_event.get()
        if not event_name:
            messagebox.showwarning("Warning", "Please select an event first.")
            return
        
        self.show_image_config_dialog(event_name)
    
    def edit_image(self):
        """Edit selected image with popup configuration"""
        event_name = self.selected_event.get()
        image_selection = self.image_listbox.curselection()
        
        if not event_name:
            messagebox.showwarning("Warning", "Please select an event first.")
            return
        if not image_selection:
            messagebox.showwarning("Warning", "Please select an image to edit.")
            return
        
        image_index = image_selection[0]
        self.show_image_config_dialog(event_name, image_index)
    
    def delete_image(self):
        """Delete selected image"""
        event_name = self.selected_event.get()
        image_selection = self.image_listbox.curselection()
        
        if not event_name:
            messagebox.showwarning("Warning", "Please select an event first.")
            return
        if not image_selection:
            messagebox.showwarning("Warning", "Please select an image to delete.")
            return
        
        image_index = image_selection[0]
        image_name = self.events_data[event_name]["images"][image_index]["name"]
        
        if messagebox.askyesno("Confirm Delete", f"Delete image '{image_name}'?"):
            del self.events_data[event_name]["images"][image_index]
            self.refresh_image_list()
            self.save_config()
            self.log_status(f"Deleted image: {image_name} from event: {event_name}")
    
    def show_image_config_dialog(self, event_name, image_index=None):
        """Show popup dialog for image configuration"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Image Configuration")
        dialog.geometry("600x700")
        dialog.configure(bg="#2b2b2b")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Variables
        image_name_var = tk.StringVar()
        image_path_var = tk.StringVar()
        confidence_var = tk.DoubleVar(value=0.8)
        region_x1_var = tk.StringVar()
        region_y1_var = tk.StringVar()
        region_x2_var = tk.StringVar()
        region_y2_var = tk.StringVar()
        action_type_var = tk.StringVar(value="key_press")
        
        # Load existing data if editing
        if image_index is not None:
            image_data = self.events_data[event_name]["images"][image_index]
            image_name_var.set(image_data["name"])
            image_path_var.set(image_data["path"])
            confidence_var.set(image_data["confidence"])
            
            if image_data.get("region"):
                region_x1_var.set(str(image_data["region"][0]))
                region_y1_var.set(str(image_data["region"][1]))
                region_x2_var.set(str(image_data["region"][2]))
                region_y2_var.set(str(image_data["region"][3]))
            
            action_type_var.set(image_data["action"]["type"])
        
        # Create form
        row = 0
        
        # Image Name
        tk.Label(dialog, text="Image Name:", bg="#2b2b2b", fg="white").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        tk.Entry(dialog, textvariable=image_name_var, width=40, bg="#404040", fg="white").grid(row=row, column=1, columnspan=2, padx=10, pady=5, sticky="ew")
        row += 1
        
        # Image Path
        tk.Label(dialog, text="Image Path:", bg="#2b2b2b", fg="white").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        tk.Entry(dialog, textvariable=image_path_var, width=30, bg="#404040", fg="white").grid(row=row, column=1, padx=10, pady=5, sticky="ew")
        tk.Button(dialog, text="Browse", command=lambda: self.browse_image_file(image_path_var), bg="#2196F3", fg="white").grid(row=row, column=2, padx=10, pady=5)
        row += 1
        
        # Confidence
        tk.Label(dialog, text="Confidence:", bg="#2b2b2b", fg="white").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        confidence_scale = tk.Scale(dialog, from_=0.1, to=1.0, resolution=0.1, orient=tk.HORIZONTAL, variable=confidence_var, bg="#404040", fg="white", highlightbackground="#2b2b2b")
        confidence_scale.grid(row=row, column=1, columnspan=2, padx=10, pady=5, sticky="ew")
        row += 1
        
        # Region
        tk.Label(dialog, text="Search Region (optional):", bg="#2b2b2b", fg="white").grid(row=row, column=0, columnspan=3, sticky="w", padx=10, pady=(15, 5))
        row += 1
        
        region_frame = tk.Frame(dialog, bg="#2b2b2b")
        region_frame.grid(row=row, column=0, columnspan=3, padx=10, pady=5, sticky="ew")
        
        tk.Label(region_frame, text="X1:", bg="#2b2b2b", fg="white").grid(row=0, column=0, padx=5)
        tk.Entry(region_frame, textvariable=region_x1_var, width=8, bg="#404040", fg="white").grid(row=0, column=1, padx=5)
        tk.Label(region_frame, text="Y1:", bg="#2b2b2b", fg="white").grid(row=0, column=2, padx=5)
        tk.Entry(region_frame, textvariable=region_y1_var, width=8, bg="#404040", fg="white").grid(row=0, column=3, padx=5)
        tk.Label(region_frame, text="X2:", bg="#2b2b2b", fg="white").grid(row=0, column=4, padx=5)
        tk.Entry(region_frame, textvariable=region_x2_var, width=8, bg="#404040", fg="white").grid(row=0, column=5, padx=5)
        tk.Label(region_frame, text="Y2:", bg="#2b2b2b", fg="white").grid(row=0, column=6, padx=5)
        tk.Entry(region_frame, textvariable=region_y2_var, width=8, bg="#404040", fg="white").grid(row=0, column=7, padx=5)
        
        tk.Button(region_frame, text="Get Region", command=lambda: self.get_screen_region(region_x1_var, region_y1_var, region_x2_var, region_y2_var), bg="#FF9800", fg="white").grid(row=0, column=8, padx=10)
        row += 1
        
        # Action Type
        tk.Label(dialog, text="Action Type:", bg="#2b2b2b", fg="white").grid(row=row, column=0, sticky="w", padx=10, pady=(15, 5))
        action_combo = ttk.Combobox(dialog, textvariable=action_type_var, values=["key_press", "key_sequence", "mouse_click", "mouse_sequence", "custom_function"], state="readonly")
        action_combo.grid(row=row, column=1, columnspan=2, padx=10, pady=(15, 5), sticky="ew")
        row += 1
        
        # Dynamic action configuration frame
        action_config_frame = tk.Frame(dialog, bg="#2b2b2b")
        action_config_frame.grid(row=row, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
        row += 1
        
        # Action configuration variables
        action_vars = {}
        
        def update_action_config(*args):
            # Clear existing widgets
            for widget in action_config_frame.winfo_children():
                widget.destroy()
            action_vars.clear()
            
            action_type = action_type_var.get()
            
            if action_type == "key_press":
                tk.Label(action_config_frame, text="Key:", bg="#2b2b2b", fg="white").grid(row=0, column=0, sticky="w", pady=5)
                action_vars["key"] = tk.StringVar()
                tk.Entry(action_config_frame, textvariable=action_vars["key"], bg="#404040", fg="white").grid(row=0, column=1, padx=10, pady=5)
                
                tk.Label(action_config_frame, text="Delay (seconds):", bg="#2b2b2b", fg="white").grid(row=1, column=0, sticky="w", pady=5)
                action_vars["delay"] = tk.StringVar(value="0.1")
                tk.Entry(action_config_frame, textvariable=action_vars["delay"], bg="#404040", fg="white").grid(row=1, column=1, padx=10, pady=5)
                
            elif action_type == "key_sequence":
                tk.Label(action_config_frame, text="Key Sequence:", bg="#2b2b2b", fg="white").grid(row=0, column=0, sticky="w", pady=5)
                tk.Label(action_config_frame, text="Format: key1,delay1,key2,delay2", bg="#2b2b2b", fg="gray").grid(row=1, column=0, columnspan=2, sticky="w", pady=2)
                action_vars["sequence"] = tk.StringVar()
                tk.Entry(action_config_frame, textvariable=action_vars["sequence"], width=40, bg="#404040", fg="white").grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
                
            elif action_type == "mouse_click":
                tk.Label(action_config_frame, text="X Position:", bg="#2b2b2b", fg="white").grid(row=0, column=0, sticky="w", pady=5)
                action_vars["x"] = tk.StringVar()
                tk.Entry(action_config_frame, textvariable=action_vars["x"], bg="#404040", fg="white").grid(row=0, column=1, padx=10, pady=5)
                
                tk.Label(action_config_frame, text="Y Position:", bg="#2b2b2b", fg="white").grid(row=1, column=0, sticky="w", pady=5)
                action_vars["y"] = tk.StringVar()
                tk.Entry(action_config_frame, textvariable=action_vars["y"], bg="#404040", fg="white").grid(row=1, column=1, padx=10, pady=5)
                
                tk.Button(action_config_frame, text="Get Position", command=lambda: self.get_click_position(action_vars["x"], action_vars["y"]), bg="#607D8B", fg="white").grid(row=0, column=2, rowspan=2, padx=10, pady=5)
                
                tk.Label(action_config_frame, text="Delay (seconds):", bg="#2b2b2b", fg="white").grid(row=2, column=0, sticky="w", pady=5)
                action_vars["delay"] = tk.StringVar(value="0.1")
                tk.Entry(action_config_frame, textvariable=action_vars["delay"], bg="#404040", fg="white").grid(row=2, column=1, padx=10, pady=5)
                
            elif action_type == "mouse_sequence":
                tk.Label(action_config_frame, text="Mouse Sequence:", bg="#2b2b2b", fg="white").grid(row=0, column=0, sticky="w", pady=5)
                tk.Label(action_config_frame, text="Format: x1,y1,delay1,x2,y2,delay2", bg="#2b2b2b", fg="gray").grid(row=1, column=0, columnspan=2, sticky="w", pady=2)
                action_vars["sequence"] = tk.StringVar()
                tk.Entry(action_config_frame, textvariable=action_vars["sequence"], width=40, bg="#404040", fg="white").grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
                
            elif action_type == "custom_function":
                tk.Label(action_config_frame, text="Function Name:", bg="#2b2b2b", fg="white").grid(row=0, column=0, sticky="w", pady=5)
                action_vars["function"] = tk.StringVar()
                tk.Entry(action_config_frame, textvariable=action_vars["function"], bg="#404040", fg="white").grid(row=0, column=1, padx=10, pady=5)
                
                tk.Label(action_config_frame, text="Parameters (JSON):", bg="#2b2b2b", fg="white").grid(row=1, column=0, sticky="w", pady=5)
                action_vars["params"] = tk.StringVar(value="{}")
                tk.Entry(action_config_frame, textvariable=action_vars["params"], width=40, bg="#404040", fg="white").grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        
        # Load existing action data if editing
        if image_index is not None:
            action_data = self.events_data[event_name]["images"][image_index]["action"]
            
            def load_action_data():
                update_action_config()
                action_type = action_data["type"]
                
                if action_type == "key_press":
                    action_vars["key"].set(action_data.get("key", ""))
                    action_vars["delay"].set(str(action_data.get("delay", 0.1)))
                elif action_type == "key_sequence":
                    action_vars["sequence"].set(action_data.get("sequence", ""))
                elif action_type == "mouse_click":
                    action_vars["x"].set(str(action_data.get("x", "")))
                    action_vars["y"].set(str(action_data.get("y", "")))
                    action_vars["delay"].set(str(action_data.get("delay", 0.1)))
                elif action_type == "mouse_sequence":
                    action_vars["sequence"].set(action_data.get("sequence", ""))
                elif action_type == "custom_function":
                    action_vars["function"].set(action_data.get("function", ""))
                    action_vars["params"].set(action_data.get("params", "{}"))
            
            dialog.after(100, load_action_data)
        
        # Bind action type change
        action_type_var.trace("w", update_action_config)
        update_action_config()
        
        # Buttons
        button_frame = tk.Frame(dialog, bg="#2b2b2b")
        button_frame.grid(row=row, column=0, columnspan=3, pady=20)
        
        def save_image_config():
            # Validate inputs
            if not image_name_var.get().strip():
                messagebox.showerror("Error", "Please enter an image name.")
                return
            if not image_path_var.get().strip():
                messagebox.showerror("Error", "Please select an image file.")
                return
            if not os.path.exists(image_path_var.get()):
                messagebox.showerror("Error", "Image file does not exist.")
                return
            
            # Build region
            region = None
            if all([region_x1_var.get(), region_y1_var.get(), region_x2_var.get(), region_y2_var.get()]):
                try:
                    region = [int(region_x1_var.get()), int(region_y1_var.get()), 
                             int(region_x2_var.get()), int(region_y2_var.get())]
                except ValueError:
                    messagebox.showerror("Error", "Region coordinates must be integers.")
                    return
            
            # Build action
            action_type = action_type_var.get()
            action = {"type": action_type}
            
            try:
                if action_type == "key_press":
                    action["key"] = action_vars["key"].get()
                    action["delay"] = float(action_vars["delay"].get())
                elif action_type == "key_sequence":
                    action["sequence"] = action_vars["sequence"].get()
                elif action_type == "mouse_click":
                    action["x"] = int(action_vars["x"].get())
                    action["y"] = int(action_vars["y"].get())
                    action["delay"] = float(action_vars["delay"].get())
                elif action_type == "mouse_sequence":
                    action["sequence"] = action_vars["sequence"].get()
                elif action_type == "custom_function":
                    action["function"] = action_vars["function"].get()
                    # Validate JSON
                    json.loads(action_vars["params"].get())
                    action["params"] = action_vars["params"].get()
            except (ValueError, json.JSONDecodeError) as e:
                messagebox.showerror("Error", f"Invalid action configuration: {str(e)}")
                return
            
            # Create image data
            image_data = {
                "name": image_name_var.get().strip(),
                "path": image_path_var.get(),
                "confidence": confidence_var.get(),
                "region": region,
                "action": action
            }
            
            # Save to event
            if image_index is not None:
                self.events_data[event_name]["images"][image_index] = image_data
                self.log_status(f"Updated image: {image_data['name']} in event: {event_name}")
            else:
                self.events_data[event_name]["images"].append(image_data)
                self.log_status(f"Added image: {image_data['name']} to event: {event_name}")
            
            self.refresh_image_list()
            self.save_config()
            dialog.destroy()
        
        tk.Button(button_frame, text="Save", command=save_image_config, bg="#4CAF50", fg="white", width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy, bg="#f44336", fg="white", width=10).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        dialog.grid_columnconfigure(1, weight=1)
        action_config_frame.grid_columnconfigure(1, weight=1)
    
    def browse_image_file(self, path_var):
        """Browse for image file"""
        filename = filedialog.askopenfilename(
            title="Select Image File",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*")]
        )
        if filename:
            path_var.set(filename)   
    def get_screen_region(self, x1_var, y1_var, x2_var, y2_var):
        """Get screen region by user selection"""
        messagebox.showinfo("Get Region", "Move mouse to first corner and press SPACE.")
        
        def get_region():
            try:
                import keyboard
                
                # Wait for user to press space
                keyboard.wait('space')
                
                # Get current mouse position as starting point
                start_x, start_y = pyautogui.position()
                
                messagebox.showinfo("Region Selection", "Now move to opposite corner and press SPACE again.")
                
                # Wait for second space press
                keyboard.wait('space')
                
                end_x, end_y = pyautogui.position()
                
                # Set the region coordinates
                x1_var.set(str(min(start_x, end_x)))
                y1_var.set(str(min(start_y, end_y)))
                x2_var.set(str(max(start_x, end_x)))
                y2_var.set(str(max(start_y, end_y)))
                
                messagebox.showinfo("Success", f"Region set: ({min(start_x, end_x)}, {min(start_y, end_y)}) to ({max(start_x, end_x)}, {max(start_y, end_y)})")
                
            except ImportError:
                # Fallback method using mouse clicks instead of keyboard
                messagebox.showinfo("Get Region", "Keyboard module not available. Click at first corner.")
                
                # Simple fallback - wait for mouse clicks
                import tkinter as tk
                
                def wait_for_click():
                    root = tk.Tk()
                    root.withdraw()  # Hide the window
                    root.attributes('-topmost', True)
                    root.attributes('-alpha', 0.1)
                    root.geometry('1x1+0+0')
                    
                    clicks = []
                    
                    def on_click(event):
                        clicks.append(pyautogui.position())
                        if len(clicks) == 1:
                            messagebox.showinfo("Region Selection", "Now click at opposite corner.")
                        elif len(clicks) == 2:
                            root.quit()
                    
                    root.bind('<Button-1>', on_click)
                    root.mainloop()
                    root.destroy()
                    
                    if len(clicks) == 2:
                        start_x, start_y = clicks[0]
                        end_x, end_y = clicks[1]
                        
                        x1_var.set(str(min(start_x, end_x)))
                        y1_var.set(str(min(start_y, end_y)))
                        x2_var.set(str(max(start_x, end_x)))
                        y2_var.set(str(max(start_y, end_y)))
                        
                        messagebox.showinfo("Success", f"Region set: ({min(start_x, end_x)}, {min(start_y, end_y)}) to ({max(start_x, end_x)}, {max(start_y, end_y)})")
                
                wait_for_click()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to get region: {str(e)}")
        
        threading.Thread(target=get_region, daemon=True).start()
    
    def get_click_position(self, x_var, y_var):
        """Get mouse click position"""
        messagebox.showinfo("Get Position", "Move mouse to desired position and press SPACE.")
        
        def get_position():
            try:
                if KEYBOARD_AVAILABLE:
                    import keyboard
                    keyboard.wait('space')
                    x, y = pyautogui.position()
                    x_var.set(str(x))
                    y_var.set(str(y))
                    messagebox.showinfo("Success", f"Position captured: ({x}, {y})")
                else:
                    # Fallback method - wait for mouse click
                    messagebox.showinfo("Get Position", "Keyboard module not available. Click at desired position.")
                    
                    import tkinter as tk
                    root = tk.Tk()
                    root.withdraw()
                    root.attributes('-topmost', True)
                    root.attributes('-alpha', 0.1)
                    root.geometry('1x1+0+0')
                    
                    def on_click(event):
                        x, y = pyautogui.position()
                        x_var.set(str(x))
                        y_var.set(str(y))
                        messagebox.showinfo("Success", f"Position captured: ({x}, {y})")
                        root.quit()
                    
                    root.bind('<Button-1>', on_click)
                    root.mainloop()
                    root.destroy()
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to get position: {str(e)}")
        
        threading.Thread(target=get_position, daemon=True).start()
    
    def on_event_select(self, event):
        """Handle event selection"""
        self.refresh_image_list()
    
    def refresh_event_list(self):
        """Refresh the event dropdown"""
        # Store current selection
        current_selection = self.selected_event.get()
        
        # Update dropdown values
        event_names = list(self.events_data.keys())
        self.event_dropdown['values'] = event_names
        
        # Restore selection if it still exists, otherwise select first item
        if current_selection in event_names:
            self.selected_event.set(current_selection)
        elif event_names:
            self.selected_event.set(event_names[0])
        else:
            self.selected_event.set("")
        
        # Force GUI update
        self.root.update_idletasks()
    
    def refresh_image_list(self):
        """Refresh the image listbox"""
        self.image_listbox.delete(0, tk.END)
        
        event_name = self.selected_event.get()
        if event_name and event_name in self.events_data:
            for image_data in self.events_data[event_name]["images"]:
                self.image_listbox.insert(tk.END, image_data["name"])
        # Force GUI update
        self.root.update_idletasks()
    
    def refresh_control_buttons(self):
        """Refresh control buttons for each event"""
        # Clear existing buttons
        for widget in self.control_buttons_frame.winfo_children():
            widget.destroy()
        
        # Create buttons for each event
        for i, event_name in enumerate(self.events_data.keys()):
            is_running = event_name in self.threads and self.threads[event_name].is_alive()
            button_text = f"Stop {event_name}" if is_running else f"Start {event_name}"
            button_color = "#f44336" if is_running else "#4CAF50"
            
            btn = tk.Button(
                self.control_buttons_frame,
                text=button_text,
                command=lambda name=event_name: self.toggle_event(name),
                bg=button_color,
                fg="white",
                width=20
            )
            btn.pack(pady=2, fill=tk.X)
        
        # Force GUI update
        self.root.update_idletasks()
    
    def toggle_event(self, event_name):
        """Start or stop an event"""
        if event_name in self.threads and self.threads[event_name].is_alive():
            self.stop_event(event_name)
        else:
            self.start_event(event_name)
        
        self.refresh_control_buttons()
    
    def start_event(self, event_name):
        """Start running an event"""
        if not self.events_data[event_name]["images"]:
            messagebox.showwarning("Warning", f"Event '{event_name}' has no images configured.")
            return
        
        self.stop_flags[event_name] = False
        self.threads[event_name] = threading.Thread(target=self.run_event, args=(event_name,), daemon=True)
        self.threads[event_name].start()
        self.log_status(f"Started event: {event_name}")
    
    def stop_event(self, event_name):
        """Stop running an event"""
        self.stop_flags[event_name] = True
        self.log_status(f"Stopped event: {event_name}")
    
    def run_event(self, event_name):
        """Main event loop"""
        event_data = self.events_data[event_name]
        
        while not self.stop_flags[event_name]:
            try:
                # Focus target window
                self.focus_window(self.target_window)
                
                # Check each image in the event
                for image_data in event_data["images"]:
                    if self.stop_flags[event_name]:
                        break
                    
                    if self.find_image_and_execute(image_data):
                        self.log_status(f"Found and executed: {image_data['name']} in {event_name}")
                        break  # Found and executed, restart loop
                
                time.sleep(0.1)  # Small delay between cycles
                
            except Exception as e:
                self.log_status(f"Error in event {event_name}: {str(e)}")
                time.sleep(1)  # Longer delay on error
    
    def find_image_and_execute(self, image_data):
        """Find image on screen and execute associated action"""
        try:
            location = pyautogui.locateOnScreen(
                image_data["path"],
                confidence=image_data["confidence"],
                grayscale=True,
                region=image_data.get("region")
            )
            
            if location:
                self.execute_action(image_data["action"])
                return True
                
        except pyautogui.ImageNotFoundException:
            pass  # Image not found, continue
        except Exception as e:
            self.log_status(f"Error finding image {image_data['name']}: {str(e)}")
        
        return False
    
    def execute_action(self, action):
        """Execute the specified action"""
        try:
            action_type = action["type"]
            
            if action_type == "key_press":
                pyautogui.press(action["key"])
                time.sleep(action.get("delay", 0.1))
                
            elif action_type == "key_sequence":
                sequence = action["sequence"].split(",")
                for i in range(0, len(sequence), 2):
                    if i + 1 < len(sequence):
                        key = sequence[i].strip()
                        delay = float(sequence[i + 1].strip())
                        pyautogui.press(key)
                        time.sleep(delay)
                        
            elif action_type == "mouse_click":
                pyautogui.click(action["x"], action["y"])
                time.sleep(action.get("delay", 0.1))
                
            elif action_type == "mouse_sequence":
                sequence = action["sequence"].split(",")
                for i in range(0, len(sequence), 3):
                    if i + 2 < len(sequence):
                        x = int(sequence[i].strip())
                        y = int(sequence[i + 1].strip())
                        delay = float(sequence[i + 2].strip())
                        pyautogui.click(x, y)
                        time.sleep(delay)
                        
            elif action_type == "custom_function":
                self.execute_custom_function(
                    action["function"],
                    action.get("params", "{}"),
                    self.target_window
                )
                
        except Exception as e:
            self.log_status(f"Error executing action: {str(e)}")
    
    def execute_custom_function(self, function_name, params, window):
        """Framework for custom functions - users add their own functions here"""
        try:
            params_dict = json.loads(params) if isinstance(params, str) else params
            self.log_status(f"Custom function '{function_name}' called with params: {params_dict}")
            
            # Users would add their custom functions here:
            if function_name == "collect_reward":
                self.log_status("Executing collect_reward function")
                # Add custom logic here
                
            elif function_name == "battle_sequence":
                self.log_status("Executing battle_sequence function")
                # Add custom logic here
                
            elif function_name == "upgrade_equipment":
                self.log_status("Executing upgrade_equipment function")
                # Add custom logic here
                
            else:
                self.log_status(f"Custom function '{function_name}' not implemented")
                self.log_status("Add your custom function logic in execute_custom_function method")
                
        except Exception as e:
            self.log_status(f"Error in custom function {function_name}: {str(e)}")
    
    def focus_window(self, window_title):
        """Focus on the target window"""
        try:
            windows = gw.getWindowsWithTitle(window_title)
            if windows:
                window = windows[0]
                if window.isMinimized:
                    window.restore()
                window.activate()
                time.sleep(0.1)
            else:
                self.log_status(f"Window '{window_title}' not found")
        except Exception as e:
            self.log_status(f"Error focusing window: {str(e)}")
    
    def take_screenshot(self):
        """Take a screenshot"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            self.log_status(f"Screenshot saved: {filename}")
            messagebox.showinfo("Screenshot", f"Screenshot saved as {filename}")
        except Exception as e:
            self.log_status(f"Error taking screenshot: {str(e)}")
            messagebox.showerror("Error", f"Failed to take screenshot: {str(e)}")
    
    def get_mouse_position(self):
        """Get current mouse position"""
        messagebox.showinfo("Mouse Position", "Move mouse to desired position and press SPACE to capture coordinates.")
        
        def capture_position():
            try:
                if KEYBOARD_AVAILABLE:
                    import keyboard
                    keyboard.wait('space')
                    x, y = pyautogui.position()
                    self.log_status(f"Mouse position captured: ({x}, {y})")
                    messagebox.showinfo("Position Captured", f"Mouse position: ({x}, {y})")
                else:
                    # Fallback method - wait for mouse click
                    messagebox.showinfo("Mouse Position", "Keyboard module not available. Click at desired position.")
                    
                    import tkinter as tk
                    root = tk.Tk()
                    root.withdraw()
                    root.attributes('-topmost', True)
                    root.attributes('-alpha', 0.1)
                    root.geometry('1x1+0+0')
                    
                    def on_click(event):
                        x, y = pyautogui.position()
                        self.log_status(f"Mouse position captured: ({x}, {y})")
                        messagebox.showinfo("Position Captured", f"Mouse position: ({x}, {y})")
                        root.quit()
                    
                    root.bind('<Button-1>', on_click)
                    root.mainloop()
                    root.destroy()
                    
            except Exception as e:
                self.log_status(f"Error capturing mouse position: {str(e)}")
        
        threading.Thread(target=capture_position, daemon=True).start()
    
    def test_image_recognition(self):
        """Test image recognition"""
        filename = filedialog.askopenfilename(
            title="Select Image to Test",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*")]
        )
        
        if filename:
            confidence = simpledialog.askfloat("Confidence", "Enter confidence level (0.1-1.0):", initialvalue=0.8, minvalue=0.1, maxvalue=1.0)
            if confidence:
                try:
                    location = pyautogui.locateOnScreen(filename, confidence=confidence, grayscale=True)
                    if location:
                        center = pyautogui.center(location)
                        self.log_status(f"Image found at: {location}, center: {center}")
                        messagebox.showinfo("Image Found", f"Image found at: {location}\nCenter: {center}")
                    else:
                        self.log_status("Image not found on screen")
                        messagebox.showinfo("Image Not Found", "Image not found on screen")
                except Exception as e:
                    self.log_status(f"Error testing image: {str(e)}")
                    messagebox.showerror("Error", f"Error testing image: {str(e)}")
    
    def log_status(self, message):
        """Log status message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.status_text.insert(tk.END, log_message)
        self.status_text.see(tk.END)
        
        # Keep only last 1000 lines
        lines = self.status_text.get("1.0", tk.END).split("\n")
        if len(lines) > 1000:
            self.status_text.delete("1.0", f"{len(lines) - 1000}.0")
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.events_data = data.get("events", {})
                    self.target_window = data.get("target_window", "LDPlayer")
                    
                    # Initialize stop flags
                    for event_name in self.events_data.keys():
                        self.stop_flags[event_name] = False
                        
                self.log_status(f"Configuration loaded from {self.config_file}")
            else:
                self.log_status("No existing configuration found, starting fresh")
        except Exception as e:
            self.log_status(f"Error loading configuration: {str(e)}")
            messagebox.showerror("Error", f"Failed to load configuration: {str(e)}")
    
    def save_config(self):
        """Save configuration to file"""
        try:
            data = {
                "events": self.events_data,
                "target_window": self.target_window
            }
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
            self.log_status(f"Configuration saved to {self.config_file}")
        except Exception as e:
            self.log_status(f"Error saving configuration: {str(e)}")
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
    
    def new_config(self):
        """Create new configuration"""
        if messagebox.askyesno("New Configuration", "This will clear all current events. Continue?"):
            # Stop all running events
            for event_name in list(self.threads.keys()):
                if self.threads[event_name].is_alive():
                    self.stop_event(event_name)
            
            self.events_data.clear()
            self.stop_flags.clear()
            self.threads.clear()
            
            self.refresh_event_list()
            self.refresh_image_list()
            self.refresh_control_buttons()
            self.log_status("New configuration created")
    
    def open_config(self):
        """Open configuration file"""
        filename = filedialog.askopenfilename(
            title="Open Configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                
                # Stop all running events
                for event_name in list(self.threads.keys()):
                    if self.threads[event_name].is_alive():
                        self.stop_event(event_name)
                
                self.events_data = data.get("events", {})
                self.target_window = data.get("target_window", "LDPlayer")
                
                # Initialize stop flags
                self.stop_flags.clear()
                self.threads.clear()
                for event_name in self.events_data.keys():
                    self.stop_flags[event_name] = False
                
                self.refresh_event_list()
                self.refresh_image_list()
                self.refresh_control_buttons()
                self.log_status(f"Configuration loaded from {filename}")
                
            except Exception as e:
                self.log_status(f"Error opening configuration: {str(e)}")
                messagebox.showerror("Error", f"Failed to open configuration: {str(e)}")
    
    def export_config(self):
        """Export configuration to file"""
        filename = filedialog.asksaveasfilename(
            title="Export Configuration",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                data = {
                    "events": self.events_data,
                    "target_window": self.target_window
                }
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                self.log_status(f"Configuration exported to {filename}")
                messagebox.showinfo("Export Complete", f"Configuration exported to {filename}")
            except Exception as e:
                self.log_status(f"Error exporting configuration: {str(e)}")
                messagebox.showerror("Error", f"Failed to export configuration: {str(e)}")
    
    def import_config(self):
        """Import configuration from file"""
        filename = filedialog.askopenfilename(
            title="Import Configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                
                # Merge with existing configuration
                imported_events = data.get("events", {})
                for event_name, event_data in imported_events.items():
                    if event_name in self.events_data:
                        if messagebox.askyesno("Duplicate Event", f"Event '{event_name}' already exists. Replace it?"):
                            self.events_data[event_name] = event_data
                            self.stop_flags[event_name] = False
                    else:
                        self.events_data[event_name] = event_data
                        self.stop_flags[event_name] = False
                
                self.refresh_event_list()
                self.refresh_image_list()
                self.refresh_control_buttons()
                self.save_config()
                self.log_status(f"Configuration imported from {filename}")
                messagebox.showinfo("Import Complete", f"Configuration imported from {filename}")
                
            except Exception as e:
                self.log_status(f"Error importing configuration: {str(e)}")
                messagebox.showerror("Error", f"Failed to import configuration: {str(e)}")
    
    def window_settings(self):
        """Configure target window settings"""
        new_window = simpledialog.askstring("Window Settings", f"Enter target window title:", initialvalue=self.target_window)
        if new_window:
            self.target_window = new_window
            self.save_config()
            self.log_status(f"Target window set to: {self.target_window}")
    
    def list_windows(self):
        """List all available windows"""
        try:
            windows = gw.getAllWindows()
            window_list = []
            for window in windows:
                if window.title.strip():
                    window_list.append(f"'{window.title}' - Size: {window.width}x{window.height}")
            
            if window_list:
                window_text = "\n".join(window_list[:20])  # Show first 20 windows
                if len(window_list) > 20:
                    window_text += f"\n... and {len(window_list) - 20} more windows"
                messagebox.showinfo("Available Windows", window_text)
            else:
                messagebox.showinfo("Available Windows", "No windows found")
                
        except Exception as e:
            self.log_status(f"Error listing windows: {str(e)}")
            messagebox.showerror("Error", f"Failed to list windows: {str(e)}")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """PyAutoGUI Game Automation Tool
Version 1.0

A comprehensive tool for automating game interactions using image recognition and PyAutoGUI.

Features:
- Event-based automation
- Image recognition with confidence levels
- Multiple action types (key press, mouse click, sequences, custom functions)
- Region-based searching
- Multi-threading support
- Configuration save/load

Created for Shadow Fight 3 automation and general game automation tasks."""
        
        messagebox.showinfo("About", about_text)
    
    def show_help(self):
        """Show help dialog"""
        help_text = """How to use the Game Automation Tool:

1. CREATE EVENT: Click 'Add Event' to create a new automation event

2. ADD IMAGES: Select an event and click 'Add Image' to add images to detect

3. CONFIGURE ACTIONS: For each image, configure what action to perform when found:
   - Key Press: Press a single key
   - Key Sequence: Press multiple keys with delays
   - Mouse Click: Click at specific coordinates
   - Mouse Sequence: Click multiple locations
   - Custom Function: Execute custom code

4. SET REGIONS: Optionally set search regions to improve performance

5. START AUTOMATION: Click the event's Start button to begin automation

6. STOP AUTOMATION: Click the Stop button to halt automation

TIPS:
- Use screenshots to capture images for detection
- Set appropriate confidence levels (0.8 is usually good)
- Use regions to limit search areas and improve speed
- Test image recognition before running automation

KEYBOARD SHORTCUTS:
- SPACE: Capture mouse position or region selection"""
        
        messagebox.showinfo("Help", help_text)
    
    def on_closing(self):
        """Handle application closing"""
        # Stop all running events
        for event_name in list(self.threads.keys()):
            if self.threads[event_name].is_alive():
                self.stop_event(event_name)
        
        # Wait a moment for threads to stop
        time.sleep(0.5)
        
        # Save configuration
        self.save_config()
        
        # Close application
        self.root.destroy()

def main():
    """Main function to run the application"""
    # Set PyAutoGUI settings
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
    
    # Create and run the application
    root = tk.Tk()
    app = GameAutomationTool(root)
    root.mainloop()

if __name__ == "__main__":
    main()