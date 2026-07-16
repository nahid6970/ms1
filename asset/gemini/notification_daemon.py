import os
import time
import tkinter as tk

FILE_PATH = r"C:\Users\nahid\notification.txt"

def show_notification(title, message):
    root = tk.Tk()
    root.withdraw() # Hide main window
    
    # Create frameless top-level window
    toast = tk.Toplevel(root)
    toast.overrideredirect(True)
    toast.attributes("-topmost", True)
    toast.attributes("-alpha", 0.01) # Start transparent
    
    # Premium White Theme Colors
    BG_COLOR = "#FFFFFF"
    BORDER_COLOR = "#D2D0CE"
    TEXT_COLOR = "#201F1E"
    MUTED_TEXT = "#605E5C"
    ACCENT_COLOR = "#0078D4" # Enterprise Blue
    
    toast.configure(bg=BG_COLOR, highlightbackground=BORDER_COLOR, highlightcolor=BORDER_COLOR, highlightthickness=1)
    
    # Left accent colored strip
    accent = tk.Frame(toast, bg=ACCENT_COLOR, width=4)
    accent.pack(side="left", fill="y")
    
    # Content Container
    content = tk.Frame(toast, bg=BG_COLOR)
    content.pack(side="left", fill="both", expand=True, padx=12, pady=10)
    
    # Title Label
    title_lbl = tk.Label(
        content, 
        text=title, 
        font=("Segoe UI", 10, "bold"), 
        fg=TEXT_COLOR, 
        bg=BG_COLOR, 
        anchor="w"
    )
    title_lbl.pack(fill="x", pady=(0, 2))
    
    # Message Label
    msg_lbl = tk.Label(
        content, 
        text=message, 
        font=("Segoe UI", 9), 
        fg=MUTED_TEXT, 
        bg=BG_COLOR, 
        anchor="nw", 
        justify="left", 
        wraplength=250
    )
    msg_lbl.pack(fill="both", expand=True)
    
    # Close Button (X)
    close_btn = tk.Label(
        toast, 
        text="×", 
        font=("Segoe UI", 14), 
        fg=MUTED_TEXT, 
        bg=BG_COLOR, 
        cursor="hand2"
    )
    close_btn.pack(side="right", anchor="n", padx=(0, 8), pady=4)
    
    close_btn.bind("<Enter>", lambda e: close_btn.config(fg=TEXT_COLOR))
    close_btn.bind("<Leave>", lambda e: close_btn.config(fg=MUTED_TEXT))
    
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
        
    # Bind clicking anywhere on the toast (or close button) to dismiss it
    toast.bind("<Button-1>", lambda e: dismiss())
    accent.bind("<Button-1>", lambda e: dismiss())
    content.bind("<Button-1>", lambda e: dismiss())
    title_lbl.bind("<Button-1>", lambda e: dismiss())
    msg_lbl.bind("<Button-1>", lambda e: dismiss())
    close_btn.bind("<Button-1>", lambda e: dismiss())
    
    # Position calculations
    width = 320
    height = 75
    
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
            
    # Start animation sequence
    active_after_id = toast.after(50, lambda: animate_in(0.01, y_start))
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
