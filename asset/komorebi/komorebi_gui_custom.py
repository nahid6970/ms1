import customtkinter as ctk
from tkinter import messagebox
import json
import os
import time

# Optional imports for window info capture
try:
    import win32gui
    import win32process
    import win32api
    PYWIN32_AVAILABLE = True
except ImportError:
    PYWIN32_AVAILABLE = False

# Set the appearance mode and default color theme
ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "dark-blue", "green"

KOMOREBI_JSON_PATH = "C:/@delta/ms1/asset/komorebi/komorebi.json"

class CaptureSelectionDialog(ctk.CTkToplevel):
    """Dialog to choose which property of a captured window to use."""
    def __init__(self, master, info, font):
        super().__init__(master)
        self.master = master
        self.info = info
        self.font = font
        self.title("Select Window Info")
        self.geometry("500x420")
        self.transient(master)
        self.grab_set()

        ctk.CTkLabel(self, text="Select the information you want to use:", font=(font[0], font[1], "bold")).pack(pady=10)

        self.choice_var = ctk.StringVar(value="Exe")
        
        options = [
            ("Exe", f"Executable: {info['Exe']}"),
            ("Title", f"Window Title: {info['Title']}"),
            ("Class", f"Window Class: {info['Class']}"),
            ("Path", f"Full Path: {info['Path']}")
        ]

        for kind, display in options:
            frame = ctk.CTkFrame(self)
            frame.pack(fill="x", padx=20, pady=2)
            rb = ctk.CTkRadioButton(frame, text=display, variable=self.choice_var, value=kind, font=self.font)
            rb.pack(side="left", padx=10, pady=5)

        ctk.CTkLabel(self, text="Add to rule lists:", font=(font[0], font[1], "bold")).pack(pady=10)
        
        self.is_float_var = ctk.BooleanVar(value=True)
        self.is_tray_var = ctk.BooleanVar(value=False)
        
        type_frame = ctk.CTkFrame(self)
        type_frame.pack(pady=5)
        ctk.CTkCheckBox(type_frame, text="Float Rule", variable=self.is_float_var, font=self.font).pack(side="left", padx=10)
        ctk.CTkCheckBox(type_frame, text="Tray App", variable=self.is_tray_var, font=self.font).pack(side="left", padx=10)
        
        ctk.CTkButton(self, text="Confirm and Open Editor", command=self.proceed, font=self.font).pack(pady=20)
        
    def proceed(self):
        kind = self.choice_var.get()
        val = self.info[kind]
        is_float = self.is_float_var.get()
        is_tray = self.is_tray_var.get()
        self.destroy()
        AddEditDialog(self.master, initial_kind=kind, initial_id=val, is_float=is_float, is_tray=is_tray, font=self.font)

