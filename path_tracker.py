import os
import json
import re
import sys
import hashlib
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from datetime import datetime
import threading
import queue

# ————— CONFIG —————
SCAN_ALL    = True
EXTENSIONS  = (".py", ".ahk", ".ps1", ".bat", ".txt")
SKIP_DIRS   = {'.git', '__pycache__', '.vscode', 'node_modules'}
SAVE_FILE   = r"C:\Users\nahid\script_output\paths_before.json"
LOG_FILE    = r"C:\Users\nahid\script_output\path_replacements.log"
BACKUP_DIR  = r"C:\Users\nahid\ms\msBackups\bak"
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
    """Modified to show progress for each folder on one line"""
    d = {}
    total_file_count = 0
    
    # Handle single path or list of paths
    if isinstance(base_paths, str):
        base_paths = [base_paths]
    
    for i, base_path in enumerate(base_paths, 1):
        folder_file_count = 0
        log_callback(f"[{i}/{len(base_paths)}] Scanning: {base_path}")
        
        for root, dirs, files in os.walk(base_path):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for fn in files:
                folder_file_count += 1
                total_file_count += 1
                
                if not SCAN_ALL and not fn.endswith(EXTENSIONS):
                    continue
                full = os.path.normpath(os.path.join(root, fn))
                h = hash_file(full)
                if h:
                    d.setdefault(h, []).append(full)
        
        # Show completion for this folder in one line
        log_callback(f"[{i}/{len(base_paths)}] ✅ {os.path.basename(base_path)}: {folder_file_count} files")
    
    return d

def save_snapshot(base_paths, log_callback):
    log_callback("Starting snapshot creation...")
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
    log_callback(f"✅ Snapshot saved: {total} files logged")

def load_snapshot(log_callback):
    if not os.path.exists(SAVE_FILE):
        log_callback("❌ No snapshot found. Please run scan first.")
        return None, []
    
    data = json.load(open(SAVE_FILE, 'r', encoding='utf-8'))
    
    if "file_hashes" in data:
        return data["file_hashes"], data.get("folders_scanned", [])
    else:
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
        return

    orig    = txt
    replacements = []
    variants = {
        old_p,
        old_p.replace("\\", "/"),
        old_p.replace("/", "\\"),
        old_p.replace("\\", "\\\\"),
    }

    for var in variants:
        if var in txt:
            if "\\\\" in var:
                rp = new_p.replace("\\", "\\\\")
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
        log_callback(f"🔁 Updated: {path}")
        log_callback(f"    Backup: {bak}")
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

    log_callback(f"🔍 Detected {len(mappings)} renamed/moved files:")
    for old_path, new_path in mappings:
        log_callback(f"    {old_path} → {new_path}")

    all_files = []
    scan_paths = base_paths if isinstance(base_paths, list) else [base_paths]
    
    for base_path in scan_paths:
        for root, dirs, files in os.walk(base_path):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for fn in files:
                if SCAN_ALL or fn.endswith(EXTENSIONS):
                    all_files.append(os.path.normpath(os.path.join(root, fn)))

    log_callback(f"📝 Scanning {len(all_files)} files for references...")
    
    # Create backup directory
    os.makedirs(BACKUP_DIR, exist_ok=True)

    log_entries = []

    for file_path in all_files:
        for old_p, new_p in mappings:
            replace_in_file(file_path, old_p, new_p, log_entries, log_callback)

    if log_entries:
        log_callback(f"Processing... {len(all_files)}/{len(all_files)} files")
        with open(LOG_FILE, 'a', encoding='utf-8') as L:
            L.write(f"\n--- {datetime.now()} ---\n")
            L.write("\n".join(log_entries) + "\n")
        log_callback(f"📝 Detailed log saved to: {LOG_FILE}")

    log_callback("✅ Reference update completed!")


class PathTrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Path Tracker - File Reference Updater")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Configuration
        self.config = {
            'SCAN_ALL': SCAN_ALL,
            'EXTENSIONS': EXTENSIONS,
            'SKIP_DIRS': SKIP_DIRS,
            'SAVE_FILE': SAVE_FILE,
            'LOG_FILE': LOG_FILE,
            'BACKUP_DIR': BACKUP_DIR
        }
        
        self.selected_folders = []
        self.setup_ui()
        
        self.log_queue = queue.Queue()
        self.process_log_queue()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Path Tracker", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Folder selection
        ttk.Label(main_frame, text="Select Folders:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        folder_frame = ttk.Frame(main_frame)
        folder_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        folder_frame.columnconfigure(1, weight=1)
        
        # Quick select dropdown
        self.quick_folders = ["C:/Users/nahid/ms/ms1/", "C:/Users/nahid/ms/msBackups/"]
        self.quick_select = ttk.Combobox(folder_frame, values=self.quick_folders, width=30, state="readonly")
        self.quick_select.grid(row=0, column=0, padx=(0, 5))
        self.quick_select.bind('<<ComboboxSelected>>', self.on_quick_select)
        
        # Selected folders display
        self.folder_listbox = scrolledtext.ScrolledText(folder_frame, width=50, height=3, 
                                                       wrap=tk.WORD, font=('Arial', 9))
        self.folder_listbox.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Buttons
        browse_btn = ttk.Button(folder_frame, text="Browse", command=self.browse_folder)
        browse_btn.grid(row=0, column=2, padx=(0, 5))
        
        clear_btn = ttk.Button(folder_frame, text="Clear All", command=self.clear_folders)
        clear_btn.grid(row=0, column=3)
        
        self.update_folder_display()
        
        # Configuration frame
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        config_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        config_frame.columnconfigure(1, weight=1)
        
        # Scan all files checkbox
        self.scan_all_var = tk.BooleanVar(value=self.config['SCAN_ALL'])
        scan_all_cb = ttk.Checkbutton(config_frame, text="Scan all files", 
                                     variable=self.scan_all_var)
        scan_all_cb.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        # Extensions
        ttk.Label(config_frame, text="Extensions:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.extensions_var = tk.StringVar(value=", ".join(self.config['EXTENSIONS']))
        extensions_entry = ttk.Entry(config_frame, textvariable=self.extensions_var, width=40)
        extensions_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        # Skip directories
        ttk.Label(config_frame, text="Skip Dirs:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.skip_dirs_var = tk.StringVar(value=", ".join(self.config['SKIP_DIRS']))
        skip_dirs_entry = ttk.Entry(config_frame, textvariable=self.skip_dirs_var, width=40)
        skip_dirs_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, columnspan=3, pady=20)
        
        self.scan_btn = ttk.Button(buttons_frame, text="📷 Scan Folders", 
                                  command=self.scan_folders, style='Accent.TButton')
        self.scan_btn.pack(side=tk.LEFT, padx=5)
        
        self.update_btn = ttk.Button(buttons_frame, text="🔄 Update References", 
                                    command=self.update_references)
        self.update_btn.pack(side=tk.LEFT, padx=5)
        
        # Status and log display
        log_frame = ttk.LabelFrame(main_frame, text="Output Log", padding="5")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, width=80, height=20, 
                                                 wrap=tk.WORD, font=('Consolas', 9))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))
        
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder and folder not in self.selected_folders:
            self.selected_folders.append(folder)
            self.update_folder_display()
            self.log_message(f"📁 Added: {folder}")
            
    def on_quick_select(self, event):
        selected = event.widget.get()
        if selected and selected not in self.selected_folders:
            self.selected_folders.append(selected)
            self.update_folder_display()
            self.log_message(f"📁 Quick selected: {selected}")
        
    def clear_folders(self):
        if self.selected_folders:
            self.selected_folders = []
            self.update_folder_display()
            self.log_message("🗑️ Cleared all folders")
    
    def update_folder_display(self):
        self.folder_listbox.delete('1.0', tk.END)
        if not self.selected_folders:
            # self.folder_listbox.insert('1.0', "No folders selected. Use dropdown or Browse button to add folders.")
            self.folder_listbox.insert('1.0', "")
        else:
            for i, folder in enumerate(self.selected_folders, 1):
                self.folder_listbox.insert(tk.END, f"{i}. {folder}\n")
        
    def log_message(self, message):
        self.log_queue.put(message)
        
    def process_log_queue(self):
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
                self.log_text.see(tk.END)
                self.root.update_idletasks()
        except queue.Empty:
            pass
        self.root.after(100, self.process_log_queue)
        
    def update_config(self):
        global SCAN_ALL, EXTENSIONS, SKIP_DIRS
        SCAN_ALL = self.scan_all_var.get()
        EXTENSIONS = tuple(ext.strip() for ext in self.extensions_var.get().split(','))
        SKIP_DIRS = {dir.strip() for dir in self.skip_dirs_var.get().split(',')}
        
    def scan_folders(self):
        if not self.selected_folders:
            messagebox.showerror("Error", "Please select at least one folder first.")
            return
            
        # Validate folders exist
        invalid_folders = [f for f in self.selected_folders if not os.path.isdir(f)]
        if invalid_folders:
            messagebox.showerror("Error", f"These folders do not exist:\n" + "\n".join(invalid_folders))
            return
            
        self.update_config()
        
        def scan_thread():
            try:
                self.scan_btn.config(state='disabled')
                self.update_btn.config(state='disabled')
                self.status_var.set("Scanning...")
                self.log_message(f"Starting scan of {len(self.selected_folders)} folders")
                
                # Create output directory if it doesn't exist
                os.makedirs(os.path.dirname(SAVE_FILE), exist_ok=True)
                
                save_snapshot(self.selected_folders, self.log_message)
                self.status_var.set("Scan completed")
                
            except Exception as e:
                self.log_message(f"❌ Error during scan: {str(e)}")
                self.status_var.set("Scan failed")
            finally:
                self.scan_btn.config(state='normal')
                self.update_btn.config(state='normal')
                
        threading.Thread(target=scan_thread, daemon=True).start()

    def update_references(self):
        if not self.selected_folders:
            messagebox.showerror("Error", "Please select at least one folder first.")
            return
            
        if not os.path.exists(SAVE_FILE):
            messagebox.showerror("Error", "No snapshot found. Please run scan first.")
            return
            
        self.update_config()
        
        def update_thread():
            try:
                self.scan_btn.config(state='disabled')
                self.update_btn.config(state='disabled')
                self.status_var.set("Updating references...")
                self.log_message(f"Starting reference update for {len(self.selected_folders)} folders")
                
                update_references(self.selected_folders, self.log_message)
                self.status_var.set("Update completed")
                
            except Exception as e:
                self.log_message(f"❌ Error during update: {str(e)}")
                self.status_var.set("Update failed")
            finally:
                self.scan_btn.config(state='normal')
                self.update_btn.config(state='normal')
                
        threading.Thread(target=update_thread, daemon=True).start()


def main():
    root = tk.Tk()
    app = PathTrackerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()