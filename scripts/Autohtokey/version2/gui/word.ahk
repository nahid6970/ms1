WordToggleItalic() {
    if (!WinExist("ahk_exe WINWORD.EXE")) {
        ToolTip("Word not found!")
        SetTimer(() => ToolTip(), -1000)
        return
    }
    WinActivate("ahk_exe WINWORD.EXE")
    Sleep(200)
    Send("^i")
    ToolTip("Toggled Italic")
    SetTimer(() => ToolTip(), -800)
}

WordColorRed() {
    if (!WinExist("ahk_exe WINWORD.EXE")) {
        ToolTip("Word not found!")
        SetTimer(() => ToolTip(), -1000)
        return
    }
    WinActivate("ahk_exe WINWORD.EXE")
    Sleep(200)
    
    ; Open font color dropdown
    Send("!hfc")        ; Alt+H (Home) + FC (Font Color)
    Sleep(300)
    
    ; Search for red color #ee0000 and click it
    try {
        if (PixelSearch(&px, &py, 0, 0, A_ScreenWidth, A_ScreenHeight, 0xee0000, 3)) {
            Click(px, py)
            ToolTip("Applied: Red Color")
            SetTimer(() => ToolTip(), -800)
        } else {
            ; Fallback: use arrow keys
            Send("{Right}{Right}{Right}{Right}{Right}")
            Send("{Enter}")
            ToolTip("Applied: Red Color (fallback)")
            SetTimer(() => ToolTip(), -800)
        }
    } catch {
        ; If pixel search fails, use arrow navigation
        Send("{Right}{Right}{Right}{Right}{Right}")
        Send("{Enter}")
        ToolTip("Applied: Red Color (fallback)")
        SetTimer(() => ToolTip(), -800)
    }
}

WordColorGreen() {
    if (!WinExist("ahk_exe WINWORD.EXE")) {
        ToolTip("Word not found!")
        SetTimer(() => ToolTip(), -1000)
        return
    }
    WinActivate("ahk_exe WINWORD.EXE")
    Sleep(200)
    
    ; Open font color dropdown
    Send("!hfc")        ; Alt+H (Home) + FC (Font Color)
    Sleep(300)
    
    ; Search for green color #00b050 and click it
    try {
        if (PixelSearch(&px, &py, 0, 0, A_ScreenWidth, A_ScreenHeight, 0x00b050, 3)) {
            Click(px, py)
            ToolTip("Applied: Green Color")
            SetTimer(() => ToolTip(), -800)
        } else {
            ; Fallback: use arrow keys
            Send("{Right}{Right}{Right}{Right}{Right}{Right}{Right}{Right}")
            Send("{Enter}")
            ToolTip("Applied: Green Color (fallback)")
            SetTimer(() => ToolTip(), -800)
        }
    } catch {
        ; If pixel search fails, use arrow navigation
        Send("{Right}{Right}{Right}{Right}{Right}{Right}{Right}{Right}")
        Send("{Enter}")
        ToolTip("Applied: Green Color (fallback)")
        SetTimer(() => ToolTip(), -800)
    }
}#Requires AutoHotkey v2.0

myGui := Gui("+AlwaysOnTop -Caption +ToolWindow -SysMenu +Owner", "Control Panel")
myGui.SetFont("s12 Bold", "Jetbrainsmono nfp")
myGui.MarginX := 1
myGui.MarginY := 1

; Set icon font size and add vertically stacked icon buttons
myGui.SetFont("s20 Bold", "Jetbrainsmono nfp")

; Close (✕) and Reload (↻)
myGui.Add("Text", "xm y+5 Backgroundffffff cec2d47 w40 +Center", "󰅗").OnEvent("Click", (*) => ExitApp())
myGui.Add("Text", "xm y+5 Backgroundffffff c1E90FF w40 +Center", "󰜉").OnEvent("Click", (*) => Reload())

; === NEW WORD FORMATTING BUTTONS ===
; Add separator line
myGui.Add("Text", "xm y+10 Backgroundcccccc w40 h2", "")

