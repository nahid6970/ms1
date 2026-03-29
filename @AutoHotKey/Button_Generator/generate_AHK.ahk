#Requires AutoHotkey v2.0

myGui := Gui("+AlwaysOnTop", "Generated Keyboard")
myGui.SetFont("s12 Bold", "Jetbrainsmono nfp")
myGui.MarginX := 20
myGui.MarginY := 20

; Nahid Ahmed
myGui.SetFont("s12 Bold c000000", "Jetbrainsmono nfp")
myGui.Add("Text", "xm ym w150 h25 +Border Center BackgroundFFCC00", "Nahid Ahmed")
myGui.SetFont("s12 Bold cDefault", "Jetbrainsmono nfp")
btn := myGui.Add("Text", "x+5 yp w250 h25 +Border Center Background00CCFF", "en")
btn.SetFont("c000000")
btn.OnEvent("Click", (*) => SendText("Nahid Ahmed"))
btn.OnEvent("ContextMenu", (*) => (A_Clipboard := "Nahid Ahmed"))
btn := myGui.Add("Text", "x+5 yp w250 h25 +Border Center Background00CCFF", "bn")
btn.SetFont("c000000")
btn.OnEvent("Click", (*) => SendText("নাহিদ আহমেদ"))
btn.OnEvent("ContextMenu", (*) => (A_Clipboard := "নাহিদ আহমেদ"))
btn := myGui.Add("Text", "x+5 yp w250 h25 +Border Center Background00CCFF", "NID")
btn.SetFont("c000000")
btn.OnEvent("Click", (*) => SendText("1505190676"))
btn.OnEvent("ContextMenu", (*) => (A_Clipboard := "1505190676"))

; Father
myGui.SetFont("s12 Bold c000000", "Jetbrainsmono nfp")
myGui.Add("Text", "xm y+5 w150 h25 +Border Center BackgroundFFCC00", "Father")
myGui.SetFont("s12 Bold cDefault", "Jetbrainsmono nfp")
btn := myGui.Add("Text", "x+5 yp w250 h25 +Border Center Background00CCFF", "en")
btn.SetFont("c000000")
btn.OnEvent("Click", (*) => SendText("Nurul Amin"))
btn.OnEvent("ContextMenu", (*) => (A_Clipboard := "Nurul Amin"))
btn := myGui.Add("Text", "x+5 yp w250 h25 +Border Center Background00CCFF", "bn")
btn.SetFont("c000000")
btn.OnEvent("Click", (*) => SendText("নুরুল আমিন"))
btn.OnEvent("ContextMenu", (*) => (A_Clipboard := "নুরুল আমিন"))

myGui.Show()
myGui.OnEvent("Close", (*) => ExitApp())

; Function to send text and briefly hide the GUI
SendText(text) {
    myGui.Hide()
    Sleep(200)
    Send(text)
    Sleep(200)
    myGui.Show()
}