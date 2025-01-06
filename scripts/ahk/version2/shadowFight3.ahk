#Requires AutoHotkey v2.0
#SingleInstance Force

#HotIf WinActive("ahk_exe dnplayer.exe",)

F13:: ; Hound
{ ; V1toV2: Added bracket
    global ; V1toV2: Made function global
    StartTime := A_TickCount
    while (A_TickCount - StartTime < 5000) {
        if !WinActive("ahk_exe dnplayer.exe") {
            break
        }
        SendEvent("{i down}")
        SendEvent("{x down}")
        SendEvent("jjj")
        SendEvent("{x up}")
        SendEvent("{i up}")
    }
    return
}

F14:: ; Hound vortex
{ ; V1toV2: Added bracket
    global ; V1toV2: Made function global
    StartTime := A_TickCount
    while (A_TickCount - StartTime < 5000) {
        if !WinActive("ahk_exe dnplayer.exe") {
            break
        }
        SendEvent("{x down}")
        Sleep(500)
        SendEvent("{i down}")
        Send("j")
        SendEvent("{i up}")
        SendEvent("{x up}")
    }
    return
}

F15:: ; Hound Laggy
{ ; V1toV2: Added bracket
    global ; V1toV2: Made function global
    StartTime := A_TickCount
    while (A_TickCount - StartTime < 5000) {
        if !WinActive("ahk_exe dnplayer.exe") {
            break
        }
        Send("{i down}")
        Send("{x down}")
        SendInput("jjj")
        Send("{x up}")
        Send("{i up}")
    }
    return
}

F16:: ; Heritage Laggy
{ ; V1toV2: Added bracket
    global ; V1toV2: Made function global
    StartTime := A_TickCount
    while (A_TickCount - StartTime < 5000) {
        if !WinActive("ahk_exe dnplayer.exe") {
            break
        }
        Send("{s down}")
        Send("{i down}")
        SendInput("iii")
        Send("{i up}")
        Send("{s up}")
    }
    return
}

F20:: ; Right Side Enemy
{
    global
    StartTime := A_TickCount
    while (A_TickCount - StartTime < 1000) {
        if !WinActive("ahk_exe dnplayer.exe") {
            break
        }
        SendEvent("{i down}")
        SendEvent("{x down}")
        SendEvent("{d down}")
        SendEvent("iiiiiixxxxxxjjiiiiiixxxxxx")
        SendEvent("{d up}")
        SendEvent("{x up}")
        SendEvent("{i up}")
    }
    return
}

F21:: ; Left Side Enemy
{
    global
    StartTime := A_TickCount
    while (A_TickCount - StartTime < 1000) {
        if !WinActive("ahk_exe dnplayer.exe") {
            break
        }
        SendEvent("{i down}")
        SendEvent("{x down}")
        SendEvent("{a down}")
        SendEvent("iiiiiixxxxxxjjiiiiiixxxxxx")
        SendEvent("{a up}")
        SendEvent("{x up}")
        SendEvent("{i up}")
    }
    return
}

;     F14::
; { ; V1toV2: Added bracket
; global ; V1toV2: Made function global
;         StartTime := A_TickCount
;         while (A_TickCount - StartTime < 5000)
;         {
;             if !WinActive("ahk_exe dnplayer.exe")
;             {
;                 break
;             }
;             SendEvent("{l down}")
;             SendEvent("{i down}")
;             SendEvent("{d down}")
;             SendEvent("j")
;             SendEvent("j")
;             SendEvent("{d up}")
;             SendEvent("{i up}")
;             SendEvent("{l up}")
;             Sleep(100)
;         }
;     return
; } ; V1toV2: Added Bracket before hotkey or Hotstring

;     F15::
; { ; V1toV2: Added bracket
; global ; V1toV2: Made function global
;     StartTime := A_TickCount
;     while (A_TickCount - StartTime < 5000)
;     {
;         if !WinActive("ahk_exe dnplayer.exe")
;         {
;             break
;         }
;         SendEvent("{x down}")
;         SendEvent("{l down}")
;         SendEvent("{i down}")
;         SendEvent("{d down}")
;         SendEvent("j")
;         SendEvent("j")
;         SendEvent("{d up}")
;         SendEvent("{i up}")
;         SendEvent("{l up}")
;         SendEvent("{x up}")
;         Sleep(100)
;     }
; return
; } ; V1toV2: Added Bracket before hotkey or Hotstring

