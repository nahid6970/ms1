import os
import datetime
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Updated log file path and separator
log_file = "C:/msBackups/Shared_Text.log"
separator = "-----x-----"

def write_to_log(text):
    """Write the shared text to the log file with a timestamp."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
    # Normalize Windows-style line endings to Unix-style and remove any trailing newline
    normalized_text = text.replace("\r\n", "\n").rstrip("\n")
    with open(log_file, "a", encoding="utf-8") as file:
        file.write(f"{timestamp}\n{normalized_text}\n{separator}\n")


def read_logs():
    """Read the log file and return logs as a list of (timestamp, text) tuples."""
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as file:
            content = file.read().strip()
        if content:
            # Split entries using the new separator
            entries = content.split(f"\n{separator}\n")
            logs = []
            # Reverse the order to display the most recent first
            for entry in reversed(entries):
                parts = entry.split("\n", 1)
                if len(parts) == 2:
                    logs.append((parts[0], parts[1].strip()))
            return logs
    return []

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get the text from the textarea
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
