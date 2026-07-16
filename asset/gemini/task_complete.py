import subprocess
import sys
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

def show_notification(title, message):
    focus_terminal_and_esc()

    # Native Windows Toast Notification script via PowerShell
    ps_script = f"""
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
    [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
    $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
    $toastXml = [Windows.Data.Xml.Dom.XmlDocument]::new()
    $toastXml.LoadXml($template.GetXml())
    $toastXml.GetElementsByTagName('text')[0].AppendChild($toastXml.CreateTextNode('{title}')) | Out-Null
    $toastXml.GetElementsByTagName('text')[1].AppendChild($toastXml.CreateTextNode('{message}')) | Out-Null
    $toast = [Windows.UI.Notifications.ToastNotification]::new($toastXml)
    [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('Antigravity').Show($toast)
    """
    
    try:
        subprocess.run(["powershell", "-Command", ps_script], capture_output=True, check=True)
    except Exception:
        # Fallback to a simple Tkinter window if PowerShell toast fails
        try:
            import tkinter as tk
            root = tk.Tk()
            root.overrideredirect(True)
            root.attributes("-topmost", True)
            root.configure(bg="#202020")
            
            # Layout size
            width = 320
            height = 75
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            x = screen_width - width - 20
            y = screen_height - height - 60
            root.geometry(f"{width}x{height}+{x}+{y}")
            
            tk.Label(root, text=title, font=("Segoe UI", 10, "bold"), fg="#FFFFFF", bg="#202020", anchor="w").pack(fill="x", padx=12, pady=(10, 2))
            tk.Label(root, text=message, font=("Segoe UI", 9), fg="#A0A0A0", bg="#202020", anchor="w").pack(fill="x", padx=12)
            
            root.after(3000, root.destroy)
            root.mainloop()
        except Exception:
            pass

if __name__ == "__main__":
    show_notification("Antigravity CLI", "Task completed successfully.")
