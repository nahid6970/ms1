import subprocess
import subprocess
import tkinter as tk
import ctypes


def set_console_title(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)
set_console_title("App Store")

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

x = screen_width - 300
y = screen_height//2 - 250//2
ROOT.geometry(f"300x350+{x}+{y}") #! overall size of the window

MAIN_FRAME = tk.Frame(BORDER_FRAME, bg="#1D2027", width=300, height=350) #!
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












BOX_WIDGET_APPID = tk.Frame(MAIN_FRAME, bg="#14bcff")
BOX_WIDGET_APPID.pack(pady=(30,0))

WIDGET_APPID = tk.Entry(BOX_WIDGET_APPID, width=30, fg="#000000", bg="#FFFFFF", font=("calibri", 18, "bold", "italic"), justify="center", relief="flat")
WIDGET_APPID.pack(padx=2, pady=2)


def insert_input():
    additional_text = WIDGET_APPID.get()
    return additional_text




def winget_search():
    additional_text = insert_input()
    additional_text = f'"{additional_text}"' if " " in additional_text else additional_text
    command = f'pwsh -Command "cd ; write-host  -foreground blue \'- Winget Search\' ; winget search {additional_text}"'
    try:
        subprocess.Popen(command)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
def winget_install():
    additional_text = insert_input()
    additional_text = f'"{additional_text}"' if " " in additional_text else additional_text
    command = f'pwsh -Command "cd ; write-host  -foreground blue \'- Winget install\' ; winget install {additional_text}"'
    try:
        subprocess.Popen(command)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
def winget_uninst():
    additional_text = insert_input()
    # Enclose additional_text in double quotes if it contains spaces
    additional_text = f'"{additional_text}"' if " " in additional_text else additional_text
    command = f'pwsh -Command "cd ; write-host  -foreground red \'- Winget Uninstall\' ; winget uninstall {additional_text}"'
    try:
        subprocess.Popen(command)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
def winget_infooo():
    additional_text = insert_input()
    # Enclose additional_text in double quotes if it contains spaces
    additional_text = f'"{additional_text}"' if " " in additional_text else additional_text
    command = f'pwsh -Command "cd ; write-host  -foreground blue \'- Winget Show\' ; winget show {additional_text}"'
    try:
        subprocess.Popen(command)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
