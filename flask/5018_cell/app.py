#!/usr/bin/env python3
from flask import Flask, render_template, request, jsonify
import json
import os
import uuid

app = Flask(__name__)

# Disable caching for development
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.svg')

@app.after_request
def add_header(response):
    # Prevent caching of all responses
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

def normalize_path(path):
    if os.name != 'nt':
        if path.lower().startswith('c:\\') or path.lower().startswith('c:/'):
            home = os.path.expanduser('~')
            rel_path = path[3:].replace('\\', '/')
            return os.path.join(home, rel_path)
        else:
            return path.replace('\\', '/')
    return path

DATA_FILE = normalize_path(r'C:\@delta\ms1\flask\5018_cell\data.json')
STATE_FILE = normalize_path(r'C:\@delta\output\5018_output\sheet_active.json')
CUSTOM_SYNTAXES_FILE = normalize_path(r'C:\@delta\ms1\flask\5018_cell\custom_syntaxes.json')
QUICK_TEXTS_FILE = normalize_path(r'C:\@delta\ms1\flask\5018_cell\quick_texts.json')
SYNTAX_REPLACE_PINS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'syntax_replace_pins.json')
SETTINGS_FILE = normalize_path(r'C:\@delta\db\5018_cell\setting.json')

# Pending CLI edits stay in memory until a user approves or rejects them.
AI_CELL_PROPOSALS = {}

def load_data():
    data = {
        'sheets': [
            {
                'name': 'Sheet1',
                'columns': [
                    {
                        'name': 'A',
                        'type': 'text',
                        'width': 150,
                        'color': '#ffffff',
                        'textColor': '#000000',
                        'font': 'JetBrains Mono',
                        'fontSize': 20,
                        'headerBgColor': '#f8f9fa',
                        'headerTextColor': '#333333',
                        'headerBold': True,
                        'headerItalic': False,
                        'headerCenter': False
                    }
                ],
                'rows': [['']]
            }
        ],
        'activeSheet': 0
    }
    
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            file_data = json.load(f)
            data.update(file_data)
            
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    state_data = json.loads(content)
                    if 'activeSheet' in state_data:
                        data['activeSheet'] = state_data['activeSheet']
        except (json.JSONDecodeError, ValueError):
            pass
                
    return data

def save_data(data):
    # Save activeSheet to state file
    state = {'activeSheet': data.get('activeSheet', 0)}
    # Ensure directory exists
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, sort_keys=True)
        
    # Save sheets to data file (excluding activeSheet)
    content = {k: v for k, v in data.items() if k != 'activeSheet'}
    
    # Check if data has actually changed before writing
    existing_content = None
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                existing_content = json.load(f)
        except:
            existing_content = None
    
    # Compare: only write if content is different
    if existing_content != content:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, sort_keys=True, ensure_ascii=False)
        
        # Auto-export static HTML ONLY if data actually changed
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
    else:
        print("No changes detected, skipping save and export")

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
    data = request.get_json(silent=True)
    if data is None:
        raw_body = request.get_data(as_text=True)
        if raw_body:
            try:
                data = json.loads(raw_body)
            except json.JSONDecodeError:
                data = None

    if data is None:
        return jsonify({'success': False, 'error': 'Invalid JSON payload'}), 400

    save_data(data)
    return jsonify({'success': True})

@app.route('/api/sheets', methods=['POST'])
def add_sheet():
    data = load_data()
    sheet_name = request.json.get('name', f'Sheet{len(data["sheets"]) + 1}')
    parent_sheet = request.json.get('parentSheet', None)
    
    # Initialize with 1 column (A) and 1 empty row
    default_column = {
        'name': 'A',
        'type': 'text',
        'width': 150,
        'color': '#ffffff',
        'textColor': '#000000',
        'font': 'JetBrains Mono',
        'fontSize': 20,
        'headerBgColor': '#f8f9fa',
        'headerTextColor': '#333333',
        'headerBold': True,
        'headerItalic': False,
        'headerCenter': False
    }
    new_sheet = {
        'name': sheet_name, 
        'columns': [default_column], 
        'rows': [['']]
    }
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

