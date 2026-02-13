import json
import os
import sys

def remove_bookmark(command):
    bookmarks_file = "C:\\@delta\\db\\FZF_launcher\\command_bookmarks.json"
    if not os.path.exists(bookmarks_file):
        return
    
    # Strip markers
    if command.startswith("* "): command = command[2:]
    elif command.startswith("  "): command = command[2:]

    try:
        with open(bookmarks_file, 'r', encoding='utf-8') as f:
            bookmarks = json.load(f)
    except json.JSONDecodeError:
        return
    
    # Filter out the command
    new_bookmarks = [bm for bm in bookmarks if bm['command'] != command]
    
    if len(new_bookmarks) != len(bookmarks):
        with open(bookmarks_file, 'w', encoding='utf-8') as f:
            json.dump(new_bookmarks, f, indent=2, ensure_ascii=False)

def get_bookmarks_display():
    bookmarks_file = "C:\\@delta\\db\\FZF_launcher\\command_bookmarks.json"
    if not os.path.exists(bookmarks_file):
        return ""
    
    try:
        with open(bookmarks_file, 'r', encoding='utf-8') as f:
            bookmarks = json.load(f)
        
        output = []
        for bm in bookmarks:
            # Format: [shell] command
            output.append(f"[{bm.get('shell', 'pwsh')}] {bm['command']}")
        return "\n".join(output)
    except:
        return ""

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--remove" and len(sys.argv) > 2:
            remove_bookmark(sys.argv[2])
        elif sys.argv[1] == "--reload":
            print(get_bookmarks_display())
        else:
            # Default to removal if just a command is passed
            remove_bookmark(sys.argv[1])
