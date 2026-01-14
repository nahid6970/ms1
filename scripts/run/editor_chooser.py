import os
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
    elif editor == "antigravity":
        if isinstance(file_paths, list):
            for file_path in file_paths:
                subprocess.run(f'antigravity "{file_path}"', shell=True)
        else:
            subprocess.run(f'antigravity "{file_paths}"', shell=True)
    elif editor == "antigravity dir":
        # Open parent directory/directories with Antigravity
        if not isinstance(file_paths, list):
            file_paths = [file_paths]
        
        # Collect unique directories
        dirs_to_open = set()
        for fp in file_paths:
            if os.path.isfile(fp):
                dirs_to_open.add(os.path.dirname(fp))
            elif os.path.isdir(fp):
                dirs_to_open.add(fp)
                
        # Open each unique directory
        for d in dirs_to_open:
            subprocess.run(f'antigravity "{d}"', shell=True)
    elif editor == "chrome":
        if isinstance(file_paths, list):
            for file_path in file_paths:
                subprocess.run(f'start chrome "{file_path}"', shell=True)
        else:
            subprocess.run(f'start chrome "{file_paths}"', shell=True)
    elif editor == "photos":
        if isinstance(file_paths, list):
            for file_path in file_paths:
                # Use the 'ms-photos:' protocol to force it to open in the Photos app
                subprocess.run(f'start ms-photos:viewer?fileName="{file_path}"', shell=True)
        else:
            subprocess.run(f'start ms-photos:viewer?fileName="{file_paths}"', shell=True)
    elif editor == "emacs":
        # Ensure HOME is set for Emacs to find config
        # Emacs on Windows often defaults to APPDATA for config if HOME is not set,
        # but if we are running from a context where HOME might be confused or unset,
        # we explicitly point it to APPDATA where the user's config likely resides.
        env = os.environ.copy()
        if 'APPDATA' in env:
             env['HOME'] = env['APPDATA']
        elif 'HOME' not in env:
             env['HOME'] = env['USERPROFILE']
        
        # Use runemacs for Windows GUI to avoid console and better env handling
        # Join arguments properly
        if isinstance(file_paths, list):
            files_args = ' '.join([f'"{fp}"' for fp in file_paths])
            subprocess.run(f'runemacs {files_args}', shell=True, env=env)
        else:
            subprocess.run(f'runemacs "{file_paths}"', shell=True, env=env)

