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

#! VSCode
    if args.action  =='remove_dup_lines'             :send_m_k  ("VisualStudioCode",["ctrl+k","alt+d"])
    elif args.action=='remove_from_selection'        :send_m_k  ("VisualStudioCode",["ctrl+h","alt+l"])
    elif args.action=='RemoveDupLines'               :send_m_k  ("VisualStudioCode",["ctrl+k","alt+d"])
    elif args.action=='RemoveFromSelection'          :send_m_k  ("VisualStudioCode",["ctrl+h","alt+l"])
    elif args.action=='AlignMultiCoulmnsbySeparator' :send_k    ("VisualStudioCode","alt+shift+semicolon" )
    elif args.action=='BookmarkLine'                 :send_k    ("VisualStudioCode","ctrl+b+ctrl+l"       )
    elif args.action=='BracketsGoTo'                 :send_k    ("VisualStudioCode","ctrl+shift+backslash")
    elif args.action=='BracketsRemove'               :send_k    ("VisualStudioCode","ctrl+alt+Backspace"  )
    elif args.action=='BracketsSelect'               :send_k    ("VisualStudioCode","ctrl+alt+right"      )
    elif args.action=='ChangeAllOccurrences'         :send_k    ("VisualStudioCode","CTRL+F2"             )
    elif args.action=='Comment'                      :send_k    ("VisualStudioCode","ctrl+k+c"            )
    elif args.action=='CommentSelection'             :send_k    ("VisualStudioCode","ALT+SHIFT+A"         )
    elif args.action=='DeleteLine'                   :send_k    ("VisualStudioCode","ctrl+shift+k"        )
    elif args.action=='ExpandSelectionquota_brackets':send_k    ("VisualStudioCode","shift+alt+right"     )
    elif args.action=='Keyboard_Shortcut'            :send_k    ("VisualStudioCode","CTRL+K+CTRL+S"       )
    elif args.action=='LineJoin'                     :send_k    ("VisualStudioCode","alt+j"               )
    elif args.action=='Minimap'                      :send_k    ("VisualStudioCode","ALT+m"               )
    elif args.action=='NewWindow'                    :send_k    ("VisualStudioCode","ctrl+n"              )
    elif args.action=='SelectNext'                   :send_k    ("VisualStudioCode","ctrl+d"              )
    elif args.action=='SelectPrevious'               :send_k    ("VisualStudioCode","ctrl+shift+d"        )
    elif args.action=='SortLinesAscending'           :send_k    ("VisualStudioCode","ALT+SHIFT+S"         )
    elif args.action=='SplitSameDocument'            :send_k    ("VisualStudioCode","CTRL+backslash"      )
    elif args.action=='TableFormatProperly'          :send_k    ("VisualStudioCode","CTRL+T+T"            )
    elif args.action=='TableFormatProperly2'         :send_k    ("VisualStudioCode","CTRL+q+f"            )
    elif args.action=='UnComment'                    :send_k    ("VisualStudioCode","ctrl+k+u"            )
#! Terminal
    elif args.action=='Terminal_Close' :send_k  (["Powershell","Command"],"Ctrl+Shift+W"        )
    elif args.action=='Terminal_SplitV':send_k  (["Powershell","Command"],"Alt+Shift+equal"     )
    elif args.action=='Terminal_SplitH':send_k  (["Powershell","Command"],"Alt+Shift+underscore")
#! Excel
    elif args.action=='Series'    :send_k  (["Excel"],"Alt,h,f,i,s")
    elif args.action=='Fit_Row'   :send_k  (["Excel"],"Alt,h,o,a"  )
    elif args.action=='Fit_Column':send_k  (["Excel"],"Alt,h,o,i"  )
 #! Global & launch
    elif args.action=='powertoys_color_picker'   :global_shortcut ("win+shift+c"         )
    elif args.action=='powertoys_ruler'          :global_shortcut ("win+shift+m"         )
    elif args.action=='powertoys_mouse_crosshair':global_shortcut ("win+alt+p"           )
    elif args.action=='powertoys_TextExtract'    :global_shortcut ("win+shift+t"         )
    elif args.action=='capture2text'             :global_shortcut ("win+ctrl+alt+shift+q")
    elif args.action=='x_mouse_enable'           :global_shortcut ("ctrl+alt+F1"         )
    elif args.action=='kill_process'             :subprocess.Popen(["powershell", "start-process", "C:/ms1/utility//kill_process.ps1", "-WindowStyle", "Normal"],shell=True)

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