/*
Platform:           Win XP, Win 7
Author:             rbrtryn

Script Function:
Show/Hide hidden folders, files and extensions in Windows XP and Windows 7

All of these system settings are found in the Windows Registry at:
Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced

The specific values are:
    Hidden              Show hidden files?      ( 2 = no, 1 = yes )
    HideFileExt         Show file extensions?   ( 1 = no, 0 = yes )
    ShowSuperHidden     Show system files?      ( 0 = no, 1 = yes )

In order to show protected system files Windows requires that both 
the ShowSuperHidden and the hidden settings be set to yes, i.e. both set to 1
*/

; Auto-Execute
#NoEnv
#LTrim
#SingleInstance force
SendMode Input
SetKeyDelay 0    ; In case SendInput is not available
SetTitleMatchMode RegEx

GroupAdd ExplorerWindows, ahk_class ExploreWClass|CabinetWClass|Progman
global SubKey := "Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"

gosub MakeTrayMenu
return

; Toggle the show/hide of hidden files
^!h::
ToggleHiddenFilesStatus:
GetRegValue("Hidden") = 1
    ? SetRegValue("Hidden", 2)
    : SetRegValue("Hidden", 1)
Menu Tray, ToggleCheck, Show Hidden Files`tCtrl+Alt+H
gosub UpdateWindows
return

; Toggle the show/hide of system files
^!s::
ToggleSystemFilesStatus:
GetRegValue("ShowSuperHidden")
    ? SetRegValue("ShowSuperHidden", 0)
    : SetRegValue("ShowSuperHidden", 1)
Menu Tray, ToggleCheck, Show System Files`tCtrl+Alt+S
gosub UpdateWindows
return

; Toggle the show/hide of extensions for known file types
^!e::
ToggleFileExtStatus:
GetRegValue("HideFileExt")
    ? SetRegValue("HideFileExt", 0)
    : SetRegValue("HideFileExt", 1)
Menu Tray, ToggleCheck, Show File Extentions`tCtrl+Alt+E
gosub UpdateWindows
return

About:
MsgBox, , About ShowHide,
( 
    This program will show/hide hidden files, system files
    and file extensions via Hotkey or tray menu.

    The defined hotkeys are:
    Ctrl+Alt+H      Toggle the show/hide of hidden files
    Ctrl+Alt+E      Toggle the show/hide of file extensions
    Ctrl+Alt+S      Toggle the show/hide of system files

    Works on both Windows XP and Windows 7
    rbrtryn 2012
)
return

GetRegValue(ValueName) {
RegRead Value, HKCU, %SubKey%, %ValueName%
return Value
}

SetRegValue(ValueName, Value) {
RegWrite REG_DWORD, HKCU, %SubKey%, %ValueName%, %Value%
}

; Send a "Refresh" message to all of the Explorer windows including the Desktop
UpdateWindows:
Code := Is_In(A_OSVERSION, "WIN_XP", "WIN_2000") ? 28931 : 41504
WinGet WindowList, List, ahk_Group ExplorerWindows
Loop %WindowList%
    PostMessage 0x111, %Code%, , , % "ahk_id" WindowList%A_Index%
return

Is_In(pStr, pList*)
{
for key, val in pList
if (A_StringCaseSense = "Off" ? pStr = val : pStr == val)
  return key

return 0
}

MakeTrayMenu:
Menu Default Menu, Standard
Menu Tray, NoStandard
Menu Tray, Add, About, About
Menu Tray, Add
Menu Tray, Add, Default Menu, :Default Menu
Menu Tray, Add
Menu Tray, Add, Show System Files`tCtrl+Alt+S, ToggleSystemFilesStatus
Menu Tray, Add, Show File Extentions`tCtrl+Alt+E, ToggleFileExtStatus
Menu Tray, Add, Show Hidden Files`tCtrl+Alt+H, ToggleHiddenFilesStatus
Menu Tray, Default, Show Hidden Files`tCtrl+Alt+H

; If any of the menu items need to start off checked, take care of it here
if GetRegValue("Hidden") = 1
  Menu Tray, Check, Show Hidden Files`tCtrl+Alt+H
if GetRegValue("ShowSuperHidden") = 1
  Menu Tray, Check, Show System Files`tCtrl+Alt+S
if GetRegValue("HideFileExt") = 0
  Menu Tray, Check, Show File Extentions`tCtrl+Alt+E
return