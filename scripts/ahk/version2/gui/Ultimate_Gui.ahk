; Help
; For line breaks use `n

#Requires AutoHotkey v2.0

myGui := Gui("+AlwaysOnTop", "Control Panel")
myGui.SetFont("s12 Bold", "Jetbrainsmono nfp")
myGui.MarginX := 20
myGui.MarginY := 20

; Add buttons with labels and actions for each command
myGui.Add("Text", "xm  ym w200 Backgroundffa114 +Center Border", "Komorebic Save").OnEvent("Click", (*) => RunWait("komorebic quick-save-resize", , "Hide"))
myGui.Add("Text", "x+5 yp w200 Backgroundffa114 +Center Border", "Komorebic Load").OnEvent("Click", (*) => RunWait("komorebic quick-load-resize", , "Hide"))

myGui.SetFont("s30 Bold", "Jetbrainsmono nfp")
myGui.Add("Text", "xm y+5 Backgroundf30000 cffffff w100 +Center", "").OnEvent("Click", (*) => KillProcess("python.exe"))
myGui.Add("Text", "x+5 yp Backgroundf30000 cffffff w100 +Center", "󱂬").OnEvent("Click", (*) => KillProcess("komorebi.exe"))
myGui.Add("Text", "x+5 yp Backgroundf30000 cffffff w100 +Center", "").OnEvent("Click", (*) => KillProcess("explorer.exe"))
myGui.Add("Text", "x+5 yp Backgroundf30000 cffffff w100 +Center", "").OnEvent("Click", (*) => KillProcess("cmd.exe"))
myGui.Add("Text", "x+5 yp Backgroundf30000 cffffff w100 +Center", "󰨊").OnEvent("Click", (*) => KillProcess("powershell.exe"))
myGui.Add("Text", "x+5 yp Backgroundf30000 cffffff w100 +Center", "").OnEvent("Click", (*) => KillProcess("pwsh.exe"))

myGui.SetFont("s20 Bold", "Jetbrainsmono nfp")
myGui.Add("Text", "xm y+5 Background31ffc1 c000000 w50 +Center +Border", "").OnEvent("Click", (*) => (myGui.Destroy(), Sleep(500), Send("#+f"))) ;; App--> Text Grab
myGui.Add("Text", "x+5 yp Background31ffc1 cec2d47 w50 +Center +Border", "").OnEvent("Click", (*) => (Run("C:\ms1\scripts\Locker.py",, "Hide"))) ;; Locker ;; python script

myGui.SetFont("s20 Bold", "Jetbrainsmono nfp")
myGui.Add("Text", "xm y+5 Background31ffc1 c000000 w50 +Center +Border", "").OnEvent("Click", (*) => (Run("C:\ms1\scripts\ffmpeg\trim.ps1",, "Show"))) ;; ffmpeg video cut
myGui.Add("Text", "x+5 yp Background31ffc1 c000000 w50 +Center +Border", "").OnEvent("Click", (*) => (Run("C:\ms1\scripts\ffmpeg\convert.ps1",, "Show"))) ;; ffmpeg video Convert
myGui.Add("Text", "x+5 yp Background31ffc1 c000000 w50 +Center +Border", "󰕩").OnEvent("Click", (*) => (Run("C:\ms1\scripts\ffmpeg\merge.ps1",, "Show"))) ;; ffmpeg video merge
myGui.Add("Text", "x+5 yp Background31ffc1 c000000 w50 +Center +Border", "").OnEvent("Click", (*) => (Run("C:\ms1\scripts\ffmpeg\vid_dim.ps1",, "Show"))) ;; ffmpeg video dimension
myGui.Add("Text", "x+5 yp Background31ffc1 c000000 w50 +Center +Border", "").OnEvent("Click", (*) => (Run("C:\ms1\scripts\ffmpeg\img_dim.ps1",, "Show"))) ;; ffmpeg image dimension

myGui.SetFont("s12 Bold", "Jetbrainsmono nfp")
myGui.Add("Text", "xm y+5  w200 +Center Border", "AHK-Scripts").SetFont("s12 Bold", "Jetbrainsmono nfp")
myGui.Add("Text", "x+5 yp Background32ec44 cBlack w200 +Center", "AhkConverter").OnEvent("Click", (*) => Run("C:\msBackups\Autohotkey\AHK_converter\QuickConvertorV2_scintilla.ahk", , "Hide"))
myGui.Add("Text", "x+5 yp Background32ec44 cBlack w200 +Center", "UIA-V2").OnEvent("Click", (*) => Run("C:\msBackups\Autohotkey\UIA_v2\UIATreeInspector.ahk", , "Hide"))

myGui.Add("Text", "xm y+5  w200 +Center Border", "Komorebi").SetFont("s12 Bold", "Jetbrainsmono nfp")
myGui.Add("Text", "x+5 yp Background32ec44 cBlack w200 +Center", "").OnEvent("Click", (*) => Run("komorebi.exe", , "Hide"))

myGui.Add("Text", "xm y+5  w200 +Center Border", "Python").SetFont("s12 Bold", "Jetbrainsmono nfp")
myGui.Add("Text", "x+5 yp Background32ec44 cBlack w200 +Center", "mypygui-H").OnEvent("Click", (*) => Run("C:\ms1\mypygui.py", , "Hide"))
myGui.Add("Text", "x+5 yp Background32ec44 cBlack w200 +Center", "mypygui-S").OnEvent("Click", (*) =>  StartPython_ST())

myGui.Add("Text", "xm y+5  w200 +Center Border", "Explorer").SetFont("s12 Bold", "Jetbrainsmono nfp")
myGui.Add("Text", "x+5 yp Background32ec44 cBlack w200 +Center", "").OnEvent("Click", (*) =>  RestartExplorer())


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

; Function to restart explorer.exe
RestartExplorer() {
    Run("taskkill /f /im explorer.exe")
    Sleep(500) 
    Run('pwsh -Command "Start-Process explorer"', ,)
}
