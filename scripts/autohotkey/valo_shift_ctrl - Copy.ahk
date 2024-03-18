#Persistent

#IfWinActive, ahk_exe C:\Riot Games\VALORANT\live\VALORANT.exe ahk_exe C:\Riot Games\VALORANT\live\ShooterGame\Binaries\Win64\VALORANT-Win64-Shipping.exe

; Initialize mode and HoldingJ variables
Mode := 3 ; Start in normal mode

F1::
  ; Set mode to normal
  Mode := 3
  SoundPlay, C:\Users\nahid\OneDrive\backup\sound\finger_snap.wav
  return

F2::
  ; Toggle between modes
  Mode := (Mode = 1) ? 2 : 1

  ; Play sound based on mode
  if (Mode = 1)
    SoundPlay, C:\Users\nahid\OneDrive\backup\sound\Shutter.wav
  else if (Mode = 2)
    SoundPlay, C:\Users\nahid\OneDrive\backup\sound\short_success.wav

  return

~LButton::
  ; While the left mouse button is held down, simulate key presses based on the mode
  While (GetKeyState("LButton", "P")) {
    if (Mode = 1) {
      ; In the first mode, simulate holding down the "J" key
      Send, {j down}
      Sleep, 10 ; Adjust the sleep time as needed
    } else if (Mode = 2) {
      ; In the second mode, simulate rapid clicks of the "K" key
      Send, k
      Sleep, 50 ; Adjust the sleep time as needed
    } else if (Mode = 3) {
      ; In the third mode (normal), let the left mouse button behave as normal
      Sleep, 10 ; A small delay to reduce CPU usage
    }
  }

  ; Release the "J" key if it was held down
  if (Mode = 1)
    Send, {j up}

  return

#IfWinActive

; Remap Left Shift to L
LShift::L

; Remap Left Ctrl to I
LCtrl::i
