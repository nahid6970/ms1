import customtkinter as ctk
import json
import os
import sys
from tkinter import filedialog, messagebox
import subprocess

# Set appearance and theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Font configuration
FONT_FAMILY = "JetBrainsMono NFP"

class AddLinkDialog(ctk.CTkToplevel):
    def __init__(self, parent, on_save_callback, edit_data=None):
        super().__init__(parent)
        title_text = "Edit Symlink" if edit_data else "Add New Symlink"
        self.title(title_text)
        self.geometry("800x450")
        self.on_save_callback = on_save_callback
        self.edit_data = edit_data
        
        # Make it modal-like
        self.after(10, self.lift)
        self.focus_force()
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)

        self.label = ctk.CTkLabel(self, text=title_text, font=ctk.CTkFont(family=FONT_FAMILY, size=20, weight="bold"))
        self.label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.name_entry = ctk.CTkEntry(self, placeholder_text="Entry Name", font=ctk.CTkFont(family=FONT_FAMILY), corner_radius=0)
        self.name_entry.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        # Type Selection (Folder vs File)
        self.type_var = ctk.StringVar(value="folder")
        self.type_label = ctk.CTkLabel(self, text="Select Type:", font=ctk.CTkFont(family=FONT_FAMILY, size=12))
        self.type_label.grid(row=2, column=0, padx=20, pady=(5, 0), sticky="w")
        
        self.type_menu = ctk.CTkSegmentedButton(self, values=["folder", "file"], variable=self.type_var, font=ctk.CTkFont(family=FONT_FAMILY), corner_radius=0)
        self.type_menu.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.target_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.target_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        self.target_frame.grid_columnconfigure(1, weight=1)

        self.target_btn = ctk.CTkButton(self.target_frame, text="📂 Target", width=100, corner_radius=0, 
                                       fg_color="#3498db", hover_color="#2980b9",
                                       font=ctk.CTkFont(family=FONT_FAMILY), command=self.browse_target)
        self.target_btn.grid(row=0, column=0, padx=(0, 10))

        self.target_entry = ctk.CTkEntry(self.target_frame, placeholder_text="Target Path (Real)", corner_radius=0, 
                                        font=ctk.CTkFont(family=FONT_FAMILY))
        self.target_entry.grid(row=0, column=1, sticky="ew")

        self.fake_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.fake_frame.grid(row=5, column=0, padx=20, pady=10, sticky="ew")
        self.fake_frame.grid_columnconfigure(1, weight=1)

        self.fake_btn = ctk.CTkButton(self.fake_frame, text="📂 Fake", width=100, corner_radius=0, 
                                     fg_color="#9b59b6", hover_color="#8e44ad",
                                     font=ctk.CTkFont(family=FONT_FAMILY), command=self.browse_fake)
        self.fake_btn.grid(row=0, column=0, padx=(0, 10))

        self.fake_entry = ctk.CTkEntry(self.fake_frame, placeholder_text="Fake Path (Shortcut)", corner_radius=0, 
                                      font=ctk.CTkFont(family=FONT_FAMILY))
        self.fake_entry.grid(row=0, column=1, sticky="ew")

        btn_text = "✅ Save Changes" if edit_data else "➕ Add Entry"
        self.save_btn = ctk.CTkButton(self, text=btn_text, command=self.save_link, corner_radius=0, 
                                     font=ctk.CTkFont(family=FONT_FAMILY, weight="bold"),
                                     fg_color="#2ecc71", hover_color="#27ae60")
        self.save_btn.grid(row=6, column=0, padx=20, pady=20)

        # Pre-fill if editing
        if edit_data:
            self.name_entry.insert(0, edit_data.get("name", ""))
            self.target_entry.insert(0, edit_data.get("target", ""))
            self.fake_entry.insert(0, edit_data.get("fake", ""))
            self.type_var.set(edit_data.get("type", "folder"))

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

    def save_link(self):
        name = self.name_entry.get().strip()
        target = self.target_entry.get().strip()
        fake = self.fake_entry.get().strip()
        link_type = self.type_var.get()

        if not name or not target or not fake:
            messagebox.showwarning("Incomplete Data", "Please fill all fields.")
            return

        self.on_save_callback(name, target, fake, link_type)
        self.destroy()

