import time
import os
import datetime
import pyperclip

# Log file path
log_file = r"C:\msBackups\@JOB\copy_pasta.txt"
separator = "-----x-----"

# Make sure directory exists
os.makedirs(os.path.dirname(log_file), exist_ok=True)

# Store last copied content
last_text = ""

def log_clipboard(text):
    """Append the copied text with timestamp to the file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
    normalized_text = text.replace("\r\n", "\n").rstrip("\n")

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"{timestamp}\n{normalized_text}\n{separator}\n")

if __name__ == "__main__":
    print("Clipboard logger started. Press Ctrl+C to stop.")

    while True:
        try:
            current_text = pyperclip.paste()
            if current_text and current_text != last_text:
                last_text = current_text
                log_clipboard(current_text)
        except Exception as e:
            print("Error accessing clipboard:", e)
        time.sleep(0.5)  # check every 1 second
