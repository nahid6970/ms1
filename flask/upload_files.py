import os
from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing messages

# Folder to store files permanently
SHARE_FOLDER = 'C:/sharepoint'
if not os.path.exists(SHARE_FOLDER):
    os.makedirs(SHARE_FOLDER)

app.config['SHARE_FOLDER'] = SHARE_FOLDER

# HTML template for file upload and listing
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>File Sharing</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f4f4f4;
        }
        h1 {
            color: #333;
        }
        form {
            margin-bottom: 20px;
        }
        input[type="file"] {
            padding: 10px;
            font-size: 16px;
        }
        button {
            padding: 10px 15px;
            font-size: 16px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        .file-list {
            margin-top: 20px;
        }
        .file-item {
            margin: 5px 0;
        }
        .download-link {
            color: #007BFF;
            text-decoration: none;
        }
        .download-link:hover {
            text-decoration: underline;
        }
        .clean-button {
            background-color: #FF5733; /* Red color for clean button */
        }
        .clean-button:hover {
            background-color: #C70039;
        }
        .flash {
            color: green;
            font-weight: bold;
            margin-top: 20px;
        }
    </style>
</head>
<body>

    <h1>File Sharing Service</h1>

    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="files" multiple required><br><br>
        <button type="submit">Upload</button>
    </form>

    <form method="POST" action="{{ url_for('clean') }}">
        <button type="submit" class="clean-button">Clean Directory</button>
    </form>

    {% if files %}
    <h2>Shared Files:</h2>
    <div class="file-list">
        {% for file in files %}
        <div class="file-item">
            <a class="download-link" href="{{ url_for('uploaded_file', filename=file) }}">{{ file }}</a>
        </div>
        {% endfor %}
    </div>
    {% endif %}

    {% with messages = get_flashed_messages() %}
      {% if messages %}
        <div class="flash">
          {{ messages[0] }}
        </div>
      {% endif %}
    {% endwith %}

</body>
</html>
'''

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if 'files' in request.files:
            files = request.files.getlist('files')
            for file in files:
                if file.filename == '':
                    flash("No file selected.")
                    continue

                # Secure the filename and define the file path
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['SHARE_FOLDER'], filename)

                # Save file only if it doesn't already exist
                if not os.path.exists(file_path):
                    file.save(file_path)
                    flash(f"File '{filename}' uploaded successfully.")
                else:
                    flash(f"File '{filename}' already exists.")

            return redirect(url_for('index'))

    # List all files in the sharepoint directory
    files = os.listdir(app.config['SHARE_FOLDER'])
    return render_template_string(HTML_TEMPLATE, files=files)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['SHARE_FOLDER'], filename)

@app.route('/clean', methods=["POST"])
def clean():
    # Remove all files in the sharepoint directory
    for filename in os.listdir(app.config['SHARE_FOLDER']):
        file_path = os.path.join(app.config['SHARE_FOLDER'], filename)
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error removing file {file_path}: {e}")

    flash("All files have been successfully deleted.")
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
