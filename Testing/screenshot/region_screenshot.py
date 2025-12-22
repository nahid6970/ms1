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
        
        # Fonts - Force JetBrains Mono everywhere
        self.font_name = "JetBrainsMono NFP"
        self.font_main = (self.font_name, 10)
        self.font_icon = (self.font_name, 36) # Increased size further
        self.font_small = (self.font_name, 8)
        self.font_title = (self.font_name + " Bold", 11)
        
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
                                 relief="flat", bd=0, padx=20, cursor="hand2")
        self.btn_close.pack()

        # Update initial size
        self.update_window_size()
        
        # Focus
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
        # Increased dimensions for 36pt icons
        width = 820 
        total_items = 1 + len(self.folders) + 1
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

        all_items = []
        # (path/label, color, icon, card_type, index)
        all_items.append(('CLIPBOARD', "#00d4ff", "📋", "CLIPBOARD", -1))
        all_items.append(('CHROME', "#ff9900", "🌏", "BROWSER", -2))
        
        for i, f_data in enumerate(self.folders):
            icon = f_data.get('icon', "\ueaf7")
            all_items.append((f_data['path'], f_data['color'], icon, "FOLDER", i))

        for idx, (path, color, icon, card_type, f_idx) in enumerate(all_items):
            row = idx // 5
            col = idx % 5
            self.create_folder_card(path, color, icon, row, col, f_idx, card_type)

        next_idx = len(all_items)
        self.create_add_button(next_idx // 5, next_idx % 5)

    def create_folder_card(self, path, color, icon, row, col, index, card_type):
        # Increased card size for 36pt icons
        card = tk.Frame(self.list_container, bg="#1a1a1a", width=150, height=120)
        card.grid(row=row, column=col, padx=5, pady=5)
        card.pack_propagate(False)

        name = path # Default to content of path argument
        if card_type == "FOLDER":
            name = os.path.basename(path)
            if not name: name = path
        
        icon_label = tk.Label(card, text=icon, font=self.font_icon, bg="#1a1a1a", fg=color)
        icon_label.pack(pady=(5, 0))

        name_label = tk.Label(card, text=name.upper()[:16], font=self.font_main, bg="#1a1a1a", fg=self.fg_color)
        name_label.pack()

        if self.edit_mode and card_type == "FOLDER":
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
                if card_type == "CLIPBOARD":
                    w.bind("<Button-1>", lambda e: self.set_choice("CLIPBOARD"))
                elif card_type == "BROWSER":
                    w.bind("<Button-1>", lambda e: self.open_in_browser())
                else: # FOLDER
                    w.bind("<Button-1>", lambda e, p=path: self.set_choice(p))
                    w.bind("<Button-3>", lambda e, p=path: self.open_explorer(p))
                w.config(cursor="hand2")
            
            w.bind("<Enter>", lambda e, c=card, col=color: self.on_hover(c, col))
            w.bind("<Leave>", lambda e, c=card: self.on_leave(c))

    def open_in_browser(self):
        import tempfile
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_dir = tempfile.gettempdir()
            filename = f"screenshot_{timestamp}.png"
            filepath = os.path.join(temp_dir, filename)
            
            self.img.save(filepath)
            
            # Open in Chrome (Windows)
            subprocess.run(f'start chrome "{filepath}"', shell=True)
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open browser: {e}")

    def create_add_button(self, row, col):
        # SYNCED SIZE: Must be 128x85 exactly like other cards
        card = tk.Frame(self.list_container, bg="#121212", width=150, height=120)
        card.grid(row=row, column=col, padx=5, pady=5)
        card.pack_propagate(False)

        icon_label = tk.Label(card, text="+", font=(self.font_name, 36), bg="#121212", fg="#444444")
        icon_label.pack(expand=True)

        # Bind explicitly to ensure click works
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
        self.is_dialog_open = True
        color = colorchooser.askcolor(title="Choose Folder Color", initialcolor=self.folders[index]['color'], parent=self.root)[1]
        self.is_dialog_open = False
        self.root.focus_force()
        if color:
            self.folders[index]['color'] = color
            save_folders(self.folders)
            self.render_folders()

    def change_folder_icon(self, index):
        from tkinter import simpledialog
        self.is_dialog_open = True
        # Added parent=self.root to ensure it doesn't get buried
        new_icon = simpledialog.askstring("Folder Icon", "Paste new icon glyph:", 
                                         initialvalue=self.folders[index].get('icon', "\ueaf7"),
                                         parent=self.root)
        self.is_dialog_open = False
        self.root.focus_force()
        if new_icon:
            self.folders[index]['icon'] = new_icon
            save_folders(self.folders)
            self.render_folders()

    def remove_folder(self, index):
        self.is_dialog_open = True
        confirm = messagebox.askyesno("Confirm", "Remove this folder from list?", parent=self.root)
        self.is_dialog_open = False
        self.root.focus_force()
        if confirm:
            self.folders.pop(index)
            save_folders(self.folders)
            self.render_folders()
            self.update_window_size()

    def add_new_folder(self):
        self.is_dialog_open = True
        path = filedialog.askdirectory(title="Select Folder to Add", parent=self.root)
        self.is_dialog_open = False
        self.root.focus_force()
        if path:
            self.is_dialog_open = True
            color = colorchooser.askcolor(title="Choose Folder Color", initialcolor="#00ff41", parent=self.root)[1]
            self.is_dialog_open = False
            self.root.focus_force()
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
