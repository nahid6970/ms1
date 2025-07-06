from flask import Flask, render_template, jsonify, request, send_from_directory
import json
import os

app = Flask(__name__)

DATA_FILE = 'data.json'

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

@app.route('/')
def index():
    return render_template('myhome_input.html')

@app.route('/myhome/<path:filename>')
def serve_myhome_static(filename):
    return send_from_directory('myhome', filename)

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

if __name__ == '__main__':
    app.run(debug=True)
