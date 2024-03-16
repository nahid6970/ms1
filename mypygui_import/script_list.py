import os
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
y = screen_height//2 - 150//2
ROOT.geometry(f"400x150+{x}+{y}") #! overall size of the window

MAIN_FRAME = tk.Frame(BORDER_FRAME, bg="#1D2027", width=400, height=150) #!
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





#! Script List
BOX_1 = tk.Frame(MAIN_FRAME, bg="#1d2027")
BOX_1.pack(side="top", anchor="center", pady=(20,0), padx=(0,0))

def load_scripts(folder_path):
    script_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(('.ahk', '.ps1', '.py')):
                script_files.append(os.path.join(root, file))
    return script_files

def folder_selected(event):
    selected_folder = folder_var.get()
    script_files = load_scripts(selected_folder)
    script_var.set("Select a script")
    script_dropdown['menu'].delete(0, 'end') # Clear previous items
    for script_file in script_files:
        script_dropdown['menu'].add_command(label=os.path.basename(script_file), command=tk._setit(script_var, os.path.abspath(script_file)))

def run_script():
    selected_script = script_var.get()
    if selected_script:
        subprocess.Popen(selected_script, shell=True)

# Folders
folders = [
"C:\\ms1\\scripts\\autohotkey",
"C:\\ms1\\scripts\\python"
]

# Dropdown for folders
folder_var = tk.StringVar(BOX_1)
folder_var.set("Select a folder")
folder_dropdown = tk.OptionMenu(BOX_1, folder_var, *folders, command=folder_selected)

folder_dropdown.configure(width=30, background="#ddf581", foreground="black", font=("JetBrainsMono NF", 10))
folder_dropdown.config(indicatoron=False)

# Dropdown for scripts
script_var = tk.StringVar(BOX_1)
script_var.set("Select a script")
script_dropdown = tk.OptionMenu(BOX_1, script_var, "Select a script")
script_dropdown.configure(width=30, background="#ddf581", foreground="black", font=("JetBrainsMono NF", 10))
script_dropdown.config(indicatoron=False)

run_button = tk.Button(BOX_1, text="Run", command=run_script, bg="#41abff", font=("JetBrainsMono NF", 12))

folder_dropdown.grid(row=0, column=1, rowspan=1, padx=5, pady=10)
script_dropdown.grid(row=1, column=1, rowspan=1, padx=5, pady=10)
run_button.grid(row=0, column=2, rowspan=2, padx=5, pady=10, sticky="nsew") #! nwse means full filling up down left right spaces so if ns means fullfill up and down portion



#! Ending
MAIN_FRAME.pack()
ROOT.mainloop()
