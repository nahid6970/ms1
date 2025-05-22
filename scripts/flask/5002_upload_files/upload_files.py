import os
from flask import Flask, request, send_from_directory, redirect, url_for, flash, render_template_string
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing messages

# Folder to store files permanently
SHARE_FOLDER = 'C:/sharepoint'
if not os.path.exists(SHARE_FOLDER):
    os.makedirs(SHARE_FOLDER)

app.config['SHARE_FOLDER'] = SHARE_FOLDER

# HTML template within the Python file (instead of an external index.html)
html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <link rel="shortcut icon" href="https://cdn-icons-png.flaticon.com/512/2840/2840124.png" type="image/x-icon">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>File Sharing with Circular Progress</title>
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
        .button-container {
            display: flex;
            gap: 10px;
            margin-top: 10px;
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
        .clean-button {
            background-color: #FF5733; /* Red color for clean button */
        }
        .clean-button:hover {
            background-color: #C70039;
        }
        .circular-progress {
            position: relative;
            width: 120px;
            height: 120px;
            border-radius: 50%;
            background: conic-gradient(#4CAF50 0%, #ccc 0%);
            margin-bottom: 20px; /* Added margin for better spacing */
        }
        .progress-percentage {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 24px;
            font-weight: bold;
            color: #333;
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
        .flash {
            color: green;
            font-weight: bold;
            margin-top: 20px;
        }
    </style>
</head>
<body>

    <h1>File Sharing with Circular Progress</h1>

    <form id="upload-form">
        <input type="file" id="file-input" name="files" multiple required><br><br>

        <div class="button-container">
            <button type="submit">Upload</button>
        </div>
    </form>

    <form id="clean-form" method="POST" action="/clean">
        <div class="button-container">
            <button type="submit" class="clean-button">Clean Directory</button>
        </div>
    </form>

    <div class="circular-progress" id="circular-progress">
        <div class="progress-percentage" id="progress-percentage">0%</div>
    </div>
    
    <div id="upload-status"></div> <div class="file-list">
        {% for file in files %}
            <div class="file-item">
                <a class="download-link" href="/uploads/{{ file }}">{{ file }}</a>
            </div>
        {% endfor %}
    </div>

    <script>
        document.getElementById("upload-form").addEventListener("submit", async function(event) {
            event.preventDefault();

            var files = document.getElementById("file-input").files;
            var totalFiles = files.length;
            var uploadedFilesCount = 0;
            var uploadStatusDiv = document.getElementById("upload-status");

            for (var i = 0; i < totalFiles; i++) {
                var file = files[i];
                var formData = new FormData();
                formData.append("file", file); // Changed 'files' to 'file' as we are sending one at a time

                await new Promise((resolve, reject) => {
                    var xhr = new XMLHttpRequest();
                    xhr.open("POST", "/", true);

                    xhr.upload.onprogress = function(event) {
                        if (event.lengthComputable) {
                            var percentComplete = (event.loaded / event.total) * 100;
                            var progressCircle = document.getElementById("circular-progress");
                            var progressText = document.getElementById("progress-percentage");

                            // Update circular progress based on overall progress
                            var overallProgress = ((uploadedFilesCount * 100) + percentComplete) / totalFiles;
                            progressCircle.style.background = 'conic-gradient(#4CAF50 ' + overallProgress + '%, #ccc ' + overallProgress + '%)';
                            progressText.innerText = Math.round(overallProgress) + "%";

                            uploadStatusDiv.innerHTML = `<p>Uploading ${file.name}: ${Math.round(percentComplete)}%</p>`;
                        }
                    };

                    xhr.onload = function() {
                        if (xhr.status === 200) {
                            uploadedFilesCount++;
                            uploadStatusDiv.innerHTML = `<p>${file.name} uploaded successfully!</p>`;
                            if (uploadedFilesCount === totalFiles) {
                                window.location.reload(); // Refresh after all files are uploaded
                            }
                            resolve();
                        } else {
                            uploadStatusDiv.innerHTML = `<p>Error uploading ${file.name}!</p>`;
                            alert("Error uploading " + file.name + "!");
                            reject();
                        }
                    };

                    xhr.onerror = function() {
                        uploadStatusDiv.innerHTML = `<p>Network error during upload of ${file.name}.</p>`;
                        reject();
                    };

                    xhr.send(formData);
                });
            }
        });
    </script>

</body>
</html>
'''

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # In the modified client-side, we expect a single 'file' now
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                flash("No file selected.")
                return '', 400 # Bad request if no file is selected

            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['SHARE_FOLDER'], filename)

            if not os.path.exists(file_path):
                file.save(file_path)
                flash(f"File '{filename}' uploaded successfully.")
            else:
                flash(f"File '{filename}' already exists.")

            return '', 200  # Return a success response to the client
        else:
            flash("No file part in the request.")
            return '', 400

    files = os.listdir(app.config['SHARE_FOLDER'])
    return render_template_string(html_template, files=files)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['SHARE_FOLDER'], filename)

@app.route('/clean', methods=["POST"])
def clean():
    for filename in os.listdir(app.config['SHARE_FOLDER']):
        file_path = os.path.join(app.config['SHARE_FOLDER'], filename)
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error removing file {file_path}: {e}")

    flash("All files have been successfully deleted.")
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)