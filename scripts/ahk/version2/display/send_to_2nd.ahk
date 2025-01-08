#Requires AutoHotkey v2.0

    SendMode("Input")
    SetWorkingDir(A_ScriptDir)

    ; Get the handle of the active window
    hwnd := WinGetID("A")
    
    ; Check if the window title is "LDPlayer"
    windowTitle := WinGetTitle("ahk_id " hwnd)
    if (windowTitle != "LDPlayer") {
        MsgBox("This script only works for the application with the title `"LDPlayer`".")
        return
    }
    
    ; Get the position and size of the active window
    WinGetPos(&x, &y, &w, &h, "ahk_id " hwnd)
    
    ; Get the work area of the primary and secondary monitors
    MonitorGetWorkArea(1, &MonitorPrimaryLeft, &MonitorPrimaryTop, &MonitorPrimaryRight, &MonitorPrimaryBottom)
    MonitorGetWorkArea(2, &MonitorSecondaryLeft, &MonitorSecondaryTop, &MonitorSecondaryRight, &MonitorSecondaryBottom)
    
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
    WinMove(newX, newY, , , "ahk_id " hwnd)
