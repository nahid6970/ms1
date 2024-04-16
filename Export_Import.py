import shutil
import os
import tkinter as tk
from tkinter import filedialog
import subprocess
import tkinter as tk
import filecmp
from datetime import datetime

root = tk.Tk()
root.title("Backup & Restore")
root.attributes('-topmost', True) 
# root.overrideredirect(True)
root.configure(bg="#282c34")



source      ="c:/test/src/hi.txt"
destination ="c:/test/dst/hi.txt"

def compare_files(source, destination):
    if not os.path.exists(source) or not os.path.exists(destination):
        label.config(text="❌ Similar files not found")
    else:
        if filecmp.cmp(source, destination):
            label.config(text="✔️ Files are equal")
        else:
            label.config(text="❌ Files are different")

        # Get last modified times of the files
        source_modified = os.path.getmtime(source)
        destination_modified = os.path.getmtime(destination)

        # Convert last modified times to human-readable format (12-hour format)
        source_last_modified = datetime.fromtimestamp(source_modified).strftime('%Y-%m-%d %I:%M:%S %p')
        destination_last_modified = datetime.fromtimestamp(destination_modified).strftime('%Y-%m-%d %I:%M:%S %p')

        if source_modified > destination_modified:
            label.config(text=label.cget("text") + f"\nLast modified: {source_last_modified} ({source})")
        else:
            label.config(text=label.cget("text") + f"\nLast modified: {destination_last_modified} ({destination})")

source = "c:/test/src/hi.txt"
destination = "c:/test/dst/hi.txt"

label = tk.Label(root, font=("calibri", 14), wraplength=300)
label.pack()

compare_files(source, destination)

backup_button = tk.Button(root, text="Backup", command=lambda: shutil.copyfile(source, destination))
backup_button.pack()

restore_button = tk.Button(root, text="Restore", command=lambda: shutil.copyfile(destination, source))
restore_button.pack()





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

yasb_src = "c:/Users/nahid/.yasb"
yasb_dst = "c:/ms1/asset/yasb_test"

label = tk.Label(root, font=("calibri", 14), wraplength=600)
label.pack()

compare_directories(yasb_src, yasb_dst)


backup_button = tk.Button(root, text="Backup", command=lambda: shutil.copyfile(yasb_src, yasb_dst))
backup_button.pack()

restore_button = tk.Button(root, text="Restore", command=lambda: shutil.copyfile(yasb_dst, yasb_src))
restore_button.pack()












# BOX_ = tk.Frame(root, bg="#1d2027")
# BOX_.pack(side="top", anchor="center", pady=(0,0), padx=(0,0))

# #! Folder
# def create_button(text, frame, bg_color, fg_color, height, width, relief, font, padx_button, pady_button, padx_pack, pady_pack, anchor, command):
#     button = tk.Button(frame, anchor=anchor, text=text, bg=bg_color, fg=fg_color, height=height, width=width, relief=relief, font=font, padx=padx_button, pady=pady_button, command=command)
#     button.pack(padx=padx_pack, pady=pady_pack)
#     return button

# button_properties =[
# ("Test",BOX_,"#1D2027","#ffffff",1,15,"flat",("calibri",14,"bold"),0,0,(0,0),(0,0),"w",lambda: subprocess.Popen(["explorer","C:\\Users\\nahid\\.yasb"],shell=True)),
# ]
# for button_props in button_properties:
#     create_button(*button_props)

root.mainloop()
