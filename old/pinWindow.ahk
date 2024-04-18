;------------------------Directives & Script Initialization-----------------------------
#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
#Warn  ; Enable warnings to assist with detecting common errors.
#SingleInstance Force	; Ensures only one instance of the script runs.
#Persistent	; Makes the script persistent.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.
SetBatchLines -1	; Ensures the script is running at maximum speed by never sleeping.
ListLines Off	; Omits subsequently-executed lines from the history.
;---------------------------------------------------------------------------------------

;A pop-up Message Box notifying the user that the script has started.
MsgBox,,,Your script has started: `n%A_ScriptDir%,3


;------Hotkey------
<#p::  ;Win+P
  pinWindow()
  RETURN
;------------------
  
;---------------Function---------------
;Makes the active window AlwaysOnTop
pinWindow(targetWindow := "A")
{
	static pWnd := 0
	static pinned := FALSE
	tWnd := WinActive(targetWindow)	;Defines %tWnd% as the ahk_id for the target window
	IF (pinned NOT TRUE)
	{
		WinSet, AlwaysOnTop, Toggle, % "ahk_id " tWnd	;Sets the target window as AlwaysOnTop
		WinGetTitle, title, % "ahk_id " tWnd	;Retrieves the title for the target window.
		IF title	;Runs code if title isn't blank.
		{
			Gosub ChangeTitle
		}
		pinned := TRUE	;Used for UnpinWindow logic
		pWnd := tWnd	;Used for unpinning window before pinning the next window.
	}
	ELSE
	{
		Gosub UnpinWindow
	}
	
ChangeTitle:
	WinGet, ExStyle, ExStyle, % "ahk_id " tWnd	;Checks the style of the target window.
	IF (ExStyle & 0x8)	;0x8 is for AlwaysOnTop
	{
		WinSetTitle, % "ahk_id " tWnd,, %title% - AlwaysOnTop	;Adds "- AlwaysOnTop" to the window title.
	}
	ELSE
	{
		WinSetTitle, % "ahk_id " tWnd,, % RegexReplace(title, " - AlwaysOnTop")	;Removes "- AlwaysOnTop" to the window title.
	}
	RETURN
UnpinWindow:
	WinSet, AlwaysOnTop, Off, % "ahk_id " pWnd	;Sets the target window as AlwaysOnTop
	WinGetTitle, title, % "ahk_id " pWnd	;Retrieves the title for the target window.
	WinSetTitle, % "ahk_id " pWnd,, % RegexReplace(title, " - AlwaysOnTop")	;Removes indicator from the window title.
	IF (tWnd != pWnd)
	{
		WinSet, AlwaysOnTop, Toggle, % "ahk_id " tWnd	;Sets the target window as AlwaysOnTop
		WinGetTitle, title, % "ahk_id " tWnd	;Retrieves the title for the target window.
		IF title
		{
			Gosub ChangeTitle
		}
		pWnd := tWnd
	}
	ELSE
	{
		pinned := FALSE
	}
	RETURN
}
;--------------------------------------