#!/usr/bin/env python3
"""
Static HTML Generator for MyHome
Generates a standalone HTML file with embedded CSS and JavaScript
"""

import json
import os
from datetime import datetime

# --- Configuration ---
# Get the absolute path of the directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = SCRIPT_DIR  # Assuming the script is in the project root

# Path to the data files
DATA_FILE = r'C:\@delta\ms1\@Flask\5000_myhome\data.json'
SIDEBAR_BUTTONS_FILE = r'C:\@delta\ms1\@Flask\5000_myhome\sidebar_buttons.json'

# Paths to source files
TEMPLATE_FILE = os.path.join(PROJECT_ROOT, 'templates', 'index.html')
NOTE_PREVIEW_TEMPLATE_FILE = os.path.join(PROJECT_ROOT, 'templates', 'note_preview.html')
CSS_FILE = os.path.join(PROJECT_ROOT, 'static', 'style.css')
MAIN_JS_FILE = os.path.join(PROJECT_ROOT, 'static', 'main.js')
LINKS_HANDLER_JS_FILE = os.path.join(PROJECT_ROOT, 'static', 'links-handler.js')
SIDEBAR_HANDLER_JS_FILE = os.path.join(PROJECT_ROOT, 'static', 'sidebar-handler.js')
CONTEXT_MENU_JS_FILE = os.path.join(PROJECT_ROOT, 'static', 'context-menu.js')

# Path to the output files
OUTPUT_HTML_FILE = r"C:\@delta\db\5000_myhome\myhome.html"
OUTPUT_NOTE_PREVIEW_FILE = r"C:\@delta\db\5000_myhome\note_preview.html"


