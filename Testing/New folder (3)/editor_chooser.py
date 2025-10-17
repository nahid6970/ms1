import sys
import subprocess
import tkinter as tk
from tkinter import font as tkfont

def open_with_editor(file_path, editor):
    """Open file with selected editor"""
    if editor == "nvim":
        subprocess.run(f'nvim "{file_path}"', shell=True)
    elif editor == "vscode":
        subprocess.run(f'code "{file_path}"', shell=True)
    elif editor == "zed":
        subprocess.run(f'zed "{file_path}"', shell=True)

def create_editor_chooser(file_path):
    """Create a GUI window to choose editor"""
    root = tk.Tk()
    root.title("Choose Editor")
    root.configure(bg='#1e1e1e')
    
    # Remove window border and add custom border
    root.overrideredirect(True)
    
    # Center window
    window_width = 500
    window_height = 150
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f'{window_width}x{window_height}+{x}+{y}')
    
    # Create border frame
    border_color = '#d782ff'
    border_frame = tk.Frame(root, bg=border_color, bd=0)
    border_frame.place(x=0, y=0, width=window_width, height=window_height)
    
    # Inner content frame
    content_frame = tk.Frame(border_frame, bg='#1e1e1e', bd=0)
    content_frame.place(x=2, y=2, width=window_width-4, height=window_height-4)
    
    # Title label
    title_font = tkfont.Font(family="Segoe UI", size=12, weight="bold")
    title = tk.Label(content_frame, text="Open with:", font=title_font, bg='#1e1e1e', fg='#ffffff')
    title.pack(pady=(15, 10))
    
    # Button frame
    button_frame = tk.Frame(content_frame, bg='#1e1e1e')
    button_frame.pack(pady=10)
    
    # Button style
    button_font = tkfont.Font(family="Segoe UI", size=11)
    
    editors = [
        ("nvim", "#19d600", ""),
        ("VSCode", "#7e96ff", ""),
        ("Zed", "#ff6b6b", ""),
    ]
    
    def create_button(editor_name, color, icon):
        def on_click():
            root.destroy()
            open_with_editor(file_path, editor_name.lower().replace("vscode", "vscode"))
        
        btn = tk.Button(
            button_frame,
            text=f"{icon}\n{editor_name}",
            font=button_font,
            bg=color,
            fg='#000000',
            activebackground=color,
            activeforeground='#000000',
            width=10,
            height=3,
            relief='flat',
            cursor='hand2',
            command=on_click,
            compound='center',
            justify='center'
        )
        btn.pack(side='left', padx=10)
        
        # Hover effect
        def on_enter(e):
            btn.config(bg=adjust_color(color, 1.2))
        
        def on_leave(e):
            btn.config(bg=color)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
    
    def adjust_color(hex_color, factor):
        """Lighten color by factor"""
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r = min(255, int(r * factor))
        g = min(255, int(g * factor))
        b = min(255, int(b * factor))
        return f'#{r:02x}{g:02x}{b:02x}'
    
    for editor_name, color, icon in editors:
        create_button(editor_name, color, icon)
    
    # ESC to close
    root.bind('<Escape>', lambda e: root.destroy())
    
    root.mainloop()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        create_editor_chooser(file_path)
    else:
        print("Usage: python editor_chooser.py <file_path>")
