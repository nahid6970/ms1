from flask import Flask, render_template, jsonify, request, send_from_directory
import json
import os
import subprocess
from datetime import datetime

app = Flask(__name__)

DATA_FILE = r'C:\msBackups\DataBase\myhome\data.json'

# Helper function to read data from JSON file
def read_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

# Helper function to write data to JSON file
def write_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    # Auto-generate static HTML after data update
    generate_static_html()

# Function to generate static HTML
def generate_static_html():
    """Generate static HTML file with embedded CSS and JS"""
    try:
        # Run the generate_static.py script from current directory
        result = subprocess.run(['pythonw', r'C:\ms1\myhome\generate_static.py'], 
                              capture_output=True, text=True, cwd='.', 
                              encoding='utf-8', errors='replace')
        if result.returncode == 0:
            print(f"[SUCCESS] Static HTML auto-generated at {datetime.now().strftime('%H:%M:%S')}")
            if result.stdout:
                print(f"[OUTPUT] {result.stdout.strip()}")
        else:
            print(f"[ERROR] Error generating static HTML:")
            print(f"[ERROR] Return code: {result.returncode}")
            if result.stderr:
                print(f"[ERROR] {result.stderr.strip()}")
            if result.stdout:
                print(f"[OUTPUT] {result.stdout.strip()}")
    except Exception as e:
        print(f"[EXCEPTION] Exception generating static HTML: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def serve_myhome_static(filename):
    return send_from_directory('static', filename)

@app.route('/api/links', methods=['GET'])
def get_links():
    links = read_data()
    return jsonify(links)

@app.route('/api/links', methods=['PUT'])
def update_all_links():
    new_links = request.json
    write_data(new_links)
    return jsonify({'message': 'Links updated successfully'})

@app.route('/api/add_link', methods=['POST'])
def add_link():
    new_link = request.json
    # Ensure default_type is set, default to 'nf-con' if not provided
    if 'default_type' not in new_link or not new_link['default_type']:
        new_link['default_type'] = 'nerd-font'
    links = read_data()
    links.append(new_link)
    write_data(links)
    return jsonify({'message': 'Link added successfully'}), 201

@app.route('/api/links/<int:link_id>', methods=['PUT'])
def edit_link(link_id):
    updated_link = request.json
    # Ensure default_type is set, default to 'nerd-font' if not provided
    if 'default_type' not in updated_link or not updated_link['default_type']:
        updated_link['default_type'] = 'nerd-font'
    links = read_data()
    if 0 <= link_id < len(links):
        links[link_id] = updated_link
        write_data(links)
        return jsonify({'message': 'Link updated successfully'})
    return jsonify({'message': 'Link not found'}), 404

@app.route('/api/links/<int:link_id>', methods=['DELETE'])
def delete_link(link_id):
    links = read_data()
    if 0 <= link_id < len(links):
        deleted_link = links.pop(link_id)
        write_data(links)
        return jsonify({'message': 'Link deleted successfully', 'deleted_link': deleted_link})
    return jsonify({'message': 'Link not found'}), 404

@app.route('/generate-static')
def manual_generate_static():
    """Manual endpoint to generate static HTML"""
    try:
        generate_static_html()
        return jsonify({'message': 'Static HTML generated successfully', 'file': r'C:\ms1\myhome\myhome.html'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)