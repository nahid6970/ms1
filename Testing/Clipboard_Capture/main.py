import customtkinter as ctk
import pyperclip
import threading
import time
from datetime import datetime

class ClipboardManager(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SmartClip Manager")
        self.geometry("900x750")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.clipboard_history = []
        self.pattern_buffer = []  # Stores current incoming batch
        self.accumulated_text = "" # Stores the full result string
        self.displayed_history_len = 0
        self.is_running = True
        self.ignore_next = None 
        
        # Grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar (Settings & Controls) - Darker background
        self.sidebar_frame = ctk.CTkFrame(self, width=320, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(10, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="SmartClip", font=ctk.CTkFont(size=28, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 20))

        # --- Settings Section ---
        self.settings_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.settings_frame.grid(row=1, column=0, sticky="ew", padx=10)
        self.settings_frame.grid_columnconfigure(0, weight=1)

        # Mode Switch
        self.auto_mode_var = ctk.BooleanVar(value=False)
        self.mode_switch = ctk.CTkSwitch(self.settings_frame, text="Auto-Pattern Mode", 
                                       variable=self.auto_mode_var, command=self.toggle_mode,
                                       font=ctk.CTkFont(size=14, weight="bold"))
        self.mode_switch.grid(row=0, column=0, sticky="w", padx=10, pady=(0, 20))

        # Items per Group (Changed to Entry)
        ctk.CTkLabel(self.settings_frame, text="Items per Group").grid(row=1, column=0, sticky="w", padx=10)
        self.group_size_entry = ctk.CTkEntry(self.settings_frame, width=200)
        self.group_size_entry.insert(0, "2")
        self.group_size_entry.grid(row=2, column=0, sticky="w", padx=10, pady=(0, 5))

        # Pattern Template
        ctk.CTkLabel(self.settings_frame, text="Template Pattern ({1}, {2}...)").grid(row=5, column=0, sticky="w", padx=10, pady=(10, 0))
        self.template_entry = ctk.CTkEntry(self.settings_frame, placeholder_text="{1} -> **{2}**")
        self.template_entry.insert(0, "{1} -> **{2}**")
        self.template_entry.grid(row=6, column=0, sticky="ew", padx=10, pady=(5, 5))

        # Batch Status (Buffer)
        self.status_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="#2b2b2b", corner_radius=6)
        self.status_frame.grid(row=3, column=0, padx=15, pady=(20, 10), sticky="ew")
        self.status_frame.grid_columnconfigure(0, weight=1)

        self.batch_label = ctk.CTkLabel(self.status_frame, text="Pattern Builder", text_color="gray")
        self.batch_label.pack(pady=5)
        
        # Buffer display
        self.buffer_text = ctk.CTkLabel(self.status_frame, text="Waiting...", text_color="gray70", wraplength=280)
        self.buffer_text.pack(pady=(0, 5))
        
        # Accumulated result display
        self.result_text = ctk.CTkTextbox(self.status_frame, height=120, fg_color="#1f1f1f", text_color="#2ecc71")
        self.result_text.pack(fill="x", padx=5, pady=5)
        self.result_text.insert("0.0", "--- Generated Output ---")
        self.result_text.configure(state="disabled")

        # Action Buttons
        self.btns_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.btns_frame.grid(row=4, column=0, sticky="ew")
        self.btns_frame.grid_columnconfigure((0,1), weight=1)

        self.copy_output_btn = ctk.CTkButton(self.btns_frame, text="Copy Output", command=self.manual_copy_output, 
                                     fg_color="#2ecc71", hover_color="#27ae60", height=30)
        self.copy_output_btn.pack(side="top", fill="x", padx=20, pady=(5, 5))

        self.clear_buffer_btn = ctk.CTkButton(self.btns_frame, text="Reset & Clear", command=self.reset_session, 
                                     fg_color="#e74c3c", hover_color="#c0392b", height=30)
        self.clear_buffer_btn.pack(side="top", fill="x", padx=20, pady=(0, 5))
        
        ctk.CTkButton(self.sidebar_frame, text="Clear History", command=self.clear_history, fg_color="transparent", border_width=1, border_color="gray50", text_color="gray80", hover_color="#333333").grid(row=9, column=0, padx=20, pady=10, sticky="s")

        # Main Content (Clipboard History)
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#1a1a1a") # Darker main bg
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.history_header = ctk.CTkLabel(self.main_frame, text="Recent Clips", font=ctk.CTkFont(size=22, weight="bold"))
        self.history_header.grid(row=0, column=0, padx=30, pady=(30, 20), sticky="w")

        self.scrollable_frame = ctk.CTkScrollableFrame(self.main_frame, label_text="", fg_color="transparent")
        self.scrollable_frame.grid(row=1, column=0, padx=30, pady=(0, 30), sticky="nsew")

        # Start Monitor
        self.monitor_thread = threading.Thread(target=self.monitor_clipboard, daemon=True)
        self.monitor_thread.start()
        
        # Periodic UI Update
        self.after(500, self.update_ui_loop)

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.is_running = False
        self.destroy()

    def get_group_size(self):
        try:
            val = int(self.group_size_entry.get())
            return max(1, val)
        except ValueError:
            return 2 # Default fallback

    def toggle_mode(self):
        if self.auto_mode_var.get():
            self.batch_label.configure(text="Pattern Builder (Active)", text_color="#2ecc71")
            self.reset_session()
        else:
            self.batch_label.configure(text="Pattern Builder (Inactive)", text_color="gray")
            self.reset_session()

    def reset_session(self):
        self.pattern_buffer.clear()
        self.accumulated_text = ""
        self.update_status_display()

    def clear_history(self):
        self.clipboard_history.clear()
        self.displayed_history_len = 0
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

    def manual_copy_output(self):
        if self.accumulated_text:
            self.copy_to_clip(self.accumulated_text)

    def update_status_display(self):
        # Update Buffer Buffer Label
        if not self.pattern_buffer:
            self.buffer_text.configure(text="Buffer: Empty (Waiting for copy...)" if self.auto_mode_var.get() else "Buffer: Inactive")
        else:
            current_count = len(self.pattern_buffer)
            total_needed = self.get_group_size()
            self.buffer_text.configure(text=f"Buffer: {current_count}/{total_needed} items ready")

        # Update Result Textbox
        self.result_text.configure(state="normal")
        self.result_text.delete("0.0", "end")
        if self.accumulated_text:
            self.result_text.insert("0.0", self.accumulated_text)
        else:
            self.result_text.insert("0.0", "--- Output Preview ---")
        self.result_text.configure(state="disabled")

    def monitor_clipboard(self):
        last_clip = ""
        while self.is_running:
            try:
                curr_clip = pyperclip.paste()
                
                if curr_clip != last_clip and curr_clip.strip() != "":
                    
                    if self.ignore_next == curr_clip:
                        last_clip = curr_clip 
                        self.ignore_next = None
                        time.sleep(0.5)
                        continue

                    last_clip = curr_clip
                    self.clipboard_history.insert(0, curr_clip)
                    if len(self.clipboard_history) > 50: 
                        self.clipboard_history.pop()

                    if self.auto_mode_var.get():
                        self.handle_auto_mode(curr_clip)
                        
            except Exception:
                pass
            time.sleep(0.5)

    def handle_auto_mode(self, clip):
        self.pattern_buffer.append(clip)
        
        required_size = self.get_group_size()
        if len(self.pattern_buffer) >= required_size:
            self.create_pattern_and_paste()
        else:
            self.after(0, self.update_status_display)

    def create_pattern_and_paste(self):
        template = self.template_entry.get()
        chunk = self.pattern_buffer
        
        # Create line
        current_line = template
        for j, item in enumerate(chunk):
            placeholder = f"{{{j+1}}}"
            current_line = current_line.replace(placeholder, item.strip())
        
        # Accumulate
        if self.accumulated_text:
            self.accumulated_text += "\n" + current_line
        else:
            self.accumulated_text = current_line
            
        # Copy FULL accumulated text
        self.ignore_next = self.accumulated_text
        pyperclip.copy(self.accumulated_text)
        
        # Clear buffer but KEEP accumulation
        self.pattern_buffer = []
        
        # UI update
        self.after(0, self.update_status_display)

    def update_ui_loop(self):
        if not self.is_running:
            return
        
        current_len = len(self.clipboard_history)
        if current_len != self.displayed_history_len:
            self.refresh_list()
            self.displayed_history_len = current_len
        
        self.after(500, self.update_ui_loop)

    def refresh_list(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for idx, clip in enumerate(self.clipboard_history):
            preview = clip.replace("\n", " ").strip()
            if len(preview) > 60:
                preview = preview[:60] + "..."
            
            card = ctk.CTkFrame(self.scrollable_frame, fg_color="#2b2b2b", corner_radius=6)
            card.pack(fill="x", pady=4)
            
            ctk.CTkLabel(card, text=f"#{idx+1}", text_color="gray50", width=30).pack(side="left", padx=(10, 5))
            ctk.CTkLabel(card, text=preview, anchor="w", font=ctk.CTkFont(size=13)).pack(side="left", fill="x", expand=True, padx=5, pady=8)
            ctk.CTkButton(card, text="Copy", width=60, height=24, fg_color="transparent", border_width=1, 
                                     command=lambda c=clip: self.copy_to_clip(c)).pack(side="right", padx=10)

    def copy_to_clip(self, text):
        self.ignore_next = text
        pyperclip.copy(text)

if __name__ == "__main__":
    app = ClipboardManager()
    app.mainloop()
