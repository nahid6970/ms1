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

class ImageConfigDialog:
    def __init__(self, parent, image_data=None):
        self.parent = parent
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Image Configuration")
        self.dialog.geometry("500x600")
        self.dialog.configure(bg="#2b2b2b")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (600 // 2)
        self.dialog.geometry(f"500x600+{x}+{y}")
        
        # Initialize data
        if image_data:
            self.image_data = image_data.copy()
        else:
            self.image_data = {
                "name": "",
                "path": "",
                "confidence": 0.8,
                "region": None,
                "action": {
                    "type": "key_press",
                    "key": "",
                    "delay": 0.1
                }
            }
        
        self.create_widgets()
        self.load_data()
        
    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.dialog, bg="#2b2b2b", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Image Name
        tk.Label(main_frame, text="Image Name:", bg="#2b2b2b", fg="white", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.name_entry = tk.Entry(main_frame, bg="#404040", fg="white", width=40, font=("Arial", 10))
        self.name_entry.grid(row=0, column=1, columnspan=2, sticky="ew", pady=(0, 10))
        
        # Image Path
        tk.Label(main_frame, text="Image Path:", bg="#2b2b2b", fg="white", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=(0, 5))
        path_frame = tk.Frame(main_frame, bg="#2b2b2b")
        path_frame.grid(row=1, column=1, columnspan=2, sticky="ew", pady=(0, 10))
        self.path_entry = tk.Entry(path_frame, bg="#404040", fg="white", width=30, font=("Arial", 10))
        self.path_entry.pack(side="left", fill="x", expand=True)
        tk.Button(path_frame, text="Browse", command=self.browse_image, bg="#404040", fg="white", font=("Arial", 9)).pack(side="right", padx=(5, 0))
        
        # Confidence
        tk.Label(main_frame, text="Confidence:", bg="#2b2b2b", fg="white", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=(0, 5))
        conf_frame = tk.Frame(main_frame, bg="#2b2b2b")
        conf_frame.grid(row=2, column=1, columnspan=2, sticky="ew", pady=(0, 10))
        self.confidence_var = tk.DoubleVar(value=0.8)
        self.confidence_scale = tk.Scale(conf_frame, from_=0.1, to=1.0, resolution=0.01, 
                                       orient="horizontal", variable=self.confidence_var,
                                       bg="#404040", fg="white", highlightbackground="#2b2b2b")
        self.confidence_scale.pack(side="left", fill="x", expand=True)
        self.conf_label = tk.Label(conf_frame, text="0.80", bg="#2b2b2b", fg="white", width=6, font=("Arial", 10))
        self.conf_label.pack(side="right")
        self.confidence_scale.config(command=self.update_confidence_label)
        
        # Region
        tk.Label(main_frame, text="Region (x1,y1,x2,y2):", bg="#2b2b2b", fg="white", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky="w", pady=(0, 5))
        region_frame = tk.Frame(main_frame, bg="#2b2b2b")
        region_frame.grid(row=3, column=1, columnspan=2, sticky="ew", pady=(0, 5))
        
        coord_frame = tk.Frame(region_frame, bg="#2b2b2b")
        coord_frame.pack(fill="x")
        self.x1_entry = tk.Entry(coord_frame, bg="#404040", fg="white", width=8, font=("Arial", 10))
        self.x1_entry.pack(side="left", padx=(0, 2))
        self.y1_entry = tk.Entry(coord_frame, bg="#404040", fg="white", width=8, font=("Arial", 10))
        self.y1_entry.pack(side="left", padx=2)
        self.x2_entry = tk.Entry(coord_frame, bg="#404040", fg="white", width=8, font=("Arial", 10))
        self.x2_entry.pack(side="left", padx=2)
        self.y2_entry = tk.Entry(coord_frame, bg="#404040", fg="white", width=8, font=("Arial", 10))
        self.y2_entry.pack(side="left", padx=(2, 5))
        tk.Button(coord_frame, text="Get Position", command=self.get_position, 
                 bg="#404040", fg="white", font=("Arial", 9)).pack(side="left", padx=5)
        
        region_btn_frame = tk.Frame(region_frame, bg="#2b2b2b")
        region_btn_frame.pack(fill="x", pady=(5, 10))
        tk.Button(region_btn_frame, text="Clear Region", command=self.clear_region, 
                 bg="#404040", fg="white", font=("Arial", 9)).pack(side="left")
        
        # Action Type
        tk.Label(main_frame, text="Action Type:", bg="#2b2b2b", fg="white", font=("Arial", 10, "bold")).grid(row=5, column=0, sticky="w", pady=(0, 5))
        self.action_var = tk.StringVar(value="key_press")
        action_types = ["key_press", "key_sequence", "mouse_click", "mouse_sequence", "custom_function"]
        self.action_combo = ttk.Combobox(main_frame, textvariable=self.action_var, values=action_types,
                                       state="readonly", width=37, font=("Arial", 10))
        self.action_combo.grid(row=5, column=1, columnspan=2, sticky="ew", pady=(0, 10))
        self.action_combo.bind("<<ComboboxSelected>>", self.on_action_change)
        
        # Action Configuration Frame
        self.action_frame = tk.Frame(main_frame, bg="#2b2b2b")
        self.action_frame.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(0, 20))
        
        # Buttons
        btn_frame = tk.Frame(main_frame, bg="#2b2b2b")
        btn_frame.grid(row=7, column=0, columnspan=3, pady=10)
        tk.Button(btn_frame, text="OK", command=self.ok_clicked, bg="#404040", fg="white", 
                 font=("Arial", 10, "bold"), width=10).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancel", command=self.cancel_clicked, bg="#404040", fg="white", 
                 font=("Arial", 10, "bold"), width=10).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Test Recognition", command=self.test_recognition, bg="#404040", fg="white", 
                 font=("Arial", 10), width=15).pack(side="left", padx=5)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
        self.create_action_widgets()
        
    def update_confidence_label(self, value):
        self.conf_label.config(text=f"{float(value):.2f}")
        
    def browse_image(self):
        filename = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All files", "*.*")]
        )
        if filename:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, filename)
            # Auto-fill name if empty
            if not self.name_entry.get():
                name = Path(filename).stem
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, name)
                
    def get_position(self):
        self.dialog.withdraw()
        messagebox.showinfo("Get Position", "Press SPACEBAR to capture mouse position")
        
        # Wait for spacebar in a separate thread
        def wait_for_spacebar():
            import keyboard
            keyboard.wait('space')
            x, y = pyautogui.position()
            self.dialog.after(0, lambda: self.set_position(x, y))
            
        threading.Thread(target=wait_for_spacebar, daemon=True).start()
        
    def set_position(self, x, y):
        self.dialog.deiconify()
        # If no region set, create a small region around the point
        if not any([self.x1_entry.get(), self.y1_entry.get(), self.x2_entry.get(), self.y2_entry.get()]):
            self.x1_entry.insert(0, str(max(0, x-50)))
            self.y1_entry.insert(0, str(max(0, y-50)))
            self.x2_entry.insert(0, str(x+50))
            self.y2_entry.insert(0, str(y+50))
        messagebox.showinfo("Position Captured", f"Mouse position: {x}, {y}")
        
    def clear_region(self):
        for entry in [self.x1_entry, self.y1_entry, self.x2_entry, self.y2_entry]:
            entry.delete(0, tk.END)
            
    def on_action_change(self, event=None):
        self.create_action_widgets()
        
    def create_action_widgets(self):
        # Clear existing widgets
        for widget in self.action_frame.winfo_children():
            widget.destroy()
            
        action_type = self.action_var.get()
        
        # Common delay field
        delay_frame = tk.Frame(self.action_frame, bg="#2b2b2b")
        delay_frame.pack(fill="x", pady=(0, 5))
        tk.Label(delay_frame, text="Delay (seconds):", bg="#2b2b2b", fg="white", font=("Arial", 10)).pack(side="left")
        self.delay_entry = tk.Entry(delay_frame, bg="#404040", fg="white", width=10, font=("Arial", 10))
        self.delay_entry.pack(side="right")
        
        if action_type == "key_press":
            key_frame = tk.Frame(self.action_frame, bg="#2b2b2b")
            key_frame.pack(fill="x", pady=5)
            tk.Label(key_frame, text="Key:", bg="#2b2b2b", fg="white", font=("Arial", 10)).pack(side="left")
            self.key_entry = tk.Entry(key_frame, bg="#404040", fg="white", width=20, font=("Arial", 10))
            self.key_entry.pack(side="right")
            
        elif action_type == "key_sequence":
            seq_frame = tk.Frame(self.action_frame, bg="#2b2b2b")
            seq_frame.pack(fill="x", pady=5)
            tk.Label(seq_frame, text="Sequence (key1,delay1,key2,delay2):", bg="#2b2b2b", fg="white", font=("Arial", 10)).pack(anchor="w")
            self.sequence_entry = tk.Entry(seq_frame, bg="#404040", fg="white", width=40, font=("Arial", 10))
            self.sequence_entry.pack(fill="x", pady=5)
            
        elif action_type == "mouse_click":
            click_frame = tk.Frame(self.action_frame, bg="#2b2b2b")
            click_frame.pack(fill="x", pady=5)
            tk.Label(click_frame, text="Click Position (X, Y):", bg="#2b2b2b", fg="white", font=("Arial", 10)).pack(anchor="w")
            coord_frame = tk.Frame(click_frame, bg="#2b2b2b")
            coord_frame.pack(fill="x", pady=5)
            self.click_x_entry = tk.Entry(coord_frame, bg="#404040", fg="white", width=10, font=("Arial", 10))
            self.click_x_entry.pack(side="left", padx=(0, 5))
            self.click_y_entry = tk.Entry(coord_frame, bg="#404040", fg="white", width=10, font=("Arial", 10))
            self.click_y_entry.pack(side="left", padx=5)
            tk.Button(coord_frame, text="Get Current Position", command=self.get_click_position, 
                     bg="#404040", fg="white", font=("Arial", 9)).pack(side="left", padx=10)
            
        elif action_type == "mouse_sequence":
            seq_frame = tk.Frame(self.action_frame, bg="#2b2b2b")
            seq_frame.pack(fill="x", pady=5)
            tk.Label(seq_frame, text="Sequence (x1,y1,delay1,x2,y2,delay2):", bg="#2b2b2b", fg="white", font=("Arial", 10)).pack(anchor="w")
            self.mouse_sequence_entry = tk.Entry(seq_frame, bg="#404040", fg="white", width=40, font=("Arial", 10))
            self.mouse_sequence_entry.pack(fill="x", pady=5)
            
        elif action_type == "custom_function":
            func_frame = tk.Frame(self.action_frame, bg="#2b2b2b")
            func_frame.pack(fill="x", pady=5)
            tk.Label(func_frame, text="Function Name:", bg="#2b2b2b", fg="white", font=("Arial", 10)).pack(anchor="w")
            self.function_entry = tk.Entry(func_frame, bg="#404040", fg="white", width=30, font=("Arial", 10))
            self.function_entry.pack(fill="x", pady=5)
            
            tk.Label(func_frame, text="Parameters (JSON format):", bg="#2b2b2b", fg="white", font=("Arial", 10)).pack(anchor="w", pady=(10, 0))
            self.params_text = tk.Text(func_frame, bg="#404040", fg="white", height=4, width=40, font=("Arial", 10))
            self.params_text.pack(fill="x", pady=5)
            
    def get_click_position(self):
        self.dialog.withdraw()
        messagebox.showinfo("Get Click Position", "Press SPACEBAR to capture mouse position for clicking")
        
        def wait_for_spacebar():
            import keyboard
            keyboard.wait('space')
            x, y = pyautogui.position()
            self.dialog.after(0, lambda: self.set_click_position(x, y))
            
        threading.Thread(target=wait_for_spacebar, daemon=True).start()
        
    def set_click_position(self, x, y):
        self.dialog.deiconify()
        self.click_x_entry.delete(0, tk.END)
        self.click_x_entry.insert(0, str(x))
        self.click_y_entry.delete(0, tk.END)
        self.click_y_entry.insert(0, str(y))
        messagebox.showinfo("Position Captured", f"Click position set to: {x}, {y}")
        
    def test_recognition(self):
        if not self.path_entry.get():
            messagebox.showerror("Error", "Please select an image first")
            return
            
        if not os.path.exists(self.path_entry.get()):
            messagebox.showerror("Error", "Image file not found")
            return
            
        try:
            confidence = self.confidence_var.get()
            region = None
            
            # Get region if specified
            if all([self.x1_entry.get(), self.y1_entry.get(), self.x2_entry.get(), self.y2_entry.get()]):
                try:
                    region = (int(self.x1_entry.get()), int(self.y1_entry.get()), 
                             int(self.x2_entry.get()) - int(self.x1_entry.get()),
                             int(self.y2_entry.get()) - int(self.y1_entry.get()))
                except ValueError:
                    messagebox.showerror("Error", "Invalid region coordinates")
                    return
            
            # Test image recognition
            location = pyautogui.locateOnScreen(
                self.path_entry.get(),
                confidence=confidence,
                grayscale=True,
                region=region
            )
            
            if location:
                x, y = pyautogui.center(location)
                messagebox.showinfo("Test Result", f"Image found at position: {x}, {y}")
            else:
                messagebox.showwarning("Test Result", "Image not found on screen")
                
        except Exception as e:
            messagebox.showerror("Error", f"Test failed: {str(e)}")
            
    def load_data(self):
        # Load existing data
        self.name_entry.insert(0, self.image_data.get("name", ""))
        self.path_entry.insert(0, self.image_data.get("path", ""))
        self.confidence_var.set(self.image_data.get("confidence", 0.8))
        
        # Load region
        region = self.image_data.get("region")
        if region:
            self.x1_entry.insert(0, str(region[0]))
            self.y1_entry.insert(0, str(region[1]))
            self.x2_entry.insert(0, str(region[2]))
            self.y2_entry.insert(0, str(region[3]))
            
        # Load action
        action = self.image_data.get("action", {})
        self.action_var.set(action.get("type", "key_press"))
        self.create_action_widgets()
        
        # Set delay
        if hasattr(self, 'delay_entry'):
            self.delay_entry.insert(0, str(action.get("delay", 0.1)))
            
        # Set action-specific fields
        action_type = action.get("type", "key_press")
        if action_type == "key_press" and hasattr(self, 'key_entry'):
            self.key_entry.insert(0, action.get("key", ""))
        elif action_type == "key_sequence" and hasattr(self, 'sequence_entry'):
            self.sequence_entry.insert(0, action.get("sequence", ""))
        elif action_type == "mouse_click":
            if hasattr(self, 'click_x_entry'):
                self.click_x_entry.insert(0, str(action.get("x", "")))
            if hasattr(self, 'click_y_entry'):
                self.click_y_entry.insert(0, str(action.get("y", "")))
        elif action_type == "mouse_sequence" and hasattr(self, 'mouse_sequence_entry'):
            self.mouse_sequence_entry.insert(0, action.get("sequence", ""))
        elif action_type == "custom_function":
            if hasattr(self, 'function_entry'):
                self.function_entry.insert(0, action.get("function", ""))
            if hasattr(self, 'params_text'):
                self.params_text.insert("1.0", action.get("params", "{}"))
                
    def ok_clicked(self):
        # Validate inputs
        if not self.name_entry.get().strip():
            messagebox.showerror("Error", "Please enter an image name")
            return
            
        if not self.path_entry.get().strip():
            messagebox.showerror("Error", "Please select an image file")
            return
            
        if not os.path.exists(self.path_entry.get()):
            messagebox.showerror("Error", "Image file not found")
            return
            
        # Build result data
        self.result = {
            "name": self.name_entry.get().strip(),
            "path": self.path_entry.get().strip(),
            "confidence": self.confidence_var.get(),
            "region": None,
            "action": self.get_action_data()
        }
        
        # Get region if specified
        if all([self.x1_entry.get(), self.y1_entry.get(), self.x2_entry.get(), self.y2_entry.get()]):
            try:
                self.result["region"] = [
                    int(self.x1_entry.get()),
                    int(self.y1_entry.get()),
                    int(self.x2_entry.get()),
                    int(self.y2_entry.get())
                ]
            except ValueError:
                messagebox.showerror("Error", "Invalid region coordinates")
                return
                
        self.dialog.destroy()
        
    def get_action_data(self):
        action_type = self.action_var.get()
        action_data = {"type": action_type}
        
        # Get delay
        try:
            action_data["delay"] = float(self.delay_entry.get() if self.delay_entry.get() else 0.1)
        except ValueError:
            action_data["delay"] = 0.1
            
        if action_type == "key_press":
            action_data["key"] = self.key_entry.get()
        elif action_type == "key_sequence":
            action_data["sequence"] = self.sequence_entry.get()
        elif action_type == "mouse_click":
            try:
                action_data["x"] = int(self.click_x_entry.get()) if self.click_x_entry.get() else 0
                action_data["y"] = int(self.click_y_entry.get()) if self.click_y_entry.get() else 0
            except ValueError:
                action_data["x"] = 0
                action_data["y"] = 0
        elif action_type == "mouse_sequence":
            action_data["sequence"] = self.mouse_sequence_entry.get()
        elif action_type == "custom_function":
            action_data["function"] = self.function_entry.get()
            try:
                params_text = self.params_text.get("1.0", tk.END).strip()
                if params_text:
                    json.loads(params_text)  # Validate JSON
                    action_data["params"] = params_text
                else:
                    action_data["params"] = "{}"
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Invalid JSON format in parameters")
                return None
                
        return action_data
        
    def cancel_clicked(self):
        self.result = None
        self.dialog.destroy()


class GameAutomationTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Shadow Fight 3 Automation Tool")
        self.root.geometry("1200x800")
        self.root.configure(bg="#2b2b2b")
        
        # Data storage
        self.events_data = {}
        self.stop_flags = {}
        self.running_threads = {}
        self.config_file = "sf3_automation_config.json"
        self.window_title = "LDPlayer"
        
        # Initialize PyAutoGUI
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
        self.create_widgets()
        self.create_menu()
        self.load_config()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def create_menu(self):
        menubar = tk.Menu(self.root, bg="#2b2b2b", fg="white")
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg="#2b2b2b", fg="white")
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_config)
        file_menu.add_command(label="Open", command=self.load_config_dialog)
        file_menu.add_command(label="Save", command=self.save_config)
        file_menu.add_command(label="Export", command=self.export_config)
        file_menu.add_command(label="Import", command=self.import_config)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0, bg="#2b2b2b", fg="white")
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Screenshot Tool", command=self.screenshot_tool)
        tools_menu.add_command(label="Test Image Recognition", command=self.test_image_recognition)
        tools_menu.add_command(label="Window Settings", command=self.window_settings)
        tools_menu.add_command(label="List Windows", command=self.list_windows)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg="#2b2b2b", fg="white")
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Help", command=self.show_help)
        
    def create_widgets(self):
        # Main container
        main_frame = tk.Frame(self.root, bg="#2b2b2b")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left Panel - Event Management
        left_frame = tk.Frame(main_frame, bg="#2b2b2b", width=400)
        left_frame.pack(side="left", fill="both", expand=False, padx=(0, 10))
        left_frame.pack_propagate(False)
        
        # Event Management Section
        event_label = tk.Label(left_frame, text="Events", bg="#2b2b2b", fg="white", font=("Arial", 12, "bold"))
        event_label.pack(pady=(0, 5))
        
        # Event list with scrollbar
        event_list_frame = tk.Frame(left_frame, bg="#2b2b2b")
        event_list_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        event_scrollbar = tk.Scrollbar(event_list_frame, bg="#404040")
        event_scrollbar.pack(side="right", fill="y")
        
        self.event_listbox = tk.Listbox(event_list_frame, bg="#404040", fg="white", 
                                       font=("Arial", 10), yscrollcommand=event_scrollbar.set,
                                       selectbackground="#606060")
        self.event_listbox.pack(side="left", fill="both", expand=True)
        event_scrollbar.config(command=self.event_listbox.yview)
        self.event_listbox.bind("<<ListboxSelect>>", self.on_event_select)
        
        # Event buttons
        event_btn_frame = tk.Frame(left_frame, bg="#2b2b2b")
        event_btn_frame.pack(fill="x", pady=(0, 10))
        
        tk.Button(event_btn_frame, text="Add Event", command=self.add_event, 
                 bg="#404040", fg="white", font=("Arial", 10)).pack(side="left", padx=(0, 5))
        tk.Button(event_btn_frame, text="Delete Event", command=self.delete_event, 
                 bg="#404040", fg="white", font=("Arial", 10)).pack(side="left", padx=5)
        tk.Button(event_btn_frame, text="Rename Event", command=self.rename_event, 
                 bg="#404040", fg="white", font=("Arial", 10)).pack(side="left", padx=5)
        
        # Image list section
        image_label = tk.Label(left_frame, text="Images", bg="#2b2b2b", fg="white", font=("Arial", 12, "bold"))
        image_label.pack(pady=(10, 5))
        
        # Image list with scrollbar
        image_list_frame = tk.Frame(left_frame, bg="#2b2b2b")
        image_list_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        image_scrollbar = tk.Scrollbar(image_list_frame, bg="#404040")
        image_scrollbar.pack(side="right", fill="y")
        
        self.image_listbox = tk.Listbox(image_list_frame, bg="#404040", fg="white", 
                                       font=("Arial", 10), yscrollcommand=image_scrollbar.set,
                                       selectbackground="#606060")
        self.image_listbox.pack(side