@app.route('/api/sheets/<int:index>/set-custom-index', methods=['POST'])
def set_sheet_custom_index(index):
    data = load_data()
    custom_index = request.json.get('customIndex')
    if 0 <= index < len(data['sheets']):
        data['sheets'][index]['customIndex'] = custom_index
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
    req_json = request.json or {}
    sheet_index = req_json.get('sheetIndex', data['activeSheet'])
    position = req_json.get('position', 'top')
    sheet = data['sheets'][sheet_index]
    
    new_row = ['' for _ in sheet['columns']]
    if position == 'top':
        # Shift cellStyles keys down by 1 row
        cell_styles = sheet.get('cellStyles', {})
        if cell_styles:
            new_cell_styles = {}
            for key, style in cell_styles.items():
                parts = key.split('-')
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    r, c = int(parts[0]), int(parts[1])
                    new_cell_styles[f"{r + 1}-{c}"] = style
                else:
                    new_cell_styles[key] = style
            sheet['cellStyles'] = new_cell_styles
        
        sheet['rows'].insert(0, new_row)
    else:
        sheet['rows'].append(new_row)
        
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
        with open(CUSTOM_SYNTAXES_FILE, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    return jsonify([])

@app.route('/api/custom-syntaxes', methods=['POST'])
def save_custom_syntaxes():
    syntaxes = request.json
    with open(CUSTOM_SYNTAXES_FILE, 'w', encoding='utf-8') as f:
        json.dump(syntaxes, f, indent=2, ensure_ascii=False)
    
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

@app.route('/api/quick-texts', methods=['GET'])
def get_quick_texts():
    if os.path.exists(QUICK_TEXTS_FILE):
        with open(QUICK_TEXTS_FILE, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    return jsonify([])

@app.route('/api/quick-texts', methods=['POST'])
def save_quick_texts():
    items = request.json
    with open(QUICK_TEXTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    return jsonify({'success': True})

@app.route('/api/syntax-replace-pins', methods=['GET'])
def get_syntax_replace_pins():
    try:
        with open(SYNTAX_REPLACE_PINS_FILE, 'r', encoding='utf-8') as f:
            pins = json.load(f)
        return jsonify(pins if isinstance(pins, list) else [])
    except FileNotFoundError:
        return jsonify([])
    except (OSError, json.JSONDecodeError):
        return jsonify([])

@app.route('/api/syntax-replace-pins', methods=['POST'])
def save_syntax_replace_pins():
    pins = request.get_json(silent=True)
    if not isinstance(pins, list) or any(
        not isinstance(item, dict)
        or not all(isinstance(item.get(key), str) for key in ('find', 'replace', 'side'))
        for item in pins
    ):
        return jsonify({'success': False, 'error': 'Expected a list of find/replace/side patterns'}), 400
    with open(SYNTAX_REPLACE_PINS_FILE, 'w', encoding='utf-8') as f:
        json.dump(pins, f, indent=2, ensure_ascii=False)
    return jsonify({'success': True})

@app.route('/api/settings', methods=['GET'])
def get_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return jsonify(json.load(f))
        except:
            return jsonify({})
    return jsonify({})

@app.route('/api/settings', methods=['POST'])
def save_settings():
    settings = request.json
    try:
        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, sort_keys=True, ensure_ascii=False)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/open-file', methods=['POST'])
def open_file():
    import subprocess, os, sys
    path = request.json.get('path', '')
    # Strip file:/// prefix
    if path.startswith('file:///'):
        path = path[8:]
    path = normalize_path(path)
    if os.path.exists(path):
        if hasattr(os, 'startfile'):
            os.startfile(path)
        else:
            if sys.platform == 'darwin':
                subprocess.run(['open', path], check=False)
            else:
                subprocess.run(['xdg-open', path], check=False)
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'File not found'}), 404

# ─────────────────────────────────────────────
# AI-accessible endpoints  (/ai/*)
# Sheets can be addressed by arrayIndex (int) or customIndex (14-digit string)
# ─────────────────────────────────────────────

