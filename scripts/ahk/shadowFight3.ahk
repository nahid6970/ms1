;*  ███████╗███████╗██████╗
;*  ██╔════╝██╔════╝╚════██╗
;*  ███████╗█████╗   █████╔╝
;*  ╚════██║██╔══╝   ╚═══██╗
;*  ███████║██║     ██████╔╝
;*  ╚══════╝╚═╝     ╚═════╝
#IfWinActive ahk_exe dnplayer.exe

    F13:: ; dj
    StartTime := A_TickCount
    while (A_TickCount - StartTime < 5000)
    {
        if !WinActive("ahk_exe dnplayer.exe")
        {
            break
        }
        Send, {d down}
        SendInput, j
        SendInput, j
        SendInput, j
        Send, {d up}
        Sleep, 100    
    }
return


    F14::
        StartTime := A_TickCount
        while (A_TickCount - StartTime < 5000)
        {
            if !WinActive("ahk_exe dnplayer.exe")
            {
                break
            }
            Send, {l down}
            Send, {i down}
            Send, {d down}
            Send, j
            Send, j
            Send, {d up}
            Send, {i up}
            Send, {l up}
            Sleep, 100    
        }
    return

    F15::
    StartTime := A_TickCount
    while (A_TickCount - StartTime < 5000)
    {
        if !WinActive("ahk_exe dnplayer.exe")
        {
            break
        }
        Send, {x down}
        Send, {l down}
        Send, {i down}
        Send, {d down}
        Send, j
        Send, j
        Send, {d up}
        Send, {i up}
        Send, {l up}
        Send, {x up}
        Sleep, 100    
    }
return


    F16::
        StartTime := A_TickCount
        while (A_TickCount - StartTime < 5000)
        {
            if !WinActive("ahk_exe dnplayer.exe")
            {
                break
            }
            Send, x
            Sleep, 100
            Send, i
        }
    return


    F17:: ; liberator
        StartTime := A_TickCount
        while (A_TickCount - StartTime < 5000)
        {
            if !WinActive("ahk_exe dnplayer.exe")
            {
                break
            }
            Send, {x down}
            Send, {a down}
            Send, l
            Send, {a up}
            Sleep, 100
            Send, {d down}
            Send, l
            Send, {d up}
            Sleep, 100
            Send, {s down}
            Send, l
            Send, {s up}
            Sleep, 100
            Send, {w down}
            Send, l
            Send, {w up}
            Sleep, 100
            Send, {d down}
            Send, j
            Send, j
            Send, {d up}
            Send, {x up}
            Sleep, 100
        }
    return


    F18:: ; xj
        StartTime := A_TickCount
        while (A_TickCount - StartTime < 5000)
        {
            if !WinActive("ahk_exe dnplayer.exe")
            {
                break
            }
            Send, {x down}
            Sleep, 650
            Send, {x up}

            Send, {j down}
            Sleep, 500
            Send, {j up}
        }
    return


    F19:: ; possessed
        StartTime := A_TickCount
        while (A_TickCount - StartTime < 5000)
        {
            if !WinActive("ahk_exe dnplayer.exe")
            {
                break
            }
            Send, {i down}

            Send, {a down}
            SendInput, l
            Sleep, 250
            Send, {a up}

            Send, {d down}
            SendInput, l
            Sleep, 250
            Send, {d up}

            Send, {s down}
            SendInput, l
            Sleep, 250
            Send, {s up}

            Send, {w down}
            SendInput, l
            Sleep, 250
            Send, {w up}

            Send, {i up}
            Sleep, 100
        }
    return

#If