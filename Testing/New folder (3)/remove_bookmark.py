import sys
import json
import os

def remove_bookmark(file_path):
    """Remove a file path from bookmarks.json"""
    bookmarks_file = r"C:\Users\nahid\script_output\bookmarks.json"
    
    if not os.path.exists(bookmarks_file):
        return
    
    try:
        with open(bookmarks_file, 'r', encoding='utf-8') as f:
            bookmarks = json.load(f)
    except json.JSONDecodeError:
        return
    
    if file_path in bookmarks:
        bookmarks.remove(file_path)
        with open(bookmarks_file, 'w', encoding='utf-8') as f:
            json.dump(bookmarks, f, indent=2, ensure_ascii=False)
        print(f"✗ Removed bookmark: {os.path.basename(file_path)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        remove_bookmark(sys.argv[1])
