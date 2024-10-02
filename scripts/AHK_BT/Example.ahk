#NoEnv
SetBatchLines, -1

; Class ImageButton by just me
; https://www.autohotkey.com/boards/viewtopic.php?t=1103
#Include C:\ms1\scripts\AHK_BT\V1_4\Class_ImageButton.ahk
; for v1.5 add UseGDIP.ahk or Include them into Class_ImageButton.ahk
; #Include UseGDIP.ahk


Gui, Margin, 20, 20
Gui, Font, s11 normal, Segoe UI

; ---------------------------------------------------------------------------------------

Gui, Add, Button, xm ym w80 h24 hWndhBtn11, % "Critical"
IBBtnStyles := [ [0, 0x80F0F0F0, , , 0, , 0x80D43F3A, 1]      ; normal
			   , [0, 0x80F0B9B8, , , 0, , 0x80D43F3A, 1]      ; hover
			   , [0, 0x80E27C79, , , 0, , 0x80D43F3A, 1]      ; pressed
			   , [0, 0x80F0F0F0, , , 0, , 0x80D43F3A, 1] ]
ImageButton.Create(hBtn11, IBBtnStyles*)


Gui, Add, Button, x+20 yp w80 h24 hWndhBtn12, % "Warning"
IBBtnStyles := [ [0, 0x80F0F0F0, , , 0, , 0x80F0AD4E, 1]      ; normal
			   , [0, 0x80FCEFDC, , , 0, , 0x80F0AD4E, 1]      ; hover
			   , [0, 0x80F6CE95, , , 0, , 0x80F0AD4E, 1]      ; pressed
			   , [0, 0x80F0F0F0, , , 0, , 0x80F0AD4E, 1] ]
ImageButton.Create(hBtn12, IBBtnStyles*)


Gui, Add, Button, x+20 yp w80 h24 hWndhBtn13, % "Success"
IBBtnStyles := [ [0, 0x80F0F0F0, , , 0, , 0x805CB85C, 1]      ; normal
			   , [0, 0x80C6E6C6, , , 0, , 0x805CB85C, 1]      ; hover
			   , [0, 0x8091CF91, , , 0, , 0x805CB85C, 1]      ; pressed
			   , [0, 0x80F0F0F0, , , 0, , 0x805CB85C, 1] ]
ImageButton.Create(hBtn13, IBBtnStyles*)


Gui, Add, Button, x+20 yp w80 h24 hWndhBtn14, % "Info"
IBBtnStyles := [ [0, 0x80F0F0F0, , , 0, , 0x8046B8DA, 1]      ; normal
			   , [0, 0x80C6E9F4, , , 0, , 0x8046B8DA, 1]      ; hover
			   , [0, 0x8086D0E7, , , 0, , 0x8046B8DA, 1]      ; pressed
			   , [0, 0x80F0F0F0, , , 0, , 0x8046B8DA, 1] ]
ImageButton.Create(hBtn14, IBBtnStyles*)

; ---------------------------------------------------------------------------------------

Gui, Add, Button, x+20 yp w80 h24 hWndhBtn21, % "Critical"
IBBtnStyles := [ [0, 0x80F0B9B8, , , 0, , 0x80D43F3A, 1]      ; normal
			   , [0, 0x80E27C79, , , 0, , 0x80D43F3A, 1]      ; hover
			   , [0, 0x80D43F3A, , , 0, , 0x80D43F3A, 1]      ; pressed
			   , [0, 0x80F0F0F0, , , 0, , 0x80D43F3A, 1] ]
ImageButton.Create(hBtn21, IBBtnStyles*)


Gui, Add, Button, x+20 yp w80 h24 hWndhBtn22, % "Warning"
IBBtnStyles := [ [0, 0x80FCEFDC, , , 0, , 0x80F0AD4E, 1]      ; normal
			   , [0, 0x80F6CE95, , , 0, , 0x80F0AD4E, 1]      ; hover
			   , [0, 0x80F0AD4E, , , 0, , 0x80F0AD4E, 1]      ; pressed
			   , [0, 0x80F0F0F0, , , 0, , 0x80F0AD4E, 1] ]
ImageButton.Create(hBtn22, IBBtnStyles*)


Gui, Add, Button, x+20 yp w80 h24 hWndhBtn23, % "Success"
IBBtnStyles := [ [0, 0x80C6E6C6, , , 0, , 0x805CB85C, 1]      ; normal
			   , [0, 0x8091CF91, , , 0, , 0x805CB85C, 1]      ; hover
			   , [0, 0x805CB85C, , , 0, , 0x805CB85C, 1]      ; pressed
			   , [0, 0x80F0F0F0, , , 0, , 0x805CB85C, 1] ]
