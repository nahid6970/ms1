from flask import Flask, render_template, jsonify, request, send_from_directory
import json
import os
import subprocess
import sys
import requests
from datetime import datetime

app = Flask(__name__)

DATA_FILE = r'C:\@delta\ms1\flask\5000_myhome\data.json'
SIDEBAR_BUTTONS_FILE = r'C:\@delta\ms1\flask\5000_myhome\sidebar_buttons.json'

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

# Helper function to read sidebar buttons from JSON file
def read_sidebar_buttons():
    if not os.path.exists(SIDEBAR_BUTTONS_FILE):
        # Default sidebar buttons
        default_buttons = [
            {
                "id": "tv-button",
                "name": "TV Shows",
                "display_type": "icon",
                "icon_class": "nf nf-md-television_classic",
                "img_src": "",
                "url": "http://192.168.0.101:5011/",
                "has_notification": True,
                "notification_api": "/api/tv-notifications",
                "mark_seen_api": "/api/mark-all-tv-seen",
                "text_color": "#000000",
                "bg_color": "#ffffff",
                "hover_color": "#e0e0e0",
                "border_color": "#cccccc",
                "border_radius": "4px",
                "font_size": "16px"
            },
            {
                "id": "movie-button", 
                "name": "Movies",
                "display_type": "icon",
                "icon_class": "nf nf-md-movie_roll",
                "img_src": "",
                "url": "http://192.168.0.101:5013/",
                "has_notification": True,
                "notification_api": "/api/movie-notifications",
                "mark_seen_api": "/api/mark-all-movies-seen",
                "text_color": "#000000",
                "bg_color": "#ffffff",
                "hover_color": "#e0e0e0",
                "border_color": "#cccccc",
                "border_radius": "4px",
                "font_size": "16px"
            },
            {
                "id": "drive-button",
                "name": "Drive",
                "display_type": "icon",
                "icon_class": "nf nf-fa-hard_drive",
                "img_src": "",
                "url": "http://192.168.0.101:5003/",
                "has_notification": False,
                "text_color": "#000000",
                "bg_color": "#ffffff",
                "hover_color": "#e0e0e0",
                "border_color": "#cccccc",
                "border_radius": "4px",
                "font_size": "16px"
            },
            {
                "id": "education-button",
                "name": "Education",
                "display_type": "icon",
                "icon_class": "nf nf-md-book_education", 
                "img_src": "",
                "url": "http://192.168.0.101:5015/",
                "has_notification": False,
                "text_color": "#000000",
                "bg_color": "#ffffff",
                "hover_color": "#e0e0e0",
                "border_color": "#cccccc",
                "border_radius": "4px",
                "font_size": "16px"
            },
            {
                "id": "rocket-button",
                "name": "Rocket",
                "display_type": "icon",
                "icon_class": "nf nf-fa-rocket",
                "img_src": "",
                "url": "http://192.168.0.101:4999/",
                "has_notification": False,
                "text_color": "#000000",
                "bg_color": "#ffffff",
                "hover_color": "#e0e0e0",
                "border_color": "#cccccc",
                "border_radius": "4px",
                "font_size": "16px"
            },
            {
                "id": "apps-button",
                "name": "Apps",
                "display_type": "icon",
                "icon_class": "nf nf-oct-apps",
                "img_src": "",
                "url": "http://192.168.0.101:4998/",
                "has_notification": False,
                "text_color": "#000000",
                "bg_color": "#ffffff",
                "hover_color": "#e0e0e0",
                "border_color": "#cccccc",
                "border_radius": "4px",
                "font_size": "16px"
            },
            {
                "id": "terminal-button",
                "name": "Terminal",
                "display_type": "icon",
                "icon_class": "nf nf-dev-terminal",
                "img_src": "",
                "url": "http://192.168.0.101:5555/",
                "has_notification": False,
                "text_color": "#000000",
                "bg_color": "#ffffff",
                "hover_color": "#e0e0e0",
                "border_color": "#cccccc",
                "border_radius": "4px",
                "font_size": "16px"
            }
        ]
        write_sidebar_buttons(default_buttons)
        return default_buttons
    with open(SIDEBAR_BUTTONS_FILE, 'r') as f:
        return json.load(f)

