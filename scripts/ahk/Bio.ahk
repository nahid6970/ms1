#Requires AutoHotkey v2.0

myGui := Gui("+AlwaysOnTop", "Custom Colored Buttons")
myGui.SetFont("s12 Bold", "Jetbrainsmono nfp")
myGui.MarginX := 20
myGui.MarginY := 20

; me
myGui.Add("Text", "xm  ym w200 +Border Center BackgroundFFCC00", "Nahid Ahmed")
myGui.Add("Text", "x+5 yp w100 +Border Center Background00CCFF", "en")         .OnEvent("Click", (*) => SendText("Nahid Ahmed"))
myGui.Add("Text", "x+5 yp w100 +Border Center BackgroundFF6666", "bn")         .OnEvent("Click", (*) => SendText("নাহিদ আহমেদ"))
myGui.Add("Text", "x+5 yp w100 +Border Center Background66FF66", "NID")        .OnEvent("Click", (*) => SendText("1505190676"))

; father
myGui.Add("Text", "xm y+5 w200 +Border Center BackgroundFFCC00", "Father")
myGui.Add("Text", "x+5 yp w100 +Border Center Background00CCFF", "en")         .OnEvent("Click", (*) => SendText("Nurul Amin"))
myGui.Add("Text", "x+5 yp w100 +Border Center BackgroundFF6666", "bn")         .OnEvent("Click", (*) => SendText("{U+09A8}{U+09C1}{U+09B0}{U+09C1}{U+09B2} {U+0986}{U+09AE}{U+09BF}{U+09A8}"))

; mother
myGui.Add("Text", "xm y+5 w200 +Border Center BackgroundFFCC00", "Mother")
myGui.Add("Text", "x+5 yp w100 +Border Center Background00CCFF", "en")         .OnEvent("Click", (*) => SendText("Nazma Begum"))
myGui.Add("Text", "x+5 yp w100 +Border Center BackgroundFF6666", "bn")         .OnEvent("Click", (*) => SendText("{U+09A8}{U+09BE}{U+099C}{U+09AE}{U+09BE} {U+09AC}{U+09C7}{U+0997}{U+09AE}"))

; Address
myGui.Add("Text", "xm y+5 w200 +Border Center BackgroundFFCC00", "Permanent Address").OnEvent("Click", (*) => SendText("Vill:Munshibari, P.O-Radhapur, 9 No Ward, Dist-Lakshmipur Post Code: 3706"))
myGui.Add("Text", "x+5 yp w100 +Border Center Background00CCFF", "P.O")              .OnEvent("Click", (*) => SendText("Radhapur"))
myGui.Add("Text", "x+5 yp w100 +Border Center BackgroundFF6666", "P.C")              .OnEvent("Click", (*) => SendText("3706"))

; ssc+hsc
myGui.Add("Text", "xm y+5 w410 +Border Center BackgroundFFCC00", "SCS & HSC Registration").OnEvent("Click", (*) => SendText("1110241111"))

; ssc
myGui.Add("Text", "xm y+5 w200 +Border Center BackgroundFFCC00", "SSC Roll").OnEvent("Click", (*) => SendText("402206"))
myGui.Add("Text", "x+5 yp w100 +Border Center Background00CCFF", "Y.R 2014").OnEvent("Click", (*) => SendText("2014"))
myGui.Add("Text", "x+5 yp w100 +Border Center BackgroundFF6666", "School")  .OnEvent("Click", (*) => SendText("Provati Uchya Bidyanikaton"))

; HSC
myGui.Add("Text", "xm y+5 w200 +Border Center BackgroundFFCC00", "HSC Roll").OnEvent("Click", (*) => SendText("510014"))
myGui.Add("Text", "x+5 yp w100 +Border Center Background00CCFF", "Y.R 2016").OnEvent("Click", (*) => SendText("2016"))
myGui.Add("Text", "x+5 yp w100 +Border Center BackgroundFF6666", "College") .OnEvent("Click", (*) => SendText("Notre Dame College"))

; BBA
myGui.Add("Text", "xm y+5 w200 +Border Center BackgroundFFCC00", "BBA Roll").OnEvent("Click", (*) => SendText("23-208"))
myGui.Add("Text", "x+5 yp w100 +Border Center Background00CCFF", "Y.R 2020").OnEvent("Click", (*) => SendText("2020"))
myGui.Add("Text", "x+5 yp w100 +Border Center BackgroundFF6666", "Versity") .OnEvent("Click", (*) => SendText("University of Dhaka"))
myGui.Add("Text", "x+5 yp w100 +Border Center BackgroundFF6666", "CGPA")    .OnEvent("Click", (*) => SendText("3.3"))

; MBA
myGui.Add("Text", "xm y+5 w200 +Border Center BackgroundFFCC00", "MBA Roll").OnEvent("Click", (*) => SendText("23-208"))
myGui.Add("Text", "x+5 yp w100 +Border Center Background00CCFF", "Y.R 2021").OnEvent("Click", (*) => SendText("2021"))
myGui.Add("Text", "x+5 yp w100 +Border Center BackgroundFF6666", "Versity") .OnEvent("Click", (*) => SendText("University of Dhaka"))
myGui.Add("Text", "x+5 yp w100 +Border Center BackgroundFF6666", "CGPA")    .OnEvent("Click", (*) => SendText("3.23"))





myGui.Show()
myGui.OnEvent("Close", (*) => ExitApp())

; Function to send text and briefly hide the GUI
SendText(text) {
    myGui.Hide()               ; Hide the GUI temporarily
    Sleep(200)                 ; Allow a short delay for the focus to shift
    Send(text)                 ; Send the text to the active field
    Sleep(200)                 ; Short delay after sending
    myGui.Show()               ; Show the GUI again
}