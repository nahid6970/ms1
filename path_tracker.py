import os
import json
import re
import sys
import hashlib

EXTENSIONS = (".py", ".ahk", ".ps1", ".bat", ".txt")
SAVE_FILE = "paths_before.json"

def hash_file(path):
    """Create a SHA256 hash of the file content"""
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        return None

def get_all_files_with_hashes(base_path):
    result = {}
    for root, _, files in os.walk(base_path):
        for file in files:
            if file.endswith(EXTENSIONS):
                full_path = os.path.normpath(os.path.join(root, file))
                file_hash = hash_file(full_path)
                if file_hash:
                    result[file_hash] = full_path
    return result

def save_snapshot(base_path):
    files = get_all_files_with_hashes(base_path)
    with open(SAVE_FILE, 'w', encoding='utf-8') as f:
        json.dump(files, f, indent=2)
    print(f"✅ Snapshot saved with {len(files)} files.")

def load_snapshot():
    if not os.path.exists(SAVE_FILE):
        print("❌ No snapshot found. Run `scan` first.")
        return {}
    with open(SAVE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def replace_path_references_in_file(file_path, old_path, new_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        original = content
        for variant in {old_path, old_path.replace("\\", "/"), old_path.replace("\\", "\\\\")}:
            pattern = re.escape(variant)
            content = re.sub(pattern, new_path.replace("\\", "\\\\"), content)

        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"🔁 Updated path in: {file_path}")
    except Exception as e:
        print(f"⚠️ Error updating {file_path}: {e}")

def update_references(base_path):
    old_snapshot = load_snapshot()
    new_snapshot = get_all_files_with_hashes(base_path)

    renamed_files = []
    for file_hash, old_path in old_snapshot.items():
        new_path = new_snapshot.get(file_hash)
        if new_path and new_path != old_path:
            renamed_files.append((old_path, new_path))

    if not renamed_files:
        print("📦 No renamed/moved files found.")
        return

    print(f"🔍 Detected {len(renamed_files)} renamed/moved files.")

    # Replace references to old paths in all scripts
    all_files = list(new_snapshot.values())
    for script_path in all_files:
        for old_path, new_path in renamed_files:
            replace_path_references_in_file(script_path, old_path, new_path)

if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ['scan', 'update']:
        print("Usage:\n  python path_tracker.py scan <folder_path>\n  python path_tracker.py update <folder_path>")
        sys.exit(1)

    mode, folder = sys.argv[1], sys.argv[2]
    if not os.path.exists(folder):
        print("❌ Provided folder does not exist.")
        sys.exit(1)

    if mode == "scan":
        save_snapshot(folder)
    elif mode == "update":
        update_references(folder)
