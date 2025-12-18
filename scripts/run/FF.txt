OpenWithEditor() {
    ; Backup current clipboard content
    ClipboardBackup := ClipboardAll()
    
    ; Clear clipboard and copy the selected file path
    A_Clipboard := ""
    Send("^c")
    
    if !ClipWait(1) {
        MsgBox("No valid file path found.")
        A_Clipboard := ClipboardBackup
        return
    }
    
    ClipBoardContent := A_Clipboard
    
    if InStr(ClipBoardContent, "\") {
        ; Handle multiple files (split by newline)
        FilePaths := ""
        Loop Parse, ClipBoardContent, "`n", "`r"
        {
            if (A_LoopField != "")
            {
                FilePaths .= '"' . A_LoopField . '" '
            }
        }
        
        if (FilePaths != "") {
            ; Call editor_chooser.py with all file paths
            Run('python "C:\Users\nahid\ms\ms1\scripts\run\editor_chooser.py" ' . FilePaths)
        }
    } else {
        MsgBox("No valid file path found.")
    }
    
    ; Restore original clipboard content
    A_Clipboard := ClipboardBackup
}