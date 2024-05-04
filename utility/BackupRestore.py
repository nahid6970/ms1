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


#! ██████   ██████ ██       ██████  ███    ██ ███████
#! ██   ██ ██      ██      ██    ██ ████   ██ ██
#! ██████  ██      ██      ██    ██ ██ ██  ██ █████
#! ██   ██ ██      ██      ██    ██ ██  ██ ██ ██
#! ██   ██  ██████ ███████  ██████  ██   ████ ███████

rclone_backup = tk.Button(root, text="Rclone Backup", command=lambda: shutil.copyfile(rclone_src, rclone_dst))
rclone_restore = tk.Button(root, text="Rclone Restore", command=lambda: shutil.copyfile(rclone_dst, rclone_src))
label_file = tk.Label(root, wraplength=300) ; compare_files(rclone_src, rclone_dst, label_file)

rclone_backup.grid(row=1, column=0)
rclone_restore.grid(row=1, column=1)
label_file.grid(row=1, column=2)

#! ████████ ███████ ██████  ███    ███ ██ ███    ██  █████  ██
#!    ██    ██      ██   ██ ████  ████ ██ ████   ██ ██   ██ ██
#!    ██    █████   ██████  ██ ████ ██ ██ ██ ██  ██ ███████ ██
#!    ██    ██      ██   ██ ██  ██  ██ ██ ██  ██ ██ ██   ██ ██
#!    ██    ███████ ██   ██ ██      ██ ██ ██   ████ ██   ██ ███████

terminal_backup = tk.Button(root, text="terminal Backup", command=lambda: shutil.copyfile(terminal_src, terminal_dst))
terminal_src_location = tk.Button(root, text="src_dir", command=lambda: subprocess.Popen(["explorer", os.path.dirname(terminal_src)], shell=True))
terminal_restore = tk.Button(root, text="terminal Restore", command=lambda: shutil.copyfile(terminal_dst, terminal_src))
terminal_dst_location = tk.Button(root, text="src_dir", command=lambda: subprocess.Popen(["explorer", os.path.dirname(terminal_dst)], shell=True))
label_file = tk.Label(root, wraplength=300) ; compare_files(terminal_src, terminal_dst, label_file)

terminal_backup.grid(row=2, column=0)
terminal_src_location.grid(row=2, column=1)
terminal_restore.grid(row=2, column=2)
terminal_dst_location.grid(row=2, column=3)
label_file.grid(row=2, column=4)

#!  ██████  ██       █████  ███████ ███████ ██     ██ ███    ███
#! ██       ██      ██   ██    ███  ██      ██     ██ ████  ████
#! ██   ███ ██      ███████   ███   █████   ██  █  ██ ██ ████ ██
#! ██    ██ ██      ██   ██  ███    ██      ██ ███ ██ ██  ██  ██
#!  ██████  ███████ ██   ██ ███████ ███████  ███ ███  ██      ██

#! glazewm_backup = tk.Button(root, text="glazewm_ Backup", command=lambda: shutil.rmtree(glazewm_dst) or shutil.copytree(glazewm_src, glazewm_dst))
glazewm_backup = tk.Button(root, text="glazewm_ Backup", command=lambda: (shutil.rmtree(glazewm_dst) if os.path.exists(glazewm_src) else None) or shutil.copytree(glazewm_src, glazewm_dst))
glazewm_restore = tk.Button(root, text="glazewm_ Restore", command=lambda: shutil.copytree(glazewm_dst, glazewm_src))
label_folder = tk.Label(root, wraplength=300) ; compare_folders(glazewm_src, glazewm_dst, label_folder)

glazewm_backup.grid(row=3, column=0)
glazewm_restore.grid(row=3, column=1)
label_folder.grid(row=3, column=2)

#! ██████╗ ███████╗███████╗
#! ██╔══██╗██╔════╝██╔════╝
#! ██████╔╝███████╗███████╗
#! ██╔══██╗╚════██║╚════██║
#! ██║  ██║███████║███████║
#! ╚═╝  ╚═╝╚══════╝╚══════╝

Rss_db_backup = tk.Button(root, text="Rss_db_ Backup", command=lambda: (shutil.rmtree(Rss_db_dst) if os.path.exists(Rss_db_src) else None) or shutil.copytree(Rss_db_src, Rss_db_dst))
Rss_db_restore = tk.Button(root, text="Rss_db_ Restore", command=lambda: (shutil.rmtree(Rss_db_src) if os.path.exists(Rss_db_dst) else None) or shutil.copytree(Rss_db_dst, Rss_db_src))
label_folder = tk.Label(root, wraplength=300) ; compare_folders(Rss_db_src, Rss_db_dst, label_folder)

Rss_db_backup.grid(row=4, column=0)
Rss_db_restore.grid(row=4, column=1)
label_folder.grid(row=4, column=2)

Rss_cf_backup = tk.Button(root, text="Rss_cf Backup", command=lambda: shutil.copyfile(Rss_cf_src, Rss_cf_dst))
Rss_cf_restore = tk.Button(root, text="Rss_cf Restore", command=lambda: shutil.copyfile(Rss_cf_dst, Rss_cf_src))
label_file = tk.Label(root, wraplength=300) ; compare_files(Rss_cf_src, Rss_cf_dst, label_file)

