import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import subprocess
import threading

class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        self.root.geometry("600x550")

        # URL Entry
        self.url_label = ttk.Label(root, text="Video URL:")
        self.url_label.pack(pady=5)
        self.url_entry = ttk.Entry(root, width=70)
        self.url_entry.pack(pady=5)
        self.fetch_button = ttk.Button(root, text="Fetch Formats", command=self.fetch_formats)
        self.fetch_button.pack(pady=5)

        # Format Selection
        self.video_format_label = ttk.Label(root, text="Video Format:")
        self.video_format_label.pack(pady=5)
        self.video_format_combo = ttk.Combobox(root, width=60)
        self.video_format_combo.pack(pady=5)

        self.audio_format_label = ttk.Label(root, text="Audio Format:")
        self.audio_format_label.pack(pady=5)
        self.audio_format_combo = ttk.Combobox(root, width=60)
        self.audio_format_combo.pack(pady=5)

        # Cookies
        self.cookies_label = ttk.Label(root, text="Authentication (for age-restricted videos):")
        self.cookies_label.pack(pady=5)
        
        # Cookie method selection
        self.cookie_method_frame = ttk.Frame(root)
        self.cookie_method_frame.pack(pady=5)
        
        self.cookie_method = tk.StringVar(value="none")
        ttk.Radiobutton(self.cookie_method_frame, text="None", variable=self.cookie_method, value="none", command=self.toggle_cookie_input).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(self.cookie_method_frame, text="Browser Cookies", variable=self.cookie_method, value="browser", command=self.toggle_cookie_input).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(self.cookie_method_frame, text="Cookie File", variable=self.cookie_method, value="file", command=self.toggle_cookie_input).pack(side=tk.LEFT, padx=5)
        
        # Browser selection
        self.browser_frame = ttk.Frame(root)
        self.browser_combo = ttk.Combobox(self.browser_frame, width=30, values=["chrome", "firefox", "edge", "safari", "opera", "brave"])
        self.browser_combo.set("chrome")
        self.browser_combo.pack(side=tk.LEFT, padx=5)
        
        # Cookie file selection
        self.cookies_file_frame = ttk.Frame(root)
        self.cookies_entry = ttk.Entry(self.cookies_file_frame, width=40)
        self.cookies_entry.pack(side=tk.LEFT, padx=5)
        self.browse_button = ttk.Button(self.cookies_file_frame, text="Browse", command=self.browse_cookies)
        self.browse_button.pack(side=tk.LEFT, padx=5)
        self.help_button = ttk.Button(self.cookies_file_frame, text="Help", command=self.show_cookie_help)
        self.help_button.pack(side=tk.LEFT, padx=5)

        # Download Button
        self.download_button = ttk.Button(root, text="Download", command=self.download_video)
        self.download_button.pack(pady=20)

        # Update Button
        self.update_button = ttk.Button(root, text="Update yt-dlp", command=self.update_yt_dlp)
        self.update_button.pack(pady=5)

        # Status Label
        self.status_label = ttk.Label(root, text="")
        self.status_label.pack(pady=5)
        
        # Initialize cookie input visibility
        self.toggle_cookie_input()

    def toggle_cookie_input(self):
        # Hide all cookie input frames first
        self.browser_frame.pack_forget()
        self.cookies_file_frame.pack_forget()
        
        # Show appropriate frame based on selection
        if self.cookie_method.get() == "browser":
            self.browser_frame.pack(pady=5)
        elif self.cookie_method.get() == "file":
            self.cookies_file_frame.pack(pady=5)
    
    def fetch_formats(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please enter a video URL.")
            return

        self.status_label.config(text="Fetching formats...")
        threading.Thread(target=self._fetch_formats_thread, args=(url,)).start()

    def _fetch_formats_thread(self, url):
        try:
            command = ["yt-dlp", "--dump-json"]
            
            # Add cookie authentication if specified
            cookie_method = self.cookie_method.get()
            if cookie_method == "browser":
                browser = self.browser_combo.get()
                command.extend(["--cookies-from-browser", browser])
            elif cookie_method == "file":
                cookies_file = self.cookies_entry.get()
                if cookies_file:
                    command.extend(["--cookies", cookies_file])
            
            # Add fallback for age-restricted videos
            command.extend(["--extractor-args", "youtube:player_client=default"])
            
            command.append(url)
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                error_msg = stderr
                # Add helpful hints for common errors
                if "Could not copy Chrome cookie database" in stderr:
                    error_msg += "\n\nTIP: Close ALL Chrome windows and try again, or use Firefox/Edge instead, or click 'Help' for cookie export instructions."
                elif "Failed to decrypt with DPAPI" in stderr:
                    error_msg += "\n\nTIP: Windows DPAPI decryption failed. You must export cookies manually using a browser extension. Click 'Help' for instructions."
                elif "Sign in to confirm your age" in stderr or "age-restricted" in stderr:
                    error_msg += "\n\nTIP: This video is age-restricted. You must use authentication. Click 'Help' for instructions."
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to fetch formats:\n{error_msg}"))
                self.root.after(0, lambda: self.status_label.config(text=""))
                return

            video_info = json.loads(stdout)
            formats = video_info.get("formats", [])

            video_formats = [f for f in formats if f.get('vcodec') != 'none']
            audio_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none']

            self.root.after(0, self.update_format_combos, video_formats, audio_formats)
            self.root.after(0, lambda: self.status_label.config(text="Formats fetched successfully."))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {e}"))
            self.root.after(0, lambda: self.status_label.config(text=""))

    def update_format_combos(self, video_formats, audio_formats):
        video_values = [f"{f['format_id']} - {f['ext']} - {f.get('resolution', 'N/A')}" for f in video_formats]
        audio_values = [f"{f['format_id']} - {f['ext']} - {f.get('abr', 'N/A')}k" for f in audio_formats]

        self.video_format_combo['values'] = ["best"] + video_values
        self.audio_format_combo['values'] = ["best"] + audio_values

        self.video_format_combo.set("best")
        self.audio_format_combo.set("best")

    def browse_cookies(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if filepath:
            self.cookies_entry.delete(0, tk.END)
            self.cookies_entry.insert(0, filepath)
    
    def show_cookie_help(self):
        help_text = """How to fix cookie authentication errors:

⚠️ DPAPI ERROR? You MUST use METHOD 3 (manual export)

METHOD 1: Close Chrome and try again
- Close ALL Chrome windows completely
- Then use "Browser Cookies" option
- ❌ Won't work for DPAPI errors

METHOD 2: Use Firefox instead
- Select "firefox" from the browser dropdown
- Make sure you're logged into YouTube in Firefox
- ❌ May still have DPAPI errors

METHOD 3: Export cookies manually (RECOMMENDED)
1. Install browser extension:
   Chrome: "Get cookies.txt LOCALLY" 
   Firefox: "cookies.txt"
   
2. Go to youtube.com while logged in
3. Click the extension icon
4. Click "Export" or "Download"
5. Save the cookies.txt file
6. In this app:
   - Select "Cookie File"
   - Click "Browse" and select the .txt file

METHOD 4: Try without authentication
- Select "None" for authentication
- May work for some videos (not age-restricted)

EXTENSION LINKS:
Chrome: Search "Get cookies.txt LOCALLY" in Chrome Web Store
Firefox: Search "cookies.txt" in Firefox Add-ons"""
        
        messagebox.showinfo("Cookie Authentication Help", help_text)

    def download_video(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please enter a video URL.")
            return

        video_selection = self.video_format_combo.get()
        audio_selection = self.audio_format_combo.get()

        video_format_id = video_selection.split(" - ")[0]
        audio_format_id = audio_selection.split(" - ")[0]

        if not video_format_id and not audio_format_id:
            messagebox.showerror("Error", "Please select at least one format.")
            return

        download_path = filedialog.askdirectory()
        if not download_path:
            return

        format_selection = ""
        if video_format_id == "best" and audio_format_id == "best":
            format_selection = "bestvideo+bestaudio/best"
        elif video_format_id == "best":
            format_selection = f"bestvideo+{audio_format_id}"
        elif audio_format_id == "best":
            format_selection = f"{video_format_id}+bestaudio"
        else:
            if video_format_id and audio_format_id:
                format_selection = f"{video_format_id}+{audio_format_id}"
            elif video_format_id:
                format_selection = video_format_id
            elif audio_format_id:
                format_selection = audio_format_id

        cookies_file = self.cookies_entry.get()
        self.status_label.config(text="Downloading...")
        threading.Thread(target=self._download_thread, args=(url, format_selection, download_path, cookies_file)).start()

    def _download_thread(self, url, format_selection, download_path, cookies_file):
        try:
            command = ["yt-dlp", "-f", format_selection, "-o", f"{download_path}/%(title)s.%(ext)s"]
            
            # Add cookie authentication
            cookie_method = self.cookie_method.get()
            if cookie_method == "browser":
                browser = self.browser_combo.get()
                command.extend(["--cookies-from-browser", browser])
            elif cookie_method == "file" and cookies_file:
                command.extend(["--cookies", cookies_file])
            
            # Add fallback for age-restricted videos
            command.extend(["--extractor-args", "youtube:player_client=default"])
            
            command.append(url)

            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.root.after(0, self.update_status, output.strip())
            
            stderr = process.communicate()[1]
            if process.returncode != 0:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Download failed:\n{stderr}"))
            else:
                self.root.after(0, lambda: messagebox.showinfo("Success", "Download completed successfully!"))

            self.root.after(0, lambda: self.status_label.config(text=""))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {e}"))
            self.root.after(0, lambda: self.status_label.config(text=""))
    
    def update_status(self, message):
        self.status_label.config(text=message)

    def update_yt_dlp(self):
        self.status_label.config(text="Updating yt-dlp...")
        threading.Thread(target=self._update_yt_dlp_thread).start()

    def _update_yt_dlp_thread(self):
        try:
            command = ["yt-dlp", "-U"]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to update yt-dlp:\n{stderr}"))
            else:
                self.root.after(0, lambda: messagebox.showinfo("Success", f"yt-dlp update output:\n{stdout}"))

            self.root.after(0, lambda: self.status_label.config(text=""))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred during update: {e}"))
            self.root.after(0, lambda: self.status_label.config(text=""))

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()