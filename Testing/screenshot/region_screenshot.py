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
                # Migration if it's just a list of strings
                if data and isinstance(data[0], str):
                    return [{"path": p, "color": "#00ff41"} for p in data]
                return data
    except Exception as e:
        print(f"Error loading config: {e}")
    
    return [
        {"path": r"C:\Users\nahid\ms\ms1\Testing", "color": "#00ff41"},
        {"path": r"C:\Users\nahid\ms\ms1\tailscale", "color": "#00d4ff"},
        {"path": r"C:\Users\nahid\Pictures", "color": "#ff007f"}
    ]

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

        # Colors & Theme
        self.bg_color = "#0e0e0e"
        self.fg_color = "#ffffff"
        self.accent_main = "#00ff41" # Matrix Green
        
        # Font setup (JetBrains Mono if available)
        self.font_main = ("JetBrains Mono", 10)
        self.font_icon = ("JetBrains Mono", 18)
        self.font_title = ("JetBrains Mono Bold", 11)
        
        self.root.config(bg="#1a1a1a")

        # Main Container
        self.container = tk.Frame(self.root, bg=self.bg_color)
        self.container.pack(fill="both", expand=True, padx=2, pady=2)

        # Header (Horizontal title and controls)
        self.header = tk.Frame(self.container, bg=self.bg_color, cursor="fleur")
        self.header.pack(fill="x", padx=15, pady=(10, 0))
        
        self.label_title = tk.Label(self.header, text="DESTINATION SELECTOR", 
                              font=self.font_title, bg=self.bg_color, fg=self.accent_main)
        self.label_title.pack(side="left")

        # Exit Button in title
        self.btn_exit = tk.Button(self.header, text="✕", command=self.root.destroy,
                                font=self.font_title, bg=self.bg_color, fg="#555555",
                                activebackground="#ff0000", activeforeground="white",
                                relief="flat", bd=0, padx=5)
        self.btn_exit.pack(side="right")
        
        self.header.bind("<ButtonPress-1>", self.start_move)
        self.header.bind("<B1-Motion>", self.do_move)

        # Folder List Container (Horizontal)
        self.scroll_canvas = tk.Canvas(self.container, bg=self.bg_color, highlightthickness=0, height=140)
        self.scroll_canvas.pack(fill="x", padx=10, pady=10)
        
        self.folder_frame = tk.Frame(self.scroll_canvas, bg=self.bg_color)
        self.scroll_canvas.create_window((0, 0), window=self.folder_frame, anchor="nw")
        
        self.render_folders()

        # Update window size based on folders
        self.root.after(10, self.update_window_size)
        
        # Focus
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.root.after(100, self.force_focus)

    def update_window_size(self):
        self.folder_frame.update_idletasks()
        width = min(max(400, self.folder_frame.winfo_width() + 40), 1200)
        height = 200
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - width/2)
        center_y = int(screen_height/2 - height/2)
        self.root.geometry(f'{width}x{height}+{center_x}+{center_y}')

    def render_folders(self):
        # Clear existing
        for widget in self.folder_frame.winfo_children():
            widget.destroy()

        # Clipboard Special
        self.create_folder_card("CLIPBOARD", "#00d4ff", is_clipboard=True)

        for i, f_data in enumerate(self.folders):
            self.create_folder_card(f_data['path'], f_data['color'], index=i)

        # Add Folder Button
        self.create_add_button()

    def create_folder_card(self, path, color, index=None, is_clipboard=False):
        card = tk.Frame(self.folder_frame, bg="#1a1a1a", padx=10, pady=10, width=120, height=110)
        card.pack(side="left", padx=5)
        card.pack_propagate(False)

        name = "CLIPBOARD" if is_clipboard else os.path.basename(path)
        if not name: name = path

        # Icon Label (\ueaf7 is the folder icon usually in Nerd Fonts)
        icon_char = "\ueaf7" if not is_clipboard else "📋"
        icon_label = tk.Label(card, text=icon_char, font=self.font_icon, bg="#1a1a1a", fg=color)
        icon_label.pack(pady=(5, 2))

        name_label = tk.Label(card, text=name.upper()[:12], font=self.font_main, bg="#1a1a1a", fg=self.fg_color)
        name_label.pack()

        # Hover and Click bindings
        for widget in [card, icon_label, name_label]:
            if is_clipboard:
                widget.bind("<Button-1>", lambda e: self.set_choice("CLIPBOARD"))
            else:
                # Primary Actions
                widget.bind("<Button-1>", lambda e, p=path: self.set_choice(p))
                widget.bind("<Button-3>", lambda e, p=path: self.open_explorer(p))
                
                # Management Actions (Middle Click OR Shift+Right Click)
                widget.bind("<Button-2>", lambda e, i=index: self.show_card_menu(e, i))
                widget.bind("<Shift-Button-3>", lambda e, i=index: self.show_card_menu(e, i))
            
            widget.bind("<Enter>", lambda e, c=card, col=color: self.on_hover(c, col))
            widget.bind("<Leave>", lambda e, c=card: self.on_leave(c))
            widget.config(cursor="hand2")

    def create_add_button(self):
        card = tk.Frame(self.folder_frame, bg="#121212", padx=10, pady=10, width=80, height=110)
        card.pack(side="left", padx=5)
        card.pack_propagate(False)

        icon_label = tk.Label(card, text="+", font=("JetBrains Mono", 24), bg="#121212", fg="#444444")
        icon_label.pack(expand=True)

        for widget in [card, icon_label]:
            widget.bind("<Button-1>", lambda e: self.add_new_folder())
            widget.bind("<Enter>", lambda e, c=card: c.config(bg="#1a1a1a"))
            widget.bind("<Leave>", lambda e, c=card: c.config(bg="#121212"))
            widget.config(cursor="hand2")

    def on_hover(self, card, color):
        card.config(bg="#252525")
        for w in card.winfo_children():
            w.config(bg="#252525")

    def on_leave(self, card):
        card.config(bg="#1a1a1a")
        for w in card.winfo_children():
            w.config(bg="#1a1a1a")

    def open_explorer(self, path):
        if os.path.exists(path):
            subprocess.run(["explorer", path])
        else:
            messagebox.showwarning("Error", f"Folder does not exist: {path}")

    def show_card_menu(self, event, index):
        menu = tk.Menu(self.root, tearoff=0, bg="#1a1a1a", fg="white", activebackground=self.accent_main)
        menu.add_command(label="Change Color", command=lambda: self.change_folder_color(index))
        menu.add_command(label="Remove Folder", command=lambda: self.remove_folder(index))
        menu.post(event.x_root, event.y_root)

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
        
        # 1. Select Region
        selector = RegionSelector()
        selection = selector.get_selection()

        if not selection:
            return

        # 2. Capture Screenshot
        import time
        time.sleep(0.1)
        img = ImageGrab.grab(bbox=selection, all_screens=True)

        # 3. Choose Folder
        chooser = FolderChooser(folders, img)
        folder = chooser.get_choice()

        if not folder:
            return

        # 4. Handle Save or Clipboard
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
