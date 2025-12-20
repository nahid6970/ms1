import tkinter as tk
from tkinter import messagebox
from PIL import ImageGrab, Image
import os
import json
from datetime import datetime
import io

# Config file path
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "folders.json")

def load_folders():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
    
    # Defaults if file missing or corrupt
    return [
        r"C:\Users\nahid\ms\ms1\Testing",
        r"C:\Users\nahid\ms\ms1\tailscale",
        r"C:\Users\nahid\Pictures"
    ]

class RegionSelector:
    def __init__(self):
        self.root = tk.Tk()
        # Increased alpha for better contrast
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
        
        # Thicker, solid crosshairs for better visibility
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
        # Solid, thicker neon border for high visibility
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
    def __init__(self, folders):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.choice = None

        # Colors & Theme
        self.bg_color = "#121212"
        self.fg_color = "#e0e0e0"
        self.accent_green = "#00ff41" # Matrix Green
        self.btn_bg = "#1e1e1e"
        
        self.root.config(bg=self.accent_green)

        # Main Container
        self.container = tk.Frame(self.root, bg=self.bg_color)
        self.container.pack(fill="both", expand=True, padx=1, pady=1)

        # Calculate height based on number of folders
        folder_count = len(folders) + 1 # +1 for clipboard
        window_width = 400
        window_height = 160 + (folder_count * 55)
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

        # Header
        self.header = tk.Frame(self.container, bg=self.bg_color, cursor="fleur")
        self.header.pack(fill="x", pady=(15, 10))
        
        title_label = tk.Label(self.header, text="SELECT DESTINATION", 
                              font=("Segoe UI Bold", 12), bg=self.bg_color, fg=self.accent_green)
        title_label.pack()
        
        self.header.bind("<ButtonPress-1>", self.start_move)
        self.header.bind("<B1-Motion>", self.do_move)

        # Buttons Frame
        self.btn_frame = tk.Frame(self.container, bg=self.bg_color)
        self.btn_frame.pack(fill="both", expand=True, padx=40)

        # Special: Copy to Clipboard
        clip_btn = tk.Button(self.btn_frame, text="📋 COPY TO CLIPBOARD", 
                            command=lambda: self.set_choice("CLIPBOARD"), 
                            font=("Segoe UI Semibold", 10),
                            bg="#1a2a3a", fg="#00ccff",
                            activebackground="#00ccff", activeforeground="black",
                            relief="flat", cursor="hand2", bd=0, height=2)
        clip_btn.pack(pady=(0, 15), fill="x")
        clip_btn.bind("<Enter>", lambda e, b=clip_btn: b.configure(bg="#223a4a"))
        clip_btn.bind("<Leave>", lambda e, b=clip_btn: b.configure(bg="#1a2a3a"))

        # Folder Buttons
        for folder in folders:
            display_path = os.path.basename(folder) if os.path.basename(folder) else folder
            btn = tk.Button(self.btn_frame, text=f"📂 {display_path.upper()}", 
                           command=lambda f=folder: self.set_choice(f), 
                           font=("Segoe UI", 10),
                           bg=self.btn_bg, fg=self.fg_color,
                           activebackground=self.accent_green, activeforeground="black",
                           relief="flat", cursor="hand2", bd=0, height=2)
            btn.pack(pady=5, fill="x")
            
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg="#2d2d2d", fg=self.accent_green))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=self.btn_bg, fg=self.fg_color))

        # Exit Area
        exit_btn = tk.Button(self.container, text="CANCEL [ESC]", command=self.root.destroy, 
                            font=("Segoe UI", 8), bg=self.bg_color, fg="#666666",
                            activebackground="#441111", activeforeground="white",
                            relief="flat", cursor="hand2", bd=0)
        exit_btn.pack(side="bottom", pady=10)

        self.root.bind("<Escape>", lambda e: self.root.destroy())
        
        # Force focus so ESC works immediately without clicking
        self.root.after(100, self.force_focus)

    def force_focus(self):
        self.root.focus_force()
        self.root.lift()
        self.root.focus_set()
        # grab_set makes it modal and ensures it gets all events
        try:
            self.root.grab_set()
        except:
            pass

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
        # Using a slight delay to ensure the overlay is fully gone
        import time
        time.sleep(0.1)
        img = ImageGrab.grab(bbox=selection, all_screens=True)

        # 3. Choose Folder
        chooser = FolderChooser(folders)
        folder = chooser.get_choice()

        if not folder:
            return

        # 4. Handle Save or Clipboard
        if folder == "CLIPBOARD":
            success = send_to_clipboard(img)
            if not success:
                messagebox.showwarning("Clipboard", "Clipboard copy failed. Ensure 'pywin32' is installed correctly.")
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
        # Create a hidden root for the messagebox if everything else died
        temp_root = tk.Tk()
        temp_root.withdraw()
        messagebox.showerror("Script Error", f"The script crashed with the following error:\n\n{error_msg}")
        temp_root.destroy()

if __name__ == "__main__":
    main()
