import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import threading
import os
import re

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("green")

class YouTubeSubtitleDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("YouTube Subtitle Downloader")
        self.geometry("600x600")

        # Configure grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)

        # --- URL Section ---
        self.url_label = ctk.CTkLabel(self, text="Video URL:")
        self.url_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        
        self.url_entry = ctk.CTkEntry(self, width=400, placeholder_text="Paste YouTube link here")
        self.url_entry.grid(row=0, column=1, padx=20, pady=(20, 5), sticky="ew")

        # --- Subtitles Options Section ---
        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=20, sticky="ew")
        self.options_frame.grid_columnconfigure(1, weight=1)

        self.lang_label = ctk.CTkLabel(self.options_frame, text="Language:", font=("Roboto", 14, "bold"))
        self.lang_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")

        self.lang_combo = ctk.CTkComboBox(self.options_frame, values=["English", "Bengali", "All Available"])
        self.lang_combo.grid(row=0, column=1, padx=15, pady=15, sticky="ew")
        self.lang_combo.set("English")

        self.auto_subs_checkbox = ctk.CTkCheckBox(self.options_frame, text="Include Auto-generated Subs")
        self.auto_subs_checkbox.grid(row=1, column=0, columnspan=2, padx=15, pady=(0, 15), sticky="w")
        
        self.convert_checkbox = ctk.CTkCheckBox(self.options_frame, text="Convert to SRT (Best compatibility)")
        self.convert_checkbox.grid(row=2, column=0, columnspan=2, padx=15, pady=(0, 15), sticky="w")
        self.convert_checkbox.select()

        self.raw_text_checkbox = ctk.CTkCheckBox(self.options_frame, text="Save as Raw Text (No Timestamps)")
        self.raw_text_checkbox.grid(row=3, column=0, columnspan=2, padx=15, pady=(0, 15), sticky="w")

        # --- Cookies / Auth Section ---
        self.cookies_frame = ctk.CTkFrame(self)
        self.cookies_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        self.cookies_frame.grid_columnconfigure(1, weight=1)

        self.cookies_label = ctk.CTkLabel(self.cookies_frame, text="Authentication (Age-Restricted):", font=("Roboto", 12, "bold"))
        self.cookies_label.grid(row=0, column=0, columnspan=3, padx=10, pady=5, sticky="w")

        self.cookie_method = tk.StringVar(value="none")
        
        self.radio_none = ctk.CTkRadioButton(self.cookies_frame, text="None", variable=self.cookie_method, value="none", command=self.toggle_cookie_input)
        self.radio_none.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.radio_browser = ctk.CTkRadioButton(self.cookies_frame, text="Browser Cookies", variable=self.cookie_method, value="browser", command=self.toggle_cookie_input)
        self.radio_browser.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        self.radio_file = ctk.CTkRadioButton(self.cookies_frame, text="Cookie File", variable=self.cookie_method, value="file", command=self.toggle_cookie_input)
        self.radio_file.grid(row=1, column=2, padx=10, pady=5, sticky="w")

        # Dynamic Cookie Inputs
        self.browser_combo = ctk.CTkComboBox(self.cookies_frame, values=["chrome", "firefox", "edge", "opera", "brave", "safari"])
        self.browser_combo.set("chrome")
        
        self.cookies_file_entry = ctk.CTkEntry(self.cookies_frame, placeholder_text="Path to cookies.txt")
        self.browse_cookies_btn = ctk.CTkButton(self.cookies_frame, text="Browse", width=80, command=self.browse_cookies)

        # --- Action Buttons ---
        self.download_button = ctk.CTkButton(self, text="DOWNLOAD SUBTITLES ONLY", height=50, fg_color="#2CC985", hover_color="#229E68", font=("Roboto", 16, "bold"), command=self.download_subtitles)
        self.download_button.grid(row=4, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        self.status_label = ctk.CTkLabel(self, text="Ready", text_color="gray")
        self.status_label.grid(row=5, column=0, columnspan=2, padx=20, pady=5)

        self.toggle_cookie_input() # Initialize state

    def toggle_cookie_input(self):
        # Clear previous dynamic widgets
        self.browser_combo.grid_forget()
        self.cookies_file_entry.grid_forget()
        self.browse_cookies_btn.grid_forget()

        method = self.cookie_method.get()
        if method == "browser":
            self.browser_combo.grid(row=2, column=0, columnspan=3, padx=10, pady=5, sticky="ew")
        elif method == "file":
            self.cookies_file_entry.grid(row=2, column=0, columnspan=1, padx=(10, 5), pady=5, sticky="ew")
            self.browse_cookies_btn.grid(row=2, column=1, padx=5, pady=5, columnspan=2)

    def browse_cookies(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if filepath:
            self.cookies_file_entry.delete(0, tk.END)
            self.cookies_file_entry.insert(0, filepath)

    def download_subtitles(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please enter a video URL.")
            return

        save_dir = filedialog.askdirectory()
        if not save_dir:
            return

        # Gather options
        lang_selection = self.lang_combo.get()
        include_auto = self.auto_subs_checkbox.get()
        convert_srt = self.convert_checkbox.get()
        raw_text = self.raw_text_checkbox.get()

        self.status_label.configure(text="Downloading subtitles...", text_color="#2CC985")
        self.download_button.configure(state="disabled")
        
        threading.Thread(target=self._download_thread, args=(url, save_dir, lang_selection, include_auto, convert_srt, raw_text)).start()

    def _download_thread(self, url, save_dir, lang_selection, include_auto, convert_srt, raw_text):
        try:
            # Base command: Skip video download, write subs
            command = ["yt-dlp", "--skip-download", "--write-subs", "-o", f"{save_dir}/%(title)s.%(ext)s"]
            
            # Subtitle Language
            lang_code = "en.*" # Default english
            if lang_selection == "Bengali":
                lang_code = "bn"
            elif lang_selection == "All Available":
                lang_code = "all"
            
            command.extend(["--sub-langs", lang_code])

            # Auto-generated subs
            if include_auto:
                command.append("--write-auto-subs")

            # Conversion: If raw_text is requested, we prefer converting to SRT first as it's easier to parse 
            # than unknown formats, but VTT is also fine.
            if convert_srt or raw_text: 
                command.extend(["--convert-subs", "srt"])

            # Auth
            method = self.cookie_method.get()
            if method == "browser":
                command.extend(["--cookies-from-browser", self.browser_combo.get()])
            elif method == "file":
                cpath = self.cookies_file_entry.get()
                if cpath: command.extend(["--cookies", cpath])
            
            # Anti-bot
            command.extend(["--extractor-args", "youtube:player_client=default"])
            
            command.append(url)

            # Process
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            downloaded_files = [] 
            
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    msg = line.strip()
                    if "[info]" in msg: msg = msg.replace("[info] ", "")
                    # Log to UI
                    self.after(0, lambda m=msg: self.status_label.configure(text=m[-80:]))
                    
                    # Capture downloaded/written subtitle filenames
                    # yt-dlp Output Example: "[info] Writing video subtitles to: C:\Path\Title.en.srt"
                    if "Writing video subtitles to: " in line:
                        parts = line.split("Writing video subtitles to: ")
                        if len(parts) > 1:
                            fpath = parts[1].strip()
                            downloaded_files.append(fpath)

            if process.returncode == 0:
                # If raw text requested, post-process
                if raw_text and downloaded_files:
                    self.after(0, lambda: self.status_label.configure(text="Converting to raw text..."))
                    for sub_file in downloaded_files:
                         self._convert_to_raw_text(sub_file)

                self.after(0, lambda: messagebox.showinfo("Success", "Subtitle Download Completed!"))
                self.after(0, lambda: self.status_label.configure(text="Ready", text_color="gray"))
            else:
                stderr = process.communicate()[1]
                raise Exception(stderr)

        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Failed: {e}"))
            self.after(0, lambda: self.status_label.configure(text="Error", text_color="red"))
        finally:
            self.after(0, lambda: self.download_button.configure(state="normal"))

    def _convert_to_raw_text(self, file_path):
        try:
            if not os.path.exists(file_path): 
                return

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.splitlines()
            text_lines = []
            
            is_srt = file_path.lower().endswith(".srt")
            
            if is_srt:
                # SRT Simple Parsing
                for line in lines:
                    line = line.strip()
                    if not line: continue
                    if line.isdigit(): continue
                    if "-->" in line: continue
                    text_lines.append(line)
            else:
                # Fallback VTT or others
                for line in lines:
                    line = line.strip()
                    if not line: continue
                    if line == "WEBVTT": continue
                    if "-->" in line: continue
                    text_lines.append(line)

            # Cleanup
            clean_text = "\n".join(text_lines)
            # Remove simple HTML tags
            clean_text = re.sub(r'<[^>]+>', '', clean_text)
            
            # Simple de-duplication of consecutive text 
            # (Often needed for auto-captions where text scrolls)
            final_lines = []
            prev_line = None
            for line in clean_text.splitlines():
                if line != prev_line:
                    final_lines.append(line)
                    prev_line = line
            
            final_content = "\n".join(final_lines)

            # Save as txt
            txt_path = os.path.splitext(file_path)[0] + ".txt"
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
                
            print(f"Created raw text file: {txt_path}")

        except Exception as e:
            print(f"Failed to convert {file_path} to raw text: {e}")

if __name__ == "__main__":
    app = YouTubeSubtitleDownloader()
    app.mainloop()
