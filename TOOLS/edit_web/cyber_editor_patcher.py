import os
import re
import sys
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path

# Theme Configuration
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class CyberPatcherApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CYBER PATCHER v3.5 - MULTI-BLOCK EDITION")
        self.geometry("1150x900")

        # State
        self.project_path = ctk.StringVar(value=os.getcwd())
        
        # UI Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="CYBER\nPATCHER v3.5", font=ctk.CTkFont(size=26, weight="bold", family="JetBrains Mono"))
        self.logo_label.pack(pady=30)

        # Project Path
        self.path_label = ctk.CTkLabel(self.sidebar, text="PROJECT ROOT:", anchor="w", font=ctk.CTkFont(size=11, weight="bold"))
        self.path_label.pack(fill="x", padx=20)
        
        self.path_entry = ctk.CTkEntry(self.sidebar, textvariable=self.project_path)
        self.path_entry.pack(fill="x", padx=20, pady=5)
        
        self.browse_btn = ctk.CTkButton(self.sidebar, text="BROWSE PATH", command=self.browse_project, fg_color="#00adb5")
        self.browse_btn.pack(fill="x", padx=20, pady=10)

        self.divider = ctk.CTkFrame(self.sidebar, height=2, fg_color="gray30")
        self.divider.pack(fill="x", padx=5, pady=25)

        # Actions
        self.help_btn = ctk.CTkButton(self.sidebar, text="GENERATE PROMPT", command=self.generate_prompt_combined, fg_color="transparent", border_width=1)
        self.help_btn.pack(fill="x", padx=20, pady=5)

        self.clean_btn = ctk.CTkButton(self.sidebar, text="🧹 CLEAN PASTE", command=self.clean_editor, fg_color="gray40")
        self.clean_btn.pack(fill="x", padx=20, pady=20)

        self.apply_btn = ctk.CTkButton(self.sidebar, text="🚀 APPLY CHANGES", command=self.apply_changes, fg_color="#ff2e63", font=ctk.CTkFont(size=16, weight="bold"), height=50)
        self.apply_btn.pack(side="bottom", fill="x", padx=20, pady=30)

        # Main Content
        self.main_container = ctk.CTkFrame(self, corner_radius=10)
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        self.label_instr = ctk.CTkLabel(self.main_container, text="INPUT BUFFER (Paste AI response here)", font=ctk.CTkFont(size=14, weight="bold"))
        self.label_instr.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="w")

        self.text_editor = ctk.CTkTextbox(self.main_container, font=ctk.CTkFont(family="Consolas", size=13))
        self.text_editor.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

        self.status_bar = ctk.CTkLabel(self, text="System Ready", anchor="w", font=ctk.CTkFont(size=12))
        self.status_bar.grid(row=1, column=0, columnspan=2, padx=20, pady=5, sticky="we")

    def browse_project(self):
        path = filedialog.askdirectory()
        if path: self.project_path.set(path)

    def update_status(self, msg, color="white"):
        self.status_bar.configure(text=msg, text_color=color)

    def clean_editor(self):
        content = self.text_editor.get("1.0", "end")
        content = re.sub(r"```[a-zA-Z]*\n", "", content)
        content = content.replace("```", "")
        self.text_editor.delete("1.0", "end")
        self.text_editor.insert("1.0", content.strip())
        self.update_status("Cleaned formatting.")

    def generate_prompt_combined(self):
        root = self.project_path.get()
        prompt = f"""# Protocol: Multi-Block Patcher
Project Root: {root}

Use one FILE: header followed by multiple SEARCH/REPLACE blocks for each file.

Format:
FILE: relative/path/to/file.py
<<<<<<< SEARCH
(block 1 old)
=======
(block 1 new)
>>>>>>> REPLACE
<<<<<<< SEARCH
(block 2 old)
=======
(block 2 new)
>>>>>>> REPLACE
"""
        self.text_editor.delete("1.0", "end")
        self.text_editor.insert("1.0", prompt)

    def normalize_text(self, text):
        return "\n".join([line.rstrip() for line in text.splitlines()])

    def apply_changes(self):
        content = self.text_editor.get("1.0", "end")
        root_path = Path(self.project_path.get())
        
        if not root_path.exists():
            messagebox.showerror("Error", "Invalid Project Root!")
            return

        # Split content by FILE: header OR --- FILE: header
        file_segments = re.split(r"(?:FILE:|--- FILE:)\s*([^\n-]+)(?:---|)\n", content)
        
        if len(file_segments) < 2:
            messagebox.showwarning("No Blocks", "No FILE: headers found.")
            return

        success_count = 0
        fail_count = 0
        log = []

        # re.split with a group returns [pre-match, group1, match-content, ...]
        for i in range(1, len(file_segments), 2):
            rel_path = file_segments[i].strip().strip("`\"' ")
            blocks_text = file_segments[i+1]
            
            full_path = root_path / rel_path
            
            # Extract blocks from this file's segment
            p1 = re.compile(r"<<<<<<< SEARCH\n(.*?)\n=======\n(.*?)\n>>>>>>> REPLACE", re.DOTALL)
            p2 = re.compile(r"DELETE:\n(.*?)\nADD:\n(.*?)\n--- END FILE ---", re.DOTALL)
            
            matches = list(p1.finditer(blocks_text)) + list(p2.finditer(blocks_text))
            
            if not matches:
                continue

            # Load file content
            file_text_raw = ""
            file_text_norm = ""
            line_ending = "\n"
            
            exists = full_path.exists()
            if exists:
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        file_text_raw = f.read()
                        file_text_norm = self.normalize_text(file_text_raw)
                        line_ending = "\r\n" if "\r\n" in file_text_raw else "\n"
                except Exception as e:
                    log.append(f"CRITICAL: Could not read {rel_path} - {e}")
                    fail_count += 1
                    continue
            
            current_file_modified = False
            
            for m in matches:
                search_str = self.normalize_text(m.group(1))
                replace_str = self.normalize_text(m.group(2))
                
                # New file creation
                if not search_str.strip() and not exists:
                    try:
                        full_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(full_path, "w", encoding="utf-8") as f:
                            f.write(replace_str)
                        success_count += 1
                        log.append(f"CREATED: {rel_path}")
                        exists = True # Flag as exists now
                        file_text_norm = replace_str # Update buffer
                        current_file_modified = True
                        continue
                    except Exception as e:
                        fail_count += 1
                        log.append(f"ERROR: {rel_path} - {e}")
                        continue

                # Patch existing
                if search_str in file_text_norm:
                    file_text_norm = file_text_norm.replace(search_str, replace_str, 1)
                    success_count += 1
                    current_file_modified = True
                    log.append(f"PATCHED: {rel_path} (Block Match)")
                else:
                    fail_count += 1
                    log.append(f"MISMATCH: {rel_path} - A block could not be matched.")

            if current_file_modified:
                try:
                    with open(full_path, "w", encoding="utf-8", newline=line_ending) as f:
                        f.write(file_text_norm)
                except Exception as e:
                    log.append(f"WRITE ERROR: {rel_path} - {e}")

        summary = f"Process Finished\n✅ Success: {success_count}\n❌ Failed: {fail_count}\n\n" + "\n".join(log)
        messagebox.showinfo("Result", summary)
        self.update_status(f"Done: {success_count} success, {fail_count} failures", "#00ff00" if fail_count == 0 else "#ff4444")

if __name__ == "__main__":
    app = CyberPatcherApp()
    app.mainloop()
