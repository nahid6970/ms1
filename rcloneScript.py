import threading
import tkinter as tk
from tkinter import ttk
import subprocess
import pyautogui




def center_and_press_alt_2(window):
    def center_window():
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')
    def press_alt_2():
        pyautogui.hotkey('alt', '2')
    center_window()
    window.after(25, press_alt_2)

# Create the main window
root = tk.Tk()
root.title("Rclone + winfsp")
root.configure(bg="#282c34")
# Variables
command_var = tk.StringVar(value="ls")
storage_var = tk.StringVar(value="")
transfer_var = tk.StringVar(value="4")
include_var = tk.StringVar(value="*.jpg")
exclude_var = tk.StringVar(value="*.jpg")
maxage_var = tk.StringVar(value="1d")
minage_var = tk.StringVar(value="1d")
maxsize_var = tk.StringVar(value="100M")
minsize_var = tk.StringVar(value="100M")

style = ttk.Style()
style.configure("Custom.TRadiobutton", font=("JetBrainsmono nfp", 12, "bold"), foreground="#e6f752", background="#282c34")

style = ttk.Style()
style.configure("Black.TFrame", background="#282c34")


# Additional options with display names
additional_options = [
    ("Fast List"              ,"--fast-list"                     ,True) ,
    ("Readable"               ,"--human-readable"                ,True) ,
    ("Acknowledge Abuse"      ,"--drive-acknowledge-abuse"       ,True) ,
    ("Web Gui **Rcd"          ,"--rc-web-gui"                    ,False) ,
    ("Log Level"              ,"--log-level ERROR"               ,False),
    ("Stats Oneline"          ,"--stats-one-line"                ,False),
    ("Trashed Only"           ,"--drive-trashed-only "           ,False),
    ("Shared With Me"         ,"--drive-shared-with-me "         ,False),
    ("Skip Dangling Shortcuts","--drive-skip-dangling-shortcuts ",False),
    ("Skip Shortcuts"         ,"--drive-skip-shortcuts "         ,False),
    ("Date **tree "           ,"-D "                             ,False),
    ("Modified Time **tree"   ,"-t "                             ,False),
]

# Manage additional items
extra_items = {
    "transfer": {"text": "Transfers", "prefix": "--transfers", "var": transfer_var, "state": False},
    "include": {"text": "Include", "prefix": "--include", "var": include_var, "state": False},
    "exclude": {"text": "Exclude", "prefix": "--exclude", "var": exclude_var, "state": False},
    "Max_Age": {"text": "Max Age", "prefix": "--max-age", "var": maxage_var, "state": False},
    "Min_Age": {"text": "Min Age", "prefix": "--min-age", "var": minage_var, "state": False},
    "Max_Size": {"text": "Max Size", "prefix": "--max-size", "var": maxsize_var, "state": False},
    "Min_Size": {"text": "Min Size", "prefix": "--min-size", "var": minsize_var, "state": False},
}

def toggle_option(label, idx):
    additional_options[idx] = (additional_options[idx][0], additional_options[idx][1], not additional_options[idx][2])
    update_label_color(label, additional_options[idx][2])

def update_extra_item(label, key):
    item = extra_items[key]
    item["state"] = not item["state"]
    update_label_color(label, item["state"])

def update_label_color(label, is_selected):
    label.config(bg="#b6fba0" if is_selected else "#fa8a93")

def initialize_labels():
    for idx, (display_text, _, is_selected) in enumerate(additional_options):
        column = idx // 5
        row = idx % 5
        label = tk.Label(arguments_frame, text=display_text, font=("Jetbrainsmono nfp",10,"bold"), bg="#b6fba0" if is_selected else "#fa8a93", width=25, anchor="center")
        label.grid(row=row, column=column, sticky=tk.W, padx=5, pady=5)
        label.bind("<Button-1>", lambda e, l=label, i=idx: toggle_option(l, i))

def update_extra_labels():
    for idx, (key, item) in enumerate(extra_items.items()):
        row = idx
        label = tk.Label(options_frame, text=item["text"], font=("Jetbrainsmono nfp",10,"bold"), bg="#b6fba0" if item["state"] else "#fa8a93", width=15)
        label.grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        label.bind("<Button-1>", lambda e, l=label, k=key: update_extra_item(l, k))
        
        ttk.Label(options_frame, text="Value:").grid(row=row, column=1, sticky=tk.W,)
        entry = ttk.Entry(options_frame, textvariable=item["var"])
        entry.grid(row=row, column=2, sticky=tk.W)