ImageButton.Create(hBtn23, IBBtnStyles*)


Gui, Add, Button, x+20 yp w80 h24 hWndhBtn24, % "Info"
IBBtnStyles := [ [0, 0x80C6E9F4, , , 0, , 0x8046B8DA, 1]      ; normal
			   , [0, 0x8086D0E7, , , 0, , 0x8046B8DA, 1]      ; hover
			   , [0, 0x8046B8DA, , , 0, , 0x8046B8DA, 1]      ; pressed
			   , [0, 0x80F0F0F0, , , 0, , 0x8046B8DA, 1] ]
ImageButton.Create(hBtn24, IBBtnStyles*)

; ---------------------------------------------------------------------------------------

Gui, Add, Button, xm y+20 w80 h24 hWndhBtn31, % "Critical"
IBBtnStyles := [ [0, 0x80F0F0F0, , , 8, 0xFFF0F0F0, 0x80D43F3A, 1]      ; normal
			   , [0, 0x80F0B9B8, , , 8, 0xFFF0F0F0, 0x80D43F3A, 1]      ; hover
			   , [0, 0x80E27C79, , , 8, 0xFFF0F0F0, 0x80D43F3A, 1]      ; pressed
			   , [0, 0x80F0F0F0, , , 8, 0xFFF0F0F0, 0x80D43F3A, 1] ]
ImageButton.Create(hBtn31, IBBtnStyles*)


Gui, Add, Button, x+20 yp w80 h24 hWndhBtn32, % "Warning"
IBBtnStyles := [ [0, 0x80F0F0F0, , , 8, 0xFFF0F0F0, 0x80F0AD4E, 1]      ; normal
			   , [0, 0x80FCEFDC, , , 8, 0xFFF0F0F0, 0x80F0AD4E, 1]      ; hover
			   , [0, 0x80F6CE95, , , 8, 0xFFF0F0F0, 0x80F0AD4E, 1]      ; pressed
			   , [0, 0x80F0F0F0, , , 8, 0xFFF0F0F0, 0x80F0AD4E, 1] ]
ImageButton.Create(hBtn32, IBBtnStyles*)


Gui, Add, Button, x+20 yp w80 h24 hWndhBtn33, % "Success"
IBBtnStyles := [ [0, 0x80F0F0F0, , , 8, 0xFFF0F0F0, 0x805CB85C, 1]      ; normal
			   , [0, 0x80C6E6C6, , , 8, 0xFFF0F0F0, 0x805CB85C, 1]      ; hover
			   , [0, 0x8091CF91, , , 8, 0xFFF0F0F0, 0x805CB85C, 1]      ; pressed
			   , [0, 0x80F0F0F0, , , 8, 0xFFF0F0F0, 0x805CB85C, 1] ]
ImageButton.Create(hBtn33, IBBtnStyles*)


Gui, Add, Button, x+20 yp w80 h24 hWndhBtn34, % "Info"
IBBtnStyles := [ [0, 0x80F0F0F0, , , 8, 0xFFF0F0F0, 0x8046B8DA, 1]      ; normal
			   , [0, 0x80C6E9F4, , , 8, 0xFFF0F0F0, 0x8046B8DA, 1]      ; hover
			   , [0, 0x8086D0E7, , , 8, 0xFFF0F0F0, 0x8046B8DA, 1]      ; pressed
			   , [0, 0x80F0F0F0, , , 8, 0xFFF0F0F0, 0x8046B8DA, 1] ]
ImageButton.Create(hBtn34, IBBtnStyles*)

; ---------------------------------------------------------------------------------------

Gui, Add, Button, x+20 yp w80 h24 hWndhBtn41, % "Critical"
IBBtnStyles := [ [0, 0x80F0B9B8, , , 8, 0xFFF0F0F0, 0x80D43F3A, 1]      ; normal
			   , [0, 0x80E27C79, , , 8, 0xFFF0F0F0, 0x80D43F3A, 1]      ; hover
			   , [0, 0x80D43F3A, , , 8, 0xFFF0F0F0, 0x80D43F3A, 1]      ; pressed
			   , [0, 0x80F0F0F0, , , 8, 0xFFF0F0F0, 0x80D43F3A, 1] ]
ImageButton.Create(hBtn41, IBBtnStyles*)


Gui, Add, Button, x+20 yp w80 h24 hWndhBtn42, % "Warning"
IBBtnStyles := [ [0, 0x80FCEFDC, , , 8, 0xFFF0F0F0, 0x80F0AD4E, 1]      ; normal
			   , [0, 0x80F6CE95, , , 8, 0xFFF0F0F0, 0x80F0AD4E, 1]      ; hover
			   , [0, 0x80F0AD4E, , , 8, 0xFFF0F0F0, 0x80F0AD4E, 1]      ; pressed
			   , [0, 0x80F0F0F0, , , 8, 0xFFF0F0F0, 0x80F0AD4E, 1] ]
