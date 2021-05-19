'=====================================================================
'
' plot spectrum
'
'=====================================================================
SUB plotspec(kennung&,ngrx%,ngry%,farbe&,vismin!,vismax!,nspec&,spec!())

' Darstellung
GRAPHIC ATTACH kennung&, 0, REDRAW
GRAPHIC CLEAR 0

xgra! = 0.0
ygra! = CSNG(ngry%) * (spec!(0) - vismin!) / (vismax! - vismin!)

FOR ispec& = 0 TO nspec& - 1
    xgrb! = CSNG(ngrx%) * CSNG(ispec&) / CSNG(nspec&)
    ygrb! = CSNG(ngry%) * (spec!(ispec&) - vismin!) / (vismax! - vismin!)
    GRAPHIC LINE (xgra!,CSNG(ngry%) - ygra!) - (xgrb!,CSNG(ngry%) - ygrb!), farbe&
    xgra! = xgrb!
    ygra! = ygrb!
NEXT ispec&

GRAPHIC REDRAW

END SUB







'=====================================================================
'
' main program
'
'=====================================================================
FUNCTION PBMAIN () AS LONG

INPUT "spectral file to visualize:", specdatei$

PRINT specdatei$

test$ = DIR$(specdatei$)
IF test$ = "" THEN
    PRINT "File not found!"
    SLEEP 20000
    END
END IF

OPEN specdatei$ FOR BINARY AS #1

GET$ #1,4,nspecchar$ ' number of spectra
GET$ #1,4,ngridchar$ ' number of gridpoints

nspec& = CVL(nspecchar$)
ngrid& = CVL(ngridchar$)

PRINT nspec&
PRINT ngrid&

DIM mess!(0 TO ngrid& - 1),calc!(0 TO ngrid& - 1)

ngrx% = 800
ngry% = 300
GRAPHIC WINDOW "spectrum", 20, 20, ngrx%, ngry% TO kenna&

FOR ispec& = 1 TO nspec&
    GET$ #1,12,specname$
    PRINT specname$

    binchar$ = ""
    GET$ #1, 4 * ngrid&, binchar$
    FOR igrid& = 0 TO ngrid& - 1
        mess!(igrid&) = CVS(MID$(binchar$,1 + 4 * igrid&,4))
        messmean! = messmean! + mess!(igrid&)
        IF messmax! < mess!(igrid&) THEN messmax! = mess!(igrid&)
        IF messmin! > mess!(igrid&) THEN messmin! = mess!(igrid&)
    NEXT igrid&
    messmean! = messmean! / CSNG(ngrid&)

    binchar$ = ""
    GET$ #1, 4 * ngrid&, binchar$
    FOR igrid& = 0 TO ngrid& - 1
        calc!(igrid&) = CVS(MID$(binchar$,1 + 4 * igrid&,4))
        calcmean! = calcmean! + calc!(igrid&)
        IF calcmax! < calc!(igrid&) THEN calcmax! = calc!(igrid&)
        IF calcmin! > calc!(igrid&) THEN calcmin! = calc!(igrid&)
    NEXT igrid&
    calcmean! = calcmean! / CSNG(ngrid&)

    ' plot meas + calc spectrum
    PRINT "plotting spectrum:",ispec&
    CALL plotspec(kenna&,ngrx%,ngry%,CLNG(RGB(255,0,0)),-0.1* messmax!,messmax!,ngrid&,mess!())
    CALL plotspec(kenna&,ngrx%,ngry%,CLNG(RGB(0,255,0)),-0.1* messmax!,messmax!,ngrid&,calc!())

    SLEEP 2000

NEXT ispec&

GRAPHIC ATTACH kenna&, 0, REDRAW
GRAPHIC WINDOW END

ERASE mess!(),calc!()

CLOSE #1

END FUNCTION
