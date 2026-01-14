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
        self.geometry("600x650")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)

        # --- URL Section ---
        self.url_label = ctk.CTkLabel(self, text="Video URL:")
        self.url_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        
        self.url_entry = ctk.CTkEntry(self, width=400, placeholder_text="Paste YouTube link here")
        self.url_entry.grid(row=0, column=1, padx=20, pady=(20, 5), sticky="ew")

        # --- Options Frame ---
        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        self.options_frame.grid_columnconfigure(1, weight=1)

        # Language
        self.lang_label = ctk.CTkLabel(self.options_frame, text="Language:", font=("Roboto", 12, "bold"))
        self.lang_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")

        self.lang_combo = ctk.CTkComboBox(self.options_frame, values=["English", "Bengali", "All Available"])
        self.lang_combo.grid(row=0, column=1, padx=15, pady=10, sticky="ew")
        self.lang_combo.set("English")

        self.auto_subs_checkbox = ctk.CTkCheckBox(self.options_frame, text="Include Auto-generated Subs")
        self.auto_subs_checkbox.grid(row=1, column=0, columnspan=2, padx=15, pady=5, sticky="w")

        # Format Selection (Radio Buttons)
        self.format_label = ctk.CTkLabel(self.options_frame, text="Output Format:", font=("Roboto", 12, "bold"))
        self.format_label.grid(row=2, column=0, padx=15, pady=10, sticky="nw")

        self.format_var = tk.StringVar(value="srt")
        
        self.radio_srt = ctk.CTkRadioButton(self.options_frame, text="SRT (SubRip)", variable=self.format_var, value="srt")
        self.radio_srt.grid(row=2, column=1, padx=15, pady=2, sticky="w")
        
        self.radio_vtt = ctk.CTkRadioButton(self.options_frame, text="VTT (WebVTT)", variable=self.format_var, value="vtt")
        self.radio_vtt.grid(row=3, column=1, padx=15, pady=2, sticky="w")
        
        self.radio_txt = ctk.CTkRadioButton(self.options_frame, text="Raw Text (.txt)", variable=self.format_var, value="txt")
        self.radio_txt.grid(row=4, column=1, padx=15, pady=2, sticky="w")

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
        self.download_button = ctk.CTkButton(self, text="DOWNLOAD", height=50, fg_color="#2CC985", hover_color="#229E68", font=("Roboto", 16, "bold"), command=self.download_subtitles)
        self.download_button.grid(row=4, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        self.status_label = ctk.CTkLabel(self, text="Ready", text_color="gray")
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

    def download_subtitles(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please enter a video URL.")
            return

        save_dir = filedialog.askdirectory()
        if not save_dir:
            return

        lang_selection = self.lang_combo.get()
        include_auto = self.auto_subs_checkbox.get()
        output_format = self.format_var.get() # srt, vtt, or txt

        self.status_label.configure(text="Downloading...", text_color="#2CC985")
        self.download_button.configure(state="disabled")
        
        threading.Thread(target=self._download_thread, args=(url, save_dir, lang_selection, include_auto, output_format)).start()

    def _convert_vtt_to_txt(self, vtt_path):
        """Simple regex-based VTT/SRT to Text converter that preserves lines but removes timestamps."""
        try:
            txt_path = os.path.splitext(vtt_path)[0] + ".txt"
            
            with open(vtt_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Remove Header (WEBVTT)
            content = re.sub(r'WEBVTT.*\n', '', content)
            
            # Remove timestamps (00:00:00.000 --> 00:00:05.000)
            # Matches VTT style and SRT style roughly
            content = re.sub(r'\d{2}:\d{2}:\d{2}[\.,]\d{3} --> \d{2}:\d{2}:\d{2}[\.,]\d{3}.*\n', '', content)
            
            # Remove pure numbers on their own lines (SRT indices)
            content = re.sub(r'^\d+\s*$', '', content, flags=re.MULTILINE)
            
            # Remove HTML/XML tags (like <c.color> or <b>)
            content = re.sub(r'<[^>]+>', '', content)

            # Cleanup empty lines
            lines = [line.strip() for line in content.splitlines() if line.strip()]
            
            # Deduplicate sequential identical lines (often happens in auto-subs)
            dedup_lines = []
            for line in lines:
                if not dedup_lines or dedup_lines[-1] != line:
                    dedup_lines.append(line)
            
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(dedup_lines))
            
            # Delete original
            os.remove(vtt_path)
            return True
        except Exception as e:
            print(f"Error converting {vtt_path}: {e}")
            return False

    def _download_thread(self, url, save_dir, lang_selection, include_auto, output_format):
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

            # Determine download format
            # If txt is requested, we download srt (easier to parse)
            dl_format = output_format if output_format != "txt" else "srt"
            command.extend(["--convert-subs", dl_format])

            # Auth
            method = self.cookie_method.get()
            if method == "browser":
                command.extend(["--cookies-from-browser", self.browser_combo.get()])
            elif method == "file":
                cpath = self.cookies_file_entry.get()
                if cpath: command.extend(["--cookies", cpath])
            
            command.extend(["--extractor-args", "youtube:player_client=default"])
            command.append(url)

            # Execution
            process = subprocess.Popen(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                creationflags=subprocess.CREATE_NO_WINDOW,
                bufsize=1,
                universal_newlines=True
            )
            
            downloaded_files = []

            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    line = line.strip()
                    self.after(0, lambda m=line: self.status_label.configure(text=m[-80:]))
                    
                    # Regex to capture filename robustly
                    # Matches: "[info] Writing video subtitles to: C:\Path\To\File.srt"
                    match = re.search(r'Writing video subtitles to:\s+(.+)$', line)
                    if match:
                         path = match.group(1).strip()
                         downloaded_files.append(path)

            stderr = process.communicate()[1]

            if process.returncode == 0:
                # Post-processing for Text
                if output_format == "txt":
                    self.after(0, lambda: self.status_label.configure(text="Converting to raw text..."))
                    if not downloaded_files:
                        self.after(0, lambda: messagebox.showwarning("Warning", "Download successful but could not auto-convert to text (file path not detected)."))
                    
                    for fpath in downloaded_files:
                        self._convert_vtt_to_txt(fpath)

                self.after(0, lambda: messagebox.showinfo("Success", "Download Completed!"))
                self.after(0, lambda: self.status_label.configure(text="Ready", text_color="gray"))
            else:
                self.after(0, lambda: messagebox.showerror("Error", f"Download failed:\n{stderr}"))
                self.after(0, lambda: self.status_label.configure(text="Error", text_color="red"))

        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Failed: {e}"))
            self.after(0, lambda: self.status_label.configure(text="Error", text_color="red"))
        finally:
            self.after(0, lambda: self.download_button.configure(state="normal"))

if __name__ == "__main__":
    app = YouTubeSubtitleDownloader()
    app.mainloop()
