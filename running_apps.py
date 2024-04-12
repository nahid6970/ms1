import tkinter as tk
import psutil
import threading
import time
from tkinter import *
from PIL import Image, ImageTk
import os

def create_custom_border(parent):
    BORDER_FRAME = tk.Frame(parent, bg="#1d2027", bd=0, highlightthickness=1, highlightbackground="red")
    BORDER_FRAME.place(relwidth=1, relheight=1)
    return BORDER_FRAME

root = tk.Tk()
root.title("Process Monitor")
root.configure(bg="#282c34")
root.overrideredirect(True)  # Remove default borders
# root.attributes('-topmost', True)  # Set always on top
def check_window_topmost():
    if not root.attributes('-topmost'):
        root.attributes('-topmost', True)
    root.after(500, check_window_topmost)
# Call the function to check window topmost status periodically
check_window_topmost()


BORDER_FRAME = create_custom_border(root)
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x = screen_width - 500
y = 0
root.geometry(f"500x30+{x}+{y}") #! overall size of the window

root.wm_attributes('-transparentcolor', '#ab23ff')
# Create a transparent label to overlay the image
transparent_label = Label(root, bg='#ab23ff')
transparent_label.place(relx=0, rely=0, relwidth=1, relheight=1)



# Function to check if a process is running
def is_process_running(process_name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == process_name:
            return True
    return False

#! examples
""" 
"xxx.exe": is_process_running("xxx.exe"),
(xxx_label       ,"xxx.exe"  ,"xxx"  ),
xxx_label    =tk.Label(box1,bg="#fcc62a",fg="#000000",font=("JETBRAINSMONO NF",10,"bold"))
xxx_label.grid(row=0,column=0,padx=5,pady=(3,1)) 

"""



# Function to update label visibility
def update_labels():
    global last_statuses
    while True:
        statuses = {
            "Notepad.exe" :is_process_running    ("Notepad.exe" ),
            "whkd.exe"    :is_process_running    ("whkd.exe"    ),
            "chrome.exe"  :is_process_running    ("chrome.exe"  ),
            "Code.exe"    :is_process_running    ("Code.exe"    ),
            "python.exe"  :is_process_running    ("python.exe"  ),
            "glazewm.exe" :is_process_running    ("glazewm.exe" ),
            "komorebi.exe":is_process_running    ("komorebi.exe"),
        }
        if statuses != last_statuses:
            root.after_idle(update_labels_gui, statuses)
            last_statuses = statuses
        time.sleep(1)  # Check every 1 second

def update_labels_gui(statuses):
    labels = [
              (notepad_label        ,"Notepad.exe"   ,"Notepad"   ),
              (whkd_label           ,"whkd.exe"      ,"whkd"      ),
              (chrome_label         ,"chrome.exe"    ,"Chrome"    ),
              (Code_label           ,"Code.exe"      ,"Code"      ),
              (Python_label         ,"python.exe"    ,"Py"         ),
              (glazewm_label        ,"glazewm.exe"   ,"glazewm"   ),
              (komorebi_label       ,"komorebi.exe"  ,"komorebi"  ),
              ]

    for label, process_name, text in labels:
        if statuses[process_name]:
            label.config(text=text)
            label.grid()
        else:
            label.grid_remove()

box1 = tk.Frame(root, bg="#ab23ff")
box1.pack(side="right", anchor="ne", pady=(1,2),padx=(3,1))

chrome_label      =tk.Label(box1,bg="#fcc62a",fg="#000000",font=("JETBRAINSMONO NF",10,"bold"))
whkd_label        =tk.Label(box1,bg="#FFFFFF",fg="#000000",font=("JETBRAINSMONO NF",10,"bold"))
notepad_label     =tk.Label(box1,bg="#5bc0de",fg="#000000",font=("JETBRAINSMONO NF",10,"bold"))
Code_label        =tk.Label(box1,bg="#23a9f2",fg="#000000",font=("JETBRAINSMONO NF",10,"bold"))
Python_label      =tk.Label(box1,bg="#3772a4",fg="#000000",font=("JETBRAINSMONO NF",10,"bold"))
glazewm_label     =tk.Label(box1,bg="#41bdf8",fg="#000000",font=("JETBRAINSMONO NF",10,"bold"))
komorebi_label    =tk.Label(box1,bg="#9068b0",fg="#000000",font=("JETBRAINSMONO NF",10,"bold"))

last_statuses = {}

notepad_label.grid (row=0,column=0,padx=5,pady=(3,1))
whkd_label.grid    (row=0,column=1,padx=5,pady=(3,1))
glazewm_label.grid (row=0,column=2,padx=5,pady=(3,1))
komorebi_label.grid(row=0,column=3,padx=5,pady=(3,1))
chrome_label.grid  (row=0,column=4,padx=5,pady=(3,1))
Code_label.grid    (row=0,column=5,padx=5,pady=(3,1))
Python_label.grid  (row=0,column=6,padx=5,pady=(3,1))

thread = threading.Thread(target=update_labels)
thread.daemon = True
thread.start()

root.mainloop()
