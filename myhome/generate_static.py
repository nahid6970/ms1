#!/usr/bin/env python3
"""
Static HTML Generator for MyHome
Generates a standalone HTML file with embedded CSS and JavaScript
"""

import json
import os
from datetime import datetime

def read_data():
    """Read data from JSON file"""
    data_file = 'C:\\msBackups\\DataBase\\myhome\\data.json'
    if not os.path.exists(data_file):
        return []
    with open(data_file, 'r') as f:
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
    
    # Read the template HTML
    template_html = read_file('templates/index.html')
    
    # Read CSS and JS files
    css_content = read_file('static/style.css')
    main_js_content = read_file('static/main.js')
    links_handler_js_content = read_file('static/links-handler.js')
    
    # Read the data
    links_data = read_data()
    
    # Create the static HTML content
    static_html = f"""<!DOCTYPE html>
<html>
<head>
  <title>Home</title>
  <link rel="shortcut icon" href="https://cdn-icons-png.flaticon.com/512/4021/4021539.png" type="image/x-icon">
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
{css_content}
  </style>
</head>

<body>
  <div class="flex-container2">

    <div class="toggle-container" style="margin-left: 25px;">
      <label class="switch">
        <input type="checkbox" id="edit-mode-toggle">
        <span class="slider round"></span>
      </label>
      <span style="color: white; margin-left: 10px;">Modify</span>
    </div>

    <!-- Updated styling for better edit mode control -->
    <style>
      .dragging {{
        opacity: 0.5;
      }}
      
      .reorder-buttons {{
        display: none;
        flex-direction: column;
        gap: 2px;
        margin-left: 5px;
      }}
      .edit-mode .reorder-buttons {{
        display: none;
      }}
      .reorder-btn {{
        background: #333;
        color: white;
        border: none;
        padding: 2px 6px;
        cursor: pointer;
        font-size: 12px;
        border-radius: 3px;
      }}
      .reorder-btn:hover {{
        background: #555;
      }}
      
      /* Group reorder buttons - only visible in edit mode */
      .group-reorder-buttons {{
        display: none;
        gap: 5px;
        margin-left: 10px;
      }}
      .edit-mode .group-reorder-buttons {{
        display: flex;
      }}
      
      .link-item {{
        cursor: move;
      }}

    </style>

  <div id="links-container" style="display: flex; width: 100%; flex-wrap: wrap; justify-content: left; flex-direction: column;">
  </div>

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
    
    {main_js_content}
    
    {links_handler_js_content}
    
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

  </div>
  
  <!-- Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -->
</body>
</html>"""

    # Write the static HTML file
    with open('myhome.html', 'w', encoding='utf-8') as f:
        f.write(static_html)
    
    print(f"✅ Static HTML generated successfully: myhome.html")
    print(f"📊 Included {len(links_data)} links")
    print(f"🕒 Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    generate_static_html()