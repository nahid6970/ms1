
import tkinter as tk
from tkinter import messagebox
import json
import os

KOMOREBI_JSON_PATH = "C:/ms1/asset/komorebi/komorebi.json"

class KomorebiConfigApp:
    def __init__(self, master):
        self.master = master
        master.title("Komorebi Config Editor")

        self.config_data = self.load_config()

        # --- Float Rules Section ---
        self.float_frame = tk.LabelFrame(master, text="Float Rules")
        self.float_frame.pack(padx=10, pady=5, fill="both", expand=True)

        self.float_listbox = tk.Listbox(self.float_frame, height=10)
        self.float_listbox.pack(side="left", fill="both", expand=True)
        self.float_scrollbar = tk.Scrollbar(self.float_frame, orient="vertical", command=self.float_listbox.yview)
        self.float_scrollbar.pack(side="right", fill="y")
        self.float_listbox.config(yscrollcommand=self.float_scrollbar.set)

        self.float_entry = tk.Entry(self.float_frame)
        self.float_entry.pack(fill="x", padx=5, pady=2)

        self.float_add_button = tk.Button(self.float_frame, text="Add Float Rule", command=self.add_float_rule)
        self.float_add_button.pack(fill="x", padx=5, pady=2)

        self.float_remove_button = tk.Button(self.float_frame, text="Remove Selected Float Rule", command=self.remove_float_rule)
        self.float_remove_button.pack(fill="x", padx=5, pady=2)

        # --- Tray and Multi-Window Applications Section ---
        self.tray_frame = tk.LabelFrame(master, text="Tray and Multi-Window Applications")
        self.tray_frame.pack(padx=10, pady=5, fill="both", expand=True)

        self.tray_listbox = tk.Listbox(self.tray_frame, height=10)
        self.tray_listbox.pack(side="left", fill="both", expand=True)
        self.tray_scrollbar = tk.Scrollbar(self.tray_frame, orient="vertical", command=self.tray_listbox.yview)
        self.tray_scrollbar.pack(side="right", fill="y")
        self.tray_listbox.config(yscrollcommand=self.tray_scrollbar.set)

        self.tray_entry = tk.Entry(self.tray_frame)
        self.tray_entry.pack(fill="x", padx=5, pady=2)

        self.tray_add_button = tk.Button(self.tray_frame, text="Add Application", command=self.add_tray_app)
        self.tray_add_button.pack(fill="x", padx=5, pady=2)

        self.tray_remove_button = tk.Button(self.tray_frame, text="Remove Selected Application", command=self.remove_tray_app)
        self.tray_remove_button.pack(fill="x", padx=5, pady=2)

        # --- Save Button ---
        self.save_button = tk.Button(master, text="Save Changes to komorebi.json", command=self.save_config)
        self.save_button.pack(padx=10, pady=10)

        self.update_listboxes()

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

    def update_listboxes(self):
        self.float_listbox.delete(0, tk.END)
        for rule in self.config_data.get("float_rules", []):
            self.float_listbox.insert(tk.END, rule)

        self.tray_listbox.delete(0, tk.END)
        for app in self.config_data.get("tray_and_multi_window_applications", []):
            self.tray_listbox.insert(tk.END, app)

    def add_float_rule(self):
        rule = self.float_entry.get().strip()
        if rule and rule not in self.config_data.get("float_rules", []):
            self.config_data.setdefault("float_rules", []).append(rule)
            self.float_entry.delete(0, tk.END)
            self.update_listboxes()
        elif rule:
            messagebox.showwarning("Warning", "Rule already exists or is empty.")

    def remove_float_rule(self):
        selected_indices = self.float_listbox.curselection()
        if selected_indices:
            for index in selected_indices[::-1]: # Delete in reverse order to avoid index issues
                rule = self.float_listbox.get(index)
                if rule in self.config_data.get("float_rules", []):
                    self.config_data["float_rules"].remove(rule)
            self.update_listboxes()
        else:
            messagebox.showwarning("Warning", "No float rule selected to remove.")

    def add_tray_app(self):
        app = self.tray_entry.get().strip()
        if app and app not in self.config_data.get("tray_and_multi_window_applications", []):
            self.config_data.setdefault("tray_and_multi_window_applications", []).append(app)
            self.tray_entry.delete(0, tk.END)
            self.update_listboxes()
        elif app:
            messagebox.showwarning("Warning", "Application already exists or is empty.")

    def remove_tray_app(self):
        selected_indices = self.tray_listbox.curselection()
        if selected_indices:
            for index in selected_indices[::-1]: # Delete in reverse order
                app = self.tray_listbox.get(index)
                if app in self.config_data.get("tray_and_multi_window_applications", []):
                    self.config_data["tray_and_multi_window_applications"].remove(app)
            self.update_listboxes()
        else:
            messagebox.showwarning("Warning", "No application selected to remove.")

if __name__ == "__main__":
    root = tk.Tk()
    app = KomorebiConfigApp(root)
    root.mainloop()
