#!/usr/bin/env python3
"""
Static HTML Export Script
Generates a standalone HTML file from the current table data

IMPORTANT: When adding new markdown syntax, update these 3 locations:
1. hasMarkdown detection (around line 1020) - add cellValue.includes() check
2. parseMarkdown() function (around line 1100) - add regex replacement pattern
3. CSS styles (around line 750) - add styling for new HTML elements if needed

These must match the implementation in:
- static/script.js (applyMarkdownFormatting and parseMarkdown functions)
- static/style.css (markdown-preview styles)
- templates/index.html (Markdown Guide modal)
"""

import json
import os
from datetime import datetime

# Paths
DATA_FILE = r'C:\Users\nahid\ms\ms1\scripts\flask\5018_cell\data.json'
CUSTOM_SYNTAXES_FILE = r'C:\Users\nahid\ms\ms1\scripts\flask\5018_cell\custom_syntaxes.json'
OUTPUT_FILE = r'C:\Users\nahid\ms\db\5000_myhome\mycell.html'

def load_data():
    """Load data from JSON file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'sheets': [], 'activeSheet': 0}

def load_custom_syntaxes():
    """Load custom color syntaxes from JSON file"""
    if os.path.exists(CUSTOM_SYNTAXES_FILE):
        with open(CUSTOM_SYNTAXES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def generate_static_html(data, custom_syntaxes):
    """Generate static HTML from table data - matches main application exactly"""
    
    # Get current time for export info
    export_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Get active sheet
    active_sheet = data.get('activeSheet', 0)
    sheets = data.get('sheets', [])
    
    # Start building HTML with exact same structure as main app
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Cell Data - Static Export</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500;1,600;1,700&display=swap" rel="stylesheet">
    <!-- KaTeX for Math Rendering -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css" integrity="sha384-n8MVd4RsNIU0tAv4ct0nTaAbDJwPJzDEaqSD1odI+WdtXRGWt2kTvGFasHpSy3SV" crossorigin="anonymous">
    <script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js" integrity="sha384-XjKyOOlGwcjNTAIQHIpgOno0Hl1YQqzUOEleOLALmuqehneUG+vnGctmUb0ZY0l8" crossorigin="anonymous"></script>
    <style>
        :root {
            --grid-line-color: #dddddd;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }

        /* Mobile-first responsive design */
        @media (max-width: 768px) {
            body {
                padding: 10px;
            }
        }

        .container {
            max-width: 100%;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            height: calc(100vh - 40px);
            overflow: hidden;
        }

        .sheet-tabs {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 20px;
            background: #f8f9fa;
            border-bottom: 1px solid #ddd;
            flex-wrap: nowrap;
            overflow-x: auto;
            overflow-y: visible;
        }



        .search-box {
            display: flex;
            align-items: center;
            gap: 5px;
            padding: 4px 8px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            transition: all 0.2s;
        }

        .search-box:focus-within {
            border-color: #007bff;
            box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
        }

        .search-box input {
            border: none;
            outline: none;
            padding: 6px 8px;
            font-size: 14px;
            width: 200px;
            background: transparent;
        }

        .btn-clear-search {
            background: none;
            border: none;
            color: #999;
            font-size: 20px;
            cursor: pointer;
            padding: 0 4px;
            line-height: 1;
            transition: color 0.2s;
            display: none;
        }

        .btn-clear-search:hover {
            color: #dc3545;
        }

        .search-box input:not(:placeholder-shown) ~ .btn-clear-search {
            display: block;
        }

        /* Search highlight */
        .search-highlight {
            background: rgba(255, 235, 59, 0.5) !important;
        }

        .button-group {
            display: flex;
            gap: 4px;
            align-items: center;
            padding: 4px;
            background: #f8f9fa;
            border: 1px solid #ddd;
            border-radius: 4px;
        }

        .btn-icon-toggle {
            display: flex;
            align-items: center;
            justify-content: center;
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            width: 32px;
            height: 32px;
            cursor: pointer;
            user-select: none;
            transition: all 0.2s;
            position: relative;
        }

        .btn-icon-toggle:hover {
            background: #e9ecef;
            border-color: #007bff;
        }

        .btn-icon-toggle input[type="checkbox"] {
            position: absolute;
            opacity: 0;
            cursor: pointer;
            width: 100%;
            height: 100%;
            margin: 0;
        }

        .btn-icon-toggle span {
            font-size: 16px;
            pointer-events: none;
        }

        .btn-icon-toggle input[type="checkbox"]:checked + span {
            opacity: 1;
        }

        .btn-icon-toggle input[type="checkbox"]:not(:checked) + span {
            opacity: 0.4;
        }

        .font-size-control {
            display: flex;
            align-items: center;
            gap: 5px;
            padding: 4px 8px;
            background: #f8f9fa;
            border: 1px solid #ddd;
            border-radius: 4px;
        }

        .font-size-label {
            font-size: 13px;
            font-weight: 500;
            color: #333;
        }

        .btn-font-size {
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            width: 28px;
            height: 28px;
            font-size: 16px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
            flex-shrink: 0;
        }

        .btn-font-size:hover {
            background: #e9ecef;
            border-color: #007bff;
            transform: scale(1.05);
        }

        .font-size-display {
            min-width: 40px;
            text-align: center;
            font-size: 13px;
            font-weight: 500;
            color: #333;
        }

        .export-info {
            margin-left: auto;
            color: #666;
            font-size: 12px;
            padding: 8px 15px;
            background: #fff;
            border: 1px solid #ddd;
            border-radius: 4px;
        }

        /* Responsive column width variables */
        :root {
            --base-column-width: 150px;
            --row-number-width: 60px;
        }

        .table-container {
            flex: 1;
            overflow: auto;
            padding: 0 20px;
        }

        table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            background: white;
            table-layout: fixed;
        }

        th, td {
            border: 1px solid var(--grid-line-color);
            padding: 8px;
            text-align: left;
            position: relative;
            box-sizing: border-box;
        }

        th {
            background: #f8f9fa;
            font-weight: 600;
            color: #333;
            position: sticky;
            top: 0;
            z-index: 10;
        }

        .header-cell {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 5px;
            overflow: visible;
            position: relative;
            padding-right: 25px;
            min-width: 0;
        }

        .column-name {
            flex: 1;
            font-weight: 600;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .row-number {
            background: #f8f9fa;
            font-weight: 600;
            text-align: left;
            white-space: nowrap;
            width: var(--row-number-width);
            min-width: var(--row-number-width);
            padding: 0 5px;
            font-family: monospace;
            font-size: 12px;
            vertical-align: middle;
            display: table-cell;
            line-height: 1.2;
        }

        /* Hide row numbers when toggle is off */
        .hide-row-numbers .row-number {
            display: none;
        }

        .cell-content {
            width: 100%;
            border: none;
            padding: 4px;
            background: transparent;
            box-sizing: border-box;
            pointer-events: none;
            white-space: nowrap;
            overflow: visible;
            text-overflow: ellipsis;
            line-height: 1.4;
            position: relative;
            display: block;
        }

        /* Markdown formatting in static export */
        .cell-content strong {
            font-weight: bold;
            color: inherit;
        }

        /* Text wrapping enabled */
        .wrap-enabled td:not(.row-number) {
            white-space: normal;
            overflow: visible;
            word-wrap: break-word;
            word-break: break-word;
            vertical-align: top;
        }

        .wrap-enabled .cell-content {
            white-space: pre-wrap;
            word-wrap: break-word;
            overflow: visible;
            text-overflow: clip;
            line-height: 1.4;
        }

        /* Markdown formatting works with wrap mode */
        .wrap-enabled .cell-content strong {
            font-weight: bold;
        }

        /* Default row height when wrap is enabled - keep same as normal */
        .wrap-enabled tr {
            height: 40px;
        }

        /* Only expand rows that actually have wrapped content */
        .wrap-enabled tr.has-wrapped-content {
            height: auto !important;
        }

        /* Keep row numbers centered vertically */
        .wrap-enabled .row-number {
            vertical-align: middle;
        }

        /* For rows without wrapped content, keep normal height */
        .wrap-enabled tr:not(.has-wrapped-content) td:not(.row-number) {
            height: 40px;
        }

        td.merged-cell {
            vertical-align: middle;
            padding: 0 !important;
            position: relative;
        }

        td.merged-cell .cell-content {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            padding: 8px;
            font-size: 14px;
            background: transparent;
            resize: none;
            font-family: inherit;
            overflow: auto;
            box-sizing: border-box;
            white-space: pre-wrap;
            word-wrap: break-word;
            line-height: 1.4;
        }

        tr {
            height: 40px;
        }

        .no-data {
            text-align: center;
            color: #666;
            font-style: italic;
            padding: 40px;
        }

        /* Mobile responsive adjustments */
        @media (max-width: 768px) {
            :root {
                --base-column-width: 120px;
                --row-number-width: 50px;
            }

            body {
                padding: 10px;
            }

            .container {
                height: calc(100vh - 20px);
            }

            .table-container {
                padding: 0 10px;
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
                min-width: 100%;
            }

            table {
                min-width: 600px;
            }

            /* Make columns more flexible on mobile */
            th, td {
                min-width: 80px !important;
                padding: 6px 4px;
            }

            .row-number {
                width: var(--row-number-width) !important;
                min-width: var(--row-number-width) !important;
                font-size: 11px;
                padding: 0 3px;
            }

            /* Adjust sheet tabs for mobile */
            .sheet-tabs {
                padding: 8px 10px;
                gap: 5px;
                flex-wrap: nowrap;
                overflow-x: auto;
            }

            .category-controls {
                flex-shrink: 0;
            }

            .sheet-controls {
                flex-shrink: 0;
            }

            .category-selector {
                min-width: 120px;
            }

            .sheet-selector {
                min-width: 120px;
            }

            .search-box {
                min-width: 150px;
            }

            .button-group {
                flex-shrink: 0;
            }

            .font-size-control {
                flex-shrink: 0;
            }

            .export-info {
                display: none;
            }

            /* Adjust column headers */
            .header-cell {
                padding-left: 20px;
            }
        }

        /* Tablet responsive adjustments */
        @media (min-width: 769px) and (max-width: 1024px) {
            :root {
                --base-column-width: 130px;
                --row-number-width: 55px;
            }
        }

        /* Large screen adjustments */
        @media (min-width: 1200px) {
            :root {
                --base-column-width: 180px;
                --row-number-width: 70px;
            }
        }

        /* Sidebar Navigation */
        .sidebar-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 999;
            display: none;
        }

        .sidebar-overlay.show {
            display: block;
        }

        .sidebar {
            position: fixed;
            top: 0;
            left: -300px;
            width: 300px;
            height: 100%;
            background: white;
            box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
            z-index: 1000;
            transition: left 0.3s ease;
            display: flex;
            flex-direction: column;
        }

        .sidebar.show {
            left: 0;
        }

        .sidebar-tree {
            flex: 1;
            overflow-y: auto;
            padding: 10px 0;
        }

        .btn-menu {
            background: none;
            border: 1px solid #ddd;
            border-radius: 4px;
            width: 36px;
            height: 36px;
            font-size: 20px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 15px;
            transition: all 0.2s;
        }

        .btn-menu:hover {
            background: #f0f0f0;
            border-color: #007bff;
        }

        .current-sheet-info {
            display: flex;
            flex-direction: column;
            gap: 2px;
            flex: 1;
        }

        .current-sheet-title {
            font-size: 16px;
            font-weight: 600;
            color: #333;
        }

        .current-category-title {
            font-size: 12px;
            color: #666;
        }

        /* Tree Items */
        .tree-item {
            display: flex;
            align-items: center;
            padding: 8px 15px;
            cursor: pointer;
            user-select: none;
            transition: background 0.2s;
            color: #333;
            font-size: 14px;
        }

        .tree-item:hover {
            background: #f0f0f0;
        }

        .tree-item.active {
            background: #e7f3ff;
            color: #007bff;
            border-right: 3px solid #007bff;
        }

        .tree-category {
            margin-bottom: 4px;
        }

        .tree-category-header {
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 600;
            color: #555;
            padding: 8px 12px;
            border-radius: 4px;
        }

        .tree-category-header:hover {
            background: #f8f9fa;
        }

        .tree-category-content {
            padding-left: 0;
            overflow: hidden;
            transition: max-height 0.3s ease-out;
        }

        .tree-category.collapsed .tree-category-content {
            display: none;
        }

        .tree-sheet {
            padding-left: 32px;
            display: flex;
            align-items: center;
            gap: 6px;
            border-radius: 4px;
            margin: 0;
            position: relative;
            padding-top: 6px;
            padding-bottom: 6px;
        }

        /* Vertical line connecting items */
        .tree-sheet::before {
            content: '';
            position: absolute;
            left: 20px;
            top: 0;
            bottom: 50%;
            width: 1px;
            background: #ccc;
        }

        /* Horizontal line (L shape) */
        .tree-sheet::after {
            content: '';
            position: absolute;
            left: 20px;
            top: 50%;
            width: 12px;
            height: 1px;
            background: #ccc;
        }

        /* Last item - only show L corner, no line below */
        .tree-sheet.last::before {
            bottom: 50%;
        }

        .tree-icon {
            font-size: 16px;
            width: 20px;
            text-align: center;
            flex-shrink: 0;
        }

        .tree-label {
            flex: 1;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        @media print {
            body {
                background: white;
                padding: 0;
            }
            
            .container {
                box-shadow: none;
                height: auto;
            }
            
            .sheet-tabs {
                display: none;
            }
        }

        /* Markdown formatting styles */
        strong {
            font-weight: bold;
        }

        em {
            font-style: italic;
        }

        code {
            background: #f4f4f4;
            border: 1px solid #ddd;
            border-radius: 3px;
            padding: 2px 5px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            color: #c7254e;
            line-height: 1.8;
            box-decoration-break: clone;
            -webkit-box-decoration-break: clone;
        }

        mark {
            background: #000000;
            color: #ffffff;
            padding: 1px 4px;
            border-radius: 3px;
            display: inline;
            vertical-align: baseline;
            line-height: 1.3;
            box-decoration-break: clone;
            -webkit-box-decoration-break: clone;
        }

        del {
            text-decoration: line-through;
            color: #999;
        }

        /* IMPORTANT: When adding new markdown syntax, add CSS styling here */
        /* These styles must match static/style.css .markdown-preview styles */
        sup {
            vertical-align: super;
            font-size: 0.75em;
            line-height: 0;
        }

        sub {
            vertical-align: sub;
            font-size: 0.75em;
            line-height: 0;
        }

        u {
            text-decoration: underline;
        }

        a {
            color: #007bff;
            text-decoration: underline;
            cursor: pointer;
            pointer-events: auto;
            position: relative;
            z-index: 2;
        }

        a:hover {
            color: #0056b3;
            text-decoration: none;
        }

        /* Markdown Grid Table Styles (CSS Grid - no <table> elements) */
        .md-grid {
            display: grid;
            grid-template-columns: repeat(var(--cols), auto);
            gap: 0;
            margin: 4px 0;
            font-size: inherit;
            font-family: inherit;
            width: fit-content;
            max-width: 100%;
        }

        .md-cell {
            padding: 4px 12px;
            border: none;
            border-right: 3px solid #ced4da;
            background: transparent;
            overflow: hidden;
            word-break: break-word;
            white-space: normal;
            min-width: 80px;
            max-width: 100%;
            /* Hanging indent for wrapped text - like lists */
            text-indent: -1em;
            padding-left: calc(12px + 1em);
        }

        /* Remove right border from last cell in each row */
        .md-cell:nth-child(var(--cols)n) {
            border-right: none;
        }

        .md-header {
            background: transparent;
            font-weight: 600;
            border-bottom: 2px solid #495057;
            white-space: normal;
            word-break: break-word;
        }

        .md-empty {
            color: #aaa;
            background: transparent;
            text-align: center;
            font-size: 1.2em;
            font-weight: bold;
            opacity: 0.6;
        }

        /* Rowspan borders - add thin black line above and below cells with rowspan */
        .md-cell[rowspan] {
            border-top: 1px solid #000000;
            border-bottom: 1px solid #000000;
        }

        /* Let coloured text / background css shine through */
        .md-grid strong {
            font-weight: bold;
        }

        .md-grid em {
            font-style: italic;
        }

        .md-grid code {
            background: #f4f4f4;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }

        .md-grid a {
            color: #007bff;
            text-decoration: underline;
        }

        /* Collapsible text styling */
        .collapsible-wrapper {
            display: inline-flex;
            align-items: baseline;
            gap: 4px;
            vertical-align: baseline;
        }

        .collapsible-toggle {
            background: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 2px 6px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
            line-height: 1;
            vertical-align: baseline;
        }

        .collapsible-toggle:hover {
            background: #007bff;
            border-color: #007bff;
            transform: scale(1.1);
        }

        .collapsible-content {
            display: inline;
            vertical-align: baseline;
        }

        /* Word Connector */
        .word-connector {
            position: relative;
            display: inline-block;
            padding-bottom: 12px;
        }

        .word-connector-line {
            position: absolute;
            bottom: 0;
            height: 12px;
            pointer-events: none;
            z-index: 1;
            overflow: visible;
        }

        /* Correct Answer Highlight */
        .correct-answer {
            background-color: transparent;
            color: inherit;
            border-radius: 3px;
            cursor: pointer;
            transition: all 0.3s ease;
            padding: 0 2px;
        }

        .correct-answer.revealed {
            background-color: #29e372;
            color: black;
            padding: 0 4px;
        }

        /* Sub-Sheet Navigation Bar */
        .subsheet-bar {
            padding: 10px 20px;
            background: #f8f9fa;
            border-bottom: 1px solid #ddd;
            min-height: 50px;
        }

        .subsheet-tabs {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            align-items: center;
        }

        .subsheet-tab {
            padding: 8px 16px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 14px;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            white-space: nowrap;
        }

        .subsheet-tab:hover {
            background: #e9ecef;
            border-color: #007bff;
        }

        .subsheet-tab.active {
            background: #007bff;
            color: white;
            border-color: #007bff;
            font-weight: 600;
        }

        .subsheet-tab-name {
            flex: 1;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        /* Settings Modal */
        .modal {
            position: fixed;
            z-index: 3000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .modal-content {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            max-width: 600px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px;
            border-bottom: 1px solid #ddd;
        }

        .modal-header h2 {
            margin: 0;
            font-size: 24px;
        }

        .close {
            font-size: 28px;
            font-weight: bold;
            color: #999;
            cursor: pointer;
            transition: color 0.2s;
        }

        .close:hover {
            color: #333;
        }

        .settings-content {
            padding: 20px;
        }

        .settings-section {
            margin-bottom: 20px;
        }

        .settings-section-title {
            font-size: 18px;
            margin-bottom: 15px;
            color: #333;
        }

        .settings-item {
            margin-bottom: 20px;
        }

        .settings-item-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .settings-label {
            font-weight: 600;
            color: #333;
        }

        .btn-reset {
            background: #f0f0f0;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 4px 12px;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.2s;
        }

        .btn-reset:hover {
            background: #e0e0e0;
        }

        .color-picker-group {
            display: flex;
            gap: 10px;
            align-items: flex-start;
        }

        .color-picker-wrapper {
            display: flex;
            flex-direction: column;
            gap: 5px;
            align-items: center;
        }

        .color-picker-wrapper input[type="color"] {
            width: 60px;
            height: 40px;
            border: 1px solid #ddd;
            border-radius: 4px;
            cursor: pointer;
        }

        .color-picker-label {
            font-size: 12px;
            color: #666;
            text-align: center;
            white-space: nowrap;
        }

        .color-input-wrapper {
            display: flex;
            align-items: center;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 8px 12px;
            background: white;
            height: 40px;
        }

        .color-input-prefix {
            font-weight: bold;
            color: #666;
            margin-right: 4px;
        }

        .color-input-wrapper input {
            border: none;
            outline: none;
            width: 80px;
            font-family: monospace;
            font-size: 14px;
        }

        .settings-description {
            font-size: 13px;
            color: #666;
            margin-top: 8px;
        }
    </style>
    <script>
        let tableData = ''' + json.dumps(data) + ''';
        
        // Try to restore last viewed sheet from localStorage, fallback to embedded activeSheet
        let currentSheet = parseInt(localStorage.getItem('staticExportActiveSheet')) || ''' + str(active_sheet) + ''';
        
        // Validate the sheet index
        if (currentSheet < 0 || currentSheet >= tableData.sheets.length) {
            currentSheet = ''' + str(active_sheet) + ''';
        }
        
        // Set currentCategory to match the active sheet's category
        let currentCategory = tableData.sheetCategories[currentSheet] || tableData.sheetCategories[String(currentSheet)] || null;

        function initializeCategories() {
            if (!tableData.categories) {
                tableData.categories = [];
            }
            if (!tableData.sheetCategories) {
                tableData.sheetCategories = {};
            }
        }

        function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            const overlay = document.getElementById('sidebarOverlay');
            
            if (sidebar.classList.contains('show')) {
                sidebar.classList.remove('show');
                overlay.classList.remove('show');
            } else {
                sidebar.classList.add('show');
                overlay.classList.add('show');
            }
        }

        function renderSidebar() {
            const treeContainer = document.getElementById('sidebarTree');
            if (!treeContainer) return;

            treeContainer.innerHTML = '';

            // Group sheets by category
            const categoryMap = {};

            // Initialize categories
            if (tableData.categories) {
                tableData.categories.forEach(cat => {
                    categoryMap[cat] = [];
                });
            }
            // Ensure Uncategorized exists
            if (!categoryMap['Uncategorized']) {
                categoryMap['Uncategorized'] = [];
            }

            // Distribute sheets (only parent sheets, skip sub-sheets)
            tableData.sheets.forEach((sheet, index) => {
                if (sheet.parentSheet !== undefined && sheet.parentSheet !== null) {
                    return; // Skip sub-sheets
                }

                const catName = tableData.sheetCategories[index] || tableData.sheetCategories[String(index)] || 'Uncategorized';
                if (!categoryMap[catName]) categoryMap[catName] = [];
                categoryMap[catName].push({ ...sheet, originalIndex: index });
            });

            // Render Categories
            Object.keys(categoryMap).forEach(catName => {
                const sheets = categoryMap[catName];

                const catDiv = document.createElement('div');
                catDiv.className = 'tree-category collapsed'; // Start collapsed

                const header = document.createElement('div');
                header.className = 'tree-category-header tree-item';
                header.onclick = (e) => {
                    // Toggle collapse and icon
                    catDiv.classList.toggle('collapsed');
                    const icon = header.querySelector('.tree-icon');
                    icon.textContent = catDiv.classList.contains('collapsed') ? '📁' : '📂';
                };

                header.innerHTML = `
                    <span class="tree-icon">📁</span>
                    <span class="tree-label">${catName}</span>
                `;

                const content = document.createElement('div');
                content.className = 'tree-category-content';

                sheets.forEach((sheet, idx) => {
                    const isLast = idx === sheets.length - 1;
                    const sheetDiv = document.createElement('div');
                    sheetDiv.className = `tree-sheet tree-item ${sheet.originalIndex === currentSheet ? 'active' : ''} ${isLast ? 'last' : ''}`;
                    sheetDiv.onclick = () => {
                        switchSheet(sheet.originalIndex);
                        toggleSidebar();
                    };

                    sheetDiv.innerHTML = `
                        <span class="tree-icon">📄</span>
                        <span class="tree-label">${sheet.name}</span>
                    `;
                    content.appendChild(sheetDiv);
                });

                catDiv.appendChild(header);
                catDiv.appendChild(content);
                treeContainer.appendChild(catDiv);
            });

            // Update Header Info
            const currentSheetObj = tableData.sheets[currentSheet];
            if (currentSheetObj) {
                document.getElementById('currentSheetTitle').textContent = currentSheetObj.name;
                const currentCat = tableData.sheetCategories[currentSheet] || tableData.sheetCategories[String(currentSheet)] || 'Uncategorized';
                document.getElementById('currentCategoryTitle').textContent = currentCat;
            }

            // Update sub-sheet bar
            renderSubSheetBar();
        }

        function switchSheet(index) {
            currentSheet = index;
            
            // Save to localStorage so it persists across refreshes
            localStorage.setItem('staticExportActiveSheet', index);
            renderSidebar();
            renderTable();
            
            // Apply font size scale after rendering
            setTimeout(() => {
                applyFontSizeScale();
            }, 0);
        }

        function renderSubSheetBar() {
            const subsheetTabs = document.getElementById('subsheetTabs');
            if (!subsheetTabs) return;
            
            subsheetTabs.innerHTML = '';

            // Get current sheet's parent (if it's a sub-sheet) or use current sheet as parent
            const currentSheetData = tableData.sheets[currentSheet];
            const parentIndex = currentSheetData?.parentSheet !== undefined ? currentSheetData.parentSheet : currentSheet;
            const parentSheet = tableData.sheets[parentIndex];

            if (!parentSheet) return;

            // Add parent sheet tab
            const parentTab = document.createElement('div');
            parentTab.className = `subsheet-tab ${currentSheet === parentIndex ? 'active' : ''}`;
            
            const parentName = document.createElement('span');
            parentName.className = 'subsheet-tab-name';
            parentName.textContent = parentSheet.name;
            
            parentTab.appendChild(parentName);
            parentTab.onclick = () => switchSheet(parentIndex);
            subsheetTabs.appendChild(parentTab);

            // Add sub-sheets
            tableData.sheets.forEach((sheet, index) => {
                if (sheet.parentSheet === parentIndex) {
                    const tab = document.createElement('div');
                    tab.className = `subsheet-tab ${currentSheet === index ? 'active' : ''}`;
                    
                    const name = document.createElement('span');
                    name.className = 'subsheet-tab-name';
                    name.textContent = sheet.name;
                    
                    tab.appendChild(name);
                    tab.onclick = () => switchSheet(index);
                    subsheetTabs.appendChild(tab);
                }
            });
        }

        function renderTable() {
            const headerRow = document.getElementById('headerRow');
            const tableBody = document.getElementById('tableBody');

            headerRow.innerHTML = '';
            tableBody.innerHTML = '';

            const sheet = tableData.sheets[currentSheet];
            if (!sheet) return;

            // Add row number column
            const rowNumHeader = document.createElement('th');
            rowNumHeader.className = 'row-number';
            rowNumHeader.textContent = '#';
            headerRow.appendChild(rowNumHeader);

            // Render headers
            sheet.columns.forEach((col, index) => {
                const th = document.createElement('th');
                th.style.width = col.width + 'px';
                th.style.minWidth = col.width + 'px';
                th.style.maxWidth = col.width + 'px';
                th.style.backgroundColor = col.headerBgColor || col.color || '#f8f9fa';

                const headerCell = document.createElement('div');
                headerCell.className = 'header-cell';

                const columnName = document.createElement('span');
                columnName.className = 'column-name';
                columnName.textContent = col.name;
                columnName.style.color = col.headerTextColor || col.textColor || '#333333';
                columnName.style.fontWeight = (col.headerBold !== false) ? 'bold' : 'normal';
                columnName.style.fontStyle = col.headerItalic ? 'italic' : 'normal';

                if (col.headerCenter) {
                    columnName.style.textAlign = 'center';
                    columnName.style.flex = '1';
                }

                headerCell.appendChild(columnName);
                th.appendChild(headerCell);
                headerRow.appendChild(th);
            });

            // Render rows
            sheet.rows.forEach((row, rowIndex) => {
                const tr = document.createElement('tr');

                // Row number
                const rowNumCell = document.createElement('td');
                rowNumCell.className = 'row-number';
                rowNumCell.textContent = rowIndex + 1;
                tr.appendChild(rowNumCell);

                // Data cells
                sheet.columns.forEach((col, colIndex) => {
                    const td = document.createElement('td');
                    td.style.width = col.width + 'px';
                    td.style.minWidth = col.width + 'px';
                    td.style.maxWidth = col.width + 'px';
                    td.style.backgroundColor = col.color;

                    const cellContent = document.createElement('div');
                    cellContent.className = 'cell-content';
                    
                    // Handle markdown formatting and newlines
                    // IMPORTANT: When adding new markdown syntax, add detection here
                    // This must match the hasMarkdown check in static/script.js
                    const cellValue = row[colIndex] || '';
                    const hasMarkdown = cellValue.includes('\\\\(') || 
                        cellValue.includes('[[') || 
                        cellValue.includes('**') || 
                        cellValue.includes('__') || 
                        cellValue.includes('@@') || 
                        cellValue.includes('##') || 
                        cellValue.includes('..') ||
                        cellValue.includes('```') || 
                        cellValue.includes('`') || 
                        cellValue.includes('~~') || 
                        cellValue.includes('==') || 
                        cellValue.includes('!!') ||
                        cellValue.includes('??') ||
                        cellValue.includes('^') || 
                        cellValue.includes('~') || 
                        cellValue.includes('{fg:') || 
                        cellValue.includes('{bg:') || 
                        cellValue.includes('{link:') || 
                        cellValue.includes('{{') ||
                        cellValue.includes('\\n- ') || 
                        cellValue.includes('\\n-- ') || 
                        cellValue.includes('\\n--- ') || 
                        cellValue.trim().startsWith('- ') || 
                        cellValue.trim().startsWith('-- ') || 
                        cellValue.trim().startsWith('--- ') ||
                        cellValue.match(/Table\\*\\d+/i) ||
                        cellValue.trim().startsWith('|') ||
                        cellValue.match(/^-{5,}$/m) ||
                        cellValue.match(/^[A-Z]+-{5,}$/m) ||
                        cellValue.match(/^-{5,}[A-Z]+$/m) ||
                        cellValue.match(/^[A-Z]+-{5,}[A-Z]+$/m) ||
                        cellValue.match(/^-{5,}#[0-9a-fA-F]{6}/m) ||
                        cellValue.match(/^[A-Z]+-{5,}#[0-9a-fA-F]{6}/m) ||
                        cellValue.match(/^Timeline(?:C)?(?:-[A-Z]+)?\\*/m) ||
                        cellValue.match(/\\[\\d+(?:-[A-Z]+)?\\]\\S+/) ||
                        (cellValue.includes('|') && cellValue.split('|').length >= 2);
                    
                    if (hasMarkdown) {
                        // Apply markdown formatting
                        cellContent.innerHTML = parseMarkdown(cellValue);
                    } else if (cellValue.includes('\\n')) {
                        // Just handle newlines
                        cellContent.innerHTML = cellValue.replace(/\\n/g, '<br>');
                    } else {
                        cellContent.textContent = cellValue;
                    }
                    
                    cellContent.style.color = col.textColor || '#000000';

                    if (col.font && col.font !== '') {
                        cellContent.style.fontFamily = `'${col.font}', monospace`;
                    }
                    
                    if (col.fontSize && col.fontSize !== '') {
                        cellContent.style.fontSize = col.fontSize + 'px';
                    }

                    // Apply cell-specific styles
                    const cellStyle = (sheet.cellStyles || {})[`${rowIndex}-${colIndex}`] || {};
                    if (cellStyle.bold) cellContent.style.fontWeight = 'bold';
                    if (cellStyle.italic) cellContent.style.fontStyle = 'italic';
                    if (cellStyle.center) cellContent.style.textAlign = 'center';
                    
                    // Handle borders properly
                    if (cellStyle.border === true) {
                        const borderWidth = cellStyle.borderWidth || '1px';
                        const borderStyle = cellStyle.borderStyle || 'solid';
                        const borderColor = cellStyle.borderColor || '#000000';
                        td.style.border = `${borderWidth} ${borderStyle} ${borderColor}`;
                    } else {
                        const gridColor = getComputedStyle(document.documentElement).getPropertyValue('--grid-line-color').trim() || '#dddddd';
                        td.style.border = `1px solid ${gridColor}`;
                    }
                    
                    if (cellStyle.bgColor) {
                        td.style.backgroundColor = cellStyle.bgColor;
                    }
                    if (cellStyle.textColor) {
                        cellContent.style.color = cellStyle.textColor;
                    }
                    if (cellStyle.fontSize) {
                        cellContent.style.fontSize = cellStyle.fontSize;
                    }

                    // Handle merged cells
                    const mergeInfo = (sheet.mergedCells || {})[`${rowIndex}-${colIndex}`];
                    if (mergeInfo) {
                        if (mergeInfo.hidden) {
                            td.style.display = 'none';
                            tr.appendChild(td);
                            return;
                        } else if (mergeInfo.colspan || mergeInfo.rowspan) {
                            td.colSpan = mergeInfo.colspan || 1;
                            td.rowSpan = mergeInfo.rowspan || 1;
                            td.classList.add('merged-cell');
                        }
                    }

                    td.appendChild(cellContent);
                    tr.appendChild(td);
                });

                tableBody.appendChild(tr);
            });
        }

        function stripMarkdown(text) {
            if (!text) return '';
            let stripped = String(text);
            // Remove bold markers: **text** -> text
            stripped = stripped.replace(/\\*\\*(.+?)\\*\\*/g, '$1');
            // Remove correct answer markers: [[text]] -> text
            stripped = stripped.replace(/\\[\\[(.+?)\\]\\]/g, '$1');
            // Remove bullet markers: - item -> item
            stripped = stripped.replace(/^\\s*-\\s+/gm, '');
            // Remove sub-bullet markers: -- item -> item
            stripped = stripped.replace(/^\\s*--\\s+/gm, '');
            // Remove sub-sub-bullet markers: --- item -> item
            stripped = stripped.replace(/^\\s*---\\s+/gm, '');
            // Remove Timeline markers: Timeline*Name or Timeline-R*Name -> Name
            stripped = stripped.replace(/^Timeline(?:C)?(?:-[A-Z]+)?\\*(.+?)$/gm, '$1');
            // Remove word connector markers: [1]Word or [1-R]Word -> Word
            stripped = stripped.replace(/\\[(\\d+)(?:-[A-Z]+)?\\](\\S+)/g, '$2');
            return stripped;
        }

        /**
         * Parse markdown syntax and convert to HTML
         * 
         * IMPORTANT: When adding new markdown syntax, add regex replacement here
         * This must match the parseMarkdown() function in static/script.js
         * 
         * Supported syntax:
         * - **bold** -> <strong>
         * - @@italic@@ -> <em>
         * - __underline__ -> <u>
         * - ~~strikethrough~~ -> <del>
         * - ^superscript^ -> <sup>
         * - ~subscript~ -> <sub>
         * - ##heading## -> larger text
         * - ..small text.. -> smaller text
         * - ----- -> horizontal separator line
         * - `code` -> <code>
         * - ==highlight== -> <mark>
         * - {link:url}text{/} -> clickable link
         * - {fg:color}text{/} or {bg:color}text{/} or {fg:color;bg:color}text{/} -> colored text
         * - - item -> bullet list
         * - -- subitem -> sub-bullet list
         * - 1. item -> numbered list
         * - ``` code block ```
         */
        /* ----------  PIPE-TABLE → CSS-GRID  ---------- */
        function parseGridTable(lines) {
            const rows = lines.map(l => {
                // Remove leading/trailing whitespace and pipes
                const trimmed = l.trim().replace(/^\\||\\|$/g, '');
                // Split by pipe and trim each cell
                const cells = trimmed.split('|').map(c => c.trim());
                return cells;
            });
            const cols = rows[0].length;
            
            // Check if first row is a header separator (e.g., |---|---|)
            const hasHeaderSeparator = rows.length > 1 && 
                rows[1].every(cell => /^-+$/.test(cell.trim()));
            
            // If header separator exists, skip it from rendering
            const dataRows = hasHeaderSeparator ? [rows[0], ...rows.slice(2)] : rows;
            const hasHeader = hasHeaderSeparator;
            
            // Color map for separator colors
            const colorMap = {
                'R': '#ff0000', 'G': '#00ff00', 'B': '#0000ff', 'Y': '#ffff00',
                'O': '#ff8800', 'P': '#ff00ff', 'C': '#00ffff', 'W': '#ffffff',
                'K': '#000000', 'GR': '#808080'
            };
            
            // Track column-wide colors (from :R-A: syntax in first row)
            const columnColors = [];
            
            // Process each cell and check for alignment markers and color codes
            const grid = dataRows.map((r, rowIndex) =>
                r.map((c, colIndex) => {
                    let align = 'left';
                    let content = c;
                    let borderColor = null;
                    
                    // Check for column-wide color code: :R-A:text or :G-A:text (only in first row)
                    if (rowIndex === 0) {
                        const columnColorMatch = content.match(/^:([A-Z]+)-A:(.+)$/);
                        if (columnColorMatch) {
                            const [, colorCode, rest] = columnColorMatch;
                            if (colorMap[colorCode]) {
                                columnColors[colIndex] = colorMap[colorCode];
                                borderColor = colorMap[colorCode];
                                content = rest;
                                
                                // Check if content also has alignment markers
                                if (content.startsWith(':') && content.endsWith(':') && content.length > 2) {
                                    align = 'center';
                                    content = content.slice(1, -1).trim();
                                } else if (content.endsWith(':')) {
                                    align = 'right';
                                    content = content.slice(0, -1).trim();
                                }
                            }
                        }
                    }
                    
                    // If no column-wide color was set, check for single-cell color: :R:text
                    if (!borderColor) {
                        const colorAlignMatch = content.match(/^:([A-Z]+):(.+)$/);
                        if (colorAlignMatch) {
                            const [, colorCode, rest] = colorAlignMatch;
                            if (colorMap[colorCode]) {
                                borderColor = colorMap[colorCode];
                                content = rest;
                                
                                // Check if content also has alignment markers
                                if (content.startsWith(':') && content.endsWith(':') && content.length > 2) {
                                    align = 'center';
                                    content = content.slice(1, -1).trim();
                                } else if (content.endsWith(':')) {
                                    align = 'right';
                                    content = content.slice(0, -1).trim();
                                }
                            }
                        }
                    }
                    
                    // Apply column-wide color if set and no cell-specific color
                    if (!borderColor && columnColors[colIndex]) {
                        borderColor = columnColors[colIndex];
                    }
                    
                    // Check for alignment without color codes
                    if (!borderColor && !content.match(/^:[A-Z]+:/)) {
                        // Check for center alignment :text:
                        if (content.startsWith(':') && content.endsWith(':') && content.length > 2) {
                            align = 'center';
                            content = content.slice(1, -1).trim();
                        }
                        // Check for right alignment text:
                        else if (content.endsWith(':') && !content.startsWith(':')) {
                            align = 'right';
                            content = content.slice(0, -1).trim();
                        }
                    }
                    
                    return {
                        content: parseMarkdownInline(content),
                        align: align,
                        borderColor: borderColor
                    };
                })
            );

            // First pass: identify ^^ cells and calculate rowspans
            const rowspans = {}; // key: "row-col", value: span count
            grid.forEach((row, rowIndex) => {
                row.forEach((cell, colIndex) => {
                    if (cell.content.trim() === '^^') {
                        // Find the first non-^^ cell above this one
                        let targetRow = rowIndex - 1;
                        while (targetRow >= 0 && grid[targetRow][colIndex].content.trim() === '^^') {
                            targetRow--;
                        }
                        if (targetRow >= 0) {
                            const targetKey = `${targetRow}-${colIndex}`;
                            rowspans[targetKey] = (rowspans[targetKey] || 1) + 1;
                        }
                    }
                });
            });

            /*  build a single <div> that looks like a table  */
            let html = `<div class="md-grid" style="--cols:${cols}">`;
            grid.forEach((row, i) => {
                row.forEach((cell, colIndex) => {
                    // Skip cells with ^^ (they're merged)
                    if (cell.content.trim() === '^^') {
                        return;
                    }

                    const key = `${i}-${colIndex}`;
                    const rowspan = rowspans[key] || 1;

                    let styles = [];
                    if (cell.align !== 'left') {
                        styles.push(`text-align: ${cell.align}`);
                    }
                    if (cell.borderColor) {
                        styles.push(`border-right-color: ${cell.borderColor} !important`);
                    }
                    if (rowspan > 1) {
                        styles.push(`grid-row: span ${rowspan}`);
                    }
                    const styleAttr = styles.length > 0 ? ` style="${styles.join('; ')}"` : '';
                    
                    // Check if cell content is only "-" (empty cell marker)
                    const isEmpty = cell.content.trim() === '-';
                    const emptyClass = isEmpty ? ' md-empty' : '';
                    // Only apply header class if we have a header separator and it's the first row
                    const isHeader = hasHeader && i === 0;
                    const rowspanAttr = rowspan > 1 ? ` rowspan="${rowspan}"` : '';
                    html += `<div class="md-cell ${isHeader ? 'md-header' : ''}${emptyClass}"${rowspanAttr}${styleAttr}>${cell.content}</div>`;
                });
            });
            html += '</div>';
            return html;
        }

        /*  inline parser for table cells - supports all markdown except lists  */
        function parseMarkdownInline(text) {
            let formatted = text;

            // Math: \\( ... \\) -> KaTeX (process first to avoid conflicts)
            if (window.katex) {
                formatted = formatted.replace(/\\\\\\((.*?)\\\\\\)/g, (match, math) => {
                    try {
                        console.log('KaTeX input:', math);
                        const result = katex.renderToString(math, {
                            throwOnError: false,
                            displayMode: false
                        });
                        console.log('KaTeX output:', result);
                        // Remove newlines in KaTeX output to prevent br insertion
                        return result.replace(/\\n/g, '');
                    } catch (e) {
                        console.error('KaTeX error:', e, 'Input was:', math);
                        return match;
                    }
                });
            }

            // Links: {link:url}text{/} -> <a href="url">text</a>
            formatted = formatted.replace(/\\{link:([^}]+)\\}(.+?)\\{\\/\\}/g, (match, url, text) => {
                return `<a href="${url}" target="_blank" rel="noopener noreferrer">${text}</a>`;
            });

            // Custom colors: {fg:color;bg:color}text{/} or {fg:color}text{/} or {bg:color}text{/}
            formatted = formatted.replace(/\\{((?:fg:[^;\\}\\s]+)?(?:;)?(?:bg:[^;\\}\\s]+)?)\\}(.+?)\\{\\/\\}/g, (match, styles, text) => {
                const styleObj = {};
                const parts = styles.split(';').filter(p => p.trim());
                let hasBg = false;
                parts.forEach(part => {
                    const [key, value] = part.split(':').map(s => s.trim());
                    if (key === 'fg') styleObj.color = value;
                    if (key === 'bg') {
                        styleObj.backgroundColor = value;
                        hasBg = true;
                    }
                });
                // Only add padding and border-radius if there's a background
                if (hasBg) {
                    styleObj.padding = '1px 6px';
                    styleObj.borderRadius = '4px';
                }
                styleObj.display = 'inline';
                styleObj.verticalAlign = 'baseline';
                styleObj.lineHeight = '1.3';
                styleObj.boxDecorationBreak = 'clone';
                styleObj.WebkitBoxDecorationBreak = 'clone';
                const styleStr = Object.entries(styleObj).map(([k, v]) => {
                    const cssKey = k.replace(/([A-Z])/g, '-$1').toLowerCase();
                    return cssKey + ': ' + v;
                }).join('; ');
                return '<span style="' + styleStr + '">' + text + '</span>';
            });

            // Border box: #R#text#/# -> colored border (letters only)
            formatted = formatted.replace(/#([A-Z]+)#(.+?)#\\/#/g, function(match, colorCode, text) {
                const colorMap = {
                    'R': '#ff0000', 'G': '#00ff00', 'B': '#0000ff', 'Y': '#ffff00',
                    'O': '#ff8800', 'P': '#ff00ff', 'C': '#00ffff', 'W': '#ffffff',
                    'K': '#000000', 'GR': '#808080'
                };
                if (colorMap[colorCode]) {
                    return '<span style="border: 2px solid ' + colorMap[colorCode] + '; padding: 2px 6px; border-radius: 4px; display: inline; box-decoration-break: clone; -webkit-box-decoration-break: clone;">' + text + '</span>';
                }
                return match;
            });

            // Variable font size heading: #2#text#/# -> custom size (2em, 1.5em, etc.)
            formatted = formatted.replace(/#([\\d.]+)#(.+?)#\\/#/g, function(match, size, text) {
                return '<span style="font-size: ' + size + 'em; font-weight: 600;">' + text + '</span>';
            });

            // Heading: ##text## -> larger text
            formatted = formatted.replace(/##(.+?)##/g, '<span style="font-size: 1.3em; font-weight: 600;">$1</span>');

            // Small text: ..text.. -> smaller text
            formatted = formatted.replace(/\\.\\.(.+?)\\.\\./g, '<span style="font-size: 0.75em;">$1</span>');

            // Wavy underline: _.text._ -> wavy underline
            formatted = formatted.replace(/_\\.(.+?)\\._/g, '<span style="text-decoration: underline wavy;">$1</span>');

            // Colored horizontal separator with optional background/text color for content below
            formatted = formatted.replace(/^([A-Z]+)?-{5,}((?:[A-Z]+)|(?:#[0-9a-fA-F]{6}(?:-#[0-9a-fA-F]{6})?))?$/gm, function(match, prefixColor, suffixColor) {
                const colorMap = {
                    'R': '#ff0000', 'G': '#00ff00', 'B': '#0000ff', 'Y': '#ffff00',
                    'O': '#ff8800', 'P': '#ff00ff', 'C': '#00ffff', 'W': '#ffffff',
                    'K': '#000000', 'GR': '#808080'
                };
                
                let separatorStyle = 'width: 100%; height: 4px; background: #ccc; margin: 6px 0; padding: 0; display: block; border: none; line-height: 0; font-size: 0;';
                if (prefixColor && colorMap[prefixColor]) {
                    separatorStyle = 'width: 100%; height: 4px; background: ' + colorMap[prefixColor] + '; margin: 6px 0; padding: 0; display: block; border: none; line-height: 0; font-size: 0;';
                }
                
                let result = '<div class="md-separator" style="' + separatorStyle + '"></div>';
                
                // Parse suffix color (can be color code or hex with optional text color)
                if (suffixColor) {
                    let bgColor = '';
                    let textColor = '';
                    
                    if (suffixColor.indexOf('#') === 0) {
                        // Hex color format: #RRGGBB or #RRGGBB-#RRGGBB
                        const hexParts = suffixColor.split('-');
                        bgColor = hexParts[0];
                        textColor = hexParts[1] || '';
                    } else if (colorMap[suffixColor]) {
                        // Color code format: R, G, B, etc.
                        bgColor = colorMap[suffixColor];
                    }
                    
                    if (bgColor) {
                        result += '<div class="md-bg-section" data-bg-color="' + bgColor + '" data-text-color="' + textColor + '">';
                    }
                }
                
                return result;
            });

            // Bold: **text** -> <strong>text</strong>
            formatted = formatted.replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>');

            // Italic: @@text@@ -> <em>text</em>
            formatted = formatted.replace(/@@(.+?)@@/g, '<em>$1</em>');

            // Colored underline: _R_text__ -> colored underline (must come before regular underline)
            formatted = formatted.replace(/_([A-Z]+)_(.+?)__/g, function(match, colorCode, text) {
                const colorMap = {
                    'R': '#ff0000', 'G': '#00ff00', 'B': '#0000ff', 'Y': '#ffff00',
                    'O': '#ff8800', 'P': '#ff00ff', 'C': '#00ffff', 'W': '#ffffff',
                    'K': '#000000', 'GR': '#808080'
                };
                if (colorMap[colorCode]) {
                    return '<u style="text-decoration-color: ' + colorMap[colorCode] + '; text-decoration-thickness: 2px;">' + text + '</u>';
                }
                return match;
            });

            // Underline: __text__ -> <u>text</u>
            formatted = formatted.replace(/__(.+?)__/g, '<u>$1</u>');

            // Strikethrough: ~~text~~ -> <del>text</del>
            formatted = formatted.replace(/~~(.+?)~~/g, '<del>$1</del>');

            // Superscript: ^text^ -> <sup>text</sup>
            formatted = formatted.replace(/\\^(.+?)\\^/g, '<sup>$1</sup>');

            // Subscript: ~text~ -> <sub>text</sub>
            formatted = formatted.replace(/~(.+?)~/g, '<sub>$1</sub>');

            // Inline code: `text` -> <code>text</code>
            formatted = formatted.replace(/`(.+?)`/g, '<code>$1</code>');

            // Highlight: ==text== -> <mark>text</mark>
            formatted = formatted.replace(/==(.+?)==/g, '<mark>$1</mark>');

            // Red highlight: !!text!! -> red background with white text
            formatted = formatted.replace(/!!(.+?)!!/g, '<span style="background: #ff0000; color: #ffffff; padding: 1px 4px; border-radius: 3px; display: inline; vertical-align: baseline; line-height: 1.3; box-decoration-break: clone; -webkit-box-decoration-break: clone;">$1</span>');

            // Blue highlight: ??text?? -> blue background with white text
            formatted = formatted.replace(/\\?\\?(.+?)\\?\\?/g, '<span style="background: #0000ff; color: #ffffff; padding: 1px 4px; border-radius: 3px; display: inline; vertical-align: baseline; line-height: 1.3; box-decoration-break: clone; -webkit-box-decoration-break: clone;">$1</span>');

            // Correct Answer: [[text]] -> hidden text with green highlight on click
            formatted = formatted.replace(/\\[\\[(.+?)\\]\\]/g, '<span class="correct-answer">$1</span>');

            // Word Connectors: [1]Word or [1-R]Word -> creates visual connection between words with same number
            var connectorColors = ['#007bff', '#dc3545', '#28a745', '#fd7e14', '#6f42c1', '#20c997', '#e83e8c', '#17a2b8'];
            var colorMap = {
                'R': '#ff0000', 'G': '#00ff00', 'B': '#0000ff', 'Y': '#ffff00',
                'O': '#ff8800', 'P': '#ff00ff', 'C': '#00ffff', 'W': '#ffffff',
                'K': '#000000', 'GR': '#808080'
            };
            formatted = formatted.replace(/\\[(\\d+)(?:-([A-Z]+))?\\](\\S+)/g, function(match, connId, colorCode, word) {
                var color;
                if (colorCode && colorMap[colorCode]) {
                    color = colorMap[colorCode];
                } else {
                    var colorIndex = (parseInt(connId) - 1) % connectorColors.length;
                    color = connectorColors[colorIndex];
                }
                return '<span class="word-connector" data-conn-id="' + connId + '" data-conn-color="' + color + '">' + word + '</span>';
            });

            // Collapsible text: {{text}} -> hidden text with toggle button
            formatted = formatted.replace(/\\{\\{(.+?)\\}\\}/g, function(match, content) {
                var id = 'collapse-' + Math.random().toString(36).substr(2, 9);
                return '<span class="collapsible-wrapper"><button class="collapsible-toggle" onclick="toggleCollapsible(\\'' + id + '\\')" title="Click to show/hide">👁️</button><span id="' + id + '" class="collapsible-content" style="display: none;">' + content + '</span></span>';
            });

            // Timeline: Timeline*Name or Timeline-R*Name or TimelineC-B*Name followed by list items
            // Timeline* = top-aligned, TimelineC* = center-aligned, -COLOR = custom separator color
            formatted = formatted.replace(/^(Timeline(?:C)?)(?:-([A-Z]+))?\\*(.+?)$/gm, function(match, type, colorCode, name) {
                var isCenter = type === 'TimelineC';
                var alignStyle = isCenter ? 'align-items: center;' : 'align-items: flex-start;';
                var colorMap = {
                    'R': '#ff0000', 'G': '#00ff00', 'B': '#0000ff', 'Y': '#ffff00',
                    'O': '#ff8800', 'P': '#ff00ff', 'C': '#00ffff', 'W': '#ffffff',
                    'K': '#000000', 'GR': '#808080'
                };
                var separatorColor = (colorCode && colorMap[colorCode]) ? colorMap[colorCode] : '#ffffff';
                return '<div class="md-timeline" style="display: flex; gap: 12px; margin: 8px 0; ' + alignStyle + '">' +
                    '<div class="md-timeline-left" style="flex: 0 0 150px; text-align: left; font-weight: 600; line-height: 1.4;">' + name + '</div>' +
                    '<div class="md-timeline-separator" style="width: 3px; background: ' + separatorColor + '; align-self: stretch; margin-top: 2px;"></div>' +
                    '<div class="md-timeline-right" style="flex: 1; line-height: 1.4;">';
            });

            // Apply custom color syntaxes
            formatted = applyCustomColorSyntaxes(formatted);

            return formatted;
        }

        function oldParseMarkdownBody(lines) {
            /* copy the *body* of the existing parser (bold, italic, lists …)
               but skip the table-splitting logic we just added. */
            let txt = lines.join('\\n');

            // Math: \\( ... \\) -> KaTeX (process first to avoid conflicts)
            if (window.katex) {
                txt = txt.replace(/\\\\\\((.*?)\\\\\\)/g, (match, math) => {
                    try {
                        console.log('KaTeX input (body):', math);
                        const result = katex.renderToString(math, {
                            throwOnError: false,
                            displayMode: false
                        });
                        console.log('KaTeX output (body):', result);
                        // Remove newlines in KaTeX output to prevent br insertion
                        return result.replace(/\\n/g, '');
                    } catch (e) {
                        console.error('KaTeX error (body):', e, 'Input was:', math);
                        return match;
                    }
                });
            }

            // Handle code blocks first (multiline)
            let inCodeBlock = false;
            const codeLines = txt.split('\\n');
            const formattedLines = codeLines.map(line => {
                let formatted = line;

                // Code block: ```text``` -> <code>text</code>
                if (formatted.trim() === '```') {
                    inCodeBlock = !inCodeBlock;
                    return ''; // Remove the ``` markers
                }

                if (inCodeBlock) {
                    return `<code>${formatted}</code>`;
                }

                // Links: {link:url}text{/} -> <a href="url">text</a>
                formatted = formatted.replace(/\\{link:([^}]+)\\}(.+?)\\{\\/\\}/g, (match, url, text) => {
                    return `<a href="${url}" target="_blank" rel="noopener noreferrer">${text}</a>`;
                });

                // Custom colors: {fg:color;bg:color}text{/} or {fg:color}text{/} or {bg:color}text{/}
                formatted = formatted.replace(/\\{((?:fg:[^;\\}\\s]+)?(?:;)?(?:bg:[^;\\}\\s]+)?)\\}(.+?)\\{\\/\\}/g, (match, styles, text) => {
                    const styleObj = {};
                    const parts = styles.split(';').filter(p => p.trim());
                    let hasBg = false;
                    parts.forEach(part => {
                        const [key, value] = part.split(':').map(s => s.trim());
                        if (key === 'fg') styleObj.color = value;
                        if (key === 'bg') {
                            styleObj.backgroundColor = value;
                            hasBg = true;
                        }
                    });
                    // Only add padding and border-radius if there's a background
                    if (hasBg) {
                        styleObj.padding = '1px 6px';
                        styleObj.borderRadius = '4px';
                    }
                    styleObj.display = 'inline';
                    styleObj.verticalAlign = 'baseline';
                    styleObj.lineHeight = '1.3';
                    styleObj.boxDecorationBreak = 'clone';
                    styleObj.WebkitBoxDecorationBreak = 'clone';
                    const styleStr = Object.entries(styleObj).map(([k, v]) => {
                        const cssKey = k.replace(/([A-Z])/g, '-$1').toLowerCase();
                        return `${cssKey}: ${v}`;
                    }).join('; ');
                    return `<span style="${styleStr}">${text}</span>`;
                });

                // Border box: #R#text#/# -> colored border (letters only)
                formatted = formatted.replace(/#([A-Z]+)#(.+?)#\\/#/g, function(match, colorCode, text) {
                    const colorMap = {
                        'R': '#ff0000', 'G': '#00ff00', 'B': '#0000ff', 'Y': '#ffff00',
                        'O': '#ff8800', 'P': '#ff00ff', 'C': '#00ffff', 'W': '#ffffff',
                        'K': '#000000', 'GR': '#808080'
                    };
                    if (colorMap[colorCode]) {
                        return '<span style="border: 2px solid ' + colorMap[colorCode] + '; padding: 2px 6px; border-radius: 4px; display: inline; box-decoration-break: clone; -webkit-box-decoration-break: clone;">' + text + '</span>';
                    }
                    return match;
                });

                // Variable font size heading: #2#text#/# -> custom size (2em, 1.5em, etc.)
                formatted = formatted.replace(/#([\\d.]+)#(.+?)#\\/#/g, function(match, size, text) {
                    return '<span style="font-size: ' + size + 'em; font-weight: 600;">' + text + '</span>';
                });

                // Heading: ##text## -> larger text
                formatted = formatted.replace(/##(.+?)##/g, '<span style="font-size: 1.3em; font-weight: 600;">$1</span>');

                // Small text: ..text.. -> smaller text
                formatted = formatted.replace(/\\.\\.(.+?)\\.\\./g, '<span style="font-size: 0.75em;">$1</span>');

                // Wavy underline: _.text._ -> wavy underline
                formatted = formatted.replace(/_\\.(.+?)\\._/g, '<span style="text-decoration: underline wavy;">$1</span>');

                // Colored horizontal separator with optional background/text color for content below
                formatted = formatted.replace(/^([A-Z]+)?-{5,}((?:[A-Z]+)|(?:#[0-9a-fA-F]{6}(?:-#[0-9a-fA-F]{6})?))?$/gm, function(match, prefixColor, suffixColor) {
                    const colorMap = {
                        'R': '#ff0000', 'G': '#00ff00', 'B': '#0000ff', 'Y': '#ffff00',
                        'O': '#ff8800', 'P': '#ff00ff', 'C': '#00ffff', 'W': '#ffffff',
                        'K': '#000000', 'GR': '#808080'
                    };
                    
                    let separatorStyle = 'width: 100%; height: 4px; background: #ccc; margin: 6px 0; padding: 0; display: block; border: none; line-height: 0; font-size: 0;';
                    if (prefixColor && colorMap[prefixColor]) {
                        separatorStyle = 'width: 100%; height: 4px; background: ' + colorMap[prefixColor] + '; margin: 6px 0; padding: 0; display: block; border: none; line-height: 0; font-size: 0;';
                    }
                    
                    let result = '<div class="md-separator" style="' + separatorStyle + '"></div>';
                    
                    // Parse suffix color (can be color code or hex with optional text color)
                    if (suffixColor) {
                        let bgColor = '';
                        let textColor = '';
                        
                        if (suffixColor.indexOf('#') === 0) {
                            // Hex color format: #RRGGBB or #RRGGBB-#RRGGBB
                            const hexParts = suffixColor.split('-');
                            bgColor = hexParts[0];
                            textColor = hexParts[1] || '';
                        } else if (colorMap[suffixColor]) {
                            // Color code format: R, G, B, etc.
                            bgColor = colorMap[suffixColor];
                        }
                        
                        if (bgColor) {
                            result += '<div class="md-bg-section" data-bg-color="' + bgColor + '" data-text-color="' + textColor + '">';
                        }
                    }
                    
                    return result;
                });

                // Bold: **text** -> <strong>text</strong>
                formatted = formatted.replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>');

                // Italic: @@text@@ -> <em>text</em>
                formatted = formatted.replace(/@@(.+?)@@/g, '<em>$1</em>');

                // Colored underline: _R_text__ -> colored underline (must come before regular underline)
                formatted = formatted.replace(/_([A-Z]+)_(.+?)__/g, function(match, colorCode, text) {
                    const colorMap = {
                        'R': '#ff0000', 'G': '#00ff00', 'B': '#0000ff', 'Y': '#ffff00',
                        'O': '#ff8800', 'P': '#ff00ff', 'C': '#00ffff', 'W': '#ffffff',
                        'K': '#000000', 'GR': '#808080'
                    };
                    if (colorMap[colorCode]) {
                        return '<u style="text-decoration-color: ' + colorMap[colorCode] + '; text-decoration-thickness: 2px;">' + text + '</u>';
                    }
                    return match;
                });

                // Underline: __text__ -> <u>text</u>
                formatted = formatted.replace(/__(.+?)__/g, '<u>$1</u>');

                // Strikethrough: ~~text~~ -> <del>text</del>
                formatted = formatted.replace(/~~(.+?)~~/g, '<del>$1</del>');

                // Superscript: ^text^ -> <sup>text</sup>
                formatted = formatted.replace(/\\^(.+?)\\^/g, '<sup>$1</sup>');

                // Subscript: ~text~ -> <sub>text</sub> (single tilde only, after strikethrough is processed)
                formatted = formatted.replace(/~(.+?)~/g, '<sub>$1</sub>');

                // Sub-sublist: --- item -> ▪ item with more indent (small square)
                if (formatted.trim().startsWith('--- ')) {
                    const content = formatted.replace(/^(\\s*)--- (.+)$/, '$2');
                    formatted = formatted.replace(/^(\\s*)--- .+$/, '$1<span style="display: inline-flex; align-items: flex-start; width: 100%; margin-left: 2em;"><span style="margin-right: 0.5em; flex-shrink: 0; line-height: 1; font-size: 0.75em; position: relative; top: 0.4em;">▪</span><span style="flex: 1;">▪CONTENT▪</span></span>');
                    formatted = formatted.replace('▪CONTENT▪', content);
                }
                // Sublist: -- item -> ◦ item with more indent (white circle)
                else if (formatted.trim().startsWith('-- ')) {
                    const content = formatted.replace(/^(\\s*)-- (.+)$/, '$2');
                    formatted = formatted.replace(/^(\\s*)-- .+$/, '$1<span style="display: inline-flex; align-items: flex-start; width: 100%; margin-left: 1em;"><span style="margin-right: 0.5em; flex-shrink: 0; line-height: 1; font-size: 0.9em; position: relative; top: 0.35em;">◦</span><span style="flex: 1;">◦CONTENT◦</span></span>');
                    formatted = formatted.replace('◦CONTENT◦', content);
                }
                // Bullet list: - item -> • item with hanging indent (black circle)
                else if (formatted.trim().startsWith('- ')) {
                    const content = formatted.replace(/^(\\s*)- (.+)$/, '$2');
                    formatted = formatted.replace(/^(\\s*)- .+$/, '$1<span style="display: inline-flex; align-items: flex-start; width: 100%;"><span style="margin-right: 0.5em; flex-shrink: 0; line-height: 1; font-size: 0.9em; position: relative; top: 0.35em;">•</span><span style="flex: 1;">•CONTENT•</span></span>');
                    formatted = formatted.replace('•CONTENT•', content);
                }

                // Numbered list: 1. item -> 1. item with hanging indent
                if (/^\\d+\\.\\s/.test(formatted.trim())) {
                    const match = formatted.match(/^(\\s*)(\\d+\\.\\s)(.+)$/);
                    if (match) {
                        const spaces = match[1];
                        const number = match[2];
                        const content = match[3];
                        formatted = `${spaces}<span style="display: inline-flex; align-items: baseline; width: 100%;"><span style="margin-right: 0.5em; flex-shrink: 0;">${number}</span><span style="flex: 1;">NUMCONTENT</span></span>`;
                        formatted = formatted.replace('NUMCONTENT', content);
                    }
                }

                // Inline code: `text` -> <code>text</code>
                formatted = formatted.replace(/`(.+?)`/g, '<code>$1</code>');

                // Highlight: ==text== -> <mark>text</mark>
                formatted = formatted.replace(/==(.+?)==/g, '<mark>$1</mark>');

                // Red highlight: !!text!! -> red background with white text
                formatted = formatted.replace(/!!(.+?)!!/g, '<span style="background: #ff0000; color: #ffffff; padding: 1px 4px; border-radius: 3px; display: inline; vertical-align: baseline; line-height: 1.3; box-decoration-break: clone; -webkit-box-decoration-break: clone;">$1</span>');

                // Blue highlight: ??text?? -> blue background with white text
                formatted = formatted.replace(/\\?\\?(.+?)\\?\\?/g, '<span style="background: #0000ff; color: #ffffff; padding: 1px 4px; border-radius: 3px; display: inline; vertical-align: baseline; line-height: 1.3; box-decoration-break: clone; -webkit-box-decoration-break: clone;">$1</span>');

                // Correct Answer: [[text]] -> hidden text with green highlight on click
                formatted = formatted.replace(/\\[\\[(.+?)\\]\\]/g, '<span class="correct-answer">$1</span>');

                // Word Connectors: [1]Word or [1-R]Word -> creates visual connection between words with same number
                var connectorColors = ['#007bff', '#dc3545', '#28a745', '#fd7e14', '#6f42c1', '#20c997', '#e83e8c', '#17a2b8'];
                var colorMap = {
                    'R': '#ff0000', 'G': '#00ff00', 'B': '#0000ff', 'Y': '#ffff00',
                    'O': '#ff8800', 'P': '#ff00ff', 'C': '#00ffff', 'W': '#ffffff',
                    'K': '#000000', 'GR': '#808080'
                };
                formatted = formatted.replace(/\\[(\\d+)(?:-([A-Z]+))?\\](\\S+)/g, function(match, connId, colorCode, word) {
                    var color;
                    if (colorCode && colorMap[colorCode]) {
                        color = colorMap[colorCode];
                    } else {
                        var colorIndex = (parseInt(connId) - 1) % connectorColors.length;
                        color = connectorColors[colorIndex];
                    }
                    return '<span class="word-connector" data-conn-id="' + connId + '" data-conn-color="' + color + '">' + word + '</span>';
                });

                // Collapsible text: {{text}} -> hidden text with toggle button
                formatted = formatted.replace(/\\{\\{(.+?)\\}\\}/g, function(match, content) {
                    var id = 'collapse-' + Math.random().toString(36).substr(2, 9);
                    return '<span class="collapsible-wrapper"><button class="collapsible-toggle" onclick="toggleCollapsible(\\'' + id + '\\')" title="Click to show/hide">👁️</button><span id="' + id + '" class="collapsible-content" style="display: none;">' + content + '</span></span>';
                });

                // Timeline: Timeline*Name or Timeline-R*Name or TimelineC-B*Name followed by list items
                // Timeline* = top-aligned, TimelineC* = center-aligned, -COLOR = custom separator color
                formatted = formatted.replace(/^(Timeline(?:C)?)(?:-([A-Z]+))?\\*(.+?)$/gm, function(match, type, colorCode, name) {
                    var isCenter = type === 'TimelineC';
                    var alignStyle = isCenter ? 'align-items: center;' : 'align-items: flex-start;';
                    var colorMap = {
                        'R': '#ff0000', 'G': '#00ff00', 'B': '#0000ff', 'Y': '#ffff00',
                        'O': '#ff8800', 'P': '#ff00ff', 'C': '#00ffff', 'W': '#ffffff',
                        'K': '#000000', 'GR': '#808080'
                    };
                    var separatorColor = (colorCode && colorMap[colorCode]) ? colorMap[colorCode] : '#ffffff';
                    return '<div class="md-timeline" style="display: flex; gap: 12px; margin: 8px 0; ' + alignStyle + '">' +
                        '<div class="md-timeline-left" style="flex: 0 0 150px; text-align: left; font-weight: 600; line-height: 1.4;">' + name + '</div>' +
                        '<div class="md-timeline-separator" style="width: 3px; background: ' + separatorColor + '; align-self: stretch; margin-top: 2px;"></div>' +
                        '<div class="md-timeline-right" style="flex: 1; line-height: 1.4;">';
                });

                // Apply custom color syntaxes
                formatted = applyCustomColorSyntaxes(formatted);

                return formatted;
            });

            // Post-process to close timeline divs and handle background sections
            var processedLines = [];
            var inTimeline = false;
            var inBgSection = false;
            var bgColor = '';
            var textColor = '';
            
            for (var i = 0; i < formattedLines.length; i++) {
                var line = formattedLines[i];
                var isTimelineStart = line.indexOf('class="md-timeline"') !== -1;
                var isListItem = line.trim().indexOf('<span style="display: inline-flex') === 0 && 
                                 (line.indexOf('•') !== -1 || line.indexOf('◦') !== -1 || line.indexOf('▪') !== -1);
                var isEmpty = line.trim() === '';
                
                // Check for background section markers (now with optional text color)
                var bgSectionMatch = line.match(/<div class="md-bg-section" data-bg-color="([^"]+)" data-text-color="([^"]*)">/);
                var isSeparator = line.includes('class="md-separator"');
                
                // If line has both separator and bg-section marker, handle both
                if (isSeparator && bgSectionMatch) {
                    if (inBgSection) {
                        processedLines.push('</div>');
                    }
                    processedLines.push(line);
                    // Open the background wrapper div with optional text color
                    bgColor = bgSectionMatch[1];
                    textColor = bgSectionMatch[2];
                    var styleStr = 'background-color: ' + bgColor + '; padding: 2px 6px; margin: 0;';
                    if (textColor) {
                        styleStr += ' color: ' + textColor + ';';
                    }
                    processedLines.push('<div style="' + styleStr + '">');
                    inBgSection = true;
                    continue;
                }
                
                // If we hit a separator without bg marker and we're in a background section, close it
                if (isSeparator && inBgSection) {
                    processedLines.push('</div>');
                    inBgSection = false;
                    bgColor = '';
                    processedLines.push(line);
                    continue;
                }
                
                // If we hit a separator and not in bg section, just push it
                if (isSeparator) {
                    processedLines.push(line);
                    continue;
                }
                
                if (isTimelineStart) {
                    processedLines.push(line);
                    inTimeline = true;
                } else if (inTimeline && isEmpty) {
                    processedLines.push('</div></div>');
                    processedLines.push(line);
                    inTimeline = false;
                } else if (inTimeline && !isListItem && line.trim() !== '') {
                    processedLines.push('</div></div>');
                    processedLines.push(line);
                    inTimeline = false;
                } else {
                    // Just push the line as-is (it's already inside the bg wrapper if inBgSection is true)
                    processedLines.push(line);
                }
            }
            
            // Close timeline at end if still open
            if (inTimeline) {
                processedLines.push('</div></div>');
            }
            
            // Close background section at end if still open
            if (inBgSection) {
                processedLines.push('</div>');
            }

            return processedLines.reduce(function(acc, line, i) {
                if (i === 0) return line;
                var prev = processedLines[i - 1];
                // Check for separator to avoid double line breaks
                var isSeparator = line.includes('md-separator');
                var prevIsSeparator = prev.includes('md-separator');
                
                // Check for background section wrapper
                var isBgWrapper = line.includes('background-color:') && line.trim().indexOf('<div style=') === 0;
                var prevIsBgWrapper = prev.includes('background-color:') && prev.trim().indexOf('<div style=') === 0;
                
                // Check for KaTeX output (don't add br inside KaTeX spans)
                var isKatex = line.includes('class="katex"') || prev.includes('class="katex"');
                
                // Don't add <br> after timeline opening or before timeline closing
                var isTimelineStart = prev.includes('class="md-timeline"');
                var isTimelineEnd = line === '</div></div>';
                var isListItem = line.trim().indexOf('<span style="display: inline-flex') === 0;
                
                if (isSeparator || prevIsSeparator || isBgWrapper || prevIsBgWrapper || isKatex || (isTimelineStart && isListItem) || isTimelineEnd) {
                    return acc + line;
                }
                return acc + '<br>' + line;
            }, '');
        }

        function parseMarkdown(text) {
            if (!text) return '';

            /* -----  GRID-TABLE DETECTION  ----- */
            const lines = text.split('\\n');
            
            // Detect table lines: either starts with | or contains | (for inline format like "Name | Age")
            const isTableLine = (line) => {
                const trimmed = line.trim();
                return trimmed.startsWith('|') || (trimmed.includes('|') && trimmed.split('|').length >= 2);
            };
            
            const hasGrid = lines.some(l => isTableLine(l));

            if (hasGrid) {
                const blocks = [];
                let cur = [], inGrid = false;

                lines.forEach(l => {
                    const isGrid = isTableLine(l);
                    if (isGrid !== inGrid) {
                        if (cur.length) blocks.push({ grid: inGrid, lines: cur });
                        cur = [];
                        inGrid = isGrid;
                    }
                    cur.push(l);
                });
                if (cur.length) blocks.push({ grid: inGrid, lines: cur });

                return blocks.map(b =>
                    b.grid ? parseGridTable(b.lines) : oldParseMarkdownBody(b.lines)
                ).join('<br>');
            }

            // If no grid table, process as normal markdown
            return oldParseMarkdownBody(lines);
        }

        function searchTable() {
            const searchInput = document.getElementById('searchInput');
            const searchTerm = searchInput.value.toLowerCase().trim();
            const table = document.getElementById('dataTable');
            const tbody = table.querySelector('tbody');
            const rows = tbody.querySelectorAll('tr');

            // Remove previous highlights
            document.querySelectorAll('.search-highlight').forEach(el => {
                el.classList.remove('search-highlight');
            });

            if (!searchTerm) {
                // Show all rows if search is empty
                rows.forEach(row => {
                    row.style.display = '';
                });
                return;
            }

            let foundCount = 0;

            rows.forEach(row => {
                const cells = row.querySelectorAll('td:not(.row-number)');
                let rowMatches = false;

                cells.forEach(cell => {
                    const cellContent = cell.querySelector('.cell-content');
                    if (cellContent) {
                        const cellValue = cellContent.textContent.toLowerCase();
                        // Strip markdown for searching
                        const strippedValue = stripMarkdown(cellValue);

                        if (strippedValue.includes(searchTerm)) {
                            rowMatches = true;
                            cell.classList.add('search-highlight');
                        }
                    }
                });

                if (rowMatches) {
                    row.style.display = '';
                    foundCount++;
                } else {
                    row.style.display = 'none';
                }
            });
        }

        function clearSearch() {
            const searchInput = document.getElementById('searchInput');
            searchInput.value = '';
            searchTable(); // This will show all rows and remove highlights
        }

        function toggleRowWrap() {
            const wrapToggle = document.getElementById('wrapToggle');
            const table = document.getElementById('dataTable');
            
            if (wrapToggle.checked) {
                table.classList.add('wrap-enabled');
                localStorage.setItem('rowWrapEnabled', 'true');
                
                // Convert all text content to wrapped display
                const cells = table.querySelectorAll('td:not(.row-number) .cell-content');
                cells.forEach(cellContent => {
                    const text = cellContent.textContent || cellContent.innerHTML;
                    if (text && text.length > 0) {
                        // Check if content needs wrapping (longer than typical cell width)
                        const tempSpan = document.createElement('span');
                        tempSpan.style.visibility = 'hidden';
                        tempSpan.style.position = 'absolute';
                        tempSpan.style.whiteSpace = 'nowrap';
                        tempSpan.textContent = text;
                        document.body.appendChild(tempSpan);
                        
                        const textWidth = tempSpan.offsetWidth;
                        const cellWidth = cellContent.closest('td').offsetWidth;
                        
                        document.body.removeChild(tempSpan);
                        
                        if (textWidth > cellWidth - 20) { // 20px padding
                            cellContent.closest('tr').classList.add('has-wrapped-content');
                        }
                    }
                });
            } else {
                table.classList.remove('wrap-enabled');
                localStorage.setItem('rowWrapEnabled', 'false');
                
                // Remove wrapped content classes
                const rows = table.querySelectorAll('tr.has-wrapped-content');
                rows.forEach(row => row.classList.remove('has-wrapped-content'));
            }
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            // Ctrl+F or Cmd+F to focus search
            if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
                e.preventDefault();
                const searchInput = document.getElementById('searchInput');
                if (searchInput) {
                    searchInput.focus();
                    searchInput.select();
                }
            }
            
            // Escape to clear search
            if (e.key === 'Escape' && document.activeElement.id === 'searchInput') {
                clearSearch();
            }
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function(event) {
            const sheetSelector = document.querySelector('.sheet-selector');
            const sheetList = document.getElementById('sheetList');
            if (!sheetSelector.contains(event.target)) {
                sheetList.classList.remove('show');
            }

            // Toggle correct answer on click
            if (event.target.classList.contains('correct-answer')) {
                event.target.classList.toggle('revealed');
            }
        });

        function toggleRowNumbers() {
            const rowToggle = document.getElementById('rowToggle');
            const table = document.getElementById('dataTable');

            if (rowToggle.checked) {
                table.classList.remove('hide-row-numbers');
                localStorage.setItem('rowNumbersVisible', 'true');
            } else {
                table.classList.add('hide-row-numbers');
                localStorage.setItem('rowNumbersVisible', 'false');
            }
        }

        let fontSizeScale = parseFloat(localStorage.getItem('fontSizeScale')) || 1.0;

        function adjustFontSize(delta) {
            fontSizeScale += delta * 0.1;
            fontSizeScale = Math.max(0.5, Math.min(2.0, fontSizeScale)); // Limit between 50% and 200%
            
            localStorage.setItem('fontSizeScale', fontSizeScale);
            
            // Update display
            document.getElementById('fontSizeDisplay').textContent = Math.round(fontSizeScale * 100) + '%';
            
            // Apply to all cell content
            const cells = document.querySelectorAll('.cell-content');
            cells.forEach(cell => {
                const currentFontSize = parseFloat(window.getComputedStyle(cell).fontSize);
                const baseFontSize = currentFontSize / (parseFloat(cell.dataset.fontScale) || 1.0);
                cell.style.fontSize = (baseFontSize * fontSizeScale) + 'px';
                cell.dataset.fontScale = fontSizeScale;
            });
        }

        function applyFontSizeScale() {
            const cells = document.querySelectorAll('.cell-content');
            cells.forEach(cell => {
                const currentFontSize = parseFloat(window.getComputedStyle(cell).fontSize);
                if (currentFontSize && fontSizeScale !== 1.0) {
                    cell.style.fontSize = (currentFontSize * fontSizeScale) + 'px';
                    cell.dataset.fontScale = fontSizeScale;
                }
            });
            document.getElementById('fontSizeDisplay').textContent = Math.round(fontSizeScale * 100) + '%';
        }

        function toggleCollapsible(id) {
            const element = document.getElementById(id);
            if (element) {
                if (element.style.display === 'none') {
                    element.style.display = 'inline';
                } else {
                    element.style.display = 'none';
                }
            }
        }

        function drawWordConnectors(container) {
            if (!container) return;
            
            container.querySelectorAll('.word-connector-line').forEach(el => el.remove());
            
            const connectorGroups = {};
            container.querySelectorAll('.word-connector').forEach(connector => {
                const connId = connector.dataset.connId;
                if (!connectorGroups[connId]) {
                    connectorGroups[connId] = [];
                }
                connectorGroups[connId].push(connector);
            });
            
            Object.entries(connectorGroups).forEach(([connId, connectors]) => {
                if (connectors.length < 2) return;
                
                connectors.sort((a, b) => {
                    const rectA = a.getBoundingClientRect();
                    const rectB = b.getBoundingClientRect();
                    return rectA.left - rectB.left;
                });
                
                const color = connectors[0].dataset.connColor;
                
                for (let i = 0; i < connectors.length - 1; i++) {
                    const start = connectors[i];
                    const end = connectors[i + 1];
                    
                    // Get bounding rectangles
                    const startRect = start.getBoundingClientRect();
                    const endRect = end.getBoundingClientRect();
                    const containerRect = container.getBoundingClientRect();
                    
                    // Calculate positions relative to container
                    const startX = startRect.left - containerRect.left + startRect.width / 2;
                    const endX = endRect.left - containerRect.left + endRect.width / 2;
                    const y = startRect.bottom - containerRect.top + 2;
                    
                    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
                    svg.classList.add('word-connector-line');
                    svg.style.left = (Math.min(startX, endX) - 3) + 'px';
                    svg.style.top = y + 'px';
                    svg.style.width = (Math.abs(endX - startX) + 6) + 'px';
                    svg.style.height = '12px';
                    svg.style.position = 'absolute';
                    svg.style.overflow = 'visible';
                    
                    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                    const width = Math.abs(endX - startX);
                    // Draw U-shape with arrow tips at top of both verticals (offset by 3 for padding)
                    const d = `M 3,9 L 3,2 M 3,9 L ${width+3},9 M ${width+3},9 L ${width+3},2 M 1.5,4 L 3,2 L 4.5,4 M ${width+1.5},4 L ${width+3},2 L ${width+4.5},4`;
                    path.setAttribute('d', d);
                    path.setAttribute('stroke', color);
                    path.setAttribute('stroke-width', '2');
                    path.setAttribute('fill', 'none');
                    path.setAttribute('stroke-linecap', 'round');
                    path.setAttribute('stroke-linejoin', 'round');
                    
                    svg.appendChild(path);
                    container.appendChild(svg);
                }
            });
        }

        function toggleAllCollapsibles() {
            const collapsibles = document.querySelectorAll('.collapsible-content');
            const correctAnswers = document.querySelectorAll('.correct-answer');
            if (collapsibles.length === 0 && correctAnswers.length === 0) {
                alert('No hidden content found');
                return;
            }

            // Check if any are visible/revealed
            const anyVisible = Array.from(collapsibles).some(el => el.style.display !== 'none') ||
                Array.from(correctAnswers).some(el => el.classList.contains('revealed'));

            // Toggle all to opposite state
            collapsibles.forEach(el => {
                el.style.display = anyVisible ? 'none' : 'inline';
            });
            correctAnswers.forEach(el => {
                if (anyVisible) {
                    el.classList.remove('revealed');
                } else {
                    el.classList.add('revealed');
                }
            });
        }

        function openSettings() {
            const modal = document.getElementById('settingsModal');
            modal.style.display = 'flex';
            
            // Load current grid line color
            const savedColor = localStorage.getItem('gridLineColor') || '#dddddd';
            document.getElementById('gridLineColor').value = savedColor;
            document.getElementById('gridLineColorText').value = savedColor.substring(1).toUpperCase();
        }

        function closeSettings() {
            const modal = document.getElementById('settingsModal');
            modal.style.display = 'none';
        }

        function syncGridLineColor(value) {
            // Handle input with or without # prefix
            let colorValue = value;
            if (!colorValue.startsWith('#')) {
                colorValue = '#' + colorValue;
            }

            // Validate hex color
            if (/^#[0-9A-Fa-f]{6}$/.test(colorValue) || /^#[0-9A-Fa-f]{3}$/.test(colorValue)) {
                document.getElementById('gridLineColor').value = colorValue;
                document.getElementById('gridLineColorText').value = colorValue.substring(1).toUpperCase();
                applyGridLineColor(colorValue);
            }
        }

        function applyGridLineColor(color) {
            // Apply the color to CSS variables
            document.documentElement.style.setProperty('--grid-line-color', color);
            localStorage.setItem('gridLineColor', color);
            
            // Re-render table to apply new color
            renderTable();
        }

        function resetGridLineColor() {
            const defaultColor = '#dddddd';
            document.getElementById('gridLineColor').value = defaultColor;
            document.getElementById('gridLineColorText').value = defaultColor.substring(1).toUpperCase();
            applyGridLineColor(defaultColor);
        }

        // Close modal when clicking outside
        window.onclick = function(event) {
            const modal = document.getElementById('settingsModal');
            if (event.target === modal) {
                closeSettings();
            }
        }

        // ==================== CUSTOM COLOR SYNTAX ====================
        let customColorSyntaxes = ''' + json.dumps(custom_syntaxes) + ''';

        function loadCustomColorSyntaxes() {
            // Syntaxes are embedded from JSON file during export
        }

        function applyCustomColorSyntaxes(text) {
            let formatted = text;
            customColorSyntaxes.forEach(syntax => {
                if (!syntax.marker) return;
                const escapedMarker = syntax.marker.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&');
                const regex = new RegExp(escapedMarker + '(.+?)' + escapedMarker, 'g');
                formatted = formatted.replace(regex, (match, content) => {
                    return '<span style="background: ' + syntax.bgColor + '; color: ' + syntax.fgColor + '; padding: 1px 4px; border-radius: 3px; display: inline; vertical-align: baseline; line-height: 1.3; box-decoration-break: clone; -webkit-box-decoration-break: clone;">' + content + '</span>';
                });
            });
            return formatted;
        }

        // Initialize on load
        window.onload = function() {
            loadCustomColorSyntaxes();
            // Apply saved grid line color
            const savedGridColor = localStorage.getItem('gridLineColor') || '#dddddd';
            document.documentElement.style.setProperty('--grid-line-color', savedGridColor);
            
            initializeCategories();
            renderSidebar();
            renderTable();
            
            // Draw word connectors after table is rendered
            setTimeout(() => {
                // For static export, draw connectors on the table cells directly
                const table = document.getElementById('dataTable');
                if (table) {
                    table.querySelectorAll('td:not(.row-number)').forEach(cell => {
                        const cellContent = cell.querySelector('.cell-content');
                        if (cellContent && cellContent.querySelector('.word-connector')) {
                            drawWordConnectors(cellContent);
                        }
                    });
                }
            }, 500);
            
            // Restore wrap toggle state
            const wrapEnabled = localStorage.getItem('rowWrapEnabled') === 'true';
            const wrapToggle = document.getElementById('wrapToggle');
            if (wrapToggle) {
                wrapToggle.checked = wrapEnabled;
                if (wrapEnabled) {
                    document.getElementById('dataTable').classList.add('wrap-enabled');
                }
            }
            
            // Restore row numbers toggle state
            const rowNumbersVisible = localStorage.getItem('rowNumbersVisible') !== 'false'; // Default true
            const rowToggle = document.getElementById('rowToggle');
            if (rowToggle) {
                rowToggle.checked = rowNumbersVisible;
                if (!rowNumbersVisible) {
                    document.getElementById('dataTable').classList.add('hide-row-numbers');
                }
            }
            
            // Apply saved font size scale
            setTimeout(() => {
                applyFontSizeScale();
            }, 100);
        };
    </script>
</head>
<body>
    <!-- Sidebar Navigation -->
    <div id="sidebarOverlay" class="sidebar-overlay" onclick="toggleSidebar()"></div>
    <div id="sidebar" class="sidebar">
        <div id="sidebarTree" class="sidebar-tree">
            <!-- Tree content will be rendered here -->
        </div>
    </div>

    <div class="container">
        <div class="sheet-tabs">
            <button class="btn-menu" onclick="toggleSidebar()" title="Open Navigation">☰</button>
            <div class="current-sheet-info">
                <span id="currentSheetTitle" class="current-sheet-title">Sheet1</span>
                <span id="currentCategoryTitle" class="current-category-title">Uncategorized</span>
            </div>

            <div class="search-box">
                <input type="text" id="searchInput" placeholder="Search..." onkeyup="searchTable()" title="Search in all cells">
                <button onclick="clearSearch()" class="btn-clear-search" title="Clear search">×</button>
            </div>

            <div class="button-group">
                <label class="btn-icon-toggle" title="Enable text wrapping - Press Enter for new lines">
                    <input type="checkbox" id="wrapToggle" onchange="toggleRowWrap()">
                    <span>↩️</span>
                </label>
                
                <label class="btn-icon-toggle" title="Show or hide row numbers">
                    <input type="checkbox" id="rowToggle" onchange="toggleRowNumbers()" checked>
                    <span>#️⃣</span>
                </label>

                <button onclick="toggleAllCollapsibles()" class="btn-icon-toggle" title="Show/hide all collapsible text">
                    <span>👁️</span>
                </button>
            </div>

            <div class="font-size-control">
                <span class="font-size-label">Font:</span>
                <button onclick="adjustFontSize(-1)" class="btn-font-size" title="Decrease font size">−</button>
                <span id="fontSizeDisplay" class="font-size-display">100%</span>
                <button onclick="adjustFontSize(1)" class="btn-font-size" title="Increase font size">+</button>
            </div>

            <button onclick="openSettings()" class="btn-icon-toggle" title="Settings" style="margin-left: 5px;">
                <span>⚙️</span>
            </button>
        </div>

        <!-- Sub-Sheet Navigation Bar -->
        <div class="subsheet-bar" id="subsheetBar">
            <div class="subsheet-tabs" id="subsheetTabs">
                <!-- Sub-sheets will be rendered here -->
            </div>
        </div>

        <div class="table-container">
            <table id="dataTable">
                <thead id="tableHead">
                    <tr id="headerRow"></tr>
                </thead>
                <tbody id="tableBody"></tbody>
            </table>
        </div>
    </div>

    <!-- Settings Modal -->
    <div id="settingsModal" class="modal" style="display: none;">
        <div class="modal-content settings-modal">
            <div class="modal-header">
                <h2>Settings</h2>
                <span class="close" onclick="closeSettings()">&times;</span>
            </div>
            <div class="settings-content">
                <div class="settings-section">
                    <h3 class="settings-section-title">🎨 Appearance</h3>
                    <div class="settings-item">
                        <div class="settings-item-header">
                            <label for="gridLineColor" class="settings-label">Grid Line Color</label>
                            <button class="btn-reset" onclick="resetGridLineColor()">Reset to Default</button>
                        </div>
                        <div class="color-picker-group">
                            <div class="color-picker-wrapper">
                                <input type="color" id="gridLineColor" value="#dddddd" oninput="syncGridLineColor(this.value)">
                                <span class="color-picker-label">Pick Color</span>
                            </div>
                            <div class="color-input-wrapper">
                                <span class="color-input-prefix">#</span>
                                <input type="text" id="gridLineColorText" value="DDDDDD" maxlength="6" placeholder="DDDDDD" oninput="syncGridLineColor('#' + this.value)">
                            </div>
                        </div>
                        <p class="settings-description">Customize the color of table borders and cell separators</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>'''

    return html_content

def export_to_static():
    """Main export function"""
    try:
        # Check if data file exists
        if not os.path.exists(DATA_FILE):
            print(f"ERROR: Data file not found: {DATA_FILE}")
            return False
        
        # Load data
        data = load_data()
        print(f"Loaded data with {len(data.get('sheets', []))} sheets")
        
        # Load custom syntaxes
        custom_syntaxes = load_custom_syntaxes()
        print(f"Loaded {len(custom_syntaxes)} custom color syntaxes")
        
        # Generate HTML
        html_content = generate_static_html(data, custom_syntaxes)
        
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