@app.route('/ai/syntaxes', methods=['GET'])
def ai_get_syntax_reference():
    """Return built-in syntax guidance and the currently configured custom markers."""
    project_dir = os.path.dirname(os.path.abspath(__file__))

    def read_reference(relative_path):
        path = os.path.join(project_dir, relative_path)
        try:
            with open(path, 'r', encoding='utf-8') as reference_file:
                return reference_file.read()
        except OSError:
            return ''

    custom_syntaxes = []
    if os.path.exists(CUSTOM_SYNTAXES_FILE):
        try:
            with open(CUSTOM_SYNTAXES_FILE, 'r', encoding='utf-8') as syntax_file:
                custom_syntaxes = json.load(syntax_file)
        except (OSError, json.JSONDecodeError):
            custom_syntaxes = []

    custom_syntax_examples = []
    for syntax in custom_syntaxes if isinstance(custom_syntaxes, list) else []:
        if not isinstance(syntax, dict):
            continue
        if syntax.get('type') == 'prefixSuffix':
            prefix = str(syntax.get('prefix') or '')
            suffix = str(syntax.get('suffix') or '')
        else:
            prefix = suffix = str(syntax.get('marker') or '')
        if not prefix or not suffix:
            continue
        custom_syntax_examples.append({
            'example': f'{prefix}text{suffix}',
            'prefix': prefix,
            'suffix': suffix,
            'prefixCodePoints': [f'U+{ord(character):04X}' for character in prefix],
            'suffixCodePoints': [f'U+{ord(character):04X}' for character in suffix],
        })

    response_data = {
        'builtInSyntaxGuide': read_reference(os.path.join('md', 'MARKDOWN_SPECIAL.md')),
        'aiCellSyntaxGuidance': read_reference(os.path.join('md', 'AI_CELL_INSTRUCTIONS.md')),
        'customSyntaxes': custom_syntaxes,
        'customSyntaxExamples': custom_syntax_examples,
        'parserSource': ['static/script.js'],
    }
    # Preserve literal Unicode markers in the response while also publishing their code points.
    return app.response_class(
        response=json.dumps(response_data, ensure_ascii=False),
        status=200,
        mimetype='application/json',
    )

def resolve_sheet(data, sheet_id):
    """Return (sheet_obj, array_index) or (None, None) if not found."""
    sheets = data.get('sheets', [])
    sid = str(sheet_id)
    # customIndex is always a 14-digit timestamp string
    if len(sid) == 14 and sid.isdigit():
        for i, s in enumerate(sheets):
            if str(s.get('customIndex', '')) == sid:
                return s, i
        return None, None
    # fall back to numeric array index
    try:
        idx = int(sid)
        if 0 <= idx < len(sheets):
            return sheets[idx], idx
    except (ValueError, TypeError):
        pass
    return None, None

@app.route('/ai/schema', methods=['GET'])
def ai_schema():
    data = load_data()
    sheets = data.get('sheets', [])
    cats = data.get('sheetCategories', {})
    result = []
    for i, s in enumerate(sheets):
        result.append({
            'arrayIndex': i,
            'customIndex': s.get('customIndex'),
            'name': s.get('name', ''),
            'nickname': s.get('nickname', ''),
            'category': cats.get(str(i)),
            'parentSheet': s.get('parentSheet'),
            'colCount': len(s.get('columns', [])),
            'rowCount': len(s.get('rows', [])),
            'columns': [c.get('name') for c in s.get('columns', [])],
        })
    return jsonify({'sheets': result, 'categories': data.get('categories', [])})

@app.route('/ai/sheet/<sheet_id>', methods=['GET'])
def ai_get_sheet(sheet_id):
    data = load_data()
    sheet, idx = resolve_sheet(data, sheet_id)
    if sheet is None:
        return jsonify({'error': 'Sheet not found'}), 404
    return jsonify({
        'arrayIndex': idx,
        'customIndex': sheet.get('customIndex'),
        'name': sheet.get('name', ''),
        'columns': [c.get('name') for c in sheet.get('columns', [])],
        'rows': sheet.get('rows', []),
        'cellStyles': sheet.get('cellStyles', {}),
    })

@app.route('/ai/cell/<sheet_id>/<int:row>/<int:col>', methods=['GET'])
def ai_get_cell(sheet_id, row, col):
    data = load_data()
    sheet, idx = resolve_sheet(data, sheet_id)
    if sheet is None:
        return jsonify({'error': 'Sheet not found'}), 404
    rows = sheet.get('rows', [])
    if row >= len(rows) or col >= len(rows[row]):
        return jsonify({'error': 'Cell out of range'}), 404
    return jsonify({
        'sheetIndex': idx,
        'customIndex': sheet.get('customIndex'),
        'row': row, 'col': col,
        'value': rows[row][col],
        'style': sheet.get('cellStyles', {}).get(f'{row}-{col}'),
    })

@app.route('/ai/cell/<sheet_id>/<int:row>/<int:col>', methods=['POST'])
def ai_set_cell(sheet_id, row, col):
    data = load_data()
    sheet, _ = resolve_sheet(data, sheet_id)
    if sheet is None:
        return jsonify({'error': 'Sheet not found'}), 404
    rows = sheet.get('rows', [])
    if row >= len(rows) or col >= len(rows[row]):
        return jsonify({'error': 'Cell out of range'}), 404
    value = request.json.get('value', '')
    rows[row][col] = value
    save_data(data)
    return jsonify({'success': True, 'row': row, 'col': col, 'value': value})

