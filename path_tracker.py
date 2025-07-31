import os
import json
import re
import sys
import hashlib
import shutil
from datetime import datetime
import customtkinter as ctk
from tkinter import filedialog
import threading
import queue

# ————— CONFIG —————
SCAN_ALL    = True
EXTENSIONS  = (".py", ".ahk", ".ps1", ".bat", ".txt")
SKIP_DIRS   = {'.git', '__pycache__', '.vscode', 'node_modules'}
SAVE_FILE   = r"C:\Users\nahid\script_output\paths_before.json"
LOG_FILE    = r"C:\Users\nahid\script_output\path_replacements.log"
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

def get_all_files_with_hashes(base_paths, log_callback):
    """Modified to accept multiple base paths"""
    d = {}
    file_count = 0
    
    # Handle single path or list of paths
    if isinstance(base_paths, str):
        base_paths = [base_paths]
    
    for base_path in base_paths:
        log_callback(f"Scanning folder: {base_path}")
        for root, dirs, files in os.walk(base_path):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for fn in files:
                file_count += 1
                if file_count % 100 == 0:
                    log_callback(f"Scanning... {file_count} files processed.")
                if not SCAN_ALL and not fn.endswith(EXTENSIONS):
                    continue
                full = os.path.normpath(os.path.join(root, fn))
                h = hash_file(full)
                if h:
                    d.setdefault(h, []).append(full)
    return d

def save_snapshot(base_paths, log_callback):
    log_callback("Starting snapshot...")
    snap = get_all_files_with_hashes(base_paths, log_callback)
    
    # Save snapshot with folder info
    snapshot_data = {
        "folders_scanned": base_paths if isinstance(base_paths, list) else [base_paths],
        "timestamp": datetime.now().isoformat(),
        "file_hashes": snap
    }
    
    with open(SAVE_FILE, 'w', encoding='utf-8') as f:
        json.dump(snapshot_data, f, indent=2)
    total = sum(len(v) for v in snap.values())
    log_callback(f"✅ Snapshot saved: {total} files from {len(snapshot_data['folders_scanned'])} folders.")

def load_snapshot(log_callback):
    if not os.path.exists(SAVE_FILE):
        log_callback("❌ No snapshot found. Run `scan` first.")
        return None, []
    
    data = json.load(open(SAVE_FILE, 'r', encoding='utf-8'))
    
    # Handle old format (just file hashes) and new format (with metadata)
    if "file_hashes" in data:
        return data["file_hashes"], data.get("folders_scanned", [])
    else:
        # Old format - assume it's just the file hashes
        return data, []

def backup_file(original_path):
    rel        = os.path.relpath(original_path).replace("\\", "_").replace("/", "_")
    timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak_name   = f"{rel}_{timestamp}.bak"
    bak_folder = BACKUP_DIR
    os.makedirs(bak_folder, exist_ok=True)
    bak_path   = os.path.join(bak_folder, bak_name)
    shutil.copy2(original_path, bak_path)
    return bak_path

def replace_in_file(path, old_p, new_p, log_entries, log_callback):
    try:
        txt = open(path, 'r', encoding='utf-8', errors='ignore').read()
    except Exception as e:
        log_callback(f"Could not read {path}: {e}")
        return

    orig    = txt
    replacements = []
    variants = {
        old_p,
        old_p.replace("\\", "/"),
        old_p.replace("/", "\\"),
        old_p.replace("\\", "\\"),
    }

    for var in variants:
        if var in txt:
            if "\\" in var:
                rp = new_p.replace("\\", "\\")
            elif "/" in var:
                rp = new_p.replace("\\", "/")
            else:
                rp = new_p
            pat = re.escape(var)
            txt = re.sub(pat, lambda m, rp=rp: rp, txt)
            replacements.append(f"    {var} → {rp}")

    if replacements and txt != orig:
        bak = backup_file(path)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(txt)
        log_callback(f"🔁 Updated: {path} (backup: {bak})")
        log_entries.append(path)
        log_entries.extend(replacements)

def update_references(base_paths, log_callback):
    log_callback("Loading old snapshot...")
    old_snap, old_folders = load_snapshot(log_callback)
    if old_snap is None:
        return

    log_callback("Creating new snapshot of current state...")
    new_snap = get_all_files_with_hashes(base_paths, log_callback)

    mappings = []
    for h, old_list in old_snap.items():
        new_list = new_snap.get(h, [])
        removed  = sorted(set(old_list) - set(new_list))
        added    = sorted(set(new_list) - set(old_list))
        for old_path, new_path in zip(removed, added):
            mappings.append((old_path, new_path))

    if not mappings:
        log_callback("📦 No renamed/moved files found.")
        return

    log_callback(f"🔍 Detected {len(mappings)} renamed/moved files. Starting update...")

    # Only scan files in the specified folders
    all_files = []
    scan_paths = base_paths if isinstance(base_paths, list) else [base_paths]
    
    for base_path in scan_paths:
        for root, dirs, files in os.walk(base_path):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for fn in files:
                if SCAN_ALL or fn.endswith(EXTENSIONS):
                    all_files.append(os.path.normpath(os.path.join(root, fn)))

    log_entries = []
    for i, file_path in enumerate(all_files):
        if i % 100 == 0:
            log_callback(f"Updating references... {i}/{len(all_files)} files checked.")
        for old_p, new_p in mappings:
            replace_in_file(file_path, old_p, new_p, log_entries, log_callback)

    if log_entries:
        with open(LOG_FILE, 'a', encoding='utf-8') as L:
            L.write(f"\n--- {datetime.now()} ---\n")
            L.write("\n".join(log_entries) + "\n")
        log_callback(f"📝 Log saved → {LOG_FILE}")
    else:
        log_callback("No references needed updating.")


class PathTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Path Tracker - Multi Folder")
        self.geometry("900x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.selected_folders = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        # --- Top Frame ---
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.top_frame.grid_columnconfigure(1, weight=1)

        self.folder_label = ctk.CTkLabel(self.top_frame, text="Target Folders:")
        self.folder_label.grid(row=0, column=0, padx=10, pady=10)

        self.add_folder_button = ctk.CTkButton(self.top_frame, text="Add Folder", command=self.add_folder)
        self.add_folder_button.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        self.clear_folders_button = ctk.CTkButton(self.top_frame, text="Clear All", command=self.clear_folders)
        self.clear_folders_button.grid(row=0, column=2, padx=10, pady=10)

        # Quick add buttons for your specific folders
        self.quick_frame = ctk.CTkFrame(self.top_frame)
        self.quick_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky="ew")
        
        self.quick_label = ctk.CTkLabel(self.quick_frame, text="Quick Add:")
        self.quick_label.grid(row=0, column=0, padx=10, pady=5)
        
        self.ms1_button = ctk.CTkButton(self.quick_frame, text="Add C:\\ms1", 
                                       command=lambda: self.add_specific_folder("C:\\ms1"))
        self.ms1_button.grid(row=0, column=1, padx=5, pady=5)
        
        self.msbackups_button = ctk.CTkButton(self.quick_frame, text="Add C:\\msBackups", 
                                             command=lambda: self.add_specific_folder("C:\\msBackups"))
        self.msbackups_button.grid(row=0, column=2, padx=5, pady=5)

        # --- Folder List Frame ---
        self.folder_list_frame = ctk.CTkFrame(self)
        self.folder_list_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.folder_list_frame.grid_columnconfigure(0, weight=1)

        self.folder_list_label = ctk.CTkLabel(self.folder_list_frame, text="Selected Folders:")
        self.folder_list_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.folder_listbox = ctk.CTkTextbox(self.folder_list_frame, height=100)
        self.folder_listbox.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.folder_listbox.configure(state="disabled")

        # --- Button Frame ---
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.button_frame.grid_columnconfigure((0, 1), weight=1)

        self.scan_button = ctk.CTkButton(self.button_frame, text="Scan Selected Folders", command=self.start_scan)
        self.scan_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.update_button = ctk.CTkButton(self.button_frame, text="Update References", command=self.start_update)
        self.update_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # --- Output Textbox ---
        self.output_textbox = ctk.CTkTextbox(self, wrap="word")
        self.output_textbox.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")
        self.output_textbox.configure(state="disabled")

        self.log_queue = queue.Queue()
        self.process_log_queue()

    def add_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path and folder_path not in self.selected_folders:
            self.selected_folders.append(folder_path)
            self.update_folder_display()

    def add_specific_folder(self, folder_path):
        if os.path.isdir(folder_path) and folder_path not in self.selected_folders:
            self.selected_folders.append(folder_path)
            self.update_folder_display()
        elif not os.path.isdir(folder_path):
            self.log(f"❌ Folder not found: {folder_path}")

    def clear_folders(self):
        self.selected_folders = []
        self.update_folder_display()

    def update_folder_display(self):
        self.folder_listbox.configure(state="normal")
        self.folder_listbox.delete("1.0", "end")
        for i, folder in enumerate(self.selected_folders, 1):
            self.folder_listbox.insert("end", f"{i}. {folder}\n")
        self.folder_listbox.configure(state="disabled")

    def log(self, message):
        self.log_queue.put(message)

    def process_log_queue(self):
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.output_textbox.configure(state="normal")
                self.output_textbox.insert("end", message + "\n")
                self.output_textbox.see("end")
                self.output_textbox.configure(state="disabled")
        except queue.Empty:
            pass
        self.after(100, self.process_log_queue)

    def set_ui_state(self, state):
        self.scan_button.configure(state=state)
        self.update_button.configure(state=state)
        self.add_folder_button.configure(state=state)
        self.clear_folders_button.configure(state=state)

    def start_task(self, func_to_run):
        if not self.selected_folders:
            self.log("❌ No folders selected. Please add at least one folder.")
            return

        # Validate all folders exist
        invalid_folders = [f for f in self.selected_folders if not os.path.isdir(f)]
        if invalid_folders:
            self.log(f"❌ Invalid folders found: {', '.join(invalid_folders)}")
            return

        self.set_ui_state("disabled")
        self.output_textbox.configure(state="normal")
        self.output_textbox.delete("1.0", "end")
        self.output_textbox.configure(state="disabled")

        thread = threading.Thread(target=self.task_worker, args=(func_to_run, self.selected_folders.copy()))
        thread.daemon = True
        thread.start()

    def task_worker(self, func, folders):
        try:
            func(folders, self.log)
        except Exception as e:
            self.log(f"❌ An unexpected error occurred: {e}")
        finally:
            self.after(0, self.set_ui_state, "normal")

    def start_scan(self):
        self.start_task(save_snapshot)

    def start_update(self):
        self.start_task(update_references)


if __name__ == "__main__":
    app = PathTrackerApp()
    app.mainloop()