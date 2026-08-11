import os
import sqlite3
import json
import uuid
import time
import shutil
import mimetypes
from flask import Flask, request, jsonify, send_file, send_from_directory

# Force correct MIME type associations to prevent corrupted Windows registry settings from breaking files
mimetypes.init()
mimetypes.add_type('application/pdf', '.pdf')
mimetypes.add_type('image/png', '.png')
mimetypes.add_type('image/jpeg', '.jpg')
mimetypes.add_type('image/jpeg', '.jpeg')
mimetypes.add_type('image/gif', '.gif')

app = Flask(__name__, static_folder=".", static_url_path="")

# Local storage directory as requested by user
UPLOAD_FOLDER = r"C:\@delta\msBackups\@JOB\Management"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "image_share.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_folder_path(folder_id):
    if not folder_id:
        return UPLOAD_FOLDER
    
    conn = get_db()
    cursor = conn.cursor()
    
    path_parts = []
    current_id = folder_id
    visited = set()
    
    while current_id and current_id not in visited:
        visited.add(current_id)
        cursor.execute("SELECT name, parentId FROM folders WHERE id = ?", (current_id,))
        row = cursor.fetchone()
        if not row:
            break
        clean_name = row["name"]
        for char in '<>:"/\\|?*':
            clean_name = clean_name.replace(char, '_')
        path_parts.insert(0, clean_name.strip())
        current_id = row["parentId"]
        
    conn.close()
    return os.path.join(UPLOAD_FOLDER, *path_parts)

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Create folders table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS folders (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        position INTEGER,
        password TEXT,
        parentId TEXT,
        bgColor TEXT,
        fgColor TEXT,
        borderColor TEXT,
        fontBold INTEGER DEFAULT 0,
        fontItalic INTEGER DEFAULT 0,
        fontSize INTEGER DEFAULT 13,
        hideFromAll INTEGER DEFAULT 0
    )
    """)
    
    # Create images table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS images (
        id TEXT PRIMARY KEY,
        url TEXT NOT NULL,
        filename TEXT NOT NULL,
        fileSize INTEGER,
        timestamp INTEGER NOT NULL,
        folderId TEXT,
        pinned INTEGER DEFAULT 0,
        isShared INTEGER DEFAULT 0,
        storageId TEXT
    )
    """)
    
    # Create settings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY DEFAULT 1,
        sortOrder TEXT DEFAULT 'newest',
        currentFolderId TEXT,
        colors TEXT,
        paintRecolorActive INTEGER DEFAULT 0,
        paintRecolorRules TEXT DEFAULT '[]'
    )
    """)
    
    # Check if settings row exists, insert default if not
    cursor.execute("SELECT COUNT(*) FROM settings")
    if cursor.fetchone()[0] == 0:
        default_colors = json.dumps({
            "convex": "#ec4899"
        })
        cursor.execute("""
        INSERT INTO settings (id, colors)
        VALUES (1, ?)
        """, (default_colors,))
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return send_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html'))

@app.route('/files/<storage_id>')
def serve_file(storage_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT folderId, filename FROM images WHERE storageId = ?", (storage_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        # Fallback: check if file starts with prefix in the root UPLOAD_FOLDER
        try:
            for f in os.listdir(UPLOAD_FOLDER):
                if f.startswith(f"{storage_id}_"):
                    mimetype = None
                    if f.lower().endswith('.pdf'):
                        mimetype = 'application/pdf'
                    elif f.lower().endswith('.png'):
                        mimetype = 'image/png'
                    elif f.lower().endswith('.jpg') or f.lower().endswith('.jpeg'):
                        mimetype = 'image/jpeg'
                    elif f.lower().endswith('.gif'):
                        mimetype = 'image/gif'
                    return send_from_directory(UPLOAD_FOLDER, f, mimetype=mimetype)
        except Exception as e:
            return str(e), 500
        return "File not found", 404
        
    folder_id = row["folderId"]
    folder_path = get_folder_path(folder_id)
    
    try:
        if os.path.exists(folder_path):
            for f in os.listdir(folder_path):
                if f.startswith(f"{storage_id}_"):
                    mimetype = None
                    if f.lower().endswith('.pdf'):
                        mimetype = 'application/pdf'
                    elif f.lower().endswith('.png'):
                        mimetype = 'image/png'
                    elif f.lower().endswith('.jpg') or f.lower().endswith('.jpeg'):
                        mimetype = 'image/jpeg'
                    elif f.lower().endswith('.gif'):
                        mimetype = 'image/gif'
                    return send_from_directory(folder_path, f, mimetype=mimetype)
    except Exception as e:
        return str(e), 500
        
    return "File not found", 404

# --- API ENDPOINTS ---

@app.route('/api/settings', methods=['GET'])
@app.route('/api/images/getSettings', methods=['GET'])
def get_settings():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM settings WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return jsonify({})
        
    settings = dict(row)
    if settings.get("colors"):
        settings["colors"] = json.loads(settings["colors"])
    else:
        settings["colors"] = {"convex": "#ec4899"}
    settings["paintRecolorActive"] = bool(settings["paintRecolorActive"])
    return jsonify(settings)

@app.route('/api/images/updateSettings', methods=['POST'])
def update_settings():
    data = request.json or {}
    conn = get_db()
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    fields = [
        "sortOrder", "currentFolderId", "paintRecolorActive"
    ]
    
    for field in fields:
        if field in data:
            updates.append(f"{field} = ?")
            val = data[field]
            if field == "paintRecolorActive":
                val = 1 if val else 0
            params.append(val)
            
    if "colors" in data:
        updates.append("colors = ?")
        params.append(json.dumps(data["colors"]))
        
    if "paintRecolorRules" in data:
        updates.append("paintRecolorRules = ?")
        params.append(data["paintRecolorRules"])
        
    if updates:
        query_str = f"UPDATE settings SET {', '.join(updates)} WHERE id = 1"
        cursor.execute(query_str, params)
        conn.commit()
        
    conn.close()
    return jsonify({"success": True})

@app.route('/api/folders', methods=['GET'])
def list_folders():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM folders ORDER BY position ASC")
    rows = cursor.fetchall()
    conn.close()
    
    folders_list = []
    for row in rows:
        f = dict(row)
        f["_id"] = f["id"]
        f["fontBold"] = bool(f["fontBold"])
        f["fontItalic"] = bool(f["fontItalic"])
        f["hideFromAll"] = bool(f["hideFromAll"])
        folders_list.append(f)
        
    return jsonify(folders_list)

@app.route('/api/images/createFolder', methods=['POST'])
def create_folder():
    data = request.json or {}
    name = data.get("name")
    parent_id = data.get("parentId")
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT MAX(position) FROM folders")
    row = cursor.fetchone()
    max_pos = row[0] if row[0] is not None else -1
    
    folder_id = str(uuid.uuid4())
    cursor.execute("""
    INSERT INTO folders (id, name, position, parentId)
    VALUES (?, ?, ?, ?)
    """, (folder_id, name, max_pos + 1, parent_id))
    conn.commit()
    conn.close()
    
    # Physically create folder on disk
    try:
        folder_path = get_folder_path(folder_id)
        os.makedirs(folder_path, exist_ok=True)
    except Exception as e:
        print(f"Failed to create physical folder on disk: {e}")
        
    return jsonify(folder_id)

@app.route('/api/images/updateFolder', methods=['POST'])
def update_folder():
    data = request.json or {}
    fid = data.get("id")
    name = data.get("name")
    position = data.get("position")
    bg_color = data.get("bgColor")
    fg_color = data.get("fgColor")
    border_color = data.get("borderColor")
    parent_id = data.get("parentId")
    font_bold = data.get("fontBold")
    font_italic = data.get("fontItalic")
    font_size = data.get("fontSize")
    
    # Resolve old path before DB update
    old_path = get_folder_path(fid)
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
    UPDATE folders SET
        name = ?, position = ?, bgColor = ?, fgColor = ?, borderColor = ?,
        parentId = ?, fontBold = ?, fontItalic = ?, fontSize = ?
    WHERE id = ?
    """, (
        name, position, bg_color, fg_color, border_color, parent_id,
        1 if font_bold else 0, 1 if font_italic else 0, font_size, fid
    ))
    conn.commit()
    conn.close()
    
    # Resolve new path after DB update
    new_path = get_folder_path(fid)
    
    if old_path != new_path and os.path.exists(old_path):
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        try:
            os.rename(old_path, new_path)
        except Exception as e:
            print(f"Failed to rename folder on disk: {e}")
            
    return jsonify({"success": True})

