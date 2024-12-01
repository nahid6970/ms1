Gui, Destroy
Gui, New, +Resize
Gui, +AlwaysOnTop
Gui, Margin, 20, 20
Gui,Font,s12 Normal Bold,Jetbrainsmono nfp

; ME
Gui,Add,Button, xm ym w200 h50,                Nahid Ahmed
Gui,Add,Button, x+5 yp w100 h50 gname_en_nahid,en
Gui,Add,Button, x+5 yp w100 h50 gname_bd_nahid,bn

; Father
Gui,Add,Button, xm y+5 w200 h50,                Father
Gui,Add,Button, x+5 yp w100 h50 gname_en_father,en
Gui,Add,Button, x+5 yp w100 h50 gname_bd_father,bn

; Mother
Gui,Add,Button, xm y+5 w200 h50,                Mother
Gui,Add,Button, x+5 yp w100 h50 gname_en_mother,en
Gui,Add,Button, x+5 yp w100 h50 gname_bd_mother,bn

Gui,Add,Button,xm y+5 w410 h50 gPermanentAddress,Vill:Munshibari, P.O-Radhapur, 9 No Ward, Dist-Lakshmipur Post Code: 3706

; SSC
Gui,Add,Button, xm y+5 w200 h50,                 SSC
Gui,Add,Button, x+5 yp w100 h50 gssc_roll,       Roll
Gui,Add,Button, x+5 yp w100 h50 gssc_year,       Year
Gui,Add,Button, x+5 yp w100 h50 gssc_school,     School

; HSC
Gui,Add,Button, xm y+5 w200 h50,                 HSC
Gui,Add,Button, x+5 yp w100 h50 ghsc_roll,       Roll
Gui,Add,Button, x+5 yp w100 h50 ghsc_year,       Year
Gui,Add,Button, x+5 yp w100 h50 ghsc_college,    College

; Gui, Show, w400 h500, BIO
Gui, Show, , BIO
return

GuiClose:
ExitApp ; Ensure the script exits entirely
return

name_bd_nahid:
    Gui, Hide ; Temporarily hides the GUI (optional, based on your needs)
    Send, {U+09A8}{U+09BE}{U+09B9}{U+09BF}{U+09A6} {U+0986}{U+09B9}{U+09AE}{U+09C7}{U+09A6}
    Gui, Show ; Brings the GUI back (if you used Hide above)
return
name_en_nahid:
    Gui, Hide ; Temporarily hides the GUI (optional, based on your needs)
    Send, Nahid Ahmed
    Gui, Show ; Brings the GUI back (if you used Hide above)
return

name_bd_father:
    Gui, Hide ; Temporarily hides the GUI (optional, based on your needs)
    Send, {U+09A8}{U+09C1}{U+09B0}{U+09C1}{U+09B2} {U+0986}{U+09AE}{U+09BF}{U+09A8}
    Gui, Show ; Brings the GUI back (if you used Hide above)
return
name_en_father:
    Gui, Hide ; Temporarily hides the GUI (optional, based on your needs)
    Send, Nurul Amin
    Gui, Show ; Brings the GUI back (if you used Hide above)
return

name_bd_mother:
    Gui, Hide ; Temporarily hides the GUI (optional, based on your needs)
    Send, {U+09A8}{U+09BE}{U+099C}{U+09AE}{U+09BE} {U+09AC}{U+09C7}{U+0997}{U+09AE}
    Gui, Show ; Brings the GUI back (if you used Hide above)
return
name_en_mother:
    Gui, Hide ; Temporarily hides the GUI (optional, based on your needs)
    Send, Nazma Begum
    Gui, Show ; Brings the GUI back (if you used Hide above)
return

PermanentAddress:
    Gui, Hide ; Temporarily hides the GUI (optional, based on your needs)
    Send, Vill:Munshibari, P.O-Radhapur, 9 No Ward, Dist-Lakshmipur Post Code: 3706
    Gui, Show ; Brings the GUI back (if you used Hide above)
return

ssc_roll:
    Gui, Hide ; Temporarily hides the GUI (optional, based on your needs)
    Send, 402206
    Gui, Show ; Brings the GUI back (if you used Hide above)
return
ssc_year:
    Gui, Hide ; Temporarily hides the GUI (optional, based on your needs)
    Send, 2014
    Gui, Show ; Brings the GUI back (if you used Hide above)
return
ssc_school:
    Gui, Hide ; Temporarily hides the GUI (optional, based on your needs)
    Send, Provati Uchya Bidyanikaton
    Gui, Show ; Brings the GUI back (if you used Hide above)
return

hsc_roll:
    Gui, Hide ; Temporarily hides the GUI (optional, based on your needs)
    Send, 510014
    Gui, Show ; Brings the GUI back (if you used Hide above)
return
hsc_year:
    Gui, Hide ; Temporarily hides the GUI (optional, based on your needs)
    Send, 2016
    Gui, Show ; Brings the GUI back (if you used Hide above)
return
hsc_college:
    Gui, Hide ; Temporarily hides the GUI (optional, based on your needs)
    Send, Notre Dame College
    Gui, Show ; Brings the GUI back (if you used Hide above)
return

