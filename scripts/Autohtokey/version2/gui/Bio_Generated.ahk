#Requires AutoHotkey v2.0

myGui := Gui("+AlwaysOnTop", "Generated Keyboard")
myGui.SetFont("s12 Bold", "Jetbrainsmono nfp")
myGui.MarginX := 20
myGui.MarginY := 20

; GG
myGui.Add("Text", "xm ym w200 +Border Center BackgroundFFCC00", "GG")
myGui.Add("Text", "x+5 yp w100 +Border Center Background0000FF", "ez") .OnEvent("Click", (*) => SendText("asdasdasdasdadsadasd"))
myGui.Add("Text", "x+5 yp w100 +Border Center Background00CCFF", "asdasdasd") .OnEvent("Click", (*) => SendText("asdasdasdasdasd"))
myGui.Add("Text", "x+5 yp w100 +Border Center Background00CCFF", "asdasd") .OnEvent("Click", (*) => SendText("asdasdasdasd"))
myGui.Add("Text", "x+5 yp w100 +Border Center Background00CCFF", "asdasd") .OnEvent("Click", (*) => SendText("asdasdasdad asdasd as asda ds asd asda ds asd asd ad as dsdasd asda sdas s sasd as"))

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