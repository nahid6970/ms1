#!/usr/bin/env python3
"""
Static HTML Export Script for Word Editor
Generates a standalone HTML file from the current document data
"""

import json
import os
from datetime import datetime

# Paths
DATA_FILE = r'C:\@delta\db\5000_myhome\myword.html'
OUTPUT_FILE = r'C:\@delta\db\5000_myhome\myword.html'

def load_data():
    """Load data from JSON file"""
    data_file = r'C:\@delta\ms1\@Flask\5019_word\word_data.json'
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'documents': [], 'activeDocument': 0}

def generate_static_html(data):
    """Generate static HTML from document data - matches main application exactly"""
    
    # Get current time for export info
    export_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Get active document
    active_document = data.get('activeDocument', 0)
    documents = data.get('documents', [])
    
    # Start building HTML with exact same structure as main app
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Documents - Static Export</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }

        .container {
            max-width: 100%;
            margin: 0 auto;
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            height: 100vh;
        }

        .document-tabs {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 20px;
            background: #f8f9fa;
            border-bottom: 1px solid #ddd;
        }

        .document-controls {
            display: flex;
            align-items: center;
            gap: 5px;
            flex: 1;
            min-width: 0;
        }

        .document-selector {
            position: relative;
            flex: 1;
            min-width: 200px;
            max-width: 400px;
        }

        .document-current {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            padding: 8px 15px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            width: 100%;
            transition: all 0.2s;
            font-family: inherit;
        }

        .document-current:hover {
            background: #f8f9fa;
            border-color: #007bff;
        }

        #currentDocumentName {
            flex: 1;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            text-align: left;
        }

        .dropdown-arrow {
            color: #666;
            font-size: 12px;
            flex-shrink: 0;
        }

        .document-list {
            display: none;
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 1px solid #ddd;
            border-radius: 6px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 1000;
            margin-top: 5px;
            max-height: 300px;
            overflow-y: auto;
        }

        .document-list.show {
            display: block;
        }

        .document-item {
            padding: 12px 15px;
            cursor: pointer;
            border-bottom: 1px solid #f0f0f0;
            transition: background 0.2s;
        }

        .document-item:last-child {
            border-bottom: none;
        }

        .document-item:hover {
            background: #f8f9fa;
        }

        .document-item.active {
            background: #e7f3ff;
            color: #007bff;
            font-weight: 600;
        }

        .document-item-name {
            font-size: 14px;
            display: block;
            width: 100%;
        }

        .document-item-info {
            font-size: 12px;
            color: #666;
            margin-top: 2px;
        }

        .export-info {
            margin-left: auto;
            color: #666;
            font-size: 12px;
            padding: 8px 15px;
            background: #fff;
            border: 1px solid #ddd;
            border-radius: 6px;
        }

        .editor-container {
            flex: 1;
            padding: 20px;
            overflow: auto;
            background: #fafafa;
        }

        .editor {
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 40px;
            min-height: calc(100vh - 200px);
            font-family: 'Inter', sans-serif;
            font-size: 14px;
            line-height: 1.6;
            color: #333;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .editor p {
            margin-bottom: 1em;
        }

        .editor h1 {
            font-size: 2em;
            font-weight: 700;
            margin-bottom: 0.5em;
            margin-top: 0.5em;
            color: #1a1a1a;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 0.3em;
        }

        .editor h2 {
            font-size: 1.5em;
            font-weight: 600;
            margin-bottom: 0.4em;
            margin-top: 0.8em;
            color: #2a2a2a;
        }

        .editor h3 {
            font-size: 1.25em;
            font-weight: 600;
            margin-bottom: 0.3em;
            margin-top: 0.6em;
            color: #3a3a3a;
        }

        .editor h4, .editor h5, .editor h6 {
            margin-bottom: 0.5em;
            font-weight: 600;
        }

        .editor ul, .editor ol {
            margin-left: 20px;
            margin-bottom: 1em;
        }

        .editor li {
            margin-bottom: 0.25em;
        }

        .no-content {
            color: #999;
            font-style: italic;
            text-align: center;
            padding: 40px;
        }

        @media print {
            body {
                background: white;
            }
            
            .container {
                box-shadow: none;
                height: auto;
            }
            
            .document-tabs {
                display: none;
            }
            
            .editor-container {
                padding: 0;
            }
            
            .editor {
                border: none;
                box-shadow: none;
                padding: 0;
            }
        }
    </style>
    <script>
        let currentDocument = ''' + str(active_document) + ''';
        let documentData = ''' + json.dumps(data) + ''';

        function switchDocument(index) {
            currentDocument = index;
            renderDocumentTabs();
            renderEditor();
        }

        function toggleDocumentList() {
            const documentList = document.getElementById('documentList');
            documentList.classList.toggle('show');
        }

        function renderDocumentTabs() {
            const currentDocumentNameEl = document.getElementById('currentDocumentName');
            if (documentData.documents[currentDocument]) {
                currentDocumentNameEl.textContent = documentData.documents[currentDocument].name;
            }

            const documentList = document.getElementById('documentList');
            documentList.innerHTML = '';

            documentData.documents.forEach((doc, index) => {
                const item = document.createElement('div');
                item.className = `document-item ${index === currentDocument ? 'active' : ''}`;

                const nameSpan = document.createElement('span');
                nameSpan.className = 'document-item-name';
                nameSpan.textContent = doc.name;
                nameSpan.onclick = () => {
                    switchDocument(index);
                    toggleDocumentList();
                };

                const infoSpan = document.createElement('div');
                infoSpan.className = 'document-item-info';
                infoSpan.textContent = `Modified: ${doc.modified || 'Never'}`;

                item.appendChild(nameSpan);
                item.appendChild(infoSpan);
                documentList.appendChild(item);
            });
        }

        function renderEditor() {
            const editor = document.getElementById('editor');
            const doc = documentData.documents[currentDocument];
            
            if (doc && doc.content) {
                editor.innerHTML = doc.content;
            } else {
                editor.innerHTML = '<div class="no-content">No content available</div>';
            }
        }

        // Close dropdown when clicking outside
        document.addEventListener('click', function(event) {
            const documentSelector = document.querySelector('.document-selector');
            const documentList = document.getElementById('documentList');
            if (!documentSelector.contains(event.target)) {
                documentList.classList.remove('show');
            }
        });

        // Initialize on load
        window.onload = function() {
            renderDocumentTabs();
            renderEditor();
        };
    </script>
