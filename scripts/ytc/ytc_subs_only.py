import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import threading
import os
import re
import tempfile
import webbrowser

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("green")

class YouTubeSubtitleDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("YouTube Subtitle Downloader")
        self.geometry("650x650")

        # Configure grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)

        # --- URL Section ---
        self.url_label = ctk.CTkLabel(self, text="Video URL:")
        self.url_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        
        self.url_entry = ctk.CTkEntry(self, width=400, placeholder_text="Paste YouTube link here")
        self.url_entry.grid(row=0, column=1, padx=20, pady=(20, 5), sticky="ew")

        # --- Options Frame ---
        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=20, sticky="ew")
        self.options_frame.grid_columnconfigure(1, weight=1)

        # Language
        self.lang_label = ctk.CTkLabel(self.options_frame, text="Language:", font=("Roboto", 14, "bold"))
        self.lang_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        self.lang_combo = ctk.CTkComboBox(self.options_frame, values=["English", "Bengali", "All Available"])
        self.lang_combo.grid(row=0, column=1, padx=15, pady=15, sticky="ew")
        self.lang_combo.set("English")

        # Checkboxes
        self.auto_subs_checkbox = ctk.CTkCheckBox(self.options_frame, text="Include Auto-generated Subs")
        self.auto_subs_checkbox.grid(row=1, column=0, columnspan=2, padx=15, pady=(0, 15), sticky="w")
        
        self.convert_checkbox = ctk.CTkCheckBox(self.options_frame, text="Convert to SRT (Best compatibility)")
        self.convert_checkbox.grid(row=2, column=0, columnspan=2, padx=15, pady=(0, 15), sticky="w")
        self.convert_checkbox.select()

        self.raw_text_checkbox = ctk.CTkCheckBox(self.options_frame, text="Save as Raw Text (No Timestamps)")
        self.raw_text_checkbox.grid(row=3, column=0, columnspan=2, padx=15, pady=(0, 15), sticky="w")

        # --- Output Method Section ---
        self.output_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.output_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=0, sticky="ew")
        
        self.output_label = ctk.CTkLabel(self.output_frame, text="Output Action:", font=("Roboto", 14, "bold"))
        self.output_label.pack(side="left", padx=(10, 20))

        self.output_mode = tk.StringVar(value="save")
        self.radio_save = ctk.CTkRadioButton(self.output_frame, text="Save to File", variable=self.output_mode, value="save")
        self.radio_save.pack(side="left", padx=10)
        
        self.radio_view = ctk.CTkRadioButton(self.output_frame, text="View in Browser (No Save)", variable=self.output_mode, value="view")
        self.radio_view.pack(side="left", padx=10)

        # --- Cookies / Auth Section ---
        self.cookies_frame = ctk.CTkFrame(self)
        self.cookies_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
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

        self.browser_combo = ctk.CTkComboBox(self.cookies_frame, values=["chrome", "firefox", "edge", "opera", "brave", "safari"])
        self.browser_combo.set("chrome")
        self.cookies_file_entry = ctk.CTkEntry(self.cookies_frame, placeholder_text="Path to cookies.txt")
        self.browse_cookies_btn = ctk.CTkButton(self.cookies_frame, text="Browse", width=80, command=self.browse_cookies)

        # --- Action Buttons ---
        self.download_button = ctk.CTkButton(self, text="PROCEED", height=50, fg_color="#2CC985", hover_color="#229E68", font=("Roboto", 16, "bold"), command=self.start_process)
        self.download_button.grid(row=4, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        self.status_label = ctk.CTkLabel(self, text="Ready", text_color="gray", wraplength=550)
        self.status_label.grid(row=5, column=0, columnspan=2, padx=20, pady=5)

        self.toggle_cookie_input()

    def toggle_cookie_input(self):
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

    def start_process(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please enter a video URL.")
            return

        mode = self.output_mode.get()
        
        save_dir = ""
        if mode == "save":
            save_dir = filedialog.askdirectory()
            if not save_dir: return
        else:
            save_dir = tempfile.mkdtemp()

        # Gather options
        lang_selection = self.lang_combo.get()
        include_auto = self.auto_subs_checkbox.get()
        convert_srt = self.convert_checkbox.get()
        raw_text = self.raw_text_checkbox.get()

        # If viewing in browser, force conversion/raw handling
        if mode == "view":
            convert_srt = True 

        self.status_label.configure(text="Processing...", text_color="#2CC985")
        self.download_button.configure(state="disabled")
        
        threading.Thread(target=self._process_thread, args=(url, save_dir, lang_selection, include_auto, convert_srt, raw_text, mode)).start()

    def _process_thread(self, url, save_dir, lang_selection, include_auto, convert_srt, raw_text, mode):
        try:
            command = ["yt-dlp", "--skip-download", "--write-subs", "-o", f"{save_dir}/%(title)s.%(ext)s"]
            
            # Language
            lang_code = "en.*"
            if lang_selection == "Bengali":
                lang_code = "bn"
            elif lang_selection == "All Available":
                lang_code = "all"
            command.extend(["--sub-langs", lang_code])

            if include_auto:
                command.append("--write-auto-subs")

            # Always convert to srt if we need raw text or browser view, to make parsing easier
            if convert_srt or raw_text or mode == "view": 
                command.extend(["--convert-subs", "srt"])

            # Auth
            method = self.cookie_method.get()
            if method == "browser":
                command.extend(["--cookies-from-browser", self.browser_combo.get()])
            elif method == "file":
                cpath = self.cookies_file_entry.get()
                if cpath: command.extend(["--cookies", cpath])
            
            command.extend(["--extractor-args", "youtube:player_client=default"])
            command.append(url)

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
                    
                    # Capture downloaded filenames more aggressively
                    # Look for "Writing video subtitles to: <filename>"
                    if "Writing video subtitles to: " in line:
                        parts = line.split("Writing video subtitles to: ")
                        if len(parts) > 1:
                            fpath = parts[1].strip()
                            downloaded_files.append(fpath)

            if process.returncode == 0:
                final_files = []
                
                # Raw Text Conversion
                if (raw_text or mode == "view") and downloaded_files:
                    self.after(0, lambda: self.status_label.configure(text="Converting to text..."))
                    for sub_file in downloaded_files:
                         txt_path = self._convert_to_raw_text(sub_file)
                         if txt_path: final_files.append(txt_path)
                else:
                    final_files = downloaded_files

                if mode == "view":
                    if not final_files:
                        self.after(0, lambda: messagebox.showerror("Error", "No subtitles found to view."))
                    else:
                        for f in final_files:
                            # Create a nice HTML wrapper for the text
                            html_path = self._create_html_view(f)
                            webbrowser.open(f"file:///{html_path}")
                        self.after(0, lambda: self.status_label.configure(text="Opened in browser", text_color="green"))
                else:
                    if not final_files:
                         self.after(0, lambda: messagebox.showwarning("Warning", "Download process finished but no subtitle files were detected. Check if usage rights or auto-subs settings prevented download."))
                    else:
                        self.after(0, lambda: messagebox.showinfo("Success", f"Saved to:\n{save_dir}"))
                        self.after(0, lambda: self.status_label.configure(text="Done", text_color="green"))

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
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.splitlines()
            text_lines = []
            
            is_srt = file_path.lower().endswith(".srt")
            
            # Basic parsing logic
            if is_srt:
                for line in lines:
                    line = line.strip()
                    if not line: continue
                    if line.isdigit(): continue
                    if "-->" in line: continue
                    text_lines.append(line)
            else:
                for line in lines:
                    line = line.strip()
                    if not line: continue
                    if line == "WEBVTT": continue
                    if "-->" in line: continue
                    text_lines.append(line)

            clean_text = "\n".join(text_lines)
            clean_text = re.sub(r'<[^>]+>', '', clean_text)
            
            final_lines = []
            prev_line = None
            for line in clean_text.splitlines():
                if line != prev_line:
                    final_lines.append(line)
                    prev_line = line
            
            final_content = "\n".join(final_lines)

            txt_path = os.path.splitext(file_path)[0] + ".txt"
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
                
            return txt_path

        except Exception as e:
            print(f"Failed to convert {file_path}: {e}")
            return None

    def _create_html_view(self, txt_path):
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            safe_content = content.replace("\n", "<br>").replace("  ", "&nbsp;&nbsp;")
            
            # A nice clean reading interface
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Subtitle Viewer</title>
                <style>
                    body {{ font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f4f4f4; color: #333; }}
                    .container {{ background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    h1 {{ color: #2CC985; font-size: 24px; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
                    .content {{ white-space: pre-wrap; font-size: 18px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Subtitle Content</h1>
                    <div class="content">{safe_content}</div>
                </div>
            </body>
            </html>
            """
            
            html_path = txt_path + ".html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html)
            return html_path
            
        except Exception:
            return txt_path # Fallback to opening text file

if __name__ == "__main__":
    app = YouTubeSubtitleDownloader()
    app.mainloop()
