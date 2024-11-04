;*  ███████╗███████╗██████╗
;*  ██╔════╝██╔════╝╚════██╗
;*  ███████╗█████╗   █████╔╝
;*  ╚════██║██╔══╝   ╚═══██╗
;*  ███████║██║     ██████╔╝
;*  ╚══════╝╚═╝     ╚═════╝
#IfWinActive ahk_exe dnplayer.exe

    F13::
        StartTime := A_TickCount  ; Record the current time
        while (A_TickCount - StartTime < 5000)  ; Run for 5000 milliseconds (5 seconds)
        {
            if !WinActive("ahk_exe dnplayer.exe")  ; Ensure dnplayer.exe is active
            {
                break  ; Stop if dnplayer.exe is no longer active
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
    while (A_TickCount - StartTime < 5000)  ; Run the loop for 5 seconds
    {
        if !WinActive("ahk_exe dnplayer.exe")
            break

        Send, {l down}     ; Hold down 'l'
        Send, {d down}     ; Hold down 'd'

        Loop, 15           ; Repeat 'j' press for 1.5 seconds
        {
            SendInput, j   ; Press 'j'
            Sleep, 100     ; Delay between each 'j' press (adjustable)
        }

        Send, {d up}       ; Release 'd' after 1.5 seconds
        Send, {l up}       ; Release 'l' after 1.5 seconds
        Sleep, 100         ; Small pause before repeating the main loop
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

    ;! liberator
    F17::
        StartTime := A_TickCount  ; Record the current time
        while (A_TickCount - StartTime < 5000)  ; Run for 5000 milliseconds (5 seconds)
        {
            if !WinActive("ahk_exe dnplayer.exe")  ; Ensure dnplayer.exe is active
            {
                break  ; Stop if dnplayer.exe is no longer active
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

    ;! xj
    F18::
        StartTime := A_TickCount  ; Record the current time
        while (A_TickCount - StartTime < 5000)  ; Run for 5000 milliseconds (5 seconds)
        {
            if !WinActive("ahk_exe dnplayer.exe")  ; Ensure dnplayer.exe is active
            {
                break  ; Stop if dnplayer.exe is no longer active
            }
            Send, {x down}
            Sleep, 650
            Send, {x up}

            Send, {j down}
            Sleep, 500
            Send, {j up}
        }
    return

    ;! possessed
    F19::
        StartTime := A_TickCount  ; Record the current time
        while (A_TickCount - StartTime < 5000)  ; Run for 5000 milliseconds (5 seconds)
        {
            if !WinActive("ahk_exe dnplayer.exe")  ; Ensure dnplayer.exe is active
            {
                break  ; Stop if dnplayer.exe is no longer active
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