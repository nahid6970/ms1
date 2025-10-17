import sys
import json
import os

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        bookmarks_file = r"C:\Users\nahid\script_output\bookmarks.json"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(bookmarks_file), exist_ok=True)
        
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
