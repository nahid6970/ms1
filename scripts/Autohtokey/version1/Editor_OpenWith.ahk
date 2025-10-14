#Requires AutoHotkey v2.0

; Configuration - Change this to switch editors easily
EDITOR := "nvim"  ; Options: "nvim", "vscode", "zed"

#t:: {
    OpenWithEditor()
}

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
        switch EDITOR {
            case "nvim":
                Run('wt.exe nvim "' . ClipBoardContent . '"')
            case "vscode":
                Run('"C:\Users\nahid\AppData\Local\Programs\Microsoft VS Code\Code.exe" "' . ClipBoardContent . '"')
            case "zed":
                Run('zed "' . ClipBoardContent . '"')
            default:
                MsgBox("Unknown editor: " . EDITOR)
        }
    } else {
        MsgBox("No valid file path found.")
    }
    
    ; Restore original clipboard content
    A_Clipboard := ClipboardBackup
}