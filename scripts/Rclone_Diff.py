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

def show_output(cfg):
    """Prints the output from the log file to the terminal."""
    try:
        with open(cfg["log"], "r") as f:
            print(f"\n--- {cfg['label']} Check Output ---")
            print(f.read())
    except FileNotFoundError:
        print(f"Log file not found for {cfg['label']}!")

def on_label_click(event, cfg):
    """Event handler for clicking a label."""
    show_output(cfg)

def check_and_update(label, cfg):
    """Runs the rclone check and updates the label color."""
    # Run rclone check and dump to log
    with open(cfg["log"], "w") as f:
        subprocess.run(cfg["cmd"], shell=True, stdout=f, stderr=f)

    # Read log and decide label color
    with open(cfg["log"], "r") as f:
        content = f.read()
    if "0 differences found" in content:
        label.config(text=cfg["label"], fg="green")
    else:
        label.config(text=cfg["label"], fg="red")

    # Schedule next check in 10 minutes
    label.after(600000, check_and_update, label, cfg)

def create_gui():
    """Creates the main GUI window."""
    root = tk.Tk()
    root.title("File Sync Checker")

    for key, cfg in commands.items():
        lbl = tk.Label(root, text=cfg["label"], font=("jetbrainsmono nfp", 16), cursor="hand2")
        lbl.pack(padx=20, pady=10, side="left")
        # Bind click event to show the output in the terminal
        lbl.bind("<Button-1>", lambda event, c=cfg: on_label_click(event, c))
        # Start its own loop
        check_and_update(lbl, cfg)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
