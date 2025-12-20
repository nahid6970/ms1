import tkinter as tk
from tkinter import messagebox
from PIL import ImageGrab
import os
from datetime import datetime

# Predefined folders
FOLDERS = [
    r"C:\Users\nahid\ms\ms1\Testing",
    r"C:\Users\nahid\ms\ms1\tailscale",
    r"C:\Users\nahid\Pictures"
]

class RegionSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes('-alpha', 0.3)
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.config(cursor="cross")

        self.canvas = tk.Canvas(self.root, cursor="cross", bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.start_x = None
        self.start_y = None
        self.rect = None
        self.selection = None
        
        # Crosshair lines
        self.v_line = self.canvas.create_line(0, 0, 0, 0, fill="white", dash=(4, 4))
        self.h_line = self.canvas.create_line(0, 0, 0, 0, fill="white", dash=(4, 4))

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.root.bind("<Escape>", lambda e: self.root.destroy())

    def on_mouse_move(self, event):
        # Update crosshair
        w, h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.canvas.coords(self.v_line, event.x, 0, event.x, h)
        self.canvas.coords(self.h_line, 0, event.y, w, event.y)

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        # Create a modern looking rectangle (white/blue dashed like ShareX)
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, 
            outline='#00bfff', width=1, dash=(2, 2)
        )

    def on_move_press(self, event):
        cur_x, cur_y = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)
        # Keep crosshair updated during drag
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
    def __init__(self, folders):
        self.root = tk.Tk()
        self.root.overrideredirect(True) # No window border
        self.root.attributes('-topmost', True)
        self.choice = None

        # Colors & Theme
        self.bg_color = "#1a1a1a"
        self.fg_color = "#ffffff"
        self.accent_green = "#00ff41" # Matrix/Cyberpunk Green
        
        self.root.config(bg=self.accent_green) # This will be our border

        # Main Container (Interior)
        self.container = tk.Frame(self.root, bg=self.bg_color, padx=2, pady=2)
        self.container.pack(fill="both", expand=True, padx=2, pady=2) # The padding reveals the green bg as border

        # Center the window
        window_width = 450
        window_height = 350
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

        # Header / Drag Area
        self.header = tk.Frame(self.container, bg=self.bg_color, cursor="fleur")
        self.header.pack(fill="x", pady=(10, 20))
        
        title_label = tk.Label(self.header, text="SAVE SCREENSHOT", 
                              font=("Segoe UI Bold", 14), bg=self.bg_color, fg=self.accent_green)
        title_label.pack()
        
        # Make window draggable
        self.header.bind("<ButtonPress-1>", self.start_move)
        self.header.bind("<B1-Motion>", self.do_move)
        title_label.bind("<ButtonPress-1>", self.start_move)
        title_label.bind("<B1-Motion>", self.do_move)

        # Folder Buttons
        self.btn_frame = tk.Frame(self.container, bg=self.bg_color)
        self.btn_frame.pack(fill="both", expand=True, padx=30)

        for folder in folders:
            btn_text = os.path.basename(folder).upper() if os.path.basename(folder) else folder
            btn = tk.Button(self.btn_frame, text=btn_text, 
                           command=lambda f=folder: self.set_choice(f), 
                           font=("Segoe UI", 11),
                           bg="#2d2d2d", fg=self.fg_color,
                           activebackground=self.accent_green, activeforeground="black",
                           relief="flat", cursor="hand2", bd=0, height=2)
            btn.pack(pady=8, fill="x")
            
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg="#3d3d3d", fg=self.accent_green))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg="#2d2d2d", fg=self.fg_color))

        # Cancel Button
        cancel_btn = tk.Button(self.container, text="EXIT", command=self.root.destroy, 
                              font=("Segoe UI", 10), bg="#401010", fg="#ff5555",
                              activebackground="#ff5555", activeforeground="white",
                              relief="flat", cursor="hand2", bd=0)
        cancel_btn.pack(pady=(20, 15), padx=100, fill="x")

        self.root.bind("<Escape>", lambda e: self.root.destroy())

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

def main():
    # 1. Select Region
    selector = RegionSelector()
    selection = selector.get_selection()

    if not selection:
        return

    # 2. Capture Screenshot
    img = ImageGrab.grab(bbox=selection, all_screens=True)

    # 3. Choose Folder
    chooser = FolderChooser(FOLDERS)
    folder = chooser.get_choice()

    if not folder:
        return

    # 4. Save Image
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{timestamp}.png"
    filepath = os.path.join(folder, filename)

    try:
        if not os.path.exists(folder):
            os.makedirs(folder)
        img.save(filepath)
    except Exception as e:
        messagebox.showerror("Error", f"Could not save file:\n{e}")

if __name__ == "__main__":
    main()
