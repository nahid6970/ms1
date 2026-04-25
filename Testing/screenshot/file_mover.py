import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, colorchooser
import os
import json
import shutil
import win32com.client
import win32gui
import win32process
import psutil
from datetime import datetime

# Config file path
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "folders.json")

def load_folders():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                if not data:
                    return []
                # Handle legacy format if necessary
                if isinstance(data, list) and len(data) > 0 and isinstance(data[0], str):
                    return [{"path": p, "color": "#00ff41"} for p in data]
                return data
    except Exception as e:
        print(f"Error loading config: {e}")
    return []

def save_folders(folders):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(folders, f, indent=4)
    except Exception as e:
        messagebox.showerror("Error", f"Could not save config: {e}")

def get_explorer_selected_files():
    files = []
    try:
        shell = win32com.client.Dispatch("Shell.Application")
        windows = shell.Windows()
        for window in windows:
            # Check for both "File Explorer" and "Windows Explorer"
            if "Explorer" in window.Name or "explorer.exe" in window.FullName.lower():
                try:
                    items = window.Document.SelectedItems()
                    for item in items:
                        files.append(item.Path)
                except Exception:
                    continue
    except Exception as e:
        print(f"Error getting Explorer files: {e}")
    return list(set(files))

def get_photos_app_file():
    """
    Tries to find the current file being viewed in Microsoft Photos.
    """
    try:
        foreground_hwnd = win32gui.GetForegroundWindow()
        window_title = win32gui.GetWindowText(foreground_hwnd)
        
        _, pid = win32process.GetWindowThreadProcessId(foreground_hwnd)
        process = psutil.Process(pid)
        
        # Check if it's the Photos app (Microsoft.Photos.exe)
        if "Photos" in process.name() or "Microsoft.Photos" in window_title:
            # Look at the process's open files.
            # We filter for common image extensions.
            images = []
            for f in process.open_files():
                if f.path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff')):
                    images.append(f.path)
            
            if images:
                # If window title contains a filename, try to match it
                filename_from_title = window_title.split(" - Photos")[0].strip()
                for img_path in images:
                    if filename_from_title in os.path.basename(img_path):
                        return [img_path]
                # If no direct match, the last opened file might be the one
                return [images[-1]]
    except Exception as e:
        print(f"Error getting Photos app file: {e}")
    return []

