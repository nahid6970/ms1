#Requires AutoHotkey v2.0

::;pi::π
::;root::√
::;^2::²
::;^3::³
::;1/2::½
::;1/4::¼
::;degree::°
::;inf::∞
::;+-::±
::;int::∫
::;sum::∑
::;approx::≈
::;neq::≠
::;leq::≤
::;geq::≥
::;times::×
::;div::÷
::;cup::∪
::;cap::∩
::;==::⇒
::;*::×
::;note::🗗
::;??::প্রশ্নমতে,

; ^+1::SendText "¹"  ; Superscript 1
; ^+2::SendText "²"  ; Superscript 2
; ^+3::SendText "³"  ; Superscript 3
; ^+4::SendText "⁴"  ; Superscript 4
; ^+5::SendText "⁵"  ; Superscript 5
; ^+6::SendText "⁶"  ; Superscript 6
; ^+7::SendText "⁷"  ; Superscript 7
; ^+8::SendText "⁸"  ; Superscript 8






; ─────────────────────────────────────────────────────────────────────────────
; WordPower.ahk – Apply true superscript for 1–8 in Word via COM (AHK v2)
; ─────────────────────────────────────────────────────────────────────────────

; Ensure AHK v2 is installed. Run this script. Make sure Microsoft Word is already open.
; When Word is active, use Ctrl+Shift+1 .. Ctrl+Shift+8 to insert a superscript digit.

^+1::InsertSuperscript("1")
^+2::InsertSuperscript("2")
^+3::InsertSuperscript("3")
^+4::InsertSuperscript("4")
^+5::InsertSuperscript("5")
^+6::InsertSuperscript("6")
^+7::InsertSuperscript("7")
^+8::InsertSuperscript("8")
^+9::InsertSuperscript("9")
;─────────────────────────────────────────────────────────────────────────────
InsertSuperscript(digit)
{
    ; Try to get the running Word application. If Word is not open, do nothing.
    wordApp := ComObjActive("Word.Application") 
    if !IsObject(wordApp)
        return  ; no running Word instance

    sel := wordApp.Selection
    ; Turn on superscript for the next typed character
    sel.Font.Superscript := True
    sel.TypeText(digit)
    ; Turn superscript off so that subsequent typing is normal
    sel.Font.Superscript := False
}
;─────────────────────────────────────────────────────────────────────────────






; insertSuperscript(number) {
;     BlockInput true
;     Send(number)
;     Sleep 50
;     Send("^+{Left}")         ; Select the number
;     Sleep 50
;     Send("^+{=}")            ; Superscript ON
;     Sleep 50
;     Send("{Right}")          ; Move cursor after
;     Send("^+{=}")            ; Superscript OFF
;     BlockInput false
; }
; ^+1::insertSuperscript("1")
; ^+2::insertSuperscript("2")
; ^+3::insertSuperscript("3")
; ^+4::insertSuperscript("4")
; ^+5::insertSuperscript("5")
; ^+6::insertSuperscript("6")
; ^+7::insertSuperscript("7")
; ^+8::insertSuperscript("8")


; ^+1::
; {
;     Send("1")
;     Send("^+{Left}")         ; Select the 1
;     Send("^+{=}")            ; Apply superscript
;     Send("{Right}")          ; Move cursor after the number
;     Send("^+{=}")            ; Disable superscript (back to normal)
; }
; ^+2::
; {
;     Send("2")
;     Send("^+{Left}")
;     Send("^+{=}")
;     Send("{Right}")
;     Send("^+{=}")
; }
; ^+3::
; {
;     Send("3")
;     Send("^+{Left}")
;     Send("^+{=}")
;     Send("{Right}")
;     Send("^+{=}")
; }
; ^+4::
; {
;     Send("4")
;     Send("^+{Left}")
;     Send("^+{=}")
;     Send("{Right}")
;     Send("^+{=}")
; }
; ^+5::
; {
;     Send("5")
;     Send("^+{Left}")
;     Send("^+{=}")
;     Send("{Right}")
;     Send("^+{=}")
; }
; ^+6::
; {
;     Send("6")
;     Send("^+{Left}")
;     Send("^+{=}")
;     Send("{Right}")
;     Send("^+{=}")
; }
; ^+7::
; {
;     Send("7")
;     Send("^+{Left}")
;     Send("^+{=}")
;     Send("{Right}")
;     Send("^+{=}")
; }
; ^+8::
; {
;     Send("8")
;     Send("^+{Left}")
;     Send("^+{=}")
;     Send("{Right}")
;     Send("^+{=}")
; }
