import customtkinter as ctk
from tkinter import messagebox
import json
import os

# Set the appearance mode and default color theme
ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "dark-blue", "green"

KOMOREBI_JSON_PATH = "C:/ms1/asset/komorebi/komorebi.json"

class KomorebiConfigApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Komorebi Config Editor")
        self.geometry("800x800") # Increased size to accommodate new fields

        self.config_data = self.load_config()

        # Configure grid layout (2x1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        # --- Float Rules Section ---
        self.float_frame = ctk.CTkFrame(self)
        self.float_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        self.float_frame.grid_columnconfigure(0, weight=1)
        self.float_frame.grid_rowconfigure(0, weight=0)
        self.float_frame.grid_rowconfigure(1, weight=1)
        self.float_frame.grid_rowconfigure(2, weight=0)
        self.float_frame.grid_rowconfigure(3, weight=0)
        self.float_frame.grid_rowconfigure(4, weight=0)

        self.float_label = ctk.CTkLabel(self.float_frame, text="Float Rules", font=ctk.CTkFont(size=16, weight="bold"))
        self.float_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.float_scroll_frame = ctk.CTkScrollableFrame(self.float_frame)
        self.float_scroll_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.float_scroll_frame.grid_columnconfigure(0, weight=1)
        self.float_list_items = [] # To store references to the labels
        self.selected_float_rule = None # Stores the full dictionary of the selected rule

        # Input fields for Float Rules
        self.float_kind_entry = ctk.CTkEntry(self.float_frame, placeholder_text="Kind (e.g., Exe, Class, Title)")
        self.float_kind_entry.grid(row=2, column=0, padx=10, pady=2, sticky="ew")

        self.float_id_entry = ctk.CTkEntry(self.float_frame, placeholder_text="ID (e.g., notepad.exe)")
        self.float_id_entry.grid(row=3, column=0, padx=10, pady=2, sticky="ew")

        self.float_matching_strategy_entry = ctk.CTkEntry(self.float_frame, placeholder_text="Matching Strategy (e.g., Equals, Contains)")
        self.float_matching_strategy_entry.grid(row=4, column=0, padx=10, pady=2, sticky="ew")

        self.float_button_frame = ctk.CTkFrame(self.float_frame, fg_color="transparent")
        self.float_button_frame.grid(row=5, column=0, padx=10, pady=5, sticky="ew")
        self.float_button_frame.grid_columnconfigure(0, weight=1)
        self.float_button_frame.grid_columnconfigure(1, weight=1)

        self.float_add_button = ctk.CTkButton(self.float_button_frame, text="Add Float Rule", command=self.add_float_rule)
        self.float_add_button.grid(row=0, column=0, padx=5, pady=2, sticky="ew")

        self.float_remove_button = ctk.CTkButton(self.float_button_frame, text="Remove Selected", command=self.remove_float_rule)
        self.float_remove_button.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        # --- Tray and Multi-Window Applications Section ---
        self.tray_frame = ctk.CTkFrame(self)
        self.tray_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.tray_frame.grid_columnconfigure(0, weight=1)
        self.tray_frame.grid_rowconfigure(0, weight=0)
        self.tray_frame.grid_rowconfigure(1, weight=1)
        self.tray_frame.grid_rowconfigure(2, weight=0)
        self.tray_frame.grid_rowconfigure(3, weight=0)
        self.tray_frame.grid_rowconfigure(4, weight=0)

        self.tray_label = ctk.CTkLabel(self.tray_frame, text="Tray and Multi-Window Applications", font=ctk.CTkFont(size=16, weight="bold"))
        self.tray_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.tray_scroll_frame = ctk.CTkScrollableFrame(self.tray_frame)
        self.tray_scroll_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.tray_scroll_frame.grid_columnconfigure(0, weight=1)
        self.tray_list_items = [] # To store references to the labels
        self.selected_tray_app = None # Stores the full dictionary of the selected app

        # Input fields for Tray Apps
        self.tray_kind_entry = ctk.CTkEntry(self.tray_frame, placeholder_text="Kind (e.g., Exe, Class, Title)")
        self.tray_kind_entry.grid(row=2, column=0, padx=10, pady=2, sticky="ew")

        self.tray_id_entry = ctk.CTkEntry(self.tray_frame, placeholder_text="ID (e.g., discord.exe)")
        self.tray_id_entry.grid(row=3, column=0, padx=10, pady=2, sticky="ew")

        self.tray_matching_strategy_entry = ctk.CTkEntry(self.tray_frame, placeholder_text="Matching Strategy (e.g., Equals, Contains)")
        self.tray_matching_strategy_entry.grid(row=4, column=0, padx=10, pady=2, sticky="ew")

        self.tray_button_frame = ctk.CTkFrame(self.tray_frame, fg_color="transparent")
        self.tray_button_frame.grid(row=5, column=0, padx=10, pady=5, sticky="ew")
        self.tray_button_frame.grid_columnconfigure(0, weight=1)
        self.tray_button_frame.grid_columnconfigure(1, weight=1)

        self.tray_add_button = ctk.CTkButton(self.tray_button_frame, text="Add Application", command=self.add_tray_app)
        self.tray_add_button.grid(row=0, column=0, padx=5, pady=2, sticky="ew")

        self.tray_remove_button = ctk.CTkButton(self.tray_button_frame, text="Remove Selected", command=self.remove_tray_app)
        self.tray_remove_button.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        # --- Save Button ---
        self.save_button = ctk.CTkButton(self, text="Save Changes to komorebi.json", command=self.save_config)
        self.save_button.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.update_list_displays()

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

    def update_list_displays(self):
        # Clear existing items in float rules display
        for item in self.float_list_items:
            item.destroy()
        self.float_list_items.clear()
        self.selected_float_rule = None

        # Populate float rules display
        for i, rule_obj in enumerate(self.config_data.get("float_rules", [])):
            # Changed display_text format
            display_text = f"{rule_obj.get('id', '')} ({rule_obj.get('kind', '')}) ({rule_obj.get('matching_strategy', '')})"
            label = ctk.CTkLabel(self.float_scroll_frame, text=display_text, anchor="w")
            label.grid(row=i, column=0, padx=5, pady=2, sticky="ew")
            # Store the full rule_obj with the label for easy access during selection
            label.rule_obj = rule_obj
            label.bind("<Button-1>", lambda event, l=label: self.select_float_rule(l))
            self.float_list_items.append(label)

        # Clear existing items in tray apps display
        for item in self.tray_list_items:
            item.destroy()
        self.tray_list_items.clear()
        self.selected_tray_app = None

        # Populate tray apps display
        for i, app_obj in enumerate(self.config_data.get("tray_and_multi_window_applications", [])):
            # Changed display_text format
            display_text = f"{app_obj.get('id', '')} ({app_obj.get('kind', '')}) ({app_obj.get('matching_strategy', '')})"
            label = ctk.CTkLabel(self.tray_scroll_frame, text=display_text, anchor="w")
            label.grid(row=i, column=0, padx=5, pady=2, sticky="ew")
            # Store the full app_obj with the label
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
        label.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])

    def add_float_rule(self):
        kind = self.float_kind_entry.get().strip()
        rule_id = self.float_id_entry.get().strip()
        matching_strategy = self.float_matching_strategy_entry.get().strip()

        if not kind or not rule_id or not matching_strategy:
            messagebox.showwarning("Warning", "All fields (Kind, ID, Matching Strategy) are required for a float rule.")
            return

        new_rule = {"kind": kind, "id": rule_id, "matching_strategy": matching_strategy}

        if new_rule not in self.config_data.get("float_rules", []):
            self.config_data.setdefault("float_rules", []).append(new_rule)
            self.float_kind_entry.delete(0, ctk.END)
            self.float_id_entry.delete(0, ctk.END)
            self.float_matching_strategy_entry.delete(0, ctk.END)
            self.update_list_displays()
        else:
            messagebox.showwarning("Warning", "This float rule already exists.")

    def remove_float_rule(self):
        if self.selected_float_rule:
            if self.selected_float_rule in self.config_data.get("float_rules", []):
                self.config_data["float_rules"].remove(self.selected_float_rule)
                self.update_list_displays()
            self.selected_float_rule = None # Clear selection after removal
        else:
            messagebox.showwarning("Warning", "No float rule selected to remove.")

    def add_tray_app(self):
        kind = self.tray_kind_entry.get().strip()
        app_id = self.tray_id_entry.get().strip()
        matching_strategy = self.tray_matching_strategy_entry.get().strip()

        if not kind or not app_id or not matching_strategy:
            messagebox.showwarning("Warning", "All fields (Kind, ID, Matching Strategy) are required for a tray application.")
            return

        new_app = {"kind": kind, "id": app_id, "matching_strategy": matching_strategy}

        if new_app not in self.config_data.get("tray_and_multi_window_applications", []):
            self.config_data.setdefault("tray_and_multi_window_applications", []).append(new_app)
            self.tray_kind_entry.delete(0, ctk.END)
            self.tray_id_entry.delete(0, ctk.END)
            self.tray_matching_strategy_entry.delete(0, ctk.END)
            self.update_list_displays()
        else:
            messagebox.showwarning("Warning", "This application already exists.")

    def remove_tray_app(self):
        if self.selected_tray_app:
            if self.selected_tray_app in self.config_data.get("tray_and_multi_window_applications", []):
                self.config_data["tray_and_multi_window_applications"].remove(self.selected_tray_app)
                self.update_list_displays()
            self.selected_tray_app = None # Clear selection after removal
        else:
            messagebox.showwarning("Warning", "No application selected to remove.")

if __name__ == "__main__":
    app = KomorebiConfigApp()
    app.mainloop()
