^SPACE:: pinWindow()

pinWindow(targetWindow := "A")
{
	tWnd := WinActive(targetWindow)
	WinGetTitle, title, % "ahk_id " tWnd
	WinSetTitle, % "ahk_id " tWnd,, % instr(title," - AlwaysOnTop") ? RegexReplace(title, " - AlwaysOnTop") : title " - AlwaysOnTop"
	WinSet, AlwaysOnTop,, % "ahk_id " tWnd
}