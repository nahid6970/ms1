#Include C:\ms1\scripts\Autohtokey\AHK_BT\V1_4\Class_ImageButton.ahk
Gui, +AlwaysOnTop
Gui, Margin, 20, 20
Gui,Font,s12 Normal Bold,Jetbrainsmono nfp

Gui, Add, Button, xm ym h30 gkomorebic_save ,Komorebic Save
Gui, Add, Button, x+5 yp h30 gkomorebic_load ,Komorebic Load

Gui, Add, Button, xm y+5 w250 h30, Komorebic
Gui, Add, Button, x+5 yp w100 h30 hWndhBtn61 gKill_Komorebi, % "Kill"
IBBtnStyles := [ [0, 0x80F0B9B8, , , 0, , 0x80D43F3A, 2]      ; normal
			   , [0, 0x80E27C79, , , 0, , 0x80D43F3A, 2]      ; hover
			   , [0, 0x80D43F3A, , , 0, , 0x80D43F3A, 2]      ; pressed
			   , [0, 0x80F0F0F0, , , 0, , 0x80D43F3A, 2] ]
ImageButton.Create(hBtn61, IBBtnStyles*)
Gui, Add, Button, x+5 yp w100 h30 hWndhBtn63 gStart_Komorebi, % "Start"
IBBtnStyles := [ [0, 0x80C6E6C6, , , 0, , 0x805CB85C, 2]      ; normal
			   , [0, 0x8091CF91, , , 0, , 0x805CB85C, 2]      ; hover
			   , [0, 0x805CB85C, , , 0, , 0x805CB85C, 2]      ; pressed
			   , [0, 0x80F0F0F0, , , 0, , 0x805CB85C, 2] ]
ImageButton.Create(hBtn63, IBBtnStyles*)

Gui, Add, Button, xm y+5 w250 h30, Explorer
Gui, Add, Button, x+5 yp w100 h30 hWndhBtn61 gkill_Explorer, % "Kill"
IBBtnStyles := [ [0, 0x80F0B9B8, , , 0, , 0x80D43F3A, 2]      ; normal
			   , [0, 0x80E27C79, , , 0, , 0x80D43F3A, 2]      ; hover
			   , [0, 0x80D43F3A, , , 0, , 0x80D43F3A, 2]      ; pressed
			   , [0, 0x80F0F0F0, , , 0, , 0x80D43F3A, 2] ]
ImageButton.Create(hBtn61, IBBtnStyles*)
Gui, Add, Button, x+5 yp w100 h30 hWndhBtn63 gstart_Explorer, % "Start"
IBBtnStyles := [ [0, 0x80C6E6C6, , , 0, , 0x805CB85C, 2]      ; normal
			   , [0, 0x8091CF91, , , 0, , 0x805CB85C, 2]      ; hover
			   , [0, 0x805CB85C, , , 0, , 0x805CB85C, 2]      ; pressed
			   , [0, 0x80F0F0F0, , , 0, , 0x805CB85C, 2] ]
ImageButton.Create(hBtn63, IBBtnStyles*)

Gui, Add, Button, xm y+5 w250 h30, Powershell
Gui, Add, Button, x+5 yp w100 h30 hWndhBtn61 gKill_PWSH, % "PWSH 7"
IBBtnStyles := [ [0, 0x80F0B9B8, , , 0, , 0x80D43F3A, 2]      ; normal
			   , [0, 0x80E27C79, , , 0, , 0x80D43F3A, 2]      ; hover
			   , [0, 0x80D43F3A, , , 0, , 0x80D43F3A, 2]      ; pressed
			   , [0, 0x80F0F0F0, , , 0, , 0x80D43F3A, 2] ]
