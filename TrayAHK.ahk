#Persistent ; Keeps the script running

; Set the tray icon to an emoji image (replace with the path to your emoji image)
Menu, Tray, Icon, C:\Users\nahid\OneDrive\Desktop\1f621.png

; Disable default tray menu items (Restore, Pause, etc.)
Menu, Tray, NoStandard

; Create a tray icon with a right-click menu
Menu, Tray, Add, Reset WorkSpace, Toggle_Reset_Workspace
Menu, Tray, Add, Exit, ExitScript

; Add a shortcut to the tray menu for easy access
Menu, Tray, Default, Exit ; Sets default menu item for left-click on tray icon

; Optional: Right-click on tray icon for menu
TrayIconShortcut:
    Return







; Function to exit the script when selected from tray menu
ExitScript:
    ExitApp

taskbarVisible := 1  ; 1 for visible, 0 for hidden
Toggle_Reset_Workspace() {
    global taskbarVisible
    ; Get the handle of the taskbar
    WinGet, taskbarHandle, ID, ahk_class Shell_TrayWnd
    if (taskbarVisible) {
        ; Hide the taskbar
        WinSet, ExStyle, +0x80, ahk_id %taskbarHandle%  ; WS_EX_TOOLWINDOW
        WinSet, ExStyle, +0x20, ahk_id %taskbarHandle%  ; WS_EX_TRANSPARENT
        WinSet, Style, -0x800000, ahk_id %taskbarHandle%  ; WS_DISABLED
        taskbarVisible := 0
    } else {
        ; Unhide the taskbar
        WinSet, Style, +0x800000, ahk_id %taskbarHandle%  ; WS_DISABLED
        WinSet, ExStyle, -0x80, ahk_id %taskbarHandle%  ; WS_EX_TOOLWINDOW
        WinSet, ExStyle, -0x20, ahk_id %taskbarHandle%  ; WS_EX_TRANSPARENT
        taskbarVisible := 1
    }
}