Rss_cf_backup.grid(row=5, column=0)
Rss_cf_restore.grid(row=5, column=1)
label_file.grid(row=5, column=2)


#! ██   ██  ██████  ███    ███  ██████  ██████  ███████ ██████  ██
#! ██  ██  ██    ██ ████  ████ ██    ██ ██   ██ ██      ██   ██ ██
#! █████   ██    ██ ██ ████ ██ ██    ██ ██████  █████   ██████  ██
#! ██  ██  ██    ██ ██  ██  ██ ██    ██ ██   ██ ██      ██   ██ ██
#! ██   ██  ██████  ██      ██  ██████  ██   ██ ███████ ██████  ██


komorebi_backup = tk.Button(root, text="komorebi Backup", command=lambda: shutil.copyfile(komorebi_src, komorebi_dst))
komorebi_restore = tk.Button(root, text="komorebi Restore", command=lambda: shutil.copyfile(komorebi_dst, komorebi_src))
label_file = tk.Label(root, wraplength=300) ; compare_files(komorebi_src, komorebi_dst, label_file)

komorebi_backup.grid(row=6, column=0)
komorebi_restore.grid(row=6, column=1)
label_file.grid(row=6, column=2)

#!  ██████  ██████  ███    ███ ███    ███  █████  ███    ██ ██████      ██   ██ ██ ███████ ████████  ██████  ██████  ██    ██
#! ██      ██    ██ ████  ████ ████  ████ ██   ██ ████   ██ ██   ██     ██   ██ ██ ██         ██    ██    ██ ██   ██  ██  ██
#! ██      ██    ██ ██ ████ ██ ██ ████ ██ ███████ ██ ██  ██ ██   ██     ███████ ██ ███████    ██    ██    ██ ██████    ████
#! ██      ██    ██ ██  ██  ██ ██  ██  ██ ██   ██ ██  ██ ██ ██   ██     ██   ██ ██      ██    ██    ██    ██ ██   ██    ██
#!  ██████  ██████  ██      ██ ██      ██ ██   ██ ██   ████ ██████      ██   ██ ██ ███████    ██     ██████  ██   ██    ██

pwshH_backup = tk.Button(root, text="pwshH Backup", command=lambda: shutil.copyfile(pwshH_src, pwshH_dst))
pwshH_restore = tk.Button(root, text="pwshH Restore", command=lambda: shutil.copyfile(pwshH_dst, pwshH_src))
label_file = tk.Label(root, wraplength=300) ; compare_files(pwshH_src, pwshH_dst, label_file)

pwshH_backup.grid(row=7, column=0)
pwshH_restore.grid(row=7, column=1)
label_file.grid(row=7, column=2)




"""
███████╗ ██████╗ ███╗   ██╗ █████╗ ██████╗ ██████╗
██╔════╝██╔═══██╗████╗  ██║██╔══██╗██╔══██╗██╔══██╗
███████╗██║   ██║██╔██╗ ██║███████║██████╔╝██████╔╝
╚════██║██║   ██║██║╚██╗██║██╔══██║██╔══██╗██╔══██╗
███████║╚██████╔╝██║ ╚████║██║  ██║██║  ██║██║  ██║
╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝
"""

Sr_db_backup = tk.Button(root, text="Sr_db Backup", command=lambda: shutil.copyfile(Sr_db_src, Sr_db_dst))
Sr_db_restore = tk.Button(root, text="Sr_db Restore", command=lambda: shutil.copyfile(Sr_db_dst, Sr_db_src))
label_file = tk.Label(root, wraplength=300) ; compare_files(Sr_db_src, Sr_db_dst, label_file)

Sr_db_backup.grid(row=8, column=0)
Sr_db_restore.grid(row=8, column=1)
label_file.grid(row=8, column=2)

Rr_db_backup = tk.Button(root, text="Rr_db Backup", command=lambda: shutil.copyfile(Rr_db_src, Rr_db_dst))
Rr_db_restore = tk.Button(root, text="Rr_db Restore", command=lambda: shutil.copyfile(Rr_db_dst, Rr_db_src))
label_file = tk.Label(root, wraplength=300) ; compare_files(Rr_db_src, Rr_db_dst, label_file)

Rr_db_backup.grid(row=9, column=0)
Rr_db_restore.grid(row=9, column=1)
label_file.grid(row=9, column=2)

Pr_db_backup = tk.Button(root, text="Pr_db Backup", command=lambda: shutil.copyfile(Pr_db_src, Pr_db_dst))
Pr_db_restore = tk.Button(root, text="Pr_db Restore", command=lambda: shutil.copyfile(Pr_db_dst, Pr_db_src))
label_file = tk.Label(root, wraplength=300) ; compare_files(Pr_db_src, Pr_db_dst, label_file)

Pr_db_backup.grid(row=10, column=0)
Pr_db_restore.grid(row=10, column=1)
label_file.grid(row=10, column=2)








root.mainloop()