def create_editor_chooser(file_paths):
    """Create a GUI window to choose editor"""
    # Normalize to list
    if not isinstance(file_paths, list):
        file_paths = [file_paths]
    
    editors = [
        ("nvim", "#19d600", ""),
        ("VSCode", "#7e96ff", ""),
        ("Emacs", "#8458b7", ""),
        ("Zed", "#ff6b6b", ""),
        ("Antigravity", "#00d9ff", ""),
        ("Antigravity Dir", "#00e6b8", ""),
    ]
    
    viewers = [
        ("Chrome", "#f4c20d", ""),
        ("Photos", "#00a2ed", ""),
    ]
    
    all_rows = [editors, viewers]
    row_titles = ["Open as Editor:", "Open as Viewer:"]

    root = tk.Tk()
    root.title("Choose Action")
    root.configure(bg='#1e1e1e')
    
    # Remove window border and add custom border
    root.overrideredirect(True)
    
    # Center window
    # Calculate width based on max number of buttons in a row
    max_buttons = max(len(row) for row in all_rows)
    content_width = max_buttons * 140
    window_width = max(500, content_width + 60)
    
    window_height = 280 # Increased for two rows
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
    
    # Main Title
    title_font = tkfont.Font(family="Segoe UI", size=11, weight="bold")
    button_font = tkfont.Font(family="Segoe UI", size=11, weight="bold")
    file_count = len(file_paths)
    main_title_text = f"Choose action for {file_count} file{'s' if file_count > 1 else ''}"
    main_title = tk.Label(content_frame, text=main_title_text, font=title_font, bg='#1e1e1e', fg='#888888')
    main_title.pack(pady=(10, 5))
    
    # Track current selection (row, col)
    current_pos = [0, 0]
    button_grid = [] # List of lists of button components
    
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
        for r_idx, row in enumerate(button_grid):
            for c_idx, (btn_frame, label, name, color) in enumerate(row):
                if r_idx == current_pos[0] and c_idx == current_pos[1]:
                    # Focused button - larger
                    btn_frame.config(width=140, height=70, highlightthickness=2, highlightbackground='#ffffff')
                    label.config(font=tkfont.Font(family="Segoe UI", size=12, weight="bold"))
                else:
                    # Unfocused button - normal size
                    btn_frame.config(width=120, height=60, highlightthickness=0)
                    label.config(font=button_font)
    
    def on_key(event):
        """Handle arrow key navigation"""
        r, c = current_pos
        if event.keysym == 'Left':
            current_pos[1] = max(0, c - 1)
        elif event.keysym == 'Right':
            current_pos[1] = min(len(all_rows[r]) - 1, c + 1)
        elif event.keysym == 'Up':
            current_pos[0] = max(0, r - 1)
            # Ensure column index is valid in new row
            current_pos[1] = min(current_pos[1], len(all_rows[current_pos[0]]) - 1)
        elif event.keysym == 'Down':
            current_pos[0] = min(len(all_rows) - 1, r + 1)
            # Ensure column index is valid in new row
            current_pos[1] = min(current_pos[1], len(all_rows[current_pos[0]]) - 1)
        elif event.keysym == 'Return':
            # Enter key - select current button
            name, _, _ = all_rows[current_pos[0]][current_pos[1]]
            root.destroy()
            open_with_editor(file_paths, name.lower().replace("vscode", "vscode"))
            return

        update_focus()
    
    def create_button(parent, name, color, icon, r_idx, c_idx):
        def on_click():
            root.destroy()
            open_with_editor(file_paths, name.lower().replace("vscode", "vscode"))
        
        # Create frame for button
        btn_frame = tk.Frame(parent, bg=color, width=120, height=60, cursor='hand2')
        btn_frame.pack(side='left', padx=10)
        btn_frame.pack_propagate(False)
        
        # Create label inside frame
        display_text = f"{icon}\n{name}" if icon else name
        label = tk.Label(
            btn_frame,
            text=display_text,
            font=button_font,
            bg=color,
            fg='#000000',
            cursor='hand2',
            justify='center'
        )
        label.pack(expand=True)
        
        # Bind click events
        btn_frame.bind('<Button-1>', lambda e: on_click())
        label.bind('<Button-1>', lambda e: on_click())
        
        # Hover effect
        def on_enter(e):
            new_color = adjust_color(color, 1.2)
            btn_frame.config(bg=new_color)
            label.config(bg=new_color)
            # Update focus to this button
            current_pos[0], current_pos[1] = r_idx, c_idx
            update_focus()
        
        def on_leave(e):
            btn_frame.config(bg=color)
            label.config(bg=color)
        
        btn_frame.bind("<Enter>", on_enter)
        btn_frame.bind("<Leave>", on_leave)
        label.bind("<Enter>", on_enter)
        label.bind("<Leave>", on_leave)
        
        return (btn_frame, label, name, color)

    # Generate rows
    for r_idx, row_data in enumerate(all_rows):
        # Title for each row
        row_title_font = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        rtitle = tk.Label(content_frame, text=row_titles[r_idx], font=row_title_font, bg='#1e1e1e', fg='#ffffff')
        rtitle.pack(pady=(5, 0), anchor='w', padx=20)
        
        row_frame = tk.Frame(content_frame, bg='#1e1e1e')
        row_frame.pack(pady=5)
        
        btn_row = []
        for c_idx, (name, color, icon) in enumerate(row_data):
            comp = create_button(row_frame, name, color, icon, r_idx, c_idx)
            btn_row.append(comp)
        button_grid.append(btn_row)
    
    # Bind keys
    root.bind('<Left>', on_key)
    root.bind('<Right>', on_key)
    root.bind('<Up>', on_key)
    root.bind('<Down>', on_key)
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
