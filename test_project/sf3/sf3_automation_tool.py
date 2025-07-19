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

class SF3AutomationTool(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Shadow Fight 3 Automation Tool")
        self.geometry("1200x800")
        self.configure(bg="#2b2b2b") # Dark theme background

        self.events_data = {} # Data structure for events
        self.stop_flags = {} # To manage stopping threads
        self.running_threads = {} # To keep track of running threads
        self.target_window_title = "LDPlayer" # Default target window

        self.selected_event = None
        self.selected_image_data = None

        self._create_styles()
        self._create_menu()
        self._create_main_layout()
        self._create_left_panel()
        self._create_right_panel()
        self._create_bottom_panel()

        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.load_config() # Load configuration on startup

    def _create_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam") # Use a theme that allows for easy customization

        # Configure general styles for dark theme
        style.configure("TFrame", background="#2b2b2b")
        style.configure("TLabel", background="#2b2b2b", foreground="white")
        style.configure("TButton", background="#404040", foreground="white", font=("Arial", 10))
        style.map("TButton", background=[("active", "#555555")])
        style.configure("TEntry", fieldbackground="#404040", foreground="white", insertbackground="white")
        style.configure("TCombobox", fieldbackground="#404040", foreground="white", selectbackground="#555555", selectforeground="white")
        style.configure("TScale", background="#2b2b2b", troughcolor="#404040", foreground="white")
        style.configure("TCheckbutton", background="#2b2b2b", foreground="white")
        style.configure("TPanedwindow", background="#2b2b2b")
        style.configure("TLabelframe", background="#2b2b2b", foreground="white")
        style.configure("TLabelframe.Label", background="#2b2b2b", foreground="white")

        # Listbox specific styles
        self.option_add("*Listbox*background", "#404040")
        self.option_add("*Listbox*foreground", "white")
        self.option_add("*Listbox*selectBackground", "#555555")
        self.option_add("*Listbox*selectForeground", "white")

    def _create_menu(self):
        menubar = tk.Menu(self, bg="#404040", fg="white")
        self.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0, bg="#404040", fg="white")
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self._new_config)
        file_menu.add_command(label="Open", command=self.load_config)
        file_menu.add_command(label="Save", command=self.save_config)
        file_menu.add_separator()
        file_menu.add_command(label="Export", command=self._export_config)
        file_menu.add_command(label="Import", command=self._import_config)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)

        tools_menu = tk.Menu(menubar, tearoff=0, bg="#404040", fg="white")
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Screenshot Tool", command=self._screenshot_tool)
        tools_menu.add_command(label="Test Image Recognition", command=self._test_image_recognition)
        tools_menu.add_command(label="Mouse Position Capture", command=self._get_mouse_position)
        tools_menu.add_command(label="Region Selection Helper", command=self._region_selection_helper)
        tools_menu.add_command(label="Available Windows", command=self._list_available_windows)
        tools_menu.add_command(label="Window Settings", command=self._window_settings)

        help_menu = tk.Menu(menubar, tearoff=0, bg="#404040", fg="white")
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
        help_menu.add_command(label="Help", command=self._show_help)

    def _create_main_layout(self):
        self.main_pane = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        self.main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.left_frame = ttk.Frame(self.main_pane, width=400, relief=tk.GROOVE, borderwidth=2)
        self.right_frame = ttk.Frame(self.main_pane, relief=tk.GROOVE, borderwidth=2)
        self.main_pane.add(self.left_frame, weight=1)
        self.main_pane.add(self.right_frame, weight=2)

        self.bottom_frame = ttk.Frame(self, height=100, relief=tk.GROOVE, borderwidth=2)
        self.bottom_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        # Status bar
        self.status_bar = ttk.Label(self, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _update_status(self, message):
        self.status_bar.config(text=message)

    def _create_left_panel(self):
        # Event Management
        event_frame = ttk.LabelFrame(self.left_frame, text="Event Management", padding=10)
        event_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.event_listbox = tk.Listbox(event_frame, height=10)
        self.event_listbox.pack(fill=tk.BOTH, expand=True)
        self.event_listbox.bind("<<ListboxSelect>>", self._on_event_select)

        event_buttons_frame = ttk.Frame(event_frame)
        event_buttons_frame.pack(fill=tk.X, pady=5)
        ttk.Button(event_buttons_frame, text="Add Event", command=self._add_event).pack(side=tk.LEFT, expand=True, padx=2)
        ttk.Button(event_buttons_frame, text="Delete Event", command=self._delete_event).pack(side=tk.LEFT, expand=True, padx=2)
        ttk.Button(event_buttons_frame, text="Rename Event", command=self._rename_event).pack(side=tk.LEFT, expand=True, padx=2)

        # Image List for Selected Event
        image_frame = ttk.LabelFrame(self.left_frame, text="Images for Selected Event", padding=10)
        image_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.image_listbox = tk.Listbox(image_frame, height=10)
        self.image_listbox.pack(fill=tk.BOTH, expand=True)
        self.image_listbox.bind("<<ListboxSelect>>", self._on_image_select)

        image_buttons_frame = ttk.Frame(image_frame)
        image_buttons_frame.pack(fill=tk.X, pady=5)
        ttk.Button(image_buttons_frame, text="Add Image", command=self._add_image).pack(side=tk.LEFT, expand=True, padx=2)
        ttk.Button(image_buttons_frame, text="Delete Image", command=self._delete_image).pack(side=tk.LEFT, expand=True, padx=2)
        ttk.Button(image_buttons_frame, text="Edit Image", command=self._edit_image).pack(side=tk.LEFT, expand=True, padx=2)

    def _create_right_panel(self):
        # Image Configuration
        config_frame = ttk.LabelFrame(self.right_frame, text="Image Configuration", padding=10)
        config_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Image Path
        ttk.Label(config_frame, text="Image Path:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.image_path_entry = ttk.Entry(config_frame, width=50)
        self.image_path_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        ttk.Button(config_frame, text="Browse", command=self._browse_image).grid(row=0, column=2, padx=2, pady=2)

        # Confidence
        ttk.Label(config_frame, text="Confidence (0.1-1.0):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.confidence_label = ttk.Label(config_frame, text="0.8")
        self.confidence_label.grid(row=1, column=2, sticky=tk.W, padx=2, pady=2)
        self.confidence_scale = ttk.Scale(config_frame, from_=0.1, to=1.0, orient=tk.HORIZONTAL, length=200, command=self._update_confidence_label)
        self.confidence_scale.set(0.8)
        self.confidence_scale.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)

        # Region Coordinates
        ttk.Label(config_frame, text="Region (x1, y1, x2, y2):").grid(row=2, column=0, sticky=tk.W, pady=2)
        region_frame = ttk.Frame(config_frame)
        region_frame.grid(row=2, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=2)
        self.region_x1_entry = ttk.Entry(region_frame, width=8)
        self.region_x1_entry.pack(side=tk.LEFT, padx=1)
        self.region_y1_entry = ttk.Entry(region_frame, width=8)
        self.region_y1_entry.pack(side=tk.LEFT, padx=1)
        self.region_x2_entry = ttk.Entry(region_frame, width=8)
        self.region_x2_entry.pack(side=tk.LEFT, padx=1)
        self.region_y2_entry = ttk.Entry(region_frame, width=8)
        self.region_y2_entry.pack(side=tk.LEFT, padx=1)

        # Action Type
        ttk.Label(config_frame, text="Action Type:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.action_type_var = tk.StringVar(self)
        self.action_type_dropdown = ttk.Combobox(config_frame, textvariable=self.action_type_var,
                                                 values=["key_press", "key_sequence", "mouse_click", "mouse_sequence", "custom_function"])
        self.action_type_dropdown.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=2)
        self.action_type_dropdown.set("key_press") # Default value
        self.action_type_dropdown.bind("<<ComboboxSelected>>", self._on_action_type_select)

        # Dynamic Action Configuration Frame
        self.action_config_frame = ttk.Frame(config_frame)
        self.action_config_frame.grid(row=4, column=0, columnspan=3, sticky=tk.EW, padx=5, pady=5)
        self._on_action_type_select() # Initialize dynamic form

        config_frame.grid_columnconfigure(1, weight=1) # Allow column 1 to expand

    def _create_bottom_panel(self):
        self.bottom_frame.grid_columnconfigure(0, weight=1) # Allow column to expand
        self.event_control_buttons_frame = ttk.Frame(self.bottom_frame)
        self.event_control_buttons_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self._update_event_control_buttons() # Populate buttons based on events

    # --- Event Management Callbacks ---
    def _on_event_select(self, event=None):
        selected_index = self.event_listbox.curselection()
        if selected_index:
            event_name = self.event_listbox.get(selected_index[0])
            self.selected_event = event_name
            self._update_image_listbox(event_name)
            self._update_event_control_buttons()
        else:
            self.selected_event = None
            self.image_listbox.delete(0, tk.END)
            self._clear_image_config_form()
            self._update_event_control_buttons()

    def _add_event(self):
        event_name = simpledialog.askstring("Add Event", "Enter event name:")
        if event_name and event_name not in self.events_data:
            self.events_data[event_name] = {"images": [], "enabled": True}
            self._update_event_listbox()
            self.save_config()
            self._update_status(f"Event '{event_name}' added.")
        elif event_name:
            messagebox.showerror("Error", f"Event '{event_name}' already exists.")

    def _delete_event(self):
        selected_index = self.event_listbox.curselection()
        if selected_index:
            event_name = self.event_listbox.get(selected_index[0])
            if messagebox.askyesno("Delete Event", f"Are you sure you want to delete event '{event_name}' and all its images?"):
                if event_name in self.running_threads and self.running_threads[event_name].is_alive():
                    messagebox.showwarning("Warning", f"Event '{event_name}' is currently running. Please stop it before deleting.")
                    return
                del self.events_data[event_name]
                if event_name in self.stop_flags:
                    del self.stop_flags[event_name]
                if event_name in self.running_threads:
                    del self.running_threads[event_name]
                self._update_event_listbox()
                self.save_config()
                self._update_status(f"Event '{event_name}' deleted.")
        else:
            messagebox.showwarning("Warning", "Please select an event to delete.")

    def _rename_event(self):
        selected_index = self.event_listbox.curselection()
        if selected_index:
            old_name = self.event_listbox.get(selected_index[0])
            new_name = simpledialog.askstring("Rename Event", f"Rename '{old_name}' to:", initialvalue=old_name)
            if new_name and new_name != old_name:
                if new_name in self.events_data:
                    messagebox.showerror("Error", f"Event '{new_name}' already exists.")
                    return
                if old_name in self.running_threads and self.running_threads[old_name].is_alive():
                    messagebox.showwarning("Warning", f"Event '{old_name}' is currently running. Please stop it before renaming.")
                    return

                self.events_data[new_name] = self.events_data.pop(old_name)
                if old_name in self.stop_flags:
                    self.stop_flags[new_name] = self.stop_flags.pop(old_name)
                if old_name in self.running_threads:
                    self.running_threads[new_name] = self.running_threads.pop(old_name)
                self._update_event_listbox()
                self.save_config()
                self._update_status(f"Event '{old_name}' renamed to '{new_name}'.")
        else:
            messagebox.showwarning("Warning", "Please select an event to rename.")

    def _update_event_listbox(self):
        self.event_listbox.delete(0, tk.END)
        for event_name in self.events_data:
            self.event_listbox.insert(tk.END, event_name)
        self._on_event_select() # Re-select if possible or clear image list

    # --- Image Management Callbacks ---
    def _on_image_select(self, event=None):
        selected_event_index = self.event_listbox.curselection()
        selected_image_index = self.image_listbox.curselection()

        if selected_event_index and selected_image_index:
            event_name = self.event_listbox.get(selected_event_index[0])
            image_name = self.image_listbox.get(selected_image_index[0])
            image_data = next((img for img in self.events_data[event_name]["images"] if img["name"] == image_name), None)
            if image_data:
                self.selected_image_data = image_data
                self._populate_image_config_form(image_data)
            else:
                self.selected_image_data = None
                self._clear_image_config_form()
        else:
            self.selected_image_data = None
            self._clear_image_config_form()

    def _add_image(self):
        if not self.selected_event:
            messagebox.showwarning("Warning", "Please select an event first.")
            return

        image_name = simpledialog.askstring("Add Image", "Enter image name:")
        if not image_name:
            return

        # Check if image name already exists for this event
        if any(img["name"] == image_name for img in self.events_data[self.selected_event]["images"]):
            messagebox.showerror("Error", f"Image '{image_name}' already exists for this event.")
            return

        file_path = filedialog.askopenfilename(title="Select Image File",
                                               filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")])
        if file_path:
            new_image_data = {
                "name": image_name,
                "path": file_path,
                "confidence": 0.8,
                "region": None,
                "action": {"type": "key_press", "key": "space", "delay": 0.1}
            }
            self.events_data[self.selected_event]["images"].append(new_image_data)
            self._update_image_listbox(self.selected_event)
            self.save_config()
            self._update_status(f"Image '{image_name}' added to '{self.selected_event}'.")
            # Select the newly added image
            self.image_listbox.selection_clear(0, tk.END)
            self.image_listbox.selection_set(tk.END)
            self.image_listbox.event_generate("<<ListboxSelect>>")
        else:
            messagebox.showwarning("Warning", "No image file selected.")

    def _delete_image(self):
        selected_event_index = self.event_listbox.curselection()
        selected_image_index = self.image_listbox.curselection()

        if selected_event_index and selected_image_index:
            event_name = self.event_listbox.get(selected_event_index[0])
            image_name = self.image_listbox.get(selected_image_index[0])
            if messagebox.askyesno("Delete Image", f"Are you sure you want to delete image '{image_name}' from '{event_name}'?"):
                self.events_data[event_name]["images"] = [
                    img for img in self.events_data[event_name]["images"] if img["name"] != image_name
                ]
                self._update_image_listbox(event_name)
                self.save_config()
                self._update_status(f"Image '{image_name}' deleted from '{event_name}'.")
        else:
            messagebox.showwarning("Warning", "Please select an image to delete.")

    def _edit_image(self):
        if not self.selected_image_data:
            messagebox.showwarning("Warning", "Please select an image to edit.")
            return

        try:
            # Update image data from form
            self.selected_image_data["path"] = self.image_path_entry.get()
            
            confidence_val = float(self.confidence_scale.get())
            if not (0.1 <= confidence_val <= 1.0):
                raise ValueError("Confidence must be between 0.1 and 1.0")
            self.selected_image_data["confidence"] = confidence_val
            
            region_coords_str = [
                self.region_x1_entry.get(), self.region_y1_entry.get(),
                self.region_x2_entry.get(), self.region_y2_entry.get()
            ]
            if all(coord.strip() == "" for coord in region_coords_str):
                self.selected_image_data["region"] = None
            else:
                try:
                    region_coords = [int(c) for c in region_coords_str]
                    if len(region_coords) != 4:
                        raise ValueError("Region must have 4 integer coordinates.")
                    self.selected_image_data["region"] = region_coords
                except ValueError:
                    raise ValueError("Region coordinates must be integers.")

            action_type = self.action_type_var.get()
            self.selected_image_data["action"]["type"] = action_type

            # Update action specific parameters
            if action_type == "key_press":
                key = self.key_entry.get()
                if not key:
                    raise ValueError("Key cannot be empty for key_press action.")
                self.selected_image_data["action"]["key"] = key
                self.selected_image_data["action"]["delay"] = float(self.delay_entry.get())
            elif action_type == "key_sequence":
                sequence = self.sequence_entry.get()
                if not sequence:
                    raise ValueError("Sequence cannot be empty for key_sequence action.")
                self.selected_image_data["action"]["sequence"] = sequence
            elif action_type == "mouse_click":
                x = self.mouse_x_entry.get()
                y = self.mouse_y_entry.get()
                if not x or not y:
                    raise ValueError("X and Y coordinates cannot be empty for mouse_click action.")
                self.selected_image_data["action"]["x"] = int(x)
                self.selected_image_data["action"]["y"] = int(y)
                self.selected_image_data["action"]["delay"] = float(self.mouse_delay_entry.get())
            elif action_type == "mouse_sequence":
                sequence = self.mouse_sequence_entry.get()
                if not sequence:
                    raise ValueError("Sequence cannot be empty for mouse_sequence action.")
                self.selected_image_data["action"]["sequence"] = sequence
            elif action_type == "custom_function":
                function_name = self.function_name_entry.get()
                if not function_name:
                    raise ValueError("Function name cannot be empty for custom_function action.")
                self.selected_image_data["action"]["function_name"] = function_name
                try:
                    self.selected_image_data["action"]["parameters"] = json.loads(self.parameters_entry.get())
                except json.JSONDecodeError:
                    raise ValueError("Invalid JSON format for custom function parameters.")

            messagebox.showinfo("Success", f"Image '{self.selected_image_data["name"]}' updated successfully.")
            self.save_config()
            self._update_status(f"Image '{self.selected_image_data["name"]}' configuration updated.")

        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def _update_image_listbox(self, event_name):
        self.image_listbox.delete(0, tk.END)
        if event_name in self.events_data:
            for image_data in self.events_data[event_name]["images"]:
                self.image_listbox.insert(tk.END, image_data["name"])
        self._clear_image_config_form()

    def _populate_image_config_form(self, image_data):
        self._clear_image_config_form() # Clear previous entries

        self.image_path_entry.insert(0, image_data.get("path", ""))
        self.confidence_scale.set(image_data.get("confidence", 0.8))
        self._update_confidence_label()

        region = image_data.get("region")
        if region and len(region) == 4:
            self.region_x1_entry.insert(0, str(region[0]))
            self.region_y1_entry.insert(0, str(region[1]))
            self.region_x2_entry.insert(0, str(region[2]))
            self.region_y2_entry.insert(0, str(region[3]))
        
        action = image_data.get("action", {"type": "key_press"})
        self.action_type_var.set(action.get("type", "key_press"))
        self._on_action_type_select() # Re-draw dynamic form

        # Populate action specific fields
        if action["type"] == "key_press":
            self.key_entry.insert(0, action.get("key", ""))
            self.delay_entry.insert(0, str(action.get("delay", 0.1)))
        elif action["type"] == "key_sequence":
            self.sequence_entry.insert(0, action.get("sequence", ""))
        elif action["type"] == "mouse_click":
            self.mouse_x_entry.insert(0, str(action.get("x", "")))
            self.mouse_y_entry.insert(0, str(action.get("y", "")))
            self.mouse_delay_entry.insert(0, str(action.get("delay", 0.1)))
        elif action["type"] == "mouse_sequence":
            self.mouse_sequence_entry.insert(0, action.get("sequence", ""))
        elif action["type"] == "custom_function":
            self.function_name_entry.insert(0, action.get("function_name", ""))
            self.parameters_entry.insert(0, json.dumps(action.get("parameters", {})))

    def _clear_image_config_form(self):
        self.image_path_entry.delete(0, tk.END)
        self.confidence_scale.set(0.8)
        self._update_confidence_label()
        self.region_x1_entry.delete(0, tk.END)
        self.region_y1_entry.delete(0, tk.END)
        self.region_x2_entry.delete(0, tk.END)
        self.region_y2_entry.delete(0, tk.END)
        self.action_type_var.set("key_press")
        self._on_action_type_select() # Clear dynamic form

    def _browse_image(self):
        file_path = filedialog.askopenfilename(title="Select Image File",
                                               filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")])
        if file_path:
            self.image_path_entry.delete(0, tk.END)
            self.image_path_entry.insert(0, file_path)

    def _update_confidence_label(self, value=None):
        self.confidence_label.config(text=f"{self.confidence_scale.get():.1f}")

    def _on_action_type_select(self, event=None):
        # Clear existing widgets in the dynamic frame
        for widget in self.action_config_frame.winfo_children():
            widget.destroy()

        action_type = self.action_type_var.get()

        if action_type == "key_press":
            ttk.Label(self.action_config_frame, text="Key:").grid(row=0, column=0, sticky=tk.W, pady=2)
            self.key_entry = ttk.Entry(self.action_config_frame, width=20)
            self.key_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
            ttk.Label(self.action_config_frame, text="Delay (s):").grid(row=1, column=0, sticky=tk.W, pady=2)
            self.delay_entry = ttk.Entry(self.action_config_frame, width=20)
            self.delay_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)
        elif action_type == "key_sequence":
            ttk.Label(self.action_config_frame, text="Sequence (key1,delay1,key2,delay2,...):").grid(row=0, column=0, sticky=tk.W, pady=2)
            self.sequence_entry = ttk.Entry(self.action_config_frame, width=50)
            self.sequence_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        elif action_type == "mouse_click":
            ttk.Label(self.action_config_frame, text="X:").grid(row=0, column=0, sticky=tk.W, pady=2)
            self.mouse_x_entry = ttk.Entry(self.action_config_frame, width=10)
            self.mouse_x_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
            ttk.Label(self.action_config_frame, text="Y:").grid(row=1, column=0, sticky=tk.W, pady=2)
            self.mouse_y_entry = ttk.Entry(self.action_config_frame, width=10)
            self.mouse_y_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
            ttk.Label(self.action_config_frame, text="Delay (s):").grid(row=2, column=0, sticky=tk.W, pady=2)
            self.mouse_delay_entry = ttk.Entry(self.action_config_frame, width=10)
            self.mouse_delay_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
            ttk.Button(self.action_config_frame, text="Get Position", command=self._get_mouse_position).grid(row=0, column=2, rowspan=2, padx=5, pady=2)
        elif action_type == "mouse_sequence":
            ttk.Label(self.action_config_frame, text="Sequence (x1,y1,delay1,x2,y2,delay2,...):").grid(row=0, column=0, sticky=tk.W, pady=2)
            self.mouse_sequence_entry = ttk.Entry(self.action_config_frame, width=50)
            self.mouse_sequence_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        elif action_type == "custom_function":
            ttk.Label(self.action_config_frame, text="Function Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
            self.function_name_entry = ttk.Entry(self.action_config_frame, width=30)
            self.function_name_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
            ttk.Label(self.action_config_frame, text="Parameters (JSON):").grid(row=1, column=0, sticky=tk.W, pady=2)
            self.parameters_entry = ttk.Entry(self.action_config_frame, width=30)
            self.parameters_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)
        
        self.action_config_frame.grid_columnconfigure(1, weight=1) # Allow column 1 to expand

    # --- Bottom Panel Callbacks (Event Control) ---
    def _update_event_control_buttons(self):
        # Clear existing buttons
        for widget in self.event_control_buttons_frame.winfo_children():
            widget.destroy()

        for event_name in self.events_data:
            button_text = f"Start {event_name}"
            command = lambda name=event_name: self._start_event(name)
            if event_name in self.running_threads and self.running_threads[event_name].is_alive(): # If running
                button_text = f"Stop {event_name}"
                command = lambda name=event_name: self._stop_event(name)
            
            ttk.Button(self.event_control_buttons_frame, text=button_text, command=command).pack(side=tk.LEFT, padx=5, pady=5)

    def _start_event(self, event_name):
        if event_name not in self.events_data:
            messagebox.showerror("Error", f"Event '{event_name}' not found.")
            return
        if event_name in self.running_threads and self.running_threads[event_name].is_alive():
            messagebox.showwarning("Warning", f"Event '{event_name}' is already running.")
            return

        self.stop_flags[event_name] = False
        thread = threading.Thread(target=self.run_event, args=(event_name,), daemon=True)
        self.running_threads[event_name] = thread
        thread.start()
        self._update_event_control_buttons()
        self._update_status(f"Started event '{event_name}'.")
        messagebox.showinfo("Info", f"Started event '{event_name}'.")

    def _stop_event(self, event_name):
        if event_name in self.stop_flags:
            self.stop_flags[event_name] = True
            self._update_status(f"Stopping event '{event_name}'. Please wait...")
            messagebox.showinfo("Info", f"Stopping event '{event_name}'. Please wait...")
            # Give a small delay for the thread to pick up the stop flag
            self.after(100, self._check_event_stopped, event_name)
        else:
            messagebox.showwarning("Warning", f"Event '{event_name}' is not running.")

    def _check_event_stopped(self, event_name):
        # This is a simple check. A more robust solution would involve joining the thread.
        # For now, we just update the buttons after a short delay.
        self._update_event_control_buttons()
        self._update_status(f"Event '{event_name}' stopped.")

    # --- Core Automation Logic ---
    def run_event(self, event_name):
        event_data = self.events_data.get(event_name)
        if not event_data:
            print(f"Error: Event data for '{event_name}' not found.")
            self.stop_flags[event_name] = True
            self.after(100, self._update_event_control_buttons)
            self.after(0, lambda: self._update_status(f"Error: Event data for '{event_name}' not found."))
            return

        print(f"Running event: {event_name}")
        self.after(0, lambda: self._update_status(f"Running event: {event_name}"))
        while not self.stop_flags[event_name]:
            try:
                # Focus target window
                if not self.focus_window(self.target_window_title):
                    print(f"Warning: Could not focus window '{self.target_window_title}'. Skipping image detection for this cycle.")
                    self.after(0, lambda: self._update_status(f"Warning: Could not focus window '{self.target_window_title}'."))
                    time.sleep(1) # Wait a bit before retrying
                    continue

                # Check each image in the event
                found_and_executed = False
                for image_data in event_data["images"]:
                    if self.stop_flags[event_name]: # Check stop flag again before processing each image
                        break
                    if self.find_image_and_execute(image_data):
                        found_and_executed = True
                        break  # Found and executed, restart loop for next cycle
                
                if not found_and_executed:
                    self.after(0, lambda: self._update_status(f"Event '{event_name}': No images found. Waiting..."))

                time.sleep(0.1)  # Small delay between cycles
            except Exception as e:
                print(f"Error in event '{event_name}': {e}")
                # Optionally, show a messagebox on the main thread
                self.after(0, lambda: messagebox.showerror("Runtime Error", f"Error in event '{event_name}': {e}"))
                self.stop_flags[event_name] = True # Stop the event on error
                self.after(100, self._update_event_control_buttons)
                self.after(0, lambda: self._update_status(f"Error in event '{event_name}': {e}"))
                break # Exit the loop

        print(f"Event '{event_name}' stopped.")
        self.stop_flags[event_name] = True # Ensure flag is set to True on exit
        self.after(100, self._update_event_control_buttons) # Update buttons on main thread
        self.after(0, lambda: self._update_status(f"Event '{event_name}' stopped."))

    def find_image_and_execute(self, image_data):
        try:
            image_path = image_data["path"]
            confidence = image_data["confidence"]
            region = image_data.get("region")

            if not os.path.exists(image_path):
                print(f"Image file not found: {image_path}")
                self.after(0, lambda: self._update_status(f"Error: Image file not found: {image_path}"))
                return False

            location = pyautogui.locateOnScreen(
                image_path,
                confidence=confidence,
                grayscale=True,
                region=region
            )
            if location:
                print(f"Found image: {image_data['name']} at {location}")
                self.after(0, lambda: self._update_status(f"Found image: {image_data['name']}"))
                self.execute_action(image_data["action"], location)
                return True
        except pyautogui.PyAutoGUIException as e:
            print(f"PyAutoGUI Error finding image {image_data['name']}: {e}")
            self.after(0, lambda: self._update_status(f"PyAutoGUI Error finding image {image_data['name']}: {e}"))
        except Exception as e:
            print(f"General Error finding image {image_data['name']}: {e}")
            self.after(0, lambda: self._update_status(f"General Error finding image {image_data['name']}: {e}"))
        return False

    def execute_action(self, action_data, location=None):
        action_type = action_data["type"]
        print(f"Executing action: {action_type}")
        self.after(0, lambda: self._update_status(f"Executing action: {action_type}"))

        try:
            if action_type == "key_press":
                key = action_data.get("key")
                delay = action_data.get("delay", 0.1)
                if key:
                    pyautogui.press(key)
                    time.sleep(delay)
            elif action_type == "key_sequence":
                sequence_str = action_data.get("sequence", "")
                parts = sequence_str.split(',')
                for i in range(0, len(parts), 2):
                    key = parts[i].strip()
                    try:
                        delay = float(parts[i+1].strip()) if i+1 < len(parts) else 0.1
                    except ValueError:
                        delay = 0.1 # Default if delay is not a valid number
                    pyautogui.press(key)
                    time.sleep(delay)
            elif action_type == "mouse_click":
                x = action_data.get("x")
                y = action_data.get("y")
                delay = action_data.get("delay", 0.1)
                if x is not None and y is not None:
                    pyautogui.click(x, y)
                    time.sleep(delay)
                elif location: # If no specific coords, click center of found image
                    pyautogui.click(pyautogui.center(location))
                    time.sleep(delay)
            elif action_type == "mouse_sequence":
                sequence_str = action_data.get("sequence", "")
                parts = sequence_str.split(',')
                for i in range(0, len(parts), 3):
                    try:
                        x = int(parts[i].strip())
                        y = int(parts[i+1].strip())
                        delay = float(parts[i+2].strip()) if i+2 < len(parts) else 0.1
                        pyautogui.click(x, y)
                        time.sleep(delay)
                    except ValueError:
                        print(f"Invalid mouse sequence part: {parts[i:i+3]}")
                        self.after(0, lambda: self._update_status(f"Error: Invalid mouse sequence part: {parts[i:i+3]}"))
                        continue
            elif action_type == "custom_function":
                function_name = action_data.get("function_name")
                parameters = action_data.get("parameters", {})
                if hasattr(self, function_name) and callable(getattr(self, function_name)):
                    # Pass location if available, and parameters
                    getattr(self, function_name)(parameters, location)
                else:
                    print(f"Custom function '{function_name}' not found or not callable.")
                    self.after(0, lambda: self._update_status(f"Error: Custom function '{function_name}' not found."))
            else:
                print(f"Unknown action type: {action_type}")
                self.after(0, lambda: self._update_status(f"Error: Unknown action type: {action_type}"))
        except Exception as e:
            print(f"Error executing action {action_type}: {e}")
            self.after(0, lambda: self._update_status(f"Error executing action {action_type}: {e}"))
            raise # Re-raise to be caught by run_event

    # --- Custom Functions (Examples) ---
    def collect_reward_function(self, params, location):
        print(f"Executing custom function: collect_reward_function with params: {params}")
        self.after(0, lambda: self._update_status(f"Executing custom function: collect_reward_function"))
        # Example: Click multiple reward positions with delays
        # params could contain a list of (x,y,delay) tuples
        if "clicks" in params:
            for click_data in params["clicks"]:
                try:
                    x, y, delay = click_data
                    pyautogui.click(x, y)
                    time.sleep(delay)
                except Exception as e:
                    print(f"Error in collect_reward_function click: {click_data}, Error: {e}")
                    self.after(0, lambda: self._update_status(f"Error in collect_reward_function click: {e}"))
        else:
            # Default behavior if no specific clicks are provided
            if location:
                pyautogui.click(pyautogui.center(location))
                time.sleep(0.5)
            else:
                print("No specific clicks or image location for collect_reward_function.")
                self.after(0, lambda: self._update_status("No specific clicks or image location for collect_reward_function."))

    def battle_sequence_function(self, params, location):
        print(f"Executing custom function: battle_sequence_function with params: {params}")
        self.after(0, lambda: self._update_status(f"Executing custom function: battle_sequence_function"))
        # Example: Execute combat key sequence
        # params could contain a "sequence" string like "a,0.1,s,0.1,d,0.1"
        sequence_str = params.get("sequence", "a,0.1,s,0.1,d,0.1")
        parts = sequence_str.split(',')
        for i in range(0, len(parts), 2):
            try:
                key = parts[i].strip()
                delay = float(parts[i+1].strip()) if i+1 < len(parts) else 0.1
                pyautogui.press(key)
                time.sleep(delay)
            except Exception as e:
                print(f"Error in battle_sequence_function key press: {parts[i:i+2]}, Error: {e}")
                self.after(0, lambda: self._update_status(f"Error in battle_sequence_function key press: {e}"))

    def upgrade_equipment_function(self, params, location):
        print(f"Executing custom function: upgrade_equipment_function with params: {params}")
        self.after(0, lambda: self._update_status(f"Executing custom function: upgrade_equipment_function"))
        # Example: Navigate upgrade menus and confirm
        # params could contain a list of clicks or key presses
        if "steps" in params:
            for step in params["steps"]:
                try:
                    if step["type"] == "click":
                        pyautogui.click(step["x"], step["y"])
                    elif step["type"] == "press":
                        pyautogui.press(step["key"])
                    time.sleep(step.get("delay", 0.5))
                except Exception as e:
                    print(f"Error in upgrade_equipment_function step: {step}, Error: {e}")
                    self.after(0, lambda: self._update_status(f"Error in upgrade_equipment_function step: {e}"))
        else:
            print("No specific steps for upgrade_equipment_function.")
            self.after(0, lambda: self._update_status("No specific steps for upgrade_equipment_function."))

    # --- Window Management ---
    def focus_window(self, window_title):
        try:
            window = gw.getWindowsWithTitle(window_title)
            if window:
                window = window[0]
                if window.isMinimized:
                    window.restore()
                window.activate()
                # print(f"Focused window: {window_title}") # Commented to reduce console spam
                return True
            else:
                # print(f"Window '{window_title}' not found.") # Commented to reduce console spam
                return False
        except Exception as e:
            print(f"Error focusing window '{window_title}': {e}")
            self.after(0, lambda: self._update_status(f"Error focusing window '{window_title}': {e}"))
            return False

    # --- Configuration Management ---
    def _get_config_file_path(self):
        return Path("sf3_automation_config.json")

    def save_config(self):
        config_path = self._get_config_file_path()
        try:
            full_config = {
                "events_data": self.events_data,
                "settings": {
                    "target_window_title": self.target_window_title
                }
            }
            with open(config_path, "w") as f:
                json.dump(full_config, f, indent=4)
            print(f"Configuration saved to {config_path}")
            self._update_status(f"Configuration saved to {config_path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save configuration: {e}")
            self._update_status(f"Save Error: {e}")

    def load_config(self):
        config_path = self._get_config_file_path()
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    full_config = json.load(f)
                self.events_data = full_config.get("events_data", {})
                settings = full_config.get("settings", {})
                self.target_window_title = settings.get("target_window_title", "LDPlayer")

                self._update_event_listbox()
                print(f"Configuration loaded from {config_path}")
                self._update_status(f"Configuration loaded from {config_path}")
            except json.JSONDecodeError as e:
                messagebox.showerror("Load Error", f"Failed to load configuration (Invalid JSON): {e}")
                self._update_status(f"Load Error (Invalid JSON): {e}")
                self.events_data = {} # Reset data if corrupted
            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load configuration: {e}")
                self._update_status(f"Load Error: {e}")
                self.events_data = {} # Reset data if corrupted
        else:
            print("No existing configuration file found. Starting with empty configuration.")
            self._update_status("No existing configuration file found. Starting with empty configuration.")
            self.events_data = {}
        self._update_event_listbox() # Ensure GUI is updated even if no file or error

    def _new_config(self):
        if messagebox.askyesno("New Configuration", "Are you sure you want to start a new configuration? Unsaved changes will be lost."):
            self.events_data = {}
            self.stop_flags = {}
            self.running_threads = {}
            self.target_window_title = "LDPlayer" # Reset to default
            self._update_event_listbox()
            self._clear_image_config_form()
            self._update_event_control_buttons()
            self._update_status("New configuration started.")
            messagebox.showinfo("Info", "New configuration started.")

    def _export_config(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                               filetypes=[("JSON files", "*.json")],
                                               title="Export Configuration As")
        if file_path:
            try:
                full_config = {
                    "events_data": self.events_data,
                    "settings": {
                        "target_window_title": self.target_window_title
                    }
                }
                with open(file_path, "w") as f:
                    json.dump(full_config, f, indent=4)
                messagebox.showinfo("Export Success", f"Configuration exported to {file_path}")
                self._update_status(f"Configuration exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export configuration: {e}")
                self._update_status(f"Export Error: {e}")

    def _import_config(self):
        file_path = filedialog.askopenfilename(title="Import Configuration From",
                                               filetypes=[("JSON files", "*.json")])
        if file_path:
            if messagebox.askyesno("Import Configuration", "Importing will overwrite current configuration. Continue?"):
                try:
                    with open(file_path, "r") as f:
                        imported_full_config = json.load(f)
                    
                    imported_events_data = imported_full_config.get("events_data", {})
                    imported_settings = imported_full_config.get("settings", {})

                    # Basic validation for imported data structure
                    if isinstance(imported_events_data, dict) and all(isinstance(v, dict) and "images" in v for v in imported_events_data.values()):
                        self.events_data = imported_events_data
                        self.target_window_title = imported_settings.get("target_window_title", "LDPlayer")
                        self._update_event_listbox()
                        self.save_config() # Save imported config as current
                        messagebox.showinfo("Import Success", f"Configuration imported from {file_path}")
                        self._update_status(f"Configuration imported from {file_path}")
                    else:
                        messagebox.showerror("Import Error", "Invalid configuration file format.")
                        self._update_status("Import Error: Invalid configuration file format.")
                except json.JSONDecodeError as e:
                    messagebox.showerror("Import Error", f"Invalid JSON format: {e}")
                    self._update_status(f"Import Error (Invalid JSON): {e}")
                except Exception as e:
                    messagebox.showerror("Import Error", f"Failed to import configuration: {e}")
                    self._update_status(f"Import Error: {e}")

    # --- Utility Features ---
    def _screenshot_tool(self):
        messagebox.showinfo("Screenshot Tool", "Click OK, then you will have 3 seconds to switch to the window you want to screenshot. The screenshot will be saved to your desktop.")
        self.after(3000, self._take_screenshot)

    def _take_screenshot(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = Path.home() / "Desktop" / f"screenshot_{timestamp}.png"
            pyautogui.screenshot(str(screenshot_path))
            messagebox.showinfo("Screenshot Saved", f"Screenshot saved to: {screenshot_path}")
            self._update_status(f"Screenshot saved to: {screenshot_path}")
        except Exception as e:
            messagebox.showerror("Screenshot Error", f"Failed to take screenshot: {e}")
            self._update_status(f"Screenshot Error: {e}")

    def _test_image_recognition(self):
        if not self.selected_image_data:
            messagebox.showwarning("Warning", "Please select an image to test recognition.")
            return

        image_data = self.selected_image_data

        messagebox.showinfo("Test Image Recognition", "Click OK, then switch to the window where you expect the image to be visible. The tool will attempt to find the image.")
        self.after(100, lambda: self._perform_image_test(image_data))

    def _perform_image_test(self, image_data):
        try:
            image_path = image_data["path"]
            confidence = image_data["confidence"]
            region = image_data.get("region")

            if not os.path.exists(image_path):
                messagebox.showerror("Error", f"Image file not found: {image_path}")
                self._update_status(f"Error: Image file not found: {image_path}")
                return

            location = pyautogui.locateOnScreen(
                image_path,
                confidence=confidence,
                grayscale=True,
                region=region
            )
            if location:
                messagebox.showinfo("Image Found", f"Image '{image_data['name']}' found at: {location}")
                self._update_status(f"Image '{image_data['name']}' found at: {location}")
                # Optionally, draw a rectangle around it for a brief moment
            else:
                messagebox.showinfo("Image Not Found", f"Image '{image_data['name']}' not found on screen with current settings.")
                self._update_status(f"Image '{image_data['name']}' not found.")
        except pyautogui.PyAutoGUIException as e:
            messagebox.showerror("PyAutoGUI Error", f"Error during image recognition test: {e}")
            self._update_status(f"PyAutoGUI Error during image recognition test: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred during image recognition test: {e}")
            self._update_status(f"Error during image recognition test: {e}")

    def _get_mouse_position(self):
        messagebox.showinfo("Mouse Position Capture", "Move your mouse to the desired position and press SPACEBAR. The coordinates will be displayed.")
        self._update_status("Mouse Position Capture: Press SPACEBAR to capture.")
        
        # Use a separate thread to listen for spacebar press
        def capture_position():
            while True:
                if pyautogui.keyDown('space'):
                    x, y = pyautogui.position()
                    self.after(0, lambda: messagebox.showinfo("Mouse Position", f"X: {x}, Y: {y}"))
                    self.after(0, lambda: self._update_status(f"Mouse Position: X: {x}, Y: {y}"))
                    # Populate mouse click fields if they exist
                    if hasattr(self, 'mouse_x_entry') and hasattr(self, 'mouse_y_entry'):
                        self.after(0, lambda: self.mouse_x_entry.delete(0, tk.END))
                        self.after(0, lambda: self.mouse_x_entry.insert(0, str(x)))
                        self.after(0, lambda: self.mouse_y_entry.delete(0, tk.END))
                        self.after(0, lambda: self.mouse_y_entry.insert(0, str(y)))
                    break
                time.sleep(0.1) # Small delay to prevent busy-waiting

        threading.Thread(target=capture_position, daemon=True).start()

    def _region_selection_helper(self):
        messagebox.showinfo("Region Selection Helper", "Click OK, then you will be able to drag a rectangle on your screen to select a region. Press 'q' to quit the selection.")
        self._update_status("Region Selection Helper: Not fully implemented. Use manual input.")
        
        # This requires a more advanced implementation, possibly using a separate Tkinter Toplevel window
        # or a library like `pyscreeze`'s `locateOnScreen` with `region` parameter and then getting the box.
        # For now, I'll provide a placeholder and suggest manual input or a more complex solution.
        messagebox.showinfo("Note", "Advanced region selection is not fully implemented in this version. Please manually input coordinates or use a separate tool to get them.")
        # A full implementation would involve:
        # 1. Creating a transparent Toplevel window that covers the screen.
        # 2. Binding mouse events (click, drag, release) to draw a rectangle.
        # 3. Getting the coordinates of the drawn rectangle.
        # 4. Populating the region entry fields.

    def _list_available_windows(self):
        try:
            windows = gw.getAllTitles()
            if windows:
                window_list_str = "\n".join(sorted(filter(None, windows))) # Filter out empty titles
                messagebox.showinfo("Available Windows", f"Found Windows:\n{window_list_str}")
                self._update_status("Available Windows listed.")
            else:
                messagebox.showinfo("Available Windows", "No windows found.")
                self._update_status("No windows found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to list windows: {e}")
            self._update_status(f"Error listing windows: {e}")

    def _window_settings(self):
        current_title = self.target_window_title
        new_title = simpledialog.askstring("Window Settings", "Enter target window title:", initialvalue=current_title)
        if new_title:
            self.target_window_title = new_title
            messagebox.showinfo("Window Settings", f"Target window title set to: '{new_title}'. This will be used for focusing the game window.")
            self._update_status(f"Target window title set to: '{new_title}'.")

    # --- Help Menu Callbacks ---
    def _show_about(self):
        messagebox.showinfo("About", "Shadow Fight 3 Automation Tool\nVersion 1.0\nDeveloped by Gemini CLI")

    def _show_help(self):
        help_text = """
        How to Use:
        1. Create Events: Use 'Add Event' to define automation sequences.
        2. Add Images: Select an event, then 'Add Image' to define visual triggers.
        3. Configure Images: For each image, set its path, confidence, region, and action.
           - Action Type: Choose what happens when the image is found.
           - Dynamic Forms: Fill in details based on the selected action type.
        4. Start/Stop Events: Use the buttons at the bottom to run or stop automation for each event.
        
        Tips:
        - Use 'Screenshot Tool' to capture images for recognition.
        - 'Test Image Recognition' helps verify if an image is found.
        - 'Mouse Position Capture' helps get coordinates for mouse actions.
        - Save your configuration regularly!
        """
        messagebox.showinfo("Help", help_text)

    def _on_closing(self):
        if messagebox.askyesno("Quit", "Do you want to save your configuration before quitting?"):
            self.save_config()
        
        # Signal all running threads to stop
        for event_name in list(self.stop_flags.keys()):
            if event_name in self.running_threads and self.running_threads[event_name].is_alive():
                self.stop_flags[event_name] = True
                print(f"Signaling event '{event_name}' to stop.")
        
        # Wait for threads to finish (with a timeout)
        for event_name, thread in list(self.running_threads.items()):
            if thread.is_alive():
                print(f"Waiting for event '{event_name}' thread to finish...")
                thread.join(timeout=1.0) # Give it 1 second to stop
                if thread.is_alive():
                    print(f"Warning: Event '{event_name}' thread did not terminate gracefully.")
        
        self.destroy()


if __name__ == "__main__":
    app = SF3AutomationTool()
    app.mainloop()