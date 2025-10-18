import sys
import subprocess
import tkinter as tk
from tkinter import font as tkfont

def open_with_editor(file_paths, editor):
    """Open file(s) with selected editor"""
    if editor == "nvim":
        # Launch nvim in a new terminal window with all files in tabs
        if isinstance(file_paths, list):
            files_args = ' '.join([f'"{fp}"' for fp in file_paths])
            subprocess.run(f'start cmd /k nvim -p {files_args}', shell=True)
        else:
            subprocess.run(['start', 'cmd', '/k', 'nvim', file_paths], shell=True)
    elif editor == "vscode":
        if isinstance(file_paths, list):
            for file_path in file_paths:
                subprocess.run(f'code "{file_path}"', shell=True)
        else:
            subprocess.run(f'code "{file_paths}"', shell=True)
    elif editor == "zed":
        if isinstance(file_paths, list):
            for file_path in file_paths:
                subprocess.run(f'zed "{file_path}"', shell=True)
        else:
            subprocess.run(f'zed "{file_paths}"', shell=True)

def create_editor_chooser(file_paths):
    """Create a GUI window to choose editor"""
    # Normalize to list
    if not isinstance(file_paths, list):
        file_paths = [file_paths]
    
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
    file_count = len(file_paths)
    title_text = f"Open {file_count} file{'s' if file_count > 1 else ''} with:"
    title = tk.Label(content_frame, text=title_text, font=title_font, bg='#1e1e1e', fg='#ffffff')
    title.pack(pady=(15, 10))
    
    # Button frame
    button_frame = tk.Frame(content_frame, bg='#1e1e1e')
    button_frame.pack(pady=10)
    
    # Button style
    button_font = tkfont.Font(family="Segoe UI", size=11, weight="bold")
    
    editors = [
        ("nvim", "#19d600", ""),
        ("VSCode", "#7e96ff", ""),
        ("Zed", "#ff6b6b", ""),
    ]
    
    # Track current selection
    current_index = [1]  # Start with VSCode (middle button)
    buttons = []
    
    def adjust_color(hex_color, factor):
        """Lighten color by factor"""
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r = min(255, int(r * factor))
        g = min(255, int(g * factor))
        b = min(255, int(b * factor))
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def update_focus():
        """Update button sizes and appearance based on focus"""
        for i, (btn_frame, label, editor_name, color) in enumerate(buttons):
            if i == current_index[0]:
                # Focused button - larger
                btn_frame.config(width=140, height=70, highlightthickness=2, highlightbackground='#ffffff')
                label.config(font=tkfont.Font(family="Segoe UI", size=12, weight="bold"))
            else:
                # Unfocused button - normal size
                btn_frame.config(width=120, height=60, highlightthickness=0)
                label.config(font=button_font)
    
    def on_key(event):
        """Handle arrow key navigation"""
        if event.keysym == 'Left':
            current_index[0] = max(0, current_index[0] - 1)
            update_focus()
        elif event.keysym == 'Right':
            current_index[0] = min(len(editors) - 1, current_index[0] + 1)
            update_focus()
        elif event.keysym == 'Return':
            # Enter key - select current button
            editor_name = editors[current_index[0]][0]
            root.destroy()
            open_with_editor(file_paths, editor_name.lower().replace("vscode", "vscode"))
    
    def create_button(editor_name, color, icon, index):
        def on_click():
            root.destroy()
            open_with_editor(file_paths, editor_name.lower().replace("vscode", "vscode"))
        
        # Create frame for button
        btn_frame = tk.Frame(button_frame, bg=color, width=120, height=60, cursor='hand2')
        btn_frame.pack(side='left', padx=10)
        btn_frame.pack_propagate(False)
        
        # Create label inside frame for better centering
        display_text = f"{icon}\n{editor_name}" if icon else editor_name
        label = tk.Label(
            btn_frame,
            text=display_text,
            font=button_font,
            bg=color,
            fg='#000000',
            cursor='hand2',
            justify='center'
        )
        # Use pack with expand to truly center
        label.pack(expand=True)
        
        # Bind click events
        btn_frame.bind('<Button-1>', lambda e: on_click())
        label.bind('<Button-1>', lambda e: on_click())
        
        # Hover effect
        def on_enter(e):
            new_color = adjust_color(color, 1.2)
            btn_frame.config(bg=new_color)
            label.config(bg=new_color)
        
        def on_leave(e):
            btn_frame.config(bg=color)
            label.config(bg=color)
        
        btn_frame.bind("<Enter>", on_enter)
        btn_frame.bind("<Leave>", on_leave)
        label.bind("<Enter>", on_enter)
        label.bind("<Leave>", on_leave)
        
        # Store button reference
        buttons.append((btn_frame, label, editor_name, color))
    
    for i, (editor_name, color, icon) in enumerate(editors):
        create_button(editor_name, color, icon, i)
    
    # Bind arrow keys
    root.bind('<Left>', on_key)
    root.bind('<Right>', on_key)
    root.bind('<Return>', on_key)
    
    # Set initial focus
    update_focus()
    
    # ESC to close
    root.bind('<Escape>', lambda e: root.destroy())
    
    root.mainloop()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Accept multiple file paths as arguments
        file_paths = sys.argv[1:]
        create_editor_chooser(file_paths)
    else:
        print("Usage: python editor_chooser.py <file_path> [<file_path2> ...]")
