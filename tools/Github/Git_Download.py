#!/usr/bin/env python3
"""
GitHub Folder Downloader GUI - Compact Version
Downloads a specific folder from a specific commit using sparse checkout
Built with CustomTkinter for modern UI
"""

import os
import re
import sys
import shutil
import subprocess
import threading
import tkinter as tk
from pathlib import Path
from urllib.parse import urlparse
from tkinter import filedialog, messagebox

try:
    import customtkinter as ctk
except ImportError:
    print("❌ Error: CustomTkinter is required")
    print("📦 Install it with: pip install customtkinter")
    sys.exit(1)

class GitHubFolderDownloaderGUI:
    def __init__(self):
        # Configure appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create compact main window
        self.root = ctk.CTk()
        self.root.title("GitHub Folder Downloader")
        self.root.geometry("700x500")  # Smaller default size
        self.root.resizable(True, True)
        
        # Variables
        self.temp_dirs = []
        # Set default path to user's home directory instead of current working directory
        default_path = os.path.expanduser("~")  # This gives C:\Users\nahid\ on Windows
        self.download_path = tk.StringVar(value=default_path)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the compact user interface"""
        # Main container with less padding
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Compact title
        title_label = ctk.CTkLabel(
            main_frame, 
            text="🐙 GitHub Folder Downloader",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(10, 5))
        
        # BIG DOWNLOAD BUTTON AT THE TOP
        self.download_btn = ctk.CTkButton(
            main_frame,
            text="⬇️ DOWNLOAD FOLDER",
            command=self.start_download,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            width=280,
            fg_color="#1f538d",
            hover_color="#14375e"
        )
        self.download_btn.pack(pady=10)
        
        # Compact URL Input
        url_frame = ctk.CTkFrame(main_frame)
        url_frame.pack(fill="x", padx=10, pady=5)
        
        url_label = ctk.CTkLabel(url_frame, text="🔗 GitHub URL:", font=ctk.CTkFont(size=12, weight="bold"))
        url_label.pack(anchor="w", padx=10, pady=(8, 2))
        
        url_input_frame = ctk.CTkFrame(url_frame, fg_color="transparent")
        url_input_frame.pack(fill="x", padx=10, pady=(0, 8))
        
        self.url_entry = ctk.CTkEntry(
            url_input_frame,
            placeholder_text="https://github.com/user/repo/tree/commit-hash/folder/path",
            font=ctk.CTkFont(size=10),
            height=30
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        example_btn = ctk.CTkButton(
            url_input_frame,
            text="📋 Example",
            command=self.load_example,
            width=80,
            height=30,
            font=ctk.CTkFont(size=10)
        )
        example_btn.pack(side="right")
        
        # Compact Download Path
        path_frame = ctk.CTkFrame(main_frame)
        path_frame.pack(fill="x", padx=10, pady=5)
        
        path_label = ctk.CTkLabel(path_frame, text="📁 Download to:", font=ctk.CTkFont(size=12, weight="bold"))
        path_label.pack(anchor="w", padx=10, pady=(8, 2))
        
        path_input_frame = ctk.CTkFrame(path_frame, fg_color="transparent")
        path_input_frame.pack(fill="x", padx=10, pady=(0, 8))
        
        self.path_entry = ctk.CTkEntry(
            path_input_frame,
            textvariable=self.download_path,
            font=ctk.CTkFont(size=10),
            height=30
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        browse_btn = ctk.CTkButton(
            path_input_frame,
            text="📂",
            command=self.browse_folder,
            width=40,
            height=30
        )
        browse_btn.pack(side="right")
        
        # Compact Progress Section
        progress_frame = ctk.CTkFrame(main_frame)
        progress_frame.pack(fill="x", padx=10, pady=5)
        
        self.progress_label = ctk.CTkLabel(
            progress_frame,
            text="Ready to download",
            font=ctk.CTkFont(size=11)
        )
        self.progress_label.pack(pady=(8, 3))
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame, height=15)
        self.progress_bar.pack(fill="x", padx=10, pady=(0, 8))
        self.progress_bar.set(0)
        
        # Compact Info Display
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill="x", padx=10, pady=5)
        
        info_label = ctk.CTkLabel(info_frame, text="📊 URL Info:", font=ctk.CTkFont(size=12, weight="bold"))
        info_label.pack(anchor="w", padx=10, pady=(8, 2))
        
        self.info_text = ctk.CTkTextbox(
            info_frame,
            height=60,
            font=ctk.CTkFont(size=9),
            wrap="word"
        )
        self.info_text.pack(fill="x", padx=10, pady=(0, 8))
        
        # Bind URL entry to update info
        self.url_entry.bind("<KeyRelease>", self.update_info)
        
        # Compact Log Section
        log_frame = ctk.CTkFrame(main_frame)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        log_header = ctk.CTkFrame(log_frame, fg_color="transparent")
        log_header.pack(fill="x", padx=10, pady=(8, 2))
        
        log_label = ctk.CTkLabel(log_header, text="📝 Log:", font=ctk.CTkFont(size=12, weight="bold"))
        log_label.pack(side="left")
        
        clear_btn = ctk.CTkButton(
            log_header,
            text="🧹 Clear",
            command=self.clear_log,
            height=25,
            width=60,
            font=ctk.CTkFont(size=9),
            fg_color="gray40",
            hover_color="gray30"
        )
        clear_btn.pack(side="right")
        
        self.log_text = ctk.CTkTextbox(
            log_frame,
            font=ctk.CTkFont(size=9, family="Courier"),
            wrap="word"
        )
        self.log_text.pack(fill="both", expand=True, padx=10, pady=(0, 8))
        
        # Bottom control buttons
        bottom_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        bottom_frame.pack(fill="x", pady=(0, 5))
        
        self.stop_btn = ctk.CTkButton(
            bottom_frame,
            text="⏹️ Stop Download",
            command=self.stop_download,
            height=30,
            width=120,
            font=ctk.CTkFont(size=10),
            fg_color="red",
            hover_color="darkred",
            state="disabled"
        )
        self.stop_btn.pack()
        
    def load_example(self):
        """Load example URL"""
        example_url = "https://github.com/nahid6970/test/tree/640671009edfee1dd07c7412c6e125a5cafaed99/FolderSync"
        self.url_entry.delete(0, "end")
        self.url_entry.insert(0, example_url)
        self.update_info()
        
    def browse_folder(self):
        """Browse for download folder"""
        folder = filedialog.askdirectory(
            title="Select Download Location",
            initialdir=self.download_path.get()
        )
        if folder:
            self.download_path.set(folder)
            
    def update_info(self, event=None):
        """Update parsed information display"""
        url = self.url_entry.get().strip()
        
        if not url:
            self.info_text.delete("1.0", "end")
            return
        
        parsed = self.parse_github_url(url)
        
        if parsed:
            info_text = f"✅ {parsed['user']}/{parsed['repo']} → {parsed['folder_path']} @ {parsed['commit_hash'][:8]}..."
        else:
            info_text = "❌ Invalid URL format. Expected: github.com/user/repo/tree/commit/folder"
        
        self.info_text.delete("1.0", "end")
        self.info_text.insert("1.0", info_text)
        
    def parse_github_url(self, url):
        """Parse GitHub URL and extract components"""
        pattern = r'^https://github\.com/([^/]+)/([^/]+)/tree/([^/]+)/(.+)$'
        match = re.match(pattern, url)
        
        if not match:
            return None
        
        return {
            'user': match.group(1),
            'repo': match.group(2),
            'commit_hash': match.group(3),
            'folder_path': match.group(4),
            'repo_url': f"https://github.com/{match.group(1)}/{match.group(2)}.git"
        }
    
    def log_message(self, message, level="INFO"):
        """Add message to log"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Add color coding based on level
        if level == "ERROR":
            prefix = "❌"
        elif level == "SUCCESS":
            prefix = "✅"
        elif level == "WARNING":
            prefix = "⚠️"
        else:
            prefix = "ℹ️"
        
        log_entry = f"[{timestamp}] {prefix} {message}\n"
        
        self.log_text.insert("end", log_entry)
        self.log_text.see("end")
        self.root.update_idletasks()
        
    def clear_log(self):
        """Clear the activity log"""
        self.log_text.delete("1.0", "end")
        
    def run_command(self, command, cwd=None):
        """Run a shell command and return success status"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                capture_output=True,
                text=True,
                cwd=cwd
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr
    
    def start_download(self):
        """Start download in a separate thread"""
        # Disable download button and enable stop button
        self.download_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        
        # Reset progress
        self.progress_bar.set(0)
        self.progress_label.configure(text="Starting download...")
        
        # Start download thread
        self.download_thread = threading.Thread(target=self.download_folder, daemon=True)
        self.download_thread.start()
        
    def stop_download(self):
        """Stop the current download"""
        self.log_message("Download stopped by user", "WARNING")
        self.cleanup()
        self.reset_ui()
        
    def reset_ui(self):
        """Reset UI to initial state"""
        self.download_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.progress_bar.set(0)
        self.progress_label.configure(text="Ready to download")
        
    def download_folder(self):
        """Main download function (runs in separate thread)"""
        try:
            url = self.url_entry.get().strip()
            download_location = self.download_path.get()
            
            if not url:
                self.log_message("Please enter a GitHub URL", "ERROR")
                self.reset_ui()
                return
            
            # Parse URL
            self.log_message("Parsing URL...")
            self.progress_bar.set(0.1)
            
            parsed = self.parse_github_url(url)
            if not parsed:
                self.log_message("Invalid GitHub URL format", "ERROR")
                self.reset_ui()
                return
            
            user = parsed['user']
            repo = parsed['repo']
            commit_hash = parsed['commit_hash']
            folder_path = parsed['folder_path']
            repo_url = parsed['repo_url']
            
            self.log_message(f"Parsed: {user}/{repo} → {folder_path}")
            
            # Create temp directory
            temp_dir = os.path.join(download_location, f"{repo}_{commit_hash[:8]}_temp")
            self.temp_dirs.append(temp_dir)
            
            # Remove existing temp directory
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            
            # Clone repository
            self.log_message("Cloning with sparse checkout...")
            self.progress_bar.set(0.2)
            
            success, output = self.run_command(
                f"git clone --filter=blob:none --sparse {repo_url} {temp_dir}"
            )
            
            if not success:
                self.log_message(f"Clone failed: {output}", "ERROR")
                self.reset_ui()
                return
            
            # Checkout commit
            self.log_message(f"Checking out commit...")
            self.progress_bar.set(0.4)
            
            success, output = self.run_command(
                f"git checkout {commit_hash}",
                cwd=temp_dir
            )
            
            if not success:
                self.log_message(f"Checkout failed: {output}", "ERROR")
                self.reset_ui()
                return
            
            # Set sparse checkout
            self.log_message(f"Setting sparse checkout...")
            self.progress_bar.set(0.6)
            
            success, output = self.run_command(
                f"git sparse-checkout set {folder_path}",
                cwd=temp_dir
            )
            
            if not success:
                self.log_message(f"Sparse checkout failed: {output}", "ERROR")
                self.reset_ui()
                return
            
            # Check if folder exists
            folder_full_path = os.path.join(temp_dir, folder_path)
            if not os.path.exists(folder_full_path):
                self.log_message(f"Folder '{folder_path}' not found", "ERROR")
                self.reset_ui()
                return
            
            # Copy folder
            self.log_message("Copying folder...")
            self.progress_bar.set(0.8)
            
            folder_name = os.path.basename(folder_path)
            final_dir = os.path.join(download_location, f"{folder_name}_{commit_hash[:8]}")
            
            if os.path.exists(final_dir):
                shutil.rmtree(final_dir)
            
            shutil.copytree(folder_full_path, final_dir)
            
            # Count files
            file_count = sum(len(files) for _, _, files in os.walk(final_dir))
            
            self.progress_bar.set(1.0)
            self.log_message(f"✅ SUCCESS! Downloaded {file_count} files", "SUCCESS")
            self.log_message(f"Location: {final_dir}", "SUCCESS")
            
            # Show success message
            messagebox.showinfo(
                "Download Complete", 
                f"Folder downloaded!\n\n📁 {final_dir}\n📄 {file_count} files"
            )
            
        except Exception as e:
            self.log_message(f"Error: {str(e)}", "ERROR")
        
        finally:
            self.cleanup()
            self.reset_ui()
    
    def cleanup(self):
        """Clean up temporary directories"""
        for temp_dir in self.temp_dirs:
            if os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    self.log_message(f"Cleanup warning: {e}", "WARNING")
        self.temp_dirs.clear()
    
    def run(self):
        """Start the GUI application"""
        # Add initial log message
        self.log_message("Ready! Enter GitHub URL and click Download")
        
        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start the main loop
        self.root.mainloop()
    
    def on_closing(self):
        """Handle application closing"""
        self.cleanup()
        self.root.quit()
        self.root.destroy()

def main():
    """Main function"""
    app = GitHubFolderDownloaderGUI()
    app.run()

if __name__ == "__main__":
    main()