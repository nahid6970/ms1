import customtkinter as ctk
from tkinter import messagebox
import json
import os

# Set the appearance mode and default color theme
ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "dark-blue", "green"

KOMOREBI_JSON_PATH = "C:/ms1/asset/komorebi/komorebi.json"

class AddEditDialog(ctk.CTkToplevel):
    def __init__(self, master, item_type, item_data=None):
        super().__init__(master)
        self.master = master
        self.item_type = item_type  # "float" or "tray"
        self.item_data = item_data  # None for add, dict for edit
        self.transient(master)  # Make dialog appear on top of main window
        self.grab_set()  # Make it a modal window
        self.geometry("400x180") # Set the size of the dialog window

        if self.item_data:
            self.title(f"Edit {item_type.capitalize()} Item")
        else:
            self.title(f"Add New {item_type.capitalize()} Item")

        self.kind_entry = ctk.CTkEntry(self, placeholder_text="Kind (e.g., Exe, Class, Title)")
        self.kind_entry.pack(padx=20, pady=5, fill="x")
        self.id_entry = ctk.CTkEntry(self, placeholder_text="ID (e.g., notepad.exe)")
        self.id_entry.pack(padx=20, pady=5, fill="x")
        self.matching_strategy_entry = ctk.CTkEntry(self, placeholder_text="Matching Strategy (e.g., Equals, Contains)")
        self.matching_strategy_entry.pack(padx=20, pady=5, fill="x")

        if self.item_data:
            self.kind_entry.insert(0, self.item_data.get("kind", ""))
            self.id_entry.insert(0, self.item_data.get("id", ""))
            self.matching_strategy_entry.insert(0, self.item_data.get("matching_strategy", ""))
            save_button = ctk.CTkButton(self, text="Save Changes", command=self.save_changes)
        else:
            save_button = ctk.CTkButton(self, text="Add Item", command=self.add_item)
        save_button.pack(padx=20, pady=10)

    def add_item(self):
        kind = self.kind_entry.get().strip()
        item_id = self.id_entry.get().strip()
        matching_strategy = self.matching_strategy_entry.get().strip()

        if not kind or not item_id or not matching_strategy:
            messagebox.showwarning("Warning", "All fields are required.", parent=self)
            return

        new_item = {"kind": kind, "id": item_id, "matching_strategy": matching_strategy}

        if self.item_type == "float":
            if new_item not in self.master.config_data.get("float_rules", []):
                self.master.config_data.setdefault("float_rules", []).append(new_item)
            else:
                messagebox.showwarning("Warning", "This float rule already exists.", parent=self)
                return
        elif self.item_type == "tray":
            if new_item not in self.master.config_data.get("tray_and_multi_window_applications", []):
                self.master.config_data.setdefault("tray_and_multi_window_applications", []).append(new_item)
            else:
                messagebox.showwarning("Warning", "This application already exists.", parent=self)
                return

        self.master.update_list_displays()
        self.destroy()  # Close dialog

    def save_changes(self):
        kind = self.kind_entry.get().strip()
        item_id = self.id_entry.get().strip()
        matching_strategy = self.matching_strategy_entry.get().strip()

        if not kind or not item_id or not matching_strategy:
            messagebox.showwarning("Warning", "All fields are required.", parent=self)
            return

        updated_item = {"kind": kind, "id": item_id, "matching_strategy": matching_strategy}

        if self.item_type == "float":
            try:
                index = self.master.config_data["float_rules"].index(self.item_data)
                self.master.config_data["float_rules"][index] = updated_item
            except ValueError:
                messagebox.showerror("Error", "Original item not found for update.", parent=self)
                return
        elif self.item_type == "tray":
            try:
                index = self.master.config_data["tray_and_multi_window_applications"].index(self.item_data)
                self.master.config_data["tray_and_multi_window_applications"][index] = updated_item
            except ValueError:
                messagebox.showerror("Error", "Original item not found for update.", parent=self)
                return

        self.master.update_list_displays()
        self.destroy()  # Close dialog


class KomorebiConfigApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Komorebi Config Editor")
        self.geometry("900x700")  # Adjusted size for two columns

        self.config_data = self.load_config()

        # Configure grid layout for the main window
        self.grid_columnconfigure(0, weight=1)  # Left panel for float rules
        self.grid_columnconfigure(1, weight=1)  # Right panel for tray apps
        self.grid_rowconfigure(0, weight=0)  # Search bar
        self.grid_rowconfigure(1, weight=1)  # Main content (float/tray frames)
        self.grid_rowconfigure(2, weight=0)  # Buttons

        # --- Search Bar ---
        self.search_frame = ctk.CTkFrame(self)
        self.search_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.search_frame.grid_columnconfigure(0, weight=1)
        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Search rules and applications...")
        self.search_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.filter_list_displays)

        # --- Float Rules Section (Left) ---
        self.float_frame = ctk.CTkFrame(self)
        self.float_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.float_frame.grid_columnconfigure(0, weight=1)
        self.float_frame.grid_rowconfigure(0, weight=0)
        self.float_frame.grid_rowconfigure(1, weight=1)

        self.float_label = ctk.CTkLabel(self.float_frame, text="Float Rules", font=ctk.CTkFont(size=16, weight="bold"))
        self.float_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.float_scroll_frame = ctk.CTkScrollableFrame(self.float_frame)
        self.float_scroll_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.float_scroll_frame.grid_columnconfigure(0, weight=1)
        self.float_list_items = []  # To store references to the labels
        self.selected_float_rule = None  # Stores the full dictionary of the selected rule

        # --- Tray and Multi-Window Applications Section (Right) ---
        self.tray_frame = ctk.CTkFrame(self)
        self.tray_frame.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")
        self.tray_frame.grid_columnconfigure(0, weight=1)
        self.tray_frame.grid_rowconfigure(0, weight=0)
        self.tray_frame.grid_rowconfigure(1, weight=1)

        self.tray_label = ctk.CTkLabel(self.tray_frame, text="Tray and Multi-Window Applications", font=ctk.CTkFont(size=16, weight="bold"))
        self.tray_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.tray_scroll_frame = ctk.CTkScrollableFrame(self.tray_frame)
        self.tray_scroll_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.tray_scroll_frame.grid_columnconfigure(0, weight=1)
        self.tray_list_items = []  # To store references to the labels
        self.selected_tray_app = None  # Stores the full dictionary of the selected app

        # --- Buttons Frame (Bottom) ---
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.button_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)  # 5 buttons

        self.add_float_button = ctk.CTkButton(self.button_frame, corner_radius=0, text="Add Float Rule", command=self.open_add_float_dialog)
        self.add_float_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.add_tray_button = ctk.CTkButton(self.button_frame, corner_radius=0, text="Add Tray App", command=self.open_add_tray_dialog)
        self.add_tray_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.edit_selected_button = ctk.CTkButton(self.button_frame, corner_radius=0, fg_color="blue", text="Edit Selected Item", command=self.open_edit_dialog)
        self.edit_selected_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        self.remove_selected_button = ctk.CTkButton(self.button_frame, fg_color="red", corner_radius=0, text="Remove Selected Item", command=self.remove_selected_item)
        self.remove_selected_button.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        self.save_button = ctk.CTkButton(self.button_frame, fg_color="green", corner_radius=0, text="Save to komorebi.json", command=self.save_config)
        self.save_button.grid(row=0, column=4, padx=5, pady=5, sticky="ew")

        self.update_list_displays() # Initial display update

    def load_config(self):
        if not os.path.exists(KOMOREBI_JSON_PATH):
            messagebox.showerror("Error", f"komorebi.json not found at {KOMOREBI_JSON_PATH}")
            return {"float_rules": [], "tray_and_multi_window_applications": []}
        try:
            with open(KOMOREBI_JSON_PATH, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Could not decode komorebi.json. Please check its format.")
            return {"float_rules": [], "tray_and_multi_window_applications": []}
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while loading: {e}")
            return {"float_rules": [], "tray_and_multi_window_applications": []}

    def save_config(self):
        try:
            with open(KOMOREBI_JSON_PATH, 'w') as f:
                json.dump(self.config_data, f, indent=4)
            messagebox.showinfo("Success", "Configuration saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving: {e}")

    def filter_list_displays(self, event=None):
        self.update_list_displays(search_query=self.search_entry.get().lower())

    def update_list_displays(self, search_query=""):
        # Clear existing items in float rules display
        for item in self.float_list_items:
            item.destroy()
        self.float_list_items.clear()
        self.selected_float_rule = None

        # Sort and populate float rules display
        float_rules = sorted(self.config_data.get("float_rules", []), key=lambda x: x.get('id', '').lower())
        filtered_float_rules = [
            rule_obj for rule_obj in float_rules
            if search_query in f"{rule_obj.get('id', '')} {rule_obj.get('kind', '')} {rule_obj.get('matching_strategy', '')}".lower()
        ]
        for i, rule_obj in enumerate(filtered_float_rules):
            display_text = f"{rule_obj.get('id', '')} ({rule_obj.get('kind', '')}) ({rule_obj.get('matching_strategy', '')})"
            label = ctk.CTkLabel(self.float_scroll_frame, text=display_text, anchor="w")
            label.grid(row=i, column=0, padx=5, pady=2, sticky="ew")
            label.rule_obj = rule_obj
            label.bind("<Button-1>", lambda event, l=label: self.select_float_rule(l))
            self.float_list_items.append(label)

        # Clear existing items in tray apps display
        for item in self.tray_list_items:
            item.destroy()
        self.tray_list_items.clear()
        self.selected_tray_app = None

        # Sort and populate tray apps display
        tray_apps = sorted(self.config_data.get("tray_and_multi_window_applications", []), key=lambda x: x.get('id', '').lower())
        filtered_tray_apps = [
            app_obj for app_obj in tray_apps
            if search_query in f"{app_obj.get('id', '')} {app_obj.get('kind', '')} {app_obj.get('matching_strategy', '')}".lower()
        ]
        for i, app_obj in enumerate(filtered_tray_apps):
            display_text = f"{app_obj.get('id', '')} ({app_obj.get('kind', '')}) ({app_obj.get('matching_strategy', '')})"
            label = ctk.CTkLabel(self.tray_scroll_frame, text=display_text, anchor="w")
            label.grid(row=i, column=0, padx=5, pady=2, sticky="ew")
            label.app_obj = app_obj
            label.bind("<Button-1>", lambda event, l=label: self.select_tray_app(l))
            self.tray_list_items.append(label)

    def select_float_rule(self, label):
        # Deselect previous
        if self.selected_float_rule:
            for item_label in self.float_list_items:
                if item_label.rule_obj == self.selected_float_rule:
                    item_label.configure(fg_color="transparent")
                    break
        # Select new
        self.selected_float_rule = label.rule_obj
        self.selected_tray_app = None # Ensure only one type is selected at a time
        label.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])

    def select_tray_app(self, label):
        # Deselect previous
        if self.selected_tray_app:
            for item_label in self.tray_list_items:
                if item_label.app_obj == self.selected_tray_app:
                    item_label.configure(fg_color="transparent")
                    break
        # Select new
        self.selected_tray_app = label.app_obj
        self.selected_float_rule = None # Ensure only one type is selected at a time
        label.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])

    def open_add_float_dialog(self):
        AddEditDialog(self, "float")

    def open_add_tray_dialog(self):
        AddEditDialog(self, "tray")

    def open_edit_dialog(self):
        if self.selected_float_rule:
            AddEditDialog(self, "float", self.selected_float_rule)
        elif self.selected_tray_app:
            AddEditDialog(self, "tray", self.selected_tray_app)
        else:
            messagebox.showwarning("Warning", "Please select an item to edit.")

    def remove_selected_item(self):
        if self.selected_float_rule:
            if self.selected_float_rule in self.config_data.get("float_rules", []):
                self.config_data["float_rules"].remove(self.selected_float_rule)
                self.update_list_displays()
            self.selected_float_rule = None  # Clear selection after removal
        elif self.selected_tray_app:
            if self.selected_tray_app in self.config_data.get("tray_and_multi_window_applications", []):
                self.config_data["tray_and_multi_window_applications"].remove(self.selected_tray_app)
                self.update_list_displays()
            self.selected_tray_app = None  # Clear selection after removal
        else:
            messagebox.showwarning("Warning", "No item selected to remove.")


if __name__ == "__main__":
    app = KomorebiConfigApp()
    app.mainloop()
