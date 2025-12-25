import customtkinter as ctk
import json
import os
import sys
from tkinter import filedialog, messagebox

# Set appearance and theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AddLinkDialog(ctk.CTkToplevel):
    def __init__(self, parent, on_add_callback):
        super().__init__(parent)
        self.title("Add New Symlink")
        self.geometry("400x450")
        self.on_add_callback = on_add_callback
        
        # Make it modal-like
        self.after(10, self.lift)
        self.focus_force()
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)

        self.label = ctk.CTkLabel(self, text="Add New Symlink", font=ctk.CTkFont(size=20, weight="bold"))
        self.label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.name_entry = ctk.CTkEntry(self, placeholder_text="Entry Name")
        self.name_entry.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        # Type Selection (Folder vs File)
        self.type_var = ctk.StringVar(value="folder")
        self.type_label = ctk.CTkLabel(self, text="Select Type:", font=ctk.CTkFont(size=12))
        self.type_label.grid(row=2, column=0, padx=20, pady=(5, 0), sticky="w")
        
        self.type_menu = ctk.CTkSegmentedButton(self, values=["folder", "file"], variable=self.type_var)
        self.type_menu.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.target_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.target_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        self.target_frame.grid_columnconfigure(1, weight=1)

        self.target_btn = ctk.CTkButton(self.target_frame, text="Browse", width=80, command=self.browse_target)
        self.target_btn.grid(row=0, column=0, padx=(0, 10))

        self.target_entry = ctk.CTkEntry(self.target_frame, placeholder_text="Target Path (Real)")
        self.target_entry.grid(row=0, column=1, sticky="ew")

        self.fake_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.fake_frame.grid(row=5, column=0, padx=20, pady=10, sticky="ew")
        self.fake_frame.grid_columnconfigure(1, weight=1)

        self.fake_btn = ctk.CTkButton(self.fake_frame, text="Browse", width=80, command=self.browse_fake)
        self.fake_btn.grid(row=0, column=0, padx=(0, 10))

        self.fake_entry = ctk.CTkEntry(self.fake_frame, placeholder_text="Fake Path (Shortcut)")
        self.fake_entry.grid(row=0, column=1, sticky="ew")

        self.add_btn = ctk.CTkButton(self, text="Add Entry", command=self.add_link, fg_color="#2ecc71", hover_color="#27ae60")
        self.add_btn.grid(row=6, column=0, padx=20, pady=20)

    def browse_target(self):
        if self.type_var.get() == "folder":
            path = filedialog.askdirectory()
        else:
            path = filedialog.askopenfilename()
        
        if path:
            self.target_entry.delete(0, "end")
            self.target_entry.insert(0, path)

    def browse_fake(self):
        if self.type_var.get() == "folder":
            path = filedialog.askdirectory()
        else:
            path = filedialog.asksaveasfilename()
        
        if path:
            self.fake_entry.delete(0, "end")
            self.fake_entry.insert(0, path)

    def add_link(self):
        name = self.name_entry.get().strip()
        target = self.target_entry.get().strip()
        fake = self.fake_entry.get().strip()
        link_type = self.type_var.get()

        if not name or not target or not fake:
            messagebox.showwarning("Incomplete Data", "Please fill all fields.")
            return

        self.on_add_callback(name, target, fake, link_type)
        self.destroy()

