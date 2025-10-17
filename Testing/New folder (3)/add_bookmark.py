import sys
import json
import os

def add_bookmark(file_path):
    """Add a file path to bookmarks.json"""
    bookmarks_file = r"C:\Users\nahid\script_output\bookmarks.json"
    
    # Load existing bookmarks
    bookmarks = []
    if os.path.exists(bookmarks_file):
        try:
            with open(bookmarks_file, 'r', encoding='utf-8') as f:
                bookmarks = json.load(f)
        except json.JSONDecodeError:
            bookmarks = []
    
    # Add new bookmark if not already present
    if file_path not in bookmarks:
        bookmarks.append(file_path)
        with open(bookmarks_file, 'w', encoding='utf-8') as f:
            json.dump(bookmarks, f, indent=2, ensure_ascii=False)
        print(f"✓ Bookmarked: {os.path.basename(file_path)}")
    else:
        print(f"Already bookmarked: {os.path.basename(file_path)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        add_bookmark(sys.argv[1])
