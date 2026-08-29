#Requires AutoHotkey v2.0
; ScreenDimmer
; AutoHotkey Version: 2.x
; Language:       English
; Platform:       Win10/11
; Author:         A.N.Other <myemail@nowhere.com>
;
; Script Function:
;	To dim or lighten the screen brightness

#SingleInstance Force
SetWorkingDir(A_ScriptDir)

DimmerGui := Gui("+AlwaysOnTop", "Screen Brightness")
DimmerGui.Add("Text", "x0 y0", "Dimmer")
DimmerGui.Add("Text", "x0 y0", "Brighter")
SD_MySlider := DimmerGui.Add("Slider", "W200 x50 y5 AltSubmit Tooltip Range0-180 vSD_MySlider")
SD_MySlider.OnEvent("Change", SD_Dimmer)
SD_MySlider.Value := 128 ; Set to 128 directly
SB := DimmerGui.Add("StatusBar")
SB.SetText("Default Brightness 128 (Click Status Bar to Reset)")
SB.OnEvent("Click", SD_Reset)

DisplaySetBrightness(128)
SD_MySlider.Value := 128
DimmerGui.Show("W300")

SD_Dimmer(*) {
  Saved := DimmerGui.Submit(false)
  ; If moving slider right (increasing value) should increase brightness:
  ; We just use the value directly.
  Brightness := Saved.SD_MySlider
  DisplaySetBrightness(Brightness)
  SB.SetText("Brightness level is " . Brightness . " (Click Status Bar to Reset)")
}

DisplaySetBrightness(Br := 128) {
  static GR := Buffer(1536)
  Loop 256 {
    n := (Br + 128) * (A_Index - 1)
    val := (n > 65535 ? 65535 : n)
    NumPut("UShort", val, GR, 2 * (A_Index - 1))
    NumPut("UShort", val, GR, 512 + 2 * (A_Index - 1))
    NumPut("UShort", val, GR, 1024 + 2 * (A_Index - 1))
  }
  hDC := DllCall("GetDC", "Ptr", 0, "Ptr")
  DllCall("SetDeviceGammaRamp", "Ptr", hDC, "Ptr", GR)
  DllCall("ReleaseDC", "Ptr", 0, "Ptr", hDC)
}

SD_Reset(*) {
  DisplaySetBrightness(128)
  SD_MySlider.Value := 128
  SB.SetText("Default Brightness 128 (Click Status Bar to Reset)")
}
