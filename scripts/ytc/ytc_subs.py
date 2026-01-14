import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import json
import subprocess
import threading
import os

ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class YouTubeDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("YouTube Video Downloader (with Subtitles)")
        self.geometry("700x700")

        # Configure grid layout (4x11)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)

        # --- URL Section ---
        self.url_label = ctk.CTkLabel(self, text="Video URL:")
        self.url_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        
        self.url_entry = ctk.CTkEntry(self, width=400, placeholder_text="Paste YouTube link here")
        self.url_entry.grid(row=0, column=1, padx=20, pady=(20, 5), sticky="ew")

        self.fetch_button = ctk.CTkButton(self, text="Fetch Formats", command=self.fetch_formats)
        self.fetch_button.grid(row=0, column=2, padx=20, pady=(20, 5))

        # --- Format SelectionSection ---
        self.video_format_label = ctk.CTkLabel(self, text="Video Format:")
        self.video_format_label.grid(row=1, column=0, padx=20, pady=5, sticky="w")
        
        self.video_format_combo = ctk.CTkComboBox(self, values=["Fetch URL first..."])
        self.video_format_combo.grid(row=1, column=1, padx=20, pady=5, sticky="ew", columnspan=2)

        self.audio_format_label = ctk.CTkLabel(self, text="Audio Format:")
        self.audio_format_label.grid(row=2, column=0, padx=20, pady=5, sticky="w")

        self.audio_format_combo = ctk.CTkComboBox(self, values=["Fetch URL first..."])
        self.audio_format_combo.grid(row=2, column=1, padx=20, pady=5, sticky="ew", columnspan=2)

        # --- Subtitles Section ---
        self.subtitle_frame = ctk.CTkFrame(self)
        self.subtitle_frame.grid(row=3, column=0, columnspan=3, padx=20, pady=10, sticky="ew")
        self.subtitle_frame.grid_columnconfigure(1, weight=1)

        self.subtitle_checkbox = ctk.CTkCheckBox(self.subtitle_frame, text="Download Subtitles", command=self.toggle_subtitle_options)
        self.subtitle_checkbox.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        self.subtitle_lang_label = ctk.CTkLabel(self.subtitle_frame, text="Language:", state="disabled")
        self.subtitle_lang_label.grid(row=0, column=1, padx=(10, 5), pady=10, sticky="e")

        self.subtitle_lang_combo = ctk.CTkComboBox(self.subtitle_frame, values=["English", "Bengali"], state="disabled")
        self.subtitle_lang_combo.grid(row=0, column=2, padx=20, pady=10, sticky="ew")
        self.subtitle_lang_combo.set("English")

        # --- Cookies / Auth Section ---
        self.cookies_frame = ctk.CTkFrame(self)
        self.cookies_frame.grid(row=4, column=0, columnspan=3, padx=20, pady=10, sticky="ew")
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
        self.help_cookies_btn = ctk.CTkButton(self.cookies_frame, text="?", width=30, command=self.show_cookie_help)

        # --- Key Action Buttons ---
        self.download_button = ctk.CTkButton(self, text="DOWNLOAD VIDEO", height=50, font=("Roboto", 16, "bold"), command=self.download_video)
        self.download_button.grid(row=6, column=0, columnspan=3, padx=20, pady=20, sticky="ew")

        self.status_label = ctk.CTkLabel(self, text="Ready", text_color="gray")
        self.status_label.grid(row=7, column=0, columnspan=3, padx=20, pady=5)

        self.update_button = ctk.CTkButton(self, text="Update yt-dlp", fg_color="transparent", border_width=1, command=self.update_yt_dlp)
        self.update_button.grid(row=8, column=0, columnspan=3, padx=20, pady=10)

        self.toggle_cookie_input() # Initialize state

    def toggle_subtitle_options(self):
        if self.subtitle_checkbox.get() == 1:
            self.subtitle_lang_label.configure(state="normal")
            self.subtitle_lang_combo.configure(state="normal")
        else:
            self.subtitle_lang_label.configure(state="disabled")
            self.subtitle_lang_combo.configure(state="disabled")

    def toggle_cookie_input(self):
        # Clear previous dynamic widgets
        self.browser_combo.grid_forget()
        self.cookies_file_entry.grid_forget()
        self.browse_cookies_btn.grid_forget()
        self.help_cookies_btn.grid_forget()

        method = self.cookie_method.get()
        if method == "browser":
            self.browser_combo.grid(row=2, column=0, columnspan=3, padx=10, pady=5, sticky="ew")
        elif method == "file":
            self.cookies_file_entry.grid(row=2, column=0, columnspan=1, padx=(10, 5), pady=5, sticky="ew")
            self.browse_cookies_btn.grid(row=2, column=1, padx=5, pady=5)
            self.help_cookies_btn.grid(row=2, column=2, padx=5, pady=5)

    def browse_cookies(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if filepath:
            self.cookies_file_entry.delete(0, tk.END)
            self.cookies_file_entry.insert(0, filepath)

    def show_cookie_help(self):
        help_text = """Cookie Authentication Help:
        
1. Use 'Browser Cookies' if you are logged into YouTube on that browser.
2. Use 'Cookie File' if you have exported cookies (e.g., via 'Get cookies.txt LOCALLY' extension).
   - This prevents age-restriction errors.
"""
        messagebox.showinfo("Help", help_text)

    def fetch_formats(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please enter a video URL.")
            return

        self.status_label.configure(text="Fetching formats...", text_color="#3B8ED0")
        self.fetch_button.configure(state="disabled")
        threading.Thread(target=self._fetch_formats_thread, args=(url,)).start()

    def _fetch_formats_thread(self, url):
        try:
            command = ["yt-dlp", "--dump-json"]
            
            # Auth
            method = self.cookie_method.get()
            if method == "browser":
                command.extend(["--cookies-from-browser", self.browser_combo.get()])
            elif method == "file":
                cookie_path = self.cookies_file_entry.get()
                if cookie_path:
                    command.extend(["--cookies", cookie_path])
            
            command.extend(["--extractor-args", "youtube:player_client=default"]) # Anti-bot
            command.append(url)

            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                raise Exception(stderr)

            video_info = json.loads(stdout)
            formats = video_info.get("formats", [])
            
            # Filter formats
            video_formats = [f for f in formats if f.get('vcodec') != 'none']
            audio_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
            
            self.after(0, lambda: self.update_format_combos(video_formats, audio_formats))

        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to fetch: {e}"))
            self.after(0, lambda: self.status_label.configure(text="Error fetching formats", text_color="red"))
        finally:
            self.after(0, lambda: self.fetch_button.configure(state="normal"))

    def update_format_combos(self, video_formats, audio_formats):
        # Format strings for display
        v_opts = [f"{f['format_id']} | {f['ext']} | {f.get('resolution', 'N/A')}" for f in video_formats]
        a_opts = [f"{f['format_id']} | {f['ext']} | {f.get('abr', 'N/A')}k" for f in audio_formats]

        self.video_format_combo.configure(values=["best"] + v_opts)
        self.audio_format_combo.configure(values=["best"] + a_opts)
        self.video_format_combo.set("best")
        self.audio_format_combo.set("best")
        self.status_label.configure(text="Formats fetched successfully", text_color="green")

    def download_video(self):
        url = self.url_entry.get()
        if not url: return

        # Formats
        v_sel = self.video_format_combo.get()
        a_sel = self.audio_format_combo.get()
        
        v_id = v_sel.split(" | ")[0]
        a_id = a_sel.split(" | ")[0]

        format_str = ""
        if v_id == "best" and a_id == "best":
            format_str = "bestvideo+bestaudio/best"
        elif v_id == "best":
            format_str = f"bestvideo+{a_id}"
        elif a_id == "best":
            format_str = f"{v_id}+bestaudio"
        else:
            format_str = f"{v_id}+{a_id}"

        # Directory
        save_dir = filedialog.askdirectory()
        if not save_dir: return

        # Subtitles
        download_subs = self.subtitle_checkbox.get()
        sub_lang = self.subtitle_lang_combo.get()
        
        # Start Thread
        self.status_label.configure(text="Downloading...", text_color="#3B8ED0")
        self.download_button.configure(state="disabled")
        threading.Thread(target=self._download_thread, args=(url, format_str, save_dir, download_subs, sub_lang)).start()

    def _download_thread(self, url, format_str, save_dir, download_subs, sub_lang):
        try:
            command = ["yt-dlp", "-f", format_str, "-o", f"{save_dir}/%(title)s.%(ext)s"]
            
            # Auth
            method = self.cookie_method.get()
            if method == "browser":
                command.extend(["--cookies-from-browser", self.browser_combo.get()])
            elif method == "file":
                cpath = self.cookies_file_entry.get()
                if cpath: command.extend(["--cookies", cpath])

            command.extend(["--extractor-args", "youtube:player_client=default"])

            # Subtitles Logic
            if download_subs:
                command.append("--write-subs")
                # Also write auto-subs if normal subs aren't available?
                # User asked explicitly for "download subtitles", usually implies manual first.
                # Adding --write-auto-subs as fallback is common good practice, 
                # but let's stick to what's requested: selection.
                
                lang_code = "en.*"
                if sub_lang == "Bengali":
                    lang_code = "bn"
                
                command.extend(["--sub-langs", lang_code])

            command.append(url)

            # Process
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    self.after(0, lambda m=line.strip(): self.status_label.configure(text=m[-80:])) # Show last part of log
            
            if process.returncode == 0:
                self.after(0, lambda: messagebox.showinfo("Success", "Download Completed!"))
                self.after(0, lambda: self.status_label.configure(text="Download Complete", text_color="green"))
            else:
                stderr = process.communicate()[1]
                raise Exception(stderr)

        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Download Failed: {e}"))
            self.after(0, lambda: self.status_label.configure(text="Download Failed", text_color="red"))
        finally:
            self.after(0, lambda: self.download_button.configure(state="normal"))

    def update_yt_dlp(self):
        self.status_label.configure(text="Updating yt-dlp...", text_color="orange")
        threading.Thread(target=lambda: self._run_update()).start()

    def _run_update(self):
        try:
             subprocess.run(["yt-dlp", "-U"], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
             self.after(0, lambda: messagebox.showinfo("Update", "yt-dlp updated successfully!"))
             self.after(0, lambda: self.status_label.configure(text="Ready", text_color="gray"))
        except Exception as e:
             self.after(0, lambda: messagebox.showerror("Update Failed", str(e)))

if __name__ == "__main__":
    app = YouTubeDownloader()
    app.mainloop()
