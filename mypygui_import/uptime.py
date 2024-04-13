import tkinter as tk
import psutil
import threading
import time
from tkinter import *

class TimeOnWidget(tk.Frame):
    def __init__(self, parent, update_interval=1000):
        super().__init__(parent, bg="red", bd=0, highlightthickness=0)

        self.label = tk.Label(self, text="", bg="red", fg="blue", font=("JETBRAINSMONO NF", 10, "bold"))
        self.label.pack(fill="both", expand=True)

        self.update_interval = update_interval
        self._update_label()

    def _update_label(self):
        uptime_seconds = int(time.time() - psutil.boot_time())
        uptime_hours = uptime_seconds // 3600
        uptime_minutes = (uptime_seconds % 3600) // 60
        uptime_formatted = f"Uptime: {uptime_hours:02d}h {uptime_minutes:02d}m"
        self.label.config(text=uptime_formatted)

        self.after(self.update_interval, self._update_label)

root = tk.Tk()
root.title("PC Uptime")
root.configure(bg="red")
root.overrideredirect(True)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x = screen_width - 250
y = screen_height - 78
root.geometry(f"250x30+{x}+{y}")

widget = TimeOnWidget(root)
widget.pack(fill="both", expand=True)

root.mainloop()
