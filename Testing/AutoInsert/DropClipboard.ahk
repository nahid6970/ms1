#Requires AutoHotkey v2.0

/**
 * DropClipboard.ahk
 * Developed for Nahid
 * 
 * This script takes the current text in your clipboard, creates a temporary .txt file, 
 * and "drops" it wherever your mouse is positioned.
 * 
 * Features:
 * 1. Automatically creates a unique temp file from clipboard text.
 * 2. Sets clipboard to BOTH the file object and the file path string.
 * 3. Simulates a 'Drop' action at the current mouse position.
 * 4. Fallback: If the target doesn't accept files, it will paste the file path text instead.
 */

; --- Configuration ---
; Hotkey: Ctrl + Shift + D (You can change this to your preference)
^+d:: {
    DropClipboard()
}

DropClipboard() {
    ; 1. Get current text from clipboard
    clipText := A_Clipboard
    if (clipText == "") {
        ShowNotification("Clipboard is empty!", "Warning")
        return
    }

    ; 2. Create a temporary folder and file
    tempDir := A_Temp "\AutoInsert"
    if !DirExist(tempDir)
        DirCreate(tempDir)
    
    ; Create a unique filename using timestamp
    fileName := "clip_" A_Now "_" A_TickCount ".txt"
    filePath := tempDir "\" fileName
    
    try {
        ; Write clipboard content to the new file
        if FileExist(filePath)
            FileDelete(filePath)
        FileAppend(clipText, filePath)
    } catch Error as err {
        MsgBox("Failed to create temporary file:`n" err.Message)
        return
    }

    ; 3. Prepare the Clipboard for "Smart Drop"
    ; We set both File (CF_HDROP) and Text (CF_UNICODETEXT) formats.
    ; This allows Windows to decide: if it's a folder, drop the file; if it's a text field, paste the path.
    if !SetClipboardSmart(filePath) {
        MsgBox("Failed to set clipboard data.")
        return
    }

    ; 4. Perform the "Drop" action
    ; Get window and position under mouse
    MouseGetPos(&mX, &mY, &hWnd)
    
    ; Optional: Activate the window to ensure it receives the focus/paste
    try {
        WinActivate("ahk_id " hWnd)
    }
    
    ; Small click to focus the exact element under the mouse
    Click(mX, mY)
    Sleep(100) ; Wait for focus to settle
    
    ; Send Paste command
    Send("^v")

    ShowNotification("Dropped: " fileName "`n(File & Path ready)", "Success")
}

; --- Helper Functions ---

/**
 * Sets the clipboard to contain both the file object (for dropping into folders/apps)
 * and the file path string (for pasting into text fields).
 */
SetClipboardSmart(filePath) {
    if !DllCall("OpenClipboard", "ptr", A_ScriptHwnd)
        return false
    
    DllCall("EmptyClipboard")

    ; -- 1. Set CF_UNICODETEXT (Pasting path into text fields) --
    hText := DllCall("GlobalAlloc", "uint", 0x42, "ptr", (StrLen(filePath) + 1) * 2, "ptr")
    pText := DllCall("GlobalLock", "ptr", hText, "ptr")
    StrPut(filePath, pText, "UTF-16")
    DllCall("GlobalUnlock", "ptr", hText)
    DllCall("SetClipboardData", "uint", 13, "ptr", hText) ; 13 = CF_UNICODETEXT

    ; -- 2. Set CF_HDROP (Dropping file into folders/browser uploads) --
    ; DROPFILES structure is 20 bytes
    charCount := StrLen(filePath) + 2 ; +1 for null, +1 for double null (required for file lists)
    hDrop := DllCall("GlobalAlloc", "uint", 0x42, "ptr", 20 + (charCount * 2), "ptr")
    pDrop := DllCall("GlobalLock", "ptr", hDrop, "ptr")
    
    NumPut("uint", 20, pDrop, 0)   ; pFiles: offset to file list
    NumPut("uint", 1, pDrop, 16)  ; fWide: 1 means Unicode
    
    ; Copy path to the offset 20
    StrPut(filePath, pDrop + 20, "UTF-16")
    ; Double null termination (already handled by GlobalAlloc zero-init, but for safety:)
    NumPut("ushort", 0, pDrop + 20 + (StrLen(filePath) * 2), 0)
    
    DllCall("GlobalUnlock", "ptr", hDrop)
    DllCall("SetClipboardData", "uint", 15, "ptr", hDrop) ; 15 = CF_HDROP

    DllCall("CloseClipboard")
    return true
}

ShowNotification(msg, title := "") {
    ToolTip(title ? title ": " msg : msg)
    SetTimer(() => ToolTip(), -2500)
}
