import subprocess
import tkinter as tk

# Commands and log file paths
commands = {
    "software": {
        "cmd":  "rclone check D:/software gu:/software --fast-list --size-only",
        "log":  "C:/test/software_check.log",
        "label": "\uf40e"
    },
    "song": {
        "cmd":  "rclone check D:/song gu:/song --fast-list --size-only",
        "log":  "C:/test/song_check.log",
        "label": "\uec1b"
    }
}

def check_and_update(label, cfg):
    # run rclone check and dump to log
    with open(cfg["log"], "w") as f:
        subprocess.run(cfg["cmd"], shell=True, stdout=f, stderr=f)

    # read log and decide
    with open(cfg["log"], "r") as f:
        content = f.read()
    if "0 differences found" in content:
        label.config(text=cfg["label"], fg="green")
    else:
        label.config(text=cfg["label"], fg="red")

    # schedule next check in 10 minutes
    label.after(600_000, check_and_update, label, cfg)

def create_gui():
    root = tk.Tk()
    root.title("File Sync Checker")

    for key, cfg in commands.items():
        lbl = tk.Label(root, text=cfg["label"], font=("Jetbrainsmono nfp", 16))
        lbl.pack(padx=20, pady=10)
        # start its own loop
        check_and_update(lbl, cfg)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
