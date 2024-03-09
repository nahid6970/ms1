; Initialize toggle variable
Toggle := false

; F1 to activate the script
F1::
    ; Toggle script activation
    Toggle := !Toggle
    ; Play activation sound
    if (Toggle)
        SoundPlay, C:\Users\nahid\OneDrive\backup\sound\Shutter.wav
    ; Play deactivation sound
    else
        SoundPlay, C:\Users\nahid\OneDrive\backup\sound\finger_snap.wav
    return

#If (Toggle)
~LButton::
    ; While left mouse button is held down, send continuous "K" key presses
    While GetKeyState("LButton", "P") {
        SendInput, k
        Sleep 50 ; Adjust sleep time as needed
    }
    return
#If
