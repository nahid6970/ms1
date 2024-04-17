import argparse
import keyboard
import pygetwindow as gw
import time

def switch_to_frame(frame_to_show, frame_to_hide):
    frame_to_hide.pack_forget()
    frame_to_show.pack()

def send_k(window_titles, shortcut):
    for title in window_titles:
        try:
            app_window = gw.getWindowsWithTitle(title)[0]
            app_window.activate()  # Activate the window
            keyboard.send(shortcut)
            return  # Exit the loop if shortcut sent successfully
        except IndexError:
            pass  # If window title not found, try the next one

def send_m_k(window_title, shortcuts):
    app_window = gw.getWindowsWithTitle(window_title)[0]
    app_window.activate()  # Activate the window
    for shortcut in shortcuts:
        keyboard.send(shortcut)
        time.sleep(0.1)

def global_shortcut(shortcut):
    keyboard.send(shortcut, True, True)

def main():
    parser = argparse.ArgumentParser(description="Execute shortcuts from command line")
    parser.add_argument("action", type=str, help="Action to perform")
    args = parser.parse_args()

    if args.action   =='remove_dup_lines      ': send_m_k         ("Visual Studio Code"     ,["ctrl+k","alt+d"])
    elif args.action =='remove_from_selection ': send_m_k         ("Visual Studio Code"     ,["ctrl+h","alt+l"])
    elif args.action =='powertoys_color_picker': global_shortcut  ("win+shift+c")



    else:
        print("Invalid action")

if __name__ == "__main__":
    main()



# import argparse
# import subprocess
# import pyautogui
# from datetime import datetime
# import psutil

# def rclone_sync():
#     subprocess.Popen(["powershell", "start", "C:\\ms1\\sync.ps1"])

# def windows_terminal():
#     subprocess.Popen(["wt"])

# def powertoys_ruler():
#     pyautogui.hotkey('win', 'shift', 'm')

# def powertoys_color_picker():
#     pyautogui.hotkey('win', 'shift', 'c')

# def powertoys_TextExtract():
#     pyautogui.hotkey('win', 'shift', 't')

# def capture2text():
#     pyautogui.hotkey('win', 'ctrl', 'alt', 'shift', 'q')

# def powertoys_mouse_crosshair():
#     pyautogui.hotkey('win', 'alt', 'p')


# def vscode_comment():
#     for proc in psutil.process_iter():
#         if "ode.exe" in proc.name():
#             proc_pid = proc.pid
#             pyautogui.hotkey('alt', 'shift', 's')
#             break
#     else:
#         print("Visual Studio Code is not running.")

# def stop_wsa():
#     subprocess.Popen(["powershell", "Stop-Process -Name WsaClient -Force"])

# def main(args):
#     if args.action == 'rclone_sync':
#         rclone_sync()
#     elif args.action == 'windows_terminal':
#         windows_terminal()
#     elif args.action == 'powertoys_ruler':
#         powertoys_ruler()
#     elif args.action == 'powertoys_TextExtract':
#         powertoys_TextExtract()
#     elif args.action == 'capture2text':
#         capture2text()
#     elif args.action == 'powertoys_mouse_crosshair':
#         powertoys_mouse_crosshair()
#     elif args.action == 'stop_wsa':
#         stop_wsa()
#     elif args.action == 'powertoys_color_picker':
#         powertoys_color_picker()
#     elif args.action == 'vscode_comment':
#         vscode_comment()
#     else:
#         print("Invalid action")

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Utility Buttons Command Line Interface")
#     parser.add_argument("action", type=str, help="Action to perform")
#     args = parser.parse_args()
#     main(args)