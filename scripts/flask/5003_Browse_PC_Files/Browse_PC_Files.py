import os
import json
from datetime import datetime
from flask import Flask, request, render_template, send_file, redirect, url_for, flash, Response
from flask import jsonify
import zipfile
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'

BOOKMARKS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bookmarks.json')
MOVE_FOLDERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'move_folders.json')

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

def get_file_icon(filename):
    """Return appropriate icon based on file extension."""
    ext = filename.lower().split('.')[-1] if '.' in filename else ''
    
    # Image files
    if ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp', 'ico']:
        return '🖼️'
    
    # Video files
    elif ext in ['mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv', 'webm', 'm4v']:
        return '🎬'
    
    # Audio files
    elif ext in ['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a', 'wma']:
        return '🎵'
    
    # Document files
    elif ext in ['pdf']:
        return '📄'
    elif ext in ['doc', 'docx']:
        return '📝'
    elif ext in ['xls', 'xlsx']:
        return '📊'
    elif ext in ['ppt', 'pptx']:
        return '📋'
    
    # Code files
    elif ext in ['py']:
        return '🐍'
    elif ext in ['js']:
        return '🟨'
    elif ext in ['html', 'htm']:
        return '🌐'
    elif ext in ['css']:
        return '🎨'
    elif ext in ['json']:
        return '📋'
    elif ext in ['xml']:
        return '📄'
    elif ext in ['sql']:
        return '🗃️'
    
    # Script files
    elif ext in ['ps1']:
        return '💙'
    elif ext in ['ahk']:
        return '⚙️'
    elif ext in ['bat', 'cmd']:
        return '⚫'
    elif ext in ['sh']:
        return '🐚'
    
    # Archive files
    elif ext in ['zip', 'rar', '7z', 'tar', 'gz', 'bz2']:
        return '📦'
    elif ext in ['iso']:
        return '💿'
    
    # Executable files
    elif ext in ['exe', 'msi']:
        return '⚙️'
    elif ext in ['apk']:
        return '📱'
    
    # Text files
    elif ext in ['txt', 'md', 'log', 'ini', 'cfg', 'conf']:
        return '📃'
    
    # Binary/Unknown files
    else:
        return '📄'

