;;* ██████╗ ███╗   ██╗██████╗     ███╗   ███╗ ██████╗ ███╗   ██╗██╗████████╗ ██████╗ ██████╗
;;* ╚════██╗████╗  ██║██╔══██╗    ████╗ ████║██╔═══██╗████╗  ██║██║╚══██╔══╝██╔═══██╗██╔══██╗
;;*  █████╔╝██╔██╗ ██║██║  ██║    ██╔████╔██║██║   ██║██╔██╗ ██║██║   ██║   ██║   ██║██████╔╝
;;* ██╔═══╝ ██║╚██╗██║██║  ██║    ██║╚██╔╝██║██║   ██║██║╚██╗██║██║   ██║   ██║   ██║██╔══██╗
;;* ███████╗██║ ╚████║██████╔╝    ██║ ╚═╝ ██║╚██████╔╝██║ ╚████║██║   ██║   ╚██████╔╝██║  ██║
;;* ╚══════╝╚═╝  ╚═══╝╚═════╝     ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝

Send_to_2nd_Monitor() {
    ; Move all windows from the secondary monitor to the primary monitor
    #NoEnv
    SendMode Input
    SetWorkingDir %A_ScriptDir%

    ; Get the handle of the active window
    WinGet, hwnd, ID, A
    
    ; Check if the window title is "LDPlayer"
    WinGetTitle, windowTitle, ahk_id %hwnd%
    if (windowTitle != "LDPlayer") {
        MsgBox, This script only works for the application with the title "LDPlayer".
        return
    }
    
    ; Get the position and size of the active window
    WinGetPos, x, y, w, h, ahk_id %hwnd%
    
    ; Get the work area of the primary and secondary monitors
    SysGet, MonitorPrimary, MonitorWorkArea, 1
    SysGet, MonitorSecondary, MonitorWorkArea, 2
    
    ; Check if the window is on the primary monitor
    if (x >= MonitorPrimaryLeft and x < MonitorPrimaryRight and y >= MonitorPrimaryTop and y < MonitorPrimaryBottom) {
        ; Calculate the new position to center the window on the secondary monitor
        newX := MonitorSecondaryLeft + ((MonitorSecondaryRight - MonitorSecondaryLeft - w) / 2)
        newY := MonitorSecondaryTop + ((MonitorSecondaryBottom - MonitorSecondaryTop - h) / 2)
    } else {
        ; Calculate the new position to center the window on the primary monitor
        newX := MonitorPrimaryLeft + ((MonitorPrimaryRight - MonitorPrimaryLeft - w) / 2)
        newY := MonitorPrimaryTop + ((MonitorPrimaryBottom - MonitorPrimaryTop - h) / 2)
    }
    
    ; Move the window to the calculated position
    WinMove, ahk_id %hwnd%, , newX, newY
}

; ██████╗ ██╗      █████╗  ██████╗██╗  ██╗     ███████╗ ██████╗██████╗ ███████╗███████╗███╗   ██╗
; ██╔══██╗██║     ██╔══██╗██╔════╝██║ ██╔╝     ██╔════╝██╔════╝██╔══██╗██╔════╝██╔════╝████╗  ██║
; ██████╔╝██║     ███████║██║     █████╔╝█████╗███████╗██║     ██████╔╝█████╗  █████╗  ██╔██╗ ██║
; ██╔══██╗██║     ██╔══██║██║     ██╔═██╗╚════╝╚════██║██║     ██╔══██╗██╔══╝  ██╔══╝  ██║╚██╗██║
; ██████╔╝███████╗██║  ██║╚██████╗██║  ██╗     ███████║╚██████╗██║  ██║███████╗███████╗██║ ╚████║
; ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝     ╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═══╝

; Define a variable to track the state of the screen blackout
blackoutState := 0
; Define a function to toggle the screen blackout
Toggle_Screen_Blackout() {
    global blackoutState  ; Declare the variable as global so it can be accessed inside the function
    if (blackoutState = 0) {
        ; If the screen is not blacked out, create a black fullscreen window
        blackoutState := 1
        ; Get the height of the taskbar
        SysGet, taskbarHeight, 4, Shell_TrayWnd
        ; Create the black window to cover the entire screen
        Gui +LastFound +AlwaysOnTop -Caption +ToolWindow ; Remove caption and border
        Gui, Color, Black
        Gui, Show, w%A_ScreenWidth% h%A_ScreenHeight% x0 y0 NoActivate
    } else {
        ; If the screen is already blacked out, close the window
        blackoutState := 0
        Gui, Destroy
    }}

