import tkinter as tk
import psutil
import threading
import time

# Function to check if a process is running
def is_process_running(process_name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == process_name:
            return True
    return False

# Function to update label visibility
def update_labels():
    global last_statuses
    while True:
        statuses = {
            "notepad.exe": is_process_running("notepad.exe"),
            "whkd.exe": is_process_running("whkd.exe"),
            "chrome.exe": is_process_running("chrome.exe"),
            "Code.exe": is_process_running("Code.exe")
        }
        if statuses != last_statuses:
            root.after_idle(update_labels_gui, statuses)
            last_statuses = statuses
        time.sleep(1)  # Check every 1 second

# Function to update GUI labels
def update_labels_gui(statuses):
    notepad_label.config(text="Notepad" if statuses["notepad.exe"] else "")
    whkd_label.config(text="whkd" if statuses["whkd.exe"] else "")
    chrome_label.config(text="Chrome" if statuses["chrome.exe"] else "")
    Code_label.config(text="Code" if statuses["Code.exe"] else "")

# Create the Tkinter window
root = tk.Tk()
root.title("Process Monitor")
root.configure(bg="#282c34")
root.overrideredirect(True)  # Remove default borders

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x = screen_width//2 - 820//2
# y = screen_height//2 - 800//2
y = 0
root.geometry(f"820x36+{x}+{y}") #! overall size of the window


# Create labels for each process
notepad_label = tk.Label(root)
whkd_label = tk.Label(root)
chrome_label = tk.Label(root)
Code_label = tk.Label(root)

# Organize labels horizontally using grid
notepad_label.grid(row=0, column=0, padx=5, pady=5)
whkd_label.grid(row=0, column=1, padx=5, pady=5)
chrome_label.grid(row=0, column=2, padx=5, pady=5)
Code_label.grid(row=0, column=3, padx=5, pady=5)

last_statuses = {}

# Start the label visibility update loop in a separate thread
thread = threading.Thread(target=update_labels)
thread.daemon = True
thread.start()

root.mainloop()
