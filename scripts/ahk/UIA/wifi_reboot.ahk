#Requires AutoHotkey v2.0 
#include <UIA>

Run("chrome.exe --new-window http://192.168.0.1/")
Sleep(3000) ; Wait for Chrome to load the page

chromeEl := UIA.ElementFromHandle("TL-WR840N - Google Chrome ahk_exe chrome.exe")
chromeEl.ElementFromPath("VYqV87vr5").Click()
chromeEl.ElementFromPath("VYqV87vr87v5").Click()
chromeEl.ElementFromPath("VYrV0").Click()
