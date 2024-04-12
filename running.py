import tkinter as tk
import psutil
import threading
import time

def create_custom_border(parent):
    BORDER_FRAME = tk.Frame(parent, bg="#1d2027", bd=0, highlightthickness=1, highlightbackground="red")
    BORDER_FRAME.place(relwidth=1, relheight=1)
    return BORDER_FRAME

root = tk.Tk()
root.title("Process Monitor")
root.configure(bg="#282c34")
root.overrideredirect(True)  # Remove default borders
root.attributes('-topmost', True)  # Set always on top

BORDER_FRAME = create_custom_border(root)
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x = screen_width - 250
y = screen_height - 78
root.geometry(f"250x30+{x}+{y}") #! overall size of the window


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
            "Code.exe": is_process_running("Code.exe"),
        }
        if statuses != last_statuses:
            root.after_idle(update_labels_gui, statuses)
            last_statuses = statuses
        time.sleep(1)  # Check every 1 second

# Function to update GUI labels
def update_labels_gui(statuses):
    labels = [
              (notepad_label     ,"notepad.exe","Notepad"),
              (whkd_label        ,"whkd.exe"   ,"whkd"   ),
              (chrome_label      ,"chrome.exe" ,"Chrome" ),
              (Code_label        ,"Code.exe"   ,"Code"   ),
              ]

    for label, process_name, text in labels:
        if statuses[process_name]:
            label.config(text=text)
            label.grid()
        else:
            label.grid_remove()

# Create labels for each process
chrome_label  =tk.Label(root,bg="#23a9f2",fg="#000000",font=("JETBRAINSMONO NF",10,"bold"))
whkd_label    =tk.Label(root,bg="#23a9f2",fg="#000000",font=("JETBRAINSMONO NF",10,"bold"))
notepad_label =tk.Label(root,bg="#23a9f2",fg="#000000",font=("JETBRAINSMONO NF",10,"bold"))
Code_label    =tk.Label(root,bg="#23a9f2",fg="#000000",font=("JETBRAINSMONO NF",10,"bold"))

last_statuses = {}

# Organize labels horizontally using grid
notepad_label.grid(row=0, column=0, padx=5, pady=5)
whkd_label.grid(row=0, column=1, padx=5, pady=5)
chrome_label.grid(row=0, column=2, padx=5, pady=5)
Code_label.grid(row=0, column=3, padx=5, pady=5)

# Start the label visibility update loop in a separate thread
thread = threading.Thread(target=update_labels)
thread.daemon = True
thread.start()

root.mainloop()