class SymlinkManager(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Symlink Manager")
        self.geometry("1000x600")

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

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh_ui())

        self.search_entry = ctk.CTkEntry(self.header_frame, placeholder_text="Search symlinks...", 
                                        font=ctk.CTkFont(family=FONT_FAMILY),
                                        textvariable=self.search_var, corner_radius=0)
        self.search_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self.add_plus_btn = ctk.CTkButton(self.header_frame, text="➕ Add Link", width=100, 
                                         font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
                                         corner_radius=0, fg_color="#2ecc71", hover_color="#27ae60", command=self.open_add_dialog)
        self.add_plus_btn.grid(row=0, column=1, sticky="e")

        # Scrollable list of items
        self.scrollable_frame = ctk.CTkScrollableFrame(self.main_frame, label_text="Symlink Entries", 
                                                       label_font=ctk.CTkFont(family=FONT_FAMILY, weight="bold"))
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
        self.search_var.set("") # Clear search when adding new
        self.save_data()
        self.refresh_ui()

    def edit_link(self, index):
        query = self.search_var.get().lower()
        filtered_links = [l for l in self.links if query in l['name'].lower() or query in l['target'].lower() or query in l['fake'].lower()]
        target_link = filtered_links[index]
        
        def on_save(name, target, fake, link_type):
            target_link["name"] = name
            target_link["target"] = target
            target_link["fake"] = fake
            target_link["type"] = link_type
            self.save_data()
            self.refresh_ui()

        AddLinkDialog(self, on_save, edit_data=target_link)

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
            # Find the actual object to remove if filtered
            query = self.search_var.get().lower()
            filtered_links = [l for l in self.links if query in l['name'].lower() or query in l['target'].lower() or query in l['fake'].lower()]
            target_link = filtered_links[index]
            self.links.remove(target_link)
            
            self.save_data()
            self.refresh_ui()

    def create_link(self, index):
        # Find actual link if filtered
        query = self.search_var.get().lower()
        filtered_links = [l for l in self.links if query in l['name'].lower() or query in l['target'].lower() or query in l['fake'].lower()]
        link = filtered_links[index]
        
        target = os.path.normpath(link["target"])
        fake = os.path.normpath(link["fake"])
        link_type = link.get("type", "folder")

        if not os.path.exists(target):
            messagebox.showerror("Error", f"Target path does not exist:\n{target}")
            return

        # Check if fake path already exists and is not a proper link
        if os.path.exists(fake) or os.path.lexists(fake):
            is_proper_link = os.path.islink(fake) or (link_type == "folder" and self.is_junction(fake))
            
            if not is_proper_link:
                # File/folder exists but is not a symbolic link
                response = messagebox.askyesnocancel(
                    "File Already Exists", 
                    f"A {link_type} already exists at:\n{fake}\n\nThis is not a symbolic link. Would you like to delete it and create the symbolic link?\n\nClick 'Yes' to delete and create link\nClick 'No' to cancel\nClick 'Cancel' to abort"
                )
                
                if response is None:  # Cancel
                    return
                elif response:  # Yes - delete existing file/folder
                    try:
                        if link_type == "folder":
                            import shutil
                            shutil.rmtree(fake)
                        else:
                            os.remove(fake)
                    except Exception as e:
                        messagebox.showerror("Delete Error", f"Failed to delete existing {link_type}:\n{str(e)}")
                        return
                else:  # No - cancel operation
                    return
            else:
                # It IS a proper link/junction.
                # We must remove the existing one first.
                try:
                    # Check if it is a directory (Junction or Directory Symlink)
                    if os.path.isdir(fake):
                        os.rmdir(fake)
                    else:
                        # It is a file (File Symlink)
                        os.remove(fake)
                except Exception as e:
                    messagebox.showerror("Delete Error", f"Failed to remove existing link before creating new one:\n{str(e)}")
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
                if "privilege" in error_msg.lower() or "access is denied" in error_msg.lower():
                     # Try to run as admin
                    try:
                        import ctypes
                        import time
                        
                        # Use ShellExecute with 'runas' to trigger UAC
                        # We must quote the command correctly for cmd /c
                        # cmd /c mklink "fake" "target"
                        
                        # Note: ShellExecuteW params are separated. 
                        # File: cmd.exe, Params: /c mklink ...
                        
                        params = f'/c {cmd}'
                        ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd.exe", params, None, 1)
                        
                        if ret > 32: # Success
                            time.sleep(0.5) # Give it a moment to execute
                            # We can't capture output from ShellExecute easily, so we check existence
                            if os.path.exists(fake) or os.path.islink(fake):
                                messagebox.showinfo("Success", f"Link created with Admin privileges:\n{fake}")
                            else:
                                # It might have failed silently or user clicked No
                                messagebox.showwarning("Check Status", "Admin command issued. Please check if the link was created.")
                        else:
                            messagebox.showerror("Error", "Failed to elevate privileges.")
                            
                    except Exception as admin_e:
                        messagebox.showerror("Error", f"Failed to run as admin: {str(admin_e)}")
                        
                elif "file already exists" in error_msg.lower():
                    # This shouldn't happen now, but just in case
                    messagebox.showerror("Error", f"File still exists after deletion attempt:\n{error_msg}")
                else:
                    messagebox.showerror("Error", f"Failed to create link:\n{error_msg}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
        
        self.refresh_ui()

    def open_folder(self, index):
        query = self.search_var.get().lower()
        filtered_links = [l for l in self.links if query in l['name'].lower() or query in l['target'].lower() or query in l['fake'].lower()]
        link = filtered_links[index]
        
        path = os.path.normpath(link["fake"])
        
        try:
            subprocess.Popen(f'explorer /select,"{path}"')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open folder:\n{str(e)}")

    def refresh_ui(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        query = self.search_var.get().lower()
        filtered_links = [l for l in self.links if query in l['name'].lower() or query in l['target'].lower() or query in l['fake'].lower()]

        if not filtered_links:
            text = "No symlinks added yet." if not self.links else "No matches found."
            empty_label = ctk.CTkLabel(self.scrollable_frame, text=text, font=ctk.CTkFont(family=FONT_FAMILY, slant="italic"))
            empty_label.grid(row=0, column=0, padx=20, pady=20)
            return

        for i, link in enumerate(filtered_links):
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
            info_frame.grid(row=0, column=0, columnspan=2, padx=15, pady=(10, 5), sticky="w")

            name_label = ctk.CTkLabel(info_frame, text=link["name"], font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"))
            name_label.grid(row=0, column=0, sticky="w")

            status_label = ctk.CTkLabel(info_frame, text=f"({status})", text_color=status_color, font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"))
            status_label.grid(row=0, column=1, padx=(10, 0), sticky="w")

            # Paths
            paths_text = f"Target: {link['target']}\nLink: {link['fake']}"
            paths_label = ctk.CTkLabel(item_frame, text=paths_text, font=ctk.CTkFont(family=FONT_FAMILY, size=11), justify="left", text_color="#bdc3c7")
            paths_label.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="w")

            btn_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            btn_frame.grid(row=0, column=2, rowspan=2, padx=15, pady=10, sticky="e")
            
            col_idx = 0

            # Fix/Create Button
            if status != "Working":
                fix_btn = ctk.CTkButton(btn_frame, text="🔗 Fix", width=75, height=28, 
                                       corner_radius=0, font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                                       fg_color="#3498db", hover_color="#2980b9",
                                       command=lambda idx=i: self.create_link(idx))
                fix_btn.grid(row=0, column=col_idx, padx=(0, 5))
                col_idx += 1

            # Open Button
            open_btn = ctk.CTkButton(btn_frame, text="📂 Open", width=75, height=28, 
                                    corner_radius=0, font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                                    fg_color="#8e44ad", hover_color="#9b59b6",
                                    command=lambda idx=i: self.open_folder(idx))
            open_btn.grid(row=0, column=col_idx, padx=(0, 5))
            col_idx += 1

            # Edit Button
            edit_btn = ctk.CTkButton(btn_frame, text="📝 Edit", width=75, height=28, 
                                    corner_radius=0, font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                                    fg_color="#f39c12", hover_color="#e67e22",
                                    command=lambda idx=i: self.edit_link(idx))
            edit_btn.grid(row=0, column=col_idx, padx=(0, 5))
            col_idx += 1

            # Delete button
            del_btn = ctk.CTkButton(btn_frame, text="🗑️ Del", width=75, height=28, 
                                   corner_radius=0, font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                                   fg_color="#c0392b", hover_color="#e74c3c",
                                   command=lambda idx=i: self.delete_link(idx))
            del_btn.grid(row=0, column=col_idx)

if __name__ == "__main__":
    app = SymlinkManager()
    app.mainloop()
