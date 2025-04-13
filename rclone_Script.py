import threading
import tkinter as tk
from tkinter import ttk
import subprocess
import pyautogui



# Create the main window
root = tk.Tk()
root.title("Rclone + winfsp")
root.configure(bg="#282c34")

# Configure row and column weights for root to allow expansion
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
root.overrideredirect(True)  # Remove default borders


# Create the Notebook widget (for tabs)
notebook = ttk.Notebook(root)
notebook.grid(row=0, column=0, sticky="nsew") # Changed sticky to "nsew"

# First tab: General Commands
tab1 = ttk.Frame(notebook, style="TNotebook.Tab")
notebook.add(tab1, text='General')

# Configure row and column weights for tab1 if needed (though pack might handle this)
tab1.grid_rowconfigure(0, weight=1)
tab1.grid_columnconfigure(0, weight=1)

BottomFrame = ttk.Frame(tab1, padding="10", style="TNotebook.Tab")
BottomFrame.pack(fill="both", expand=False) # Use fill="both" to expand in both directions

# Second tab: Quick Commands
tab2 = ttk.Frame(notebook, style="TNotebook.Tab")
notebook.add(tab2, text='Quick Commands')

quick_commands_frame = ttk.Frame(tab2, padding="10", style="TNotebook.Tab")
quick_commands_frame.pack(fill="x", expand=False)

style = ttk.Style()
style.theme_use('default') # Try a different theme (e.g.,'winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')
# print(style.theme_names())  # See available themes

style.configure("Custom.TRadiobutton", font=("Arial", 12, "bold"), foreground="#e6f752", background="#282c34")
style.map("Custom.TRadiobutton",
    foreground=[('active', '#333333'), ('selected', '#000000')],
    background=[('active', '#e0e0e0'), ('selected', '#ffffff')]
)
style.configure("Black.TFrame", background="#282c34")
style.configure("TCombobox", font=("JetBrainsmono nfp", 10))
style.configure("TEntry", font=("JetBrainsmono nfp", 10))

# --- Customizing the Notebook Tab Bar ---
style.configure("TNotebook",
                    background="#272727",
                    foreground="#c0c0c0",                   
                    borderwidth=0)
style.configure("TNotebook.Tab",
                    background="#333333",
                    foreground="#c39645",
                    focuscolor="#666666",
                    borderwidth=0                            
                    )
style.map('TNotebook.Tab',background=[("selected",'#272727')],
                    highlightbackground =[("active","#333")],                                    
                            lightcolor=[("selected", "#333333")],
                            foreground=[("active","#4f5a69")])


# Variables
command_var = tk.StringVar(value="ls")
storage_var = tk.StringVar(value="")
from_var = tk.StringVar(value="")
to_var = tk.StringVar(value="")
transfer_var = tk.StringVar(value="4")
include_var = tk.StringVar(value="*.jpg")
exclude_var = tk.StringVar(value="*.jpg")
maxage_var = tk.StringVar(value="1d")
minage_var = tk.StringVar(value="1d")
maxsize_var = tk.StringVar(value="100M")
minsize_var = tk.StringVar(value="100M")
grep_var = tk.StringVar(value="")


