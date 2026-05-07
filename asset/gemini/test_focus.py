import pygetwindow as gw
import pyautogui
import time

def focus_gemini():
    # Try to find windows with 'Gemini' in title or common terminal names
    titles = gw.getAllTitles()
    print(f"Available windows: {titles}")
    
    target_window = None
    for title in titles:
        if "Gemini" in title:
            target_window = gw.getWindowsWithTitle(title)[0]
            break
    
    if not target_window:
        # Fallback to common terminal titles if Gemini isn't in the title
        for title in titles:
            if any(term in title for term in ["Windows PowerShell", "Command Prompt", "Terminal"]):
                target_window = gw.getWindowsWithTitle(title)[0]
                break

    if target_window:
        print(f"Found window: {target_window.title}")
        try:
            target_window.activate()
            time.sleep(0.5)
            pyautogui.press('esc')
            print("Sent ESC key")
        except Exception as e:
            print(f"Error activating window: {e}")
    else:
        print("Could not find Gemini or Terminal window")

if __name__ == "__main__":
    focus_gemini()
