#Requires AutoHotkey v2.0

myGui := Gui("+AlwaysOnTop", "Generated Keyboard")
myGui.SetFont("s12 Bold", "Jetbrainsmono nfp")
myGui.MarginX := 20
myGui.MarginY := 20

; g0
myGui.SetFont("s12 Bold c000000", "Jetbrainsmono nfp")
titleCtrl := myGui.Add("Button", "xm ym w150 h25 +Border Center BackgroundFFCC00", "g0")
titleCtrl.OnEvent("Click", (*) => SendText("nahid6970@gmail.com"))
myGui.SetFont("s12 Bold cDefault", "Jetbrainsmono nfp")

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