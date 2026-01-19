import os
import datetime
from flask import Flask, render_template, request, redirect, url_for
import pyperclip


app = Flask(__name__)

# Updated log file path and separator
log_file = "C:/@delta/db/shared_text/Shared_Text.log"
separator = "-----x-----"

def write_to_log(text):
    """Write the shared text to the log file with a timestamp and copy to clipboard."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
    normalized_text = text.replace("\r\n", "\n").rstrip("\n")

    # Copy to clipboard
    try:
        pyperclip.copy(normalized_text)
    except Exception as e:
        print("Clipboard copy failed:", e)

    # Write to file
    with open(log_file, "a", encoding="utf-8") as file:
        file.write(f"{timestamp}\n{normalized_text}\n{separator}\n")


def read_logs():
    """Read the log file and return logs as a list of (timestamp, text) tuples."""
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as file:
            content = file.read().strip()
        if content:
            entries = content.split(f"\n{separator}\n")
            logs = []
            for i, entry in enumerate(reversed(entries)):
                parts = entry.split("\n", 1)
                if len(parts) == 2:
                    text = parts[1].strip()
                    # Remove separator from the last entry (most recent) if present
                    if i == 0 and text.endswith(separator):
                        text = text[: -len(separator)].strip()
                    logs.append((parts[0], text))
            return logs
    return []

def delete_log_entry(index_to_delete):
    """Deletes a specific log entry based on its index (0-based, from the most recent)."""
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as file:
            content = file.read().strip()
        if content:
            entries = content.split(f"\n{separator}\n")
            
            # Since we display logs in reverse order (newest first), we need to adjust the index
            # to match the original file order (oldest first).
            original_index = len(entries) - 1 - index_to_delete
            
            if 0 <= original_index < len(entries):
                del entries[original_index]
                with open(log_file, "w", encoding="utf-8") as file:
                    file.write(f"\n{separator}\n".join(entries))
                    if entries: # Ensure a trailing separator if there are still entries
                        file.write(f"\n{separator}\n")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Handle text submission
        shared_text = request.form.get("text", "")
        if shared_text:
            write_to_log(shared_text)
        return redirect(url_for('index'))
    
    logs = read_logs()
    return render_template("index.html", logs=logs)

@app.route("/clean", methods=["POST"])
def clean_logs():
    """Clean the log file completely."""
    if os.path.exists(log_file):
        with open(log_file, "w", encoding="utf-8") as file:
            file.write("")
    return redirect(url_for('index'))

@app.route("/delete/<int:index>", methods=["POST"])
def delete_entry(index):
    """Route to handle deleting a single log entry."""
    delete_log_entry(index)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)