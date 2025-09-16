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
    
    ; Set up input hooks with ~ prefix to let mouse clicks pass through naturally
    HotKey("~*LButton", RecordClick, "On")
    HotKey("~*RButton", RecordClick, "On")
    HotKey("~*MButton", RecordClick, "On")
    
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
    try HotKey("~*LButton", "Off")
    try HotKey("~*RButton", "Off")
    try HotKey("~*MButton", "Off")
    
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
    button := StrReplace(A_ThisHotkey, "~*")  ; Remove the ~*
    
    ; Calculate delay from previous action
    delay := A_TickCount - StartTime
    if (Actions.Length > 0) {
        delay := A_TickCount - Actions[Actions.Length].timestamp
    }
    
    ; Record the action
    action := {type: "click", button: button, x: x, y: y, delay: delay, timestamp: A_TickCount}
    Actions.Push(action)
    
    ; Don't manually click here - the ~ prefix lets the original click pass through naturally
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
    
    ; Add small delay before starting playback to ensure system is ready
    Sleep(100)
    
    Loop Actions.Length {
        action := Actions[A_Index]
        
        ; Wait for the recorded delay (minimum 10ms to prevent issues)
        if (action.delay > 0) {
            Sleep(Max(action.delay, 10))
        } else {
            Sleep(10)  ; Minimum delay between actions
        }
        
        ; Execute the action
        if (action.type = "click") {
            ; Move mouse to position first
            MouseMove(action.x, action.y, 2)  ; Speed 2 for smooth movement
            Sleep(50)  ; Small delay after mouse movement
            
            ; Perform the click
            if (action.button = "LButton") {
                Click("Left")
            } else if (action.button = "RButton") {
                Click("Right")
            } else if (action.button = "MButton") {
                Click("Middle")
            }
            
        } else if (action.type = "key") {
            ; Send the key - it's already in proper AutoHotkey format
            ; Add extra delay for system operations like cut/copy/paste
            if (InStr(action.key, "^{x}") || InStr(action.key, "^{c}") || InStr(action.key, "^{v}")) {
                Send(action.key)
                Sleep(100)  ; Give time for clipboard operations
            } else {
                Send(action.key)
                Sleep(25)   ; Small delay after each keypress
            }
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