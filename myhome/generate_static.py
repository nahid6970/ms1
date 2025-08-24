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

# Path to the data file.
DATA_FILE = r'C:\Users\nahid\ms\ms1\myhome\data.json'

# Paths to source files
TEMPLATE_FILE = os.path.join(PROJECT_ROOT, 'templates', 'index.html')
CSS_FILE = os.path.join(PROJECT_ROOT, 'static', 'style.css')
MAIN_JS_FILE = os.path.join(PROJECT_ROOT, 'static', 'main.js')
LINKS_HANDLER_JS_FILE = os.path.join(PROJECT_ROOT, 'static', 'links-handler.js')

# Path to the output file
OUTPUT_HTML_FILE = r"C:\Users\nahid\ms\db\5000_myhome\myhome.html"


def read_data():
    """Read data from JSON file"""
    if not os.path.exists(DATA_FILE):
        print(f"Warning: Data file not found at {DATA_FILE}")
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
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

    # Read the data
    links_data = read_data()

    # Create the script to embed data and override fetch
    data_script = f"""
  <script>
    // Embedded data
    const STATIC_LINKS_DATA = {json.dumps(links_data, indent=2)};
    
    // Override fetch for static version
    const originalFetch = window.fetch;
    window.fetch = function(url, options) {{
      if (url === '/api/links' && (!options || options.method === 'GET' || !options.method)) {{
        return Promise.resolve({{
          ok: true,
          json: () => Promise.resolve(STATIC_LINKS_DATA)
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
      
      // Remove edit buttons and functionality
      const style = document.createElement('style');
      style.textContent = `
        .edit-button, .delete-button, .add-link-item, .edit-group-button, .collapsible-edit-btn {{
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
    static_html = static_html.replace('<script src="../static/links-handler.js"></script>', f'<script>{links_handler_js_content}</script>')
    static_html = static_html.replace('<script src="../static/main.js"></script>', f'<script>{main_js_content}</script>')

    # Inject the data script before the closing </body> tag
    static_html = static_html.replace('</body>', f'{data_script}</body>')
    
    # Add a generation timestamp
    # timestamp_comment = f'<!-- Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} -->'
    # static_html = static_html.replace('</html>', f'{timestamp_comment}</html>')


    # Write the static HTML file
    with open(OUTPUT_HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(static_html)

    print(f"[SUCCESS] Static HTML generated successfully: {os.path.basename(OUTPUT_HTML_FILE)}")
    print(f"[INFO] Included {len(links_data)} links")
    print(f"[INFO] Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    generate_static_html()