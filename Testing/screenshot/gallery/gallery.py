import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import os
import json
import subprocess

# Config file path
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "gallery_config.json")

def load_images():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
    return []

def save_images(images):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(images, f, indent=4)
    except Exception as e:
        messagebox.showerror("Error", f"Could not save config: {e}")

class ImageGallery:
    def __init__(self, image_paths):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.image_paths = [p for p in image_paths if os.path.exists(p)]
        self.current_idx = 0 if self.image_paths else -1
        self.is_dialog_open = False
        
        # Cache for images to prevent lagginess
        self.photo_cache = {}
        
        # Colors & Theme
        self.bg_color = "#000000"
        self.accent_color = "#00ffff"
        
        # Fonts
        self.font_name = "JetBrains Mono"
        self.font_icons = (self.font_name, 32)
        self.font_small = (self.font_name, 9)

        self.root.config(bg=self.bg_color)
        
        # Dimensions
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        
        # Reduced size
        self.bar_h = int(sh * 0.35) 
        self.win_w = int(sw * 0.9) # 90% width
        self.card_w = int(self.bar_h * 0.55) 
        self.card_h = int(self.bar_h * 0.8)
        
        # Center the window
        self.root.geometry(f"{self.win_w}x{self.bar_h}+{int((sw-self.win_w)/2)}+{int((sh-self.bar_h)/2)}")

        # Main Container
        self.container = tk.Frame(self.root, bg=self.bg_color)
        self.container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.container, bg=self.bg_color, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=40)
        
        self.inner_frame = tk.Frame(self.canvas, bg=self.bg_color)
        self.inner_id = self.canvas.create_window((self.win_w/2, self.bar_h/2), window=self.inner_frame, anchor="center")

        # Bindings
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        self.root.bind("<Left>", lambda e: self.prev_image())
        self.root.bind("<Right>", lambda e: self.next_image())
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.root.bind("<FocusOut>", self.on_focus_out)
        
        self.render_cards()
        self.root.after(100, self.force_focus)

    def get_cached_image(self, path):
        if path in self.photo_cache:
            return self.photo_cache[path]
        
        try:
            img = Image.open(path)
            # Center crop logic
            t_w, t_h = self.card_w, self.card_h
            img_ratio = img.width / img.height
            target_ratio = t_w / t_h
            
            if img_ratio > target_ratio:
                new_h = t_h
                new_w = int(new_h * img_ratio)
                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                left = (new_w - t_w) / 2
                img = img.crop((left, 0, left + t_w, t_h))
            else:
                new_w = t_w
                new_h = int(new_w / img_ratio)
                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                top = (new_h - t_h) / 2
                img = img.crop((0, top, t_w, top + t_h))

            tk_img = ImageTk.PhotoImage(img)
            self.photo_cache[path] = tk_img
            return tk_img
        except:
            return None

    def render_cards(self):
        # We only destroy if the number of items changed
        # For performance, we'll keep it simple but optimized with caching
        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        # Add Card
        self.create_add_card()

        # Image Cards
        for i, path in enumerate(self.image_paths):
            self.create_image_card(path, i)

        self.inner_frame.update_idletasks()
        
        # Center or Anchor
        frame_w = self.inner_frame.winfo_reqwidth()
        canvas_w = self.canvas.winfo_width() if self.canvas.winfo_width() > 1 else self.win_w - 80

        if frame_w < canvas_w:
            self.canvas.coords(self.inner_id, canvas_w/2, self.bar_h/2)
            self.canvas.itemconfigure(self.inner_id, anchor="center")
        else:
            self.canvas.coords(self.inner_id, 0, self.bar_h/2)
            self.canvas.itemconfigure(self.inner_id, anchor="w")

        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.scroll_to_active()

    def create_add_card(self):
        f = tk.Frame(self.inner_frame, bg="#111111", width=self.card_w, height=self.card_h)
        f.pack(side="left", padx=12)
        f.pack_propagate(False)
        
        # Vertical stacking for better look
        center = tk.Frame(f, bg="#111111")
        center.pack(expand=True)
        
        tk.Label(center, text="+", font=self.font_icons, bg="#111111", fg=self.accent_color).pack()
        tk.Label(center, text="ADD IMAGE", font=self.font_small, bg="#111111", fg="#444444").pack()
        
        for w in [f, center] + list(center.winfo_children()):
            w.bind("<Button-1>", lambda e: self.add_image())
            w.config(cursor="hand2")

    def create_image_card(self, path, idx):
        is_active = (idx == self.current_idx)
        bd = 2 if is_active else 0
        
        f = tk.Frame(self.inner_frame, bg=self.accent_color if is_active else self.bg_color,
                     width=self.card_w + (bd*2), height=self.card_h + (bd*2))
        f.pack(side="left", padx=12)
        f.pack_propagate(False)

        tk_img = self.get_cached_image(path)
        if tk_img:
            lb = tk.Label(f, image=tk_img, bg=self.bg_color)
            lb.pack(fill="both", expand=True, padx=bd, pady=bd)
            
            # Optimization: only change border on selection
            lb.bind("<Button-1>", lambda e, i=idx: self.select_idx(i))
            lb.bind("<Double-Button-1>", lambda e, p=path: self.open_in_chrome(p))
            lb.config(cursor="hand2")
        else:
            tk.Label(f, text="ERR", fg="red", bg="black").pack(expand=True)

    def select_idx(self, idx):
        if self.current_idx == idx: return
        self.current_idx = idx
        self.render_cards()

    def next_image(self):
        if not self.image_paths: return
        self.current_idx = (self.current_idx + 1) % len(self.image_paths)
        self.render_cards()

    def prev_image(self):
        if not self.image_paths: return
        self.current_idx = (self.current_idx - 1) % len(self.image_paths)
        self.render_cards()

    def scroll_to_active(self):
        self.root.update_idletasks()
        total_w = self.inner_frame.winfo_width()
        canvas_w = self.canvas.winfo_width()
        if total_w <= canvas_w: return
        
        # Calculate card center position
        # (+1 for add button)
        card_x = (self.current_idx + 1) * (self.card_w + 24) + (self.card_w / 2)
        fraction = (card_x - (canvas_w / 2)) / total_w
        self.canvas.xview_moveto(max(0, min(1, fraction)))

    def on_mousewheel(self, event):
        self.canvas.xview_scroll(int(-1*(event.delta/120)), "units")

    def add_image(self):
        self.is_dialog_open = True
        paths = filedialog.askopenfilenames(parent=self.root)
        self.is_dialog_open = False
        self.root.focus_force()
        if paths:
            new_paths = [p for p in paths if p not in self.image_paths]
            self.image_paths.extend(new_paths)
            save_images(self.image_paths)
            if self.current_idx == -1: self.current_idx = 0
            self.render_cards()

    def open_in_chrome(self, path):
        subprocess.run(f'start chrome "{path}"', shell=True)
        self.root.destroy()

    def on_focus_out(self, event):
        if self.is_dialog_open: return
        if self.root.focus_displayof() is None:
            self.root.destroy()

    def force_focus(self):
        self.root.focus_force()
        self.root.lift()
        self.root.focus_set()
        try: self.root.grab_set()
        except: pass

if __name__ == "__main__":
    imgs = load_images()
    gallery = ImageGallery(imgs)
    gallery.root.mainloop()
