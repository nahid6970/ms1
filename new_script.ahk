#Requires AutoHotkey v2.0

myGui := Gui("+Resize +AlwaysOnTop", "Custom Colored Buttons")
myGui.SetFont("s12 Bold", "Jetbrainsmono nfp")
myGui.MarginX := 20
myGui.MarginY := 20

; Add buttons styled as text (with actions)
btn1 := myGui.Add("Text", "xm ym w200 h50 +Border Center BackgroundFFCC00", "Nahid Ahmed")
btn2 := myGui.Add("Text", "x+5 yp w100 h50 +Border Center Background00CCFF", "en")
btn3 := myGui.Add("Text", "x+5 yp w100 h50 +Border Center BackgroundFF6666", "bn")
btn4 := myGui.Add("Text", "x+5 yp w100 h50 +Border Center Background66FF66", "NID")

; Add non-interactive text field (button with no effect)
nonInteractiveText := myGui.Add("Text", "x+5 yp w200 h50 +Border Center BackgroundDDDDDD", "This is a text field")
; Note: No event is attached to `nonInteractiveText`, so it does nothing when clicked

; Add click events to send text to the active field
btn1.OnEvent("Click", (*) => SendText("Nahid Ahmed"))
btn2.OnEvent("Click", (*) => SendText("en"))
btn3.OnEvent("Click", (*) => SendText("নাহিদ আহমেদ")) ; Bangla text
btn4.OnEvent("Click", (*) => SendText("1505190676"))   ; NID

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
