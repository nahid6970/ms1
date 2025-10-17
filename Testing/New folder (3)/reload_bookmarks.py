import json
import os

def reload_bookmarks():
    """Output current bookmarks for fzf reload"""
    bookmarks_file = r"C:\Users\nahid\script_output\bookmarks.json"
    
    if not os.path.exists(bookmarks_file):
        return
    
    try:
        with open(bookmarks_file, 'r', encoding='utf-8') as f:
            bookmarks = json.load(f)
        
        # Filter valid bookmarks
        valid_bookmarks = [b for b in bookmarks if os.path.exists(b)]
        
        for bookmark in valid_bookmarks:
            print(bookmark)
    except:
        pass

if __name__ == "__main__":
    reload_bookmarks()
