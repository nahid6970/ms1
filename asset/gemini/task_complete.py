import datetime
import time
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

def main():
    focus_terminal_and_esc()
    
    # Format date and time: YYYY-MM-DD-HH:MM
    now_str = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M")
    
    try:
        with open(r"C:\Users\nahid\notification.txt", "w", encoding="utf-8") as f:
            f.write(now_str)
    except Exception as e:
        print(f"Failed to write notification file: {e}")

if __name__ == "__main__":
    main()
