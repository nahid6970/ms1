import os
import datetime
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
log_file = "C:/Users/nahid/nahidna.log"

def write_to_log(text):
    """Write the shared text to the log file with a timestamp."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")  # 12-hour format with AM/PM
    with open(log_file, "a", encoding="utf-8") as file:
        file.write(f"{timestamp}\n{text.strip()}\n---\n")  # Use "---" as a separator

def read_logs():
    """Read the log file and return logs as a list of (timestamp, text) tuples."""
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as file:
            content = file.read().strip()
        entries = content.split("\n---\n")  # Split logs by "---"
        logs = []
        for entry in reversed(entries):  # Reverse to show the latest first
            parts = entry.split("\n", 1)  # Split into timestamp and text
            if len(parts) == 2:
                logs.append((parts[0], parts[1]))  # (timestamp, text)
        return logs
    return []

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        shared_text = request.form["text"]
        write_to_log(shared_text)
        return redirect(url_for('index'))  # Redirect to avoid duplicate submissions

    logs = read_logs()
    return render_template("index.html", logs=logs)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