; Normal text (remove formatting)
myGui.Add("Text", "xm y+5 Backgroundffffff c000000 w40 +Center", "N").OnEvent("Click", (*) => WordFormatNormal())

; Normal text but keep bullets
myGui.Add("Text", "xm y+5 Backgroundffffff c800080 w40 +Center", "N•").OnEvent("Click", (*) => WordFormatNormalKeepBullets())

; Title formatting
myGui.Add("Text", "xm y+5 Backgroundffffff c8B4513 w40 +Center", "T").OnEvent("Click", (*) => WordFormatTitle())

; Heading 1
myGui.Add("Text", "xm y+5 Backgroundffffff cDC143C w40 +Center", "H1").OnEvent("Click", (*) => WordFormatH1())

; Heading 2
myGui.Add("Text", "xm y+5 Backgroundffffff cFF6347 w40 +Center", "H2").OnEvent("Click", (*) => WordFormatH2())

; Heading 3
myGui.Add("Text", "xm y+5 Backgroundffffff c32CD32 w40 +Center", "H3").OnEvent("Click", (*) => WordFormatH3())

; Remove spacing (line spacing = single, no space before/after)
myGui.Add("Text", "xm y+5 Backgroundffffff c4169E1 w40 +Center", "SP").OnEvent("Click", (*) => WordRemoveSpacing())

; Bold toggle
myGui.Add("Text", "xm y+5 Backgroundffffff c000000 w40 +Center", "B").OnEvent("Click", (*) => WordToggleBold())

; Italic toggle
myGui.Add("Text", "xm y+5 Backgroundffffff c000000 w40 +Center", "I").OnEvent("Click", (*) => WordToggleItalic())

; Red text color
myGui.Add("Text", "xm y+5 Backgroundffffff cFF0000 w40 +Center", "R").OnEvent("Click", (*) => WordColorRed())

; Green text color
myGui.Add("Text", "xm y+5 Backgroundffffff c00FF00 w40 +Center", "G").OnEvent("Click", (*) => WordColorGreen())

; Show temporarily to calculate actual size
myGui.Show("x0 y0 AutoSize")
Sleep(10) ; brief pause to ensure size is updated
; Now get real size
myGui.GetClientPos(, , &w, &h)
screenW := 1920
screenH := 1080
x := screenW - w
y := (screenH - h) // 2
; Move to actual position
myGui.Move(x, y)

; === WORD FORMATTING FUNCTIONS ===
WordFormatNormal() {
    ; First activate Word if it exists
    if (!WinExist("ahk_exe WINWORD.EXE")) {
        ToolTip("Word not found!")
        SetTimer(() => ToolTip(), -1000)
        return
    }
    WinActivate("ahk_exe WINWORD.EXE")
    Sleep(200)  ; Wait for activation
    
    ; Multiple methods to ensure ALL formatting is removed
    Send("^{Space}")  ; Remove character formatting
    Sleep(50)
    Send("^q")        ; Remove paragraph formatting
    Sleep(50)
    Send("^+n")       ; Apply Normal style
    Sleep(50)
    Send("^+z")       ; Clear formatting (alternative)
    
    ToolTip("Applied: Normal (all formatting cleared)")
    SetTimer(() => ToolTip(), -800)
}

WordFormatTitle() {
    if (!WinExist("ahk_exe WINWORD.EXE")) {
        ToolTip("Word not found!")
        SetTimer(() => ToolTip(), -1000)
        return
    }
    WinActivate("ahk_exe WINWORD.EXE")
    Sleep(200)
    Send("^+s")  ; Open Apply Styles
    Sleep(300)
    SendText("Title")
    Send("{Enter}")
    Sleep(100)
    Send("{Escape}")  ; Close if still open
    ToolTip("Applied: Title")
    SetTimer(() => ToolTip(), -800)
}

WordFormatH1() {
    if (!WinExist("ahk_exe WINWORD.EXE")) {
        ToolTip("Word not found!")
        SetTimer(() => ToolTip(), -1000)
        return
    }
    WinActivate("ahk_exe WINWORD.EXE")
    Sleep(200)
    Send("^!1")  ; Ctrl+Alt+1 for Heading 1
    ToolTip("Applied: Heading 1")
    SetTimer(() => ToolTip(), -800)
}

