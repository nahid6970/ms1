import tkinter as tk
import subprocess
import filecmp
import os
root = tk.Tk()


def compare_directories(dir1, dir2):
    if not os.path.exists(dir1) or not os.path.exists(dir2):
        label.config(text="❌ Similar directories not found")
    else:
        dcmp = filecmp.dircmp(dir1, dir2)
        if len(dcmp.left_only) == 0 and len(dcmp.right_only) == 0 and len(dcmp.diff_files) == 0:
            label.config(text="✔️ Directories are identical")
        else:
            label.config(text="❌ Directories are different")
            
            # Display differences
            for subdir in dcmp.subdirs.values():
                for f in subdir.left_only:
                    label.config(text=label.cget("text") + f"\nFile only in {dir1}: {os.path.join(subdir.left, f)}")
                for f in subdir.right_only:
                    label.config(text=label.cget("text") + f"\nFile only in {dir2}: {os.path.join(subdir.right, f)}")
                for f in subdir.diff_files:
                    label.config(text=label.cget("text") + f"\nDifferent files: {os.path.join(subdir.left, f)} and {os.path.join(subdir.right, f)}")


def perform_comparison():
    src = "c:/Users/nahid/.yasb/"
    dst = "c:/ms1/asset/.yasb/"
    compare_directories(src, dst)

label = tk.Label(root, font=("calibri", 10), wraplength=600)
label.pack()

compare_button = tk.Button(root, text="Compare", command=perform_comparison)
compare_button.pack()

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

root.mainloop()
