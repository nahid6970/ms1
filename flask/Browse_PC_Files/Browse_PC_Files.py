import os
from datetime import datetime
from flask import Flask, request, render_template, send_file, redirect, url_for, flash, Response

app = Flask(__name__)
app.secret_key = 'your_secret_key'

EDITABLE_EXTENSIONS = (".py", ".ps1", ".txt", ".log", ".html", ".css", ".ahk", ".md")

def format_size(bytes_size):
    """Convert file size to human-readable format (KB, MB, GB)."""
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 ** 2:
        return f"{bytes_size / 1024:.2f} KB"
    elif bytes_size < 1024 ** 3:
        return f"{bytes_size / (1024 ** 2):.2f} MB"
    else:
        return f"{bytes_size / (1024 ** 3):.2f} GB"

def get_size(path):
    """Return the formatted size of a file."""
    if os.path.isfile(path):
        return format_size(os.path.getsize(path))
    return "0 B"

@app.route("/", methods=["GET", "POST"])
def index():
    drive = request.args.get('drive', 'C:/')
    dir_path = request.args.get('dir_path', drive)

    try:
        directories = [d for d in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, d))]
        files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]

        file_times = {
            f: datetime.fromtimestamp(os.path.getmtime(os.path.join(dir_path, f)))
            .strftime("%d/%m/%Y %I:%M%p")
            .replace("AM", "am")
            .replace("PM", "pm")
            for f in files
        }
        file_sizes = {
            f: get_size(os.path.join(dir_path, f)) for f in files
        }
    except Exception as e:
        flash(f"Error accessing directory: {e}")
        directories, files, file_times, file_sizes = [], [], {}, {}

    return render_template('index.html',
                           directories=directories,
                           files=files,
                           file_times=file_times,
                           file_sizes=file_sizes,
                           current_dir=dir_path,
                           current_drive=drive,
                           editable_extensions=EDITABLE_EXTENSIONS)

@app.route("/view/<path:file_path>")
def view_file(file_path):
    full_file_path = os.path.join(file_path)
    # Detect file type to open or serve the file in the browser
    if os.path.exists(full_file_path):
        if full_file_path.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            # Open the image and serve it directly
            with open(full_file_path, 'rb') as image_file:
                image_data = image_file.read()
                return Response(image_data, mimetype='image/jpeg')  # Update mimetype based on actual file extension
        elif full_file_path.endswith(('.txt', '.py', '.ps1', '.log', 'opml', 'ini', '.html', '.css', '.js')):
            return send_file(full_file_path, mimetype='text/plain')
        elif full_file_path.endswith(('.mkv','.mp4', '.webm', '.ogg', '.mp3')):
            return stream_video(full_file_path)  # Stream the video for playing
        elif full_file_path.endswith('.pdf'):
            return send_file(full_file_path, mimetype='application/pdf')  # Serve PDF files
        else:
            flash("File type is not supported for direct viewing")
            return redirect(url_for('index', dir_path=os.path.dirname(full_file_path)))
    else:
        flash("File not found")
        return redirect(url_for('index', dir_path=os.path.dirname(full_file_path)))

def stream_video(file_path):
    """Stream video files for playing in the browser."""
    def generate():
        with open(file_path, 'rb') as video:
            data = video.read(1024)
            while data:
                yield data
                data = video.read(1024)
    return Response(generate(), mimetype="video/mp4")

@app.route("/download/<path:file_path>")
def download_file(file_path):
    full_file_path = os.path.join(file_path)
    try:
        return send_file(full_file_path, as_attachment=True)
    except Exception as e:
        flash(f"Error downloading file: {e}")
        return redirect(url_for('index', dir_path=os.path.dirname(full_file_path)))

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

@app.route("/back")
def go_back():
    # Get the current directory and drive
    dir_path = request.args.get('dir_path', 'C:/')
    drive = request.args.get('drive', 'C:/')
    
    # Move to the parent directory
    parent_dir = os.path.abspath(os.path.join(dir_path, os.pardir))
    
    return redirect(url_for('index', dir_path=parent_dir, drive=drive))

@app.route("/files/<path:dir_path>")
def list_files(dir_path):
    files = []
    file_times = {}  # Add logic for file times

    # List files in the directory
    for file_name in os.listdir(dir_path):
        full_path = os.path.join(dir_path, file_name)
        if os.path.isfile(full_path):
            files.append(file_name)
            # Add logic to populate file_times

    return render_template("file_list.html", files=files, file_times=file_times, current_dir=dir_path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
