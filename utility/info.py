import tkinter as tk
import win32gui
import win32process
import psutil
import textwrap
import pyperclip

ROOT = tk.Tk()
ROOT.title("Python GUI")
ROOT.configure(bg="#83a598")
ROOT.overrideredirect(True)  # Remove default borders
ROOT.attributes('-topmost', True)  # Set always on top

def check_window_topmost():
    if not ROOT.attributes('-topmost'):
        ROOT.attributes('-topmost', True)
    ROOT.after(500, check_window_topmost)
# Call the function to check window topmost status periodically
check_window_topmost()

class ActiveWindowInfo(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.info_type = 0  # 0 for process name, 1 for title/class name
        self.label = tk.Label(self, text="", pady=1 ,bg="#83a598", fg="#000000", font=("JETBRAINSMONO NF", 10), justify="left", wraplength=1000)
        self.label.pack(pady=(0,0))
        self.label.bind("<Button-1>", self.toggle_info)
        self.label.bind("<Button-3>", self.copy_to_clipboard)
        self.update_info()

        # Center the window on the screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = 0
        y = screen_height -75
        master.geometry(f"+{x}+{y}")

    def update_info(self):
        # Get the position of the mouse cursor
        pos = win32gui.GetCursorPos()

        # Get the handle of the window under the cursor
        hwnd = win32gui.WindowFromPoint(pos)

        # Get the active window information
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        if self.info_type == 0:  # Process name
            try:
                process_name = psutil.Process(pid).name()
                self.label.config(text=f"\udb85\udcfb {process_name}")
            except psutil.NoSuchProcess:
                self.label.config(text="No active window found")
        elif self.info_type == 1:  # Title/class name
            class_name = win32gui.GetClassName(hwnd)
            window_text = win32gui.GetWindowText(hwnd)
            # Truncate text if it exceeds 20 characters
            window_text = textwrap.shorten(window_text, width=100, placeholder="...")
            class_name = textwrap.shorten(class_name, width=100, placeholder="...")
            self.label.config(text=f"\udb86\ude07 {window_text}   \udb86\ude07 {class_name}")
        self.after(250, self.update_info)  # Update every 250 milliseconds

    def toggle_info(self, event=None):
        self.info_type = (self.info_type + 1) % 2  # Toggle between 0 and 1
        if self.info_type == 0:
            self.label.config(text="Active Window Process Name: ")
        else:
            self.label.config(text="Active Window Title: \nClass Name: ")

    def copy_to_clipboard(self, event=None):
        text = self.label.cget("text")
        pyperclip.copy(text)

if __name__ == "__main__":
    app = ActiveWindowInfo(master=ROOT)
    app.mainloop()