@app.route('/ai/cell/<sheet_id>/<int:row>/<int:col>/proposal', methods=['POST'])
def ai_propose_cell_update(sheet_id, row, col):
    """Queue a cell update for in-app review instead of applying it immediately."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or 'value' not in payload:
        return jsonify({'error': 'Expected JSON with a value field'}), 400

    data = load_data()
    sheet, sheet_index = resolve_sheet(data, sheet_id)
    if sheet is None:
        return jsonify({'error': 'Sheet not found'}), 404
    rows = sheet.get('rows', [])
    if row >= len(rows) or col >= len(rows[row]):
        return jsonify({'error': 'Cell out of range'}), 404

    columns = sheet.get('columns') or []
    column_name = columns[col].get('name', f'Column {col + 1}') if col < len(columns) else f'Column {col + 1}'
    proposal_id = str(uuid.uuid4())
    proposal = {
        'id': proposal_id,
        'sheetId': str(sheet.get('customIndex') or sheet_index),
        'sheetIndex': sheet_index,
        'sheetName': sheet.get('name', ''),
        'row': row,
        'col': col,
        'columnName': column_name,
        'originalValue': rows[row][col],
        'proposedValue': payload['value'],
    }
    AI_CELL_PROPOSALS[proposal_id] = proposal
    return jsonify({'success': True, 'proposalId': proposal_id, 'status': 'pending_review'}), 202

@app.route('/ai/proposals', methods=['GET'])
def ai_get_cell_proposals():
    return jsonify({'proposals': list(AI_CELL_PROPOSALS.values())})

@app.route('/ai/proposals/<proposal_id>/approve', methods=['POST'])
def ai_approve_cell_proposal(proposal_id):
    proposal = AI_CELL_PROPOSALS.get(proposal_id)
    if proposal is None:
        return jsonify({'error': 'Proposal not found or already handled'}), 404

    data = load_data()
    sheet, _ = resolve_sheet(data, proposal['sheetId'])
    if sheet is None:
        return jsonify({'error': 'Sheet not found'}), 404
    rows = sheet.get('rows', [])
    row, col = proposal['row'], proposal['col']
    if row >= len(rows) or col >= len(rows[row]):
        return jsonify({'error': 'Cell out of range'}), 404
    if rows[row][col] != proposal['originalValue']:
        return jsonify({'error': 'Cell changed after this proposal was created; review the latest value before applying.'}), 409

    rows[row][col] = proposal['proposedValue']
    save_data(data)
    AI_CELL_PROPOSALS.pop(proposal_id, None)
    return jsonify({'success': True, 'proposal': proposal})

@app.route('/ai/proposals/<proposal_id>', methods=['DELETE'])
def ai_reject_cell_proposal(proposal_id):
    if AI_CELL_PROPOSALS.pop(proposal_id, None) is None:
        return jsonify({'error': 'Proposal not found or already handled'}), 404
    return jsonify({'success': True})

@app.route('/ai/cells', methods=['POST'])
def ai_set_cells():
    """Batch update. Body: [{"sheet": id, "row": r, "col": c, "value": v}, ...]"""
    data = load_data()
    updates = request.json
    if not isinstance(updates, list):
        return jsonify({'error': 'Expected a list of updates'}), 400
    results = []
    for u in updates:
        sheet, _ = resolve_sheet(data, u.get('sheet'))
        if sheet is None:
            results.append({'error': 'Sheet not found', 'update': u})
            continue
        r, c, v = u.get('row'), u.get('col'), u.get('value', '')
        rows = sheet.get('rows', [])
        if r is None or c is None or r >= len(rows) or c >= len(rows[r]):
            results.append({'error': 'Cell out of range', 'update': u})
            continue
        rows[r][c] = v
        results.append({'success': True, 'row': r, 'col': c})
    save_data(data)
    return jsonify(results)

@app.route('/ai/find', methods=['GET'])
def ai_find():
    """GET /ai/find?sheet=<id>&q=<text>  — case-insensitive substring match."""
    sheet_id = request.args.get('sheet')
    query = request.args.get('q', '').lower()
    if not sheet_id or not query:
        return jsonify({'error': 'sheet and q params required'}), 400
    data = load_data()
    sheet, idx = resolve_sheet(data, sheet_id)
    if sheet is None:
        return jsonify({'error': 'Sheet not found'}), 404
    matches = []
    for r, row in enumerate(sheet.get('rows', [])):
        for c, cell in enumerate(row):
            if query in str(cell).lower():
                matches.append({'row': r, 'col': c, 'value': cell})
    return jsonify({'sheetIndex': idx, 'query': query, 'matches': matches})


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5018)
