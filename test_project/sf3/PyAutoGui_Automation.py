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
import subprocess
import sys

class SF3AutomationTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Shadow Fight 3 Automation Tool")
        self.root.geometry("1200x800")
        self.root.configure(bg="#2b2b2b")
        
        # Data storage
        self.config_file = "sf3_automation_config.json"
        self.events_data = {}
        self.running_threads = {}
        self.stop_flags = {}
        
        # Load existing config
        self.load_config()
        
        # Create GUI
        self.create_widgets()
        
        # Window settings
        self.window_title = "LDPlayer"
        
        # Disable pyautogui failsafe
        pyautogui.FAILSAFE = False
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Event management
        left_panel = ttk.LabelFrame(main_frame, text="Event Management", padding="10")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Event list
        ttk.Label(left_panel, text="Events:").pack(anchor=tk.W)
        
        event_frame = ttk.Frame(left_panel)
        event_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.event_listbox = tk.Listbox(event_frame, height=8, bg="#404040", fg="white")
        self.event_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.event_listbox.bind('<<ListboxSelect>>', self.on_event_select)
        
        event_scrollbar = ttk.Scrollbar(event_frame, orient=tk.VERTICAL, command=self.event_listbox.yview)
        event_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.event_listbox.config(yscrollcommand=event_scrollbar.set)
        
        # Event buttons
        event_btn_frame = ttk.Frame(left_panel)
        event_btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(event_btn_frame, text="Add Event", command=self.add_event).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(event_btn_frame, text="Delete Event", command=self.delete_event).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(event_btn_frame, text="Rename Event", command=self.rename_event).pack(side=tk.LEFT)
        
        # Event details
        details_frame = ttk.LabelFrame(left_panel, text="Event Details", padding="10")
        details_frame.pack(fill=tk.BOTH, expand=True)
        
        # Image list for selected event
        ttk.Label(details_frame, text="Images:").pack(anchor=tk.W)
        
        image_frame = ttk.Frame(details_frame)
        image_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.image_listbox = tk.Listbox(image_frame, height=8, bg="#404040", fg="white")
        self.image_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.image_listbox.bind('<<ListboxSelect>>', self.on_image_select)
        
        image_scrollbar = ttk.Scrollbar(image_frame, orient=tk.VERTICAL, command=self.image_listbox.yview)
        image_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.image_listbox.config(yscrollcommand=image_scrollbar.set)
        
        # Image buttons
        image_btn_frame = ttk.Frame(details_frame)
        image_btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(image_btn_frame, text="Add Image", command=self.add_image).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(image_btn_frame, text="Delete Image", command=self.delete_image).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(image_btn_frame, text="Edit Image", command=self.edit_image).pack(side=tk.LEFT)
        
        # Right panel - Image configuration
        right_panel = ttk.LabelFrame(main_frame, text="Image Configuration", padding="10")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Image path
        ttk.Label(right_panel, text="Image Path:").pack(anchor=tk.W)
        self.image_path_var = tk.StringVar()
        path_frame = ttk.Frame(right_panel)
        path_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Entry(path_frame, textvariable=self.image_path_var, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(path_frame, text="Browse", command=self.browse_image).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Confidence
        ttk.Label(right_panel, text="Confidence:").pack(anchor=tk.W)
        self.confidence_var = tk.DoubleVar(value=0.8)
        confidence_frame = ttk.Frame(right_panel)
        confidence_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Scale(confidence_frame, from_=0.1, to=1.0, variable=self.confidence_var, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(confidence_frame, textvariable=self.confidence_var).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Region
        ttk.Label(right_panel, text="Region (x1, y1, x2, y2):").pack(anchor=tk.W)
        region_frame = ttk.Frame(right_panel)
        region_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.region_vars = [tk.IntVar() for _ in range(4)]
        for i, var in enumerate(self.region_vars):
            ttk.Entry(region_frame, textvariable=var, width=8).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(region_frame, text="Get Region", command=self.get_region).pack(side=tk.LEFT)
        
        # Action Type
        ttk.Label(right_panel, text="Action Type:").pack(anchor=tk.W)
        self.action_type_var = tk.StringVar(value="key_press")
        action_combo = ttk.Combobox(right_panel, textvariable=self.action_type_var, 
                                   values=["key_press", "key_sequence", "mouse_click", "mouse_sequence", "custom_function"])
        action_combo.pack(fill=tk.X, pady=(0, 10))
        action_combo.bind('<<ComboboxSelected>>', self.on_action_type_change)
        
        # Action configuration frame
        self.action_config_frame = ttk.LabelFrame(right_panel, text="Action Configuration", padding="10")
        self.action_config_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Default action config
        self.create_key_press_config()
        
        # Save button
        ttk.Button(right_panel, text="Save Image Configuration", command=self.save_image_config).pack(fill=tk.X, pady=(0, 10))
        
        # Bottom panel - Control buttons
        bottom_panel = ttk.Frame(main_frame)
        bottom_panel.pack(fill=tk.X, pady=(10, 0))
        
        control_frame = ttk.LabelFrame(bottom_panel, text="Control", padding="10")
        control_frame.pack(fill=tk.X)
        
        # Event control buttons
        self.create_event_control_buttons(control_frame)
        
        # Utility buttons
        utility_frame = ttk.Frame(control_frame)
        utility_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(utility_frame, text="Save Config", command=self.save_config).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(utility_frame, text="Load Config", command=self.load_config).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(utility_frame, text="Export Config", command=self.export_config).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(utility_frame, text="Import Config", command=self.import_config).pack(side=tk.LEFT)
        
        # Populate event list
        self.populate_event_list()
        
    def create_event_control_buttons(self, parent):
        """Create start/stop buttons for each event"""
        self.control_buttons_frame = ttk.Frame(parent)
        self.control_buttons_frame.pack(fill=tk.X)
        
        # Will be populated when events are loaded
        self.control_buttons = {}
        
    def update_control_buttons(self):
        """Update control buttons based on current events"""
        # Clear existing buttons
        for widget in self.control_buttons_frame.winfo_children():
            widget.destroy()
        
        self.control_buttons = {}
        
        # Create buttons for each event
        for event_name in self.events_data.keys():
            btn = ttk.Button(self.control_buttons_frame, text=f"Start {event_name}", 
                           command=lambda name=event_name: self.toggle_event(name))
            btn.pack(side=tk.LEFT, padx=(0, 5))
            self.control_buttons[event_name] = btn
            
    def create_key_press_config(self):
        """Create key press configuration widgets"""
        self.clear_action_config()
        
        ttk.Label(self.action_config_frame, text="Key:").pack(anchor=tk.W)
        self.key_var = tk.StringVar()
        ttk.Entry(self.action_config_frame, textvariable=self.key_var).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(self.action_config_frame, text="Delay (seconds):").pack(anchor=tk.W)
        self.delay_var = tk.DoubleVar(value=0.1)
        ttk.Entry(self.action_config_frame, textvariable=self.delay_var).pack(fill=tk.X)
        
    def create_key_sequence_config(self):
        """Create key sequence configuration widgets"""
        self.clear_action_config()
        
        ttk.Label(self.action_config_frame, text="Key Sequence (format: key1,delay1,key2,delay2):").pack(anchor=tk.W)
        self.sequence_var = tk.StringVar()
        ttk.Entry(self.action_config_frame, textvariable=self.sequence_var).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(self.action_config_frame, text="Example: space,1,c,2,e,0.5").pack(anchor=tk.W)
        
    def create_mouse_click_config(self):
        """Create mouse click configuration widgets"""
        self.clear_action_config()
        
        ttk.Label(self.action_config_frame, text="Click Position (x, y):").pack(anchor=tk.W)
        click_frame = ttk.Frame(self.action_config_frame)
        click_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.click_x_var = tk.IntVar()
        self.click_y_var = tk.IntVar()
        
        ttk.Entry(click_frame, textvariable=self.click_x_var, width=10).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(click_frame, textvariable=self.click_y_var, width=10).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(click_frame, text="Get Position", command=self.get_mouse_position).pack(side=tk.LEFT)
        
        ttk.Label(self.action_config_frame, text="Delay (seconds):").pack(anchor=tk.W)
        self.delay_var = tk.DoubleVar(value=0.1)
        ttk.Entry(self.action_config_frame, textvariable=self.delay_var).pack(fill=tk.X)
        
    def create_mouse_sequence_config(self):
        """Create mouse sequence configuration widgets"""
        self.clear_action_config()
        
        ttk.Label(self.action_config_frame, text="Mouse Sequence (format: x1,y1,delay1,x2,y2,delay2):").pack(anchor=tk.W)
        self.mouse_sequence_var = tk.StringVar()
        ttk.Entry(self.action_config_frame, textvariable=self.mouse_sequence_var).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(self.action_config_frame, text="Example: 100,200,1,150,250,2").pack(anchor=tk.W)
        
    def create_custom_function_config(self):
        """Create custom function configuration widgets"""
        self.clear_action_config()
        
        ttk.Label(self.action_config_frame, text="Function Name:").pack(anchor=tk.W)
        self.function_name_var = tk.StringVar()
        ttk.Entry(self.action_config_frame, textvariable=self.function_name_var).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(self.action_config_frame, text="Parameters (JSON format):").pack(anchor=tk.W)
        self.function_params_var = tk.StringVar()
        ttk.Entry(self.action_config_frame, textvariable=self.function_params_var).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(self.action_config_frame, text="Example: {\"param1\": \"value1\", \"param2\": 123}").pack(anchor=tk.W)
        
    def clear_action_config(self):
        """Clear all widgets in action config frame"""
        for widget in self.action_config_frame.winfo_children():
            widget.destroy()
            
    def on_action_type_change(self, event=None):
        """Handle action type change"""
        action_type = self.action_type_var.get()
        
        if action_type == "key_press":
            self.create_key_press_config()
        elif action_type == "key_sequence":
            self.create_key_sequence_config()
        elif action_type == "mouse_click":
            self.create_mouse_click_config()
        elif action_type == "mouse_sequence":
            self.create_mouse_sequence_config()
        elif action_type == "custom_function":
            self.create_custom_function_config()
            
    def get_region(self):
        """Get screen region using mouse selection"""
        messagebox.showinfo("Region Selection", 
                          "Click OK, then click and drag to select the region on screen.\n"
                          "Press ESC to cancel.")
        
        self.root.withdraw()  # Hide main window
        
        try:
            # Simple region selection using messagebox
            region_str = simpledialog.askstring("Region Input", 
                                               "Enter region coordinates (x1,y1,x2,y2):")
            if region_str:
                coords = [int(x.strip()) for x in region_str.split(',')]
                if len(coords) == 4:
                    for i, var in enumerate(self.region_vars):
                        var.set(coords[i])
        except:
            pass
        finally:
            self.root.deiconify()  # Show main window
            
    def get_mouse_position(self):
        """Get current mouse position"""
        messagebox.showinfo("Mouse Position", 
                          "Click OK, then move mouse to desired position and press SPACE.")
        
        def get_pos():
            import keyboard
            keyboard.wait('space')
            x, y = pyautogui.position()
            self.click_x_var.set(x)
            self.click_y_var.set(y)
            
        threading.Thread(target=get_pos, daemon=True).start()
        
    def browse_image(self):
        """Browse for image file"""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if file_path:
            self.image_path_var.set(file_path)
            
    def add_event(self):
        """Add new event"""
        event_name = simpledialog.askstring("Add Event", "Enter event name:")
        if event_name and event_name not in self.events_data:
            self.events_data[event_name] = {"images": [], "enabled": True}
            self.populate_event_list()
            self.update_control_buttons()
            self.save_config()
            
    def delete_event(self):
        """Delete selected event"""
        selection = self.event_listbox.curselection()
        if selection:
            event_name = self.event_listbox.get(selection[0])
            if messagebox.askyesno("Delete Event", f"Delete event '{event_name}'?"):
                del self.events_data[event_name]
                self.populate_event_list()
                self.update_control_buttons()
                self.save_config()
                
    def rename_event(self):
        """Rename selected event"""
        selection = self.event_listbox.curselection()
        if selection:
            old_name = self.event_listbox.get(selection[0])
            new_name = simpledialog.askstring("Rename Event", "Enter new name:", initialvalue=old_name)
            if new_name and new_name != old_name and new_name not in self.events_data:
                self.events_data[new_name] = self.events_data.pop(old_name)
                self.populate_event_list()
                self.update_control_buttons()
                self.save_config()
                
    def add_image(self):
        """Add new image to selected event"""
        selection = self.event_listbox.curselection()
        if selection:
            event_name = self.event_listbox.get(selection[0])
            image_name = simpledialog.askstring("Add Image", "Enter image name:")
            if image_name:
                default_image = {
                    "name": image_name,
                    "path": "",
                    "confidence": 0.8,
                    "region": None,
                    "action": {
                        "type": "key_press",
                        "key": "space",
                        "delay": 0.1
                    }
                }
                self.events_data[event_name]["images"].append(default_image)
                self.populate_image_list(event_name)
                self.save_config()
                
    def delete_image(self):
        """Delete selected image"""
        event_selection = self.event_listbox.curselection()
        image_selection = self.image_listbox.curselection()
        
        if event_selection and image_selection:
            event_name = self.event_listbox.get(event_selection[0])
            image_index = image_selection[0]
            
            if messagebox.askyesno("Delete Image", "Delete selected image?"):
                del self.events_data[event_name]["images"][image_index]
                self.populate_image_list(event_name)
                self.save_config()
                
    def edit_image(self):
        """Edit selected image"""
        event_selection = self.event_listbox.curselection()
        image_selection = self.image_listbox.curselection()
        
        if event_selection and image_selection:
            event_name = self.event_listbox.get(event_selection[0])
            image_index = image_selection[0]
            image_data = self.events_data[event_name]["images"][image_index]
            
            # Load image data into form
            self.load_image_data(image_data)
            
    def save_image_config(self):
        """Save current image configuration"""
        event_selection = self.event_listbox.curselection()
        image_selection = self.image_listbox.curselection()
        
        if event_selection and image_selection:
            event_name = self.event_listbox.get(event_selection[0])
            image_index = image_selection[0]
            
            # Get current form data
            image_data = self.get_image_data_from_form()
            
            # Update the image data
            self.events_data[event_name]["images"][image_index] = image_data
            
            # Update display
            self.populate_image_list(event_name)
            self.save_config()
            
            messagebox.showinfo("Success", "Image configuration saved!")
            
    def get_image_data_from_form(self):
        """Get image data from current form"""
        # Get region
        region = None
        if any(var.get() for var in self.region_vars):
            region = [var.get() for var in self.region_vars]
            
        # Get action data based on type
        action_type = self.action_type_var.get()
        action_data = {"type": action_type}
        
        if action_type == "key_press":
            action_data.update({
                "key": self.key_var.get(),
                "delay": self.delay_var.get()
            })
        elif action_type == "key_sequence":
            action_data["sequence"] = self.sequence_var.get()
        elif action_type == "mouse_click":
            action_data.update({
                "x": self.click_x_var.get(),
                "y": self.click_y_var.get(),
                "delay": self.delay_var.get()
            })
        elif action_type == "mouse_sequence":
            action_data["sequence"] = self.mouse_sequence_var.get()
        elif action_type == "custom_function":
            action_data.update({
                "function": self.function_name_var.get(),
                "params": self.function_params_var.get()
            })
            
        return {
            "name": "Current Image",  # This should be set properly
            "path": self.image_path_var.get(),
            "confidence": self.confidence_var.get(),
            "region": region,
            "action": action_data
        }
        
    def load_image_data(self, image_data):
        """Load image data into form"""
        self.image_path_var.set(image_data.get("path", ""))
        self.confidence_var.set(image_data.get("confidence", 0.8))
        
        # Load region
        region = image_data.get("region")
        if region:
            for i, var in enumerate(self.region_vars):
                var.set(region[i] if i < len(region) else 0)
        else:
            for var in self.region_vars:
                var.set(0)
                
        # Load action data
        action = image_data.get("action", {})
        action_type = action.get("type", "key_press")
        self.action_type_var.set(action_type)
        
        # Trigger action type change to create appropriate widgets
        self.on_action_type_change()
        
        # Load action-specific data
        if action_type == "key_press":
            self.key_var.set(action.get("key", ""))
            self.delay_var.set(action.get("delay", 0.1))
        elif action_type == "key_sequence":
            self.sequence_var.set(action.get("sequence", ""))
        elif action_type == "mouse_click":
            self.click_x_var.set(action.get("x", 0))
            self.click_y_var.set(action.get("y", 0))
            self.delay_var.set(action.get("delay", 0.1))
        elif action_type == "mouse_sequence":
            self.mouse_sequence_var.set(action.get("sequence", ""))
        elif action_type == "custom_function":
            self.function_name_var.set(action.get("function", ""))
            self.function_params_var.set(action.get("params", ""))
            
    def on_event_select(self, event):
        """Handle event selection"""
        selection = self.event_listbox.curselection()
        if selection:
            event_name = self.event_listbox.get(selection[0])
            self.populate_image_list(event_name)
            
    def on_image_select(self, event):
        """Handle image selection"""
        event_selection = self.event_listbox.curselection()
        image_selection = self.image_listbox.curselection()
        
        if event_selection and image_selection:
            event_name = self.event_listbox.get(event_selection[0])
            image_index = image_selection[0]
            image_data = self.events_data[event_name]["images"][image_index]
            
            # Load image data into form
            self.load_image_data(image_data)
            
    def populate_event_list(self):
        """Populate event listbox"""
        self.event_listbox.delete(0, tk.END)
        for event_name in self.events_data.keys():
            self.event_listbox.insert(tk.END, event_name)
            
    def populate_image_list(self, event_name):
        """Populate image listbox for given event"""
        self.image_listbox.delete(0, tk.END)
        if event_name in self.events_data:
            for image in self.events_data[event_name]["images"]:
                self.image_listbox.insert(tk.END, image["name"])
                
    def toggle_event(self, event_name):
        """Toggle event execution"""
        if event_name in self.running_threads and self.running_threads[event_name].is_alive():
            # Stop the event
            self.stop_flags[event_name] = True
            self.running_threads[event_name].join()
            self.control_buttons[event_name].config(text=f"Start {event_name}")
        else:
            # Start the event
            self.stop_flags[event_name] = False
            thread = threading.Thread(target=self.run_event, args=(event_name,), daemon=True)
            thread.start()
            self.running_threads[event_name] = thread
            self.control_buttons[event_name].config(text=f"Stop {event_name}")
            
    def run_event(self, event_name):
        """Run event automation"""
        if event_name not in self.events_data:
            return
            
        event_data = self.events_data[event_name]
        window = self.focus_window(self.window_title)
        
        if not window:
            print(f"Window '{self.window_title}' not found.")
            return
            
        try:
            while not self.stop_flags.get(event_name, False):
                self.focus_window(self.window_title)
                
                for image_data in event_data["images"]:
                    if self.stop_flags.get(event_name, False):
                        break
                        
                    if self.find_image_and_execute(image_data, window):
                        break  # Found and executed, move to next cycle
                        
                time.sleep(0.1)  # Small delay between cycles
                
        except KeyboardInterrupt:
            print(f"Event {event_name} stopped by user.")
        except Exception as e:
            print(f"Error in event {event_name}: {e}")
            
    def find_image_and_execute(self, image_data, window):
        """Find image and execute associated action"""
        if not image_data["path"] or not os.path.exists(image_data["path"]):
            return False
            
        try:
            # Convert region format if needed
            region = image_data.get("region")
            if region and len(region) == 4:
                x1, y1, x2, y2 = region
                region = (x1, y1, x2 - x1, y2 - y1)
                
            # Find image
            location = pyautogui.locateOnScreen(
                image_data["path"],
                confidence=image_data.get("confidence", 0.8),
                grayscale=True,
                region=region
            )
            
            if location:
                # Execute action
                self.execute_action(image_data["action"], window)
                return True
                
        except Exception as e:
            print(f"Error finding image {image_data['name']}: {e}")
            
        return False
        
    def execute_action(self, action_data, window):
        """Execute the specified action"""
        action_type = action_data.get("type", "key_press")
        
        if action_type == "key_press":
            key = action_data.get("key", "space")
            delay = action_data.get("delay", 0.1)
            window.activate()
            pyautogui.press(key)
            time.sleep(delay)
            
        elif action_type == "key_sequence":
            sequence = action_data.get("sequence", "")
            parts = sequence.split(',')
            window.activate()
            for i in range(0, len(parts), 2):
                if i + 1 < len(parts):
                    key = parts[i].strip()
                    delay = float(parts[i + 1].strip())
                    pyautogui.press(key)
                    time.sleep(delay)
                    
        elif action_type == "mouse_click":
            x = action_data.get("x", 0)
            y = action_data.get("y", 0)
            delay = action_data.get("delay", 0.1)
            window.activate()
            pyautogui.click(x, y)
            time.sleep(delay)
            
        elif action_type == "mouse_sequence":
            sequence = action_data.get("sequence", "")
            parts = sequence.split(',')
            window.activate()
            for i in range(0, len(parts), 3):
                if i + 2 < len(parts):
                    x = int(parts[i].strip())
                    y = int(parts[i + 1].strip())
                    delay = float(parts[i + 2].strip())
                    pyautogui.click(x, y)
                    time.sleep(delay)
                    
        elif action_type == "custom_function":
            function_name = action_data.get("function", "")
            params = action_data.get("params", "{}")
            
            # Execute custom function
            try:
                import json
                params_dict = json.loads(params)
                self.execute_custom_function(function_name, params_dict, window)
            except Exception as e:
                print(f"Error executing custom function: {e}")
                
    def execute_custom_function(self, function_name, params, window):
        """Execute custom function"""
        # Add your custom functions here
        if function_name == "collect_reward":
            self.collect_reward_function(params, window)
        elif function_name == "battle_sequence":
            self.battle_sequence_function(params, window)
        elif function_name == "upgrade_equipment":
            self.upgrade_equipment_function(params, window)
        else:
            print(f"Unknown custom function: {function_name}")
            
    def collect_reward_function(self, params, window):
        """Custom function to collect rewards"""
        window.activate()
        time.sleep(0.5)
        
        # Example reward collection sequence
        positions = params.get("positions", [[500, 300], [600, 400]])
        delay = params.get("delay", 1.0)
        
        for pos in positions:
            pyautogui.click(pos[0], pos[1])
            time.sleep(delay)
            
    def battle_sequence_function(self, params, window):
        """Custom function for battle sequences"""
        window.activate()
        time.sleep(0.5)
        
        # Example battle sequence
        actions = params.get("actions", ["space", "c", "e"])
        delay = params.get("delay", 0.5)
        
        for action in actions:
            pyautogui.press(action)
            time.sleep(delay)
            
    def upgrade_equipment_function(self, params, window):
        """Custom function for equipment upgrade"""
        window.activate()
        time.sleep(0.5)
        
        # Example upgrade sequence
        upgrade_button = params.get("upgrade_button", [700, 500])
        confirm_button = params.get("confirm_button", [800, 600])
        
        pyautogui.click(upgrade_button[0], upgrade_button[1])
        time.sleep(1.0)
        pyautogui.click(confirm_button[0], confirm_button[1])
        time.sleep(2.0)
        
    def focus_window(self, window_title):
        """Focus on specific window"""
        try:
            windows = gw.getWindowsWithTitle(window_title)
            if windows:
                window = windows[0]
                if window.isMinimized:
                    window.restore()
                window.activate()
                time.sleep(0.2)
                return window
        except Exception as e:
            print(f"Error focusing window: {e}")
        return None
        
    def save_config(self):
        """Save configuration to JSON file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.events_data, f, indent=2)
            print(f"Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"Error saving config: {e}")
            messagebox.showerror("Error", f"Failed to save configuration: {e}")
            
    def load_config(self):
        """Load configuration from JSON file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.events_data = json.load(f)
                print(f"Configuration loaded from {self.config_file}")
            else:
                # Create default configuration
                self.events_data = {
                    "Daily_Rewards": {
                        "enabled": True,
                        "images": [
                            {
                                "name": "Collect_Button",
                                "path": "",
                                "confidence": 0.8,
                                "region": None,
                                "action": {
                                    "type": "mouse_click",
                                    "x": 500,
                                    "y": 300,
                                    "delay": 1.0
                                }
                            }
                        ]
                    },
                    "Battle_Automation": {
                        "enabled": True,
                        "images": [
                            {
                                "name": "Fight_Button",
                                "path": "",
                                "confidence": 0.8,
                                "region": None,
                                "action": {
                                    "type": "key_press",
                                    "key": "space",
                                    "delay": 0.5
                                }
                            }
                        ]
                    }
                }
        except Exception as e:
            print(f"Error loading config: {e}")
            self.events_data = {}
            
    def export_config(self):
        """Export configuration to file"""
        file_path = filedialog.asksaveasfilename(
            title="Export Configuration",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.events_data, f, indent=2)
                messagebox.showinfo("Success", f"Configuration exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export configuration: {e}")
                
    def import_config(self):
        """Import configuration from file"""
        file_path = filedialog.askopenfilename(
            title="Import Configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    imported_data = json.load(f)
                    
                # Merge with existing data
                self.events_data.update(imported_data)
                
                # Update GUI
                self.populate_event_list()
                self.update_control_buttons()
                self.save_config()
                
                messagebox.showinfo("Success", f"Configuration imported from {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import configuration: {e}")
                
    def create_screenshot_tool(self):
        """Create a simple screenshot tool for getting regions"""
        screenshot_window = tk.Toplevel(self.root)
        screenshot_window.title("Screenshot Tool")
        screenshot_window.geometry("400x300")
        
        ttk.Label(screenshot_window, text="Screenshot Tool", font=("Arial", 16)).pack(pady=10)
        
        ttk.Button(screenshot_window, text="Take Screenshot", 
                  command=self.take_screenshot).pack(pady=5)
        
        ttk.Button(screenshot_window, text="Select Region", 
                  command=self.select_region_tool).pack(pady=5)
        
        ttk.Button(screenshot_window, text="Get Current Mouse Position", 
                  command=self.get_current_mouse_pos).pack(pady=5)
        
    def take_screenshot(self):
        """Take a screenshot of the current screen"""
        try:
            screenshot = pyautogui.screenshot()
            
            # Save screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            
            # Create screenshots directory if it doesn't exist
            screenshots_dir = Path("screenshots")
            screenshots_dir.mkdir(exist_ok=True)
            
            filepath = screenshots_dir / filename
            screenshot.save(filepath)
            
            messagebox.showinfo("Screenshot", f"Screenshot saved as {filepath}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to take screenshot: {e}")
            
    def select_region_tool(self):
        """Tool to select region on screen"""
        messagebox.showinfo("Region Selection", 
                          "This feature requires additional implementation.\n"
                          "For now, use the manual coordinate input method.")
        
    def get_current_mouse_pos(self):
        """Get and display current mouse position"""
        x, y = pyautogui.position()
        messagebox.showinfo("Mouse Position", f"Current position: ({x}, {y})")
        
    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Config", command=self.new_config)
        file_menu.add_command(label="Open Config", command=self.load_config)
        file_menu.add_command(label="Save Config", command=self.save_config)
        file_menu.add_separator()
        file_menu.add_command(label="Export Config", command=self.export_config)
        file_menu.add_command(label="Import Config", command=self.import_config)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Screenshot Tool", command=self.create_screenshot_tool)
        tools_menu.add_command(label="Test Image Recognition", command=self.test_image_recognition)
        tools_menu.add_command(label="Window Settings", command=self.window_settings)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Help", command=self.show_help)
        
    def new_config(self):
        """Create new configuration"""
        if messagebox.askyesno("New Config", "This will clear all current events. Continue?"):
            self.events_data = {}
            self.populate_event_list()
            self.update_control_buttons()
            self.save_config()
            
    def test_image_recognition(self):
        """Test image recognition functionality"""
        file_path = filedialog.askopenfilename(
            title="Select Image to Test",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        
        if file_path:
            try:
                confidence = simpledialog.askfloat("Confidence", "Enter confidence level (0.1-1.0):", 
                                                 initialvalue=0.8, minvalue=0.1, maxvalue=1.0)
                if confidence:
                    location = pyautogui.locateOnScreen(file_path, confidence=confidence)
                    if location:
                        messagebox.showinfo("Test Result", 
                                          f"Image found at: {location}\n"
                                          f"Center: {pyautogui.center(location)}")
                    else:
                        messagebox.showwarning("Test Result", "Image not found on screen")
            except Exception as e:
                messagebox.showerror("Error", f"Test failed: {e}")
                
    def window_settings(self):
        """Configure window settings"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Window Settings")
        settings_window.geometry("300x200")
        
        ttk.Label(settings_window, text="Target Window Title:").pack(pady=5)
        
        window_var = tk.StringVar(value=self.window_title)
        ttk.Entry(settings_window, textvariable=window_var, width=40).pack(pady=5)
        
        def save_window_settings():
            self.window_title = window_var.get()
            messagebox.showinfo("Settings", "Window settings saved!")
            settings_window.destroy()
            
        ttk.Button(settings_window, text="Save", command=save_window_settings).pack(pady=10)
        
        # List available windows
        ttk.Label(settings_window, text="Available Windows:").pack(pady=(10, 0))
        
        try:
            windows = gw.getAllTitles()
            windows_text = "\n".join([w for w in windows if w.strip()])[:200] + "..."
            ttk.Label(settings_window, text=windows_text, wraplength=280).pack(pady=5)
        except:
            ttk.Label(settings_window, text="Could not retrieve window list").pack(pady=5)
            
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About", 
                          "Shadow Fight 3 Automation Tool\n"
                          "Version 1.0\n\n"
                          "A GUI tool for automating Shadow Fight 3 tasks\n"
                          "using image recognition and customizable actions.")
        
    def show_help(self):
        """Show help dialog"""
        help_text = """
        Shadow Fight 3 Automation Tool Help
        
        1. Create Events: Add events for different automation tasks
        2. Add Images: For each event, add images to detect
        3. Configure Actions: Set what happens when images are found
        4. Set Regions: Limit search to specific screen areas
        5. Start/Stop: Use control buttons to run automation
        
        Action Types:
        - Key Press: Press a single key
        - Key Sequence: Press multiple keys with delays
        - Mouse Click: Click at specific coordinates
        - Mouse Sequence: Multiple clicks with delays
        - Custom Function: Run predefined functions
        
        Tips:
        - Use screenshots to capture images
        - Test image recognition before running
        - Adjust confidence levels for better detection
        - Use regions to improve performance
        """
        
        messagebox.showinfo("Help", help_text)
        
    def on_closing(self):
        """Handle window closing"""
        # Stop all running events
        for event_name in list(self.running_threads.keys()):
            if self.running_threads[event_name].is_alive():
                self.stop_flags[event_name] = True
                
        # Save config before closing
        self.save_config()
        
        self.root.destroy()

def main():
    """Main function to run the application"""
    # Check if required packages are installed
    try:
        import pyautogui
        import pygetwindow
    except ImportError as e:
        print(f"Required package not found: {e}")
        print("Please install required packages:")
        print("pip install pyautogui pygetwindow pillow")
        return
        
    # Create and run the application
    root = tk.Tk()
    app = SF3AutomationTool(root)
    
    # Add menu bar
    app.create_menu()
    
    # Set up window closing handler
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main()