ImageButton.Create(hBtn61, IBBtnStyles*)
Gui, Add, Button, x+5 yp w100 h30 hWndhBtn61 gKill_Powershell, % "PWSH 1"
IBBtnStyles := [ [0, 0x80F0B9B8, , , 0, , 0x80D43F3A, 2]      ; normal
			   , [0, 0x80E27C79, , , 0, , 0x80D43F3A, 2]      ; hover
			   , [0, 0x80D43F3A, , , 0, , 0x80D43F3A, 2]      ; pressed
			   , [0, 0x80F0F0F0, , , 0, , 0x80D43F3A, 2] ]
ImageButton.Create(hBtn61, IBBtnStyles*)

Gui, Add, Button, xm y+5 w250 h30, Python
Gui, Add, Button, x+5 yp w100 h30 hWndhBtn61 gKill_Python, % "Kill"
IBBtnStyles := [ [0, 0x80F0B9B8, , , 0, , 0x80D43F3A, 2]      ; normal
			   , [0, 0x80E27C79, , , 0, , 0x80D43F3A, 2]      ; hover
			   , [0, 0x80D43F3A, , , 0, , 0x80D43F3A, 2]      ; pressed
			   , [0, 0x80F0F0F0, , , 0, , 0x80D43F3A, 2] ]
ImageButton.Create(hBtn61, IBBtnStyles*)
Gui, Add, Button, x+5 yp w100 h30 hWndhBtn63 gStart_Python_mypygui_showT, % "mypygui-S"
IBBtnStyles := [ [0, 0x80C6E6C6, , , 0, , 0x805CB85C, 2]      ; normal
			   , [0, 0x8091CF91, , , 0, , 0x805CB85C, 2]      ; hover
			   , [0, 0x805CB85C, , , 0, , 0x805CB85C, 2]      ; pressed
			   , [0, 0x80F0F0F0, , , 0, , 0x805CB85C, 2] ]
ImageButton.Create(hBtn63, IBBtnStyles*)
Gui, Add, Button, x+5 yp w100 h30 hWndhBtn63 gStart_Python_mypygui_hideT, % "mypygui-H"
IBBtnStyles := [ [0, 0x80C6E6C6, , , 0, , 0x805CB85C, 2]      ; normal
			   , [0, 0x8091CF91, , , 0, , 0x805CB85C, 2]      ; hover
			   , [0, 0x805CB85C, , , 0, , 0x805CB85C, 2]      ; pressed
			   , [0, 0x80F0F0F0, , , 0, , 0x805CB85C, 2] ]
ImageButton.Create(hBtn63, IBBtnStyles*)

Gui, Show,, Image Buttons
return

GuiClose:
ExitApp ; Ensure the script exits entirely
return

komorebic_save:
RunWait, komorebic quick-save-resize,,Hide
return
komorebic_load:
RunWait, komorebic quick-load-resize,,Hide
return
Kill_Komorebi:
Run, taskkill /f /im komorebi.exe,,Hide
return
Start_Komorebi:
Run, komorebi.exe,,Hide
return

Kill_Python:
Run, taskkill /f /im python.exe,,Hide
return
Start_Python_mypygui_hideT:
Run, C:\ms1\mypygui.py,,Hide
return
Start_Python_mypygui_showT:
    Run, cmd /k python "C:\ms1\mypygui.py", , UseErrorLevel
    if (ErrorLevel)
    {
        MsgBox, Script failed to execute. Error code: %ErrorLevel%
    }
return

Kill_PWSH:
Run, taskkill /f /im pwsh.exe,,Hide
return
Kill_Powershell:
Run, taskkill /f /im powershell.exe,,Hide
return
Kill_CMD:
Run, taskkill /f /im cmd.exe,,Hide
return

start_Explorer:
Run, pwsh -c explorer.exe,,Hide
return
kill_Explorer:
Run, taskkill /f /im explorer.exe,,Hide
return

; extra unused
start_RunningAppsMonitor:
Run, python.exe C:\ms1\running_apps.py,,Hide
return
start_cmd_asAdmin:
Run, pwsh -Command "cd $env:USERPROFILE; Start-Process pwsh -Verb RunAs",,Hide
return
start_Run:
Run, "C:\Users\nahid\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\System Tools\Run.lnk"
return
