import tkinter as tk
from tkinter import messagebox
from PIL import ImageGrab
import os
from datetime import datetime
import sys

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

        self.canvas = tk.Canvas(self.root, cursor="cross", bg="grey")
        self.canvas.pack(fill="both", expand=True)

        self.start_x = None
        self.start_y = None
        self.rect = None
        self.selection = None

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.root.bind("<Escape>", lambda e: self.root.destroy())

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, 1, 1, outline='red', width=2)

    def on_move_press(self, event):
        cur_x, cur_y = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        end_x, end_y = (event.x, event.y)
        x1 = min(self.start_x, end_x)
        y1 = min(self.start_y, end_y)
        x2 = max(self.start_x, end_x)
        y2 = max(self.start_y, end_y)
        
        if x2 - x1 > 5 and y2 - y1 > 5:
            self.selection = (x1, y1, x2, y2)
        
        self.root.destroy()

    def get_selection(self):
        self.root.mainloop()
        return self.selection

class FolderChooser:
    def __init__(self, folders):
        self.root = tk.Tk()
        self.root.title("Save Screenshot To...")
        self.root.attributes('-topmost', True)
        self.choice = None

        # Center the window
        window_width = 400
        window_height = 250
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

        label = tk.Label(self.root, text="Select destination folder:", font=("Arial", 12), pady=10)
        label.pack()

        for folder in folders:
            # We don't check existence here so the user sees all options 
            # or we can check and grey them out/hide them. 
            # Let's show all but check on save.
            btn_text = os.path.basename(folder) if os.path.basename(folder) else folder
            btn = tk.Button(self.root, text=btn_text, 
                           command=lambda f=folder: self.set_choice(f), 
                           width=40, height=2, font=("Segoe UI", 10),
                           bg="#e1e1e1", activebackground="#0078d7", activeforeground="white",
                           relief="flat", cursor="hand2")
            btn.pack(pady=5, padx=20)
            
            # Simple hover effect
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg="#d1d1d1"))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg="#e1e1e1"))

        cancel_btn = tk.Button(self.root, text="Cancel", command=self.root.destroy, 
                              width=20, pady=5, bg="#ffcccc")
        cancel_btn.pack(pady=10)

        self.root.bind("<Escape>", lambda e: self.root.destroy())

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
        print("Selection cancelled.")
        return

    # 2. Capture Screenshot (Hide selector window first is handled by .destroy())
    # Wait a tiny bit for window to fully vanish if needed, though destroy() is usually enough
    img = ImageGrab.grab(bbox=selection, all_screens=True)

    # 3. Choose Folder
    chooser = FolderChooser(FOLDERS)
    folder = chooser.get_choice()

    if not folder:
        print("Save cancelled.")
        return

    # 4. Save Image
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{timestamp}.png"
    filepath = os.path.join(folder, filename)

    try:
        img.save(filepath)
        print(f"Saved to: {filepath}")
    except Exception as e:
        print(f"Error saving file: {e}")
        tk.messagebox.showerror("Error", f"Could not save file:\n{e}")

if __name__ == "__main__":
    main()
