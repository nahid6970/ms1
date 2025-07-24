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
        self.geometry("700x700")

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

        self.float_label = ctk.CTkLabel(self.float_frame, text="Float Rules", font=ctk.CTkFont(size=16, weight="bold"))
        self.float_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.float_scroll_frame = ctk.CTkScrollableFrame(self.float_frame)
        self.float_scroll_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.float_scroll_frame.grid_columnconfigure(0, weight=1)
        self.float_list_items = [] # To store references to the labels
        self.selected_float_rule = None

        self.float_entry = ctk.CTkEntry(self.float_frame, placeholder_text="Enter new float rule")
        self.float_entry.grid(row=2, column=0, padx=10, pady=2, sticky="ew")

        self.float_button_frame = ctk.CTkFrame(self.float_frame, fg_color="transparent")
        self.float_button_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
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

        self.tray_label = ctk.CTkLabel(self.tray_frame, text="Tray and Multi-Window Applications", font=ctk.CTkFont(size=16, weight="bold"))
        self.tray_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.tray_scroll_frame = ctk.CTkScrollableFrame(self.tray_frame)
        self.tray_scroll_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.tray_scroll_frame.grid_columnconfigure(0, weight=1)
        self.tray_list_items = [] # To store references to the labels
        self.selected_tray_app = None

        self.tray_entry = ctk.CTkEntry(self.tray_frame, placeholder_text="Enter new application")
        self.tray_entry.grid(row=2, column=0, padx=10, pady=2, sticky="ew")

        self.tray_button_frame = ctk.CTkFrame(self.tray_frame, fg_color="transparent")
        self.tray_button_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
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
        for i, rule in enumerate(self.config_data.get("float_rules", [])):
            label = ctk.CTkLabel(self.float_scroll_frame, text=rule, anchor="w")
            label.grid(row=i, column=0, padx=5, pady=2, sticky="ew")
            label.bind("<Button-1>", lambda event, r=rule, l=label: self.select_float_rule(r, l))
            self.float_list_items.append(label)

        # Clear existing items in tray apps display
        for item in self.tray_list_items:
            item.destroy()
        self.tray_list_items.clear()
        self.selected_tray_app = None

        # Populate tray apps display
        for i, app in enumerate(self.config_data.get("tray_and_multi_window_applications", [])):
            label = ctk.CTkLabel(self.tray_scroll_frame, text=app, anchor="w")
            label.grid(row=i, column=0, padx=5, pady=2, sticky="ew")
            label.bind("<Button-1>", lambda event, a=app, l=label: self.select_tray_app(a, l))
            self.tray_list_items.append(label)

    def select_float_rule(self, rule, label):
        # Deselect previous
        if self.selected_float_rule:
            for item_label in self.float_list_items:
                if item_label.cget("text") == self.selected_float_rule:
                    item_label.configure(fg_color="transparent")
                    break
        # Select new
        self.selected_float_rule = rule
        label.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])

    def select_tray_app(self, app, label):
        # Deselect previous
        if self.selected_tray_app:
            for item_label in self.tray_list_items:
                if item_label.cget("text") == self.selected_tray_app:
                    item_label.configure(fg_color="transparent")
                    break
        # Select new
        self.selected_tray_app = app
        label.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])

    def add_float_rule(self):
        rule = self.float_entry.get().strip()
        if rule and rule not in self.config_data.get("float_rules", []):
            self.config_data.setdefault("float_rules", []).append(rule)
            self.float_entry.delete(0, ctk.END)
            self.update_list_displays()
        elif rule:
            messagebox.showwarning("Warning", "Rule already exists.")
        else:
            messagebox.showwarning("Warning", "Rule cannot be empty.")

    def remove_float_rule(self):
        if self.selected_float_rule:
            if self.selected_float_rule in self.config_data.get("float_rules", []):
                self.config_data["float_rules"].remove(self.selected_float_rule)
                self.update_list_displays()
            self.selected_float_rule = None # Clear selection after removal
        else:
            messagebox.showwarning("Warning", "No float rule selected to remove.")

    def add_tray_app(self):
        app = self.tray_entry.get().strip()
        if app and app not in self.config_data.get("tray_and_multi_window_applications", []):
            self.config_data.setdefault("tray_and_multi_window_applications", []).append(app)
            self.tray_entry.delete(0, ctk.END)
            self.update_list_displays()
        elif app:
            messagebox.showwarning("Warning", "Application already exists.")
        else:
            messagebox.showwarning("Warning", "Application cannot be empty.")

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
