import tkinter as tk
from tkinter import messagebox, ttk
import os
import winreg
import json

class ItemEditorWindow(tk.Toplevel):
    def __init__(self, parent, item=None, item_index=None):
        super().__init__(parent)
        self.parent = parent
        self.item = item
        self.item_index = item_index
        self.title(f"{'Edit' if item else 'Add'} Startup Item")
        self.configure(bg="#2e2f3e")
        self.create_widgets()
        if self.item:
            self.populate_fields()

    def create_widgets(self):
        labels = ["Name", "Path", "Arguments", "Type", "Execution Method"]
        self.entries = {}

        for i, label_text in enumerate(labels):
            label = tk.Label(self, text=label_text, bg="#2e2f3e", fg="white")
            label.grid(row=i, column=0, padx=10, pady=5, sticky="w")

            if label_text == "Type":
                self.entries[label_text] = ttk.Combobox(self, values=["Command", "App"])
                self.entries[label_text].grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            elif label_text == "Execution Method":
                self.entries[label_text] = ttk.Combobox(self, values=["direct", "pythonw", "powershell"])
                self.entries[label_text].grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            else:
                entry = tk.Entry(self, bg="#3a3c49", fg="white", insertbackground="white")
                entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
                self.entries[label_text] = entry

        save_button = tk.Button(self, text="Save", command=self.save_item, bg="#4a4b5a", fg="white")
        save_button.grid(row=len(labels), column=0, columnspan=2, pady=10)

    def populate_fields(self):
        self.entries["Name"].insert(0, self.item.get("name", ""))
        self.entries["Path"].insert(0, self.item.get("path", ""))
        self.entries["Arguments"].insert(0, self.item.get("args", ""))
        self.entries["Type"].set(self.item.get("type", ""))
        self.entries["Execution Method"].set(self.item.get("execution_method", ""))

    def save_item(self):
        new_item_data = {
            "type": self.entries["Type"].get(),
            "name": self.entries["Name"].get(),
            "path": self.entries["Path"].get(),
            "args": self.entries["Arguments"].get(),
            "execution_method": self.entries["Execution Method"].get()
        }

        # Validate required fields, allowing empty args
        required_fields = ["type", "name", "path", "execution_method"]
        if not all(new_item_data[field] for field in required_fields):
            messagebox.showerror("Error", "All fields except Arguments are required.")
            return

        self.parent.save_item_to_json(new_item_data, self.item_index)
        self.destroy()

class StartupManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self.title("Startup Manager")
        self.configure(bg="#2e2f3e")
        self.json_path = "C:\\ms1\\Testing\\startup_items.json"
        self.items = self.filter_existing_items(self.load_items())
        self.create_widgets()
        self.center_window()
        self.attributes('-topmost', True)
        self.deiconify()

    def load_items(self):
        try:
            with open(self.json_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def filter_existing_items(self, items):
        filtered_items = []
        for item in items:
            if os.path.exists(item["path"]):
                filtered_items.append(item)
        return filtered_items

    def create_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

        commands = [(i, item) for i, item in enumerate(self.items) if item["type"] == "Command"]
        apps = [(i, item) for i, item in enumerate(self.items) if item["type"] == "App"]

        self.create_section("Commands", commands, column=0)
        separator = tk.Frame(self, width=2, bg="#4a4b5a")
        separator.grid(row=1, column=1, rowspan=max(len(commands), len(apps)) + 2, sticky="ns")
        self.create_section("Apps", apps, column=2)

        add_button = tk.Button(self, text="Add Item", command=self.open_add_item_window, bg="#4a4b5a", fg="white")
        add_button.grid(row=max(len(commands), len(apps)) + 2, column=0, columnspan=3, pady=10)

    def create_section(self, section_name, items_with_indices, column):
        separator = tk.Label(self, text=section_name, font=("Helvetica", 10, "bold"), bg="#3a3c49", fg="#ffffff")
        separator.grid(row=0, column=column, pady=5, sticky="ew", columnspan=1)

        for i, (item_index, item) in enumerate(items_with_indices):
            self.create_item_widget(item, item_index, i + 1, column)

    def create_item_widget(self, item, item_index, row, col):
        frame = tk.Frame(self, bg="#2e2f3e")
        frame.grid(row=row, column=col, padx=5, pady=5, sticky="w")

        checked = self.is_checked(item)
        icon_text = "\uf205" if checked else "\uf204"
        icon_color = "#9ef959" if checked else "gray"

        icon_label = tk.Label(frame, text=icon_text, font=("Jetbrainsmono nfp", 12, "bold"), fg=icon_color, bg="#2e2f3e")
        icon_label.bind("<Button-1>", lambda e, i=item, f=frame: self.toggle_startup(i, f))
        icon_label.pack(side=tk.LEFT, padx=0)

        name_label = tk.Label(frame, text=item["name"], font=("Jetbrainsmono nfp", 12, "bold"), bg="#2e2f3e")
        name_label.bind("<Button-1>", lambda e, i=item: self.launch_command(i))
        name_label.pack(side=tk.LEFT)

        edit_button = tk.Button(frame, text="\u270E", font=("Jetbrainsmono nfp", 12, "bold"), bg="#2e2f3e", fg="white", command=lambda i=item, idx=item_index: self.open_edit_item_window(i, idx))
        edit_button.pack(side=tk.LEFT, padx=5)

        delete_button = tk.Button(frame, text="\u274C", font=("Jetbrainsmono nfp", 12, "bold"), bg="#2e2f3e", fg="red", command=lambda idx=item_index: self.delete_item(idx))
        delete_button.pack(side=tk.LEFT, padx=5)

        self.update_label_color(name_label, checked)

    def get_full_command(self, item):
        path = item["path"]
        args = item.get("args", "")
        method = item.get("execution_method", "direct")

        if method == "pythonw":
            return f'"C:\\Users\\nahid\\scoop\\apps\\python312\\current\\pythonw.exe" "{path}" {args}'
        elif method == "powershell":
            return f'powershell.exe -File "{path}" {args}'
        else: # direct
            return f'"{path}" {args}'

    def launch_command(self, item):
        full_command = self.get_full_command(item)
        try:
            os.system(f'start "" {full_command}')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch {item['name']}: {e}")

    def is_checked(self, item):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_READ) as reg_key:
                winreg.QueryValueEx(reg_key, item["name"])
                return True
        except FileNotFoundError:
            return False
        except WindowsError:
            return False

    def toggle_startup(self, item, frame):
        reg_path = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        name_label = frame.winfo_children()[1]
        icon_label = frame.winfo_children()[0]
        try:
            if self.is_checked(item):
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_ALL_ACCESS) as reg_key:
                    winreg.DeleteValue(reg_key, item["name"])
                self.update_label_color(name_label, False)
                icon_label.config(text="\uf204", fg="gray")
            else:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_ALL_ACCESS) as reg_key:
                    full_command = self.get_full_command(item)
                    winreg.SetValueEx(reg_key, item["name"], 0, winreg.REG_SZ, full_command)
                self.update_label_color(name_label, True)
                icon_label.config(text="\uf205", fg="#9ef959")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to modify {item['name']} in startup: {e}")

    def update_label_color(self, label, checked):
        label.config(fg="#63dbff" if checked else "red")

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def open_add_item_window(self):
        ItemEditorWindow(self)

    def open_edit_item_window(self, item, item_index):
        ItemEditorWindow(self, item=item, item_index=item_index)

    def save_item_to_json(self, new_item_data, item_index=None):
        if item_index is not None:
            self.items[item_index] = new_item_data
        else:
            self.items.append(new_item_data)
        with open(self.json_path, 'w') as f:
            json.dump(self.items, f, indent=4)
        self.refresh_items()

    def delete_item(self, item_index):
        if messagebox.askyesno("Delete Item", "Are you sure you want to delete this item?"):
            del self.items[item_index]
            with open(self.json_path, 'w') as f:
                json.dump(self.items, f, indent=4)
            self.refresh_items()

    def refresh_items(self):
        self.items = self.filter_existing_items(self.load_items())
        self.create_widgets()

if __name__ == "__main__":
    app = StartupManager()
    app.mainloop()