# Helper function to write sidebar buttons to JSON file
def write_sidebar_buttons(data):
    with open(SIDEBAR_BUTTONS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Function to generate static HTML
def generate_static_html():
    """Generate static HTML file with embedded CSS and JS"""
    try:
        # Run the generate_static.py script from current directory
        result = subprocess.run(['pythonw', r'C:\@delta\ms1\flask\5000_myhome\generate_static.py'], 
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
    # Ensure horizontal_stack is set, default to false if not provided
    if 'horizontal_stack' not in new_link:
        new_link['horizontal_stack'] = False
    
    links = read_data()
    
    # If this link belongs to an existing group, inherit the group properties
    group_name = new_link.get('group')
    if group_name:
        # Look for an existing link in the same group to copy properties from
        for existing_link in links:
            if existing_link.get('group') == group_name:
                # Copy group-level properties
                if 'collapsible' in existing_link:
                    new_link['collapsible'] = existing_link['collapsible']
                if 'display_style' in existing_link:
                    new_link['display_style'] = existing_link['display_style']
                if 'horizontal_stack' in existing_link:
                    new_link['horizontal_stack'] = existing_link['horizontal_stack']
                if 'password_protect' in existing_link:
                    new_link['password_protect'] = existing_link['password_protect']
                if 'top_name' in existing_link:
                    new_link['top_name'] = existing_link['top_name']
                if 'top_bg_color' in existing_link:
                    new_link['top_bg_color'] = existing_link['top_bg_color']
                if 'top_text_color' in existing_link:
                    new_link['top_text_color'] = existing_link['top_text_color']
                if 'top_border_color' in existing_link:
                    new_link['top_border_color'] = existing_link['top_border_color']
                if 'top_hover_color' in existing_link:
                    new_link['top_hover_color'] = existing_link['top_hover_color']
                if 'popup_bg_color' in existing_link:
                    new_link['popup_bg_color'] = existing_link['popup_bg_color']
                if 'popup_text_color' in existing_link:
                    new_link['popup_text_color'] = existing_link['popup_text_color']
                if 'popup_border_color' in existing_link:
                    new_link['popup_border_color'] = existing_link['popup_border_color']
                if 'popup_border_radius' in existing_link:
                    new_link['popup_border_radius'] = existing_link['popup_border_radius']
                if 'horizontal_bg_color' in existing_link:
                    new_link['horizontal_bg_color'] = existing_link['horizontal_bg_color']
                if 'horizontal_text_color' in existing_link:
                    new_link['horizontal_text_color'] = existing_link['horizontal_text_color']
                if 'horizontal_border_color' in existing_link:
                    new_link['horizontal_border_color'] = existing_link['horizontal_border_color']
                if 'horizontal_hover_color' in existing_link:
                    new_link['horizontal_hover_color'] = existing_link['horizontal_hover_color']
                break  # Only need to copy from one existing link in the group
    
    links.append(new_link)
    write_data(links)
    return jsonify({'message': 'Link added successfully'}), 201

@app.route('/api/links/<int:link_id>', methods=['PUT'])
def edit_link(link_id):
    updated_link = request.json
    # Ensure default_type is set, default to 'nerd-font' if not provided
    if 'default_type' not in updated_link or not updated_link['default_type']:
        updated_link['default_type'] = 'nerd-font'
    # Ensure horizontal_stack is set, default to false if not provided
    if 'horizontal_stack' not in updated_link:
        updated_link['horizontal_stack'] = False
    links = read_data()
    if 0 <= link_id < len(links):
        # Get the original link to check if group is changing
        original_link = links[link_id]
        original_group = original_link.get('group')
        new_group = updated_link.get('group')
        
        # If the link is being moved to a different group, inherit properties from the new group
        if original_group != new_group:
            # Look for an existing link in the new group to copy properties from
            for existing_link in links:
                if existing_link.get('group') == new_group:
                    # Copy group-level properties
                    if 'collapsible' in existing_link:
                        updated_link['collapsible'] = existing_link['collapsible']
                    if 'display_style' in existing_link:
                        updated_link['display_style'] = existing_link['display_style']
                    if 'horizontal_stack' in existing_link:
                        updated_link['horizontal_stack'] = existing_link['horizontal_stack']
                    if 'password_protect' in existing_link:
                        updated_link['password_protect'] = existing_link['password_protect']
                    if 'top_name' in existing_link:
                        updated_link['top_name'] = existing_link['top_name']
                    if 'top_bg_color' in existing_link:
                        updated_link['top_bg_color'] = existing_link['top_bg_color']
                    if 'top_text_color' in existing_link:
                        updated_link['top_text_color'] = existing_link['top_text_color']
                    if 'top_border_color' in existing_link:
                        updated_link['top_border_color'] = existing_link['top_border_color']
                    if 'top_hover_color' in existing_link:
                        updated_link['top_hover_color'] = existing_link['top_hover_color']
                    if 'popup_bg_color' in existing_link:
                        updated_link['popup_bg_color'] = existing_link['popup_bg_color']
                    if 'popup_text_color' in existing_link:
                        updated_link['popup_text_color'] = existing_link['popup_text_color']
                    if 'popup_border_color' in existing_link:
                        updated_link['popup_border_color'] = existing_link['popup_border_color']
                    if 'popup_border_radius' in existing_link:
                        updated_link['popup_border_radius'] = existing_link['popup_border_radius']
                    if 'horizontal_bg_color' in existing_link:
                        updated_link['horizontal_bg_color'] = existing_link['horizontal_bg_color']
                    if 'horizontal_text_color' in existing_link:
                        updated_link['horizontal_text_color'] = existing_link['horizontal_text_color']
                    if 'horizontal_border_color' in existing_link:
                        updated_link['horizontal_border_color'] = existing_link['horizontal_border_color']
                    if 'horizontal_hover_color' in existing_link:
                        updated_link['horizontal_hover_color'] = existing_link['horizontal_hover_color']
                    break  # Only need to copy from one existing link in the group
            
            # Remove the link from its original position
            removed_link = links.pop(link_id)
            
            # Add the updated link to the end of the list to maintain proper group ordering
            links.append(updated_link)
        else:
            # If staying in the same group, just update in place
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
        return jsonify({'message': 'Static HTML generated successfully', 'file': r'C:\@delta\ms1\myhome\myhome.html'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trigger-scan', methods=['POST'])
def trigger_scan():
    """Trigger scan for both TV shows and movies"""
    try:
        results = {
            'tv_scan': {'success': False, 'message': ''},
            'movie_scan': {'success': False, 'message': ''}
        }
        
        # Trigger TV show scan (blue scan button on port 5011)
        try:
            tv_scan_response = requests.post('http://192.168.0.101:5011/scan', timeout=30)
            if tv_scan_response.status_code == 200:
                results['tv_scan']['success'] = True
                results['tv_scan']['message'] = 'TV show scan completed'
            else:
                results['tv_scan']['message'] = f'TV scan failed with status {tv_scan_response.status_code}'
        except requests.exceptions.RequestException as e:
            results['tv_scan']['message'] = f'TV scan error: {str(e)}'
        
        # Trigger movie scan (green sync button on port 5013)
        try:
            movie_scan_response = requests.post('http://192.168.0.101:5013/sync', timeout=30)
            if movie_scan_response.status_code == 200:
                results['movie_scan']['success'] = True
                results['movie_scan']['message'] = 'Movie sync completed'
            else:
                results['movie_scan']['message'] = f'Movie sync failed with status {movie_scan_response.status_code}'
        except requests.exceptions.RequestException as e:
            results['movie_scan']['message'] = f'Movie sync error: {str(e)}'
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tv-notifications')
def get_tv_notifications():
    """Get unseen episode count from TV show app"""
    try:
        response = requests.get('http://192.168.0.101:5011/api/unseen_count', timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return jsonify({'unseen_count': 0, 'error': 'Failed to fetch count'})
    except requests.exceptions.RequestException as e:
        return jsonify({'unseen_count': 0, 'error': str(e)})

@app.route('/api/movie-notifications')
def get_movie_notifications():
    """Get unseen movie count from movie app"""
    try:
        response = requests.get('http://192.168.0.101:5013/get_unseen_notifications', timeout=10)
        if response.status_code == 200:
            data = response.json()
            return jsonify({'unseen_count': data.get('count', 0), 'movies': data.get('movies', [])})
        else:
            return jsonify({'unseen_count': 0, 'error': 'Failed to fetch movie count'})
    except requests.exceptions.RequestException as e:
        return jsonify({'unseen_count': 0, 'error': str(e)})

@app.route('/api/mark-all-tv-seen', methods=['POST'])
def mark_all_tv_seen():
    """Mark all TV episodes as seen"""
    try:
        response = requests.post('http://192.168.0.101:5011/api/mark_all_seen', timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            return jsonify({'success': False, 'error': 'Failed to mark episodes as seen'})
    except requests.exceptions.RequestException as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/mark-all-movies-seen', methods=['POST'])
def mark_all_movies_seen():
    """Mark all movies as seen"""
    try:
        # First get all unseen movies
        response = requests.get('http://192.168.0.101:5013/get_unseen_notifications', timeout=10)
        if response.status_code != 200:
            return jsonify({'success': False, 'error': 'Failed to fetch unseen movies'})
        
        data = response.json()
        movies = data.get('movies', [])
        updated_count = 0
        
        # Mark each movie as seen
        for movie in movies:
            movie_id = movie.get('id')
            if movie_id:
                update_response = requests.post(
                    f'http://192.168.0.101:5013/update_notify/{movie_id}',
                    json={'notify': 'seen'},
                    timeout=10
                )
                if update_response.status_code == 200:
                    updated_count += 1
        
        return jsonify({'success': True, 'updated_count': updated_count})
        
    except requests.exceptions.RequestException as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/sidebar-buttons', methods=['GET'])
def get_sidebar_buttons():
    """Get all sidebar buttons"""
    buttons = read_sidebar_buttons()
    return jsonify(buttons)

@app.route('/api/sidebar-buttons', methods=['PUT'])
def update_sidebar_buttons():
    """Update all sidebar buttons"""
    new_buttons = request.json
    write_sidebar_buttons(new_buttons)
    return jsonify({'message': 'Sidebar buttons updated successfully'})

@app.route('/api/sidebar-buttons', methods=['POST'])
def add_sidebar_button():
    """Add a new sidebar button"""
    new_button = request.json
    buttons = read_sidebar_buttons()
    buttons.append(new_button)
    write_sidebar_buttons(buttons)
    return jsonify({'message': 'Sidebar button added successfully'}), 201

@app.route('/api/sidebar-buttons/<int:button_index>', methods=['PUT'])
def edit_sidebar_button(button_index):
    """Edit a sidebar button"""
    updated_button = request.json
    buttons = read_sidebar_buttons()
    if 0 <= button_index < len(buttons):
        buttons[button_index] = updated_button
        write_sidebar_buttons(buttons)
        return jsonify({'message': 'Sidebar button updated successfully'})
    return jsonify({'message': 'Button not found'}), 404

@app.route('/api/sidebar-buttons/<int:button_index>', methods=['DELETE'])
def delete_sidebar_button(button_index):
    """Delete a sidebar button"""
    buttons = read_sidebar_buttons()
    if 0 <= button_index < len(buttons):
        deleted_button = buttons.pop(button_index)
        write_sidebar_buttons(buttons)
        return jsonify({'message': 'Sidebar button deleted successfully', 'deleted_button': deleted_button})
    return jsonify({'message': 'Button not found'}), 404

@app.route('/open-file')
def open_file():
    """Open local files using the default system application"""
    file_path = request.args.get('path')
    if not file_path:
        return jsonify({'error': 'No file path provided'}), 400
    
    try:
        # URL decode the file path
        import urllib.parse
        decoded_path = urllib.parse.unquote(file_path)
        
        # Convert forward slashes to backslashes for Windows
        if os.name == 'nt':  # Windows
            decoded_path = decoded_path.replace('/', '\\')
        
        # Check if file exists
        if not os.path.exists(decoded_path):
            return jsonify({'error': f'File not found: {decoded_path}'}), 404
        
        # Use subprocess to open the file with the default application
        if os.name == 'nt':  # Windows
            os.startfile(decoded_path)
        elif os.name == 'posix':  # macOS and Linux
            subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', decoded_path])
        
        return jsonify({'success': True, 'message': f'Opened {decoded_path}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/preview-note')
def preview_note():
    """Preview note content as rendered Markdown"""
    note_content = request.args.get('content', '')
    
    if not note_content:
        html_content = '<h2>No note content to preview</h2>'
    else:
        # Convert Markdown syntax to HTML
        html_content = convert_markdown_to_html(note_content)
    
    # Use the dedicated template
    return render_template('note_preview.html', content=html_content)

def convert_markdown_to_html(text):
    """Convert Markdown syntax to HTML"""
    import re
    
    # Escape HTML characters first
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    # Split into lines for better processing
    lines = text.split('\n')
    html_lines = []
    in_code_block = False
    code_block_content = []
    
    for line in lines:
        original_line = line
        line_stripped = line.strip()
        
        # Handle code blocks first
        if line_stripped.startswith('```'):
            if in_code_block:
                # End code block
                code_content = '\n'.join(code_block_content)
                html_lines.append(f'<pre><code>{code_content}</code></pre>')
                code_block_content = []
                in_code_block = False
            else:
                # Start code block
                in_code_block = True
            continue
        
        if in_code_block:
            code_block_content.append(line)
            continue
        
        if not line_stripped:
            # Empty line - will be handled as paragraph break
            html_lines.append('')
            continue
            
        # Check for headers (Markdown uses # for headers)
        if re.match(r'^#{1,6} ', line_stripped):
            level = len(re.match(r'^#+', line_stripped).group())
            header_text = re.sub(r'^#+ ', '', line_stripped)
            html_lines.append(f'<h{level}>{header_text}</h{level}>')
        # Check for lists
        elif re.match(r'^[-*+] ', line_stripped):
            list_text = re.sub(r'^[-*+] ', '', line_stripped)
            html_lines.append(f'<li>{list_text}</li>')
        elif re.match(r'^\d+\. ', line_stripped):
            list_text = re.sub(r'^\d+\. ', '', line_stripped)
            html_lines.append(f'<li>{list_text}</li>')
        # Check for blockquotes
        elif line_stripped.startswith('> '):
            quote_text = re.sub(r'^> ', '', line_stripped)
            html_lines.append(f'<blockquote>{quote_text}</blockquote>')
        else:
            html_lines.append(line_stripped)
    
    # Now join and create proper HTML structure
    result = []
    current_paragraph = []
    current_list = []
    list_type = None
    
    for line in html_lines:
        if line == '':
            # Empty line - end current paragraph/list if any
            if current_paragraph:
                paragraph_text = '<br>'.join(current_paragraph)
                result.append(f'<p>{paragraph_text}</p>')
                current_paragraph = []
            if current_list:
                list_tag = 'ul' if list_type == 'unordered' else 'ol'
                result.append(f'<{list_tag}>{"".join(current_list)}</{list_tag}>')
                current_list = []
                list_type = None
        elif line.startswith('<h') or line.startswith('<pre') or line.startswith('<blockquote'):
            # Block element - end current paragraph/list and add the block
            if current_paragraph:
                paragraph_text = '<br>'.join(current_paragraph)
                result.append(f'<p>{paragraph_text}</p>')
                current_paragraph = []
            if current_list:
                list_tag = 'ul' if list_type == 'unordered' else 'ol'
                result.append(f'<{list_tag}>{"".join(current_list)}</{list_tag}>')
                current_list = []
                list_type = None
            result.append(line)
        elif line.startswith('<li>'):
            # List item - add to current list
            if current_paragraph:
                paragraph_text = '<br>'.join(current_paragraph)
                result.append(f'<p>{paragraph_text}</p>')
                current_paragraph = []
            current_list.append(line)
            if list_type is None:
                list_type = 'unordered'  # Default to unordered
        else:
            # Regular text - add to current paragraph
            if current_list:
                list_tag = 'ul' if list_type == 'unordered' else 'ol'
                result.append(f'<{list_tag}>{"".join(current_list)}</{list_tag}>')
                current_list = []
                list_type = None
            current_paragraph.append(line)
    
    # Don't forget the last paragraph/list
    if current_paragraph:
        paragraph_text = '<br>'.join(current_paragraph)
        result.append(f'<p>{paragraph_text}</p>')
    if current_list:
        list_tag = 'ul' if list_type == 'unordered' else 'ol'
        result.append(f'<{list_tag}>{"".join(current_list)}</{list_tag}>')
    
    text = '\n'.join(result)
    
    # Now apply inline formatting
    # Bold and italic (Markdown syntax)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)  # **bold**
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)  # *italic*
    text = re.sub(r'__([^_]+)__', r'<strong>\1</strong>', text)  # __bold__
    text = re.sub(r'_([^_]+)_', r'<em>\1</em>', text)  # _italic_
    text = re.sub(r'~~([^~]+)~~', r'<del>\1</del>', text)  # ~~strikethrough~~
    
    # Inline code (Markdown syntax)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)  # `code`
    
    # Links (Markdown syntax: [text](url))
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', text)
    
    return text

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)