;     F16::
; { ; V1toV2: Added bracket
; global ; V1toV2: Made function global
;         StartTime := A_TickCount
;         while (A_TickCount - StartTime < 5000)
;         {
;             if !WinActive("ahk_exe dnplayer.exe")
;             {
;                 break
;             }
;             SendEvent("x")
;             Sleep(100)
;             SendEvent("x")
;             Sleep(100)
;             SendEvent("x")
;             Sleep(100)
;             SendEvent("x")
;             Sleep(100)
;             SendEvent("i")
;         }
;     return
; } ; V1toV2: Added Bracket before hotkey or Hotstring

;     F17:: ; liberator
; { ; V1toV2: Added bracket
; global ; V1toV2: Made function global
;         StartTime := A_TickCount
;         while (A_TickCount - StartTime < 5000)
;         {
;             if !WinActive("ahk_exe dnplayer.exe")
;             {
;                 break
;             }
;             SendEvent("{x down}")
;             SendEvent("{a down}")
;             SendEvent("l")
;             SendEvent("{a up}")
;             Sleep(100)
;             SendEvent("{d down}")
;             SendEvent("l")
;             SendEvent("{d up}")
;             Sleep(100)
;             SendEvent("{s down}")
;             SendEvent("l")
;             SendEvent("{s up}")
;             Sleep(100)
;             SendEvent("{w down}")
;             SendEvent("l")
;             SendEvent("{w up}")
;             Sleep(100)
;             SendEvent("{d down}")
;             SendEvent("j")
;             SendEvent("j")
;             SendEvent("{d up}")
;             SendEvent("{x up}")
;             Sleep(100)
;         }
;     return
; } ; V1toV2: Added Bracket before hotkey or Hotstring

;     F18:: ; xj
; { ; V1toV2: Added bracket
; global ; V1toV2: Made function global
;         StartTime := A_TickCount
;         while (A_TickCount - StartTime < 5000)
;         {
;             if !WinActive("ahk_exe dnplayer.exe")
;             {
;                 break
;             }
;             SendEvent("{x down}")
;             Sleep(650)
;             SendEvent("{x up}")

;             SendEvent("{j down}")
;             Sleep(500)
;             SendEvent("{j up}")
;         }
;     return
; } ; V1toV2: Added Bracket before hotkey or Hotstring

;     F19:: ; possessed
; { ; V1toV2: Added bracket
; global ; V1toV2: Made function global
;         StartTime := A_TickCount
;         while (A_TickCount - StartTime < 5000)
;         {
;             if !WinActive("ahk_exe dnplayer.exe")
;             {
;                 break
;             }
;             SendEvent("{i down}")

;             SendEvent("{a down}")
;             SendEvent("l")
;             Sleep(100)
;             SendEvent("{a up}")

;             SendEvent("{d down}")
;             SendEvent("l")
;             Sleep(100)
;             SendEvent("{d up}")

;             SendEvent("{s down}")
;             SendEvent("l")
;             Sleep(100)
;             SendEvent("{s up}")

;             SendEvent("{w down}")
;             SendEvent("l")
;             Sleep(100)
;             SendEvent("{w up}")

;             SendEvent("{i up}")
;         }
;     return
;     }

; ;     F20:: ; Hound
; ; { ; V1toV2: Added bracket
; ; global ; V1toV2: Made function global
; ;     StartTime := A_TickCount
; ;     while (A_TickCount - StartTime < 5000)
; ;     {
; ;         if !WinActive("ahk_exe dnplayer.exe")
; ;         {
; ;             break
; ;         }

; ;         SendEvent("{i down}")
; ;         SendEvent("{x down}")
; ;         Sleep(1500)

; ;         ; Hold down 'd' for 3 seconds while pressing 'j' repeatedly
; ;         SendEvent("{d down}")
; ;         Loop 10 ; Press 'j' 30 times (approx 1 press per 100ms for 3 seconds)
; ;         {
; ;             SendInput("j")
; ;             Sleep(100) ; Adjust the delay between each 'j' press
; ;         }
; ;         SendEvent("{d up}") ; Release 'd' after 3 seconds
; ;         SendEvent("{x up}")
; ;         SendEvent("{i up}")
; ;     }
; ;     return
; ;     }

; ; F21:: ; Laggy other set
; ; { ; V1toV2: Added bracket
; ; global ; V1toV2: Made function global
; ;     StartTime := A_TickCount
; ;     while (A_TickCount - StartTime < 5000)
; ;     {
; ;         if !WinActive("ahk_exe dnplayer.exe")
; ;         {
; ;             break
; ;         }

; ;         Send("{s down}")
; ;         Sendinput("s")
; ;         Send("{s up}")
; ;     }
; ;     return
; ;     }

#HotIf