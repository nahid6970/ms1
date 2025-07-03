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

@app.route('/api/add_link', methods=['POST'])
def add_link():
    new_link = request.json
    links = read_data()
    links.append(new_link)
    write_data(links)
    return jsonify({'message': 'Link added successfully'}), 201

if __name__ == '__main__':
    app.run(debug=True)