def read_data():
    """Read data from JSON file"""
    if not os.path.exists(DATA_FILE):
        print(f"Warning: Data file not found at {DATA_FILE}")
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def read_sidebar_buttons():
    """Read sidebar buttons from JSON file"""
    if not os.path.exists(SIDEBAR_BUTTONS_FILE):
        print(f"Warning: Sidebar buttons file not found at {SIDEBAR_BUTTONS_FILE}")
        return []
    with open(SIDEBAR_BUTTONS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def read_file(filepath):
    """Read content from a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Warning: {filepath} not found")
        return ""


def generate_static_html():
    """Generate static HTML file with embedded CSS and JS"""

    # Read the base template
    template_html = read_file(TEMPLATE_FILE)
    if not template_html:
        print("[ERROR] Template file not found. Aborting.")
        return

    # Read CSS and JS files
    css_content = read_file(CSS_FILE)
    main_js_content = read_file(MAIN_JS_FILE)
    links_handler_js_content = read_file(LINKS_HANDLER_JS_FILE)
    sidebar_handler_js_content = read_file(SIDEBAR_HANDLER_JS_FILE)
    context_menu_js_content = read_file(CONTEXT_MENU_JS_FILE)

    # Read the data
    links_data = read_data()
    sidebar_buttons_data = read_sidebar_buttons()

    # Create the script to embed data and override fetch
    data_script = f"""
  <script>
    // Embedded data
    const STATIC_LINKS_DATA = {json.dumps(links_data, indent=2)};
    const STATIC_SIDEBAR_BUTTONS_DATA = {json.dumps(sidebar_buttons_data, indent=2)};
    
    // Override fetch for static version
    const originalFetch = window.fetch;
    window.fetch = function(url, options) {{
      if (url === '/api/links' && (!options || options.method === 'GET' || !options.method)) {{
        return Promise.resolve({{
          ok: true,
          json: () => Promise.resolve(STATIC_LINKS_DATA)
        }});
      }}
      if (url === '/api/sidebar-buttons' && (!options || options.method === 'GET' || !options.method)) {{
        return Promise.resolve({{
          ok: true,
          json: () => Promise.resolve(STATIC_SIDEBAR_BUTTONS_DATA)
        }});
      }}
      // For notification APIs, return empty data
      if (url === '/api/tv-notifications' || url === '/api/movie-notifications') {{
        return Promise.resolve({{
          ok: true,
          json: () => Promise.resolve({{ unseen_count: 0 }})
        }});
      }}
      // For other requests, show a message that editing is not available
      if (url.startsWith('/api/')) {{
        alert('Editing is not available in static version. Use the live version to make changes.');
        return Promise.reject(new Error('Static version - editing disabled'));
      }}
      return originalFetch.apply(this, arguments);
    }};
    
    // Disable edit functionality in static version
    document.addEventListener('DOMContentLoaded', function() {{
      // Hide edit toggle
      const editToggle = document.querySelector('.toggle-container');
      if (editToggle) {{
        editToggle.style.display = 'none';
      }}
      
      // Override note preview to use static file
      if (window.openNotePreview) {{
        window.openNotePreview = function(noteContent) {{
          const decodedContent = decodeURIComponent(noteContent);
          const encodedContent = encodeURIComponent(decodedContent);
          const previewUrl = `note_preview.html?content=${{encodedContent}}`;
          
          const previewWindow = window.open(
            previewUrl,
            'notePreview',
            'width=900,height=700,scrollbars=yes,resizable=yes,toolbar=no,menubar=no,location=no,status=no'
          );
          
          if (!previewWindow) {{
            alert('Please allow popups to preview notes');
          }}
        }};
      }}
      
      // Remove edit buttons and functionality
      const style = document.createElement('style');
      style.textContent = `
        .edit-button, .delete-button, .add-link-item, .edit-group-button, .collapsible-edit-btn,
        .sidebar-edit-buttons, .sidebar-add-button {{
          display: none !important;
        }}
        .link-item {{
          cursor: default !important;
        }}
        .collapsible-group {{
          cursor: default !important;
        }}
      `;
      document.head.appendChild(style);
    }});
  </script>
"""

    # --- HTML Injection ---
    # Replace CSS link with embedded style
    static_html = template_html.replace('<link rel="stylesheet" href="../static/style.css">', f'<style>{css_content}</style>')

    # Replace JS files with embedded scripts
    static_html = static_html.replace('<script src="../static/context-menu.js"></script>', f'<script>{context_menu_js_content}</script>')
    static_html = static_html.replace('<script src="../static/links-handler.js"></script>', f'<script>{links_handler_js_content}</script>')
    static_html = static_html.replace('<script src="../static/sidebar-handler.js"></script>', f'<script>{sidebar_handler_js_content}</script>')
    static_html = static_html.replace('<script src="../static/main.js"></script>', f'<script>{main_js_content}</script>')

    # Inject the data script before the closing </body> tag
    static_html = static_html.replace('</body>', f'{data_script}</body>')
    
    # Add a generation timestamp
    # timestamp_comment = f'<!-- Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} -->'
    # static_html = static_html.replace('</html>', f'{timestamp_comment}</html>')


    # Write the static HTML file
    with open(OUTPUT_HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(static_html)

    # Generate static note preview HTML
    note_preview_html = read_file(NOTE_PREVIEW_TEMPLATE_FILE)
    if note_preview_html:
        # Create a standalone note preview that can handle URL parameters
        note_preview_script = """
  <script>
    // Get note content from URL parameter
    const urlParams = new URLSearchParams(window.location.search);
    const encodedContent = urlParams.get('content');
    
    if (encodedContent) {
      try {
        const decodedContent = decodeURIComponent(encodedContent);
        // Simple markdown-like conversion
        let html = decodedContent
          .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
          .replace(/\*(.+?)\*/g, '<em>$1</em>')
          .replace(/`(.+?)`/g, '<code>$1</code>')
          .replace(/^# (.+)$/gm, '<h1>$1</h1>')
          .replace(/^## (.+)$/gm, '<h2>$2</h2>')
          .replace(/^### (.+)$/gm, '<h3>$1</h3>')
          .replace(/\\n/g, '<br>');
        
        document.querySelector('.content').innerHTML = html;
      } catch (e) {
        document.querySelector('.content').innerHTML = '<p>Error loading note content</p>';
      }
    } else {
      document.querySelector('.content').innerHTML = '<p>No note content provided</p>';
    }
  </script>
"""
        note_preview_html = note_preview_html.replace('</body>', f'{note_preview_script}</body>')
        
        with open(OUTPUT_NOTE_PREVIEW_FILE, 'w', encoding='utf-8') as f:
            f.write(note_preview_html)
        
        print(f"[SUCCESS] Static note preview generated: {os.path.basename(OUTPUT_NOTE_PREVIEW_FILE)}")

    print(f"[SUCCESS] Static HTML generated successfully: {os.path.basename(OUTPUT_HTML_FILE)}")
    print(f"[INFO] Included {len(links_data)} links")
    print(f"[INFO] Included {len(sidebar_buttons_data)} sidebar buttons")
    print(f"[INFO] Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    generate_static_html()