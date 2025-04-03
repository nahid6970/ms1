import os
from datetime import datetime
from flask import Flask, request, render_template, send_file, redirect, url_for, flash, Response

app = Flask(__name__)
app.secret_key = 'your_secret_key'

EDITABLE_EXTENSIONS = (".py", ".ps1", ".txt", ".log", ".html", ".css")

@app.route("/", methods=["GET", "POST"])
def index():
    drive = request.args.get('drive', 'C:/')
    dir_path = request.args.get('dir_path', drive)

    try:
        directories = [d for d in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, d))]
        files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
        file_times = {
            f: datetime.fromtimestamp(os.path.getmtime(os.path.join(dir_path, f))).strftime("%d/%m/%Y %I:%M%p").replace("AM", "am").replace("PM", "pm")
            for f in files
        }
    except Exception as e:
        flash(f"Error accessing directory: {e}")
        directories, files, file_times = [], [], {}

    return render_template('index.html', directories=directories, files=files, file_times=file_times, current_dir=dir_path, current_drive=drive, editable_extensions=EDITABLE_EXTENSIONS)

@app.route("/edit/<path:file_path>", methods=["GET", "POST"])
def edit_file(file_path):
    full_file_path = os.path.join(file_path)

    if not os.path.exists(full_file_path):
        flash("File not found")
        return redirect(url_for('index', dir_path=os.path.dirname(full_file_path)))

    if request.method == "POST":
        new_content = request.form.get("file_content")
        try:
            with open(full_file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            flash("File saved successfully")
        except Exception as e:
            flash(f"Error saving file: {e}")

        return redirect(url_for("index", dir_path=os.path.dirname(full_file_path)))

    try:
        with open(full_file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        flash(f"Error reading file: {e}")
        content = ""

    return render_template("edit.html", file_path=file_path, content=content)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