def wget_inst_fzf():
    command = ' $host.UI.RawUI.WindowTitle = "wget🔽" ; winget search --exact "" | fzf --multi --preview-window=up:60% --preview \'winget show {1}\' | ForEach-Object { winget install $_.split()[0] }'
    try:
        subprocess.Popen([ 'start' , 'pwsh', '-Command', command], shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
def wget_unin_fzf():
    command = ' $host.UI.RawUI.WindowTitle = "wget❌" ; winget list "" | fzf --multi --preview-window=up:60% --preview \'winget show {1}\' | ForEach-Object { winget uninstall $_.split()[0] }'
    try:
        subprocess.Popen([ 'start' , 'pwsh', '-Command', command], shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def scoop_search():
    additional_text = insert_input()
    additional_text = f'"{additional_text}"' if " " in additional_text else additional_text
    command = f'pwsh -Command "cd ; write-host  -foreground blue \'- Scoop search\' ; scoop search {additional_text}"'
    try:
        subprocess.Popen(["powershell", "-Command", command], shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
def scoop_install():
    additional_text = insert_input()
    additional_text = f'"{additional_text}"' if " " in additional_text else additional_text
    command = f'pwsh -Command "cd ; write-host  -foreground blue \'- Scoop Install\' ; scoop install {additional_text}"'
    try:
        subprocess.Popen(["powershell", "-Command", command], shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
def scoop_uninstall():
    additional_text = insert_input()
    additional_text = f'"{additional_text}"' if " " in additional_text else additional_text
    command = f'pwsh -Command "cd ; write-host  -foreground red \'- Scoop UnInstall\' ; scoop uninstall {additional_text}"'
    try:
        subprocess.Popen(["powershell", "-Command", command], shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
def scoop_info():
    additional_text = insert_input()
    additional_text = f'"{additional_text}"' if " " in additional_text else additional_text
    command = f'pwsh -Command "cd ; write-host  -foreground blue \'- Scoop Info\' ; scoop info {additional_text}"'
    try:
        subprocess.Popen(["powershell", "-Command", command], shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
def scoop_install_fzf():
    # Path to the Python script generating the package list
    python_script = r"C:\ms1\scripts\python\scoop_list.py"

    # Run the Python script to generate the package list
    try:
        subprocess.run(['python', python_script], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        return
    # Path to the text file containing package list
    package_list_file = r"C:\Users\nahid\OneDrive\backup\installed_apps\python_scoop_list_fzf.txt"
    # Command to read from the text file and pipe it to fzf
    command = f'$host.UI.RawUI.WindowTitle = "scoop🔽" ; type {package_list_file} | fzf --multi --preview "scoop info {{1}}" | ForEach-Object {{scoop install $_.split()[0]}}'
    try:
        subprocess.Popen(['start', 'pwsh', '-Command', command], shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
def scoop_uninstall_fzf():
    command = '$host.UI.RawUI.WindowTitle = "scoop❌" ; scoop list "" | fzf --multi --preview \'scoop info {1}\' | ForEach-Object { scoop uninstall $_.split()[0] }'
    try:
        subprocess.Popen(['start' , 'pwsh', '-Command', command], shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

#! App Store
def create_button(
        text,
        command,
        bg_color,
        fg_color,
        height,
        width,
        relief,
        font,
        padx_button,
        padx_pack,
        pady_button,
        pady_pack,
        row_button,
        column_button,
        columnspan,
        sticky,
        ):
    button = tk.Button(input_frame, text=text, command=command, width=width, fg=fg_color, bg=bg_color, font=font)
    button.grid(row=row_button, column=column_button, padx=padx_button, pady=pady_button, sticky=sticky, columnspan=columnspan)
    return button

input_frame = tk.Frame(MAIN_FRAME, bg="#1D2027")
input_frame.pack(pady=10)

winget_scoop_button_properties = [
("Winget"    ,None               ,"#76c2ff","#000000",1,12,"flat",("JetBrainsMono NF",12),5,5,0,5,     1,1,1 ,"ew"),
("Search"    ,winget_search      ,"#1D2027","#FFFFFF",1,12,"flat",("JetBrainsMono NF",10),5,5,0,5,     2,1,1 ,""  ),
("Info"      ,winget_infooo      ,"#1D2027","#FFFFFF",1,12,"flat",("JetBrainsMono NF",10),5,5,0,5,     3,1,1 ,""  ),
("Install"   ,winget_install     ,"#1D2027","#FFFFFF",1,12,"flat",("JetBrainsMono NF",10),5,5,0,5,     4,1,1 ,""  ),
("Uninstall" ,winget_uninst      ,"#1D2027","#FFFFFF",1,12,"flat",("JetBrainsMono NF",10),5,5,0,5,     5,1,1 ,""  ),
("Install"   ,wget_inst_fzf      ,"#1D2027","#00FF00",1,12,"flat",("JetBrainsMono NF",10),5,5,0,5,     6,1,1 ,""  ),
("Uninstall" ,wget_unin_fzf      ,"#1D2027","#FF0000",1,12,"flat",("JetBrainsMono NF",10),5,5,0,5,     7,1,1 ,""  ),

("Scoop"     ,None               ,"#95cd95","#000000",1,12,"flat",("JetBrainsMono NF",12),5,5,0,5,     1,2,1 ,"ew"),
("Search"    ,scoop_search       ,"#1D2027","#FFFFFF",1,12,"flat",("JetBrainsMono NF",10),5,5,0,5,     2,2,1 ,""  ),
("Info"      ,scoop_info         ,"#1D2027","#FFFFFF",1,12,"flat",("JetBrainsMono NF",10),5,5,0,5,     3,2,1 ,""  ),
("Install"   ,scoop_install      ,"#1D2027","#FFFFFF",1,12,"flat",("JetBrainsMono NF",10),5,5,0,5,     4,2,1 ,""  ),
("Uninstall" ,scoop_uninstall    ,"#1D2027","#FFFFFF",1,12,"flat",("JetBrainsMono NF",10),5,5,0,5,     5,2,1 ,""  ),
("Install"   ,scoop_install_fzf  ,"#1D2027","#00FF00",1,12,"flat",("JetBrainsMono NF",10),5,5,0,5,     6,2,1 ,""  ),
("Uninstall" ,scoop_uninstall_fzf,"#1D2027","#FF0000",1,12,"flat",("JetBrainsMono NF",10),5,5,0,5,     7,2,1 ,""  )
]

for button_props in winget_scoop_button_properties:
    create_button(*button_props)

#! Ending
MAIN_FRAME.pack()
ROOT.mainloop()