def load_bookmarks():
    """Load bookmarks from JSON file."""
    try:
        if os.path.exists(BOOKMARKS_FILE):
            with open(BOOKMARKS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading bookmarks: {e}")
    return []

def save_bookmarks(bookmarks):
    """Save bookmarks to JSON file."""
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(BOOKMARKS_FILE), exist_ok=True)
        
        with open(BOOKMARKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(bookmarks, f, indent=2, ensure_ascii=False)
        print(f"Bookmarks saved successfully to {BOOKMARKS_FILE}")
        return True
    except Exception as e:
        print(f"Error saving bookmarks to {BOOKMARKS_FILE}: {e}")
        return False

def load_move_folders():
    """Load move folders from JSON file."""
    try:
        if os.path.exists(MOVE_FOLDERS_FILE):
            with open(MOVE_FOLDERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading move folders: {e}")
    return []

def save_move_folders(move_folders):
    """Save move folders to JSON file."""
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(MOVE_FOLDERS_FILE), exist_ok=True)
        
        with open(MOVE_FOLDERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(move_folders, f, indent=2, ensure_ascii=False)
        print(f"Move folders saved successfully to {MOVE_FOLDERS_FILE}")
        return True
    except Exception as e:
        print(f"Error saving move folders to {MOVE_FOLDERS_FILE}: {e}")
        return False

@app.route('/update_move_folder_color', methods=['POST'])
def update_move_folder_color():
    """Update the color of a move folder."""
    data = request.get_json()
    path = data.get('path', '').strip()
    bg_color = data.get('bg_color', '#444').strip()
    text_color = data.get('text_color', '#ffffff').strip()
    hover_bg_color = data.get('hover_bg_color', '#FF9800').strip()
    hover_text_color = data.get('hover_text_color', '#000000').strip()
    
    if not path:
        return jsonify({"error": "Path is required"}), 400
    
    # Normalize the path
    normalized_path = os.path.normpath(path).replace('\\', '/')
    
    move_folders = load_move_folders()
    
    # Find and update the folder
    folder_found = False
    for folder in move_folders:
        folder_normalized = os.path.normpath(folder['path']).replace('\\', '/')
        if folder_normalized == normalized_path:
            folder['bg_color'] = bg_color
            folder['text_color'] = text_color
            folder['hover_bg_color'] = hover_bg_color
            folder['hover_text_color'] = hover_text_color
            folder_found = True
            break
    
    if not folder_found:
        return jsonify({"error": "Move folder not found"}), 404
    
    if save_move_folders(move_folders):
        return jsonify({"success": "Folder color updated successfully"}), 200
    else:
        return jsonify({"error": "Failed to update folder color"}), 500

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
        file_icons = {
            f: get_file_icon(f) for f in files
        }
    except Exception as e:
        flash(f"Error accessing directory: {e}")
        directories, files, file_times, file_sizes, file_icons = [], [], {}, {}, {}

    bookmarks = load_bookmarks()
    
    return render_template('index.html',
                           directories=directories,
                           files=files,
                           file_times=file_times,
                           file_sizes=file_sizes,
                           file_icons=file_icons,
                           bookmarks=bookmarks,
                           current_dir=dir_path,
                           current_drive=drive,
                           editable_extensions=EDITABLE_EXTENSIONS)

@app.route("/view/<path:file_path>")
def view_file(file_path):
    full_file_path = os.path.join(file_path)
    # Detect file type to open or serve the file in the browser
    if os.path.exists(full_file_path):
        if full_file_path.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp', '.ico')):
            # Redirect to image gallery viewer
            directory = os.path.dirname(full_file_path)
            filename = os.path.basename(full_file_path)
            return redirect(url_for('image_gallery', dir_path=directory, filename=filename))
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



# Assuming you're using Flask and have a directory for files
import os
from flask import request, redirect, url_for, flash

@app.route('/rename/<path:current_dir>/<file_name>', methods=['GET'])
def rename_file(current_dir, file_name):
    new_name = request.args.get('new_name')
    if not new_name:
        return "New file name is required", 400

    old_file_path = os.path.join(current_dir, file_name)
    new_file_path = os.path.join(current_dir, new_name)

    if os.path.exists(new_file_path):
        return "File with this name already exists", 400

    try:
        os.rename(old_file_path, new_file_path)
        
        # Return a meta-refresh response to reload the page
        return '''
        <html>
        <head><meta http-equiv="refresh" content="0;url=/list/''' + current_dir + '''"></head>
        <body>Renaming successful! Redirecting...</body>
        </html>
        '''
    except FileNotFoundError:
        return f"Error: File not found: {old_file_path}", 404
    except Exception as e:
        return f"Error renaming file: {e}", 500



@app.route('/delete/<path:current_dir>/<file_name>', methods=['DELETE'])
def delete_file(current_dir, file_name):
    file_path = os.path.join(current_dir, file_name)

    # Ensure the file exists before attempting to delete it
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    try:
        os.remove(file_path)  # Delete the file
        return jsonify({"success": "File deleted successfully"}), 200  # Send success response
    except Exception as e:
        return jsonify({"error": f"Error deleting file: {str(e)}"}), 500  # Send error response


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

@app.route('/add_bookmark', methods=['POST'])
def add_bookmark():
    """Add a new bookmark."""
    data = request.get_json()
    path = data.get('path', '').strip()
    name = data.get('name', '').strip()
    
    if not path or not name:
        return jsonify({"error": "Path and name are required"}), 400
    
    if not os.path.exists(path):
        return jsonify({"error": "Path does not exist"}), 400
    
    bookmarks = load_bookmarks()
    
    # Check if bookmark already exists
    for bookmark in bookmarks:
        if bookmark['path'] == path:
            return jsonify({"error": "Bookmark already exists"}), 400
    
    # Add new bookmark
    bookmarks.append({"name": name, "path": path})
    
    if save_bookmarks(bookmarks):
        return jsonify({"success": "Bookmark added successfully"}), 200
    else:
        return jsonify({"error": "Failed to save bookmark"}), 500

@app.route('/remove_bookmark', methods=['POST'])
def remove_bookmark():
    """Remove a bookmark."""
    data = request.get_json()
    path = data.get('path', '').strip()
    
    if not path:
        return jsonify({"error": "Path is required"}), 400
    
    bookmarks = load_bookmarks()
    bookmarks = [b for b in bookmarks if b['path'] != path]
    
    if save_bookmarks(bookmarks):
        return jsonify({"success": "Bookmark removed successfully"}), 200
    else:
        return jsonify({"error": "Failed to remove bookmark"}), 500

@app.route("/image_gallery")
def image_gallery():
    """Display image gallery with navigation."""
    dir_path = request.args.get('dir_path', 'C:/')
    filename = request.args.get('filename', '')
    
    try:
        # Get all image files in the directory
        image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp', '.ico')
        all_files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
        image_files = [f for f in all_files if f.lower().endswith(image_extensions)]
        image_files.sort()  # Sort alphabetically
        
        if not image_files:
            flash("No images found in this directory")
            return redirect(url_for('index', dir_path=dir_path))
        
        # Find current image index
        current_index = 0
        if filename in image_files:
            current_index = image_files.index(filename)
        
        current_image = image_files[current_index]
        
        # Get previous and next images
        prev_image = image_files[current_index - 1] if current_index > 0 else None
        next_image = image_files[current_index + 1] if current_index < len(image_files) - 1 else None
        
        return render_template('image_gallery.html',
                             current_image=current_image,
                             prev_image=prev_image,
                             next_image=next_image,
                             current_index=current_index + 1,
                             total_images=len(image_files),
                             dir_path=dir_path,
                             current_drive=request.args.get('drive', dir_path))
    
    except Exception as e:
        flash(f"Error loading image gallery: {e}")
        return redirect(url_for('index', dir_path=dir_path))

@app.route("/serve_image/<path:file_path>")
def serve_image(file_path):
    """Serve individual image files."""
    full_file_path = os.path.join(file_path)
    if os.path.exists(full_file_path):
        # Determine correct mimetype
        ext = os.path.splitext(full_file_path)[1].lower()
        mimetype_map = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.svg': 'image/svg+xml',
            '.webp': 'image/webp',
            '.ico': 'image/x-icon'
        }
        mimetype = mimetype_map.get(ext, 'image/jpeg')
        
        return send_file(full_file_path, mimetype=mimetype)
    else:
        return "Image not found", 404

@app.route('/get_move_folders', methods=['GET'])
def get_move_folders():
    """Get move folders as JSON for dynamic updates."""
    move_folders = load_move_folders()
    
    # Clean up and normalize paths if needed, add default colors
    cleaned_folders = []
    for folder in move_folders:
        normalized_path = os.path.normpath(folder['path']).replace('\\', '/')
        cleaned_folder = {
            "path": normalized_path, 
            "name": folder['name'],
            "bg_color": folder.get('bg_color', '#444'),
            "text_color": folder.get('text_color', '#ffffff'),
            "hover_bg_color": folder.get('hover_bg_color', '#FF9800'),
            "hover_text_color": folder.get('hover_text_color', '#000000')
        }
        cleaned_folders.append(cleaned_folder)
    
    # Save cleaned folders if any changes were made
    if cleaned_folders != move_folders:
        print("Cleaning up move folder paths and adding default colors...")
        save_move_folders(cleaned_folders)
        move_folders = cleaned_folders
    
    return jsonify({"folders": move_folders}), 200

@app.route('/add_move_folder', methods=['POST'])
def add_move_folder():
    """Add a new move folder."""
    data = request.get_json()
    path = data.get('path', '').strip()
    name = data.get('name', '').strip()
    
    if not path or not name:
        return jsonify({"error": "Path and name are required"}), 400
    
    # Normalize the path to use forward slashes consistently
    normalized_path = os.path.normpath(path).replace('\\', '/')
    print(f"Original path: '{path}' -> Normalized path: '{normalized_path}'")
    
    move_folders = load_move_folders()
    
    # Check if folder already exists (compare normalized paths)
    for folder in move_folders:
        existing_normalized = os.path.normpath(folder['path']).replace('\\', '/')
        if existing_normalized == normalized_path:
            return jsonify({"error": "Folder already exists in move list"}), 400
    
    # Add new folder with normalized path and default colors
    move_folders.append({
        "path": normalized_path, 
        "name": name,
        "bg_color": "#444",
        "text_color": "#ffffff",
        "hover_bg_color": "#FF9800",
        "hover_text_color": "#000000"
    })
    
    if save_move_folders(move_folders):
        return jsonify({"success": "Move folder added successfully"}), 200
    else:
        return jsonify({"error": "Failed to add move folder"}), 500

@app.route('/remove_move_folder', methods=['POST'])
def remove_move_folder():
    """Remove a move folder."""
    data = request.get_json()
    path = data.get('path', '').strip()
    
    if not path:
        return jsonify({"error": "Path is required"}), 400
    
    move_folders = load_move_folders()
    move_folders = [folder for folder in move_folders if folder['path'] != path]
    
    if save_move_folders(move_folders):
        return jsonify({"success": "Move folder removed successfully"}), 200
    else:
        return jsonify({"error": "Failed to remove move folder"}), 500

@app.route('/move_image', methods=['POST'])
def move_image():
    """Move an image file to a different directory."""
    data = request.get_json()
    source_dir = data.get('source_dir', '').strip()
    filename = data.get('filename', '').strip()
    target_dir = data.get('target_dir', '').strip()
    
    if not source_dir or not filename or not target_dir:
        return jsonify({"error": "Source directory, filename, and target directory are required"}), 400
    
    source_path = os.path.join(source_dir, filename)
    target_path = os.path.join(target_dir, filename)
    
    # Check if source file exists
    if not os.path.exists(source_path):
        return jsonify({"error": "Source file does not exist"}), 404
    
    # Check if target directory exists
    if not os.path.exists(target_dir):
        return jsonify({"error": "Target directory does not exist"}), 404
    
    # Check if target file already exists
    if os.path.exists(target_path):
        return jsonify({"error": "File already exists in target directory"}), 409
    
    try:
        import shutil
        shutil.move(source_path, target_path)
        return jsonify({"success": "Image moved successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to move image: {e}"}), 500

@app.route('/get_bookmarks', methods=['GET'])
def get_bookmarks():
    """Get bookmarks as JSON for dynamic updates."""
    bookmarks = load_bookmarks()
    return jsonify({"bookmarks": bookmarks}), 200

@app.route('/move_move_folder', methods=['POST'])
def move_move_folder():
    """Move a move folder up or down in the list."""
    data = request.get_json()
    path = data.get('path', '').strip()
    direction = data.get('direction', '').strip()
    
    print(f"Move folder request: path='{path}', direction='{direction}'")
    
    if not path:
        return jsonify({"error": "Path is required"}), 400
    
    if direction not in ['up', 'down']:
        return jsonify({"error": "Direction must be 'up' or 'down'"}), 400
    
    move_folders = load_move_folders()
    print(f"Total move folders: {len(move_folders)}")
    
    # Normalize the search path
    normalized_search_path = os.path.normpath(path).replace('\\', '/')
    print(f"Normalized search path: '{normalized_search_path}'")
    
    # Find the move folder index
    folder_index = -1
    for i, folder in enumerate(move_folders):
        folder_normalized = os.path.normpath(folder['path']).replace('\\', '/')
        print(f"Checking folder {i}: '{folder_normalized}' == '{normalized_search_path}' ? {folder_normalized == normalized_search_path}")
        if folder_normalized == normalized_search_path:
            folder_index = i
            break
    
    if folder_index == -1:
        print(f"Move folder not found. Available paths: {[f['path'] for f in move_folders]}")
        return jsonify({"error": f"Move folder not found. Path: '{path}'"}), 404
    
    print(f"Found folder at index {folder_index}")
    
    # Check boundaries and move
    if direction == 'up':
        if folder_index > 0:
            print(f"Moving folder up from index {folder_index} to {folder_index - 1}")
            # Swap with previous folder
            move_folders[folder_index], move_folders[folder_index - 1] = move_folders[folder_index - 1], move_folders[folder_index]
        else:
            print("Cannot move up - already at top")
            return jsonify({"error": "Cannot move up - folder is already at the top"}), 400
    elif direction == 'down':
        if folder_index < len(move_folders) - 1:
            print(f"Moving folder down from index {folder_index} to {folder_index + 1}")
            # Swap with next folder
            move_folders[folder_index], move_folders[folder_index + 1] = move_folders[folder_index + 1], move_folders[folder_index]
        else:
            print("Cannot move down - already at bottom")
            return jsonify({"error": "Cannot move down - folder is already at the bottom"}), 400
    
    if save_move_folders(move_folders):
        print("Move folder operation successful")
        return jsonify({"success": "Move folder moved successfully"}), 200
    else:
        print("Failed to save move folders")
        return jsonify({"error": "Failed to save move folders"}), 500

@app.route('/move_bookmark', methods=['POST'])
def move_bookmark():
    """Move a bookmark up or down in the list."""
    data = request.get_json()
    path = data.get('path', '').strip()
    direction = data.get('direction', '').strip()
    
    if not path:
        return jsonify({"error": "Path is required"}), 400
    
    if direction not in ['up', 'down']:
        return jsonify({"error": "Direction must be 'up' or 'down'"}), 400
    
    bookmarks = load_bookmarks()
    
    # Find the bookmark index
    bookmark_index = -1
    for i, bookmark in enumerate(bookmarks):
        if bookmark['path'] == path:
            bookmark_index = i
            break
    
    if bookmark_index == -1:
        return jsonify({"error": "Bookmark not found"}), 404
    
    # Move the bookmark
    if direction == 'up' and bookmark_index > 0:
        # Swap with previous bookmark
        bookmarks[bookmark_index], bookmarks[bookmark_index - 1] = bookmarks[bookmark_index - 1], bookmarks[bookmark_index]
    elif direction == 'down' and bookmark_index < len(bookmarks) - 1:
        # Swap with next bookmark
        bookmarks[bookmark_index], bookmarks[bookmark_index + 1] = bookmarks[bookmark_index + 1], bookmarks[bookmark_index]
    else:
        return jsonify({"error": "Cannot move bookmark in that direction"}), 400
    
    if save_bookmarks(bookmarks):
        return jsonify({"success": "Bookmark moved successfully"}), 200
    else:
        return jsonify({"error": "Failed to move bookmark"}), 500

@app.route('/open_explorer', methods=['POST'])
def open_explorer():
    """Open the specified directory in Windows Explorer."""
    import subprocess
    
    data = request.get_json()
    path = data.get('path', '').strip()
    
    if not path:
        return jsonify({"error": "Path is required"}), 400
    
    # Normalize the path for Windows
    normalized_path = os.path.normpath(path)
    
    if not os.path.exists(normalized_path):
        return jsonify({"error": f"Path does not exist: {normalized_path}"}), 400
    
    try:
        # Use Windows Explorer to open the directory
        # Use /select flag to open and select the folder, or just the path to open it
        if os.path.isdir(normalized_path):
            result = subprocess.run(['explorer', normalized_path], shell=True, capture_output=True)
        else:
            # If it's a file, open the parent directory and select the file
            result = subprocess.run(['explorer', '/select,', normalized_path], shell=True, capture_output=True)
        
        # Explorer often returns exit code 1 even when successful, so we don't check the return code
        return jsonify({"success": "Directory opened in Explorer"}), 200
    except Exception as e:
        return jsonify({"error": f"Error opening Explorer: {e}"}), 500

@app.route('/download_directory')
def download_directory():
    dir_path = request.args.get('dir_path')
    if not dir_path or not os.path.isdir(dir_path):
        flash('Invalid directory path.')
        return redirect(url_for('index'))

    # Create a memory file for the zip archive
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, dir_path)
                zf.write(file_path, arcname)

    memory_file.seek(0)
    return send_file(memory_file,
                     download_name=f'{os.path.basename(dir_path)}.zip',
                     as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)
