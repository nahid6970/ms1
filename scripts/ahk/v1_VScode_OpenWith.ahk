#Requires AutoHotkey v1.0

    ; Backup current clipboard content
    ClipboardBackup := ClipboardAll
    ; Clear clipboard and copy the selected file path
    Clipboard := ""
    Send, ^c
    ClipWait 1
    if ErrorLevel
    {
        MsgBox, No valid file path found.
        ; Restore original clipboard content
        Clipboard := ClipboardBackup
        return
    }
    ClipBoardContent := Clipboard
    IfInString, ClipBoardContent, \
    {
        Run, "C:\Users\nahid\AppData\Local\Programs\Microsoft VS Code\Code.exe" "%ClipBoardContent%"
    }
    else
    {
        MsgBox, No valid file path found.
    }
    ; Restore original clipboard content
    Clipboard := ClipboardBackup