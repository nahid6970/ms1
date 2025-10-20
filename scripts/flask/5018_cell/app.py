from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

DATA_FILE = 'data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {'columns': [], 'rows': []}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify(load_data())

@app.route('/api/data', methods=['POST'])
def save_table_data():
    data = request.json
    save_data(data)
    return jsonify({'success': True})

@app.route('/api/columns', methods=['POST'])
def add_column():
    data = load_data()
    column = request.json
    data['columns'].append(column)
    save_data(data)
    return jsonify({'success': True})

@app.route('/api/columns/<int:index>', methods=['DELETE'])
def delete_column(index):
    data = load_data()
    if 0 <= index < len(data['columns']):
        data['columns'].pop(index)
        for row in data['rows']:
            if len(row) > index:
                row.pop(index)
        save_data(data)
    return jsonify({'success': True})

@app.route('/api/rows', methods=['POST'])
def add_row():
    data = load_data()
    data['rows'].append(['' for _ in data['columns']])
    save_data(data)
    return jsonify({'success': True})

@app.route('/api/rows/<int:index>', methods=['DELETE'])
def delete_row(index):
    data = load_data()
    if 0 <= index < len(data['rows']):
        data['rows'].pop(index)
        save_data(data)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, port=5018)
