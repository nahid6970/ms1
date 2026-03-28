#Requires AutoHotkey v2.0

myGui := Gui("+AlwaysOnTop", "Generated Keyboard")
myGui.SetFont("s12 Bold", "Jetbrainsmono nfp")
myGui.MarginX := 20
myGui.MarginY := 20

; GG
myGui.SetFont("s12 Bold c55AAFF", "Jetbrainsmono nfp")
myGui.Add("Text", "xm ym w200 h25 +Border Center Background4A7F04", "GG")
myGui.SetFont("s12 Bold cDefault", "Jetbrainsmono nfp")
btn := myGui.Add("Text", "x+5 yp w100 h25 +Border Center Background0000FF", "ez")
btn.SetFont("cFF0B75")
btn.OnEvent("Click", (*) => SendText("asdasdasdasdadsadasd"))
btn.OnEvent("ContextMenu", (*) => (A_Clipboard := "asdasdasdasdadsadasd"))
btn := myGui.Add("Text", "x+5 yp w100 h25 +Border Center Background00CCFF", "asdasdasd")
btn.SetFont("c000000")
btn.OnEvent("Click", (*) => SendText("asdasdasdasdasd"))
btn.OnEvent("ContextMenu", (*) => (A_Clipboard := "asdasdasdasdasd"))
btn := myGui.Add("Text", "x+5 yp w100 h25 +Border Center Background00CCFF", "asdasd")
btn.SetFont("c000000")
btn.OnEvent("Click", (*) => SendText("asdasdasdasd"))
btn.OnEvent("ContextMenu", (*) => (A_Clipboard := "asdasdasdasd"))
btn := myGui.Add("Text", "x+5 yp w100 h25 +Border Center Background00CCFF", "asdasd")
btn.SetFont("c000000")
btn.OnEvent("Click", (*) => SendText("asdasdasdad asdasd as asda ds asd asda ds asd asd ad as dsdasd asda sdas s sasd as"))
btn.OnEvent("ContextMenu", (*) => (A_Clipboard := "asdasdasdad asdasd as asda ds asd asda ds asd asd ad as dsdasd asda sdas s sasd as"))

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