@app.route('/api/images/reorderFolders', methods=['POST'])
def reorder_folders():
    data = request.json or {}
    folder_ids = data.get("folderIds", [])
    
    conn = get_db()
    cursor = conn.cursor()
    for index, fid in enumerate(folder_ids):
        cursor.execute("UPDATE folders SET position = ? WHERE id = ?", (index, fid))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True})

@app.route('/api/images/setFolderPassword', methods=['POST'])
def set_folder_password():
    data = request.json or {}
    fid = data.get("id")
    password = data.get("password")
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE folders SET password = ? WHERE id = ?", (password, fid))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True})

@app.route('/api/images/removeFolder', methods=['POST'])
def remove_folder():
    data = request.json or {}
    fid = data.get("id")
    password = data.get("password")
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT password FROM folders WHERE id = ?", (fid,))
    row = cursor.fetchone()
    if row:
        stored_pw = row["password"]
        if stored_pw and stored_pw != password:
            conn.close()
            return jsonify({"error": "Incorrect password"}), 403
            
    # Select images inside this folder to move their physical files
    cursor.execute("SELECT id, filename, storageId FROM images WHERE folderId = ?", (fid,))
    images = cursor.fetchall()
    
    current_folder_path = get_folder_path(fid)
    
    # Move physical files of these images to No folder (root UPLOAD_FOLDER)
    for img in images:
        filename = img["filename"]
        storage_id = img["storageId"]
        if storage_id:
            old_file_path = os.path.join(current_folder_path, f"{storage_id}_{filename}")
            new_file_path = os.path.join(UPLOAD_FOLDER, f"{storage_id}_{filename}")
            if os.path.exists(old_file_path):
                try:
                    os.rename(old_file_path, new_file_path)
                except Exception as e:
                    print(f"Failed to move file on delete folder: {e}")
                    
    cursor.execute("UPDATE images SET folderId = NULL WHERE folderId = ?", (fid,))
    cursor.execute("DELETE FROM folders WHERE id = ?", (fid,))
    conn.commit()
    conn.close()
    
    # Delete physical directory on disk
    if os.path.exists(current_folder_path):
        try:
            shutil.rmtree(current_folder_path, ignore_errors=True)
        except Exception as e:
            print(f"Failed to delete directory: {e}")
            
    return jsonify({"success": True})

