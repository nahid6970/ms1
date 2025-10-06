; AutoHotkey v2 Script - Language Switcher
; Runs once and exits - switches to next input language

#Requires AutoHotkey v2.0

; Switch language immediately on startup
SwitchInputLanguage()

; Exit the script after switching
ExitApp

; Function to switch input language
SwitchInputLanguage() {
    ; Get the current foreground window
    hwnd := WinGetID("A")
    
    ; Get current keyboard layout
    currentLayout := DllCall("GetKeyboardLayout", "UInt", DllCall("GetWindowThreadProcessId", "Ptr", hwnd, "Ptr", 0), "Ptr")
    
    ; Get list of all installed keyboard layouts
    layoutCount := DllCall("GetKeyboardLayoutList", "Int", 0, "Ptr", 0)
    
    if (layoutCount > 1) {
        ; Allocate memory for layout list
        layouts := Buffer(layoutCount * A_PtrSize)
        DllCall("GetKeyboardLayoutList", "Int", layoutCount, "Ptr", layouts.Ptr)
        
        ; Find current layout index
        currentIndex := -1
        Loop layoutCount {
            layout := NumGet(layouts, (A_Index - 1) * A_PtrSize, "Ptr")
            if (layout = currentLayout) {
                currentIndex := A_Index - 1
                break
            }
        }
        
        ; Calculate next layout index (cycle through)
        nextIndex := (currentIndex + 1) >= layoutCount ? 0 : currentIndex + 1
        nextLayout := NumGet(layouts, nextIndex * A_PtrSize, "Ptr")
        
        ; Switch to next layout
        PostMessage(0x50, 0, nextLayout, , "A")
        
        ; Optional: Show notification with current language
        ShowLanguageNotification(nextLayout)
    }
}

; Function to show language notification (optional)
ShowLanguageNotification(layout) {
    ; Get language name from layout
    langName := GetLanguageName(layout)
    
    ; Show tooltip for 1 second
    ToolTip("Language: " . langName)
    SetTimer(() => ToolTip(), -1000)
}

; Function to get language name from layout ID
GetLanguageName(layout) {
    ; Extract language ID (lower 16 bits)
    langID := layout & 0xFFFF
    
    ; Common language mappings
    languages := Map(
        0x0409, "English (US)",
        0x0809, "English (UK)",
        0x040C, "French",
        0x0407, "German",
        0x040A, "Spanish",
        0x0410, "Italian",
        0x0411, "Japanese",
        0x0412, "Korean",
        0x0804, "Chinese (Simplified)",
        0x0404, "Chinese (Traditional)",
        0x0419, "Russian",
        0x0416, "Portuguese (Brazil)",
        0x0413, "Dutch",
        0x041D, "Swedish",
        0x0414, "Norwegian",
        0x040E, "Hungarian",
        0x0415, "Polish",
        0x0405, "Czech",
        0x041F, "Turkish",
        0x0408, "Greek",
        0x040D, "Hebrew",
        0x0401, "Arabic"
    )
    
    return languages.Has(langID) ? languages[langID] : "Unknown (" . Format("0x{:04X}", langID) . ")"
}

; Optional: Show current language on startup
; Uncomment the line below if you want to see current language when script starts
; SetTimer(() => ShowLanguageNotification(DllCall("GetKeyboardLayout", "UInt", 0, "Ptr")), -500)