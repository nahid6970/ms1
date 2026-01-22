#Requires AutoHotkey v2.0

; Check if the active window is Windows Terminal with "Gemini" in the title
IsGeminiTerminal() {
    ; Get the active window's process name and title
    try {
        processName := WinGetProcessName("A")
        windowTitle := WinGetTitle("A")
        
        ; Check if it's Windows Terminal and has "Gemini" in the title
        if (processName = "WindowsTerminal.exe" && InStr(windowTitle, "Gemini")) {
            return true
        }
    }
    return false
}

; Only activate hotkeys when in Gemini terminal
#HotIf IsGeminiTerminal()

; Ctrl+S hotkey - Send "/chat save"
^s::
{
    SendText("/chat save")
}

; Ctrl+R hotkey - Send "/chat resume"  
^r::
{
    SendText("/chat resume")
}

#HotIf