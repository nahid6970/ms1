#Requires AutoHotkey v2.0

myGui := Gui("+AlwaysOnTop", "Control Panel")
myGui.SetFont("s12 Bold", "Jetbrainsmono nfp")
myGui.MarginX := 20
myGui.MarginY := 20

; Add buttons with labels and actions for each command
myGui.Add("Button", "xm  ym w200 h50 +Center", "Komorebic Save").OnEvent("Click", (*) => RunWait("komorebic quick-save-resize", , "Hide"))
myGui.Add("Button", "x+5 yp w200 h50 +Center", "Komorebic Load").OnEvent("Click", (*) => RunWait("komorebic quick-load-resize", , "Hide"))
myGui.Add("Button", "x+5 yp w200 h50 +Center", "Kill Komorebi").OnEvent("Click", (*) => Run("taskkill /f /im komorebi.exe", , "Hide"))
myGui.Add("Button", "x+5 yp w200 h50 +Center", "Start Komorebi").OnEvent("Click", (*) => Run("komorebi.exe", , "Hide"))
myGui.Add("Button", "x+5 yp w200 h50 +Center", "Kill Python").OnEvent("Click", (*) => Run("taskkill /f /im python.exe", , "Hide"))
myGui.Add("Button", "x+5 yp w200 h50 +Center", "Start Python (myGui)").OnEvent("Click", (*) => Run("C:\ms1\mypygui.py", , "Hide"))

myGui.Show()

myGui.OnEvent("Close", (*) => ExitApp())
