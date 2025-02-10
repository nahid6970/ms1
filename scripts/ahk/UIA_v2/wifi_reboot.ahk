#Requires AutoHotkey v2.0 
#include <UIA>

Run("chrome.exe --new-window http://192.168.0.1/")
Sleep(3000)

chromeEl := UIA.ElementFromHandle("TL-WR840N - Google Chrome ahk_exe chrome.exe")

; Send the password and press Enter
try {
    chromeEl.ElementFromPath("V874").Value := "6123009riy"
    Send("{Enter}")
} catch {
    ; Do nothing if the element is not found
}
Sleep(2000)

chromeEl.ElementFromPath("VYqV87vr5").Click()
Sleep(1000)
chromeEl.ElementFromPath("VYqV87vr87v5").Click()
Sleep(1000)
chromeEl.ElementFromPath("VYrV0").Click()
Sleep(1000)
chromeEl.ElementFromPath("QYYY/Y/0").Click()
