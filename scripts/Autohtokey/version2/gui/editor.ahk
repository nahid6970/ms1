#Requires AutoHotkey v2.0

myGui := Gui("+AlwaysOnTop -Caption", "Control Panel")
myGui.SetFont("s12 Bold", "Jetbrainsmono nfp")
myGui.MarginX := 1
myGui.MarginY := 1

; Set icon font size and add vertically stacked icon buttons
myGui.SetFont("s12 Bold", "Jetbrainsmono nfp")

; Close (✕) and Reload (↻)
myGui.Add("Text", "xm y+5 BackgroundFF5C5C cFFFFFF w30 +Center +Border", "✕").OnEvent("Click", (*) => ExitApp())
myGui.Add("Text", "xm y+5 BackgroundFFD966 c000000 w30 +Center +Border", "↻").OnEvent("Click", (*) => Reload())

; Functional buttons
myGui.Add("Text", "xm y+5 Background31ffc1 c000000 w30 +Center +Border", "").OnEvent("Click", (*) => (myGui.Destroy(), Sleep(500), Send("#+f"))) ; Text Grab
myGui.Add("Text", "xm y+5 Background31ffc1 c000000 w30 +Center +Border", "").OnEvent("Click", (*) =>  (myGui.Destroy(), Sleep(500), pasteshit(), Reload()))
myGui.Add("Text", "xm y+5 Background31ffc1 c000000 w30 +Center +Border", "").OnEvent("Click", (*) => (Run("C:\ms1\scripts\xy\XY_CroosHair.py",, "Hide"))) ; CrossHair
myGui.Add("Text", "xm y+5 Background31ffc1 cec2d47 w30 +Center +Border", "").OnEvent("Click", (*) => (Run("C:\ms1\scripts\Locker.py",, "Hide"))) ; Locker

; Add the Ctrl + WheelDown button (using a down-arrow icon “🔽”)
myGui.Add("Text" , "xm y+5 Background31ffc1 c000000 w30 +Center +Border" , "🔽" )
.OnEvent("Click"
    , (*) => (
        ; Activate your app by its executable name
        WinActivate("ahk_exe dnplayer.exe")
        Sleep(1000)           ; give it a moment to become active
        Send("{Ctrl down}")
        Send("{WheelDown}")
        Send("{WheelDown}")
        Send("{WheelDown}")
        Send("{WheelDown}")
        Send("{WheelDown}")
        Send("{WheelDown}")
        Send("{WheelDown}")
        Send("{Ctrl up}")
    )
)


; Show temporarily to calculate actual size
myGui.Show("x0 y0 AutoSize")
Sleep(10) ; brief pause to ensure size is updated

; Now get real size
myGui.GetClientPos(, , &w, &h)
screenW := 1920
screenH := 1080
x := screenW - w
y := (screenH - h) // 2

; Move to actual position
myGui.Move(x, y)




pasteshit() {
    send("^!{Numpad2}")
    Sleep(100)
    SendText(" ➔ ")
    Sleep(100)
    send("^!{Numpad1}")
    Sleep(100)
    ; SendText(",")
    Sleep(100)
    Send("{Enter}")
}
