import pyautogui
import pygetwindow as gw
import ctypes

def click_without_moving(x, y, window_title):
    # Find the window with the specified title
    window = gw.getWindowsWithTitle(window_title)
    
    if window:
        window = window[0]
        win_x, win_y = window.topleft
        win_width, win_height = window.size

        # Calculate the absolute screen coordinates
        abs_x = win_x + x
        abs_y = win_y + y

        # Save the current mouse position
        current_pos = pyautogui.position()

        # Perform the click at the desired location
        ctypes.windll.user32.SetCursorPos(abs_x, abs_y)
        pyautogui.click()
        
        # Restore the original mouse position
        ctypes.windll.user32.SetCursorPos(current_pos.x, current_pos.y)
    else:
        print(f"Window with title '{window_title}' not found.")

# Click at coordinates (1260, 228) within the "LDPlayer" window
click_without_moving(1260, 228, "LDPlayer")
