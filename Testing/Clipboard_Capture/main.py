import customtkinter as ctk
import pyperclip
import threading
import time
from datetime import datetime

class ClipboardManager(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SmartClip Manager")
        self.geometry("900x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.clipboard_history = []
        self.displayed_history_len = 0
        self.is_running = True
        
        # Grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar (Settings & Controls) - Darker background
        self.sidebar_frame = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(10, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="SmartClip", font=ctk.CTkFont(size=28, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 20))

        # --- Settings Section ---
        self.settings_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.settings_frame.grid(row=1, column=0, sticky="ew", padx=10)
        self.settings_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.settings_frame, text="PATTERN SETTINGS", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray70").grid(row=0, column=0, sticky="w", padx=10, pady=(0, 10))

        # Items per Group
        ctk.CTkLabel(self.settings_frame, text="Items per Group").grid(row=1, column=0, sticky="w", padx=10)
        self.group_size_slider = ctk.CTkSlider(self.settings_frame, from_=1, to=10, number_of_steps=9)
        self.group_size_slider.set(2)
        self.group_size_slider.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 5))
        self.group_size_value = ctk.CTkLabel(self.settings_frame, text="2", font=ctk.CTkFont(weight="bold"))
        self.group_size_value.grid(row=2, column=0, sticky="e", padx=15)
        self.group_size_slider.configure(command=self.update_slider_labels)

        # Total Items
        ctk.CTkLabel(self.settings_frame, text="Total Items to Process").grid(row=3, column=0, sticky="w", padx=10, pady=(10, 0))
        self.total_items_slider = ctk.CTkSlider(self.settings_frame, from_=2, to=20, number_of_steps=18)
        self.total_items_slider.set(4)
        self.total_items_slider.grid(row=4, column=0, sticky="ew", padx=10, pady=(0, 5))
        self.total_items_value = ctk.CTkLabel(self.settings_frame, text="4", font=ctk.CTkFont(weight="bold"))
        self.total_items_value.grid(row=4, column=0, sticky="e", padx=15)
        self.total_items_slider.configure(command=self.update_slider_labels)

        # Pattern Template
        ctk.CTkLabel(self.settings_frame, text="Template Pattern ({1}, {2}...)").grid(row=5, column=0, sticky="w", padx=10, pady=(10, 0))
        self.template_entry = ctk.CTkEntry(self.settings_frame, placeholder_text="{1} -> **{2}**")
        self.template_entry.insert(0, "{1} -> **{2}**")
        self.template_entry.grid(row=6, column=0, sticky="ew", padx=10, pady=(5, 5))

        # Separator Setting
        ctk.CTkLabel(self.settings_frame, text="Row Separator (default: Newline)").grid(row=7, column=0, sticky="w", padx=10, pady=(10, 0))
        self.separator_entry = ctk.CTkEntry(self.settings_frame, placeholder_text="\\n")
        self.separator_entry.insert(0, "\\n")
        self.separator_entry.grid(row=8, column=0, sticky="ew", padx=10, pady=(5, 5))

        # Action Buttons
        self.process_btn = ctk.CTkButton(self.sidebar_frame, text="GENERATE PATTERN", command=self.process_pattern, 
                                       fg_color="#106BA0", hover_color="#0D4F75", height=40, font=ctk.CTkFont(weight="bold"))
        self.process_btn.grid(row=2, column=0, padx=20, pady=30, sticky="ew")
        
        # Status Label
        self.status_label = ctk.CTkLabel(self.sidebar_frame, text="", text_color="green")
        self.status_label.grid(row=3, column=0)

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
        self.after(500, self.update_history_ui_loop)

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.is_running = False
        self.destroy()

    def update_slider_labels(self, value=None):
        self.group_size_value.configure(text=str(int(self.group_size_slider.get())))
        self.total_items_value.configure(text=str(int(self.total_items_slider.get())))

    def clear_history(self):
        self.clipboard_history.clear()
        self.displayed_history_len = 0
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

    def monitor_clipboard(self):
        last_clip = ""
        while self.is_running:
            try:
                curr_clip = pyperclip.paste()
                if curr_clip != last_clip and curr_clip.strip() != "":
                    last_clip = curr_clip
                    # Store as valid text
                    self.clipboard_history.insert(0, curr_clip)
                    if len(self.clipboard_history) > 50: # Keep last 50
                        self.clipboard_history.pop()
            except Exception as e:
                print(f"Clipboard Error: {e}")
            time.sleep(0.5)

    def update_history_ui_loop(self):
        if not self.is_running:
            return
            
        # Only update if length changed or first run
        current_len = len(self.clipboard_history)
        if current_len != self.displayed_history_len:
            self.refresh_list()
            self.displayed_history_len = current_len
        
        self.after(500, self.update_history_ui_loop)

    def refresh_list(self):
        # Clear existing
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for idx, clip in enumerate(self.clipboard_history):
            preview = clip.replace("\n", " ").strip()
            if len(preview) > 60:
                preview = preview[:60] + "..."
            
            # Card-like look
            card = ctk.CTkFrame(self.scrollable_frame, fg_color="#2b2b2b", corner_radius=6)
            card.pack(fill="x", pady=4)
            
            lbl_idx = ctk.CTkLabel(card, text=f"#{idx+1}", text_color="gray50", width=30)
            lbl_idx.pack(side="left", padx=(10, 5))

            lbl_text = ctk.CTkLabel(card, text=preview, anchor="w", font=ctk.CTkFont(size=13))
            lbl_text.pack(side="left", fill="x", expand=True, padx=5, pady=8)

            btn_copy = ctk.CTkButton(card, text="Copy", width=60, height=24, fg_color="transparent", border_width=1, 
                                     command=lambda c=clip: self.copy_to_clip(c))
            btn_copy.pack(side="right", padx=10)

    def copy_to_clip(self, text):
        pyperclip.copy(text)
    
    def process_pattern(self):
        try:
            total_needed = int(self.total_items_slider.get())
            group_size = int(self.group_size_slider.get())
            template = self.template_entry.get()
            sep_setting = self.separator_entry.get()
            
            # Handle escape sequences for separator
            separator = sep_setting.replace("\\n", "\n").replace("\\t", "\t")

            if len(self.clipboard_history) < total_needed:
                self.status_label.configure(text="Not enough history!", text_color="red")
                self.after(2000, lambda: self.status_label.configure(text=""))
                return

            recent_items = self.clipboard_history[:total_needed]
            chronological_items = recent_items[::-1] # Now [Oldest ... Newest] of the batch

            formatted_groups = []
            
            # Pad chronological_items if not divisible by group_size?
            # Or just ignore leftover? User probably knows what they are doing.
            # But let's pad with empty strings just in case to avoid IndexError
            remainder = len(chronological_items) % group_size
            if remainder != 0:
                for _ in range(group_size - remainder):
                    chronological_items.append("")

            # Iterate in chunks of group_size
            for i in range(0, len(chronological_items), group_size):
                chunk = chronological_items[i:i + group_size]
                
                heading_pattern = template
                # Replace markers {1}, {2}, etc.
                for j, item in enumerate(chunk):
                    # Remove surrounding whitespace from the item itself? 
                    # Maybe keep it if the user wants space.
                    # But usually user expects clean text.
                    placeholder = f"{{{j+1}}}"
                    heading_pattern = heading_pattern.replace(placeholder, item.strip())
                
                formatted_groups.append(heading_pattern)
            
            final_output = separator.join(formatted_groups) 
            
            pyperclip.copy(final_output)
            self.status_label.configure(text="Copied Pattern!", text_color="green")
            self.after(3000, lambda: self.status_label.configure(text=""))
            
        except Exception as e:
            print(f"Error processing pattern: {e}")
            self.status_label.configure(text="Error!", text_color="red")

if __name__ == "__main__":
    app = ClipboardManager()
    app.mainloop()
