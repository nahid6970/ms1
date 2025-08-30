#Requires AutoHotkey v2.0

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

; === IMPROVED COLOR FUNCTIONS ===
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
    Sleep(400)
    
    ; Try to find the color palette by looking for the standard color row
    if (FindColorPalette(&paletteX, &paletteY)) {
        ; Click on red color (2nd position in the standard row)
        Click(paletteX + 25, paletteY)  ; Approximate offset for red
        ToolTip("Applied: Red Color")
        SetTimer(() => ToolTip(), -800)
    } else {
        ; Fallback: use keyboard navigation to standard colors
        Send("{Down}{Down}")  ; Navigate to standard colors row
        Send("{Right}{Right}")  ; Navigate to red position
        Send("{Enter}")
        ToolTip("Applied: Red Color (keyboard)")
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
    Sleep(400)
    
    ; Try to find the color palette by looking for the standard color row
    if (FindColorPalette(&paletteX, &paletteY)) {
        ; Click on green color (6th position in the standard row)
        Click(paletteX + 125, paletteY)  ; Approximate offset for green
        ToolTip("Applied: Green Color")
        SetTimer(() => ToolTip(), -800)
    } else {
        ; Fallback: use keyboard navigation to standard colors
        Send("{Down}{Down}")  ; Navigate to standard colors row
        Send("{Right}{Right}{Right}{Right}{Right}{Right}")  ; Navigate to green position
        Send("{Enter}")
        ToolTip("Applied: Green Color (keyboard)")
        SetTimer(() => ToolTip(), -800)
    }
}

; Function to find the color palette by looking for multiple consecutive palette colors
FindColorPalette(&paletteX, &paletteY) {
    ; Search in a limited area where the color dropdown typically appears
    ; (top portion of screen where ribbon/menus are)
    searchTop := 0
    searchBottom := A_ScreenHeight // 3  ; Only search top third of screen
    
    ; Standard Word color palette row colors (in hex)
    ; c00000 ee0000 ffc000 ffff00 92d050 00b050 00b0f0 0070c0 002060 7030a0
    
    ; Method 1: Look for dark red (c00000) and verify the sequence
    if (PixelSearch(&x1, &y1, 0, searchTop, A_ScreenWidth, searchBottom, 0xc00000, 8)) {
        ; Verify this is part of the palette by checking for red (ee0000) nearby
        if (PixelSearch(&x2, &y2, x1 + 10, y1 - 8, x1 + 40, y1 + 8, 0xee0000, 8)) {
            ; Further verify by checking for yellow (ffff00) in the sequence
            if (PixelSearch(&x3, &y3, x1 + 50, y1 - 8, x1 + 100, y1 + 8, 0xffff00, 8)) {
                paletteX := x1
                paletteY := y1
                return true
            }
        }
    }
    
    ; Method 2: Look for yellow and work backwards/forwards
    if (PixelSearch(&x1, &y1, 0, searchTop, A_ScreenWidth, searchBottom, 0xffff00, 8)) {
        ; Check if we can find red to the left (indicating this is the palette)
        if (PixelSearch(&x2, &y2, x1 - 60, y1 - 8, x1 - 20, y1 + 8, 0xee0000, 8)) {
            ; Check for green to the right
            if (PixelSearch(&x3, &y3, x1 + 10, y1 - 8, x1 + 50, y1 + 8, 0x00b050, 8)) {
                ; Calculate start position (red should be about 25 pixels left of yellow)
                paletteX := x1 - 50
                paletteY := y1
                return true
            }
        }
    }
    
    ; Method 3: Look for green and verify context
    if (PixelSearch(&x1, &y1, 0, searchTop, A_ScreenWidth, searchBottom, 0x00b050, 8)) {
        ; Check if yellow is to the left
        if (PixelSearch(&x2, &y2, x1 - 50, y1 - 8, x1 - 10, y1 + 8, 0xffff00, 8)) {
            ; Calculate approximate start of palette
            paletteX := x1 - 100  ; Green is about 100 pixels from start
            paletteY := y1
            return true
        }
    }
    
    return false
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