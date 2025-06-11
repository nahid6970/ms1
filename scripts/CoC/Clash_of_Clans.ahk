#Requires AutoHotkey v2.0
#include C:\ms1\scripts\Autohtokey\UIA_v2\Lib\UIA.ahk

#HotIf WinActive("ahk_exe dnplayer.exe",)

; F1:: { ;* with hero

;     if WinActive("ahk_exe dnplayer.exe") {

;         SendEvent("1x")
;         Sleep(100)
;         SendEvent("2y")
;         Sleep(100)
;         SendEvent("3z")
;         Sleep(200)

;         SendEvent("4y")
;         Sleep(100)
;         SendEvent("y")
;         Sleep(100)
;         SendEvent("4")
;         Sleep(100)

;         SendEvent("5x6z")
;         Sleep(100)

;         SendEvent("0y")
;         Sleep(100)

;         SendEvent("7x8z")
;     }
; }







^z:: { ;! witouth hero
    CoordMode "Mouse", "Screen"       ; Ensure we're using screen coordinates for all mouse functions
    MouseGetPos &origX, &origY        ; Store the original mouse position (absolute screen position)

    if WinActive("ahk_exe dnplayer.exe") {
        SendEvent("0x")
        Sleep(100)
        SendEvent("1y")
        Sleep(100)
        SendEvent("2z")
        Sleep(200)

        SendEvent("3y")
        Sleep(100)
        SendEvent("y")
        Sleep(100)
        SendEvent("3")
        Sleep(100)

        SendEvent("4x5z")
        Sleep(100)

        ; SendEvent("0y")
        ; Sleep(100)

        SendEvent("6x7z")
    }

    pythonEl := UIA.ElementFromHandle("Python GUI ahk_exe python.exe")
    pythonEl.ElementFromPath("YYYY0").Click("left")

    Click 1672, 65  ; Screen click

    MouseMove origX, origY, 0         ; Restore the mouse to original screen position
}




#HotIf