import os
from datetime import datetime

from flask import Flask, request, render_template, send_file, redirect, url_for, flash, Response

app = Flask(__name__)
app.secret_key = 'your_secret_key'

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

    return render_template('index.html', directories=directories, files=files, file_times=file_times, current_dir=dir_path, current_drive=drive)

@app.route("/back")
def go_back():
    # Get the current directory and drive
    dir_path = request.args.get('dir_path', 'C:/')
    drive = request.args.get('drive', 'C:/')
    
    # Move to the parent directory
    parent_dir = os.path.abspath(os.path.join(dir_path, os.pardir))
    
    return redirect(url_for('index', dir_path=parent_dir, drive=drive))

@app.route("/download/<path:file_path>")
def download_file(file_path):
    # Serve file for download
    full_file_path = os.path.join(file_path)
    try:
        return send_file(full_file_path, as_attachment=True)
    except Exception as e:
        flash(f"Error downloading file: {e}")
        return redirect(url_for('index', dir_path=os.path.dirname(full_file_path)))

@app.route("/view/<path:file_path>")
def view_file(file_path):
    full_file_path = os.path.join(file_path)

    # Detect file type to open or serve the file in the browser
    if os.path.exists(full_file_path):
        if full_file_path.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            return send_file(full_file_path, mimetype='image/*')
        elif full_file_path.endswith(('.txt', '.py', '.log', '.html', '.css', '.js')):
            return send_file(full_file_path, mimetype='text/plain')
        elif full_file_path.endswith(('.mkv','.mp4', '.webm', '.ogg', '.mp3')):
            return stream_video(full_file_path)  # Stream the video for playing
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
