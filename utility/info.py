import tkinter as tk
import win32gui
import win32process
import psutil
import textwrap
import pyperclip
import keyboard

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
        self.label_process = tk.Label(self, text="", pady=0 ,bg="#83a598", fg="#000000", font=("JETBRAINSMONO NFP", 11 ,"bold"), anchor="w",justify="left", wraplength=1000)
        self.label_process.grid(row=0, column=0, padx=5, pady=0, sticky='ew')
        
        self.label_class = tk.Label(self, text="", pady=0 ,bg="#83a598", fg="#000000", font=("JETBRAINSMONO NFP", 11 ,"bold"), anchor="w",justify="left", wraplength=1000)
        self.label_class.grid(row=1, column=0, padx=5, pady=0, sticky='ew')
        
        self.label_title = tk.Label(self, text="", pady=0 ,bg="#83a598", fg="#000000", font=("JETBRAINSMONO NFP", 11 ,"bold"), anchor="w",justify="left", wraplength=1000)
        self.label_title.grid(row=2, column=0, padx=5, pady=0, sticky='ew')
        
        self.update_info()

        # Center the window on the screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = 0
        y = 0
        master.geometry(f"+{x}+{y}")

        # Register global hotkeys
        keyboard.add_hotkey('ctrl+1', lambda: self.copy_to_clipboard(0))
        keyboard.add_hotkey('ctrl+2', lambda: self.copy_to_clipboard(1))
        keyboard.add_hotkey('ctrl+3', lambda: self.copy_to_clipboard(2))
        keyboard.add_hotkey('esc', self.exit_app)

    def update_info(self):
        # Get the position of the mouse cursor
        pos = win32gui.GetCursorPos()

        # Get the handle of the window under the cursor
        hwnd = win32gui.WindowFromPoint(pos)

        # Get the active window information
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        
        try:
            process_name = psutil.Process(pid).name()
            self.label_process.config(text=f"Process: {process_name}")
        except psutil.NoSuchProcess:
            self.label_process.config(text="No active window found")
        
        class_name = win32gui.GetClassName(hwnd)
        window_text = win32gui.GetWindowText(hwnd)
        # Truncate text if it exceeds 20 characters
        window_text = textwrap.shorten(window_text, width=100, placeholder="...")
        class_name = textwrap.shorten(class_name, width=100, placeholder="...")
        self.label_class.config(text=f"Class: {class_name}")
        self.label_title.config(text=f"Title: {window_text}")

        self.after(250, self.update_info)  # Update every 250 milliseconds

    def copy_to_clipboard(self, info_type):
        if info_type == 0:  # Process name
            text = self.label_process.cget("text").split(": ")[-1]
        elif info_type == 1:  # Class name
            text = self.label_class.cget("text").split(": ")[-1]
        elif info_type == 2:  # Window title
            text = self.label_title.cget("text").split(": ")[-1]
        pyperclip.copy(text)

    def exit_app(self):
        ROOT.quit()

if __name__ == "__main__":
    app = ActiveWindowInfo(master=ROOT)
    app.mainloop()
