#Requires AutoHotkey v2.0

myGui := Gui("+AlwaysOnTop", "Generated Keyboard")
myGui.SetFont("s12 Bold", "Jetbrainsmono nfp")
myGui.MarginX := 20
myGui.MarginY := 20

; Example Name
myGui.SetFont("s12 Bold c000000", "Jetbrainsmono nfp")
myGui.Add("Text", "xm ym w350 h25 +Border Center BackgroundFFCC00", "Example Name")
myGui.SetFont("s12 Bold cDefault", "Jetbrainsmono nfp")
btn := myGui.Add("Text", "x+5 yp w250 h25 +Border Center Background00CCFF", "BangladeshTT")
btn.SetFont("c000000")
btn.OnEvent("Click", (*) => SendText("বাংলাদেশের কয়টি বিভাগ রয়েছে"))
btn.OnEvent("ContextMenu", (*) => (A_Clipboard := "বাংলাদেশের কয়টি বিভাগ রয়েছে"))
btn := myGui.Add("Text", "x+5 yp w250 h25 +Border Center Background00CCFF", "sadasdasd")
btn.SetFont("c000000")
btn.OnEvent("Click", (*) => SendText("asdasdasdasdasdasdasdasdasdasd asdasdasda"))
btn.OnEvent("ContextMenu", (*) => (A_Clipboard := "asdasdasdasdasdasdasdasdasdasd asdasdasda"))

; dddddddddddddddddddddddddddddddd
myGui.SetFont("s12 Bold c000000", "Jetbrainsmono nfp")
myGui.Add("Text", "xm y+5 w350 h25 +Border Center BackgroundFFCC00", "dddddddddddddddddddddddddddddddd")
myGui.SetFont("s12 Bold cDefault", "Jetbrainsmono nfp")
btn := myGui.Add("Text", "x+5 yp w250 h25 +Border Center Background00CCFF", "dddddddddddddddd")
btn.SetFont("c000000")
btn.OnEvent("Click", (*) => SendText("dddddddddddddddddddddddd"))
btn.OnEvent("ContextMenu", (*) => (A_Clipboard := "dddddddddddddddddddddddd"))

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