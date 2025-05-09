import subprocess
from plyer import notification
import tkinter as tk
import os

# Commands for 'software' and 'song'
CHECK_CMD_SOFTWARE = 'rclone check D:/software gu:/software --fast-list --size-only'
CHECK_CMD_SONG = 'rclone check D:/song gu:/song --fast-list --size-only'

# Log file paths for 'software' and 'song'
LOG_FILE_SOFTWARE = 'C:/test/software_check.log'
LOG_FILE_SONG = 'C:/test/song_check.log'

def run_rclone_check(command, log_file):
    try:
        # Run the rclone check command and redirect the output to a log file
        with open(log_file, 'w') as f:
            result = subprocess.run(command, shell=True, stdout=f, stderr=f)
        return result.returncode  # Return 0 if successful
    except Exception as e:
        print(f"Error running rclone check: {e}")
        return 1  # Return non-zero if an error occurs

def check_for_differences(log_file):
    try:
        # Read the log file to check if it contains "0 differences found"
        with open(log_file, 'r') as f:
            log_content = f.read()
            if "0 differences found" in log_content:
                return False  # No differences found
            else:
                return True  # Differences found
    except Exception as e:
        print(f"Error reading log file: {e}")
        return False  # Default to no differences if the file can't be read

def notify_user(message):
    notification.notify(
        title="Sync Difference Detected",
        message=message,
        timeout=10
    )

def update_label(label, differences_found, no_diff_message, diff_message):
    if differences_found:
        label.config(text=diff_message, fg="red")  # Show the "differences" message in red
    else:
        label.config(text=no_diff_message, fg="green")  # Show the "no differences" message in green

def run_check(label_software, label_song):
    # Define your custom messages
    software_message_no_diff = "Software files are synced!"
    software_message_diff = "Software files have differences!"
    
    song_message_no_diff = "\uec1b!"
    song_message_diff = "\uec1b!"
    
    # Run the check for both 'software' and 'song', saving outputs to log files
    run_rclone_check(CHECK_CMD_SOFTWARE, LOG_FILE_SOFTWARE)
    run_rclone_check(CHECK_CMD_SONG, LOG_FILE_SONG)

    # Check for differences in the log files
    differences_software = check_for_differences(LOG_FILE_SOFTWARE)
    differences_song = check_for_differences(LOG_FILE_SONG)

    # Notify and update labels with customized messages
    if differences_software:
        notify_user(software_message_diff)  # Custom message for differences in software
    else:
        notify_user(software_message_no_diff)  # Custom message for no differences in software
    update_label(label_software, differences_software, software_message_no_diff, software_message_diff)

    if differences_song:
        notify_user(song_message_diff)  # Custom message for differences in song
    else:
        notify_user(song_message_no_diff)  # Custom message for no differences in song
    update_label(label_song, differences_song, song_message_no_diff, song_message_diff)

    # Run the check again in 10 minutes
    label_software.after(600000, run_check, label_software, label_song)

def create_gui():
    root = tk.Tk()
    root.title("File Sync Checker")

    # Labels for 'software' and 'song'
    label_software = tk.Label(root, text="Software - Checking...", font=("Helvetica", 16))
    label_software.pack(padx=20, pady=20)

    label_song = tk.Label(root, text="Song - Checking...", font=("jetbrainsmono nfp", 16))
    label_song.pack(padx=20, pady=20)

    # Start checking when the GUI is loaded
    run_check(label_software, label_song)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
