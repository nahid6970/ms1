import subprocess
import subprocess
import tkinter as tk

# Vaiables to track the position of the mouse when clicking​⁡
drag_data = {"x": 0, "y": 0}

def start_drag(event):
    drag_data["x"] = event.x
    drag_data["y"] = event.y

def stop_drag(event):
    drag_data["x"] = None
    drag_data["y"] = None

def do_drag(event):
    if drag_data["x"] is not None and drag_data["y"] is not None:
        x, y = (event.x - drag_data["x"] + ROOT.winfo_x(), event.y - drag_data["y"] + ROOT.winfo_y())
        ROOT.geometry("+%s+%s" % (x, y))

def create_custom_border(parent):
    BORDER_FRAME = tk.Frame(parent, bg="#1d2027", bd=0, highlightthickness=1, highlightbackground="red")
    BORDER_FRAME.place(relwidth=1, relheight=1)
    return BORDER_FRAME

# Create main window
ROOT = tk.Tk()
ROOT.title("Folder")
ROOT.attributes('-topmost', True)  # Set always on top
# ROOT.geometry("520x800")
ROOT.configure(bg="#282c34")
ROOT.overrideredirect(True)  # Remove default borders

# Create custom border
BORDER_FRAME = create_custom_border(ROOT)

# Add bindings to make the window movable
ROOT.bind("<ButtonPress-1>", start_drag)
ROOT.bind("<ButtonRelease-1>", stop_drag)
ROOT.bind("<B1-Motion>", do_drag)

screen_width = ROOT.winfo_screenwidth()
screen_height = ROOT.winfo_screenheight()

x = screen_width - 400
y = screen_height//2 - 200//2
ROOT.geometry(f"400x200+{x}+{y}") #! overall size of the window

MAIN_FRAME = tk.Frame(BORDER_FRAME, bg="#1D2027", width=400, height=200) #!
MAIN_FRAME.pack_propagate(False)
MAIN_FRAME.pack(pady=1)  # Add some padding at the top
MAIN_FRAME.pack(expand=True)


#! Close Window
def close_window(event=None):
    ROOT.destroy()

#!? Main ROOT BOX
ROOT1 = tk.Frame(ROOT, bg="#1d2027")
ROOT1.pack(side="right", anchor="ne", pady=(3,2),padx=(3,1))

def create_label(text, parent, bg, fg, width, height, relief, font, ht, htc, padx, pady, anchor, row, column, rowspan, columnspan):
    label = tk.Label(parent, text=text, bg=bg, fg=fg, width=width, height=height, relief=relief, font=font, highlightthickness=ht, highlightbackground=htc)
    label.grid(row=row, column=column, padx=padx, pady=pady, sticky=anchor, rowspan=rowspan, columnspan=columnspan)
    return label

label_properties = [
{"text": "r","parent": ROOT1,"bg": "#1d2027","fg": "#ff0000","width": 0  ,"height": "0","relief": "flat","font": ("Webdings",10,"bold")  ,"ht": 0,"htc": "#FFFFFF","padx": (0 ,2) ,"pady": (0,0),"anchor": "w","row": 1,"column": 1 ,"rowspan": 1,"columnspan": 1},#! LB_X alternative wingdings x
]
labels = [create_label(**prop) for prop in label_properties]
LB_XXX, = labels
LB_XXX.bind("<Button-1>", close_window)



#! Process
def insert_input():
    additional_text = WIDGET_APPID.get()
    return additional_text

def get_process():
    additional_text = insert_input()
    if not additional_text:  # Check if input is empty
        return  # Do nothing if input is empty
    command = f'Get-Process | Where-Object {{ $_.Name -like "*{additional_text}*" }} | Format-Table -Property ProcessName, Id -AutoSize'
    try:
        subprocess.run(["start","powershell", "-NoExit", "-Command", command], shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def kil_process():
    additional_text = insert_input()
    command = f'Stop-Process -Name {additional_text}'
    try:
        output = subprocess.run(["powershell", "-Command", command], stderr=subprocess.PIPE, shell=True, text=True)
        if "Cannot find a process with the name" in output.stderr:
            print(f"\033[91mError: Process {additional_text} not found.\033[0m")
        else:
            print(f"\033[94mProcess {additional_text} killed successfully.\033[0m")
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def custom_command():
    additional_text = insert_input()
    if not additional_text:  # Check if input is empty
        return  # Do nothing if input is empty
    profile_path = r'C:\Users\nahid\OneDrive\backup\Microsoft.PowerShell_profile.ps1'
    command = f'powershell -ExecutionPolicy Bypass -NoProfile -Command "& {{ . {profile_path}; {additional_text} }}"'
    try:
        # Execute the custom PowerShell command and capture the output
        subprocess.run(command, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

BOX_WIDGET_APPID = tk.Frame(MAIN_FRAME, bg="#FF0000")
BOX_WIDGET_APPID.pack(pady=(30,0))

WIDGET_APPID = tk.Entry(BOX_WIDGET_APPID, width=30, fg="#000000", bg="#14bcff", font=("calibri", 18, "bold", "italic"), justify="center", relief="flat")
WIDGET_APPID.pack(padx=2, pady=2)

BOX_ROW_APPID2 = tk.Frame(MAIN_FRAME, bg="black")
BOX_ROW_APPID2.pack(pady=2)

BT_GET_ID = tk.Button(BOX_ROW_APPID2, bg="#00ff21", fg="#fcffef", height=1, width=15, bd=0, highlightthickness=0, font=("calibri", 14, "bold"), command=get_process, text="🔍")
BT_GET_ID.pack(side="top", pady=0)

BT_KIL_ID = tk.Button(BOX_ROW_APPID2, bg="#ff4f00", fg="#fcffef", height=1, width=15, bd=0, highlightthickness=0, font=("calibri", 14, "bold"), command=kil_process, text="❌")
BT_KIL_ID.pack(side="top", pady=0)

BT_CUSTOM_CMD = tk.Button(BOX_ROW_APPID2, bg="#41abff", fg="#fcffef", height=1, width=15, bd=0, highlightthickness=0, font=("calibri", 14, "bold"), command=custom_command, text="🏃")
BT_CUSTOM_CMD.pack(side="top", pady=0)

#! Ending
MAIN_FRAME.pack()
ROOT.mainloop()