@app.route('/api/images/toggleHideFromAll', methods=['POST'])
def toggle_hide_from_all():
    data = request.json or {}
    fid = data.get("id")
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT hideFromAll FROM folders WHERE id = ?", (fid,))
    row = cursor.fetchone()
    if row:
        next_val = 0 if row["hideFromAll"] else 1
        cursor.execute("UPDATE folders SET hideFromAll = ? WHERE id = ?", (next_val, fid))
        conn.commit()
        
    conn.close()
    return jsonify({"success": True})

@app.route('/api/images', methods=['GET'])
def list_images():
    folder_id = request.args.get("folderId")
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM images")
    all_images = [dict(row) for row in cursor.fetchall()]
    cursor.execute("SELECT * FROM folders")
    all_folders = {row["id"]: dict(row) for row in cursor.fetchall()}
    conn.close()
    
    filtered_images = []
    if folder_id == "shared":
        filtered_images = [img for img in all_images if img["isShared"] == 1]
    elif folder_id == "none" or folder_id == "":
        filtered_images = [img for img in all_images if not img["folderId"]]
    elif folder_id:
        filtered_images = [img for img in all_images if img["folderId"] == folder_id]
    else:
        hidden_folder_ids = {
            fid for fid, folder in all_folders.items()
            if folder.get("password") or folder.get("hideFromAll") == 1
        }
        filtered_images = [
            img for img in all_images
            if not img["folderId"] or img["folderId"] not in hidden_folder_ids
        ]
        
    for img in filtered_images:
        img["_id"] = img["id"]
        img["pinned"] = bool(img["pinned"])
        img["isShared"] = bool(img["isShared"])
        
    filtered_images.sort(key=lambda x: (not x["pinned"], -x["timestamp"]))
    return jsonify(filtered_images)

