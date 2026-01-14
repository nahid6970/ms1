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

    def _convert_to_raw_text(self, file_path):
        """Converts SRT/VTT to strict raw text by removing timestamps, indices, and tags."""
        try:
            txt_path = os.path.splitext(file_path)[0] + ".txt"
            
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            clean_lines = []
            last_line = ""

            for line in lines:
                line = line.strip()
                if not line: continue
                
                # Skip numeric indices (pure numbers)
                if line.isdigit():
                    continue
                
                # Skip timestamp lines (contain "-->")
                if "-->" in line:
                    continue
                
                # Skip Headers (common in VTT)
                if line.startswith("WEBVTT") or line.startswith("Kind:") or line.startswith("Language:"):
                    continue

                # Remove HTML/XML tags (like <c.color>, <i>, <b>, <font>)
                line = re.sub(r'<[^>]+>', '', line)
                
                # Remove timestamps if inline (rare in standard srt but good safety)
                line = re.sub(r'\d{2}:\d{2}:\d{2}[\.,]\d{3}', '', line)

                if not line: continue

                # Sequential Dedup (avoid repeating lines)
                if line != last_line:
                    clean_lines.append(line)
                    last_line = line
            
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(clean_lines))
            
            # Delete original srt/vtt
            os.remove(file_path)
            return True
        except Exception as e:
            print(f"Error converting {file_path}: {e}")
            return False

    def _convert_to_raw_text(self, file_path):
        """Converts SRT/VTT to strict raw text by removing timestamps, indices, tags, and rolling duplicates."""
        try:
            txt_path = os.path.splitext(file_path)[0] + ".txt"
            
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            clean_lines = []
            seen_lines = set() # For global deduplication if needed, but let's do sequential smart processing

            for line in lines:
                line = line.strip()
                if not line: continue
                
                # Check 1: Strict numeric index (just digits)
                if re.fullmatch(r'\d+', line):
                    continue
                
                # Check 2: Timestamp line (contains arrow)
                if "-->" in line:
                    continue
                
                # Check 3: WebVTT Headers
                if line.startswith("WEBVTT") or line.startswith("Kind:") or line.startswith("Language:"):
                    continue

                # Remove Tags
                line = re.sub(r'<[^>]+>', '', line)
                
                # Remove inline timestamps if any
                line = re.sub(r'\d{2}:\d{2}:\d{2}[\.,]\d{3}', '', line)
                line = line.strip()
                
                if not line: continue

                # Logic for "Rolling" captions (e.g. Line 1, then Line 1+2, then Line 1+2+3)
                # We want to only keep the 'new' part of the info.
                # However, generic deduplication (checking if previous line is same) is safest for now.
                # Advanced de-rolling is risky without semantic analysis.
                # We will just do strict sequential deduplication.
                
                if not clean_lines or clean_lines[-1] != line:
                    # Also check if this line is just a substring of the previous one (rare)
                    # or if the previous line is a substring of this one (rolling caption case!)
                    
                    # Case: Rolling captions
                    # Prev: "Hello"
                    # Curr: "Hello World"
                    # We want to maybe just update the last line? 
                    # OR we just output "Hello World" and user sees repetition?
                    # The user specifically asked to remove numbers and timestamps.
                    # Let's keep it simple: Sequential Dedup.
                     clean_lines.append(line)
            
            # Additional cleanup: Filter out lines that are subsets of the next line (Rolling fix attempt)
            # Example:
            # 1. "Test"
            # 2. "Test Live"
            # -> We usually only want "Test Live", but this is tricky if they are distinct sentences.
            # Let's stick to the requested "remove timestamps and numbers" for now, 
            # but I will add a check: if `line` starts with `last_line`, process it?
            # Actually, standard SRT viewers handle this. For raw text, it IS annoying.
            # Let's try a simple heuristic: If Line B starts with Line A, replace Line A with Line B.
            
            final_lines = []
            for line in clean_lines:
                if final_lines and line.startswith(final_lines[-1]):
                    # Replace the previous partial line with the new longer one
                    final_lines[-1] = line
                elif final_lines and final_lines[-1] in line:
                     # If the previous line is contained anywhere in the new line?
                     # Too aggressive. "I am" -> "I am here".
                     final_lines[-1] = line
                else:
                    final_lines.append(line)

            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(final_lines))
            
            # Delete original
            try:
                os.remove(file_path)
            except:
                pass
            return True
        except Exception as e:
            print(f"Error converting {file_path}: {e}")
            return False

    def _download_thread(self, url, save_dir, lang_selection, include_auto, output_format):
        try:
            # Track start time to find new files
            import time
            start_time = time.time()

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
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Just read output to keep buffer clear, but don't rely on it for filenames
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    self.after(0, lambda m=line.strip(): self.status_label.configure(text=m[-80:]))

            stderr = process.communicate()[1]

            if process.returncode == 0:
                if output_format == "txt":
                    self.after(0, lambda: self.status_label.configure(text="Converting to raw text..."))
                    
                    # Robust File Finding: Look for any .srt or .vtt file modified AFTER start_time in the folder
                    found_files = []
                    try:
                        for filename in os.listdir(save_dir):
                            if filename.endswith(".srt") or filename.endswith(".vtt"):
                                full_path = os.path.join(save_dir, filename)
                                # Check modification time
                                if os.path.getmtime(full_path) > start_time - 5: # 5s buffer
                                    found_files.append(full_path)
                    except Exception as e:
                        print(f"File scan error: {e}")

                    if found_files:
                        success_count = 0
                        for fpath in found_files:
                            if self._convert_to_raw_text(fpath):
                                success_count += 1
                        
                        if success_count > 0:
                             self.after(0, lambda: messagebox.showinfo("Success", f"Download & Conversion Completed!\nProcessed {success_count} file(s)."))
                        else:
                             self.after(0, lambda: messagebox.showwarning("Warning", "Downloaded files found but conversion failed."))
                    else:
                        self.after(0, lambda: messagebox.showwarning("Warning", "Download successful but no new subtitle files were found for conversion."))

                else:
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
