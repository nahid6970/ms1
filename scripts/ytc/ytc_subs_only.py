import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import threading
import os

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("green")  # Distinct theme for the subtitles-only app

class YouTubeSubtitleDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("YouTube Subtitle Downloader")
        self.geometry("600x550")

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

        lang_selection = self.lang_combo.get()
        include_auto = self.auto_subs_checkbox.get()
        convert_srt = self.convert_checkbox.get()

        self.status_label.configure(text="Downloading subtitles...", text_color="#2CC985")
        self.download_button.configure(state="disabled")
        
        threading.Thread(target=self._download_thread, args=(url, save_dir, lang_selection, include_auto, convert_srt)).start()

    def _download_thread(self, url, save_dir, lang_selection, include_auto, convert_srt):
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

            # Conversion
            if convert_srt:
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
            
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    # Update status with relevant info (trimming generic info)
                    msg = line.strip()
                    if "[info]" in msg: msg = msg.replace("[info] ", "")
                    self.after(0, lambda m=msg: self.status_label.configure(text=m[-80:]))
            
            if process.returncode == 0:
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

if __name__ == "__main__":
    app = YouTubeSubtitleDownloader()
    app.mainloop()