# Create the style for the frame

# Create command frame with the new style
command_frame = ttk.Frame(root, padding="10", style="Black.TFrame")
command_frame.grid(row=0, column=0, sticky=tk.W)


ttk.Label(command_frame, text="Command:", background="#f15812", font=("Jetbrainsmono nfp", 12, "bold")).grid(row=0, column=0, sticky=tk.W)
# Command radios configuration
command_radios = [
    {"text": "ls"   ,"value": "ls"}   ,
    {"text": "Tree" ,"value": "tree"} ,
    {"text": "NcDu" ,"value": "ncdu"} ,
    {"text": "Size" ,"value": "size"} ,
    {"text": "Mount","value": "mount"},
    {"text": "Rcd","value": "rcd"},
]
# Initialize command radio buttons
for idx, item in enumerate(command_radios):
    radio = ttk.Radiobutton(command_frame, text=item["text"], variable=command_var, value=item["value"], style="Custom.TRadiobutton")
    radio.grid(row=0, column=idx+1, sticky=tk.W)

# ls_radio = ttk.Radiobutton(command_frame, text="ls", variable=command_var, value="ls", style="Custom.TRadiobutton")
# ls_radio.grid(row=0, column=1, sticky=tk.W)
# tree_radio = ttk.Radiobutton(command_frame, text="tree", variable=command_var, value="tree", style="Custom.TRadiobutton")
# tree_radio.grid(row=0, column=2, sticky=tk.W)
# ncdu_radio = ttk.Radiobutton(command_frame, text="ncdu", variable=command_var, value="ncdu", style="Custom.TRadiobutton")
# ncdu_radio.grid(row=0, column=3, sticky=tk.W)
# size_radio = ttk.Radiobutton(command_frame, text="size", variable=command_var, value="size", style="Custom.TRadiobutton")
# size_radio.grid(row=0, column=4, sticky=tk.W)
# mount_radio = ttk.Radiobutton(command_frame, text="mount", variable=command_var, value="mount", style="Custom.TRadiobutton")
# mount_radio.grid(row=0, column=5, sticky=tk.W)

# Create storage frame
storage_frame = ttk.Frame(root, padding="10", style="Black.TFrame")
storage_frame.grid(row=1, column=0, sticky=tk.W)


#! alt1 start
ttk.Label(storage_frame, text="Storage:", background="#f15812", font=("JetBrainsmono nfp", 12, "bold")).grid(row=0, column=0, sticky=tk.W)
storage_radios = [
    {"text": "N/A"  ,"value": ""     ,"row": 1,"column": 1},
    {"text": "C:/"  ,"value": "C:/"  ,"row": 1,"column": 2},
    {"text": "D:/"  ,"value": "D:/"  ,"row": 1,"column": 3},
    {"text": "cgu:/","value": "cgu:/","row": 2,"column": 1},
    {"text": "gu:/" ,"value": "gu:/" ,"row": 2,"column": 2},
    {"text": "g00:/","value": "g00:/","row": 2,"column": 3},
    {"text": "g01:/","value": "g01:/","row": 3,"column": 1},
    {"text": "g02:/","value": "g02:/","row": 3,"column": 2},
    {"text": "g03:/","value": "g03:/","row": 3,"column": 3},
    {"text": "g04:/","value": "g04:/","row": 3,"column": 4},
    {"text": "g05:/","value": "g05:/","row": 3,"column": 5},
    {"text": "g06:/","value": "g06:/","row": 4,"column": 1},
    {"text": "g07:/","value": "g07:/","row": 4,"column": 2},
    {"text": "g08:/","value": "g08:/","row": 4,"column": 3},
    {"text": "g09:/","value": "g09:/","row": 4,"column": 4},
    {"text": "g10:/","value": "g10:/","row": 4,"column": 5},
    {"text": "g11:/","value": "g11:/","row": 5,"column": 1},
    {"text": "g12:/","value": "g12:/","row": 5,"column": 2},
    {"text": "g13:/","value": "g13:/","row": 5,"column": 3},
    {"text": "g14:/","value": "g14:/","row": 5,"column": 4},
    {"text": "g15:/","value": "g15:/","row": 5,"column": 5},
]

