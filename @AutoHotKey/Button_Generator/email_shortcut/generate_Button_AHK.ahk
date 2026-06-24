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

; g1
myGui.SetFont("s12 Bold c000000", "Jetbrainsmono nfp")
titleCtrl := myGui.Add("Button", "xm y+5 w150 h25 +Border Center BackgroundFFCC00", "g1")
titleCtrl.OnEvent("Click", (*) => SendText("nahid69701@gmail.com"))
myGui.SetFont("s12 Bold cDefault", "Jetbrainsmono nfp")

; g2
myGui.SetFont("s12 Bold c000000", "Jetbrainsmono nfp")
titleCtrl := myGui.Add("Button", "xm y+5 w150 h25 +Border Center BackgroundFFCC00", "g2")
titleCtrl.OnEvent("Click", (*) => SendText("nahid69702@gmail.com"))
myGui.SetFont("s12 Bold cDefault", "Jetbrainsmono nfp")

; g3
myGui.SetFont("s12 Bold c000000", "Jetbrainsmono nfp")
titleCtrl := myGui.Add("Button", "xm y+5 w150 h25 +Border Center BackgroundFFCC00", "g3")
titleCtrl.OnEvent("Click", (*) => SendText("nahid69703@gmail.com"))
myGui.SetFont("s12 Bold cDefault", "Jetbrainsmono nfp")

; g4
myGui.SetFont("s12 Bold c000000", "Jetbrainsmono nfp")
titleCtrl := myGui.Add("Button", "xm y+5 w150 h25 +Border Center BackgroundFFCC00", "g4")
titleCtrl.OnEvent("Click", (*) => SendText("nahid69704@gmail.com"))
myGui.SetFont("s12 Bold cDefault", "Jetbrainsmono nfp")

; g5
myGui.SetFont("s12 Bold c000000", "Jetbrainsmono nfp")
titleCtrl := myGui.Add("Button", "xm y+5 w150 h25 +Border Center BackgroundFFCC00", "g5")
titleCtrl.OnEvent("Click", (*) => A_Clipboard := "nahid69705@gmail.com")
myGui.SetFont("s12 Bold cDefault", "Jetbrainsmono nfp")

; 
myGui.SetFont("s12 Bold c000000", "Jetbrainsmono nfp")
titleCtrl := myGui.Add("Button", "xm y+5 w150 h25 +Border Center BackgroundFFCC00", "")
titleCtrl.OnEvent("Click", (*) => SendText(""))
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