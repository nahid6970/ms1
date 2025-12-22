import tkinter as tk
from tkinter import messagebox, filedialog, colorchooser, simpledialog
import os
import json
import subprocess
import sys

# Config file path
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

def load_folders():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                if not data:
                    return []
                # Migration safety
                if isinstance(data, list) and len(data) > 0 and isinstance(data[0], str):
                    return [{"path": p, "color": "#00ff41", "icon": "\ueaf7"} for p in data]
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

class FolderLauncher:
    def __init__(self, folders):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.folders = folders
        self.edit_mode = False

        # Colors & Theme
        self.bg_color = "#0e0e0e"
        self.fg_color = "#ffffff"
        self.accent_main = "#00ff41" # Matrix Green
        self.accent_edit = "#ffcc00" # Warning/Edit Color
        
        # Fonts - JetBrains Mono
        self.font_name = "JetBrains Mono"
        self.font_main = (self.font_name, 10)
        self.font_icon = (self.font_name, 36)
        self.font_small = (self.font_name, 8)
        self.font_title = (self.font_name + " Bold", 11)
        
        self.root.config(bg="#1a1a1a")

        self.container = tk.Frame(self.root, bg=self.bg_color)
        self.container.pack(fill="both", expand=True, padx=2, pady=2)

        # Header
        self.header = tk.Frame(self.container, bg=self.bg_color, cursor="fleur")
        self.header.pack(fill="x", padx=15, pady=(15, 5))
        
        self.label_title = tk.Label(self.header, text="QUICK LAUNCHER", 
                              font=self.font_title, bg=self.bg_color, fg=self.accent_main,
                              cursor="arrow")
        self.label_title.pack(side="left")

        # Edit Toggle Button
        self.btn_edit_toggle = tk.Button(self.header, text="EDIT: OFF", command=self.toggle_edit_mode,
                                       font=self.font_small, bg="#1a1a1a", fg="#666666",
                                       activebackground=self.accent_edit, activeforeground="black",
                                       relief="flat", bd=0, padx=10, cursor="hand2")
        self.btn_edit_toggle.pack(side="right")
        
        self.header.bind("<ButtonPress-1>", self.start_move)
        self.header.bind("<B1-Motion>", self.do_move)

        # Grid Container
        self.list_container = tk.Frame(self.container, bg=self.bg_color)
        self.list_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.render_folders()

        # Footer
        self.footer = tk.Frame(self.container, bg=self.bg_color)
        self.footer.pack(fill="x", pady=(0, 10))
        
        self.btn_close = tk.Button(self.footer, text="EXIT [ESC]", command=self.root.destroy,
                                 font=self.font_small, bg=self.bg_color, fg="#555555",
                                 activebackground="#ff0000", activeforeground="white",
                                 relief="flat", bd=0, padx=20, cursor="hand2")
        self.btn_close.pack()

        self.update_window_size()
        
        # Focus & Bindings
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.root.bind("<FocusOut>", self.on_focus_out)
        self.root.after(100, self.force_focus)

    def on_focus_out(self, event):
        # Only destroy if the focus actually left the root window
        # (widget is None means it went to another app)
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
        # Same geometry as the paid version ;)
        width = 820 
        # Items + 1 for Add button
        total_items = len(self.folders) + 1 
        rows = (total_items + 4) // 5
        height = 110 + (rows * 135)
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - width/2)
        center_y = int(screen_height/2 - height/2)
        self.root.geometry(f'{width}x{height}+{center_x}+{center_y}')

    def render_folders(self):
        for widget in self.list_container.winfo_children():
            widget.destroy()

        # Prepare items: path, color, icon, index
        items = []
        for i, f_data in enumerate(self.folders):
            icon = f_data.get('icon', "\ueaf7")
            items.append((f_data['path'], f_data['color'], icon, i))

        for idx, (path, color, icon, f_idx) in enumerate(items):
            row = idx // 5
            col = idx % 5
            self.create_folder_card(path, color, icon, row, col, f_idx)

        next_idx = len(items)
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
            
            # Color
            col_l = tk.Label(card, text="🎨", font=self.font_small, bg="#1a1a1a", fg=self.accent_edit, cursor="hand2")
            col_l.place(x=10, y=90)
            col_l.bind("<Button-1>", lambda e, i=index: self.change_folder_color(i))
            
            # Icon 
            ico_l = tk.Label(card, text="🔣", font=self.font_small, bg="#1a1a1a", fg=self.accent_edit, cursor="hand2")
            ico_l.place(x=65, y=90)
            ico_l.bind("<Button-1>", lambda e, i=index: self.change_folder_icon(i))

            # Delete
            del_l = tk.Label(card, text="✕", font=self.font_small, bg="#1a1a1a", fg="#ff4444", cursor="hand2")
            del_l.place(x=125, y=90)
            del_l.bind("<Button-1>", lambda e, i=index: self.remove_folder(i))

        widgets = [card, icon_label, name_label]
        for w in widgets:
            if not self.edit_mode:
                w.bind("<Button-1>", lambda e, p=path: self.launch_folder(p))
                w.config(cursor="hand2")
            
            w.bind("<Enter>", lambda e, c=card, col=color: self.on_hover(c, col))
            w.bind("<Leave>", lambda e, c=card: self.on_leave(c))

    def create_add_button(self, row, col):
        card = tk.Frame(self.list_container, bg="#121212", width=150, height=120)
        card.grid(row=row, column=col, padx=5, pady=5)
        card.pack_propagate(False)

        icon_label = tk.Label(card, text="+", font=(self.font_name, 36), bg="#121212", fg="#444444")
        icon_label.pack(expand=True)

        for w in [card, icon_label]:
            w.bind("<Button-1>", lambda e: self.add_new_folder())
            w.bind("<Enter>", lambda e: self.on_add_hover(card, icon_label))
            w.bind("<Leave>", lambda e: self.on_add_leave(card, icon_label))
            w.config(cursor="hand2")

    def on_add_hover(self, card, label):
        card.config(bg="#1a1a1a")
        label.config(bg="#1a1a1a")

    def on_add_leave(self, card, label):
        card.config(bg="#121212")
        label.config(bg="#121212")

    def on_hover(self, card, color):
        if not self.edit_mode:
            card.config(bg="#252525")
            for w in card.winfo_children():
                w.config(bg="#252525")

    def on_leave(self, card):
        if not self.edit_mode:
            card.config(bg="#1a1a1a")
            for w in card.winfo_children():
                w.config(bg="#1a1a1a")

    def launch_folder(self, path):
        if os.path.exists(path):
            subprocess.run(["explorer", os.path.normpath(path)])
            self.root.destroy()
        else:
            messagebox.showwarning("Error", f"Folder does not exist: {path}")

    def change_folder_color(self, index):
        color = colorchooser.askcolor(title="Choose Folder Color", initialcolor=self.folders[index]['color'], parent=self.root)[1]
        if color:
            self.folders[index]['color'] = color
            save_folders(self.folders)
            self.render_folders()

    def change_folder_icon(self, index):
        new_icon = simpledialog.askstring("Folder Icon", "Paste new icon glyph:", 
                                         initialvalue=self.folders[index].get('icon', "\ueaf7"),
                                         parent=self.root)
        if new_icon:
            self.folders[index]['icon'] = new_icon
            save_folders(self.folders)
            self.render_folders()

    def remove_folder(self, index):
        if messagebox.askyesno("Confirm", "Remove this folder?", parent=self.root):
            self.folders.pop(index)
            save_folders(self.folders)
            self.render_folders()
            self.update_window_size()

    def add_new_folder(self):
        path = filedialog.askdirectory(title="Select Folder to Add", parent=self.root)
        if path:
            color = colorchooser.askcolor(title="Choose Folder Color", initialcolor="#00ff41", parent=self.root)[1]
            if not color: color = "#00ff41"
            self.folders.append({"path": path, "color": color, "icon": "\ueaf7"})
            save_folders(self.folders)
            self.render_folders()
            self.update_window_size()

    def force_focus(self):
        self.root.focus_force()
        self.root.lift()
        self.root.focus_set()
        try: self.root.grab_set()
        except: pass

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

def main():
    try:
        folders = load_folders()
        FolderLauncher(folders).root.mainloop()
            
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        temp_root = tk.Tk()
        temp_root.withdraw()
        messagebox.showerror("Launcher Error", f"{error_msg}")
        temp_root.destroy()

if __name__ == "__main__":
    main()
