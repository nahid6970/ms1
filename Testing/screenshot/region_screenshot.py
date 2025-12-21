import tkinter as tk
from tkinter import messagebox, filedialog, colorchooser
from PIL import ImageGrab, Image
import os
import json
from datetime import datetime
import io
import subprocess

# Config file path
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "folders.json")

def load_folders():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                if not data:
                    return []
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

class RegionSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes('-alpha', 0.5) 
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.config(cursor="cross")

        self.canvas = tk.Canvas(self.root, cursor="cross", bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.start_x = None
        self.start_y = None
        self.rect = None
        self.selection = None
        
        self.v_line = self.canvas.create_line(0, 0, 0, 0, fill="#ffffff", width=1)
        self.h_line = self.canvas.create_line(0, 0, 0, 0, fill="#ffffff", width=1)

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.root.bind("<Escape>", lambda e: self.root.destroy())

    def on_mouse_move(self, event):
        w, h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.canvas.coords(self.v_line, event.x, 0, event.x, h)
        self.canvas.coords(self.h_line, 0, event.y, w, event.y)

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, 
            outline='#00ffff', width=2
        )

    def on_move_press(self, event):
        cur_x, cur_y = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)
        self.on_mouse_move(event)

    def on_button_release(self, event):
        end_x, end_y = (event.x, event.y)
        x1 = min(self.start_x, end_x)
        y1 = min(self.start_y, end_y)
        x2 = max(self.start_x, end_x)
        y2 = max(self.start_y, end_y)
        
        if x2 - x1 > 2 and y2 - y1 > 2:
            self.selection = (x1, y1, x2, y2)
        
        self.root.destroy()

    def get_selection(self):
        self.root.mainloop()
        return self.selection

