import sys
import json
import os

def add_bookmark(command, shell="pwsh"):
    bookmarks_file = "C:\\Users\\nahid\\script_output\\command_bookmarks.json"
    
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
    
    # Check if already bookmarked
    for bm in bookmarks:
        if bm['command'] == command:
            return
            
    # Add new bookmark
    bookmarks.append({"command": command, "shell": shell})
    
    with open(bookmarks_file, 'w', encoding='utf-8') as f:
        json.dump(bookmarks, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        shell = sys.argv[2] if len(sys.argv) > 2 else "pwsh"
        add_bookmark(command, shell)