ImageButton.Create(hBtn42, IBBtnStyles*)


Gui, Add, Button, x+20 yp w80 h24 hWndhBtn43, % "Success"
IBBtnStyles := [ [0, 0x80C6E6C6, , , 8, 0xFFF0F0F0, 0x805CB85C, 1]      ; normal
			   , [0, 0x8091CF91, , , 8, 0xFFF0F0F0, 0x805CB85C, 1]      ; hover
			   , [0, 0x805CB85C, , , 8, 0xFFF0F0F0, 0x805CB85C, 1]      ; pressed
			   , [0, 0x80F0F0F0, , , 8, 0xFFF0F0F0, 0x805CB85C, 1] ]
ImageButton.Create(hBtn43, IBBtnStyles*)


Gui, Add, Button, x+20 yp w80 h24 hWndhBtn44, % "Info"
IBBtnStyles := [ [0, 0x80C6E9F4, , , 8, 0xFFF0F0F0, 0x8046B8DA, 1]      ; normal
			   , [0, 0x8086D0E7, , , 8, 0xFFF0F0F0, 0x8046B8DA, 1]      ; hover
			   , [0, 0x8046B8DA, , , 8, 0xFFF0F0F0, 0x8046B8DA, 1]      ; pressed
			   , [0, 0x80F0F0F0, , , 8, 0xFFF0F0F0, 0x8046B8DA, 1] ]
ImageButton.Create(hBtn44, IBBtnStyles*)

; ---------------------------------------------------------------------------------------

Gui, Add, Button, xm y+20 w200 h40 hWndhBtn51, % "Critical"
IBBtnStyles := [ [0, 0x80F0F0F0, , , 0, , 0x80D43F3A, 2]      ; normal
			   , [0, 0x80F0B9B8, , , 0, , 0x80D43F3A, 2]      ; hover
			   , [0, 0x80E27C79, , , 0, , 0x80D43F3A, 2]      ; pressed
			   , [0, 0x80F0F0F0, , , 0, , 0x80D43F3A, 2] ]
ImageButton.Create(hBtn51, IBBtnStyles*)


Gui, Add, Button, x+20 yp w200 h40 hWndhBtn52, % "Warning"
IBBtnStyles := [ [0, 0x80F0F0F0, , , 0, , 0x80F0AD4E, 2]      ; normal
			   , [0, 0x80FCEFDC, , , 0, , 0x80F0AD4E, 2]      ; hover
			   , [0, 0x80F6CE95, , , 0, , 0x80F0AD4E, 2]      ; pressed
			   , [0, 0x80F0F0F0, , , 0, , 0x80F0AD4E, 2] ]
ImageButton.Create(hBtn52, IBBtnStyles*)


Gui, Add, Button, x+20 yp w200 h40 hWndhBtn53, % "Success"
IBBtnStyles := [ [0, 0x80F0F0F0, , , 0, , 0x805CB85C, 2]      ; normal
			   , [0, 0x80C6E6C6, , , 0, , 0x805CB85C, 2]      ; hover
			   , [0, 0x8091CF91, , , 0, , 0x805CB85C, 2]      ; pressed
			   , [0, 0x80F0F0F0, , , 0, , 0x805CB85C, 2] ]
ImageButton.Create(hBtn53, IBBtnStyles*)


Gui, Add, Button, x+20 yp w200 h40 hWndhBtn54, % "Info"
IBBtnStyles := [ [0, 0x80F0F0F0, , , 0, , 0x8046B8DA, 2]      ; normal
			   , [0, 0x80C6E9F4, , , 0, , 0x8046B8DA, 2]      ; hover
			   , [0, 0x8086D0E7, , , 0, , 0x8046B8DA, 2]      ; pressed
			   , [0, 0x80F0F0F0, , , 0, , 0x8046B8DA, 2] ]
ImageButton.Create(hBtn54, IBBtnStyles*)

; ---------------------------------------------------------------------------------------

Gui, Add, Button, xm y+20 w200 h40 hWndhBtn61, % "Critical"
IBBtnStyles := [ [0, 0x80F0B9B8, , , 0, , 0x80D43F3A, 2]      ; normal
			   , [0, 0x80E27C79, , , 0, , 0x80D43F3A, 2]      ; hover
			   , [0, 0x80D43F3A, , , 0, , 0x80D43F3A, 2]      ; pressed
			   , [0, 0x80F0F0F0, , , 0, , 0x80D43F3A, 2] ]
ImageButton.Create(hBtn61, IBBtnStyles*)


