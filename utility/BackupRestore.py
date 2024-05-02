import os
import shutil
import tkinter as tk
import filecmp

import sys
sys.path.append('C:/ms1/')
from functionlist import *


def compare_files(source, destination, label):
    if not os.path.exists(source) or not os.path.exists(destination):
        label.config(text="\uf06a")
    else:
        if filecmp.cmp(source, destination):
            label.config(text="\uf058")
        else:
            label.config(text="\uf530")
    # Schedule the next comparison after 1 second
    label.after(1000, lambda: compare_files(source, destination, label))

def compare_folders(source, destination, label):
    if not os.path.exists(source) or not os.path.exists(destination):
        label.config(text="\uf06a")
    else:
        dir_cmp = filecmp.dircmp(source, destination)
        if dir_cmp.left_only or dir_cmp.right_only or dir_cmp.diff_files:
            label.config(text="\uf530")
        else:
            label.config(text="\uf058")
    # Schedule the next comparison after 1 second
    label.after(1000, lambda: compare_folders(source, destination, label))

root = tk.Tk()
root.title("Backup & Restore")

default_font = ("Jetbrainsmono nfp", 14, "italic")
root.option_add("*Font", default_font)

#! Files

rclone_backup = tk.Button(root, text="Rclone Backup", command=lambda: shutil.copyfile(rclone_src, rclone_dst))
rclone_restore = tk.Button(root, text="Rclone Restore", command=lambda: shutil.copyfile(rclone_dst, rclone_src))
label_file = tk.Label(root, wraplength=300) ; compare_files(rclone_src, rclone_dst, label_file)

rclone_backup.grid(row=1, column=0)
rclone_restore.grid(row=1, column=1)
label_file.grid(row=1, column=2)


#! Folders

#! glazewm_backup = tk.Button(root, text="glazewm_ Backup", command=lambda: shutil.rmtree(glazewm_dst) or shutil.copytree(glazewm_src, glazewm_dst))
glazewm_backup = tk.Button(root, text="glazewm_ Backup", command=lambda: (shutil.rmtree(glazewm_dst) if os.path.exists(glazewm_src) else None) or shutil.copytree(glazewm_src, glazewm_dst))
glazewm_restore = tk.Button(root, text="glazewm_ Restore", command=lambda: shutil.copytree(glazewm_dst, glazewm_src))
label_folder = tk.Label(root, wraplength=300) ; compare_folders(glazewm_src, glazewm_dst, label_folder)

glazewm_backup.grid(row=2, column=0)
glazewm_restore.grid(row=2, column=1)
label_folder.grid(row=2, column=2)

root.mainloop()




















# def compare_files(source, destination, label):
#     if not os.path.exists(source) or not os.path.exists(destination):
#         label.config(text="❌ Similar files not found")
#     else:
#         if filecmp.cmp(source, destination):
#             label.config(text="✔️ Files are equal")
#         else:
#             label.config(text="❌ Files are different")

        # # Get last modified times of the files
        # source_modified = os.path.getmtime(source)
        # destination_modified = os.path.getmtime(destination)

        # # Convert last modified times to human-readable format (12-hour format)
        # source_last_modified = datetime.fromtimestamp(source_modified).strftime('%Y-%m-%d %I:%M:%S %p')
        # destination_last_modified = datetime.fromtimestamp(destination_modified).strftime('%Y-%m-%d %I:%M:%S %p')

        # if source_modified > destination_modified:
        #     label.config(text=label.cget("text") + f"\nLast modified: {source_last_modified} ({source})")
        # else:
        #     label.config(text=label.cget("text") + f"\nLast modified: {destination_last_modified} ({destination})")
