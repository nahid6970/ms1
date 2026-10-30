#Requires AutoHotkey v2.0
MinimizeActiveWindow() {
    hwnd := WinExist("A")
    if !hwnd
        return

    ; Method 1: Standard system command (best for most apps + many games)
    PostMessage(0x0112, 0xF020, 0, , hwnd)   ; WM_SYSCOMMAND + SC_MINIMIZE

    ; Method 2: Direct ShowWindow call (helps stubborn windows)
    DllCall("ShowWindow", "Ptr", hwnd, "Int", 6)  ; SW_MINIMIZE = 6

    ; Method 3: Fallback to WinMinimize
    try WinMinimize("ahk_id " hwnd)
}
