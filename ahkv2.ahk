#Requires AutoHotkey v2.0

RAlt & Numpad1::Run("C:\msBackups\Display\DisplaySwitch.exe /internal", "", "Hide")
RAlt & Numpad2::Run("C:\msBackups\Display\DisplaySwitch.exe /external", "", "Hide")
RAlt & Numpad3::Run("C:\msBackups\Display\DisplaySwitch.exe /extend", "", "Hide")
