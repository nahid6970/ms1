#Requires AutoHotkey v2.0 
#include <UIA>
Run("control.exe folders")
Sleep(1000)

explorerEl := UIA.ElementFromHandle("File Explorer Options ahk_exe explorer.exe")
explorerEl.ElementFromPath("IJq").Click()
