import time
import subprocess
from pathlib import Path
from difflib import unified_diff
from plyer import notification
import re
import tkinter as tk
from tkinter import messagebox

# Commands for 'software' and 'song'
LOCAL_CMD_SOFTWARE = 'rclone ls D:/software --fast-list > C:/test/software_local.log'
CLOUD_CMD_SOFTWARE = 'rclone ls gu:/software --fast-list > C:/test/software_cloud.log'

LOCAL_CMD_SONG = 'rclone ls D:/song --fast-list > C:/test/song_local.log'
CLOUD_CMD_SONG = 'rclone ls gu:/song --fast-list > C:/test/song_cloud.log'

# Log file paths
LOCAL_LOG_SOFTWARE = Path("C:/test/software_local.log")
CLOUD_LOG_SOFTWARE = Path("C:/test/software_cloud.log")

LOCAL_LOG_SONG = Path("C:/test/song_local.log")
CLOUD_LOG_SONG = Path("C:/test/song_cloud.log")

def run_rclone_commands():
    try:
        subprocess.run(LOCAL_CMD_SOFTWARE, shell=True, stderr=subprocess.DEVNULL)
        subprocess.run(CLOUD_CMD_SOFTWARE, shell=True, stderr=subprocess.DEVNULL)
        subprocess.run(LOCAL_CMD_SONG, shell=True, stderr=subprocess.DEVNULL)
        subprocess.run(CLOUD_CMD_SONG, shell=True, stderr=subprocess.DEVNULL)
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

def compare_logs(local_log, cloud_log):
    local_lines = clean_lines(read_file_lines(local_log))
    cloud_lines = clean_lines(read_file_lines(cloud_log))

    # Generate differences
    diff = list(unified_diff(local_lines, cloud_lines, fromfile='local', tofile='cloud'))
    return diff

def notify_user(message):
    notification.notify(
        title="Sync Difference Detected",
        message=message,
        timeout=10
    )

def update_label(label, differences_found, category, diff_data):
    if differences_found:
        label.config(text=f"{category} - Differences found!", fg="red")
        label.bind("<Button-1>", lambda event: show_differences(diff_data))  # Show differences on click
    else:
        label.config(text=f"{category} - No differences detected", fg="green")
        label.unbind("<Button-1>")  # Unbind click event if no differences

def show_differences(diff_data):
    print("Differences found in the files (displayed serially):\n")
    for idx, line in enumerate(diff_data, 1):
        print(f"{idx}. {line}")
    print("\nEnd of Differences.")

def run_check(label_software, label_song):
    run_rclone_commands()

    # Check for differences in 'software' and 'song'
    differences_software = compare_logs(LOCAL_LOG_SOFTWARE, CLOUD_LOG_SOFTWARE)
    differences_song = compare_logs(LOCAL_LOG_SONG, CLOUD_LOG_SONG)

    if differences_software:
        notify_user("Differences found in 'software' files.")
    update_label(label_software, bool(differences_software), "Software", differences_software)

    if differences_song:
        notify_user("Differences found in 'song' files.")
    update_label(label_song, bool(differences_song), "Song", differences_song)

    # Run the check again in 10 minutes
    label_software.after(600000, run_check, label_software, label_song)

def create_gui():
    root = tk.Tk()
    root.title("File Sync Checker")

    # Labels for 'software' and 'song'
    label_software = tk.Label(root, text="Software - Checking...", font=("Helvetica", 16))
    label_software.pack(padx=20, pady=20)

    label_song = tk.Label(root, text="Song - Checking...", font=("Helvetica", 16))
    label_song.pack(padx=20, pady=20)

    # Start checking when the GUI is loaded
    run_check(label_software, label_song)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
