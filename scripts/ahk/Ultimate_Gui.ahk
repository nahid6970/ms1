#Requires AutoHotkey v2.0

#Requires AutoHotkey v2.0

myGui := Gui("+AlwaysOnTop", "Control Panel")
myGui.SetFont("s12 Bold", "Jetbrainsmono nfp")
myGui.MarginX := 20
myGui.MarginY := 20

; Add buttons with labels for each command and bind actions to them
myGui.Add("Button", "xm ym w200 h50 +Center", "Komorebic Save").OnEvent("Click", komorebic_save)
myGui.Add("Button", "x+5 yp w200 h50 +Center", "Komorebic Load").OnEvent("Click", komorebic_load)
myGui.Add("Button", "x+5 yp w200 h50 +Center", "Kill Komorebi").OnEvent("Click", Kill_Komorebi)
myGui.Add("Button", "x+5 yp w200 h50 +Center", "Start Komorebi").OnEvent("Click", Start_Komorebi)
myGui.Add("Button", "x+5 yp w200 h50 +Center", "Kill Python").OnEvent("Click", Kill_Python)
myGui.Add("Button", "x+5 yp w200 h50 +Center", "Start Python (myGui)").OnEvent("Click", Start_Python_mypygui_hideT)

myGui.Show()

myGui.OnEvent("Close", (*) => ExitApp())

; Function definitions for the button actions
komorebic_save(*) {
    RunWait("komorebic quick-save-resize", , "Hide")
}

komorebic_load(*) {
    RunWait("komorebic quick-load-resize", , "Hide")
}

Kill_Komorebi(*) {
    Run("taskkill /f /im komorebi.exe", , "Hide")
}

Start_Komorebi(*) {
    Run("komorebi.exe", , "Hide")
}

Kill_Python(*) {
    Run("taskkill /f /im python.exe", , "Hide")
}

Start_Python_mypygui_hideT(*) {
    Run("C:\ms1\mypygui.py", , "Hide")
}
