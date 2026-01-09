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

class ToolTip:
    def __init__(self, widget, text, delay=1000):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.id = None
        self.tw = None
        
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.delay, self.showtip)

    def unschedule(self):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    def showtip(self):
        if self.tw: return
        x, y, cx, cy = self.widget.bbox("insert") 
        x = x + self.widget.winfo_rootx() + 25
        y = y + self.widget.winfo_rooty() + 25
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry(f"+{x}+{y}")
        
        # Transparent-ish background? No, just standard tooltip look
        label = tk.Label(self.tw, text=self.text, justify='left',
                       background="#ffffe0", relief='solid', borderwidth=1,
                       font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        if self.tw:
            self.tw.destroy()
            self.tw = None

class CharEditDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, initial_char="", initial_desc=""):
        super().__init__(parent)
        self.title(title)
        self.geometry("320x240")
        self.resizable(False, False)
        self.result = None
        
        # Center relative to parent (manual calculation)
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - 160
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - 120
        self.geometry(f"+{x}+{y}")
        
        self.transient(parent)
        self.grab_set()
        self.configure(fg_color="#1d2027")
        
        # UI
        ctk.CTkLabel(self, text="Character:", font=("Segoe UI", 12), text_color="gray").pack(pady=(20, 5), padx=20, anchor="w")
        self.char_entry = ctk.CTkEntry(self, width=280, corner_radius=0, border_color="gray")
        self.char_entry.insert(0, initial_char)
        self.char_entry.pack(pady=0, padx=20)
        self.char_entry.focus()
        
        ctk.CTkLabel(self, text="Description (Tooltip):", font=("Segoe UI", 12), text_color="gray").pack(pady=(15, 5), padx=20, anchor="w")
        self.desc_entry = ctk.CTkEntry(self, width=280, corner_radius=0, border_color="gray")
        self.desc_entry.insert(0, initial_desc)
        self.desc_entry.pack(pady=0, padx=20)
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20, padx=20, fill="x")
        
        ctk.CTkButton(btn_frame, text="Cancel", fg_color="transparent", border_width=1, border_color="gray",
                      command=self.cancel, width=100, corner_radius=0).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_frame, text="Save", fg_color="#10b153", hover_color="#0e9646",
                      command=self.save, width=100, corner_radius=0).pack(side="right")

        self.bind("<Return>", lambda e: self.save())
        self.bind("<Escape>", lambda e: self.cancel())
        
        self.wait_window(self)

    def save(self):
        self.result = (self.char_entry.get(), self.desc_entry.get())
        self.destroy()

    def cancel(self):
        self.destroy()