WordFormatH2() {
    if (!WinExist("ahk_exe WINWORD.EXE")) {
        ToolTip("Word not found!")
        SetTimer(() => ToolTip(), -1000)
        return
    }
    WinActivate("ahk_exe WINWORD.EXE")
    Sleep(200)
    Send("^!2")  ; Ctrl+Alt+2 for Heading 2
    ToolTip("Applied: Heading 2")
    SetTimer(() => ToolTip(), -800)
}

WordFormatH3() {
    if (!WinExist("ahk_exe WINWORD.EXE")) {
        ToolTip("Word not found!")
        SetTimer(() => ToolTip(), -1000)
        return
    }
    WinActivate("ahk_exe WINWORD.EXE")
    Sleep(200)
    Send("^!3")  ; Ctrl+Alt+3 for Heading 3
    ToolTip("Applied: Heading 3")
    SetTimer(() => ToolTip(), -800)
}

WordRemoveSpacing() {
    if (!WinExist("ahk_exe WINWORD.EXE")) {
        ToolTip("Word not found!")
        SetTimer(() => ToolTip(), -1000)
        return
    }
    WinActivate("ahk_exe WINWORD.EXE")
    Sleep(200)
    Send("^1")    ; Single line spacing
    Sleep(200)
    ; Open paragraph dialog
    Send("!h")    ; Home tab
    Sleep(100)
    Send("pg")    ; Paragraph group
    Sleep(300)
    ; Set spacing before and after to 0
    Send("!f")    ; Before spacing
    SendText("0")
    Send("{Tab}")
    Send("!r")    ; After spacing  
    SendText("0")
    Send("{Enter}")
    ToolTip("Removed spacing")
    SetTimer(() => ToolTip(), -800)
}

WordToggleBold() {
    if (!WinExist("ahk_exe WINWORD.EXE")) {
        ToolTip("Word not found!")
        SetTimer(() => ToolTip(), -1000)
        return
    }
    WinActivate("ahk_exe WINWORD.EXE")
    Sleep(200)
    Send("^b")
    ToolTip("Toggled Bold")
    SetTimer(() => ToolTip(), -800)
}

WordFormatNormalKeepBullets() {
    if (!WinExist("ahk_exe WINWORD.EXE")) {
        ToolTip("Word not found!")
        SetTimer(() => ToolTip(), -1000)
        return
    }
    WinActivate("ahk_exe WINWORD.EXE")
    Sleep(200)
    
    ; Only remove character formatting (bold, italic, font changes)
    ; but keep paragraph formatting (bullets, numbering, etc.)
    Send("^{Space}")  ; Remove character formatting only
    
    ToolTip("Applied: Normal (kept bullets)")
    SetTimer(() => ToolTip(), -800)
}

; === WORD HOTKEYS (Only active in Word) ===
#HotIf WinActive("ahk_exe WINWORD.EXE")

; Select All Occurrences (Ctrl+D) - VS Code style
^d:: {
    selectedText := GetSelectedText()
    
    if (selectedText = "") {
        return
    }
    
    ; Method 1: Use Find and Replace to select all
    Send("^h")  ; Open Find & Replace
    Sleep(150)
    Send("^a")  ; Select all in find field
    SendText(selectedText)
    Send("{Tab}")  ; Move to replace field
    Send("^a")     ; Select all in replace field
    SendText(selectedText)
    Send("!a")     ; Replace All (this selects all occurrences)
    Sleep(100)
    Send("{Escape}")  ; Close dialog
    
    ToolTip("Selected all: " . selectedText)
    SetTimer(() => ToolTip(), -1500)
}

GetSelectedText() {
    ClipboardOld := A_Clipboard
    A_Clipboard := ""
    Send("^c")
    
    if (!ClipWait(1)) {
        A_Clipboard := ClipboardOld
        return ""
    }
    
    selectedText := A_Clipboard
    A_Clipboard := ClipboardOld
    return selectedText
}

#HotIf