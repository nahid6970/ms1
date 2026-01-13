"""Flask backend for Markdown-First Single-Column Sheet System"""
from flask import Flask, render_template, jsonify, request, send_file
import json
import os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = 'data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "categories": [
            {
                "id": "cat_1",
                "name": "Default",
                "order": 0,
                "sheets": [
                    {
                        "id": "sheet_1",
                        "name": "Welcome",
                        "parentId": None,
                        "rows": [
                            {"id": "row_1", "content": "# Welcome to **Markdown Sheets**\n\nStart typing with ==highlights==, **bold**, and more!"}
                        ]
                    }
                ]
            }
        ],
        "lastSheet": "sheet_1",
        "lastCursor": {"row": 0, "pos": 0},
        "customSyntaxes": {}
    }

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify(load_data())

@app.route('/api/data', methods=['POST'])
def update_data():
    data = request.json
    save_data(data)
    return jsonify({"status": "ok"})

@app.route('/api/sheet/<sheet_id>', methods=['PUT'])
def update_sheet(sheet_id):
    data = load_data()
    updates = request.json
    for cat in data['categories']:
        for sheet in cat['sheets']:
            if sheet['id'] == sheet_id:
                sheet.update(updates)
                save_data(data)
                return jsonify({"status": "ok"})
    return jsonify({"error": "Sheet not found"}), 404

@app.route('/api/category', methods=['POST'])
def create_category():
    data = load_data()
    new_cat = {
        "id": f"cat_{datetime.now().timestamp()}",
        "name": request.json.get('name', 'New Category'),
        "order": len(data['categories']),
        "sheets": []
    }
    data['categories'].append(new_cat)
    save_data(data)
    return jsonify(new_cat)

@app.route('/api/sheet', methods=['POST'])
def create_sheet():
    data = load_data()
    req = request.json
    cat_id = req.get('categoryId')
    new_sheet = {
        "id": f"sheet_{datetime.now().timestamp()}",
        "name": req.get('name', 'New Sheet'),
        "parentId": req.get('parentId'),
        "rows": [{"id": f"row_{datetime.now().timestamp()}", "content": ""}]
    }
    for cat in data['categories']:
        if cat['id'] == cat_id:
            cat['sheets'].append(new_sheet)
            save_data(data)
            return jsonify(new_sheet)
    return jsonify({"error": "Category not found"}), 404


@app.route('/api/category/<cat_id>', methods=['DELETE'])
def delete_category(cat_id):
    data = load_data()
    data['categories'] = [c for c in data['categories'] if c['id'] != cat_id]
    save_data(data)
    return jsonify({"status": "ok"})

@app.route('/api/sheet/<sheet_id>', methods=['DELETE'])
def delete_sheet(sheet_id):
    data = load_data()
    for cat in data['categories']:
        cat['sheets'] = [s for s in cat['sheets'] if s['id'] != sheet_id]
    save_data(data)
    return jsonify({"status": "ok"})

@app.route('/api/state', methods=['POST'])
def save_state():
    """Save last sheet and cursor position for seamless reload"""
    data = load_data()
    state = request.json
    if 'lastSheet' in state:
        data['lastSheet'] = state['lastSheet']
    if 'lastCursor' in state:
        data['lastCursor'] = state['lastCursor']
    save_data(data)
    return jsonify({"status": "ok"})

@app.route('/api/custom-syntaxes', methods=['GET'])
def get_custom_syntaxes():
    if os.path.exists('custom_syntaxes.json'):
        with open('custom_syntaxes.json', 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    return jsonify({})

@app.route('/api/custom-syntaxes', methods=['POST'])
def save_custom_syntaxes():
    with open('custom_syntaxes.json', 'w', encoding='utf-8') as f:
        json.dump(request.json, f, indent=2)
    return jsonify({"status": "ok"})

@app.route('/api/export/static')
def export_static():
    """Generate standalone HTML export"""
    data = load_data()
    # Read template and inline all assets
    with open('templates/index.html', 'r', encoding='utf-8') as f:
        html = f.read()
    with open('static/css/style.css', 'r', encoding='utf-8') as f:
        css = f.read()
    with open('static/js/app.js', 'r', encoding='utf-8') as f:
        js = f.read()
    
    static_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Markdown Sheets Export</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
    <style>{css}</style>
</head>
<body>
    <div id="app"></div>
    <script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
    <script>const STATIC_DATA = {json.dumps(data)}; const IS_STATIC = true;</script>
    <script>{js}</script>
</body>
</html>"""
    
    from io import BytesIO
    buffer = BytesIO(static_html.encode('utf-8'))
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='markdown_sheets_export.html', mimetype='text/html')

if __name__ == '__main__':
    app.run(debug=True, port=5099)
