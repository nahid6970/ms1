; Initialize a variable to toggle the script on/off
ScriptActive := 0
$*F1:: ; Activate when F1 is pressed
    ScriptActive := 1
    return
$*F2:: ; Deactivate when F2 is pressed
    ScriptActive := 0
    return
#If ScriptActive  ; Only execute the following hotkeys if ScriptActive is true
    ~RButton & LButton::
    SetTitleMatchMode, 2
    ; Close Chrome
    Process, Close, chrome.exe
    ; Focus on PotPlayer
    IfWinExist, PotPlayer
    {
        WinActivate
        WinWaitNotActive
        WinActivate
    }
    else
    {
        Run, "C:\Users\nahid\scoop\apps\potplayer\current\PotPlayerMini64.exe"
    }
    return
#If ; Reset the hotkey condition
