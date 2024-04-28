import os
import shutil
import tkinter as tk
import filecmp

def compare_files(source, destination, label):
    if not os.path.exists(source) or not os.path.exists(destination):
        label.config(text="❓")
    else:
        if filecmp.cmp(source, destination):
            label.config(text="✔️")
        else:
            label.config(text="❌")
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


def compare_folders(source, destination, label):
    dir_cmp = filecmp.dircmp(source, destination)
    if dir_cmp.left_only or dir_cmp.right_only or dir_cmp.diff_files:
        label.config(text="❌ Folders are different")
    else:
        label.config(text="✔️ Folders are equal")


root = tk.Tk()
root.title("Backup & Restore")





#! Files

rclone_src="C:/Users/nahid/scoop/apps/rclone/current/rclone.conf"
rclone_dst="C:/Users/nahid/OneDrive/backup/rclone/rclone.conf"

rclone_backup = tk.Button(root, text="Rclone Backup", command=lambda:shutil.copyfile(rclone_src, rclone_dst))
rclone_backup.grid(row=1, column=0)

label = tk.Label(root, font=("calibri", 14), wraplength=300)
label.grid(row=1, column=1)
compare_files(rclone_src, rclone_dst, label)

rclone_restore = tk.Button(root, text="Rclone Restore", command=lambda:shutil.copyfile(rclone_dst, rclone_src))
rclone_restore.grid(row=1, column=2)




#! Folders








root.mainloop()