</head>
<body>
    <div class="container">
        <div class="document-tabs">
            <div class="document-controls">
                <div class="document-selector">
                    <button class="document-current" id="currentDocumentBtn" onclick="toggleDocumentList()">
                        <span id="currentDocumentName">''' + (documents[active_document]['name'] if documents and active_document < len(documents) else 'Document1') + '''</span>
                        <span class="dropdown-arrow">▼</span>
                    </button>
                    <div class="document-list" id="documentList"></div>
                </div>
            </div>

            <div class="export-info">
                Static export - ''' + export_time + '''
            </div>
        </div>

        <div class="editor-container">
            <div id="editor" class="editor"></div>
        </div>
    </div>
</body>
</html>'''

    return html_content

def export_to_static():
    """Main export function"""
    try:
        # Check if data file exists
        data_file = r'C:\@delta\ms1\@Flask\5019_word\word_data.json'
        if not os.path.exists(data_file):
            print(f"ERROR: Data file not found: {data_file}")
            return False
        
        # Load data
        data = load_data()
        print(f"Loaded data with {len(data.get('documents', []))} documents")
        
        # Generate HTML
        html_content = generate_static_html(data)
        
        # Ensure output directory exists
        output_dir = os.path.dirname(OUTPUT_FILE)
        print(f"Creating output directory: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
        
        # Write HTML file
        print(f"Writing HTML file to: {OUTPUT_FILE}")
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Verify file was created
        if os.path.exists(OUTPUT_FILE):
            file_size = os.path.getsize(OUTPUT_FILE)
            print(f"Static HTML exported successfully!")
            print(f"   File: {OUTPUT_FILE}")
            print(f"   Size: {file_size:,} bytes")
            return True
        else:
            print(f"ERROR: File was not created: {OUTPUT_FILE}")
            return False
        
    except Exception as e:
        import traceback
        print(f"ERROR: Error exporting static HTML: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    export_to_static()