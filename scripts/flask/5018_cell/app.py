from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

DATA_FILE = 'data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {
        'sheets': [
            {'name': 'Sheet1', 'columns': [], 'rows': []}
        ],
        'activeSheet': 0
    }

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

@app.route('/api/sheets', methods=['POST'])
def add_sheet():
    data = load_data()
    sheet_name = request.json.get('name', f'Sheet{len(data["sheets"]) + 1}')
    data['sheets'].append({'name': sheet_name, 'columns': [], 'rows': []})
    save_data(data)
    return jsonify({'success': True, 'sheetIndex': len(data['sheets']) - 1})

@app.route('/api/sheets/<int:index>', methods=['DELETE'])
def delete_sheet(index):
    data = load_data()
    if len(data['sheets']) > 1 and 0 <= index < len(data['sheets']):
        data['sheets'].pop(index)
        if data['activeSheet'] >= len(data['sheets']):
            data['activeSheet'] = len(data['sheets']) - 1
        save_data(data)
    return jsonify({'success': True})

@app.route('/api/sheets/<int:index>/rename', methods=['POST'])
def rename_sheet(index):
    data = load_data()
    new_name = request.json.get('name')
    if 0 <= index < len(data['sheets']) and new_name:
        data['sheets'][index]['name'] = new_name
        save_data(data)
    return jsonify({'success': True})

@app.route('/api/columns', methods=['POST'])
def add_column():
    data = load_data()
    sheet_index = request.json.get('sheetIndex', data['activeSheet'])
    column = request.json.get('column')
    data['sheets'][sheet_index]['columns'].append(column)
    save_data(data)
    return jsonify({'success': True})

@app.route('/api/columns/<int:sheet_index>/<int:col_index>', methods=['DELETE'])
def delete_column(sheet_index, col_index):
    data = load_data()
    sheet = data['sheets'][sheet_index]
    if 0 <= col_index < len(sheet['columns']):
        sheet['columns'].pop(col_index)
        for row in sheet['rows']:
            if len(row) > col_index:
                row.pop(col_index)
        save_data(data)
    return jsonify({'success': True})

@app.route('/api/rows', methods=['POST'])
def add_row():
    data = load_data()
    sheet_index = request.json.get('sheetIndex', data['activeSheet'])
    sheet = data['sheets'][sheet_index]
    sheet['rows'].append(['' for _ in sheet['columns']])
    save_data(data)
    return jsonify({'success': True})

@app.route('/api/rows/<int:sheet_index>/<int:row_index>', methods=['DELETE'])
def delete_row(sheet_index, row_index):
    data = load_data()
    sheet = data['sheets'][sheet_index]
    if 0 <= row_index < len(sheet['rows']):
        sheet['rows'].pop(row_index)
        save_data(data)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, port=5018)
