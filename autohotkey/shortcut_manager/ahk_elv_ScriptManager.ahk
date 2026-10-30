#Requires AutoHotkey v2.0
RestartScriptManager()
RestartScriptManager() {
    ; Check if the window exists
    if WinExist("SCRIPT // MANAGER") {
        ; Get the process ID of the window
        ProcessID := WinGetPID("SCRIPT // MANAGER")
        ; Kill the process
        Run("taskkill /f /pid " ProcessID, , "Hide")
        ; Wait a moment for the process to close
        Sleep(500)
    }
    ; Launch the script
    Run('pythonw "C:\@delta\ms1\tools\Script_Manager\script_manager_gui_qt.py"')
    WinWait("SCRIPT // MANAGER")
    WinActivate("SCRIPT // MANAGER")
}