@app.route('/api/images/generateUploadUrl', methods=['POST'])
def generate_upload_url():
    return jsonify("/api/upload-raw")

@app.route('/api/upload-raw', methods=['POST'])
def upload_raw():
    file_id = str(uuid.uuid4())
    temp_filename = f"temp_{file_id}"
    temp_path = os.path.join(UPLOAD_FOLDER, temp_filename)
    
    # Use request.get_data() to retrieve entire raw binary upload body reliably
    data = request.get_data()
    if not data:
        # Fallback stream read if request.get_data() is unavailable
        data = request.stream.read()
        
    with open(temp_path, "wb") as f:
        f.write(data)
            
    return jsonify({"storageId": file_id})

@app.route('/api/images/saveStorageImage', methods=['POST'])
def save_storage_image():
    data = request.json or {}
    storage_id = data.get("storageId")
    filename = data.get("filename")
    file_size = data.get("fileSize")
    folder_id = data.get("folderId")
    
    if not storage_id or not filename:
        return jsonify({"error": "Missing storageId or filename"}), 400
        
    temp_filename = f"temp_{storage_id}"
    temp_path = os.path.join(UPLOAD_FOLDER, temp_filename)
    clean_filename = os.path.basename(filename)
    
    folder_path = get_folder_path(folder_id)
    os.makedirs(folder_path, exist_ok=True)
    
    disk_filename = f"{storage_id}_{clean_filename}"
    disk_path = os.path.join(folder_path, disk_filename)
    
    if os.path.exists(temp_path):
        os.rename(temp_path, disk_path)
        
    url = f"/files/{storage_id}"
    
    conn = get_db()
    cursor = conn.cursor()
    image_id = str(uuid.uuid4())
    cursor.execute("""
    INSERT INTO images (id, url, filename, fileSize, timestamp, folderId, storageId)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (image_id, url, clean_filename, file_size, int(time.time() * 1000), folder_id, storage_id))
    conn.commit()
    conn.close()
    
    return jsonify(image_id)

@app.route('/api/images/add', methods=['POST'])
def add_image():
    data = request.json or {}
    url = data.get("url")
    filename = data.get("filename")
    file_size = data.get("fileSize")
    folder_id = data.get("folderId")
    
    conn = get_db()
    cursor = conn.cursor()
    image_id = str(uuid.uuid4())
    cursor.execute("""
    INSERT INTO images (id, url, filename, fileSize, timestamp, folderId)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (image_id, url, filename, file_size, int(time.time() * 1000), folder_id))
    conn.commit()
    conn.close()
    
    return jsonify(image_id)

@app.route('/api/images/togglePin', methods=['POST'])
def toggle_pin():
    data = request.json or {}
    image_id = data.get("id")
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT pinned FROM images WHERE id = ?", (image_id,))
    row = cursor.fetchone()
    if row:
        next_pinned = 0 if row["pinned"] else 1
        cursor.execute("UPDATE images SET pinned = ? WHERE id = ?", (next_pinned, image_id))
        conn.commit()
        
    conn.close()
    return jsonify({"success": True})

@app.route('/api/images/renameImage', methods=['POST'])
def rename_image():
    data = request.json or {}
    image_id = data.get("id")
    filename = data.get("filename")
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE images SET filename = ? WHERE id = ?", (filename, image_id))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True})

