import time
import subprocess
from pathlib import Path
from difflib import unified_diff
from plyer import notification
import re
import tkinter as tk

LOCAL_CMD = 'rclone ls D:/software --fast-list > C:/test/software_local.log'
CLOUD_CMD = 'rclone ls gu:/software --fast-list > C:/test/software_cloud.log'
LOCAL_LOG = Path("C:/test/software_local.log")
CLOUD_LOG = Path("C:/test/software_cloud.log")

def run_rclone_commands():
    try:
        subprocess.run(LOCAL_CMD, shell=True, stderr=subprocess.DEVNULL)
        subprocess.run(CLOUD_CMD, shell=True, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Error running rclone commands: {e}")

def clean_lines(lines):
    # Remove leading numbers and spaces
    cleaned = [re.sub(r'^\s*\d+\s+', '', line) for line in lines if line.strip()]
    return sorted(cleaned)

def read_file_lines(filepath):
    if filepath.exists():
        return filepath.read_text(encoding='utf-8').splitlines()
    return []

def compare_logs():
    local_lines = clean_lines(read_file_lines(LOCAL_LOG))
    cloud_lines = clean_lines(read_file_lines(CLOUD_LOG))

    # Generate differences
    diff = list(unified_diff(local_lines, cloud_lines, fromfile='local', tofile='cloud'))
    return diff

def notify_user(message):
    notification.notify(
        title="Sync Difference Detected",
        message=message,
        timeout=10
    )

def update_label(label, differences_found):
    if differences_found:
        label.config(text="Software - Differences found!", fg="red")
    else:
        label.config(text="Software - No differences detected", fg="green")

def run_check(label):
    run_rclone_commands()
    differences = compare_logs()

    if differences:
        notify_user("Differences found between local and cloud files.")
    update_label(label, bool(differences))

    # Run the check again in 10 minutes
    label.after(600000, run_check, label)

def create_gui():
    root = tk.Tk()
    root.title("File Sync Checker")

    label = tk.Label(root, text="Software - Checking...", font=("Helvetica", 16))
    label.pack(padx=20, pady=20)

    # Start checking when the GUI is loaded
    run_check(label)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