for item in storage_radios:
    radio = ttk.Radiobutton(storage_frame, text=item["text"], variable=storage_var, value=item["value"], style="Custom.TRadiobutton")
    radio.grid(row=item["row"], column=item["column"], sticky=tk.W)
#! alt1 end

# ttk.Label(storage_frame, text="Storage:",background="#f15812", font=("Jetbrainsmono nfp",12,"bold")).grid(row=0, column=0, sticky=tk.W)
# storage_radios = [
#     ("C:/", "C:/"),
#     ("D:/", "D:/"),
#     ("cgu:/", "cgu:/"),
#     ("gu:/", "gu:/"),
#     ("g00:/", "g00:/"),
#     ("g01:/", "g01:/"),
#     ("g02:/", "g02:/"),
#     ("g03:/", "g03:/"),
#     ("g04:/", "g04:/"),
#     ("g05:/", "g05:/"),
#     ("g06:/", "g06:/"),
#     ("g07:/", "g07:/"),
#     ("g08:/", "g08:/"),
#     ("g09:/", "g09:/"),
#     ("g10:/", "g10:/"),
#     ("g11:/", "g11:/"),
#     ("g12:/", "g12:/"),
#     ("g13:/", "g13:/"),
#     ("g14:/", "g14:/"),
#     ("g15:/", "g15:/"),
# ]

# for idx, (text, value) in enumerate(storage_radios):
#     if idx < 4:
#         row = idx // 2
#         column = idx % 2 + 1
#     else:
#         row = 2
#         column = idx - 3
#     style = ttk.Style()
#     style.configure("Custom.TRadiobutton", font=("JetBrains Mono", 12, "bold"), foreground="#efd0b5", )
#     radio = ttk.Radiobutton(storage_frame, text=text, variable=storage_var, value=value, style="Custom.TRadiobutton")
#     radio.grid(row=row, column=column, sticky=tk.W)


# Create arguments frame
arguments_frame = ttk.Frame(root, padding="10", style="Black.TFrame")
arguments_frame.grid(row=2, column=0, sticky=tk.W)

# Create labels for additional options
initialize_labels()

# Create options frame for --transfer, --include, and --exclude
options_frame = ttk.Frame(root, padding="10", style="Black.TFrame")
options_frame.grid(row=3, column=0, sticky=tk.W)

# Update labels for extra items
update_extra_labels()

def execute_command():
    command = ["rclone", command_var.get(), storage_var.get()]
    if command_var.get() == "mount":
        # For mount command, generate the specific mount argument
        mount_dir = f"c:/{storage_var.get().strip(':/')}/"
        command.append(mount_dir)
    for display_text, actual_text, is_selected in additional_options:
        if is_selected:
            command.append(actual_text)
    # Include/exclude options
    for key, item in extra_items.items():
        if item["state"]:
            command.append(f"{item['prefix']}={item['var'].get()}")
    final_command = " ".join(command)
    print("Executing:", final_command)
    def run_command():
        process = subprocess.Popen(final_command, shell=True)
        process.wait()
        print("\033[94mJob Done\033[0m")  # Print "Job Done" in blue
    thread = threading.Thread(target=run_command)
    thread.start()


def clear_terminal():
    subprocess.run("cls", shell=True)

BottomFrame = ttk.Frame(root, padding="10", style="Black.TFrame")
BottomFrame.grid(row=4, column=0, sticky=tk.E)

execute_button = tk.Button(BottomFrame, text="Execute", font=("Jetbrainsmono nfp",12,"bold"), bg="#4da9ff", fg="#000000", command=execute_command)
execute_button.grid(row=4, column=0, pady=10, padx=10, sticky=tk.W)

clear_button = tk.Button(BottomFrame, text="Clear", font=("Jetbrainsmono nfp",12,"bold"), bg="#282c34",fg="#ffffff", command=clear_terminal)
clear_button.grid(row=4, column=1, pady=10, sticky=tk.W)

center_and_press_alt_2(root)
# Run the main event loop
root.mainloop()