; ██████╗ ██╗███╗   ███╗      ███████╗ ██████╗██████╗ ███████╗███████╗███╗   ██╗
; ██╔══██╗██║████╗ ████║      ██╔════╝██╔════╝██╔══██╗██╔════╝██╔════╝████╗  ██║
; ██║  ██║██║██╔████╔██║█████╗███████╗██║     ██████╔╝█████╗  █████╗  ██╔██╗ ██║
; ██║  ██║██║██║╚██╔╝██║╚════╝╚════██║██║     ██╔══██╗██╔══╝  ██╔══╝  ██║╚██╗██║
; ██████╔╝██║██║ ╚═╝ ██║      ███████║╚██████╗██║  ██║███████╗███████╗██║ ╚████║
; ╚═════╝ ╚═╝╚═╝     ╚═╝      ╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═══╝

; Define a variable to track the state of the screen dimming
dimState := 0
; Define a function to toggle screen dimming
Toggle_Screen_Dim() {
    global dimState  ; Declare the variable as global so it can be accessed inside the function
    if (dimState = 0) {
        ; If the screen is not dimmed, create a semi-transparent black fullscreen window
        dimState := 1
        ; Create the dim window to cover the entire screen
        Gui +LastFound +AlwaysOnTop -Caption +ToolWindow -MinimizeBox -MaximizeBox ; Remove caption, border, and buttons
        Gui, Color, Black
        ; Set the window's transparency (255 is fully opaque, 0 is fully transparent)
        Gui, Add, Text, w%A_ScreenWidth% h%A_ScreenHeight% BackgroundBlack
        WinSet, Transparent, 128 ;! Adjust transparency (0-255)
        Gui, Show, w%A_ScreenWidth% h%A_ScreenHeight% x0 y0 NoActivate
        ; Allow mouse clicks and keyboard input to pass through
        WinSet, ExStyle, +0x20 ; WS_EX_TRANSPARENT
    } else {
        ; If the screen is already dimmed, close the window
        dimState := 0
        Gui, Destroy
    }
}

; ██╗    ██╗██╗  ██╗██╗████████╗███████╗    ███████╗ ██████╗██████╗ ███████╗███████╗███╗   ██╗
; ██║    ██║██║  ██║██║╚══██╔══╝██╔════╝    ██╔════╝██╔════╝██╔══██╗██╔════╝██╔════╝████╗  ██║
; ██║ █╗ ██║███████║██║   ██║   █████╗█████╗███████╗██║     ██████╔╝█████╗  █████╗  ██╔██╗ ██║
; ██║███╗██║██╔══██║██║   ██║   ██╔══╝╚════╝╚════██║██║     ██╔══██╗██╔══╝  ██╔══╝  ██║╚██╗██║
; ╚███╔███╔╝██║  ██║██║   ██║   ███████╗    ███████║╚██████╗██║  ██║███████╗███████╗██║ ╚████║
;  ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝   ╚═╝   ╚══════╝    ╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═══╝

; Define a variable to track the state of the screen Whiteout
whiteoutState := 0
; Define a function to toggle the screen Whiteout
Toggle_Screen_Whiteout() {
    global whiteoutState  ; Declare the variable as global so it can be accessed inside the function
    if (whiteoutState = 0) {
        ; If the screen is not Whiteed out, create a White fullscreen window
        whiteoutState := 1
        ; Get the height of the taskbar
        SysGet, taskbarHeight, 4, Shell_TrayWnd
        ; Create the White window to cover the entire screen
        Gui +LastFound +AlwaysOnTop -Caption +ToolWindow ; Remove caption and border
        
        ; Convert the RGB color #ffffff to BGR format
        color := 0xf6efb0  ; White color in RGB
        Gui, Color, %color%
        
        Gui, Show, w%A_ScreenWidth% h%A_ScreenHeight% x0 y0 NoActivate
    } else {
        ; If the screen is already Whiteed out, close the window
        whiteoutState := 0
        Gui, Destroy
    }
}