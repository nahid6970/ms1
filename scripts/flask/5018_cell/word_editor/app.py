from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

DATA_FILE = r'C:\Users\nahid\ms\ms1\scripts\flask\5019_word\word_data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'documents': [
            {'name': 'Document1', 'content': '', 'created': '', 'modified': ''}
        ],
        'activeDocument': 0
    }

def save_data(data):
    # Ensure directory exists
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
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

@app.route('/api/data', methods=['POST'])
def save_document_data():
    data = request.json
    # Update modified timestamp
    from datetime import datetime
    if 'activeDocument' in data and data['activeDocument'] < len(data.get('documents', [])):
        data['documents'][data['activeDocument']]['modified'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    save_data(data)
    return jsonify({'success': True})

@app.route('/api/documents', methods=['POST'])
def add_document():
    data = load_data()
    doc_name = request.json.get('name', f'Document{len(data["documents"]) + 1}')
    from datetime import datetime
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data['documents'].append({
        'name': doc_name, 
        'content': '', 
        'created': now, 
        'modified': now
    })
    save_data(data)
    return jsonify({'success': True, 'documentIndex': len(data['documents']) - 1})

@app.route('/api/documents/<int:index>', methods=['DELETE'])
def delete_document(index):
    data = load_data()
    if len(data['documents']) > 1 and 0 <= index < len(data['documents']):
        data['documents'].pop(index)
        if data['activeDocument'] >= len(data['documents']):
            data['activeDocument'] = len(data['documents']) - 1
        save_data(data)
    return jsonify({'success': True})

@app.route('/api/documents/<int:index>/rename', methods=['POST'])
def rename_document(index):
    data = load_data()
    new_name = request.json.get('name')
    if 0 <= index < len(data['documents']) and new_name:
        data['documents'][index]['name'] = new_name
        from datetime import datetime
        data['documents'][index]['modified'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        save_data(data)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, port=5019)