class SpecialCharPicker(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Special Character Picker")
        self.geometry("700x600")
        
        # Migration and Loading
        self.data = self.load_data()
        self.current_category = None
        self.current_hover_card = None

        # Determine initial category
        if self.data:
            self.current_category = list(self.data.keys())[0]
        else:
            self.data = {"General": []}
            self.current_category = "General"

        # UI Layout
        self.setup_ui()
        self.refresh_full_ui()

    def get_char_text(self, item):
        if isinstance(item, dict):
            return item.get("char", "?")
        return str(item)

    def get_char_desc(self, item):
        if isinstance(item, dict):
            return item.get("desc", "")
        return ""

    def load_data(self):
        default_data = {
            "Favorites": ["★", "✓", "✗", "❤", "•"],
            "Currency": ["€", "£", "¥", "৳", "₹", "₽"],
            "Math": ["≈", "≠", "≤", "≥", "÷", "×", "±", "∞"],
            "Arrows": ["←", "↑", "→", "↓", "↔", "▲", "▼"],
            "Latin/Greek": ["ø", "æ", "å", "ß", "Ω", "π", "µ"],
            "Bangla": ["ঁ", "ং", "ঃ", "অ", "আ", "ই", "ঈ"],
            "Misc": ["©", "®", "™", "…", "§"]
        }

        if not os.path.exists(CONFIG_FILE):
            self.cols = 5
            return default_data

        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                content = json.load(f)
                
            # Migration: List -> Dict
            if isinstance(content, list):
                self.cols = 5
                return {"General": content}
            
            # Retrieve as Dict
            if isinstance(content, dict):
                # Extract settings if present
                if "_settings" in content:
                    self.cols = content["_settings"].get("cols", 5)
                else:
                    self.cols = 5
                return content
                
            self.cols = 5
            return default_data

        except Exception as e:
            print(f"Error loading config: {e}")
            self.cols = 5
            return default_data

    def save_data(self):
        try:
            # Update settings in data
            self.data["_settings"] = {"cols": self.cols}
            
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def setup_ui(self):
        # --- Top Header ---
        self.header_frame = ctk.CTkFrame(self, height=50, corner_radius=0, fg_color="#1d2027")
        self.header_frame.pack(fill="x")
        
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="CharPicker", 
            font=("Segoe UI", 18, "bold"),
            text_color="white"
        )
        self.title_label.pack(side="left", padx=20, pady=10)

        # Global Add Button (Adds to current Category)
        self.add_btn = ctk.CTkButton(
            self.header_frame, 
            text="+ Add Char", 
            width=100, 
            height=30,
            fg_color="#10b153", 
            hover_color="#0e9646",
            corner_radius=0,
            command=self.add_new_char
        )
        self.add_btn.pack(side="right", padx=20, pady=10)

        # Column Config
        self.col_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.col_frame.pack(side="right", padx=(0, 10))
        
        ctk.CTkLabel(self.col_frame, text="Cols:", text_color="gray", font=("Segoe UI", 12)).pack(side="left", padx=(0, 5))
        self.col_option = ctk.CTkComboBox(
            self.col_frame,
            width=60,
            height=28,
            corner_radius=0,
            values=[str(i) for i in range(3, 13)],
            command=self.change_cols
        )
        self.col_option.set(str(self.cols))
        self.col_option.pack(side="left")

        # --- Main Body (Split View) ---
        self.body_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.body_frame.pack(fill="both", expand=True)

        # 1. Left Sidebar (Categories)
        self.sidebar = ctk.CTkScrollableFrame(
            self.body_frame, 
            width=100, # Initial small width
            corner_radius=0, 
            fg_color="#21252b",
            scrollbar_button_color="#21252b",   # Hide Scrollbar (match bg)
            scrollbar_button_hover_color="#21252b"
        )
        self.sidebar.pack(side="left", fill="y")
        
        # Category Buttons Container is self.sidebar itself

        # 2. Right Content (Grid)
        self.content_area = ctk.CTkFrame(self.body_frame, fg_color="transparent")
        self.content_area.pack(side="right", fill="both", expand=True)

        # Top Bar of Content (Category Info)
        self.cat_header = ctk.CTkFrame(self.content_area, height=40, fg_color="transparent")
        self.cat_header.pack(fill="x", padx=20, pady=(20, 0))
        
        self.current_cat_label = ctk.CTkLabel(self.cat_header, text="General", font=("Segoe UI", 20, "bold"))
        self.current_cat_label.pack(side="left")

        # Hint
        ctk.CTkLabel(self.cat_header, text="(Right-click to Copy/Delete)", text_color="gray").pack(side="right", anchor="s")

        # Scrollable Grid
        self.grid_frame = ctk.CTkScrollableFrame(
            self.content_area, 
            fg_color="transparent",
            scrollbar_button_color="#2b2b2b",  # Minimal visibility or transparent
            scrollbar_button_hover_color="#3a3f4b"
        )
        self.grid_frame._scrollbar.configure(width=0)
        self.grid_frame.configure(scrollbar_button_color=self.cget("fg_color"), scrollbar_button_hover_color=self.cget("fg_color"))
        
        self.grid_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Grid Cols Setup
        self.setup_grid_cols()

    def setup_grid_cols(self):
        # Reset column weights
        for i in range(20): # clear old ones roughly
            self.grid_frame.grid_columnconfigure(i, weight=0)
            
        for i in range(self.cols):
            self.grid_frame.grid_columnconfigure(i, weight=1)

    def change_cols(self, value):
        try:
            self.cols = int(value)
            self.setup_grid_cols()
            self.refresh_grid()
            self.save_data()
        except ValueError:
            pass

    def refresh_full_ui(self):
        self.refresh_sidebar()
        self.refresh_grid()

    def refresh_sidebar(self):
        # Calculate required width based on content
        max_name_len = 0
        from tkinter import font as tkfont
        # Note: ctk buttons use specific fonts, we use Segoe UI 12 as a safe measure
        f = tkfont.Font(family="Segoe UI", size=12)
        
        # Measure all category names
        for cat in self.data.keys():
            if cat == "_settings": continue
            w = f.measure(cat)
            if w > max_name_len:
                max_name_len = w
        
        # Super tight width calculation
        sidebar_width = max(90, max_name_len + 30) 
        self.sidebar.configure(width=sidebar_width)

        # Clear sidebar entirely (everything inside is destroyable now)
        for widget in self.sidebar.winfo_children():
            widget.destroy()

        # Sidebar Header (Smaller)
        ctk.CTkLabel(self.sidebar, text="LIST", font=("Segoe UI", 10, "bold"), text_color="gray").pack(pady=(10, 5), padx=10, anchor="w")

        # List Categories
        for cat in self.data.keys():
            if cat == "_settings": continue # Skip settings key
            
            is_active = (cat == self.current_category)
            fg = "#2b2f38" if not is_active else "#10b153"
            hover = "#3a3f4b" if not is_active else "#10b153"
            
            btn = ctk.CTkButton(
                self.sidebar,
                text=cat,
                fg_color=fg,
                hover_color=hover,
                corner_radius=0,
                height=30,  # Slightly shorter buttons
                anchor="w",
                font=("Segoe UI", 12),
                command=lambda c=cat: self.switch_category(c)
            )
            btn.pack(fill="x", padx=5, pady=1) # tighter padding
            
            # Context Menu for Category (Rename/Delete)
            btn.bind("<Button-3>", lambda e, c=cat: self.show_category_context(e, c))

        # New Category Button
        sep = ctk.CTkFrame(self.sidebar, height=1, fg_color="#2b2b2b")
        sep.pack(fill="x", padx=8, pady=8)

        new_btn = ctk.CTkButton(
            self.sidebar,
            text="+ New",
            fg_color="transparent",
            border_width=1,
            border_color="gray",
            text_color="gray",
            hover_color="#2b2f38",
            corner_radius=0,
            height=28,
            font=("Segoe UI", 11),
            command=self.add_category
        )
        new_btn.pack(fill="x", padx=5, pady=(0, 20))

    def switch_category(self, cat):
        self.current_category = cat
        self.refresh_sidebar() # to update highlights
        self.refresh_grid()

    def refresh_grid(self):
        # Update Header
        self.current_cat_label.configure(text=self.current_category)

        # Clear Grid
        self.current_hover_card = None
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        # Get items
        items = self.data.get(self.current_category, [])

        if not items:
            ctk.CTkLabel(self.grid_frame, text="No characters yet.", text_color="gray").pack(pady=50)
            return

        for idx, item in enumerate(items):
            row = idx // self.cols
            col = idx % self.cols
            
            char_text = self.get_char_text(item)
            char_desc = self.get_char_desc(item)

            # Card
            card = ctk.CTkFrame(self.grid_frame, corner_radius=0, fg_color="#2b2f38")
            card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            card.char_index = idx  # Store index for drag-drop
            
            # Label
            lbl = ctk.CTkLabel(card, text=char_text, font=("Nirmala UI", 32), text_color="white")
            lbl.pack(expand=True, pady=15, padx=15)
            
            # ToolTip
            if char_desc:
                ToolTip(card, char_desc, delay=1000)
                ToolTip(lbl, char_desc, delay=1000)

            # Hover Logic (Singleton)
            def on_enter(e, c=card):
                if self.current_hover_card and self.current_hover_card != c:
                    try: self.current_hover_card.configure(fg_color="#2b2f38", border_width=0)
                    except: pass
                
                c.configure(fg_color="#3a3f4b", border_width=1, border_color="#10b153")
                self.current_hover_card = c

            # Mouse wheel scrolling often causes "Leave" events, handle gracefully
            def on_leave(e, c=card):
                x, y = c.winfo_pointerxy()
                widget_x = c.winfo_rootx()
                widget_y = c.winfo_rooty()
                # If truly outside
                if not (widget_x <= x <= widget_x + c.winfo_width() and 
                        widget_y <= y <= widget_y + c.winfo_height()):
                    c.configure(fg_color="#2b2f38", border_width=0)
                    if self.current_hover_card == c:
                        self.current_hover_card = None

            card.bind("<Enter>", on_enter)
            card.bind("<Leave>", on_leave)
            lbl.bind("<Enter>", on_enter)
            lbl.bind("<Leave>", on_leave)

            # Actions - Combined Drag & Click
            # Use Index to identify items
            card.bind("<Button-1>", lambda e, i=idx: self.start_drag(e, i))
            lbl.bind("<Button-1>", lambda e, i=idx: self.start_drag(e, i))
            
            card.bind("<B1-Motion>", self.do_drag)
            lbl.bind("<B1-Motion>", self.do_drag)
            
            card.bind("<ButtonRelease-1>", self.stop_drag)
            lbl.bind("<ButtonRelease-1>", self.stop_drag)

            # Right Click still works (pass full item)
            card.bind("<Button-3>", lambda e, i=item: self.show_char_context(e, i))
            lbl.bind("<Button-3>", lambda e, i=item: self.show_char_context(e, i))

    def copy_char(self, item):
        char_text = self.get_char_text(item)
        if pyperclip:
            pyperclip.copy(char_text)
        else:
            self.clipboard_clear()
            self.clipboard_append(char_text)
            self.update()
        self.show_toast(f"Copied: {char_text}")

    # --- Drag and Drop Sorting ---
    def start_drag(self, event, index):
        item = self.data[self.current_category][index]
        self.drag_data = {
            "index": index,
            "x": event.x_root,
            "y": event.y_root,
            "moved": False,
            "item": item,
            "display": self.get_char_text(item)
        }

    def do_drag(self, event):
        if not hasattr(self, "drag_data"): return
        
        dx = abs(event.x_root - self.drag_data["x"])
        dy = abs(event.y_root - self.drag_data["y"])
        
        # Threshold to differentiate between click (copy) and drag (move)
        if not self.drag_data["moved"] and (dx > 10 or dy > 10):
            self.drag_data["moved"] = True
            # Create a ghost label that follows the mouse
            self.ghost = ctk.CTkLabel(self, text=self.drag_data["display"], 
                                     font=("Nirmala UI", 32), fg_color="#3a3f4b")
            self.ghost.place(x=0, y=0)

        if self.drag_data["moved"]:
            # Ghost follows mouse with a small offset
            self.ghost.place(x=event.x_root - self.winfo_rootx() + 10, 
                             y=event.y_root - self.winfo_rooty() + 10)

    def stop_drag(self, event):
        if not hasattr(self, "drag_data"): return
        
        if not self.drag_data.get("moved"):
            # It was just a quick click, not a drag -> Perform Copy
            self.copy_char(self.drag_data["item"])
        else:
            # It was a drag -> Handle Reorder
            self.ghost.destroy()
            
            # Find which item we dropped over
            target_idx = self.find_drop_index(event.x_root, event.y_root)
            
            if target_idx is not None and target_idx != self.drag_data["index"]:
                items = self.data[self.current_category]
                char = items.pop(self.drag_data["index"])
                items.insert(target_idx, char)
                self.save_data()
                self.refresh_grid()
        
        del self.drag_data

    def find_drop_index(self, x_root, y_root):
        # Convert global mouse coords to grid_frame local coords
        lx = x_root - self.grid_frame.winfo_rootx()
        ly = y_root - self.grid_frame.winfo_rooty()
        
        # Iterate children and check where the mouse landed
        for widget in self.grid_frame.winfo_children():
            if hasattr(widget, "char_index"):
                wx = widget.winfo_x()
                wy = widget.winfo_y()
                ww = widget.winfo_width()
                wh = widget.winfo_height()
                
                # Check if mouse is within card bounds
                if wx <= lx <= wx + ww and wy <= ly <= wy + wh:
                    return widget.char_index
        return None

    def show_toast(self, message):
        self.title(f"{message}   ✔")
        self.after(1500, lambda: self.title("Special Character Picker"))

    # --- Management ---
    def add_category(self):
        name = simpledialog.askstring("New Category", "Enter category name:")
        if name:
            name = name.strip()
            if name and name not in self.data:
                self.data[name] = []
                self.current_category = name
                self.save_data()
                self.refresh_full_ui()
            elif name in self.data:
                messagebox.showerror("Error", "Category already exists.")

    def add_new_char(self):
         if not self.current_category:
             return
         
         # Use custom dialog for adding
         dialog = CharEditDialog(self, f"Add to '{self.current_category}'")
         if not dialog.result: return # Cancelled
         
         char_text, char_desc = dialog.result
         char_text = char_text.strip()
         char_desc = char_desc.strip()
         
         if not char_text: return

         # Construct new item
         if char_desc:
             new_item = {"char": char_text, "desc": char_desc}
         else:
             new_item = char_text
             
         # Check duplicates? (optional, but good practice)
         # Using display text to check existence might be tricky if mixed, 
         # but let's check against existing items in a smart way.
         existing_texts = [self.get_char_text(i) for i in self.data[self.current_category]]
         if char_text in existing_texts:
             messagebox.showwarning("Duplicate", f"Character '{char_text}' already exists in this category.")
             return

         self.data[self.current_category].append(new_item)
         self.save_data()
         self.refresh_grid()

    # --- Context Menus ---
    def show_char_context(self, event, item):
        char_text = self.get_char_text(item)
        menu = tk.Menu(self, tearoff=0, bg="#2b2f38", fg="white", activebackground="#10b153", bd=0)
        menu.add_command(label=f"Copy '{char_text}'", command=lambda: self.copy_char(item))
        menu.add_separator()
        menu.add_command(label="Edit Character", command=lambda: self.edit_char(item))
        menu.add_command(label="Delete", command=lambda: self.delete_char(item))
        
        # Move to another category
        menu.add_separator()
        move_menu = tk.Menu(menu, tearoff=0, bg="#2b2f38", fg="white", activebackground="#10b153", bd=0)
        for cat in self.data.keys():
            # Skip current category AND the internal _settings key
            if cat != self.current_category and cat != "_settings":
                move_menu.add_command(label=f"Move to {cat}", command=lambda c=item, t=cat: self.move_char(c, t))
        menu.add_cascade(label="Move to...", menu=move_menu)

        try: menu.tk_popup(event.x_root, event.y_root)
        finally: menu.grab_release()

    def show_category_context(self, event, cat):
        menu = tk.Menu(self, tearoff=0, bg="#2b2f38", fg="white", activebackground="#10b153", bd=0)
        menu.add_command(label=f"Rename Category", command=lambda: self.rename_category(cat))
        menu.add_separator()
        menu.add_command(label=f"Delete Category '{cat}'", command=lambda: self.delete_category(cat))
        
        try: menu.tk_popup(event.x_root, event.y_root)
        finally: menu.grab_release()

    def delete_char(self, item):
        char_text = self.get_char_text(item)
        if messagebox.askyesno("Delete", f"Delete '{char_text}' from {self.current_category}?"):
            if item in self.data[self.current_category]:
                self.data[self.current_category].remove(item)
                self.save_data()
                self.refresh_grid()

    def edit_char(self, old_item):
        old_text = self.get_char_text(old_item)
        old_desc = self.get_char_desc(old_item)
        
        # Use custom dialog
        dialog = CharEditDialog(self, "Edit Character", initial_char=old_text, initial_desc=old_desc)
        if not dialog.result: return # Cancelled
        
        new_text, new_desc = dialog.result
        new_text = new_text.strip()
        new_desc = new_desc.strip()
        
        if not new_text: return
        
        # Construct new item
        if new_desc:
            new_item = {"char": new_text, "desc": new_desc}
        else:
            new_item = new_text
            
        # Update
        idx = self.data[self.current_category].index(old_item)
        self.data[self.current_category][idx] = new_item
        self.save_data()
        self.refresh_grid()

    def rename_category(self, old_name):
        new_name = simpledialog.askstring("Rename Category", "Enter new name:", initialvalue=old_name)
        if new_name:
            new_name = new_name.strip()
            if new_name and new_name != old_name:
                if new_name in self.data:
                    messagebox.showerror("Error", "Category name already exists.")
                    return
                # Transfer data
                self.data[new_name] = self.data.pop(old_name)
                if self.current_category == old_name:
                    self.current_category = new_name
                self.save_data()
                self.refresh_full_ui()

    def move_char(self, item, target_cat):
        if item in self.data[self.current_category]:
            self.data[self.current_category].remove(item)
            self.data[target_cat].append(item)
            self.save_data()
            self.refresh_grid()
            self.show_toast(f"Moved to {target_cat}")

    def delete_category(self, cat):
        if messagebox.askyesno("Delete", f"Delete category '{cat}' and all its characters?"):
            del self.data[cat]
            if cat == self.current_category:
                # Switch to another available or create empty
                remaining = [k for k in self.data.keys() if k != "_settings"]
                if remaining:
                    self.current_category = remaining[0]
                else:
                    self.data["General"] = []
                    self.current_category = "General"
            self.save_data()
            self.refresh_full_ui()

if __name__ == "__main__":
    try:
        app = SpecialCharPicker()
        app.mainloop()
    except Exception as e:
        import traceback
        traceback.print_exc()
        input("Error occurred. Press Enter...")