class CollisionDialog(tk.Toplevel):
    def __init__(self, parent, filename):
        super().__init__(parent)
        self.title("File Collision")
        self.result = None # 'rename', 'skip', 'cancel'
        
        self.attributes('-topmost', True)
        self.geometry("400x180")
        self.resizable(False, False)
        self.configure(bg="#1a1a1a")
        
        # Center the dialog
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - 200
        y = (screen_height // 2) - 90
        self.geometry(f"+{x}+{y}")

        tk.Label(self, text="FILE ALREADY EXISTS", font=("JetBrainsMono NFP Bold", 12), 
                 bg="#1a1a1a", fg="#ffcc00").pack(pady=(10, 5))
        
        tk.Label(self, text=filename, font=("JetBrainsMono NFP", 10), 
                 bg="#1a1a1a", fg="#ffffff", wraplength=350).pack(pady=5)
        
        btn_frame = tk.Frame(self, bg="#1a1a1a")
        btn_frame.pack(fill="x", side="bottom", pady=15)
        
        style = {"font": ("JetBrainsMono NFP", 9), "relief": "flat", "padx": 10, "pady": 5, "cursor": "hand2"}
        
        tk.Button(btn_frame, text="RENAME", bg="#00ff41", fg="black", command=self.on_rename, **style).pack(side="left", padx=10, expand=True)
        tk.Button(btn_frame, text="SKIP", bg="#333333", fg="white", command=self.on_skip, **style).pack(side="left", padx=10, expand=True)
        tk.Button(btn_frame, text="CANCEL", bg="#ff4444", fg="white", command=self.on_cancel, **style).pack(side="left", padx=10, expand=True)
        
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.grab_set()
        self.wait_window()

    def on_rename(self):
        self.result = 'rename'
        self.destroy()

    def on_skip(self):
        self.result = 'skip'
        self.destroy()

    def on_cancel(self):
        self.result = 'cancel'
        self.destroy()

class FileMoverUI:
    def __init__(self, folders, files_to_move):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.folders = folders
        self.files_to_move = files_to_move
        self.edit_mode = False
        self.is_dialog_open = False

        # Colors & Theme (Matching region_screenshot.py)
        self.bg_color = "#0e0e0e"
        self.fg_color = "#ffffff"
        self.accent_main = "#00ff41" 
        self.accent_edit = "#ffcc00"
        
        self.font_name = "JetBrainsMono NFP"
        self.font_main = (self.font_name, 10)
        self.font_icon = (self.font_name, 36)
        self.font_small = (self.font_name, 8)
        self.font_title = (self.font_name + " Bold", 11)
        
        self.root.config(bg=self.accent_main)

        self.container = tk.Frame(self.root, bg=self.bg_color)
        self.container.pack(fill="both", expand=True, padx=1, pady=1)

        self.header = tk.Frame(self.container, bg=self.bg_color, cursor="fleur")
        self.header.pack(fill="x", padx=15, pady=(15, 5))
        
        title_text = f"MOVE {len(files_to_move)} FILES" if len(files_to_move) > 1 else "MOVE FILE"
        self.label_title = tk.Label(self.header, text=title_text, 
                              font=self.font_title, bg=self.bg_color, fg=self.accent_main)
        self.label_title.pack(side="left")

        self.btn_edit_toggle = tk.Button(self.header, text="EDIT: OFF", command=self.toggle_edit_mode,
                                       font=self.font_small, bg="#1a1a1a", fg="#666666",
                                       activebackground=self.accent_edit, activeforeground="black",
                                       relief="flat", bd=0, padx=10, cursor="hand2")
        self.btn_edit_toggle.pack(side="right")
        
        self.header.bind("<ButtonPress-1>", self.start_move)
        self.header.bind("<B1-Motion>", self.do_move)

        self.list_container = tk.Frame(self.container, bg=self.bg_color)
        self.list_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.render_folders()

        self.footer = tk.Frame(self.container, bg=self.bg_color)
        self.footer.pack(fill="x", pady=(0, 10))
        
        self.btn_close = tk.Button(self.footer, text="EXIT [ESC]", command=self.root.destroy,
                                 font=self.font_small, bg=self.bg_color, fg="#555555",
                                 activebackground="#ff0000", activeforeground="white",
                                 relief="flat", bd=0, padx=20, cursor="hand2")
        self.btn_close.pack()

        self.update_window_size()
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.root.bind("<FocusOut>", self.on_focus_out)
        self.root.after(100, self.force_focus)

    def on_focus_out(self, event):
        if getattr(self, 'is_dialog_open', False):
            return
        if self.root.focus_displayof() is None:
             self.root.destroy()

    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode
        color = self.accent_edit if self.edit_mode else "#666666"
        text = "EDIT: ON" if self.edit_mode else "EDIT: OFF"
        self.btn_edit_toggle.config(fg=color, text=text)
        self.render_folders()

    def update_window_size(self):
        self.list_container.update_idletasks()
        width = 820 
        total_items = len(self.folders) + 1 # ADD
        rows = (total_items + 4) // 5
        height = 110 + (rows * 135)
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - width/2)
        center_y = int(screen_height/2 - height/2)
        self.root.geometry(f"{width}x{height}+{center_x}+{center_y}")

    def render_folders(self):
        for widget in self.list_container.winfo_children():
            widget.destroy()

        for i, f_data in enumerate(self.folders):
            path = f_data["path"]
            color = f_data.get("color", "#00ff41")
            icon = f_data.get("icon", "\ueaf7")
            row = i // 5
            col = i % 5
            self.create_folder_card(path, color, icon, row, col, i)

        next_idx = len(self.folders)
        self.create_add_button(next_idx // 5, next_idx % 5)

    def create_folder_card(self, path, color, icon, row, col, index):
        card = tk.Frame(self.list_container, bg="#1a1a1a", width=150, height=120)
        card.grid(row=row, column=col, padx=5, pady=5)
        card.pack_propagate(False)

        name = os.path.basename(path)
        if not name: name = path
        
        icon_label = tk.Label(card, text=icon, font=self.font_icon, bg="#1a1a1a", fg=color)
        icon_label.pack(pady=(5, 0))

        name_label = tk.Label(card, text=name.upper()[:16], font=self.font_main, bg="#1a1a1a", fg=self.fg_color)
        name_label.pack()

        if self.edit_mode:
            card.config(highlightbackground=self.accent_edit, highlightthickness=1)
            
            # Management Buttons at bottom
            # Color
            col_l = tk.Label(card, text="🎨", font=self.font_main, bg="#1a1a1a", fg=self.accent_edit, cursor="hand2")
            col_l.place(x=10, y=90)
            col_l.bind("<Button-1>", lambda e, i=index: self.change_folder_color(i))
            
            # Icon 
            ico_l = tk.Label(card, text="🔣", font=self.font_main, bg="#1a1a1a", fg=self.accent_edit, cursor="hand2")
            ico_l.place(x=65, y=90)
            ico_l.bind("<Button-1>", lambda e, i=index: self.change_folder_icon(i))

            # Delete
            del_l = tk.Label(card, text="✕", font=self.font_main, bg="#1a1a1a", fg="#ff4444", cursor="hand2")
            del_l.place(x=125, y=90)
            del_l.bind("<Button-1>", lambda e, i=index: self.remove_folder(i))

        widgets = [card, icon_label, name_label]
        for w in widgets:
            if not self.edit_mode:
                w.bind("<Button-1>", lambda e, p=path: self.execute_move(p))
                w.config(cursor="hand2")
            w.bind("<Enter>", lambda e, c=card: self.on_hover(c))
            w.bind("<Leave>", lambda e, c=card: self.on_leave(c))

    def change_folder_color(self, index):
        self.is_dialog_open = True
        color = colorchooser.askcolor(title="Choose Folder Color", initialcolor=self.folders[index]["color"], parent=self.root)[1]
        self.is_dialog_open = False
        self.root.focus_force()
        if color:
            self.folders[index]["color"] = color
            save_folders(self.folders)
            self.render_folders()

    def change_folder_icon(self, index):
        self.is_dialog_open = True
        new_icon = simpledialog.askstring("Folder Icon", "Paste new icon glyph:", 
                                         initialvalue=self.folders[index].get("icon", "\ueaf7"),
                                         parent=self.root)
        self.is_dialog_open = False
        self.root.focus_force()
        if new_icon:
            self.folders[index]["icon"] = new_icon
            save_folders(self.folders)
            self.render_folders()

    def create_add_button(self, row, col):
        card = tk.Frame(self.list_container, bg="#121212", width=150, height=120)
        card.grid(row=row, column=col, padx=5, pady=5)
        card.pack_propagate(False)

        icon_label = tk.Label(card, text="+", font=(self.font_name, 36), bg="#121212", fg="#444444")
        icon_label.pack(expand=True)

        card.bind("<Button-1>", lambda e: self.add_new_folder())
        icon_label.bind("<Button-1>", lambda e: self.add_new_folder())
        
        for w in [card, icon_label]:
            w.bind("<Enter>", lambda e: self.on_add_hover(card, icon_label))
            w.bind("<Leave>", lambda e: self.on_add_leave(card, icon_label))
            w.config(cursor="hand2")

    def on_add_hover(self, card, label):
        card.config(bg="#1a1a1a")
        label.config(bg="#1a1a1a")

    def on_add_leave(self, card, label):
        card.config(bg="#121212")
        label.config(bg="#121212")

    def on_hover(self, card):
        if not self.edit_mode:
            card.config(bg="#252525")
            for w in card.winfo_children():
                w.config(bg="#252525")

    def on_leave(self, card):
        if not self.edit_mode:
            card.config(bg="#1a1a1a")
            for w in card.winfo_children():
                w.config(bg="#1a1a1a")

    def add_new_folder(self):
        self.is_dialog_open = True
        path = filedialog.askdirectory(parent=self.root)
        self.is_dialog_open = False
        self.root.focus_force()
        if path:
            self.folders.append({"path": path, "color": "#00ff41"})
            save_folders(self.folders)
            self.render_folders()
            self.update_window_size()

    def remove_folder(self, index):
        self.is_dialog_open = True
        if messagebox.askyesno("Confirm", "Remove this folder?", parent=self.root):
            self.folders.pop(index)
            save_folders(self.folders)
            self.render_folders()
            self.update_window_size()
        self.is_dialog_open = False
        self.root.focus_force()

    def execute_move(self, target_dir):
        if not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)

        for src_path in self.files_to_move:
            if not os.path.exists(src_path):
                continue
                
            filename = os.path.basename(src_path)
            dest_path = os.path.join(target_dir, filename)
            
            if os.path.exists(dest_path):
                dialog = CollisionDialog(self.root, filename)
                if dialog.result == 'rename':
                    # Generate unique name
                    name, ext = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(os.path.join(target_dir, f"{name}_{counter}{ext}")):
                        counter += 1
                    dest_path = os.path.join(target_dir, f"{name}_{counter}{ext}")
                elif dialog.result == 'skip':
                    continue
                else: # cancel
                    break
            
            try:
                shutil.move(src_path, dest_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to move {filename}: {e}", parent=self.root)
        
        self.root.destroy()

    def force_focus(self):
        self.root.focus_force()
        self.root.lift()

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def run(self):
        self.root.mainloop()

def main():
    # 1. Gather files
    files = get_explorer_selected_files()
    if not files:
        files = get_photos_app_file()
    
    if not files:
        return

    # 2. Load folders
    folders = load_folders()
    
    # 3. Show UI
    mover = FileMoverUI(folders, files)
    mover.run()

if __name__ == "__main__":
    main()
