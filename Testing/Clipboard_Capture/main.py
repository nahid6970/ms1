import customtkinter as ctk
import pyperclip
import threading
import time
import re
import json
import os
import sys
from PIL import Image, ImageDraw
import pystray # pip install pystray

HISTORY_FILE = "clipboard_history.json"

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Settings")
        self.geometry("350x250")
        self.resizable(False, False)
        self.attributes('-topmost', True) # Keep settings on top too
        
        # Auto Mode Switch
        self.mode_switch = ctk.CTkSwitch(self, text="Auto-Pattern Mode", 
                                       variable=parent.auto_mode_var, command=parent.toggle_mode,
                                       font=ctk.CTkFont(size=14, weight="bold"))
        self.mode_switch.pack(pady=20, padx=20, anchor="w")

        # Template
        ctk.CTkLabel(self, text="Pattern Template ({1}, {2}...)").pack(pady=(10, 5), padx=20, anchor="w")
        self.template_entry = ctk.CTkEntry(self, width=300)
        self.template_entry.insert(0, parent.pattern_template)
        self.template_entry.pack(pady=5, padx=20)
        self.template_entry.bind("<KeyRelease>", self.on_template_change)

        # Dynamic Info
        self.group_info = ctk.CTkLabel(self, text=f"Detected Group Size: {parent.get_group_size()}", text_color="gray70")
        self.group_info.pack(pady=5, padx=20, anchor="w")
        
        ctk.CTkLabel(self, text="* Close to save settings", font=("Arial", 10), text_color="gray50").pack(side="bottom", pady=10)

    def on_template_change(self, event):
        self.parent.pattern_template = self.template_entry.get()
        size = self.parent.get_group_size()
        self.group_info.configure(text=f"Detected Group Size: {size}")
        self.parent.update_status()

class CompactClipboardApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SmartClip")
        self.geometry("320x450")
        self.resizable(False, True)
        ctk.set_appearance_mode("dark")
        # Start hidden? Usually tray apps do. But user said "launch from tray", maybe they want to see it first.
        # I'll let it show on start.
        
        # Data & State
        self.clipboard_history = []
        self.pattern_buffer = [] 
        self.accumulated_text = ""
        self.last_clip = ""
        self.auto_mode_var = ctk.BooleanVar(value=True) # Default On? Or Off. Let's start Off.
        self.pattern_template = "{1} -> **{2}**"
        self.ignore_next = None
        self.is_running = True

        # Load Data
        self.load_history()
        
        try:
            self.last_clip = pyperclip.paste()
        except: 
            pass

        # --- UI Construction ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 1. Top Bar (Status)
        self.top_frame = ctk.CTkFrame(self, height=40, fg_color="transparent")
        self.top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        
        self.status_label = ctk.CTkLabel(self.top_frame, text="Ready", font=ctk.CTkFont(size=14, weight="bold"), text_color="gray")
        self.status_label.pack(side="left")
        
        self.settings_btn = ctk.CTkButton(self.top_frame, text="⚙", width=30, height=30, command=self.open_settings)
        self.settings_btn.pack(side="right")

        # 2. Main Content (Output Preview)
        self.preview_box = ctk.CTkTextbox(self, font=("Consolas", 12), fg_color="#1f1f1f", text_color="#2ecc71")
        self.preview_box.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.preview_box.insert("0.0", "Accumulated pattern will appear here...")
        self.preview_box.configure(state="disabled")

        # 3. Action Buttons
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        self.btn_frame.grid_columnconfigure((0,1), weight=1)

        self.btn_copy = ctk.CTkButton(self.btn_frame, text="Copy Output", command=self.manual_copy, fg_color="#2ecc71", hover_color="#27ae60")
        self.btn_copy.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 5))

        self.btn_reset = ctk.CTkButton(self.btn_frame, text="Reset Session", command=self.reset_session, fg_color="#e67e22", hover_color="#d35400")
        self.btn_reset.grid(row=1, column=0, sticky="ew", padx=(0, 2))

        self.btn_clear_hist = ctk.CTkButton(self.btn_frame, text="Clear DB", command=self.clear_history, fg_color="#c0392b", hover_color="#922b21")
        self.btn_clear_hist.grid(row=1, column=1, sticky="ew", padx=(2, 0))

        # System Tray Setup
        self.protocol("WM_DELETE_WINDOW", self.hide_window)
        
        # Start Threads
        self.monitor_thread = threading.Thread(target=self.monitor_clipboard, daemon=True)
        self.monitor_thread.start()

        # Init Tray
        self.tray_thread = threading.Thread(target=self.setup_tray, daemon=True)
        self.tray_thread.start()
        
        self.update_status()
        
        # Ensure initial position is correct too
        self.after(100, self._show_window_safe)

    def create_image(self):
        # Generate a simple icon
        width = 64
        height = 64
        color1 = "#2ecc71"
        color2 = "#3498db"
        image = Image.new('RGB', (width, height), color1)
        dc = ImageDraw.Draw(image)
        dc.rectangle((width // 2, 0, width, height // 2), fill=color2)
        dc.rectangle((0, height // 2, width // 2, height), fill=color2)
        return image

    def setup_tray(self):
        # default=True makes the "Show" item trigger on left-click
        menu = pystray.Menu(
            pystray.MenuItem("Show", self.show_window, default=True),
            pystray.MenuItem("Exit", self.quit_app)
        )
        icon = pystray.Icon("SmartClip", self.create_image(), "SmartClip Manager", menu=menu)
        self.tray_icon = icon
        icon.run()

    def show_window(self, icon=None, item=None):
        # Triggers UI update from the tray thread, so schedule it on main thread
        self.after(0, self._show_window_safe)

    def _show_window_safe(self):
        self.deiconify()
        self.update_idletasks()
        try:
            self.lift()
            self.attributes('-topmost', True) # Keep on top
            self.focus_force()
        except: pass
        
        try:
            screen_w = self.winfo_screenwidth()
            screen_h = self.winfo_screenheight()
            win_w = 320
            win_h = 450
            
            # Position: Right side, Vertically centered
            x_pos = screen_w - win_w - 20
            y_pos = (screen_h - win_h) // 2
            
            self.geometry(f"{win_w}x{win_h}+{x_pos}+{y_pos}")
        except: pass

    def hide_window(self):
        self.withdraw()

    def quit_app(self, icon=None, item=None):
        self.is_running = False
        try:
            self.tray_icon.stop()
        except: pass
        # Clean exit on main thread
        self.after(0, self._quit_safe)

    def _quit_safe(self):
        self.quit()
        self.destroy()

    def open_settings(self):
        SettingsWindow(self)

    # --- Logic ---

    def toggle_mode(self):
        self.reset_session()
        self.update_status()

    def get_group_size(self):
        matches = re.findall(r'\{(\d+)\}', self.pattern_template)
        if matches:
            return max(1, max(map(int, matches)))
        return 1

    def update_status(self):
        # Header Status
        if self.auto_mode_var.get():
            req = self.get_group_size()
            curr = len(self.pattern_buffer)
            self.status_label.configure(text=f"Active: {curr}/{req} in buffer", text_color="#2ecc71")
        else:
            self.status_label.configure(text="Auto-Mode: OFF", text_color="gray")
        
        # Textbox
        self.preview_box.configure(state="normal")
        self.preview_box.delete("0.0", "end")
        if self.accumulated_text:
            self.preview_box.insert("0.0", self.accumulated_text)
        else:
            self.preview_box.insert("0.0", "(Waiting for input...)")
        self.preview_box.configure(state="disabled")

    def manual_copy(self):
        if self.accumulated_text:
            self.copy_to_clip(self.accumulated_text)

    def reset_session(self):
        self.pattern_buffer.clear()
        self.accumulated_text = ""
        self.update_status()

    def clear_history(self):
        self.clipboard_history.clear()
        self.save_history()
        # Update last_clip to current system clipboard so we don't re-import it immediately
        try:
            self.last_clip = pyperclip.paste()
        except: pass

    def copy_to_clip(self, text):
        self.ignore_next = text
        pyperclip.copy(text)

    # --- Persistence ---
    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    self.clipboard_history = json.load(f)
            except: self.clipboard_history = []
            
    def save_history(self):
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.clipboard_history, f, indent=4)
        except: pass

    # --- Monitor ---
    def monitor_clipboard(self):
        while self.is_running:
            try:
                curr_clip = pyperclip.paste()
                if curr_clip != self.last_clip and curr_clip.strip() != "":
                    
                    if self.ignore_next == curr_clip:
                        self.last_clip = curr_clip
                        self.ignore_next = None
                        time.sleep(0.5)
                        continue
                    
                    # Dedupe vs history[0]
                    if self.clipboard_history and self.clipboard_history[0] == curr_clip:
                        self.last_clip = curr_clip 
                        time.sleep(0.5)
                        continue

                    self.last_clip = curr_clip
                    self.clipboard_history.insert(0, curr_clip)
                    if len(self.clipboard_history) > 50: self.clipboard_history.pop()
                    self.save_history()

                    if self.auto_mode_var.get():
                        self.handle_auto_mode(curr_clip)
                        
            except: pass
            time.sleep(0.5)

    def handle_auto_mode(self, clip):
        self.pattern_buffer.append(clip)
        if len(self.pattern_buffer) >= self.get_group_size():
            # Process Buffer
            template = self.pattern_template
            line = template
            for i, item in enumerate(self.pattern_buffer):
                 line = line.replace(f"{{{i+1}}}", item.strip())
            
            if self.accumulated_text:
                self.accumulated_text += "\n" + line
            else:
                self.accumulated_text = line
            
            self.copy_to_clip(self.accumulated_text)
            self.pattern_buffer = []
        
        self.after(0, self.update_status)

if __name__ == "__main__":
    app = CompactClipboardApp()
    app.mainloop()
