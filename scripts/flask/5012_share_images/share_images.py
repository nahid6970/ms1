import os
import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort
from werkzeug.utils import secure_filename
import json
import glob

app = Flask(__name__)

# Configuration for image uploads
UPLOAD_FOLDER = 'C:/Users/nahid/ms/msBackups/Shared_Images' # Make sure this directory exists or create it
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
METADATA_FILE = os.path.join(UPLOAD_FOLDER, 'images_metadata.json') # File to store image metadata

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create the upload directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    """Checks if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_images_from_folder(folder_path):
    """Recursively gets all image files from a folder and its subfolders."""
    image_files = []
    for ext in ALLOWED_EXTENSIONS:
        # Search recursively for each extension
        pattern = os.path.join(folder_path, '**', f'*.{ext}')
        image_files.extend(glob.glob(pattern, recursive=True))
        # Also search for uppercase extensions
        pattern = os.path.join(folder_path, '**', f'*.{ext.upper()}')
        image_files.extend(glob.glob(pattern, recursive=True))
    return image_files

def process_uploaded_file(file, metadata):
    """Process a single uploaded file and add to metadata."""
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # Handle duplicate filenames: append a number
    counter = 1
    original_filename_no_ext, ext = os.path.splitext(filename)
    while os.path.exists(filepath):
        filename = f"{original_filename_no_ext}_{counter}{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        counter += 1

    file.save(filepath)

    # Add metadata
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
    metadata.append({
        "filename": filename,
        "timestamp": timestamp,
        "filepath": filepath
    })
    return filename

def copy_file_to_upload_folder(source_path, metadata):
    """Copy a file from source path to upload folder and add to metadata."""
    filename = secure_filename(os.path.basename(source_path))
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # Handle duplicate filenames: append a number
    counter = 1
    original_filename_no_ext, ext = os.path.splitext(filename)
    while os.path.exists(filepath):
        filename = f"{original_filename_no_ext}_{counter}{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        counter += 1

    # Copy the file
    import shutil
    shutil.copy2(source_path, filepath)

    # Add metadata
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
    metadata.append({
        "filename": filename,
        "timestamp": timestamp,
        "filepath": filepath
    })
    return filename

def load_image_metadata():
    """Loads image metadata from the JSON file."""
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return [] # Return empty list if JSON is malformed
    return []

def save_image_metadata(metadata):
    """Saves image metadata to the JSON file."""
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=4)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        metadata = load_image_metadata()
        uploaded_count = 0

        # Handle multiple file uploads
        if 'files' in request.files:
            files = request.files.getlist('files')
            for file in files:
                if file and file.filename != '' and allowed_file(file.filename):
                    process_uploaded_file(file, metadata)
                    uploaded_count += 1

        # Handle folder selection (via folder_path form field)
        if 'folder_path' in request.form and request.form['folder_path']:
            folder_path = request.form['folder_path']
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                image_files = get_images_from_folder(folder_path)
                for image_path in image_files:
                    try:
                        copy_file_to_upload_folder(image_path, metadata)
                        uploaded_count += 1
                    except Exception as e:
                        print(f"Error copying {image_path}: {e}")

        if uploaded_count > 0:
            save_image_metadata(metadata)
        
        return redirect(url_for('index'))

    # Display images
    images_data = load_image_metadata()
    # Reverse the order to display newest first
    images_data.reverse()
    return render_template("image_index.html", images=images_data)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/delete_image/<string:filename>", methods=["POST"])
def delete_image(filename):
    """Deletes a specific image and its metadata."""
    metadata = load_image_metadata()
    updated_metadata = []
    file_deleted = False

    for item in metadata:
        if item['filename'] == filename:
            try:
                os.remove(item['filepath']) # Delete the actual image file
                file_deleted = True
            except OSError as e:
                print(f"Error deleting file {item['filepath']}: {e}")
        else:
            updated_metadata.append(item)

    if file_deleted:
        save_image_metadata(updated_metadata)
    
    return redirect(url_for('index'))

@app.route("/clean_all_images", methods=["POST"])
def clean_all_images():
    """Deletes all uploaded images and clears metadata."""
    metadata = load_image_metadata()
    for item in metadata:
        try:
            os.remove(item['filepath'])
        except OSError as e:
            print(f"Error deleting file {item['filepath']}: {e}")
    
    # Clear all metadata
    save_image_metadata([])
    
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5012, debug=True) # Changed port to 5002 to avoid conflict with text app