Gui, Add, Button, x+20 yp w200 h40 hWndhBtn62, % "Warning"
IBBtnStyles := [ [0, 0x80FCEFDC, , , 0, , 0x80F0AD4E, 2]      ; normal
			   , [0, 0x80F6CE95, , , 0, , 0x80F0AD4E, 2]      ; hover
			   , [0, 0x80F0AD4E, , , 0, , 0x80F0AD4E, 2]      ; pressed
			   , [0, 0x80F0F0F0, , , 0, , 0x80F0AD4E, 2] ]
ImageButton.Create(hBtn62, IBBtnStyles*)


Gui, Add, Button, x+20 yp w200 h40 hWndhBtn63, % "Success"
IBBtnStyles := [ [0, 0x80C6E6C6, , , 0, , 0x805CB85C, 2]      ; normal
			   , [0, 0x8091CF91, , , 0, , 0x805CB85C, 2]      ; hover
			   , [0, 0x805CB85C, , , 0, , 0x805CB85C, 2]      ; pressed
			   , [0, 0x80F0F0F0, , , 0, , 0x805CB85C, 2] ]
ImageButton.Create(hBtn63, IBBtnStyles*)


Gui, Add, Button, x+20 yp w200 h40 hWndhBtn64, % "Info"
IBBtnStyles := [ [0, 0x80C6E9F4, , , 0, , 0x8046B8DA, 2]      ; normal
			   , [0, 0x8086D0E7, , , 0, , 0x8046B8DA, 2]      ; hover
			   , [0, 0x8046B8DA, , , 0, , 0x8046B8DA, 2]      ; pressed
			   , [0, 0x80F0F0F0, , , 0, , 0x8046B8DA, 2] ]
ImageButton.Create(hBtn64, IBBtnStyles*)

; ---------------------------------------------------------------------------------------

Gui, Add, Button, xm y+20 w200 h40 hWndhBtn71, % "Critical"
IBBtnStyles := [ [0, 0x80F0F0F0, , , 8, 0xFFF0F0F0, 0x80D43F3A, 2]      ; normal
			   , [0, 0x80F0B9B8, , , 8, 0xFFF0F0F0, 0x80D43F3A, 2]      ; hover
			   , [0, 0x80E27C79, , , 8, 0xFFF0F0F0, 0x80D43F3A, 2]      ; pressed
			   , [0, 0x80F0F0F0, , , 8, 0xFFF0F0F0, 0x80D43F3A, 2] ]
ImageButton.Create(hBtn71, IBBtnStyles*)


Gui, Add, Button, x+20 yp w200 h40 hWndhBtn72, % "Warning"
IBBtnStyles := [ [0, 0x80F0F0F0, , , 8, 0xFFF0F0F0, 0x80F0AD4E, 2]      ; normal
			   , [0, 0x80FCEFDC, , , 8, 0xFFF0F0F0, 0x80F0AD4E, 2]      ; hover
			   , [0, 0x80F6CE95, , , 8, 0xFFF0F0F0, 0x80F0AD4E, 2]      ; pressed
			   , [0, 0x80F0F0F0, , , 8, 0xFFF0F0F0, 0x80F0AD4E, 2] ]
ImageButton.Create(hBtn72, IBBtnStyles*)


Gui, Add, Button, x+20 yp w200 h40 hWndhBtn73, % "Success"
IBBtnStyles := [ [0, 0x80F0F0F0, , , 8, 0xFFF0F0F0, 0x805CB85C, 2]      ; normal
			   , [0, 0x80C6E6C6, , , 8, 0xFFF0F0F0, 0x805CB85C, 2]      ; hover
			   , [0, 0x8091CF91, , , 8, 0xFFF0F0F0, 0x805CB85C, 2]      ; pressed
			   , [0, 0x80F0F0F0, , , 8, 0xFFF0F0F0, 0x805CB85C, 2] ]
ImageButton.Create(hBtn73, IBBtnStyles*)


Gui, Add, Button, x+20 yp w200 h40 hWndhBtn74, % "Info"
IBBtnStyles := [ [0, 0x80F0F0F0, , , 8, 0xFFF0F0F0, 0x8046B8DA, 2]      ; normal
			   , [0, 0x80C6E9F4, , , 8, 0xFFF0F0F0, 0x8046B8DA, 2]      ; hover
			   , [0, 0x8086D0E7, , , 8, 0xFFF0F0F0, 0x8046B8DA, 2]      ; pressed
			   , [0, 0x80F0F0F0, , , 8, 0xFFF0F0F0, 0x8046B8DA, 2] ]
ImageButton.Create(hBtn74, IBBtnStyles*)

; ---------------------------------------------------------------------------------------

Gui, Show,, Image Buttons
return


GuiClose:
GuiEscape:
ExitApp