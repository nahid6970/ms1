Replace_Dash_W_Space() {
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
    }





; Convert to Lowercase
Convert_Lowercase() {
    Gui, Destroy
    ClipboardBackup := ClipboardAll
    Clipboard := ""
    Send, ^c
    ClipWait, 1
    if ErrorLevel {
        MsgBox, No text selected or copying failed.
        Clipboard := ClipboardBackup
        return
    }
    ClipBoardContent := Clipboard
    ;* Convert to lowercase
    StringLower, ClipBoardContent, ClipBoardContent
    Clipboard := ClipBoardContent
    Send, ^v
    Clipboard := ClipboardBackup
    return
}





; Convert Text to Uppercase
Convert_Uppercase(){
    Gui, Destroy
    ClipboardBackup := ClipboardAll
    Clipboard := ""
    Send, ^c
    ClipWait, 1
    if ErrorLevel
    {
        MsgBox, No text selected or copying failed.
        return
    }
    ClipBoardContent := Clipboard
    ;* Convert to uppercase
    StringUpper, ClipBoardContent, ClipBoardContent
    Clipboard := ClipBoardContent
    Send, ^v
    Clipboard := ClipboardBackup
    return
    }





; Remove Duplicate Lines
Remove_Duplicate_Lines() {
    Gui, Destroy
    ClipboardBackup := ClipboardAll
    Clipboard := ""
    Send, ^c
    ClipWait, 1
    if ErrorLevel {
        MsgBox, No text selected or copying failed.
        Clipboard := ClipboardBackup
        return
    }
    ClipBoardContent := Clipboard
    ;* Remove duplicate lines
    Lines := []
    Loop, parse, ClipBoardContent, `n, `r
    {
        if !(Lines[A_LoopField]) {
            Lines[A_LoopField] := True
            Result .= A_LoopField . "`n"
        }
    }
    ClipBoardContent := Result
    Clipboard := ClipBoardContent
    Send, ^v
    Clipboard := ClipboardBackup
    return
}





; Replace Text from Selection
Replace_Matching_words_Selection(){
    ClipboardBackup := ClipboardAll
    Clipboard := ""
    Send, ^c
    ;* Wait for the clipboard to contain the copied text
    ClipWait, 1
    if ErrorLevel
    {
        MsgBox, No text selected or copying failed.
        return
    }
    ;* Get the clipboard content
    ClipBoardContent := Clipboard
    ;* Prompt user for the word to replace
    InputBox, OldWord, Replace Word, Enter the word to replace:
    if (ErrorLevel)
    {
        ;* User canceled the input box
        Clipboard := ClipboardBackup
        return
    }
    ;* Prompt user for the replacement word
    InputBox, NewWord, Replace Word, Enter the new word:
    if (ErrorLevel)
    {
        ;* User canceled the input box
        Clipboard := ClipboardBackup
        return
    }
    ;* Replace all occurrences of the old word with the new word
    StringReplace, ClipBoardContent, ClipBoardContent, %OldWord%, %NewWord%, All
    ;* Restore the clipboard content with the modified text
    Clipboard := ClipBoardContent
    ;* Paste the modified text
    Send, ^v
    ;* Restore the original clipboard content
    Clipboard := ClipboardBackup
    return
}





; Remove All Punctuation
Remove_All_Punctuation(){
    ClipboardBackup := ClipboardAll
    Clipboard := ""
    Send, ^c
    ClipWait, 1
    if ErrorLevel
    {
        MsgBox, No text selected or copying failed.
        return
    }
    ClipBoardContent := Clipboard
    ;* Remove punctuation
    StringReplace, ClipBoardContent, ClipBoardContent, `.,,`, All
    StringReplace, ClipBoardContent, ClipBoardContent, `;,`, All
    StringReplace, ClipBoardContent, ClipBoardContent, `:,`, All
    StringReplace, ClipBoardContent, ClipBoardContent, ``,`, All
    ;* Add more punctuation characters as needed
    Clipboard := ClipBoardContent
    Send, ^v
    Clipboard := ClipboardBackup
    return
}





; Function to Remove All Spaces from Selection
Remove_AllSpace_Selection() {
    ; Backup the clipboard
    ClipboardBackup := ClipboardAll
    ; Clear the clipboard
    Clipboard := ""
    ; Copy the selected text
    Send, ^c
    ; Wait for the clipboard to contain the copied text
    ClipWait, 1
    if ErrorLevel {
        MsgBox, No text selected or copying failed.
    } else {
        ; Get the clipboard content
        ClipBoardContent := Clipboard
        ; Replace all spaces with nothing
        StringReplace, ClipBoardContent, ClipBoardContent, %A_Space%, , All
        ; Restore the clipboard content with the modified text
        Clipboard := ClipBoardContent
        ; Paste the modified text
        Send, ^v
    }
    ; Restore the original clipboard content
    Clipboard := ClipboardBackup
    return
}
