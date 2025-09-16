#Requires AutoHotkey v2.0
#SingleInstance Force
SendMode("Input")
SetWorkingDir(A_ScriptDir)

; Global variables
Recording := false
Playing := false
Actions := []
StartTime := 0

; Main control hotkeys (always active)
^!k::StartRecording  ; Ctrl+Alt+K to start recording
^!l::PlayActions     ; Ctrl+Alt+L to replay actions

; Conditional Esc hotkey - only active during recording
#HotIf Recording
Esc::StopRecording
#HotIf

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
    
    ; Set up input hooks only for basic keys, not modifier combinations
    HotKey("*LButton", RecordClick, "On")
    HotKey("*RButton", RecordClick, "On")
    HotKey("*MButton", RecordClick, "On")
    
    ; Hook individual keys (letters and numbers)
    Loop 26 {
        key := Chr(64 + A_Index)  ; A-Z
        HotKey("~*" . key, RecordKey, "On")  ; ~ lets key pass through
    }
    
    Loop 10 {
        key := A_Index - 1  ; 0-9
        HotKey("~*" . key, RecordKey, "On")
    }
    
    ; Special keys with ~ prefix to let them pass through
    SpecialKeys := ["Space", "Enter", "Tab", "Backspace", "Delete", "Home", "End", 
                   "Up", "Down", "Left", "Right", "PgUp", "PgDn", "Insert"]
    
    for key in SpecialKeys {
        HotKey("~*" . key, RecordKey, "On")
    }
    
    ; Function keys
    Loop 12 {
        key := "F" . A_Index
        HotKey("~*" . key, RecordKey, "On")
    }
    
    ; Common punctuation with ~ prefix
    PuncKeys := [";", "'", ",", ".", "/", "-", "=", "\", "[", "]", "``"]
    for key in PuncKeys {
        HotKey("~*" . key, RecordKey, "On")
    }
    
    ; Record modifier keys when pressed with other keys
    HotKey("~*Ctrl", RecordModifier, "On")
    HotKey("~*Alt", RecordModifier, "On")
    HotKey("~*Shift", RecordModifier, "On")
    HotKey("~*LWin", RecordModifier, "On")
    HotKey("~*RWin", RecordModifier, "On")
}

StopRecording() {
    if (!Recording) {
        return
    }
    
    global Recording, Actions
    Recording := false
    ToolTip("✅ Recording stopped. " . Actions.Length . " actions recorded.")
    SetTimer(ClearToolTip, -2000)
    
    ; Remove all recording hotkeys
    try HotKey("*LButton", "Off")
    try HotKey("*RButton", "Off")
    try HotKey("*MButton", "Off")
    
    Loop 26 {
        key := Chr(64 + A_Index)
        try HotKey("~*" . key, "Off")
    }
    
    Loop 10 {
        key := A_Index - 1
        try HotKey("~*" . key, "Off")
    }
    
    SpecialKeys := ["Space", "Enter", "Tab", "Backspace", "Delete", "Home", "End", 
                   "Up", "Down", "Left", "Right", "PgUp", "PgDn", "Insert"]
    
    for key in SpecialKeys {
        try HotKey("~*" . key, "Off")
    }
    
    Loop 12 {
        key := "F" . A_Index
        try HotKey("~*" . key, "Off")
    }
    
    PuncKeys := [";", "'", ",", ".", "/", "-", "=", "\", "[", "]", "``"]
    for key in PuncKeys {
        try HotKey("~*" . key, "Off")
    }
    
    ; Remove modifier key hooks
    try HotKey("~*Ctrl", "Off")
    try HotKey("~*Alt", "Off")
    try HotKey("~*Shift", "Off")
    try HotKey("~*LWin", "Off")
    try HotKey("~*RWin", "Off")
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
    
    ; Click passes through automatically since we're not using ~ prefix for mouse
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
    
    ; Get the actual key pressed
    key := A_ThisHotkey
    key := StrReplace(key, "~*", "")  ; Remove ~* prefix
    
    ; Build modifier string for AutoHotkey Send format
    modifiers := ""
    if GetKeyState("Ctrl", "P")
        modifiers .= "^"  ; Ctrl = ^
    if GetKeyState("Alt", "P")
        modifiers .= "!"  ; Alt = !
    if GetKeyState("Shift", "P")
        modifiers .= "+"  ; Shift = +
    if GetKeyState("LWin", "P") || GetKeyState("RWin", "P")
        modifiers .= "#"  ; Win = #
    
    ; Format key for AutoHotkey Send
    finalKey := modifiers . "{" . key . "}"
    
    ; Calculate delay from previous action
    delay := A_TickCount - StartTime
    if (Actions.Length > 0) {
        delay := A_TickCount - Actions[Actions.Length].timestamp
    }
    
    ; Record the action
    action := {type: "key", key: finalKey, delay: delay, timestamp: A_TickCount}
    Actions.Push(action)
    
    ; Key passes through automatically due to ~ prefix
}

RecordModifier(*) {
    ; This function exists just to capture modifier key presses
    ; The actual recording happens in RecordKey when modifiers are combined with other keys
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
            ; Send the key - it's already in proper AutoHotkey format
            Send(action.key)
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
ToolTip("🎯 Macro Recorder Ready!`nCtrl+Alt+K: Start recording`nEsc: Stop recording (only while recording)`nCtrl+Alt+L: Replay actions")
SetTimer(ClearToolTip, -4000)