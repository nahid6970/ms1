#Requires AutoHotkey v2.0
#include C:\ms1\scripts\Autohtokey\UIA_v2\Lib\UIA.ahk

#HotIf WinActive("ahk_exe dnplayer.exe",)



F12:: ;! main base event attack
{ ; V1toV2: Added bracket
    global ; V1toV2: Made function global
    StartTime := A_TickCount
    while (A_TickCount - StartTime < 2000) {
        if !WinActive("ahk_exe dnplayer.exe") {
            break
        }
        SendEvent("ppp")
    }
    return
}




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




; The tilde (~) prefix allows the right mouse button's original function
; (e.g., context menu) to still occur, in addition to triggering this hotkey.
; This hotkey triggers when the RButton is pressed down.
~RButton::
{
    ; Loop indefinitely while the right mouse button is physically held down.
    ; GetKeyState("RButton", "P") checks if the physical key state of RButton is 'pressed'.
    While GetKeyState("RButton", "P")
    {
        ; Send the 'x' key. SendEvent is used for more reliable key sending.
        SendEvent("x")
        ; Pause for a short duration to ensure the game registers the key press.
        Sleep(1) ; Adjust this value (in milliseconds) to control speed.

        ; Send the 'y' key.
        SendEvent("y")
        ; Pause again.
        Sleep(1)

        ; Send the 'z' key.
        SendEvent("z")
        ; Pause for a short duration.
        Sleep(1)

        ; Send the 'x' key. SendEvent is used for more reliable key sending.
        SendEvent("i")
        ; Pause for a short duration to ensure the game registers the key press.
        Sleep(1) ; Adjust this value (in milliseconds) to control speed.

        ; Send the 'y' key.
        SendEvent("o")
        ; Pause again.
        Sleep(1)

        ; Send the 'z' key.
        SendEvent("p")
        ; Pause for a short duration.
        Sleep(1)

        ; Send the 'x' key. SendEvent is used for more reliable key sending.
        SendEvent("g")
        ; Pause for a short duration to ensure the game registers the key press.
        Sleep(1) ; Adjust this value (in milliseconds) to control speed.

        ; Send the 'y' key.
        SendEvent("h")
        ; Pause again.
        Sleep(1)

        ; Send the 'z' key.
        SendEvent("t")
        ; Pause for a short duration.
        Sleep(1)

        ; Send the 'x' key. SendEvent is used for more reliable key sending.
        SendEvent("s")
        ; Pause for a short duration to ensure the game registers the key press.
        Sleep(1) ; Adjust this value (in milliseconds) to control speed.

        ; Send the 'y' key.
        SendEvent("f")
        ; Pause again.
        Sleep(1)

        ; Send the 'z' key.
        SendEvent("k")
        ; Pause for a short duration.
        Sleep(1)

        ; You can add a slightly longer sleep here if you want a pause after
        ; each 'x', 'y', 'z' cycle before it repeats.
        ; Sleep(100)
    }
    ; The loop automatically stops when the right mouse button is released.
}



#HotIf