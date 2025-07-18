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

class PathTrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Path Tracker - File Reference Updater")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Configuration
        self.config = {
            'SCAN_ALL': True,
            'EXTENSIONS': (".py", ".ahk", ".ps1", ".bat", ".txt"),
            'SKIP_DIRS': {'.git', '__pycache__', '.vscode', 'node_modules'},
            'SAVE_FILE': r"C:\Users\nahid\script_output\paths_before.json",
            'LOG_FILE': r"C:\Users\nahid\script_output\path_replacements.log",
            'BACKUP_DIR': r"C:\msBackups\bak"
        }
        
        self.selected_folder = tk.StringVar()
        self.setup_ui()
        
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
        ttk.Label(main_frame, text="Select Folder:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        folder_frame = ttk.Frame(main_frame)
        folder_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        folder_frame.columnconfigure(0, weight=1)
        
        self.folder_entry = ttk.Entry(folder_frame, textvariable=self.selected_folder, width=50)
        self.folder_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        browse_btn = ttk.Button(folder_frame, text="Browse", command=self.browse_folder)
        browse_btn.grid(row=0, column=1)
        
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
        
        self.scan_btn = ttk.Button(buttons_frame, text="📷 Scan Folder", 
                                  command=self.scan_folder, style='Accent.TButton')
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
        if folder:
            self.selected_folder.set(folder)
            
    def log_message(self, message):
        self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def update_config(self):
        self.config['SCAN_ALL'] = self.scan_all_var.get()
        self.config['EXTENSIONS'] = tuple(ext.strip() for ext in self.extensions_var.get().split(','))
        self.config['SKIP_DIRS'] = {dir.strip() for dir in self.skip_dirs_var.get().split(',')}
        
    def hash_file(self, path):
        h = hashlib.sha256()
        try:
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return None

    def get_all_files_with_hashes(self, base_path):
        d = {}
        file_count = 0
        
        for root, dirs, files in os.walk(base_path):
            dirs[:] = [d for d in dirs if d not in self.config['SKIP_DIRS']]
            for fn in files:
                if not self.config['SCAN_ALL'] and not fn.endswith(self.config['EXTENSIONS']):
                    continue
                full = os.path.normpath(os.path.join(root, fn))
                h = self.hash_file(full)
                if h:
                    d.setdefault(h, []).append(full)
                    file_count += 1
                    
                if file_count % 100 == 0:
                    self.status_var.set(f"Processing... {file_count} files")
                    self.root.update_idletasks()
        
        return d

    def scan_folder(self):
        folder = self.selected_folder.get()
        if not folder:
            messagebox.showerror("Error", "Please select a folder first.")
            return
            
        if not os.path.isdir(folder):
            messagebox.showerror("Error", "Selected folder does not exist.")
            return
            
        self.update_config()
        
        def scan_thread():
            try:
                self.scan_btn.config(state='disabled')
                self.update_btn.config(state='disabled')
                self.status_var.set("Scanning...")
                self.log_message(f"Starting scan of: {folder}")
                
                # Create output directory if it doesn't exist
                os.makedirs(os.path.dirname(self.config['SAVE_FILE']), exist_ok=True)
                
                snap = self.get_all_files_with_hashes(folder)
                
                with open(self.config['SAVE_FILE'], 'w', encoding='utf-8') as f:
                    json.dump(snap, f, indent=2)
                
                total = sum(len(v) for v in snap.values())
                self.log_message(f"✅ Snapshot saved: {total} files logged to {self.config['SAVE_FILE']}")
                self.status_var.set("Scan completed")
                
            except Exception as e:
                self.log_message(f"❌ Error during scan: {str(e)}")
                self.status_var.set("Scan failed")
            finally:
                self.scan_btn.config(state='normal')
                self.update_btn.config(state='normal')
                
        threading.Thread(target=scan_thread, daemon=True).start()

    def backup_file(self, original_path):
        rel = os.path.relpath(original_path).replace("\\", "_").replace("/", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        bak_name = f"{rel}_{timestamp}.bak"
        bak_folder = self.config['BACKUP_DIR']
        os.makedirs(bak_folder, exist_ok=True)
        bak_path = os.path.join(bak_folder, bak_name)
        shutil.copy2(original_path, bak_path)
        return bak_path

    def replace_in_file(self, path, old_p, new_p, log):
        try:
            txt = open(path, 'r', encoding='utf-8', errors='ignore').read()
        except:
            return

        orig = txt
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
            bak = self.backup_file(path)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(txt)
            self.log_message(f"🔁 Updated: {path}")
            self.log_message(f"    Backup: {bak}")
            log.append(path)
            log.extend(entries)

    def update_references(self):
        folder = self.selected_folder.get()
        if not folder:
            messagebox.showerror("Error", "Please select a folder first.")
            return
            
        if not os.path.isdir(folder):
            messagebox.showerror("Error", "Selected folder does not exist.")
            return
            
        if not os.path.exists(self.config['SAVE_FILE']):
            messagebox.showerror("Error", "No snapshot found. Please run scan first.")
            return
            
        self.update_config()
        
        def update_thread():
            try:
                self.scan_btn.config(state='disabled')
                self.update_btn.config(state='disabled')
                self.status_var.set("Updating references...")
                self.log_message(f"Starting reference update for: {folder}")
                
                # Load old snapshot
                with open(self.config['SAVE_FILE'], 'r', encoding='utf-8') as f:
                    old_snap = json.load(f)
                
                # Get current snapshot
                new_snap = self.get_all_files_with_hashes(folder)
                
                # Find mappings
                mappings = []
                for h, old_list in old_snap.items():
                    new_list = new_snap.get(h, [])
                    removed = sorted(set(old_list) - set(new_list))
                    added = sorted(set(new_list) - set(old_list))
                    # pair one-to-one by sorted order
                    for old_path, new_path in zip(removed, added):
                        mappings.append((old_path, new_path))
                
                if not mappings:
                    self.log_message("📦 No renamed/moved files found.")
                    self.status_var.set("No changes detected")
                    return
                
                self.log_message(f"🔍 Detected {len(mappings)} renamed/moved files:")
                for old_path, new_path in mappings:
                    self.log_message(f"    {old_path} → {new_path}")
                
                # Gather all files to scan
                all_files = []
                for root, dirs, files in os.walk(folder):
                    dirs[:] = [d for d in dirs if d not in self.config['SKIP_DIRS']]
                    for fn in files:
                        if self.config['SCAN_ALL'] or fn.endswith(self.config['EXTENSIONS']):
                            all_files.append(os.path.normpath(os.path.join(root, fn)))
                
                self.log_message(f"📝 Scanning {len(all_files)} files for references...")
                
                # Create backup directory
                os.makedirs(self.config['BACKUP_DIR'], exist_ok=True)
                
                log_entries = []
                processed = 0
                
                for file_path in all_files:
                    for old_p, new_p in mappings:
                        self.replace_in_file(file_path, old_p, new_p, log_entries)
                    
                    processed += 1
                    if processed % 50 == 0:
                        self.status_var.set(f"Processing... {processed}/{len(all_files)} files")
                        self.root.update_idletasks()
                
                if log_entries:
                    with open(self.config['LOG_FILE'], 'a', encoding='utf-8') as L:
                        L.write(f"\n--- {datetime.now()} ---\n")
                        L.write("\n".join(log_entries) + "\n")
                    self.log_message(f"📝 Detailed log saved to: {self.config['LOG_FILE']}")
                
                self.log_message("✅ Reference update completed!")
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