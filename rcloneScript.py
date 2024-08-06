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

# Additional options with display names
additional_options = [
    ("Fast-List", "--fast-list", False),
    ("Check-First", "--check-first", False),
]

# Update the state of an option and change the color of the label
def toggle_option(label, index):
    current_value = additional_options[index][2]
    additional_options[index] = (additional_options[index][0], additional_options[index][1], not current_value)
    update_label_color(label, not current_value)

# Update label color based on state
def update_label_color(label, is_selected):
    if is_selected:
        label.config(bg="green")
    else:
        label.config(bg="red")

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

# Create storage frame
storage_frame = ttk.Frame(root, padding="10")
storage_frame.grid(row=1, column=0, sticky=tk.W)

ttk.Label(storage_frame, text="Storage:").grid(row=0, column=0, sticky=tk.W)
storage_radios = [
    ("C:/", "C:/"),
    ("D:/", "D:/"),
    ("I:/", "I:/"),
    ("E:/", "E:/")
]

for idx, (text, value) in enumerate(storage_radios):
    radio = ttk.Radiobutton(storage_frame, text=text, variable=storage_var, value=value)
    radio.grid(row=0, column=1+idx, sticky=tk.W)

# Create arguments frame
arguments_frame = ttk.Frame(root, padding="10")
arguments_frame.grid(row=2, column=0, sticky=tk.W)

# Create labels for additional options
for idx, (display_text, _, _) in enumerate(additional_options):
    row = idx // 3
    column = idx % 3
    label = tk.Label(arguments_frame, text=display_text, bg="red", width=15)
    label.grid(row=row, column=column, sticky=tk.W, padx=5, pady=5)
    label.bind("<Button-1>", lambda e, l=label, i=idx: toggle_option(l, i))

ttk.Label(arguments_frame, text="--transfer=").grid(row=len(additional_options)//3 + 1, column=0, sticky=tk.W)
transfer_entry = ttk.Entry(arguments_frame, textvariable=transfer_var)
transfer_entry.grid(row=len(additional_options)//3 + 1, column=1, sticky=tk.W)

def execute_command():
    command = ["rclone", command_var.get(), storage_var.get()]

    for _, actual_text, is_selected in additional_options:
        if is_selected:
            command.append(actual_text)

    command.append(f"--transfer={transfer_var.get()}")

    final_command = " ".join(command)
    print("Executing:", final_command)
    subprocess.run(final_command, shell=True)

def clear_terminal():
    subprocess.run("cls", shell=True)

execute_button = ttk.Button(root, text="Execute", command=execute_command)
execute_button.grid(row=3, column=0, pady=10, sticky=tk.W)

clear_button = ttk.Button(root, text="Clear", command=clear_terminal)
clear_button.grid(row=3, column=1, pady=10, sticky=tk.W)

# Run the main event loop
root.mainloop()
