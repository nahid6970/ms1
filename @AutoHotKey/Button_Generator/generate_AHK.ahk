#Requires AutoHotkey v2.0

myGui := Gui("+AlwaysOnTop", "Generated Keyboard")
myGui.SetFont("s12 Bold", "Jetbrainsmono nfp")
myGui.MarginX := 20
myGui.MarginY := 20

; Example Name
myGui.SetFont("s12 Bold c000000", "Jetbrainsmono nfp")
myGui.Add("Text", "xm ym w150 h25 +Border Center BackgroundFFCC00", "Example Name")
myGui.SetFont("s12 Bold cDefault", "Jetbrainsmono nfp")
btn := myGui.Add("Text", "x+5 yp w250 h25 +Border Center Background00CCFF", "SSK")
btn.SetFont("c000000")
btn.OnEvent("Click", (*) => SendText("FFF"))
btn.OnEvent("ContextMenu", (*) => (A_Clipboard := "FFF"))
btn := myGui.Add("Text", "x+5 yp w250 h25 +Border Center Background00CCFF", "LMG")
btn.SetFont("c000000")
btn.OnEvent("Click", (*) => SendText("Fast"))
btn.OnEvent("ContextMenu", (*) => (A_Clipboard := "Fast"))

; RR
myGui.SetFont("s12 Bold c000000", "Jetbrainsmono nfp")
myGui.Add("Text", "xm y+5 w150 h25 +Border Center BackgroundFFCC00", "RR")
myGui.SetFont("s12 Bold cDefault", "Jetbrainsmono nfp")
btn := myGui.Add("Text", "x+5 yp w250 h25 +Border Center Background00CCFF", "F1")
btn.SetFont("c000000")
btn.OnEvent("Click", (*) => SendText("Field2"))
btn.OnEvent("ContextMenu", (*) => (A_Clipboard := "Field2"))

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