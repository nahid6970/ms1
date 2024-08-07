import tkinter as tk
from tkinter import ttk
import subprocess

# Create the main window
root = tk.Tk()
root.title("Rclone GUI")

# Variables
command_var = tk.StringVar(value="ls")
storage_var = tk.StringVar(value="C:/")
transfer_var = tk.StringVar(value="4")
include_var = tk.StringVar(value="*.jpg")
exclude_var = tk.StringVar(value="*.jpg")

# Additional options with display names
additional_options = [
    ("Fast-List", "--fast-list", True),
    ("HM", "--human-readable", True),
]

# Manage additional items
extra_items = {
    "transfer": {"text": "Transfers", "prefix": "--transfers", "var": transfer_var, "state": False},
    "include": {"text": "Include", "prefix": "--include", "var": include_var, "state": False},
    "exclude": {"text": "Exclude", "prefix": "--exclude", "var": exclude_var, "state": False}
}

def toggle_option(label, idx):
    additional_options[idx] = (additional_options[idx][0], additional_options[idx][1], not additional_options[idx][2])
    update_label_color(label, additional_options[idx][2])

def update_extra_item(label, key):
    item = extra_items[key]
    item["state"] = not item["state"]
    update_label_color(label, item["state"])

def update_label_color(label, is_selected):
    label.config(bg="green" if is_selected else "red")

def initialize_labels():
    for idx, (display_text, _, is_selected) in enumerate(additional_options):
        column = idx // 5
        row = idx % 5
        label = tk.Label(arguments_frame, text=display_text, bg="green" if is_selected else "red", width=20)
        label.grid(row=row, column=column, sticky=tk.W, padx=5, pady=5)
        label.bind("<Button-1>", lambda e, l=label, i=idx: toggle_option(l, i))

def update_extra_labels():
    for idx, (key, item) in enumerate(extra_items.items()):
        row = idx
        label = tk.Label(options_frame, text=item["text"], bg="green" if item["state"] else "red", width=15)
        label.grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        label.bind("<Button-1>", lambda e, l=label, k=key: update_extra_item(l, k))
        
        ttk.Label(options_frame, text="Value:").grid(row=row, column=1, sticky=tk.W)
        entry = ttk.Entry(options_frame, textvariable=item["var"])
        entry.grid(row=row, column=2, sticky=tk.W)

# Create command frame
command_frame = ttk.Frame(root, padding="10")
command_frame.grid(row=0, column=0, sticky=tk.W)

ttk.Label(command_frame, text="Command:").grid(row=0, column=0, sticky=tk.W)
ls_radio = ttk.Radiobutton(command_frame, text="ls", variable=command_var, value="ls")
ls_radio.grid(row=0, column=1, sticky=tk.W)
tree_radio = ttk.Radiobutton(command_frame, text="tree", variable=command_var, value="tree")
tree_radio.grid(row=0, column=2, sticky=tk.W)
ncdu_radio = ttk.Radiobutton(command_frame, text="ncdu", variable=command_var, value="ncdu")
ncdu_radio.grid(row=0, column=3, sticky=tk.W)
size_radio = ttk.Radiobutton(command_frame, text="size", variable=command_var, value="size")
size_radio.grid(row=0, column=4, sticky=tk.W)
mount_radio = ttk.Radiobutton(command_frame, text="mount", variable=command_var, value="mount")
mount_radio.grid(row=0, column=5, sticky=tk.W)

# Create storage frame
storage_frame = ttk.Frame(root, padding="10")
storage_frame.grid(row=1, column=0, sticky=tk.W)

ttk.Label(storage_frame, text="Storage:").grid(row=0, column=0, sticky=tk.W)
storage_radios = [
    ("C:/", "C:/"),
    ("D:/", "D:/"),
    ("cgu:/", "cgu:/"),
    ("gu:/", "gu:/"),
    ("g00:/", "g00:/"),
    ("g01:/", "g01:/"),
    ("g02:/", "g02:/"),
    ("g03:/", "g03:/"),
    ("g04:/", "g04:/"),
    ("g05:/", "g05:/"),
    ("g06:/", "g06:/"),
    ("g07:/", "g07:/"),
    ("g08:/", "g08:/"),
    ("g09:/", "g09:/"),
    ("g10:/", "g10:/"),
    ("g11:/", "g11:/"),
    ("g12:/", "g12:/"),
    ("g13:/", "g13:/"),
    ("g14:/", "g14:/"),
    ("g15:/", "g15:/"),
]

for idx, (text, value) in enumerate(storage_radios):
    if idx < 4:
        row = idx // 2
        column = idx % 2 + 1
    else:
        row = 2
        column = idx - 3
    radio = ttk.Radiobutton(storage_frame, text=text, variable=storage_var, value=value)
    radio.grid(row=row, column=column, sticky=tk.W)

# Create arguments frame
arguments_frame = ttk.Frame(root, padding="10")
arguments_frame.grid(row=2, column=0, sticky=tk.W)

# Create labels for additional options
initialize_labels()

# Create options frame for --transfer, --include, and --exclude
options_frame = ttk.Frame(root, padding="10")
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
    subprocess.Popen(final_command, shell=True)

def clear_terminal():
    subprocess.run("cls", shell=True)

execute_button = ttk.Button(root, text="Execute", command=execute_command)
execute_button.grid(row=4, column=0, pady=10, sticky=tk.W)

clear_button = ttk.Button(root, text="Clear", command=clear_terminal)
clear_button.grid(row=4, column=1, pady=10, sticky=tk.W)

# Run the main event loop
root.mainloop()