class AddEditDialog(ctk.CTkToplevel):
    def __init__(self, master, item_data=None, *, font=None, initial_kind=None, initial_id=None, is_float=False, is_tray=False):
        super().__init__(master)
        self.master = master
        self.item_data = item_data  # unified dict if editing
        self.font = font if font else ("sans-serif", 12, "normal")
        self.transient(master)
        self.grab_set()
        self.geometry("400x260")

        self.title("Edit Item" if item_data else "Add Item")

        kind_options = ["Exe", "Class", "Title", "Path"]
        matching_strategy_options = [
            "Legacy", "Equals", "StartsWith", "EndsWith", "Contains", "Regex",
            "DoesNotEndWith", "DoesNotStartWith", "DoesNotEqual", "DoesNotContain"
        ]

        self.kind_combobox = ctk.CTkComboBox(self, values=kind_options, font=self.font)
        self.kind_combobox.pack(padx=20, pady=5, fill="x")
        self.id_entry = ctk.CTkEntry(self, placeholder_text="ID", font=self.font)
        self.id_entry.pack(padx=20, pady=5, fill="x")
        self.matching_strategy_combobox = ctk.CTkComboBox(self, values=matching_strategy_options, font=self.font)
        self.matching_strategy_combobox.pack(padx=20, pady=5, fill="x")

        self.is_float_var = ctk.BooleanVar(value=item_data["is_float"] if item_data else is_float)
        self.is_tray_var = ctk.BooleanVar(value=item_data["is_tray"] if item_data else is_tray)

        self.float_cb = ctk.CTkCheckBox(self, text="Float Rule", variable=self.is_float_var, font=self.font)
        self.float_cb.pack(padx=20, pady=5, anchor="w")
        self.tray_cb = ctk.CTkCheckBox(self, text="Tray / Multi-Window", variable=self.is_tray_var, font=self.font)
        self.tray_cb.pack(padx=20, pady=5, anchor="w")

        if item_data:
            self.kind_combobox.set(item_data["kind"])
            self.id_entry.insert(0, item_data["id"])
            self.matching_strategy_combobox.set(item_data["matching_strategy"])
            btn_text = "Save Changes"
            cmd = self.save_changes
        else:
            self.kind_combobox.set(initial_kind if initial_kind else kind_options[0])
            self.id_entry.insert(0, initial_id if initial_id else "")
            self.matching_strategy_combobox.set(matching_strategy_options[0])
            btn_text = "Add Item"
            cmd = self.add_item

        ctk.CTkButton(self, text=btn_text, command=cmd, font=self.font).pack(padx=20, pady=10)

    def get_data(self):
        return {
            "kind": self.kind_combobox.get(),
            "id": self.id_entry.get().strip(),
            "matching_strategy": self.matching_strategy_combobox.get()
        }

    def add_item(self):
        data = self.get_data()
        if not data["id"]:
            messagebox.showwarning("Warning", "ID cannot be empty.")
            return
        
        if not self.is_float_var.get() and not self.is_tray_var.get():
            messagebox.showwarning("Warning", "Select at least one type (Float or Tray).")
            return

        if self.is_float_var.get():
            self.master.config_data.setdefault("float_rules", []).append(data)
        if self.is_tray_var.get():
            self.master.config_data.setdefault("tray_and_multi_window_applications", []).append(data)
        
        self.master.update_list_displays()
        self.destroy()

    def save_changes(self):
        new_data = self.get_data()
        if not new_data["id"]:
            messagebox.showwarning("Warning", "ID cannot be empty.")
            return

        if not self.is_float_var.get() and not self.is_tray_var.get():
            messagebox.showwarning("Warning", "Select at least one type (Float or Tray).")
            return

        # Remove old data from both lists
        old_base = {"kind": self.item_data["kind"], "id": self.item_data["id"], "matching_strategy": self.item_data["matching_strategy"]}
        
        if old_base in self.master.config_data.get("float_rules", []):
            self.master.config_data["float_rules"].remove(old_base)
        if old_base in self.master.config_data.get("tray_and_multi_window_applications", []):
            self.master.config_data["tray_and_multi_window_applications"].remove(old_base)

        # Add new data to selected lists
        if self.is_float_var.get():
            self.master.config_data.setdefault("float_rules", []).append(new_data)
        if self.is_tray_var.get():
            self.master.config_data.setdefault("tray_and_multi_window_applications", []).append(new_data)

        self.master.update_list_displays()
        self.destroy()

    def add_item(self):
        kind = self.kind_combobox.get()
        item_id = self.id_entry.get().strip()
        matching_strategy = self.matching_strategy_combobox.get()

        if not item_id:
            messagebox.showwarning("Warning", "The ID field cannot be empty.", parent=self)
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
        kind = self.kind_combobox.get()
        item_id = self.id_entry.get().strip()
        matching_strategy = self.matching_strategy_combobox.get()

        if not item_id:
            messagebox.showwarning("Warning", "The ID field cannot be empty.", parent=self)
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
        self.geometry("800x700")

        self.app_font = ("jetbrainsmono nfp", 12, "normal")
        self.bold_font = ("jetbrainsmono nfp", 16, "bold")

        self.config_data = self.load_config()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Search
        self.grid_rowconfigure(1, weight=1)  # List
        self.grid_rowconfigure(2, weight=0)  # Buttons

        # --- Search Bar ---
        self.search_frame = ctk.CTkFrame(self)
        self.search_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.search_frame.grid_columnconfigure(0, weight=1)
        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Search rules and applications...", font=self.app_font)
        self.search_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.filter_list_displays)

        # --- Main List Section ---
        self.list_frame = ctk.CTkFrame(self)
        self.list_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.list_frame.grid_columnconfigure(0, weight=1)
        self.list_frame.grid_rowconfigure(0, weight=1)

        self.scroll_frame = ctk.CTkScrollableFrame(self.list_frame)
        self.scroll_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        
        self.list_items = []
        self.selected_item = None

        # --- Buttons Frame ---
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.button_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.add_button = ctk.CTkButton(self.button_frame, text="Add New Rule", corner_radius=0, command=self.open_add_dialog, font=self.app_font)
        self.add_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.get_item_button = ctk.CTkButton(self.button_frame, text="Get Item Info", corner_radius=0, command=self.get_window_info, font=self.app_font)
        self.get_item_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.remove_button = ctk.CTkButton(self.button_frame, text="Remove Selected", fg_color="red", corner_radius=0, command=self.remove_selected_item, font=self.app_font)
        self.remove_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        self.save_button = ctk.CTkButton(self.button_frame, text="Save to JSON", fg_color="green", corner_radius=0, command=self.save_config, font=self.app_font)
        self.save_button.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        self.update_list_displays()

    def get_window_info(self):
        if not PYWIN32_AVAILABLE:
            messagebox.showerror("Error", "pywin32 library is not installed.")
            return
        self.get_item_button.configure(text="Click target window...", fg_color="orange")
        self.after(100, self.wait_for_mouse_release)

    def wait_for_mouse_release(self):
        if win32api.GetAsyncKeyState(0x01) == 0:
            self.poll_for_next_click()
        else:
            self.after(50, self.wait_for_mouse_release)

    def poll_for_next_click(self):
        if win32api.GetAsyncKeyState(0x01) < 0:
            self.after(150, self.perform_capture_at_cursor)
        else:
            self.after(50, self.poll_for_next_click)

    def perform_capture_at_cursor(self):
        self.get_item_button.configure(text="Get Item Info", fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])
        pos = win32api.GetCursorPos()
        hwnd = win32gui.WindowFromPoint(pos)
        if not hwnd: return
        hwnd = win32gui.GetAncestor(hwnd, 2)
        title = win32gui.GetWindowText(hwnd)
        cls = win32gui.GetClassName(hwnd)
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            handle = win32api.OpenProcess(0x0400 | 0x0010, False, pid)
            path = win32process.GetModuleFileNameEx(handle, 0)
            exe = os.path.basename(path)
            win32api.CloseHandle(handle)
        except: path, exe = "Unknown", "Unknown"
        CaptureSelectionDialog(self, {"Exe": exe, "Title": title, "Class": cls, "Path": path}, self.app_font)

    def load_config(self):
        if not os.path.exists(KOMOREBI_JSON_PATH):
            return {"float_rules": [], "tray_and_multi_window_applications": []}
        try:
            with open(KOMOREBI_JSON_PATH, 'r') as f:
                return json.load(f)
        except: return {"float_rules": [], "tray_and_multi_window_applications": []}

    def save_config(self):
        try:
            with open(KOMOREBI_JSON_PATH, 'w') as f:
                json.dump(self.config_data, f, indent=4)
            messagebox.showinfo("Success", "Configuration saved!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def filter_list_displays(self, event=None):
        self.update_list_displays(search_query=self.search_entry.get().lower())

    def update_list_displays(self, search_query=""):
        for item in self.list_items:
            item.destroy()
        self.list_items.clear()
        self.selected_item = None

        unified = {}
        for rule in self.config_data.get("float_rules", []):
            key = (rule["kind"], rule["id"], rule["matching_strategy"])
            unified[key] = {**rule, "is_float": True, "is_tray": False}
        
        for app in self.config_data.get("tray_and_multi_window_applications", []):
            key = (app["kind"], app["id"], app["matching_strategy"])
            if key in unified:
                unified[key]["is_tray"] = True
            else:
                unified[key] = {**app, "is_float": False, "is_tray": True}

        items_to_show = sorted([v for v in unified.values() if search_query in f"{v['id']} {v['kind']} {v['matching_strategy']}".lower()], key=lambda x: x["id"].lower())

        for i, val in enumerate(items_to_show):
            frame = ctk.CTkFrame(self.scroll_frame)
            frame.grid(row=i, column=0, padx=5, pady=2, sticky="ew")
            frame.grid_columnconfigure(0, weight=1)
            
            label = ctk.CTkLabel(frame, text=f"{val['id']} ({val['kind']}) ({val['matching_strategy']})", anchor="w", font=self.app_font)
            label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
            
            tag_frame = ctk.CTkFrame(frame, fg_color="transparent")
            tag_frame.grid(row=0, column=1, padx=5)
            
            if val["is_float"]:
                ctk.CTkLabel(tag_frame, text="FLOAT", font=(self.app_font[0], 9, "bold"), fg_color="#1f538d", text_color="white", corner_radius=4).pack(side="left", padx=2)
            if val["is_tray"]:
                ctk.CTkLabel(tag_frame, text="TRAY", font=(self.app_font[0], 9, "bold"), fg_color="#22733d", text_color="white", corner_radius=4).pack(side="left", padx=2)

            frame.val = val
            for widget in [frame, label, tag_frame]:
                widget.bind("<Button-1>", lambda e, f=frame: self.select_item(f))
                widget.bind("<Double-Button-1>", lambda e, v=val: self.open_edit_dialog(v))
            self.list_items.append(frame)

    def select_item(self, frame):
        if self.selected_item:
            self.selected_item.configure(fg_color=ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
        self.selected_item = frame
        frame.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])

    def open_add_dialog(self):
        AddEditDialog(self, font=self.app_font)

    def open_edit_dialog(self, val):
        AddEditDialog(self, item_data=val, font=self.app_font)

    def remove_selected_item(self):
        if not self.selected_item:
            messagebox.showwarning("Warning", "Select an item to remove.")
            return
        
        val = self.selected_item.val
        base = {"kind": val["kind"], "id": val["id"], "matching_strategy": val["matching_strategy"]}
        
        if base in self.config_data.get("float_rules", []):
            self.config_data["float_rules"].remove(base)
        if base in self.config_data.get("tray_and_multi_window_applications", []):
            self.config_data["tray_and_multi_window_applications"].remove(base)
            
        self.update_list_displays()

if __name__ == "__main__":
    app = KomorebiConfigApp()
    app.mainloop()
