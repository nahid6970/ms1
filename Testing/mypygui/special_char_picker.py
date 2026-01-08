import customtkinter as ctk
import tkinter as tk
from tkinter import simpledialog, messagebox
import json
import os
import sys

# Try to import pyperclip for better clipboard support
try:
    import pyperclip
except ImportError:
    pyperclip = None

# Set defaults
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "special_chars.json")

class SpecialCharPicker(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Special Character Picker")
        self.geometry("500x700")
        
        # Load Data
        self.chars = self.load_chars()

        # UI Layout
        self.setup_ui()
        self.refresh_grid()

    def load_chars(self):
        if not os.path.exists(CONFIG_FILE):
             # A preset of useful obscure characters + some Bangla examples
            return [
                "ø", "æ", "å", "ß", "€", "£", "¥", "©", "®", "™", 
                "•", "→", "←", "↑", "↓", "★", "✗", "✓", 
                "৳", "ঁ", "ং", "ঃ", "অ" 
            ]
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return []

    def save_chars(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.chars, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def setup_ui(self):
        # --- Header ---
        self.header_frame = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color="#1d2027")
        self.header_frame.pack(fill="x")
        
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="Character Picker", 
            font=("Segoe UI", 20, "bold"),
            text_color="white"
        )
        self.title_label.pack(side="left", padx=20, pady=15)

        # Add Button
        self.add_btn = ctk.CTkButton(
            self.header_frame, 
            text="+ Add Character", 
            width=120, 
            height=35,
            fg_color="#10b153", 
            hover_color="#0e9646",
            command=self.add_new_char
        )
        self.add_btn.pack(side="right", padx=20, pady=15)

        # Hint Label
        self.hint_label = ctk.CTkLabel(self, text="Right-click directly on a character to Copy", text_color="gray", font=("Segoe UI", 12))
        self.hint_label.pack(pady=(10, 0))

        # --- Grid Area ---
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Configure columns for responsive-like grid
        self.cols = 5
        for i in range(self.cols):
            self.scroll_frame.grid_columnconfigure(i, weight=1)

    def refresh_grid(self):
        # Clear existing stuff
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Populate grid
        for idx, char in enumerate(self.chars):
            row = idx // self.cols
            col = idx % self.cols
            
            # Card Container
            card = ctk.CTkFrame(self.scroll_frame, corner_radius=10, fg_color="#2b2f38")
            card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            # Character Label
            # Using Nirmala UI as it has good support for mixed scripts including Bangla
            lbl = ctk.CTkLabel(card, text=char, font=("Nirmala UI", 32), text_color="white")
            lbl.pack(expand=True, pady=15, padx=15)
            
            # Hover Effect
            card.bind("<Enter>", lambda e, c=card: c.configure(fg_color="#3a3f4b", border_width=1, border_color="#10b153"))
            card.bind("<Leave>", lambda e, c=card: c.configure(fg_color="#2b2f38", border_width=0))
            
            # Context Menu Bindings
            card.bind("<Button-3>", lambda e, c=char: self.show_context_menu(e, c))
            lbl.bind("<Button-3>", lambda e, c=char: self.show_context_menu(e, c))
            
            # Left Click to Copy (optional but handy)
            card.bind("<Button-1>", lambda e, c=char: self.copy_char(c))
            lbl.bind("<Button-1>", lambda e, c=char: self.copy_char(c))

    def show_context_menu(self, event, char):
        menu = tk.Menu(self, tearoff=0, bg="#2b2f38", fg="white", activebackground="#10b153", bd=0)
        menu.add_command(label=f"Copy  '{char}'", command=lambda: self.copy_char(char))
        menu.add_separator()
        menu.add_command(label="Delete", command=lambda: self.delete_char(char))
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def copy_char(self, char):
        # Use pyperclip if avaialble, else tkinter fallback
        if pyperclip:
            pyperclip.copy(char)
        else:
            self.clipboard_clear()
            self.clipboard_append(char)
            self.update() 
            
        # Flash visual feedback
        print(f"Copied: {char}")
        self.show_toast(f"Copied: {char}")

    def show_toast(self, message):
        # Simple toast using title update or popup
        orig_title = self.title()
        self.title(f"{message}   ✔")
        self.after(1500, lambda: self.title("Special Character Picker"))

    def add_new_char(self):
        # Custom input dialog style? defaulting to simpledialog for simplicity
        char = simpledialog.askstring("Add Character", "Paste your special character here:")
        if char:
            char = char.strip()
            if char and char not in self.chars:
                self.chars.append(char)
                self.save_chars()
                self.refresh_grid()
            elif char in self.chars:
                messagebox.showinfo("Exists", "This character is already in your list.")

    def delete_char(self, char):
        if messagebox.askyesno("Delete", f"Are you sure you want to delete '{char}'?"):
            if char in self.chars:
                self.chars.remove(char)
                self.save_chars()
                self.refresh_grid()

if __name__ == "__main__":
    app = SpecialCharPicker()
    app.mainloop()
