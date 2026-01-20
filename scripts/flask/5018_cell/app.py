from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

# Disable caching for development
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.after_request
def add_header(response):
    # Prevent caching of all responses
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

DATA_FILE = r'C:\@delta\ms1\scripts\flask\5018_cell\data.json'
STATE_FILE = r'C:\@delta\output\5018_output\sheet_active.json'
CUSTOM_SYNTAXES_FILE = r'C:\@delta\ms1\scripts\flask\5018_cell\custom_syntaxes.json'

def load_data():
    data = {
        'sheets': [
            {'name': 'Sheet1', 'columns': [], 'rows': []}
        ],
        'activeSheet': 0
    }
    
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            file_data = json.load(f)
            data.update(file_data)
            
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            state_data = json.load(f)
            if 'activeSheet' in state_data:
                data['activeSheet'] = state_data['activeSheet']
                
    return data

def save_data(data):
    # Save activeSheet to state file
    state = {'activeSheet': data.get('activeSheet', 0)}
    # Ensure directory exists
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)
        
    # Save sheets to data file (excluding activeSheet)
    content = {k: v for k, v in data.items() if k != 'activeSheet'}
    with open(DATA_FILE, 'w') as f:
        json.dump(content, f, indent=2)
    
    # Auto-export static HTML after saving data
    try:
        import subprocess
        import sys
        script_dir = os.path.dirname(os.path.abspath(__file__))
        export_script_path = os.path.join(script_dir, 'export_static.py')
        result = subprocess.run([sys.executable, export_script_path], 
                              capture_output=True, text=True, cwd=script_dir)
        if result.returncode == 0:
            print("Auto-exported static HTML")
            if result.stdout.strip():
                print(result.stdout.strip())
        else:
            print(f"Auto-export failed: {result.stderr}")
    except Exception as e:
        print(f"Auto-export failed: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify(load_data())

@app.route('/api/active-sheet', methods=['POST'])
def save_active_sheet():
    index = request.json.get('activeSheet')
    if index is not None:
        state = {'activeSheet': index}
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    return jsonify({'success': True})

@app.route('/api/data', methods=['POST'])
def save_table_data():
    data = request.json
    save_data(data)
    return jsonify({'success': True})

@app.route('/api/sheets', methods=['POST'])
def add_sheet():
    data = load_data()
    sheet_name = request.json.get('name', f'Sheet{len(data["sheets"]) + 1}')
    parent_sheet = request.json.get('parentSheet', None)
    
    new_sheet = {'name': sheet_name, 'columns': [], 'rows': []}
    if parent_sheet is not None:
        new_sheet['parentSheet'] = parent_sheet
    
    data['sheets'].append(new_sheet)
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
    new_nickname = request.json.get('nickname', '')
    if 0 <= index < len(data['sheets']) and new_name:
        data['sheets'][index]['name'] = new_name
        data['sheets'][index]['nickname'] = new_nickname
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

@app.route('/api/custom-syntaxes', methods=['GET'])
def get_custom_syntaxes():
    if os.path.exists(CUSTOM_SYNTAXES_FILE):
        with open(CUSTOM_SYNTAXES_FILE, 'r') as f:
            return jsonify(json.load(f))
    return jsonify([])

@app.route('/api/custom-syntaxes', methods=['POST'])
def save_custom_syntaxes():
    syntaxes = request.json
    with open(CUSTOM_SYNTAXES_FILE, 'w') as f:
        json.dump(syntaxes, f, indent=2)
    
    # Auto-export static HTML after saving syntaxes
    try:
        import subprocess
        import sys
        script_dir = os.path.dirname(os.path.abspath(__file__))
        export_script_path = os.path.join(script_dir, 'export_static.py')
        subprocess.run([sys.executable, export_script_path], 
                      capture_output=True, text=True, cwd=script_dir)
    except Exception as e:
        print(f"Auto-export failed: {e}")
    
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5018)
