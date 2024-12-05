#Requires AutoHotkey v2.0

myGui := Gui("+AlwaysOnTop", "Control Panel")
myGui.SetFont("s12 Bold", "Jetbrainsmono nfp")
myGui.MarginX := 20
myGui.MarginY := 20

; Add buttons with labels and actions for each command
myGui.Add("Text", "xm  ym w200 +Center", "Komorebic Save").OnEvent("Click", (*) => RunWait("komorebic quick-save-resize", , "Hide"))
myGui.Add("Text", "x+5 yp w200 +Center", "Komorebic Load").OnEvent("Click", (*) => RunWait("komorebic quick-load-resize", , "Hide"))

myGui.Add("Text", "xm y+5  w200 +Center", "Komorebi")
myGui.Add("Text", "x+5 yp Backgroundf30000 cWhite w200 +Center", "").OnEvent("Click", (*) => KillProcess("komorebi.exe"))
myGui.Add("Text", "x+5 yp Background32ec44 cBlack w200 +Center", "").OnEvent("Click", (*) => Run("komorebi.exe", , "Hide"))

myGui.Add("Text", "xm y+5  w200 +Center", "Python")
myGui.Add("Text", "x+5 yp Backgroundf30000 cWhite w200 +Center", "").OnEvent("Click", (*) => KillProcess("python.exe"))
myGui.Add("Text", "x+5 yp Background32ec44 cBlack w200 +Center", "mypygui-H").OnEvent("Click", (*) => Run("C:\ms1\mypygui.py", , "Hide"))
myGui.Add("Text", "x+5 yp Background32ec44 cBlack w200 +Center", "mypygui-S").OnEvent("Click", (*) =>  StartPython_ST())

myGui.Add("Text", "xm y+5  w200 +Center", "Terminals")
myGui.Add("Text", "x+5 yp Backgroundf30000 cWhite w200 +Center", "pwsh")      .OnEvent("Click", (*) => KillProcess("pwsh.exe"))
myGui.Add("Text", "x+5 yp Backgroundf30000 cWhite w200 +Center", "powershell").OnEvent("Click", (*) => KillProcess("powershell.exe"))
myGui.Add("Text", "x+5 yp Backgroundf30000 cWhite w200 +Center", "cmd")       .OnEvent("Click", (*) => KillProcess("cmd.exe"))




myGui.Show()
myGui.OnEvent("Close", (*) => ExitApp())

; Function to kill a process by name
KillProcess(processName) {
    Run("taskkill /f /im " processName, , "Hide") ; Kill the specified process
}

; Function to start Python with a specific script, keeping PowerShell open for errors
startpython_st() {
    Run('pwsh -NoExit -Command "python C:\ms1\mypygui.py"', , "") 
}