class FolderChooser:
    def __init__(self, folders, screenshot_img):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.choice = None
        self.folders = folders
        self.img = screenshot_img
        self.edit_mode = False

        # Colors & Theme
        self.bg_color = "#0e0e0e"
        self.fg_color = "#ffffff"
        self.accent_main = "#00ff41" # Matrix Green
        self.accent_edit = "#ffcc00" # Warning/Edit Color
        
        self.font_main = ("JetBrains Mono", 10)
        self.font_icon = ("JetBrains Mono", 18)
        self.font_small = ("JetBrains Mono", 8)
        self.font_title = ("JetBrains Mono Bold", 11)
        
        self.root.config(bg="#1a1a1a")

        # Main Container
        self.container = tk.Frame(self.root, bg=self.bg_color)
        self.container.pack(fill="both", expand=True, padx=2, pady=2)

        # Header
        self.header = tk.Frame(self.container, bg=self.bg_color, cursor="fleur")
        self.header.pack(fill="x", padx=15, pady=(15, 5))
        
        self.label_title = tk.Label(self.header, text="DESTINATION SELECTOR", 
                              font=self.font_title, bg=self.bg_color, fg=self.accent_main,
                              cursor="arrow") # Standard cursor for text
        self.label_title.pack(side="left")

        # Edit Toggle Button
        self.btn_edit_toggle = tk.Button(self.header, text="EDIT: OFF", command=self.toggle_edit_mode,
                                       font=self.font_small, bg="#1a1a1a", fg="#666666",
                                       activebackground=self.accent_edit, activeforeground="black",
                                       relief="flat", bd=0, padx=10,
                                       cursor="hand2") # Hand cursor for button
        self.btn_edit_toggle.pack(side="right")
        
        self.header.bind("<ButtonPress-1>", self.start_move)
        self.header.bind("<B1-Motion>", self.do_move)

        # Folder List Container (Grid-like with rows of 5)
        self.list_container = tk.Frame(self.container, bg=self.bg_color)
        self.list_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.render_folders()

        # Footer
        self.footer = tk.Frame(self.container, bg=self.bg_color)
        self.footer.pack(fill="x", pady=(0, 10))
        
        self.btn_close = tk.Button(self.footer, text="EXIT [ESC]", command=self.root.destroy,
                                 font=self.font_small, bg=self.bg_color, fg="#555555",
                                 activebackground="#ff0000", activeforeground="white",
                                 relief="flat", bd=0, padx=20)
        self.btn_close.pack()

        # Update initial size
        self.update_window_size()
        
        # Focus
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.root.after(100, self.force_focus)

    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode
        color = self.accent_edit if self.edit_mode else "#666666"
        text = "EDIT: ON" if self.edit_mode else "EDIT: OFF"
        self.btn_edit_toggle.config(fg=color, text=text)
        self.render_folders()

    def update_window_size(self):
        self.list_container.update_idletasks()
        # Increased width to 740 to ensure 5 columns + container padding fit perfectly
        width = 740 
        total_items = 1 + len(self.folders) + 1
        rows = (total_items + 4) // 5
        height = 100 + (rows * 105)
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - width/2)
        center_y = int(screen_height/2 - height/2)
        self.root.geometry(f'{width}x{height}+{center_x}+{center_y}')

    def render_folders(self):
        for widget in self.list_container.winfo_children():
            widget.destroy()

        all_items = []
        all_items.append(('CLIPBOARD', "#00d4ff", True, -1))
        for i, f_data in enumerate(self.folders):
            all_items.append((f_data['path'], f_data['color'], False, i))

        for idx, (path, color, is_clip, f_idx) in enumerate(all_items):
            row = idx // 5
            col = idx % 5
            self.create_folder_card(path, color, row, col, f_idx, is_clip)

        next_idx = len(all_items)
        self.create_add_button(next_idx // 5, next_idx % 5)

    def create_folder_card(self, path, color, row, col, index, is_clipboard):
        # Card size: 128x85
        card = tk.Frame(self.list_container, bg="#1a1a1a", width=128, height=85)
        card.grid(row=row, column=col, padx=6, pady=6)
        card.pack_propagate(False)

        name = "CLIPBOARD" if is_clipboard else os.path.basename(path)
        if not name: name = path
        
        icon_char = "📋" if is_clipboard else "\ueaf7"
        icon_label = tk.Label(card, text=icon_char, font=self.font_icon, bg="#1a1a1a", fg=color)
        icon_label.pack(pady=(8, 0))

        name_label = tk.Label(card, text=name.upper()[:12], font=self.font_main, bg="#1a1a1a", fg=self.fg_color)
        name_label.pack()

        if self.edit_mode and not is_clipboard:
            card.config(highlightbackground=self.accent_edit, highlightthickness=1)
            # Safe positioning within 128x85
            del_label = tk.Label(card, text="✕", font=self.font_main, bg="#1a1a1a", fg="#ff4444", cursor="hand2")
            del_label.place(x=105, y=55)
            del_label.bind("<Button-1>", lambda e, i=index: self.remove_folder(i))
            
            col_label = tk.Label(card, text="🎨", font=self.font_main, bg="#1a1a1a", fg=self.accent_edit, cursor="hand2")
            col_label.place(x=5, y=55)
            col_label.bind("<Button-1>", lambda e, i=index: self.change_folder_color(i))

        widgets = [card, icon_label, name_label]
        for w in widgets:
            if not self.edit_mode:
                if is_clipboard:
                    w.bind("<Button-1>", lambda e: self.set_choice("CLIPBOARD"))
                else:
                    w.bind("<Button-1>", lambda e, p=path: self.set_choice(p))
                    w.bind("<Button-3>", lambda e, p=path: self.open_explorer(p))
                w.config(cursor="hand2")
            
            w.bind("<Enter>", lambda e, c=card, col=color: self.on_hover(c, col))
            w.bind("<Leave>", lambda e, c=card: self.on_leave(c))

    def create_add_button(self, row, col):
        # SYNCED SIZE: Must be 128x85 exactly like other cards
        card = tk.Frame(self.list_container, bg="#121212", width=128, height=85)
        card.grid(row=row, column=col, padx=6, pady=6)
        card.pack_propagate(False)

        icon_label = tk.Label(card, text="+", font=("JetBrains Mono", 24), bg="#121212", fg="#444444")
        icon_label.pack(expand=True)

        for w in [card, icon_label]:
            w.bind("<Button-1>", lambda e: self.add_new_folder())
            w.bind("<Enter>", lambda e, c=card: c.config(bg="#1a1a1a"))
            w.bind("<Leave>", lambda e, c=card: c.config(bg="#121212"))
            w.config(cursor="hand2")

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

    def open_explorer(self, path):
        if os.path.exists(path):
            subprocess.run(["explorer", os.path.normpath(path)])

    def change_folder_color(self, index):
        color = colorchooser.askcolor(title="Choose Folder Color", initialcolor=self.folders[index]['color'])[1]
        if color:
            self.folders[index]['color'] = color
            save_folders(self.folders)
            self.render_folders()

    def remove_folder(self, index):
        if messagebox.askyesno("Confirm", "Remove this folder from list?"):
            self.folders.pop(index)
            save_folders(self.folders)
            self.render_folders()
            self.update_window_size()

    def add_new_folder(self):
        path = filedialog.askdirectory(title="Select Folder to Add")
        if path:
            color = colorchooser.askcolor(title="Choose Folder Color", initialcolor="#00ff41")[1]
            if not color: color = "#00ff41"
            self.folders.append({"path": path, "color": color})
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

    def set_choice(self, folder):
        self.choice = folder
        self.root.destroy()

    def get_choice(self):
        self.root.mainloop()
        return self.choice

def send_to_clipboard(img):
    try:
        import win32clipboard
        output = io.BytesIO()
        img.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]
        output.close()
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()
        return True
    except Exception as e:
        print(f"Clipboard error: {e}")
        return False

def main():
    try:
        folders = load_folders()
        selector = RegionSelector()
        selection = selector.get_selection()
        if not selection: return

        import time
        time.sleep(0.1)
        img = ImageGrab.grab(bbox=selection, all_screens=True)

        chooser = FolderChooser(folders, img)
        folder = chooser.get_choice()
        if not folder: return

        if folder == "CLIPBOARD":
            send_to_clipboard(img)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = os.path.join(folder, filename)
            if not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)
            img.save(filepath)
            
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        temp_root = tk.Tk()
        temp_root.withdraw()
        messagebox.showerror("Script Error", f"{error_msg}")
        temp_root.destroy()

if __name__ == "__main__":
    main()
