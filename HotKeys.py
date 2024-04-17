import argparse
import keyboard
import pygetwindow as gw
import time
import subprocess

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

    if args.action  =='remove_dup_lines'         :send_m_k       ("VisualStudioCode",["ctrl+k","alt+d"])
    elif args.action=='remove_from_selection'    :send_m_k       ("VisualStudioCode",["ctrl+h","alt+l"])
    elif args.action=='powertoys_color_picker'   :global_shortcut("win+shift+c"         )
    elif args.action=='powertoys_ruler'          :global_shortcut("win+shift+m"         )
    elif args.action=='powertoys_mouse_crosshair':global_shortcut("win+alt+p"           )
    elif args.action=='powertoys_TextExtract'    :global_shortcut("win+shift+t"         )
    elif args.action=='capture2text'             :global_shortcut("win+ctrl+alt+shift+q")



    else:
        print("Invalid action")

if __name__ == "__main__":
    main()




# def rclone_sync():
#     subprocess.Popen(["powershell", "start", "C:\\ms1\\sync.ps1"])

# def windows_terminal():
#     subprocess.Popen(["wt"])

# def powertoys_ruler():
#     pyautogui.hotkey('win', 'shift', 'm')

# def capture2text():
#     pyautogui.hotkey('win', 'ctrl', 'alt', 'shift', 'q')

# def stop_wsa():
#     subprocess.Popen(["powershell", "Stop-Process -Name WsaClient -Force"])