import os
import json
import re
import sys
import hashlib
import shutil
from datetime import datetime

# ————— CONFIG —————
SCAN_ALL    = True
EXTENSIONS  = (".py", ".ahk", ".ps1", ".bat", ".txt")
SKIP_DIRS   = {'.git', '__pycache__', '.vscode', 'node_modules'}
SAVE_FILE   = "paths_before.json"
LOG_FILE    = "path_replacements.log"
BACKUP_DIR  = r"C:\msBackups\bak"
# ——————————————————

def hash_file(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None

def get_all_files_with_hashes(base_path):
    d = {}
    for root, dirs, files in os.walk(base_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            if not SCAN_ALL and not fn.endswith(EXTENSIONS):
                continue
            full = os.path.normpath(os.path.join(root, fn))
            h = hash_file(full)
            if h:
                d.setdefault(h, []).append(full)
    return d

def save_snapshot(base_path):
    snap = get_all_files_with_hashes(base_path)
    with open(SAVE_FILE, 'w', encoding='utf-8') as f:
        json.dump(snap, f, indent=2)
    total = sum(len(v) for v in snap.values())
    print(f"✅ Snapshot saved: {total} files logged.")

def load_snapshot():
    if not os.path.exists(SAVE_FILE):
        print("❌ No snapshot found. Run `scan` first.")
        sys.exit(1)
    return json.load(open(SAVE_FILE, 'r', encoding='utf-8'))

def backup_file(original_path):
    rel        = os.path.relpath(original_path).replace("\\", "_").replace("/", "_")
    timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak_name   = f"{rel}_{timestamp}.bak"
    bak_folder = BACKUP_DIR
    os.makedirs(bak_folder, exist_ok=True)
    bak_path   = os.path.join(bak_folder, bak_name)
    shutil.copy2(original_path, bak_path)
    return bak_path

def replace_in_file(path, old_p, new_p, log):
    try:
        txt = open(path, 'r', encoding='utf-8', errors='ignore').read()
    except:
        return

    orig    = txt
    entries = []
    variants = {
        old_p,
        old_p.replace("\\", "/"),
        old_p.replace("/", "\\"),
        old_p.replace("\\", "\\\\"),
    }

    for var in variants:
        if var in txt:
            # preserve slash style:
            if "\\\\" in var:
                rp = new_p.replace("\\", "\\\\")
            elif "/" in var:
                rp = new_p.replace("\\", "/")
            else:
                rp = new_p
            pat = re.escape(var)
            txt = re.sub(pat, lambda m, rp=rp: rp, txt)
            entries.append(f"    {var} → {rp}")

    if entries and txt != orig:
        bak = backup_file(path)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(txt)
        print(f"🔁 Updated: {path} (backup: {bak})")
        log.append(path)
        log.extend(entries)

def update_references(base_path):
    old_snap = load_snapshot()
    new_snap = get_all_files_with_hashes(base_path)

    mappings = []
    for h, old_list in old_snap.items():
        new_list = new_snap.get(h, [])
        removed  = sorted(set(old_list) - set(new_list))
        added    = sorted(set(new_list) - set(old_list))
        # pair one‑to‑one by sorted order
        for old_path, new_path in zip(removed, added):
            mappings.append((old_path, new_path))

    if not mappings:
        print("📦 No renamed/moved files found.")
        return

    print(f"🔍 Detected {len(mappings)} renamed/moved files.")

    # gather all files to scan
    all_files = []
    for root, dirs, files in os.walk(base_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            if SCAN_ALL or fn.endswith(EXTENSIONS):
                all_files.append(os.path.normpath(os.path.join(root, fn)))

    log_entries = []
    for file_path in all_files:
        for old_p, new_p in mappings:
            replace_in_file(file_path, old_p, new_p, log_entries)

    if log_entries:
        with open(LOG_FILE, 'a', encoding='utf-8') as L:
            L.write(f"\n--- {datetime.now()} ---\n")
            L.write("\n".join(log_entries) + "\n")
        print(f"📝 Log saved → {LOG_FILE}")

if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("scan", "update"):
        print("Usage:\n  python path_tracker.py scan <folder>\n  python path_tracker.py update <folder>")
        sys.exit(1)

    cmd, folder = sys.argv[1], sys.argv[2]
    if not os.path.isdir(folder):
        print("❌ Folder not found.")
        sys.exit(1)

    if cmd == "scan":
        save_snapshot(folder)
    else:
        update_references(folder)
