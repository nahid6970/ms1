import os
import time
import tkinter as tk

FILE_PATH = r"C:\Users\nahid\notification.txt"

# Gradient color sets for animation (matching task_complete.py)
GRADIENT_COLORS = [
    ("#FF6B6B", "#4ECDC4"),  # Red to Teal
    ("#667eea", "#764ba2"),  # Blue to Purple
    ("#f093fb", "#f5576c"),  # Pink to Red
    ("#4facfe", "#00f2fe"),  # Blue to Cyan
    ("#43e97b", "#38f9d7"),  # Green to Cyan
    ("#fa709a", "#fee140"),  # Pink to Yellow
    ("#a8edea", "#fed6e3"),  # Cyan to Pink
    ("#ff9a9e", "#fecfef"),  # Pink to Light Pink
]

def parse_hex(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def to_hex(rgb):
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

def interpolate_color(color1, color2, t):
    r1, g1, b1 = parse_hex(color1)
    r2, g2, b2 = parse_hex(color2)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return to_hex((r, g, b))

def get_text_color(bg_color):
    r, g, b = parse_hex(bg_color)
    brightness = (r * 0.299 + g * 0.587 + b * 0.114)
    return "#000000" if brightness > 128 else "#FFFFFF"

def ease_in_out_quad(t):
    return 2 * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 2 / 2

def show_notification(title, message):
    root = tk.Tk()
    root.withdraw() # Hide main window
    
    # Position calculations
    width = 320
    height = 75
    
    # Create frameless top-level window
    toast = tk.Toplevel(root)
    toast.overrideredirect(True)
    toast.attributes("-topmost", True)
    toast.attributes("-alpha", 0.01) # Start transparent
    
    BORDER_COLOR = "#313244"
    toast.configure(bg="#1E1E2E", highlightbackground=BORDER_COLOR, highlightcolor=BORDER_COLOR, highlightthickness=1)
    
    # Create Canvas to host custom drawn gradient background and transparent text
    canvas = tk.Canvas(toast, width=width, height=height, bd=0, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    
    # Pre-create text and button elements on the canvas
    title_id = canvas.create_text(
        16, 22, 
        text=title, 
        font=("Segoe UI", 10, "bold"), 
        fill="#FFFFFF", 
        anchor="w"
    )
    
    msg_id = canvas.create_text(
        16, 42, 
        text=message, 
        font=("Segoe UI", 9), 
        fill="#DDDDDD", 
        anchor="nw",
        width=260 # Wraps text nicely
    )
    
    close_btn_id = canvas.create_text(
        width - 14, 14, 
        text="×", 
        font=("Segoe UI", 14), 
        fill="#DDDDDD", 
        anchor="ne",
        tags="close_btn"
    )
    
    active_after_id = None
    
    # Function to dismiss the toast
    def dismiss():
        nonlocal active_after_id
        if active_after_id:
            try:
                toast.after_cancel(active_after_id)
            except Exception:
                pass
                
        def animate_out(alpha=1.0):
            nonlocal active_after_id
            if not toast.winfo_exists():
                return
            if alpha > 0.0:
                next_alpha = max(alpha - 0.15, 0.0)
                toast.attributes("-alpha", next_alpha)
                toast.update()
                active_after_id = toast.after(15, lambda: animate_out(next_alpha))
            else:
                try:
                    root.destroy()
                except Exception:
                    pass
        animate_out()
        
    # Bind clicking on the canvas or the close button to dismiss
    canvas.bind("<Button-1>", lambda e: dismiss())
    canvas.tag_bind("close_btn", "<Button-1>", lambda e: dismiss())
    
    # Close button hover effects
    canvas.tag_bind("close_btn", "<Enter>", lambda e: canvas.itemconfig(close_btn_id, font=("Segoe UI", 14, "bold")))
    canvas.tag_bind("close_btn", "<Leave>", lambda e: canvas.itemconfig(close_btn_id, font=("Segoe UI", 14)))
    
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    x = screen_width - width - 20
    y_target = screen_height - height - 60 # Sits above taskbar
    y_start = screen_height - height - 5 # Start slightly low
    
    toast.geometry(f"{width}x{height}+{x}+{y_start}")
    toast.deiconify()
    toast.lift()
    toast.focus_force()
    root.update_idletasks()
    
    # Slide up & Fade in animation
    def animate_in(alpha=0.01, y=y_start):
        nonlocal active_after_id
        if not toast.winfo_exists():
            return
        if alpha < 1.0 or y > y_target:
            next_alpha = min(alpha + 0.15, 1.0)
            next_y = max(y - 6, y_target)
            toast.attributes("-alpha", next_alpha)
            toast.geometry(f"{width}x{height}+{x}+{next_y}")
            toast.update()
            active_after_id = toast.after(15, lambda: animate_in(next_alpha, next_y))
            
    # Gradient background animation loop
    start_time = time.time()
    
    def update_gradient():
        if not toast.winfo_exists():
            return
            
        current_time = time.time()
        elapsed = current_time - start_time
        cycle_len = 3.7 # 2.5s hold + 1.2s transition
        
        cycle_num = int(elapsed // cycle_len)
        cycle_time = elapsed % cycle_len
        
        idx1 = cycle_num % len(GRADIENT_COLORS)
        idx2 = (cycle_num + 1) % len(GRADIENT_COLORS)
        
        if cycle_time < 2.5:
            color1, color2 = GRADIENT_COLORS[idx1]
        else:
            t = (cycle_time - 2.5) / 1.2
            progress = ease_in_out_quad(t)
            c1_start, c2_start = GRADIENT_COLORS[idx1]
            c1_end, c2_end = GRADIENT_COLORS[idx2]
            color1 = interpolate_color(c1_start, c1_end, progress)
            color2 = interpolate_color(c2_start, c2_end, progress)
            
        avg_color = interpolate_color(color1, color2, 0.5)
        text_color = get_text_color(avg_color)
        muted_text = "#333333" if text_color == "#000000" else "#DDDDDD"
        
        canvas.delete("gradient")
        step = 4
        for i in range(0, width, step):
            t_col = i / width
            col_c = interpolate_color(color1, color2, t_col)
            canvas.create_rectangle(i, 0, i + step, height, fill=col_c, outline=col_c, tags="gradient")
        canvas.tag_lower("gradient")
        
        canvas.itemconfig(title_id, fill=text_color)
        canvas.itemconfig(msg_id, fill=muted_text)
        canvas.itemconfig(close_btn_id, fill=muted_text)
        
        toast.after(30, update_gradient)
            
    # Start animation sequence
    active_after_id = toast.after(50, lambda: animate_in(0.01, y_start))
    update_gradient()
    root.mainloop()

def main():
    print(f"Monitoring {FILE_PATH} for changes...")
    
    # Initialize the notification file if it doesn't exist
    if not os.path.exists(FILE_PATH):
        try:
            with open(FILE_PATH, "w", encoding="utf-8") as f:
                f.write("")
        except Exception:
            pass

    # Read current content
    last_content = ""
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            last_content = f.read().strip()
    except Exception:
        pass

    while True:
        time.sleep(1)
        if os.path.exists(FILE_PATH):
            try:
                with open(FILE_PATH, "r", encoding="utf-8") as f:
                    current_content = f.read().strip()
                if current_content != last_content:
                    last_content = current_content
                    if current_content: # Only notify if content is not empty
                        show_notification("Task Completed", f"Finished at: {current_content}")
            except Exception as e:
                pass

if __name__ == "__main__":
    main()
