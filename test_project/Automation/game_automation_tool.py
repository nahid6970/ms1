import customtkinter as ctk
from customtkinter import CTkInputDialog
from tkinter import filedialog, messagebox
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

class GameAutomationTool(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PyAutoGUI Game Automation Tool - Shadow Fight 3")
        self.geometry("570x800")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # Initialize data structures
        self.events_data = {}
        self.stop_flags = {}
        self.threads = {}
        self.config_file = "sf3_automation_config.json"
        self.target_window = "LDPlayer"
        self.right_frame_visible = False
        self.minimal_window = None

        # Setup GUI
        self.setup_gui()

        # Load existing config
        self.load_config()

        # Bind close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Add a minimize button to the title bar (or a custom one)
        self.minimize_button = ctk.CTkButton(self, text="Minimal Mode", width=100, font=("Jetbrainsmono nfp", 12), corner_radius=0, command=self.show_minimal_mode_window)
        self.minimize_button.place(relx=0.99, rely=0.02, anchor="ne")

        # Bind global hotkey for stopping all events
        if KEYBOARD_AVAILABLE:
            try:
                keyboard.add_hotkey('esc', self.stop_all_events)
                self.log_status("Global hotkey 'ESC' to stop all events is enabled.")
            except Exception as e:
                self.log_status(f"Could not bind ESC hotkey: {e}. Run as administrator if needed.")

        # Start in minimal mode
        self.show_minimal_mode_window()

    def setup_gui(self):
        # Main container
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

        # Left Panel - Event Management
        left_frame = ctk.CTkFrame(self.main_frame, width=400)
        left_frame.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=False, padx=(0, 10))
        left_frame.pack_propagate(False)

        # Event Management Section
        event_label = ctk.CTkLabel(left_frame, text="Events", font=("Arial", 12, "bold"))
        event_label.pack(anchor="w", pady=(0, 5))

        # Event selection frame
        event_select_frame = ctk.CTkFrame(left_frame)
        event_select_frame.pack(fill=ctk.X, pady=(0, 10))

        # Event dropdown
        self.selected_event = ctk.StringVar()
        self.event_dropdown = ctk.CTkOptionMenu(
            event_select_frame,
            variable=self.selected_event,
            values=["No Events"], # Initial dummy value
            corner_radius=0,
            command=self.on_event_select
        )
        self.event_dropdown.pack(side=ctk.LEFT, fill=ctk.X, expand=True, padx=(0, 5))

        # Add event button with + icon
        add_event_btn = ctk.CTkButton(
            event_select_frame,
            text="+ Add",
            corner_radius=0,
            command=self.add_event,
            width=60
        )
        add_event_btn.pack(side=ctk.RIGHT)

        # Event management buttons
        event_btn_frame = ctk.CTkFrame(left_frame)
        event_btn_frame.pack(fill=ctk.X, pady=(0, 10))
        
        # Use grid for better button layout
        event_btn_frame.grid_columnconfigure(0, weight=1)
        event_btn_frame.grid_columnconfigure(1, weight=1)
        event_btn_frame.grid_columnconfigure(2, weight=1)
        event_btn_frame.grid_columnconfigure(3, weight=1)

        ctk.CTkButton(event_btn_frame, text="Rename Event", corner_radius=0, command=self.rename_event).grid(row=0, column=0, padx=(0, 5), sticky="ew")
        ctk.CTkButton(event_btn_frame, text="Event Settings", corner_radius=0, command=self.edit_event_settings).grid(row=0, column=1, padx=(0, 5), sticky="ew")
        ctk.CTkButton(event_btn_frame, text="Duplicate Event", corner_radius=0, command=self.duplicate_event).grid(row=0, column=2, padx=(0, 5), sticky="ew")
        ctk.CTkButton(event_btn_frame, text="Delete Event", corner_radius=0, command=self.delete_event, fg_color="red", hover_color="darkred").grid(row=0, column=3, sticky="ew")

        # Image Management Section
        image_label = ctk.CTkLabel(left_frame, text="Images", font=("Arial", 12, "bold"))
        image_label.pack(anchor="w", pady=(10, 5))

        # Image listbox with scrollbar
        self.image_frame = ctk.CTkScrollableFrame(left_frame)
        self.image_frame.pack(fill=ctk.BOTH, expand=True, pady=(0, 10))

        # Image buttons
        image_btn_frame = ctk.CTkFrame(left_frame)
        image_btn_frame.pack(fill=ctk.X, pady=(0, 10))

        ctk.CTkButton(image_btn_frame, text="Add Image", fg_color="#a8df92", text_color="black", corner_radius=0, font=("Jetbrainsmono nfp", 16, "bold"), command=self.add_image).pack(side=ctk.LEFT, padx=(0, 5))
        ctk.CTkButton(image_btn_frame, text="Add Separator", fg_color="#a8df92", text_color="black", corner_radius=0, font=("Jetbrainsmono nfp", 16, "bold"), command=self.add_separator).pack(side=ctk.LEFT, padx=(0, 5))

        # Control Panel
        control_frame = ctk.CTkFrame(left_frame)
        control_frame.pack(fill=ctk.X, pady=(20, 0))

        control_label = ctk.CTkLabel(control_frame, text="Event Control", font=("Arial", 12, "bold"))
        control_label.pack(anchor="w", pady=(0, 10))

        self.control_buttons_frame = ctk.CTkFrame(control_frame)
        self.control_buttons_frame.pack(fill=ctk.X)

        # Right Panel - Status and Info
        self.right_frame = ctk.CTkFrame(self.main_frame)
        # Don't pack it initially

        # Status Section
        status_label = ctk.CTkLabel(self.right_frame, text="Status & Information", font=("Jetbrainsmono nfp", 12, "bold"))
        status_label.pack(anchor="w", pady=(0, 10))

        # Status text area
        self.status_text = ctk.CTkTextbox(self.right_frame, font=("Jetbrainsmono nfp", 16), wrap=ctk.WORD, height=20)
        self.status_text.pack(fill=ctk.BOTH, expand=True)

        # Toggle button for the right panel
        self.toggle_right_frame_btn = ctk.CTkButton(self, text="Expand Desk", width=100, font=("Jetbrainsmono nfp", 12), corner_radius=0, command=self.toggle_right_frame)
        self.toggle_right_frame_btn.place(relx=0.99, rely=0.06, anchor="ne") # Position below minimal button

        

        # Initialize display
        self.refresh_event_list()
        self.refresh_control_buttons()

    

    def add_event(self):
        dialog = CTkInputDialog(text="Enter event name:", title="Add Event")
        name = dialog.get_input()
        if name and name not in self.events_data:
            self.events_data[name] = {
                "images": [],
                "enabled": True,
                "target_window": self.target_window # Initialize with global default
            }
            self.stop_flags[name] = False
            self.refresh_event_list()
            self.refresh_control_buttons()
            self.save_config()
            self.log_status(f"Added event: {name}")
        elif name in self.events_data:
            messagebox.showerror("Error", "Event name already exists!")

    def delete_event(self):
        event_name = self.selected_event.get()
        if not event_name:
            messagebox.showwarning("Warning", "Please select an event to delete.")
            return

        if messagebox.askyesno("Confirm Delete", f"Delete event '{event_name}'?"):
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
        old_name = self.selected_event.get()
        if not old_name:
            messagebox.showwarning("Warning", "Please select an event to rename.")
            return

        dialog = CTkInputDialog(text=f"Enter new name for '{old_name}':", title="Rename Event")
        new_name = dialog.get_input()

        if new_name and new_name != old_name:
            if new_name in self.events_data:
                messagebox.showerror("Error", "Event name already exists!")
                return

            if old_name in self.threads and self.threads[old_name].is_alive():
                self.stop_event(old_name)

            self.events_data[new_name] = self.events_data.pop(old_name)
            self.stop_flags[new_name] = self.stop_flags.pop(old_name, False)
            if old_name in self.threads:
                self.threads[new_name] = self.threads.pop(old_name)

            self.refresh_event_list()
            self.refresh_control_buttons()
            self.save_config()
            self.log_status(f"Renamed event: {old_name} -> {new_name}")

    def duplicate_event(self):
        old_name = self.selected_event.get()
        if not old_name:
            messagebox.showwarning("Warning", "Please select an event to duplicate.")
            return

        dialog = CTkInputDialog(text=f"Enter name for duplicate of '{old_name}':", title="Duplicate Event")
        new_name = dialog.get_input()

        if new_name and new_name != old_name:
            if new_name in self.events_data:
                messagebox.showerror("Error", "Event name already exists!")
                return

            import copy
            # Create a cleaned version of the event data for deepcopy
            cleaned_event_data = self.events_data[old_name].copy()
            cleaned_images = []
            for img_data in self.events_data[old_name]["images"]:
                cleaned_img_data = img_data.copy()
                cleaned_img_data.pop("_checkbox_ref", None)
                cleaned_img_data.pop("_button_ref", None)
                cleaned_images.append(cleaned_img_data)
            cleaned_event_data["images"] = cleaned_images

            self.events_data[new_name] = copy.deepcopy(cleaned_event_data)
            self.stop_flags[new_name] = False

            self.refresh_event_list()
            self.refresh_control_buttons()
            self.save_config()
            self.log_status(f"Duplicated event: {old_name} -> {new_name}")

    def duplicate_event(self):
        old_name = self.selected_event.get()
        if not old_name:
            messagebox.showwarning("Warning", "Please select an event to duplicate.")
            return

        dialog = CTkInputDialog(text=f"Enter name for duplicate of '{old_name}':", title="Duplicate Event")
        new_name = dialog.get_input()

        if new_name and new_name != old_name:
            if new_name in self.events_data:
                messagebox.showerror("Error", "Event name already exists!")
                return

            import copy
            # Create a cleaned version of the event data for deepcopy
            cleaned_event_data = self.events_data[old_name].copy()
            cleaned_images = []
            for img_data in self.events_data[old_name]["images"]:
                cleaned_img_data = img_data.copy()
                cleaned_img_data.pop("_checkbox_ref", None)
                cleaned_img_data.pop("_button_ref", None)
                cleaned_images.append(cleaned_img_data)
            cleaned_event_data["images"] = cleaned_images

            self.events_data[new_name] = copy.deepcopy(cleaned_event_data)
            self.stop_flags[new_name] = False

            self.refresh_event_list()
            self.refresh_control_buttons()
            self.save_config()
            self.log_status(f"Duplicated event: {old_name} -> {new_name}")

    def edit_event_settings(self):
        event_name = self.selected_event.get()
        if not event_name:
            messagebox.showwarning("Warning", "Please select an event first.")
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Settings for {event_name}")
        dialog.geometry("400x150")
        dialog.transient(self)
        dialog.grab_set()

        current_target_window = self.events_data[event_name].get("target_window", "LDPlayer")
        target_window_var = ctk.StringVar(value=current_target_window)

        ctk.CTkLabel(dialog, text="Target Window Title:").pack(anchor="w", padx=20, pady=(10, 0))
        ctk.CTkEntry(dialog, textvariable=target_window_var, width=300).pack(padx=20, fill=ctk.X)

        def save_settings():
            new_target_window = target_window_var.get()
            self.events_data[event_name]["target_window"] = new_target_window
            self.save_config()
            self.log_status(f"Target window for '{event_name}' set to '{new_target_window}'")
            dialog.destroy()

        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(pady=20)
        ctk.CTkButton(button_frame, text="Save", command=save_settings).pack(side=ctk.LEFT, padx=10)
        ctk.CTkButton(button_frame, text="Cancel", command=dialog.destroy).pack(side=ctk.RIGHT, padx=10)

        dialog.wait_window()

    def add_image(self):
        event_name = self.selected_event.get()
        if not event_name:
            messagebox.showwarning("Warning", "Please select an event first.")
            return
        self.show_image_config_dialog(event_name)

    def edit_image(self, image_index):
        event_name = self.selected_event.get()
        if not event_name:
            messagebox.showwarning("Warning", "Please select an event first.")
            return
        self.show_image_config_dialog(event_name, image_index)

    def delete_image(self, image_index):
        event_name = self.selected_event.get()
        if not event_name:
            messagebox.showwarning("Warning", "Please select an event first.")
            return

        item_to_delete = self.events_data[event_name]["images"][image_index]
        item_type = "image" if item_to_delete.get("type") != "separator" else "separator"
        
        if item_type == "image":
            confirm_message = f"Delete image '{item_to_delete.get('name', 'Untitled')}'?"
        else:
            confirm_message = "Delete this separator?"

        if messagebox.askyesno("Confirm Delete", confirm_message):
            del self.events_data[event_name]["images"][image_index]
            self.save_config()
            self.refresh_image_list()
            self.log_status(f"{item_type.capitalize()} deleted.")

    def duplicate_image(self, image_index):
        event_name = self.selected_event.get()
        if not event_name:
            messagebox.showwarning("Warning", "Please select an event first.")
            return

        destination_event = self.ask_duplicate_destination(event_name)
        if not destination_event:
            return # User cancelled

        import copy
        original_image_data = self.events_data[event_name]["images"][image_index]
        duplicated_image_data = copy.deepcopy(original_image_data)
        duplicated_image_data["name"] = f"{original_image_data['name']} (copy)"

        if destination_event == event_name:
            # Duplicate in the same event
            self.events_data[event_name]["images"].insert(image_index + 1, duplicated_image_data)
        else:
            # Duplicate to another event
            self.events_data[destination_event]["images"].append(duplicated_image_data)

        self.save_config()
        self.refresh_image_list()
        self.log_status(f"Duplicated image '{original_image_data['name']}' to event '{destination_event}'")

    def add_separator(self):
        event_name = self.selected_event.get()
        if not event_name:
            messagebox.showwarning("Warning", "Please select an event first.")
            return

        self.events_data[event_name]["images"].append({"type": "separator"})
        self.save_config()
        self.refresh_image_list()
        self.log_status("Added separator.")

    def ask_duplicate_destination(self, current_event_name):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Duplicate Image")
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()

        result = {"destination": None}

        ctk.CTkLabel(dialog, text="Where do you want to duplicate this image?").pack(pady=10)

        destination_var = ctk.StringVar(value="Current Event")
        current_rb = ctk.CTkRadioButton(dialog, text=f"Current Event ('{current_event_name}')", variable=destination_var, value="Current Event")
        current_rb.pack(anchor="w", padx=20)

        other_events = [name for name in self.events_data.keys() if name != current_event_name]
        other_event_rb = ctk.CTkRadioButton(dialog, text="Another Event", variable=destination_var, value="Another Event", state=ctk.NORMAL if other_events else ctk.DISABLED)
        other_event_rb.pack(anchor="w", padx=20)

        other_event_var = ctk.StringVar()
        if other_events:
            other_event_var.set(other_events[0])

        other_event_dropdown = ctk.CTkOptionMenu(dialog, variable=other_event_var, values=other_events, state=ctk.NORMAL if other_events else ctk.DISABLED)
        other_event_dropdown.pack(padx=40, pady=(0, 10), fill="x")

        def on_ok():
            if destination_var.get() == "Current Event":
                result["destination"] = current_event_name
            else:
                result["destination"] = other_event_var.get()
            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(pady=20)
        ctk.CTkButton(button_frame, text="OK", command=on_ok).pack(side=ctk.LEFT, padx=10)
        ctk.CTkButton(button_frame, text="Cancel", command=on_cancel).pack(side=ctk.RIGHT, padx=10)

        dialog.wait_window()
        return result["destination"]

    def edit_separator(self, index):
        event_name = self.selected_event.get()
        if not event_name:
            messagebox.showwarning("Warning", "Please select an event first.")
            return

        separator_data = self.events_data[event_name]["images"][index]

        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Separator")
        dialog.geometry("300x200")
        dialog.transient(self)
        dialog.grab_set()

        # Thickness
        ctk.CTkLabel(dialog, text="Thickness:").pack(anchor="w", padx=20, pady=(10, 0))
        thickness_var = ctk.StringVar(value=str(separator_data.get("thickness", 2)))
        ctk.CTkEntry(dialog, textvariable=thickness_var).pack(padx=20, fill=ctk.X)

        # Color
        ctk.CTkLabel(dialog, text="Color (e.g., red, #FF0000):").pack(anchor="w", padx=20, pady=(10, 0))
        color_var = ctk.StringVar(value=separator_data.get("color", "gray"))
        ctk.CTkEntry(dialog, textvariable=color_var).pack(padx=20, fill=ctk.X)

        def save_separator_config():
            try:
                thickness = int(thickness_var.get())
                if thickness <= 0:
                    raise ValueError("Thickness must be a positive integer.")
                separator_data["thickness"] = thickness
                separator_data["color"] = color_var.get()
                self.save_config()
                self.refresh_image_list()
                dialog.destroy()
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid input: {e}")

        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(pady=20)
        ctk.CTkButton(button_frame, text="Save", command=save_separator_config).pack(side=ctk.LEFT, padx=10)
        ctk.CTkButton(button_frame, text="Cancel", command=dialog.destroy).pack(side=ctk.RIGHT, padx=10)

        dialog.wait_window()

    def show_image_config_dialog(self, event_name, image_index=None):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Image Configuration")
        dialog.geometry("600x700")
        dialog.transient(self)
        dialog.grab_set()

        # Variables for image data
        image_data = self.events_data[event_name]["images"][image_index] if image_index is not None else {}
        name_var = ctk.StringVar(value=image_data.get("name", ""))
        path_var = ctk.StringVar(value=image_data.get("path", ""))
        confidence_var = ctk.StringVar(value=str(image_data.get("confidence", 0.8)))
        region_data = image_data.get("region")
        x1_var = ctk.StringVar(value=str(region_data[0]) if region_data and len(region_data) > 0 and region_data[0] is not None else "")
        y1_var = ctk.StringVar(value=str(region_data[1]) if region_data and len(region_data) > 1 and region_data[1] is not None else "")
        x2_var = ctk.StringVar(value=str(region_data[2]) if region_data and len(region_data) > 2 and region_data[2] is not None else "")
        y2_var = ctk.StringVar(value=str(region_data[3]) if region_data and len(region_data) > 3 and region_data[3] is not None else "")
        action_type_var = ctk.StringVar(value=image_data.get("action", {}).get("type", "mouse_click"))
        enabled_var = ctk.BooleanVar(value=image_data.get("enabled", True))
        is_folder_var = ctk.BooleanVar(value=image_data.get("is_folder", False))

        # Image Name
        ctk.CTkLabel(dialog, text="Image Name:").pack(anchor="w", padx=20, pady=(10, 0))
        ctk.CTkEntry(dialog, textvariable=name_var, width=570).pack(padx=20, fill=ctk.X)

        # Image Path
        ctk.CTkLabel(dialog, text="Image Path:").pack(anchor="w", padx=20, pady=(10, 0))
        path_frame = ctk.CTkFrame(dialog)
        path_frame.pack(padx=20, fill=ctk.X)
        ctk.CTkEntry(path_frame, textvariable=path_var, width=400).pack(side=ctk.LEFT, fill=ctk.X, expand=True)
        ctk.CTkButton(path_frame, text="Browse", command=lambda: self.browse_image_file(path_var, is_folder_var.get())).pack(side=ctk.RIGHT, padx=(10, 0))

        # Is Folder Checkbox
        ctk.CTkCheckBox(dialog, text="Is Folder (search for any image in this directory)", variable=is_folder_var).pack(anchor="w", padx=20, pady=(5, 0))

        # Confidence
        ctk.CTkLabel(dialog, text="Confidence (0.1-1.0):").pack(anchor="w", padx=20, pady=(10, 0))
        ctk.CTkEntry(dialog, textvariable=confidence_var, width=570).pack(padx=20, fill=ctk.X)

        # Region
        ctk.CTkLabel(dialog, text="Region (x1, y1, x2, y2):").pack(anchor="w", padx=20, pady=(10, 0))
        region_frame = ctk.CTkFrame(dialog)
        region_frame.pack(padx=20, fill=ctk.X)
        ctk.CTkEntry(region_frame, textvariable=x1_var, width=80).pack(side=ctk.LEFT, padx=(0, 5))
        ctk.CTkEntry(region_frame, textvariable=y1_var, width=80).pack(side=ctk.LEFT, padx=(0, 5))
        ctk.CTkEntry(region_frame, textvariable=x2_var, width=80).pack(side=ctk.LEFT, padx=(0, 5))
        ctk.CTkEntry(region_frame, textvariable=y2_var, width=80).pack(side=ctk.LEFT, padx=(0, 5))
        ctk.CTkButton(region_frame, text="Get Region", command=lambda: self.get_screen_region(x1_var, y1_var, x2_var, y2_var)).pack(side=ctk.RIGHT, padx=(10, 0))

        # Action Type
        ctk.CTkLabel(dialog, text="Action Type:").pack(anchor="w", padx=20, pady=(10, 0))
        action_type_options = ["mouse_click", "key_press", "key_sequence", "mouse_sequence", "custom_function", "click_on_found_image"]
        ctk.CTkOptionMenu(dialog, variable=action_type_var, values=action_type_options, command=lambda x: self.on_action_type_select(x, action_frame, image_data.get("action", {}))).pack(padx=20, fill=ctk.X)

        # Action specific inputs frame
        action_frame = ctk.CTkFrame(dialog)
        action_frame.pack(padx=20, pady=(10, 0), fill=ctk.BOTH, expand=True)

        # Enabled Checkbox
        ctk.CTkCheckBox(dialog, text="Enabled", variable=enabled_var).pack(anchor="w", padx=20, pady=(10, 0))

        # Buttons
        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(pady=20)
        ctk.CTkButton(button_frame, text="Save", command=lambda: self.save_image_config(event_name, image_index, name_var.get(), path_var.get(), confidence_var.get(), x1_var.get(), y1_var.get(), x2_var.get(), y2_var.get(), action_type_var.get(), action_frame, enabled_var.get(), is_folder_var.get(), dialog)).pack(side=ctk.LEFT, padx=10)
        ctk.CTkButton(button_frame, text="Cancel", command=dialog.destroy).pack(side=ctk.RIGHT, padx=10)

        # Initial call to set up action fields
        self.on_action_type_select(action_type_var.get(), action_frame, image_data.get("action", {}))

        dialog.wait_window()

    def save_image_config(self, event_name, image_index, name, path, confidence, x1, y1, x2, y2, action_type, action_frame, enabled, is_folder, dialog):
        if not name or not path:
            messagebox.showerror("Error", "Image Name and Path cannot be empty.")
            return

        try:
            confidence = float(confidence)
            if not (0.1 <= confidence <= 1.0):
                raise ValueError("Confidence must be between 0.1 and 1.0")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid Confidence: {e}")
            return

        region = None
        if x1 and y1 and x2 and y2:
            try:
                region = (int(x1), int(y1), int(x2), int(y2))
            except ValueError:
                messagebox.showerror("Error", "Region coordinates must be integers.")
                return

        action = {"type": action_type}
        if action_type == "key_press":
            key = action_frame.key_var.get()
            delay = action_frame.delay_var.get()
            if not key:
                messagebox.showerror("Error", "Key cannot be empty for Key Press action.")
                return
            try:
                delay = float(delay)
            except ValueError:
                messagebox.showerror("Error", "Delay must be a number for Key Press action.")
                return
            action.update({"key": key, "delay": delay})
        elif action_type == "key_sequence":
            sequence = action_frame.sequence_var.get()
            if not sequence:
                messagebox.showerror("Error", "Key Sequence cannot be empty.")
                return
            action.update({"sequence": sequence})
        elif action_type == "mouse_click":
            x = action_frame.x_var.get()
            y = action_frame.y_var.get()
            delay = action_frame.delay_var.get()
            if not x or not y:
                messagebox.showerror("Error", "X and Y coordinates cannot be empty for Mouse Click action.")
                return
            try:
                x = int(x)
                y = int(y)
                delay = float(delay)
            except ValueError:
                messagebox.showerror("Error", "Coordinates and Delay must be numbers for Mouse Click action.")
                return
            action.update({"x": x, "y": y, "delay": delay})
        elif action_type == "mouse_sequence":
            sequence = action_frame.sequence_var.get()
            if not sequence:
                messagebox.showerror("Error", "Mouse Sequence cannot be empty.")
                return
            action.update({"sequence": sequence})
        elif action_type == "custom_function":
            function_name = action_frame.function_var.get()
            params = action_frame.params_var.get()
            if not function_name:
                messagebox.showerror("Error", "Function Name cannot be empty for Custom Function action.")
                return
            try:
                json.loads(params) # Validate JSON
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Parameters must be a valid JSON string.")
                return
            action.update({"function": function_name, "params": params})

        image_data = {
            "name": name,
            "path": path,
            "confidence": confidence,
            "region": region,
            "action": action,
            "enabled": enabled,
            "is_folder": is_folder
        }

        if image_index is None:
            # Add new image
            self.events_data[event_name]["images"].append(image_data)
            self.log_status(f"Added image '{name}' to event '{event_name}'")
        else:
            # Update existing image
            self.events_data[event_name]["images"][image_index] = image_data
            self.log_status(f"Updated image '{name}' in event '{event_name}'")

        self.save_config()
        self.refresh_image_list()
        dialog.destroy()

    def browse_image_file(self, path_var, is_folder=False):
        if is_folder:
            dirname = filedialog.askdirectory(
                title="Select Image Folder"
            )
            if dirname:
                path_var.set(dirname)
        else:
            filename = filedialog.askopenfilename(
                title="Select Image File",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*")]
            )
            if filename:
                path_var.set(filename)

    def get_screen_region(self, x1_var, y1_var, x2_var, y2_var):
        if not KEYBOARD_AVAILABLE:
            messagebox.showerror("Error", "Keyboard module not available. Cannot capture region.")
            return

        messagebox.showinfo("Get Region", "Move mouse to first corner and press SPACE. Then move to second corner and press SPACE again.")
        self.log_status("Waiting for SPACE key for first corner...")

        def capture_region_thread():
            try:
                keyboard.wait('space')
                x1, y1 = pyautogui.position()
                self.log_status(f"First corner captured: ({x1}, {y1})")
                x1_var.set(x1)
                y1_var.set(y1)

                self.log_status("Waiting for SPACE key for second corner...")
                keyboard.wait('space')
                x2, y2 = pyautogui.position()
                self.log_status(f"Second corner captured: ({x2}, {y2})")
                x2_var.set(x2)
                y2_var.set(y2)

                messagebox.showinfo("Region Captured", f"Region: ({x1}, {y1}, {x2}, {y2})")
            except Exception as e:
                self.log_status(f"Error capturing region: {str(e)}")
                messagebox.showerror("Error", f"Failed to capture region: {str(e)}")

        threading.Thread(target=capture_region_thread, daemon=True).start()

    def get_click_position(self, x_var, y_var):
        if not KEYBOARD_AVAILABLE:
            messagebox.showerror("Error", "Keyboard module not available. Cannot capture position.")
            return

        messagebox.showinfo("Get Position", "Move mouse to desired position and press SPACE.")
        self.log_status("Waiting for SPACE key for position...")

        def capture_position_thread():
            try:
                keyboard.wait('space')
                x, y = pyautogui.position()
                self.log_status(f"Position captured: ({x}, {y})")
                x_var.set(x)
                y_var.set(y)
                messagebox.showinfo("Position Captured", f"Position: ({x}, {y})")
            except Exception as e:
                self.log_status(f"Error capturing position: {str(e)}")
                messagebox.showerror("Error", f"Failed to capture position: {str(e)}")

        threading.Thread(target=capture_position_thread, daemon=True).start()

    def on_action_type_select(self, action_type, action_frame, initial_action_data=None):
        # Clear existing widgets in the action_frame
        for widget in action_frame.winfo_children():
            widget.destroy()

        if initial_action_data is None:
            initial_action_data = {}

        if action_type == "key_press":
            ctk.CTkLabel(action_frame, text="Key:").pack(anchor="w", padx=5, pady=(5, 0))
            key_var = ctk.StringVar(value=initial_action_data.get("key", ""))
            ctk.CTkEntry(action_frame, textvariable=key_var).pack(fill=ctk.X, padx=5)
            ctk.CTkLabel(action_frame, text="Delay (seconds):").pack(anchor="w", padx=5, pady=(5, 0))
            delay_var = ctk.StringVar(value=str(initial_action_data.get("delay", 0.1)))
            ctk.CTkEntry(action_frame, textvariable=delay_var).pack(fill=ctk.X, padx=5)
            action_frame.key_var = key_var
            action_frame.delay_var = delay_var

        elif action_type == "key_sequence":
            ctk.CTkLabel(action_frame, text="Key Sequence (key1,delay1,key2,delay2,...):").pack(anchor="w", padx=5, pady=(5, 0))
            sequence_var = ctk.StringVar(value=initial_action_data.get("sequence", ""))
            ctk.CTkEntry(action_frame, textvariable=sequence_var).pack(fill=ctk.X, padx=5)
            action_frame.sequence_var = sequence_var

        elif action_type == "mouse_click":
            ctk.CTkLabel(action_frame, text="X Coordinate:").pack(anchor="w", padx=5, pady=(5, 0))
            x_var = ctk.StringVar(value=str(initial_action_data.get("x", "")))
            ctk.CTkEntry(action_frame, textvariable=x_var).pack(fill=ctk.X, padx=5)
            ctk.CTkLabel(action_frame, text="Y Coordinate:").pack(anchor="w", padx=5, pady=(5, 0))
            y_var = ctk.StringVar(value=str(initial_action_data.get("y", "")))
            ctk.CTkEntry(action_frame, textvariable=y_var).pack(fill=ctk.X, padx=5)
            ctk.CTkButton(action_frame, text="Get Position", command=lambda: self.get_click_position(x_var, y_var)).pack(pady=(5, 0))
            ctk.CTkLabel(action_frame, text="Delay (seconds):").pack(anchor="w", padx=5, pady=(5, 0))
            delay_var = ctk.StringVar(value=str(initial_action_data.get("delay", 0.1)))
            ctk.CTkEntry(action_frame, textvariable=delay_var).pack(fill=ctk.X, padx=5)
            action_frame.x_var = x_var
            action_frame.y_var = y_var
            action_frame.delay_var = delay_var

        elif action_type == "mouse_sequence":
            ctk.CTkLabel(action_frame, text="Mouse Sequence (x1,y1,delay1,x2,y2,delay2,...):").pack(anchor="w", padx=5, pady=(5, 0))
            sequence_var = ctk.StringVar(value=initial_action_data.get("sequence", ""))
            ctk.CTkEntry(action_frame, textvariable=sequence_var).pack(fill=ctk.X, padx=5)
            action_frame.sequence_var = sequence_var

        elif action_type == "custom_function":
            ctk.CTkLabel(action_frame, text="Function Name:").pack(anchor="w", padx=5, pady=(5, 0))
            function_var = ctk.StringVar(value=initial_action_data.get("function", ""))
            ctk.CTkEntry(action_frame, textvariable=function_var).pack(fill=ctk.X, padx=5)
            ctk.CTkLabel(action_frame, text="Parameters (JSON string):").pack(anchor="w", padx=5, pady=(5, 0))
            params_var = ctk.StringVar(value=initial_action_data.get("params", "{}"))
            ctk.CTkEntry(action_frame, textvariable=params_var).pack(fill=ctk.X, padx=5)
            action_frame.function_var = function_var
            action_frame.params_var = params_var

        elif action_type == "click_on_found_image":
            # No specific inputs needed for this action type
            pass

    def on_event_select(self, event):
        self.refresh_image_list()

    def refresh_event_list(self):
        current_selection = self.selected_event.get()
        event_names = list(self.events_data.keys())
        if not event_names:
            event_names = ["No Events"] # Placeholder if no events exist

        # Update the values of the OptionMenu
        self.event_dropdown.configure(values=event_names)

        if current_selection in event_names and current_selection != "No Events":
            self.selected_event.set(current_selection)
        elif event_names and event_names[0] != "No Events":
            self.selected_event.set(event_names[0])
        else:
            self.selected_event.set("No Events")
        self.update_idletasks()
        self.refresh_image_list() # Refresh image list when event list changes

    def refresh_image_list(self):
        for widget in self.image_frame.winfo_children():
            widget.destroy()

        event_name = self.selected_event.get()
        self.selected_image_index = None  # Reset selection

        if event_name and event_name in self.events_data:
            images = self.events_data[event_name]["images"]
            for i, image_data in enumerate(images):
                if image_data.get("type") == "separator":
                    separator_entry_frame = ctk.CTkFrame(self.image_frame)
                    separator_entry_frame.pack(fill=ctk.X, pady=2)

                    thickness = image_data.get("thickness", 2)
                    color = image_data.get("color", "gray")

                    # Separator line
                    separator_line = ctk.CTkFrame(separator_entry_frame, height=thickness, fg_color=color)
                    separator_line.pack(side=ctk.LEFT, padx=(5, 0), expand=True, fill=ctk.X)

                    # Move button for separator
                    move_btn = ctk.CTkButton(
                        separator_entry_frame,
                        text="↕", # Up-Down arrow
                        font=("Jetbrainsmono nfp", 16), corner_radius=0,
                        width=25,
                        fg_color="#212121",
                        text_color="#5cf25c"
                    )
                    move_btn.pack(side=ctk.LEFT, padx=(5, 0))
                    move_btn.bind("<Button-1>", lambda event, idx=i: self.move_image_up(idx))
                    move_btn.bind("<Button-3>", lambda event, idx=i: self.move_image_down(idx))

                    # Edit button for separator
                    edit_btn = ctk.CTkButton(
                        separator_entry_frame,
                        text="\uf044", # Edit icon
                        font=("Jetbrainsmono nfp", 16), corner_radius=0,
                        command=lambda idx=i: self.edit_separator(idx),
                        width=25,
                        fg_color="#212121",
                        text_color="#6ca8fa"
                    )
                    edit_btn.pack(side=ctk.LEFT, padx=(5, 0))

                    # Delete button for separator
                    delete_btn = ctk.CTkButton(
                        separator_entry_frame,
                        text="\uf00d", # Delete icon
                        font=("Jetbrainsmono nfp", 16), corner_radius=0,
                        command=lambda idx=i: self.delete_image(idx),
                        fg_color="#212121",
                        hover_color="darkred",
                        text_color="red",
                        width=25,
                    )
                    delete_btn.pack(side=ctk.LEFT, padx=(5, 5))

                else:
                    image_entry_frame = ctk.CTkFrame(self.image_frame)
                    image_entry_frame.pack(fill=ctk.X, pady=2)

                    checkbox_var = ctk.BooleanVar(value=image_data.get("enabled", True))
                    checkbox = ctk.CTkCheckBox(
                        image_entry_frame,
                        text=image_data["name"],
                        variable=checkbox_var,
                        command=lambda idx=i, var=checkbox_var: self.toggle_image_enabled(idx, var.get())
                    )
                    checkbox.pack(side=ctk.LEFT, padx=(5, 0), expand=True, fill=ctk.X)

                    move_btn = ctk.CTkButton(
                        image_entry_frame,
                        text="\uf0dc", # Up-Down arrow
                        font=("Jetbrainsmono nfp", 16), corner_radius=0,
                        width=25,
                        fg_color="#212121",
                        text_color="#5cf25c"
                    )
                    move_btn.pack(side=ctk.LEFT, padx=(5, 0))

                    # Bind left-click to move up and right-click to move down
                    move_btn.bind("<Button-1>", lambda event, idx=i: self.move_image_up(idx))
                    move_btn.bind("<Button-3>", lambda event, idx=i: self.move_image_down(idx))

                    edit_btn = ctk.CTkButton(
                        image_entry_frame,
                        text="\uf044",
                        font=("Jetbrainsmono nfp", 16), corner_radius=0,
                        command=lambda idx=i: self.edit_image(idx),
                        width=25,
                        fg_color="#212121",
                        text_color="#6ca8fa"
                    )
                    edit_btn.pack(side=ctk.LEFT, padx=(5, 0))

                    duplicate_btn = ctk.CTkButton(
                        image_entry_frame,
                        text="\uf4c4",
                        font=("Jetbrainsmono nfp", 16), corner_radius=0,
                        command=lambda idx=i: self.duplicate_image(idx),
                        width=25,
                        fg_color="#212121",
                        text_color="#f2d21c"
                    )
                    duplicate_btn.pack(side=ctk.LEFT, padx=(5, 0))

                    delete_btn = ctk.CTkButton(
                        image_entry_frame,
                        text="\uf00d",
                        font=("Jetbrainsmono nfp", 16), corner_radius=0,
                        command=lambda idx=i: self.delete_image(idx),
                        fg_color="#212121",
                        hover_color="darkred",
                        text_color="red",
                        width=25,
                    )
                    delete_btn.pack(side=ctk.LEFT, padx=(5, 5))
        self.update_idletasks()

    

    def toggle_image_enabled(self, index, enabled):
        event_name = self.selected_event.get()
        if not event_name or event_name not in self.events_data:
            return

        if 0 <= index < len(self.events_data[event_name]["images"]):
            self.events_data[event_name]["images"][index]["enabled"] = enabled
            self.save_config()
            self.log_status(f"Image '{self.events_data[event_name]["images"][index]["name"]}' enabled set to {enabled}")

    def move_image_up(self, index, event=None):
        event_name = self.selected_event.get()
        if not event_name or event_name not in self.events_data:
            return

        if index > 0:
            images = self.events_data[event_name]["images"]
            images.insert(index - 1, images.pop(index))
            self.save_config()
            self.log_status("Image moved up.")
            # Debounce refresh_image_list
            if hasattr(self, '_refresh_image_list_after_id'):
                self.after_cancel(self._refresh_image_list_after_id)
            self._refresh_image_list_after_id = self.after(100, self.refresh_image_list)

    def move_image_down(self, index, event=None):
        event_name = self.selected_event.get()
        if not event_name or event_name not in self.events_data:
            return

        images = self.events_data[event_name]["images"]
        if index < len(images) - 1:
            images.insert(index + 1, images.pop(index))
            self.save_config()
            self.log_status("Image moved down.")
            # Debounce refresh_image_list
            if hasattr(self, '_refresh_image_list_after_id'):
                self.after_cancel(self._refresh_image_list_after_id)
            self._refresh_image_list_after_id = self.after(100, self.refresh_image_list)

    def refresh_control_buttons(self):
        for widget in self.control_buttons_frame.winfo_children():
            widget.destroy()

        for i, event_name in enumerate(self.events_data.keys()):
            is_running = event_name in self.threads and self.threads[event_name].is_alive()
            button_text = f"Stop {event_name}" if is_running else f"{event_name}"

            btn = ctk.CTkButton(
                self.control_buttons_frame,
                text=button_text,
                command=lambda name=event_name: self.toggle_event(name),
                width=20,
                fg_color="red" if is_running else "#3B8ED0", # Red when running, default otherwise
                hover_color="darkred" if is_running else "#325882", # Darker red when running, default otherwise
                font=("Jetbrainsmono nfp", 16, "bold"), corner_radius=0,
                text_color="#442f1e"
            )
            btn.pack(pady=2, fill=ctk.X)
        self.update_idletasks()

    def refresh_minimal_control_buttons(self):
        if not self.minimal_window:
            return

        for widget in self.minimal_control_frame.winfo_children():
            widget.destroy()

        for i, event_name in enumerate(self.events_data.keys()):
            is_running = event_name in self.threads and self.threads[event_name].is_alive()
            button_text = f"Stop {event_name}" if is_running else f"{event_name}"
            btn = ctk.CTkButton(
                self.minimal_control_frame,
                text=button_text,
                command=lambda name=event_name: self.toggle_event(name),
                width=100,
                fg_color="red" if is_running else "#3B8ED0",
                hover_color="darkred" if is_running else "#325882",
                font=("Jetbrainsmono nfp", 12, "bold"), corner_radius=0,
                text_color="#442f1e"
            )
            btn.pack(side=ctk.LEFT, padx=5, pady=5)

    def toggle_event(self, event_name):
        if event_name in self.threads and self.threads[event_name].is_alive():
            self.stop_event(event_name)
        else:
            self.start_event(event_name)
        self.refresh_control_buttons()
        self.refresh_minimal_control_buttons()

    def start_event(self, event_name):
        if not self.events_data[event_name]["images"]:
            messagebox.showwarning("Warning", f"Event '{event_name}' has no images configured.")
            return

        self.stop_flags[event_name] = False
        self.threads[event_name] = threading.Thread(target=self.run_event, args=(event_name,), daemon=True)
        self.threads[event_name].start()
        self.log_status(f"Started event: {event_name}")

    def stop_event(self, event_name):
        self.stop_flags[event_name] = True
        self.log_status(f"Stopped event: {event_name}")
        self.after(100, self.refresh_minimal_control_buttons)

    def run_event(self, event_name):
        event_data = self.events_data[event_name]
        event_target_window = event_data.get("target_window", self.target_window) # Use event-specific or global default
        try:
            while not self.stop_flags[event_name]:
                try:
                    self.focus_window(event_target_window)
                    for image_data in event_data["images"]:
                        if self.stop_flags[event_name]:
                            break
                        if image_data.get("type") == "separator": # Skip separators
                            continue
                        if image_data.get("enabled", True): # Only process if enabled
                            if self.find_image_and_execute(image_data):
                                self.log_status(f"Found and executed: {image_data['name']} in {event_name}")
                                break
                    time.sleep(0.1)
                except Exception as e:
                    self.log_status(f"Error in event {event_name}: {str(e)}")
                    time.sleep(1)
        finally:
            # Ensure the thread is removed from the active threads list when it finishes
            if event_name in self.threads:
                del self.threads[event_name]
            self.after(100, self.refresh_control_buttons) # Refresh UI after thread truly stops
            self.after(100, self.refresh_minimal_control_buttons)

    def find_image_and_execute(self, image_data):
        try:
            location = None
            if image_data.get("is_folder", False):
                # Search for any image in the specified folder
                image_folder = image_data["path"]
                for filename in os.listdir(image_folder):
                    if filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
                        full_path = os.path.join(image_folder, filename)
                        try:
                            location = pyautogui.locateOnScreen(
                                full_path,
                                confidence=image_data["confidence"],
                                grayscale=True,
                                region=image_data.get("region")
                            )
                            if location:
                                self.log_status(f"Found image '{filename}' in folder '{image_folder}'")
                                break # Found an image, no need to search further in this folder
                        except pyautogui.ImageNotFoundException:
                            continue # Image not found, try next one in folder
            else:
                # Search for a single image file
                location = pyautogui.locateOnScreen(
                    image_data["path"],
                    confidence=image_data["confidence"],
                    grayscale=True,
                    region=image_data.get("region")
                )

            if location:
                self.execute_action(image_data["action"], location)
                return True
        except pyautogui.ImageNotFoundException:
            pass
        except Exception as e:
            self.log_status(f"Error finding image {image_data['name']}: {str(e)}")
        return False

    def execute_action(self, action, found_location=None):
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
            elif action_type == "click_on_found_image":
                if found_location:
                    x, y, w, h = found_location
                    center_x = x + w // 2
                    center_y = y + h // 2
                    pyautogui.click(center_x, center_y)
                    time.sleep(action.get("delay", 0.1)) # Add a small delay after clicking
                else:
                    self.log_status("Error: No image location provided for 'click_on_found_image' action.")
        except Exception as e:
            self.log_status(f"Error executing action: {str(e)}")

    def execute_custom_function(self, function_name, params, window):
        try:
            params_dict = json.loads(params) if isinstance(params, str) else params
            self.log_status(f"Custom function '{function_name}' called with params: {params_dict}")
            if function_name == "collect_reward":
                self.log_status("Executing collect_reward function")
            elif function_name == "battle_sequence":
                self.log_status("Executing battle_sequence function")
            elif function_name == "upgrade_equipment":
                self.log_status("Executing upgrade_equipment function")
            else:
                self.log_status(f"Custom function '{function_name}' not implemented")
                self.log_status("Add your custom function logic in execute_custom_function method")
        except Exception as e:
            self.log_status(f"Error in custom function {function_name}: {str(e)}")

    def focus_window(self, window_title):
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
        messagebox.showinfo("Mouse Position", "Move mouse to desired position and press SPACE to capture coordinates.")
        def capture_position():
            try:
                if KEYBOARD_AVAILABLE:
                    keyboard.wait('space')
                    x, y = pyautogui.position()
                    self.log_status(f"Mouse position captured: ({x}, {y})")
                    messagebox.showinfo("Position Captured", f"Mouse position: ({x}, {y})")
                else:
                    messagebox.showinfo("Mouse Position", "Keyboard module not available. Click at desired position.")
                    # Fallback implementation
            except Exception as e:
                self.log_status(f"Error capturing mouse position: {str(e)}")
        threading.Thread(target=capture_position, daemon=True).start()

    def test_image_recognition(self):
        filename = filedialog.askopenfilename(
            title="Select Image to Test",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*")]
        )
        if filename:
            dialog = CTkInputDialog(text="Enter confidence level (0.1-1.0):", title="Confidence", initialvalue=0.8)
            confidence = dialog.get_input()
            if confidence:
                try:
                    location = pyautogui.locateOnScreen(filename, confidence=float(confidence), grayscale=True)
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
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        self.status_text.insert(ctk.END, log_message)
        self.status_text.see(ctk.END)
        lines = self.status_text.get("1.0", ctk.END).split("\n")
        if len(lines) > 1000:
            self.status_text.delete("1.0", f"{len(lines) - 1000}.0")

    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.events_data = data.get("events", {})
                    # Iterate through events to set stop_flags and ensure target_window is present
                    for event_name, event_data in self.events_data.items():
                        self.stop_flags[event_name] = False
                        if "target_window" not in event_data:
                            event_data["target_window"] = self.target_window # Set default if not present
                self.log_status(f"Configuration loaded from {self.config_file}")
                self.refresh_event_list()
                self.refresh_control_buttons()
                self.refresh_image_list()
            else:
                self.log_status("No existing configuration found, starting fresh")
        except Exception as e:
            self.log_status(f"Error loading configuration: {str(e)}")
            messagebox.showerror("Error", f"Failed to load configuration: {str(e)}")

    def save_config(self):
        try:
            # Create a deep copy to avoid modifying the live data structure during cleanup
            data_to_save = {"events": {}, "target_window": self.target_window}
            for event_name, event_data in self.events_data.items():
                copied_event_data = event_data.copy()
                copied_event_data.pop("target_window", None) # Remove target_window from top-level if it exists
                copied_event_data["images"] = []
                for image_data in event_data["images"]:
                    cleaned_image_data = image_data.copy()
                    cleaned_image_data.pop("_checkbox_ref", None) # Remove the UI widget reference
                    cleaned_image_data.pop("_button_ref", None) # Remove old UI widget reference if it exists
                    copied_event_data["images"].append(cleaned_image_data)
                data_to_save["events"][event_name] = copied_event_data

            with open(self.config_file, 'w') as f:
                json.dump(data_to_save, f, indent=2)
            self.log_status(f"Configuration saved to {self.config_file}")
        except Exception as e:
            self.log_status(f"Error saving configuration: {str(e)}")
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")

    def new_config(self):
        if messagebox.askyesno("New Configuration", "This will clear all current events. Continue?"):
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
        filename = filedialog.askopenfilename(
            title="Open Configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                for event_name in list(self.threads.keys()):
                    if self.threads[event_name].is_alive():
                        self.stop_event(event_name)
                self.events_data = data.get("events", {})
                self.target_window = data.get("target_window", "LDPlayer")
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
        filename = filedialog.askopenfilename(
            title="Import Configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
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
        dialog = CTkInputDialog(text="Enter target window title:", title="Window Settings", initialvalue=self.target_window)
        new_window = dialog.get_input()
        if new_window:
            self.target_window = new_window
            self.save_config()
            self.log_status(f"Target window set to: {self.target_window}")

    def list_windows(self):
        try:
            windows = gw.getAllWindows()
            window_list = []
            for window in windows:
                if window.title.strip():
                    window_list.append(f"'{window.title}' - Size: {window.width}x{window.height}")
            if window_list:
                window_text = "\n".join(window_list[:20])
                if len(window_list) > 20:
                    window_text += f"\n... and {len(window_list) - 20} more windows"
                messagebox.showinfo("Available Windows", window_text)
            else:
                messagebox.showinfo("Available Windows", "No windows found")
        except Exception as e:
            self.log_status(f"Error listing windows: {str(e)}")
            messagebox.showerror("Error", f"Failed to list windows: {str(e)}")

    def show_about(self):
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
        help_text = """How to use the Game Automation Tool:
1. CREATE EVENT: Click '+ Add' to create a new automation event
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
        for event_name in list(self.threads.keys()):
            if self.threads[event_name].is_alive():
                self.stop_event(event_name)
        time.sleep(0.5)
        self.save_config()
        if KEYBOARD_AVAILABLE:
            try:
                keyboard.unhook_all_hotkeys()
                self.log_status("Unhooked all hotkeys.")
            except Exception as e:
                self.log_status(f"Error unhooking hotkeys: {e}")
        self.destroy()

    def toggle_right_frame(self):
        self.right_frame_visible = not self.right_frame_visible
        if self.right_frame_visible:
            self.geometry("1200x800")
            self.right_frame.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True)
            self.toggle_right_frame_btn.configure(text="Shrink")
        else:
            self.right_frame.pack_forget()
            self.geometry("570x800")
            self.toggle_right_frame_btn.configure(text="Expand Desk")

    def show_minimal_mode_window(self):
        self.withdraw() # Hide the main window

        self.minimal_window = ctk.CTkToplevel(self)
        self.minimal_window.title("Minimal Mode")
        # Calculate top-center position
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 400
        window_height = 100

        x = (screen_width // 2) - (window_width // 2)
        y = 0 # Top of the screen

        self.minimal_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.minimal_window.transient(self)
        self.minimal_window.overrideredirect(True) # Remove default title bar

        # Custom drag functionality
        self.minimal_window.x = 0
        self.minimal_window.y = 0

        def start_drag(event):
            self.minimal_window.x = event.x
            self.minimal_window.y = event.y

        def do_drag(event):
            deltax = event.x - self.minimal_window.x
            deltay = event.y - self.minimal_window.y
            x = self.minimal_window.winfo_x() + deltax
            y = self.minimal_window.winfo_y() + deltay
            self.minimal_window.geometry(f"{{self.minimal_window_initial_width}}x{{self.minimal_window_initial_height}}+{x}+{y}")

        self.minimal_window.bind("<Button-1>", start_drag)
        self.minimal_window.bind("<B1-Motion>", do_drag)

        def on_minimal_close():
            self.deiconify() # Show the main window again
            self.minimal_window.destroy()
            self.minimal_window = None

        self.minimal_window.protocol("WM_DELETE_WINDOW", on_minimal_close)

        # Main container frame in the minimal window
        container_frame = ctk.CTkFrame(self.minimal_window)
        container_frame.pack(fill=ctk.X, padx=(0,5))

        # Configure grid for container_frame
        container_frame.grid_columnconfigure(0, weight=1) # Column for event buttons
        container_frame.grid_columnconfigure(1, weight=0) # Column for restore button
        container_frame.grid_columnconfigure(2, weight=0) # Column for close button
        container_frame.grid_rowconfigure(0, weight=0) # Row for content, prevent vertical expansion

        # Frame for the event buttons that will be refreshed
        self.minimal_control_frame = ctk.CTkFrame(container_frame)
        self.minimal_control_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        # Restore button in the main container, won't be cleared
        restore_btn = ctk.CTkButton(container_frame, text="\uf2d2", font=("Jetbrainsmono nfp", 12), corner_radius=0, command=on_minimal_close, width=40)
        restore_btn.grid(row=0, column=1, sticky="e", padx=(0, 5))

        # Close button in the main container
        close_btn = ctk.CTkButton(container_frame, text="\uf00d", font=("Jetbrainsmono nfp", 12), corner_radius=0, command=self.on_closing, width=40, fg_color="red", hover_color="darkred")
        close_btn.grid(row=0, column=2, sticky="e", padx=(0, 0))

        self.refresh_minimal_control_buttons() # Initial population of the event buttons

        # Calculate and set the window size based on content
        self.minimal_window.update_idletasks() # Update to get correct sizes
        req_width = self.minimal_window.winfo_reqwidth()
        req_height = self.minimal_window.winfo_reqheight()

        # Calculate top-center position based on actual content size
        screen_width = self.winfo_screenwidth()
        x = (screen_width // 2) - (req_width // 2)
        y = 0 # Top of the screen

        self.minimal_window.geometry(f"{req_width}x{req_height}+{x}+{y}")

        # Store initial dimensions for dragging
        self.minimal_window_initial_width = req_width
        self.minimal_window_initial_height = req_height

    

    def stop_all_events(self):
        self.log_status("ESC pressed: Stopping all running events...")
        for event_name in list(self.threads.keys()):
            if self.threads[event_name].is_alive():
                self.stop_event(event_name)
        self.after(100, self.refresh_control_buttons) # Refresh UI after all events are stopped
        self.after(100, self.refresh_minimal_control_buttons)

def main():
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
    app = GameAutomationTool()
    app.mainloop()

if __name__ == "__main__":
    main()
