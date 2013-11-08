Name "Klaasculator_3"
OutFile "dist\klaasculator_3_install.exe"

InstallDir $PROGRAMFILES\klaasculator

Icon "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
UninstallIcon "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

ComponentText "Installeer de Klaasculator, kies je opties:"

DirText "Kies een directory om naartoe te installeren:"

section "De Klaasculator zelf."
	SetOutPath $INSTDIR
	File "build\pygtk\*"
		
	SetOutPath $INSTDIR\cairo
	File "build\pygtk\cairo\*"

	SetOutPath $INSTDIR\codegen
	File "build\pygtk\codegen\*"

	SetOutPath $INSTDIR\gobject
	File "build\pygtk\gobject\*"

	SetOutPath $INSTDIR\gtk
	File "build\pygtk\gtk\*"

	SetOutPath $INSTDIR\klaasculator
	File "build\lib\klaasculator\*"

#	setOutPath $INSTDIR\boekhouding
#	File "boekhouding\*"

	WriteRegStr HKLM SOFTWARE\klaasculator "Path" "$INSTDIR"

	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\klaasculator" "DisplayName" "Klaasculator (uninstall)"
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\klaasculator" "UninstallString" '"$INSTDIR\klaasculator_uninstall"'

	WriteUninstaller "klaasculator_uninstall.exe"

sectionEnd

section "GTK+ runtime environment (nodig)."
	SetOutPath $INSTDIR
	File "pygtk\gtk2-runtime-2.16.6-2010-05-12-ash.exe"
	ExecWait "$INSTDIR\gtk2-runtime-2.16.6-2010-05-12-ash.exe"

	WriteRegStr HKLM SOFTWARE\klaasculator "GTK+ runtime environment" "ja"
sectionEnd

section "OpenOffice plugin."
	SetOutPath $INSTDIR
	File "build\klaasculator_3.uno.pkg"

	ClearErrors
#	ReadRegStr $0 HKLM "SOFTWARE\OpenOffice.org\UNO\InstallPath" ""
#	
#	IfErrors 0 +2 # goto
#	MessageBox MB_OK "Kon geen OpenOffice vinden. Installeer eerst OpenOffice en probeer dan opnieuw." IDOK end
#
#	ExecWait '"$0\unopkg.exe" add -f --shared "$INSTDIR\klaasculator_mk2.1.uno.pkg"' $1
#	DetailPrint "$1"
#	
#	WriteRegStr HKLM SOFTWARE\klaasculator "OpenOffice plugin" "ja"
#
#	end:
sectionEnd

section "Uninstall"
	MessageBox MB_OKCANCEL "Klaasculator in $INSTDIR deinstalleren?" IDOK DoUninstall
	
	Abort "Geannuleerd."

	DoUninstall: # AAAARGH een goto

	ReadRegStr $0 HKLM SOFTWARE\klaasculator "OpenOffice plugin"
	
	IfErrors beyondoo # goto
	
	ReadRegStr $0 HKLM "SOFTWARE\OpenOffice.org\UNO\InstallPath" ""
	
	IfErrors beyondoo # goto

	ExecWait '"$0\unopkg.exe" remove --shared klaasculator_3.uno.pkg' $1
	DetailPrint "$1"
	
	beyondoo:
	ClearErrors

	ReadRegStr $0 HKLM SOFTWARE\klaasculator "GTK+ runtime environment"

	IfErrors beyondgtk

	MessageBox MB_OKCANCEL "GTK+ runtime environment deinstalleren? Belangrijk: als je dit doet is het mogelijk dat andere programmas die van GTK+ afhaneklijk zijn (zoals bijvoorbeeld the gimp, pidgin, gnumeric, abiword, etc.) niet meer werken." IDCANCEL beyondgtk

	ReadRegStr $0 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Gtk+ Runtime Environment" "UninstallString"
	ExecWait '"$0"' $1
	DetailPrint "$1"
	
	beyondgtk:

	DeleteRegKey HKLM "SOFTWARE\klaasculator"
	DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\klaasculator"
	
	RMDir /r "$INSTDIR"
sectionEnd