class SymlinkManager(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Symlink Manager")
        self.geometry("700x600")

        self.data_file = "links.json"
        self.links = self.load_data()

        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main view
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        # Header Frame for Title and Add Button
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.list_label = ctk.CTkLabel(self.header_frame, text="Managed Symlinks", font=ctk.CTkFont(size=22, weight="bold"))
        self.list_label.grid(row=0, column=0, sticky="w")

        self.add_plus_btn = ctk.CTkButton(self.header_frame, text="+", width=40, font=ctk.CTkFont(size=20, weight="bold"),
                                         fg_color="#2ecc71", hover_color="#27ae60", command=self.open_add_dialog)
        self.add_plus_btn.grid(row=0, column=1, sticky="e")

        # Scrollable list of items
        self.scrollable_frame = ctk.CTkScrollableFrame(self.main_frame, label_text="Symlink Entries")
        self.scrollable_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        self.refresh_ui()

    def open_add_dialog(self):
        AddLinkDialog(self, self.on_link_added)

    def on_link_added(self, name, target, fake, link_type):
        self.links.append({
            "name": name,
            "target": target,
            "fake": fake,
            "type": link_type
        })
        self.save_data()
        self.refresh_ui()

    def load_data(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_file = os.path.join(script_dir, "links.json")
        
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_data(self):
        with open(self.data_file, "w") as f:
            json.dump(self.links, f, indent=4)

    def check_status(self, target, fake, link_type):
        if not os.path.exists(fake) and not os.path.lexists(fake):
            return "Missing Link"
        
        try:
            is_link = os.path.islink(fake) or (link_type == "folder" and self.is_junction(fake))
            
            if not is_link:
                return f"Not a {link_type.capitalize()} Link"
            
            realpath = os.path.realpath(fake)
            target_norm = os.path.normpath(target).lower()
            real_norm = os.path.normpath(realpath).lower()

            if real_norm == target_norm:
                if os.path.exists(target):
                    return "Working"
                else:
                    return "Broken (Target Missing)"
            else:
                return "Points Elsewhere"
        except Exception as e:
            return f"Error: {str(e)}"

    def is_junction(self, path):
        try:
            import ctypes
            FILE_ATTRIBUTE_REPARSE_POINT = 0x0400
            attrs = ctypes.windll.kernel32.GetFileAttributesW(path)
            return bool(attrs != -1 and (attrs & FILE_ATTRIBUTE_REPARSE_POINT))
        except:
            return False

    def delete_link(self, index):
        if messagebox.askyesno("Confirm", "Delete this entry?"):
            self.links.pop(index)
            self.save_data()
            self.refresh_ui()

    def create_link(self, index):
        link = self.links[index]
        target = link["target"]
        fake = link["fake"]
        link_type = link.get("type", "folder")

        if not os.path.exists(target):
            messagebox.showerror("Error", f"Target path does not exist:\n{target}")
            return

        try:
            if link_type == "folder":
                cmd = f'mklink /J "{fake}" "{target}"'
            else:
                cmd = f'mklink "{fake}" "{target}"'

            import subprocess
            result = subprocess.run(f'cmd /c {cmd}', capture_output=True, text=True, shell=True)

            if result.returncode == 0:
                messagebox.showinfo("Success", f"Link created successfully:\n{fake}")
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                if "Privilege" in error_msg or "access is denied" in error_msg.lower():
                    messagebox.showerror("Permission Denied", "Creation failed. Please run this script as Administrator to create symlinks.")
                else:
                    messagebox.showerror("Error", f"Failed to create link:\n{error_msg}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
        
        self.refresh_ui()

    def refresh_ui(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not self.links:
            empty_label = ctk.CTkLabel(self.scrollable_frame, text="No symlinks added yet.", font=ctk.CTkFont(slant="italic"))
            empty_label.grid(row=0, column=0, padx=20, pady=20)
            return

        for i, link in enumerate(self.links):
            link_type = link.get("type", "folder") 
            status = self.check_status(link["target"], link["fake"], link_type)
            
            if status == "Working":
                status_color = "#2ecc71"
            elif "Broken" in status or "Error" in status:
                status_color = "#e74c3c"
            else:
                status_color = "#f39c12"

            item_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent", border_width=1, border_color="#34495e")
            item_frame.grid(row=i, column=0, padx=10, pady=5, sticky="ew")
            item_frame.grid_columnconfigure(1, weight=1)

            info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            info_frame.grid(row=0, column=0, columnspan=2, padx=15, pady=(10, 5), sticky="ew")
            info_frame.grid_columnconfigure(0, weight=1)

            name_label = ctk.CTkLabel(info_frame, text=link["name"], font=ctk.CTkFont(size=14, weight="bold"))
            name_label.grid(row=0, column=0, sticky="w")

            status_label = ctk.CTkLabel(info_frame, text=status, text_color=status_color, font=ctk.CTkFont(size=11, weight="bold"))
            status_label.grid(row=0, column=1, sticky="e")

            paths_text = f"Target: {link['target']}\nLink: {link['fake']}"
            paths_label = ctk.CTkLabel(item_frame, text=paths_text, font=ctk.CTkFont(size=11), justify="left", text_color="#bdc3c7")
            paths_label.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="w")

            btn_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            btn_frame.grid(row=0, column=2, rowspan=2, padx=15, pady=10, sticky="e")

            if status != "Working":
                fix_btn = ctk.CTkButton(btn_frame, text="Fix/Link", width=70, height=28, 
                                       fg_color="#3498db", hover_color="#2980b9",
                                       command=lambda idx=i: self.create_link(idx))
                fix_btn.grid(row=0, column=0, padx=(0, 5))

            del_btn = ctk.CTkButton(btn_frame, text="Remove", width=70, height=28, 
                                   fg_color="#c0392b", hover_color="#e74c3c",
                                   command=lambda idx=i: self.delete_link(idx))
            del_btn.grid(row=0, column=1)

if __name__ == "__main__":
    app = SymlinkManager()
    app.mainloop()
