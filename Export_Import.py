import tkinter as tk
import subprocess
import filecmp
import os
root = tk.Tk()

def compare_directories(src_dir, dst_dir):
    if not (os.path.exists(src_dir) and os.path.exists(dst_dir)):
        return "One or both directories do not exist"
    dcmp = filecmp.dircmp(src_dir, dst_dir)
    if len(dcmp.left_only) == 0 and len(dcmp.right_only) == 0 and len(dcmp.diff_files) == 0:
        return "Directories are identical"
    else:
        return "Directories are different"

def create_button(text, frame, bg_color, fg_color, height, width, relief, font, padx_button, pady_button, padx_pack, pady_pack, anchor, command):
    button = tk.Button(frame, anchor=anchor, text=text, bg=bg_color, fg=fg_color, height=height, width=width, relief=relief, font=font, padx=padx_button, pady=pady_button, command=command)
    button.pack(padx=padx_pack, pady=pady_pack)
    return button

def perform_comparison(src_dir, dst_dir):
    result = compare_directories(src_dir, dst_dir)
    label.config(text=result)

button_properties = [
    ("whkdrc_Backup", root, "#1D2027", "#ffffff", 1, 15, "flat", ("calibri", 14, "bold"), 0, 0, (0, 0), (0, 0), "w", lambda: subprocess.Popen(['powershell.exe', 'Copy-Item', '-Path', '"C:\\Users\\nahid\\.config\\whkdrc"', '-Destination', '"C:\\Users\\nahid\\OneDrive\\Desktop\\wtc"', '-Recurse', '-Force', '-Verbose'], shell=True)),
    ("whkdrc_Restore", root, "#1D2027", "#ffffff", 1, 15, "flat", ("calibri", 14, "bold"), 0, 0, (0, 0), (0, 0), "w", lambda: subprocess.Popen(['powershell.exe', 'Copy-Item', '-Path', '"C:\\Users\\nahid\\OneDrive\\Desktop\\wtc"', '-Destination',  '"C:\\Users\\nahid\\.config\\whkdrc"', '-Recurse', '-Force', '-Verbose'], shell=True)),
]

for button_props in button_properties:
    create_button(*button_props)

label = tk.Label(root, font=("calibri", 14), wraplength=600)
label.pack()

root.mainloop()