# Additional options with display names
additional_options = [
    ("Fast List",                                                                                                          "--fast-list"                                                                                                                                   ,True),
    ("Readable",                                                                                                            "--human-readable"                                                                                                                              ,True),
    ("Acknowledge Abuse",                                                                                                   "--drive-acknowledge-abuse"                                                                                                                   ,True),
    ("Progress",                                                                                                              "-P"                                                                                                                                            ,False),
    ("Dry Run",                                                                                                             "--dry-run"                                                                                                                                     ,False),
    ("Web Gui **Rcd",                                                                                                        "--rc-web-gui"                                                                                                                                ,False),
    ("vfs-cache",                                                                                                           "--vfs-cache-mode writes"                                                                                                                   ,False),
    ("Verbose Lengthy",                                                                                                     "-vv"                                                                                                                                            ,False),
    ("Verbose Minimal",                                                                                                     "-v"                                                                                                                                             ,False),
    ("Log Level",                                                                                                           "--log-level ERROR"                                                                                                                             ,False),
    ("Stats Oneline",                                                                                                       "--stats-one-line"                                                                                                                                ,True),
    ("Trashed Only",                                                                                                        "--drive-trashed-only "                                                                                                                          ,False),
    ("Shared With Me",                                                                                                      "--drive-shared-with-me "                                                                                                                        ,False),
    ("Skip Dangling Shortcuts",                                                                                             "--drive-skip-dangling-shortcuts "                                                                                                             ,False),
    ("Skip Shortcuts",                                                                                                      "--drive-skip-shortcuts "                                                                                                                         ,False),
    ("Date **tree ",                                                                                                         "-D "                                                                                                                                            ,False),
    ("Modified Time **tree",                                                                                                "-t "                                                                                                                                            ,False),
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

def Main_Flags():
    for idx, (display_text, _, is_selected) in enumerate(additional_options):
        column = idx // 5
        row = idx % 5
        label = tk.Label(Main_Flags_list, text=display_text, font=("Jetbrainsmono nfp",10,"bold"), bg="#b6fba0" if is_selected else "#fa8a93", width=25, anchor="center")
        label.grid(row=row, column=column, sticky=tk.W, padx=5, pady=5)
        label.bind("<Button-1>", lambda e, l=label, i=idx: toggle_option(l, i))

def update_extra_labels():
    for idx, (key, item) in enumerate(extra_items.items()):
        row = idx
        label = tk.Label(Filter_Flags, text=item["text"], font=("Jetbrainsmono nfp",10,"bold"), bg="#b6fba0" if item["state"] else "#fa8a93", width=15)
        label.grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        label.bind("<Button-1>", lambda e, l=label, k=key: update_extra_item(l, k))

        entry = ttk.Entry(Filter_Flags, textvariable=item["var"], font=("JetBrainsmono nfp", 12, "bold"))
        entry.grid(row=row, column=1, sticky=tk.W)

# Create the style for the frame

# Create command frame with the new style
command_frame = ttk.Frame(BottomFrame, padding="10", style="Black.TFrame")
command_frame.grid(row=0, column=0, sticky=tk.W)


ttk.Label(command_frame, text="Command:", background="#f15812", font=("Jetbrainsmono nfp", 12, "bold")).grid(row=0, column=0, sticky=tk.W)
# Command radios configuration
command_radios = [
    {"text": "ls"    ,"value": "ls"},
    {"text": "copy"  ,"value": "copy"},
    {"text": "sync"  ,"value": "sync"},
    {"text": "tree"  ,"value": "tree"} ,
    {"text": "ncdu"  ,"value": "ncdu"} ,
    {"text": "size"  ,"value": "size"} ,
    {"text": "mount(winfsp)","value": "mount"},
    {"text": "rcd"   ,"value": "rcd"},
]
# Initialize command radio buttons
for idx, item in enumerate(command_radios):
    radio = ttk.Radiobutton(command_frame, text=item["text"], variable=command_var, value=item["value"], style="Custom.TRadiobutton")
    radio.grid(row=0, column=idx+1, sticky=tk.W)


# Create storage frame
storage_frame = ttk.Frame(BottomFrame, padding="10", style="Black.TFrame")
storage_frame.grid(row=1, column=0, sticky=tk.W)

#! alt1 start
ttk.Label(storage_frame, text="Storage:", background="#f15812", font=("JetBrainsmono nfp", 12, "bold")).grid(row=0, column=0, sticky=tk.W)
storage_radios = [
    {"text": "N/A"   ,"value": ""      ,"row": 0,"column": 1},
    {"text": "C:/"   ,"value": "C:/"   ,"row": 0,"column": 2},
    {"text": "D:/"   ,"value": "D:/"   ,"row": 0,"column": 3},

    {"text": "cgu:/" ,"value": "cgu:/" ,"row": 1,"column": 1},
    {"text": "gu:/"  ,"value": "gu:/"  ,"row": 1,"column": 2},
    {"text": "g00:/" ,"value": "g00:/" ,"row": 1,"column": 3},

    {"text": "g01:/" ,"value": "g01:/" ,"row": 2,"column": 1},
    {"text": "g02:/" ,"value": "g02:/" ,"row": 2,"column": 2},
    {"text": "g03:/" ,"value": "g03:/" ,"row": 2,"column": 3},
    {"text": "g04:/" ,"value": "g04:/" ,"row": 2,"column": 4},
    {"text": "g05:/" ,"value": "g05:/" ,"row": 2,"column": 5},

    {"text": "g06:/" ,"value": "g06:/" ,"row": 3,"column": 1},
    {"text": "g07:/" ,"value": "g07:/" ,"row": 3,"column": 2},
    {"text": "g08:/" ,"value": "g08:/" ,"row": 3,"column": 3},
    {"text": "g09:/" ,"value": "g09:/" ,"row": 3,"column": 4},
    {"text": "g10:/" ,"value": "g10:/" ,"row": 3,"column": 5},

    {"text": "g11:/" ,"value": "g11:/" ,"row": 4,"column": 1},
    {"text": "g12:/" ,"value": "g12:/" ,"row": 4,"column": 2},
    {"text": "g13:/" ,"value": "g13:/" ,"row": 4,"column": 3},
    {"text": "g14:/" ,"value": "g14:/" ,"row": 4,"column": 4},
    {"text": "g15:/" ,"value": "g15:/" ,"row": 4,"column": 5},

    {"text": "o0:/"  ,"value": "o0:/"  ,"row": 5,"column": 1},
    {"text": "ouk:/" ,"value": "ouk:/" ,"row": 5,"column": 2},

    {"text": "m0:/"  ,"value": "m0:/"  ,"row": 6,"column": 1},
    {"text": "m1:/"  ,"value": "m1:/"  ,"row": 6,"column": 2},
]

for item in storage_radios:
    radio = ttk.Radiobutton(storage_frame, text=item["text"], variable=storage_var, value=item["value"], style="Custom.TRadiobutton")
    radio.grid(row=item["row"], column=item["column"], sticky=tk.W)


# Define common paths with custom names
common_paths = {
    "Songs_Cloud": "gu:/song",
    "Software_Cloud": "gu:/software",
    "MX_Cloud": "gu:/mx",

    "-------------------------------1": "",

    "Desktop_Local": "C:/Users/nahid/Desktop",
    "Desktop_Cloud": "o0/Desktop",
    "Pictures_Local": "C:/Users/nahid/Pictures",
    "Pictures_Cloud": "o0:/Pictures",

    "-------------------------------2": "",

    "Download_Rclone_C": "C:/rclone_download/",
    "Download_Rclone_D": "D:/rclone_download/"
}

# From
from_frame = ttk.Frame(BottomFrame, padding="0", style="Black.TFrame")
from_frame.grid(row=2, column=0, sticky=tk.W, pady=(10,0), padx=(10,0))

ttk.Label(from_frame, text="From:", width=5, background="#f15812", font=("JetBrainsmono nfp", 12, "bold")).grid(row=0, column=0, sticky=tk.W)
from_options = list(common_paths.keys())
from_combo = ttk.Combobox(from_frame, textvariable=from_var, values=from_options, width=50, font=("JetBrainsmono nfp", 12, "bold"))
from_combo.grid(row=0, column=1, sticky=tk.W)
from_combo.set("") # Set a default value

def update_from_var(event):
    selected_name = from_combo.get()
    if selected_name in common_paths:
        from_var.set(common_paths[selected_name])
    else:
        from_var.set("") # Clear if not in the predefined paths

from_combo.bind("<<ComboboxSelected>>", update_from_var)


# TO
to_frame = ttk.Frame(BottomFrame, padding="0", style="Black.TFrame")
to_frame.grid(row=3, column=0, sticky=tk.W, pady=(0,10), padx=(10,0))

ttk.Label(to_frame, text="To:", width=5, background="#f15812", font=("JetBrainsmono nfp", 12, "bold")).grid(row=0, column=0, sticky=tk.W)
to_options = list(common_paths.keys())
to_combo = ttk.Combobox(to_frame, textvariable=to_var, values=to_options, width=50, font=("JetBrainsmono nfp", 12, "bold"))
to_combo.grid(row=0, column=1, sticky=tk.W)
to_combo.set("") # Set a default value

def update_to_var(event):
    selected_name = to_combo.get()
    if selected_name in common_paths:
        to_var.set(common_paths[selected_name])
    else:
        to_var.set("") # Clear if not in the predefined paths

to_combo.bind("<<ComboboxSelected>>", update_to_var)

# Create arguments frame
Main_Flags_list = ttk.Frame(BottomFrame, padding="10", style="Black.TFrame")
Main_Flags_list.grid(row=4, column=0, sticky=tk.W)

# Create labels for additional options
Main_Flags()

# Create options frame for --transfer, --include, and --exclude
Filter_Flags = ttk.Frame(BottomFrame, padding="10", style="Black.TFrame")
Filter_Flags.grid(row=5, column=0, sticky=tk.W)

grep_frame = ttk.Frame(BottomFrame, padding="10", style="Black.TFrame")
grep_frame.grid(row=6, column=0, sticky=tk.W)

ttk.Label(grep_frame, text="Grep Text:", background="#f15812", font=("Jetbrainsmono nfp", 12, "bold")).grid(row=0, column=0, sticky=tk.W)
grep_entry = ttk.Entry(grep_frame, textvariable=grep_var, width=30, font=("JetBrainsmono nfp", 12, "bold"))
grep_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

# Update labels for extra items
update_extra_labels()

def execute_command():
    command = ["rclone", command_var.get(), storage_var.get(), from_var.get(), to_var.get()]
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

    # Append grep filter if text is provided
    grep_text = grep_var.get().strip()
    if grep_text:
        command.append(f"| grep -i {grep_text}")

    final_command = " ".join(command)
    print("Executing:", final_command)

    def run_command():
        process = subprocess.Popen(final_command, shell=True)
        process.wait()
        print("\033[92mTask Completed\033[0m")
    thread = threading.Thread(target=run_command)
    thread.start()



def clear_terminal():
    subprocess.run("cls", shell=True)

execute_button = tk.Button(BottomFrame, text="Execute", font=("Jetbrainsmono nfp",12,"bold"), bg="#4da9ff", fg="#000000", command=execute_command)
execute_button.grid(row=10, column=0, pady=10, padx=10, sticky=tk.W)

clear_button = tk.Button(BottomFrame, text="Clear", font=("Jetbrainsmono nfp",12,"bold"), bg="#282c34",fg="#ffffff", command=clear_terminal)
clear_button.grid(row=10, column=1, pady=10, sticky=tk.W)



# Assuming quick_commands_frame is already created.
msBackups_Label = tk.Label( quick_commands_frame, text="msBackups \uf40a", font=("Jetbrainsmono nfp", 12, "bold"), bg="#a0522d", fg="#ffffff" )
msBackups_Label.grid(row=1, column=1, pady=10, padx=10, sticky=tk.W)
msBackups_Label.bind("<Button-1>", lambda event: threading.Thread(target=lambda: (
    print("Executing: rclone sync C:\\msBackups\\ o0:\\msBackups\\ -P --check-first --transfers=10 --track-renames --fast-list"),
    subprocess.Popen("rclone sync C:\\msBackups\\ o0:\\msBackups\\ -P --check-first --transfers=10 --track-renames --fast-list", shell=True).wait(),
    # print("\033[92mBackup Sync Completed\033[0m")
)).start())

# Assuming quick_commands_frame is already created.
Song_Label = tk.Label( quick_commands_frame, text="Song \uf40a", font=("Jetbrainsmono nfp", 12, "bold"), bg="#a0522d", fg="#ffffff" )
Song_Label.grid(row=2, column=1, pady=10, padx=10, sticky=tk.W)
Song_Label.bind("<Button-1>", lambda event: threading.Thread(target=lambda: (
    print("Executing: rclone sync D:\\song\\ gu:\\song\\ -P --check-first --transfers=10 --track-renames --fast-list"),
    subprocess.Popen("rclone sync D:\\song\\ gu:\\song\\ -P --check-first --transfers=10 --track-renames --fast-list", shell=True).wait(),
    # print("\033[92mBackup Sync Completed\033[0m")
)).start())



root.update_idletasks()
width = root.winfo_width()
height = root.winfo_height()
x = (root.winfo_screenwidth() // 2) - (width // 2)
y = (root.winfo_screenheight() // 2) - (height // 2)
root.geometry(f'{width}x{height}+{x}+{y}')

root.mainloop()