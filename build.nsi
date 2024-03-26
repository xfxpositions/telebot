!include "MUI2.nsh"


!define input_path "nsi_inputfiles"
!define build_path "nsi_build"


; General settings
Name "Logo Telebot 0.5"
; Set build number by input
!ifdef BUILD_NUMBER
    OutFile "${build_path}\telebot_setup_${BUILD_NUMBER}.exe"
!else
    OutFile "${build_path}\telebot_setup.exe"
!endif
InstallDir "$LOCALAPPDATA\logotelebot"
InstallDirRegKey HKCU "Software\logotelebot" ""
RequestExecutionLevel admin
Unicode True


; Interface settings
!define MUI_ABORTWARNING

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "${input_path}\license.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "English"

; Check for Voicemeeter Installation and Offer Installation if Not Found
Function .onInit
    ; Check if Voicemeeter is installed by looking for its registry entry
    ClearErrors
    ReadRegStr $0 HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Voicemeeter" "UninstallString"
    IfErrors 0 voicemeeter_already_installed
    
    ; Check for the Voicemeeter setup file
    IfFileExists "${input_path}\voicemeetersetup.exe" proceed_with_installation voicemeeter_setup_not_found
    
    proceed_with_installation:
    MessageBox MB_YESNO|MB_ICONQUESTION "Voicemeeter is not detected on your system. Would you like to install it now?" IDYES install_voicemeeter IDNO abort_installation
    Goto done
    
    voicemeeter_already_installed:
    MessageBox MB_OK|MB_ICONINFORMATION "Voicemeeter is already installed on your system. Setup will now continue."
    Goto done

    voicemeeter_setup_not_found:
    MessageBox MB_OK|MB_ICONSTOP "Voicemeeter setup file was not found in the expected directory. Please ensure that the 'voicemeetersetup.exe' file is located in '${input_path}'. Setup will now exit."
    Abort

    install_voicemeeter:
    ExecWait '"${input_path}\voicemeetersetup.exe"' $0
    ${If} $0 != 0
        MessageBox MB_OK|MB_ICONSTOP "Voicemeeter installation failed or was cancelled. Setup will now exit."
        Abort
    ${EndIf}
    Goto done

    abort_installation:
    MessageBox MB_OK|MB_ICONEXCLAMATION "Voicemeeter installation is required. Setup will now exit."
    Abort

    done:
FunctionEnd

; Installer Sections
Section "Telebot" SecDummy
    SetOutPath "$INSTDIR"
    
    ; Add application files
    File "${input_path}\telebot.exe"
    
    ; Create the documentation folder
    SetOutPath "$INSTDIR\documentation"
    
    ; Add documentation to the documentation folder
    File "${input_path}\documentation.pdf"
    
    ; Store installation folder
    WriteRegStr HKCU "Software\logotelebot" "" $INSTDIR
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\Telebot Uninstall.exe"
    
SectionEnd

; Descriptions
LangString DESC_SecDummy ${LANG_ENGLISH} "Installs Logo Telebot 0.5 and its dependencies."
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDummy} $(DESC_SecDummy)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; Uninstaller Section
Section "Uninstall"
    ; Delete application files
    Delete "$INSTDIR\telebot.exe"
    Delete "$INSTDIR\.env"
    Delete "$INSTDIR\openai_config.json"
    Delete "$INSTDIR\settings.json"
    
    ; Delete documentation and its folder
    Delete "$INSTDIR\documentation\documentation.pdf"
    RMDir "$INSTDIR\documentation"
    
    ; Delete the entire installation directory
    RMDir /r "$INSTDIR"
    
    ; Remove the registry key
    DeleteRegKey /ifempty HKCU "Software\logotelebot"
SectionEnd
