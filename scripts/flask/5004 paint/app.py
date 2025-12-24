from flask import Flask, render_template, request, jsonify
import os
import base64
import time
import uuid
import json

app = Flask(__name__)
SAVE_DIR = os.path.join(os.path.dirname(__file__), "static", "saved_art")
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")

if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save', methods=['POST'])
def save_art():
    data = request.json
    image_data = data.get('image')
    
    if image_data:
        try:
            # Remove header of base64 string
            if ',' in image_data:
                head, data_content = image_data.split(',', 1)
                file_ext = head.split(';')[0].split('/')[1]
            else:
                return jsonify({"success": False, "error": "Invalid image data"})

            decoded_img = base64.b64decode(data_content)
            
            filename = f"art_{int(time.time())}_{uuid.uuid4().hex[:8]}.{file_ext}"
            filepath = os.path.join(SAVE_DIR, filename)
            
            with open(filepath, 'wb') as f:
                f.write(decoded_img)
                
            return jsonify({"success": True, "filename": filename, "url": f"/static/saved_art/{filename}"})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})
            
    return jsonify({"success": False, "error": "No data"})

@app.route('/gallery')
def gallery():
    try:
        files = sorted(os.listdir(SAVE_DIR), key=lambda x: os.path.getmtime(os.path.join(SAVE_DIR, x)), reverse=True)
        images = [f"/static/saved_art/{f}" for f in files if f.endswith(('.png', '.jpg', '.jpeg', '.webp'))]
        return jsonify(images)
    except Exception as e:
        return jsonify([])

@app.route('/delete', methods=['POST'])
def delete_art():
    data = request.json
    filename = data.get('filename')
    
    if not filename:
        return jsonify({"success": False, "error": "No filename provided"})
    
    # Security check: ensure no directory traversal
    safe_filename = os.path.basename(filename)
    filepath = os.path.join(SAVE_DIR, safe_filename)
    
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})
    else:
        return jsonify({"success": False, "error": "File not found"})

@app.route('/save_settings', methods=['POST'])
def save_settings():
    try:
        settings = request.json
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/get_settings', methods=['GET'])
def get_settings():
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
            return jsonify(settings)
        return jsonify({})
    except Exception as e:
        return jsonify({})

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True, port=5004)
