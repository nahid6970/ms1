import sys
import json
import os

def toggle_bookmark(command, shell="pwsh"):
    bookmarks_file = "C:\\@delta\\db\\FZF_launcher\\command_bookmarks.json"
    
    # Strip markers if present
    if command.startswith("* "): command = command[2:]
    elif command.startswith("  "): command = command[2:]
    
    if not command.strip():
        return

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
    exists = False
    for i, bm in enumerate(bookmarks):
        if bm['command'] == command:
            bookmarks.pop(i)
            exists = True
            break
            
    # Add new bookmark if it didn't exist
    if not exists:
        bookmarks.append({"command": command, "shell": shell})
    
    with open(bookmarks_file, 'w', encoding='utf-8') as f:
        json.dump(bookmarks, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        shell = sys.argv[2] if len(sys.argv) > 2 else "pwsh"
        toggle_bookmark(command, shell)
