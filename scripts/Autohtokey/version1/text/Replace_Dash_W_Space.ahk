#Requires AutoHotkey v1.0

    ; Backup the clipboard
    ClipboardBackup := ClipboardAll
    ; Clear the clipboard
    Clipboard := ""
    ; Copy the selected text
    Send, ^c
    ; Wait for the clipboard to contain the copied text
    ClipWait, 1
    if ErrorLevel
    {
        MsgBox, No text selected or copying failed.
    }
    else
    {
        ; Get the clipboard content
        ClipBoardContent := Clipboard
        ; Replace all hyphens with spaces
        StringReplace, ClipBoardContent, ClipBoardContent, -, %A_Space%, All
        ; Restore the clipboard content with the modified text
        Clipboard := ClipBoardContent
        ; Paste the modified text
        Send, ^v
    }
    ; Restore the original clipboard content
    Clipboard := ClipboardBackup
    return