@app.route('/api/images/moveToFolder', methods=['POST'])
def move_to_folder():
    data = request.json or {}
    image_id = data.get("imageId")
    folder_id = data.get("folderId")
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Select image details to move physical file
    cursor.execute("SELECT folderId, filename, storageId FROM images WHERE id = ?", (image_id,))
    row = cursor.fetchone()
    if row:
        old_folder_id = row["folderId"]
        filename = row["filename"]
        storage_id = row["storageId"]
        
        if storage_id:
            old_folder_path = get_folder_path(old_folder_id)
            new_folder_path = get_folder_path(folder_id)
            os.makedirs(new_folder_path, exist_ok=True)
            
            old_file_path = os.path.join(old_folder_path, f"{storage_id}_{filename}")
            new_file_path = os.path.join(new_folder_path, f"{storage_id}_{filename}")
            
            if os.path.exists(old_file_path):
                try:
                    os.rename(old_file_path, new_file_path)
                except Exception as e:
                    print(f"Failed to move file on disk: {e}")
                    
    cursor.execute("UPDATE images SET folderId = ? WHERE id = ?", (folder_id, image_id))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True})

@app.route('/api/images/toggleSharing', methods=['POST'])
def toggle_sharing():
    data = request.json or {}
    image_id = data.get("id")
    is_shared = data.get("isShared")
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE images SET isShared = ? WHERE id = ?", (1 if is_shared else 0, image_id))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True})

@app.route('/api/images/remove', methods=['POST'])
def remove_image():
    data = request.json or {}
    image_id = data.get("id")
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT storageId, filename, folderId FROM images WHERE id = ?", (image_id,))
    row = cursor.fetchone()
    if row:
        storage_id = row["storageId"]
        filename = row["filename"]
        folder_id = row["folderId"]
        
        if storage_id:
            folder_path = get_folder_path(folder_id)
            file_path = os.path.join(folder_path, f"{storage_id}_{filename}")
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Failed to delete disk file: {e}")
                    
    cursor.execute("DELETE FROM images WHERE id = ?", (image_id,))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True})

@app.route('/api/images/clear', methods=['POST'])
def clear_images():
    data = request.json or {}
    folder_id = data.get("folderId")
    
    conn = get_db()
    cursor = conn.cursor()
    
    if folder_id == "none":
        cursor.execute("SELECT id, storageId, filename, folderId FROM images WHERE folderId IS NULL AND pinned = 0")
    elif folder_id:
        cursor.execute("SELECT id, storageId, filename, folderId FROM images WHERE folderId = ? AND pinned = 0", (folder_id,))
    else:
        cursor.execute("SELECT id FROM folders WHERE password IS NOT NULL OR hideFromAll = 1")
        hidden_ids = [r["id"] for r in cursor.fetchall()]
        
        cursor.execute("SELECT id, folderId, storageId, filename FROM images WHERE pinned = 0")
        all_unpinned = cursor.fetchall()
        images_to_delete = []
        for img in all_unpinned:
            if not img["folderId"] or img["folderId"] not in hidden_ids:
                images_to_delete.append(img)
                
        for img in images_to_delete:
            storage_id = img["storageId"]
            filename = img["filename"]
            img_folder_id = img["folderId"]
            
            if storage_id:
                folder_path = get_folder_path(img_folder_id)
                file_path = os.path.join(folder_path, f"{storage_id}_{filename}")
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(e)
            cursor.execute("DELETE FROM images WHERE id = ?", (img["id"],))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
        
    rows = cursor.fetchall()
    for row in rows:
        storage_id = row["storageId"]
        filename = row["filename"]
        img_folder_id = row["folderId"]
        
        if storage_id:
            folder_path = get_folder_path(img_folder_id)
            file_path = os.path.join(folder_path, f"{storage_id}_{filename}")
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(e)
        cursor.execute("DELETE FROM images WHERE id = ?", (row["id"],))
        
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/api/images/updateImageStorage', methods=['POST'])
def update_image_storage():
    data = request.json or {}
    image_id = data.get("id")
    url = data.get("url")
    storage_id = data.get("storageId")
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT storageId, filename, folderId FROM images WHERE id = ?", (image_id,))
    row = cursor.fetchone()
    if row and row["storageId"] and row["storageId"] != storage_id:
        old_storage_id = row["storageId"]
        filename = row["filename"]
        folder_id = row["folderId"]
        folder_path = get_folder_path(folder_id)
        file_path = os.path.join(folder_path, f"{old_storage_id}_{filename}")
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(e)
                
    if storage_id and not url:
        url = f"/files/{storage_id}"
        
    cursor.execute("UPDATE images SET url = ?, storageId = ? WHERE id = ?", (url, storage_id, image_id))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
