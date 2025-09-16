#Requires AutoHotkey v2.0
#SingleInstance Force
SendMode("Input")
SetWorkingDir(A_ScriptDir)

; Global variables
Recording := false
Playing := false
Actions := []
StartTime := 0

; Hotkeys
^!k::StartRecording  ; Ctrl+Alt+K to start recording
Esc::StopRecording   ; Esc to stop recording
^!l::PlayActions     ; Ctrl+Alt+L to replay actions

StartRecording() {
    if (Playing) {
        return
    }
    
    global Recording, Actions, StartTime
    Recording := true
    Actions := []
    StartTime := A_TickCount
    
    ; Show recording indicator
    ToolTip("🔴 RECORDING - Press ESC to stop")
    
    ; Set up input hooks
    HotKey("*LButton", RecordClick, "On")
    HotKey("*RButton", RecordClick, "On")
    HotKey("*MButton", RecordClick, "On")
    
    ; Hook all printable keys and common special keys
    Loop 26 {
        key := Chr(64 + A_Index)  ; A-Z
        HotKey("*" . key, RecordKey, "On")
        HotKey("*+" . key, RecordKey, "On")  ; Shift combinations
    }
    
    Loop 10 {
        key := A_Index - 1  ; 0-9
        HotKey("*" . key, RecordKey, "On")
    }
    
    ; Special keys
    SpecialKeys := ["Space", "Enter", "Tab", "Backspace", "Delete", "Home", "End", 
                   "Up", "Down", "Left", "Right", "PgUp", "PgDn", "Insert",
                   "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"]
    
    for key in SpecialKeys {
        HotKey("*" . key, RecordKey, "On")
        HotKey("*+" . key, RecordKey, "On")  ; Shift combinations
    }
    
    ; Common punctuation
    PuncKeys := [";", "'", ",", ".", "/", "-", "=", "\", "[", "]", "``"]
    for key in PuncKeys {
        HotKey("*" . key, RecordKey, "On")
        HotKey("*+" . key, RecordKey, "On")  ; Shift combinations
    }
}

StopRecording() {
    if (!Recording) {
        return
    }
    
    global Recording, Actions
    Recording := false
    ToolTip("✅ Recording stopped. " . Actions.Length . " actions recorded.")
    SetTimer(ClearToolTip, -2000)
    
    ; Remove all hotkeys
    HotKey("*LButton", "Off")
    HotKey("*RButton", "Off")
    HotKey("*MButton", "Off")
    
    Loop 26 {
        key := Chr(64 + A_Index)
        try HotKey("*" . key, "Off")
        try HotKey("*+" . key, "Off")
    }
    
    Loop 10 {
        key := A_Index - 1
        try HotKey("*" . key, "Off")
    }
    
    SpecialKeys := ["Space", "Enter", "Tab", "Backspace", "Delete", "Home", "End", 
                   "Up", "Down", "Left", "Right", "PgUp", "PgDn", "Insert",
                   "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"]
    
    for key in SpecialKeys {
        try HotKey("*" . key, "Off")
        try HotKey("*+" . key, "Off")
    }
    
    PuncKeys := [";", "'", ",", ".", "/", "-", "=", "\", "[", "]", "``"]
    for key in PuncKeys {
        try HotKey("*" . key, "Off")
        try HotKey("*+" . key, "Off")
    }
}

RecordClick(*) {
    if (!Recording) {
        return
    }
    
    global Actions, StartTime
    
    ; Get mouse position and button
    MouseGetPos(&x, &y)
    button := StrReplace(A_ThisHotkey, "*")  ; Remove the *
    
    ; Calculate delay from previous action
    delay := A_TickCount - StartTime
    if (Actions.Length > 0) {
        delay := A_TickCount - Actions[Actions.Length].timestamp
    }
    
    ; Record the action
    action := {type: "click", button: button, x: x, y: y, delay: delay, timestamp: A_TickCount}
    Actions.Push(action)
    
    ; Let the click through
    if (button = "LButton") {
        Click()
    } else if (button = "RButton") {
        Click("Right")
    } else if (button = "MButton") {
        Click("Middle")
    }
}

RecordKey(*) {
    if (!Recording) {
        return
    }
    
    global Actions, StartTime
    
    key := StrReplace(A_ThisHotkey, "*")  ; Remove *
    
    ; Calculate delay from previous action
    delay := A_TickCount - StartTime
    if (Actions.Length > 0) {
        delay := A_TickCount - Actions[Actions.Length].timestamp
    }
    
    ; Record the action
    action := {type: "key", key: key, delay: delay, timestamp: A_TickCount}
    Actions.Push(action)
    
    ; Let the key through
    Send("{" . key . "}")
}

PlayActions() {
    if (Recording or Playing or Actions.Length = 0) {
        return
    }
    
    global Playing, Actions
    Playing := true
    ToolTip("▶️ Playing " . Actions.Length . " actions...")
    
    Loop Actions.Length {
        action := Actions[A_Index]
        
        ; Wait for the recorded delay
        if (action.delay > 0) {
            Sleep(action.delay)
        }
        
        ; Execute the action
        if (action.type = "click") {
            MouseMove(action.x, action.y, 0)
            if (action.button = "LButton") {
                Click()
            } else if (action.button = "RButton") {
                Click("Right")
            } else if (action.button = "MButton") {
                Click("Middle")
            }
        } else if (action.type = "key") {
            Send("{" . action.key . "}")
        }
    }
    
    Playing := false
    ToolTip("✅ Playback complete!")
    SetTimer(ClearToolTip, -2000)
}

ClearToolTip() {
    ToolTip()
}

; Show help on startup
ToolTip("🎯 Macro Recorder Ready!`nCtrl+Alt+K: Start recording`nEsc: Stop recording`nCtrl+Alt+L: Replay actions")
SetTimer(ClearToolTip, -3000)