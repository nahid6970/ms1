import sys
import time
import tkinter as tk
import pygetwindow as gw
import pyautogui

def focus_terminal_and_esc():
    """Attempts to find the Gemini terminal window, focus it, and send ESC."""
    try:
        # Give a small delay for the window to settle
        time.sleep(0.5)
        titles = gw.getAllTitles()
        target_window = None
        
        # Priority 1: Window with 'Gemini' in title
        for title in titles:
            if "Gemini" in title and "File Explorer" not in title:
                target_window = gw.getWindowsWithTitle(title)[0]
                break
        
        # Priority 2: Common terminal titles
        if not target_window:
            for title in titles:
                if any(term in title for term in ["Windows PowerShell", "Command Prompt", "Terminal"]):
                    target_window = gw.getWindowsWithTitle(title)[0]
                    break
        
        if target_window:
            target_window.activate()
            # Wait for focus to be established
            time.sleep(0.2)
            pyautogui.press('esc')
    except Exception:
        pass # Silently fail if window manipulation fails

def show_notification(title, message, duration=5000):
    focus_terminal_and_esc()

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
    close_btn.bind("<Button-1>", lambda e: root.destroy())
    
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
        if alpha < 1.0 or y > y_target:
            next_alpha = min(alpha + 0.15, 1.0)
            next_y = max(y - 6, y_target)
            toast.attributes("-alpha", next_alpha)
            toast.geometry(f"{width}x{height}+{x}+{next_y}")
            toast.update()
            toast.after(15, lambda: animate_in(next_alpha, next_y))
        else:
            toast.after(duration, animate_out)
            
    # Slide down/fade out animation
    def animate_out(alpha=1.0):
        if alpha > 0.0:
            next_alpha = max(alpha - 0.15, 0.0)
            toast.attributes("-alpha", next_alpha)
            toast.update()
            toast.after(15, lambda: animate_out(next_alpha))
        else:
            root.destroy()
            
    # Start animation sequence
    toast.after(50, lambda: animate_in(0.01, y_start))
    root.mainloop()

if __name__ == "__main__":
    show_notification("Antigravity CLI", "Task completed successfully.")
