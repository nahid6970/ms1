#Persistent ; Keeps the script running

; Set the tray icon to an emoji image (replace with the path to your emoji image)
Menu, Tray, Icon, C:\Users\nahid\OneDrive\Desktop\1f621.png

; Disable default tray menu items (Restore, Pause, etc.)
Menu, Tray, NoStandard

; Create a tray icon with a right-click menu
Menu, Tray, Add, Show Message, ShowMessage ; Menu item to trigger ShowMessage function
Menu, Tray, Add, Exit, ExitScript ; Menu item to exit the script

; Add a shortcut to the tray menu for easy access
Menu, Tray, Default, Show Message ; Sets default menu item for left-click on tray icon

; Function to show a message when selected from tray menu
ShowMessage:
    MsgBox, This is a message from your tray icon!
    Return

; Function to exit the script when selected from tray menu
ExitScript:
    ExitApp

; Optional: Right-click on tray icon for menu
TrayIconShortcut:
    Return
