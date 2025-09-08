; VRChat Hybrid Proximity Engine NSIS Installer Script
; Easier to build than WiX MSI, creates professional EXE installer

!define APPNAME "VRChat Hybrid Proximity Engine"
!define COMPANYNAME "Wolf Clan Family"  
!define DESCRIPTION "Ultra-fast avatar proximity detection for VRChat"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0
!define HELPURL "https://github.com/wolfclan/vrchat-proximity"
!define UPDATEURL "https://github.com/wolfclan/vrchat-proximity/releases"
!define ABOUTURL "https://github.com/wolfclan/vrchat-proximity"
!define INSTALLSIZE 51200  ; Estimated size in KB

; Modern UI
!include "MUI2.nsh"
!include "Sections.nsh"
!include "FileFunc.nsh"

; Request application privileges for Windows Vista+
RequestExecutionLevel admin

; Registry key for uninstaller
!define UNINSTALL_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"

; Installer settings
Name "${APPNAME}"
OutFile "VRChatProximityEngine-${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}-Setup.exe"
InstallDir "$PROGRAMFILES\${COMPANYNAME}\${APPNAME}"
InstallDirRegKey HKLM "${UNINSTALL_KEY}" "InstallLocation"
ShowInstDetails show
ShowUnInstDetails show

; Version info
VIProductVersion "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}.0"
VIAddVersionKey "ProductName" "${APPNAME}"
VIAddVersionKey "CompanyName" "${COMPANYNAME}"
VIAddVersionKey "LegalCopyright" "© 2024 ${COMPANYNAME}"
VIAddVersionKey "FileDescription" "${DESCRIPTION}"
VIAddVersionKey "FileVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}.0"
VIAddVersionKey "ProductVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}.0"

; MUI Configuration
!define MUI_ICON "icons\app_icon.ico"
!define MUI_UNICON "icons\app_icon.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "images\header.bmp"
!define MUI_WELCOMEFINISHPAGE_BITMAP "images\welcome.bmp"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "images\welcome.bmp"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "license\license.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\RUN_HYBRID_ENGINE.bat"
!define MUI_FINISHPAGE_RUN_TEXT "Launch VRChat Proximity Engine"
!define MUI_FINISHPAGE_LINK "Visit project homepage"
!define MUI_FINISHPAGE_LINK_LOCATION "${ABOUTURL}"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages  
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "English"

; Sections
Section "Core Application" SecCore
  SectionIn RO  ; Read-only section (always installed)
  
  DetailPrint "Installing core application files..."
  SetOutPath "$INSTDIR"
  
  ; Core Python files
  File "..\hybrid_proximity_engine.py"
  File "..\standalone_proximity_detector.py" 
  File "..\fast_vision.zig"
  File "..\fast_network.go"
  File "..\go.mod"
  File "..\build_hybrid.bat"
  File "..\RUN_HYBRID_ENGINE.bat"
  
  ; Documentation
  File /nonfatal "..\README.md"
  File /nonfatal "..\PROJECT_STATUS.md"
  File /nonfatal "..\TESTING_GUIDE.md"
  
  ; Pre-compiled binaries (if available)
  File /nonfatal "..\fast_vision.dll"
  File /nonfatal "..\fast_network.exe"
  
  ; Configuration files
  SetOutPath "$INSTDIR\config"
  File /r "config\*.*"
  
  ; Example files
  SetOutPath "$INSTDIR\examples"
  File /r "examples\*.*"
  
  ; Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  
  ; Registry entries for uninstaller
  WriteRegStr HKLM "${UNINSTALL_KEY}" "DisplayName" "${APPNAME}"
  WriteRegStr HKLM "${UNINSTALL_KEY}" "UninstallString" "$\"$INSTDIR\Uninstall.exe$\""
  WriteRegStr HKLM "${UNINSTALL_KEY}" "QuietUninstallString" "$\"$INSTDIR\Uninstall.exe$\" /S"
  WriteRegStr HKLM "${UNINSTALL_KEY}" "InstallLocation" "$INSTDIR"
  WriteRegStr HKLM "${UNINSTALL_KEY}" "Publisher" "${COMPANYNAME}"
  WriteRegStr HKLM "${UNINSTALL_KEY}" "HelpLink" "${HELPURL}"
  WriteRegStr HKLM "${UNINSTALL_KEY}" "URLUpdateInfo" "${UPDATEURL}"
  WriteRegStr HKLM "${UNINSTALL_KEY}" "URLInfoAbout" "${ABOUTURL}"
  WriteRegStr HKLM "${UNINSTALL_KEY}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
  WriteRegDWORD HKLM "${UNINSTALL_KEY}" "VersionMajor" ${VERSIONMAJOR}
  WriteRegDWORD HKLM "${UNINSTALL_KEY}" "VersionMinor" ${VERSIONMINOR}
  WriteRegDWORD HKLM "${UNINSTALL_KEY}" "NoModify" 1
  WriteRegDWORD HKLM "${UNINSTALL_KEY}" "NoRepair" 1
  WriteRegDWORD HKLM "${UNINSTALL_KEY}" "EstimatedSize" ${INSTALLSIZE}
  
  ; Application registry
  WriteRegStr HKLM "Software\${COMPANYNAME}\${APPNAME}" "InstallPath" "$INSTDIR"
  WriteRegStr HKLM "Software\${COMPANYNAME}\${APPNAME}" "Version" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
  
  ; File associations
  WriteRegStr HKCR ".vrprox" "" "VRChatProximityConfig"
  WriteRegStr HKCR "VRChatProximityConfig" "" "VRChat Proximity Configuration"
  WriteRegStr HKCR "VRChatProximityConfig\DefaultIcon" "" "$INSTDIR\hybrid_proximity_engine.py,0"
  WriteRegStr HKCR "VRChatProximityConfig\shell\open\command" "" 'python "$INSTDIR\hybrid_proximity_engine.py" "%1"'
  
SectionEnd

Section "Start Menu Shortcuts" SecStartMenu
  DetailPrint "Creating Start Menu shortcuts..."
  
  CreateDirectory "$SMPROGRAMS\${APPNAME}"
  
  CreateShortCut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" \
    "$INSTDIR\RUN_HYBRID_ENGINE.bat" "" "$INSTDIR\RUN_HYBRID_ENGINE.bat" 0 \
    SW_SHOWNORMAL "" "Ultra-fast avatar proximity detection"
    
  CreateShortCut "$SMPROGRAMS\${APPNAME}\Configure Settings.lnk" \
    "$INSTDIR\hybrid_proximity_engine.py" "--config" "$INSTDIR\hybrid_proximity_engine.py" 0 \
    SW_SHOWNORMAL "" "Configure proximity detection settings"
    
  CreateShortCut "$SMPROGRAMS\${APPNAME}\User Guide.lnk" \
    "$INSTDIR\README.md" "" "$INSTDIR\README.md" 0 \
    SW_SHOWNORMAL "" "VRChat Proximity Engine documentation"
    
  CreateShortCut "$SMPROGRAMS\${APPNAME}\Uninstall.lnk" \
    "$INSTDIR\Uninstall.exe" "" "$INSTDIR\Uninstall.exe" 0 \
    SW_SHOWNORMAL "" "Uninstall ${APPNAME}"
    
SectionEnd

Section "Desktop Shortcut" SecDesktop
  DetailPrint "Creating Desktop shortcut..."
  
  CreateShortCut "$DESKTOP\VRChat Proximity Engine.lnk" \
    "$INSTDIR\RUN_HYBRID_ENGINE.bat" "" "$INSTDIR\RUN_HYBRID_ENGINE.bat" 0 \
    SW_SHOWNORMAL "" "Ultra-fast avatar proximity detection"
    
SectionEnd

Section "Python Dependencies" SecPyDeps
  DetailPrint "Installing Python dependencies..."
  
  ; Check if Python is installed
  ReadRegStr $0 HKLM "SOFTWARE\Python\PythonCore\3.11\InstallPath" ""
  IfErrors python_not_found python_found
  
  ReadRegStr $0 HKLM "SOFTWARE\Python\PythonCore\3.10\InstallPath" ""
  IfErrors python_not_found python_found
  
  ReadRegStr $0 HKLM "SOFTWARE\Python\PythonCore\3.9\InstallPath" ""
  IfErrors python_not_found python_found
  
  ReadRegStr $0 HKLM "SOFTWARE\Python\PythonCore\3.8\InstallPath" ""
  IfErrors python_not_found python_found
  
  python_not_found:
    MessageBox MB_ICONEXCLAMATION "Python 3.8+ not found. Please install Python first.$\nDownload from: https://python.org/downloads/"
    Goto pip_done
    
  python_found:
    DetailPrint "Found Python installation"
    
    ; Install required packages
    ExecWait 'python -m pip install --user websocket-client requests' $1
    IntCmp $1 0 pip_success pip_fail pip_fail
    
    pip_success:
      DetailPrint "Python dependencies installed successfully"
      Goto pip_done
      
    pip_fail:
      DetailPrint "Warning: Some Python dependencies may not have installed correctly"
      
  pip_done:
    
SectionEnd

Section "Build Optimized Components" SecBuild
  DetailPrint "Building optimized components..."
  
  ; Try to build Zig and Go components for maximum performance
  ExecWait '"$INSTDIR\build_hybrid.bat"' $2
  IntCmp $2 0 build_success build_partial build_partial
  
  build_success:
    DetailPrint "All components built successfully - maximum performance enabled"
    Goto build_done
    
  build_partial:
    DetailPrint "Some components built with fallbacks - application will still work"
    
  build_done:
    
SectionEnd

; Section descriptions
LangString DESC_SecCore ${LANG_ENGLISH} "Core application files (required)"
LangString DESC_SecStartMenu ${LANG_ENGLISH} "Add shortcuts to Start Menu"
LangString DESC_SecDesktop ${LANG_ENGLISH} "Add shortcut to Desktop" 
LangString DESC_SecPyDeps ${LANG_ENGLISH} "Install required Python packages"
LangString DESC_SecBuild ${LANG_ENGLISH} "Build optimized Zig and Go components"

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SecCore} $(DESC_SecCore)
  !insertmacro MUI_DESCRIPTION_TEXT ${SecStartMenu} $(DESC_SecStartMenu) 
  !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop} $(DESC_SecDesktop)
  !insertmacro MUI_DESCRIPTION_TEXT ${SecPyDeps} $(DESC_SecPyDeps)
  !insertmacro MUI_DESCRIPTION_TEXT ${SecBuild} $(DESC_SecBuild)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; Uninstaller
Section "Uninstall"
  DetailPrint "Removing application files..."
  
  ; Remove application files
  Delete "$INSTDIR\hybrid_proximity_engine.py"
  Delete "$INSTDIR\standalone_proximity_detector.py"
  Delete "$INSTDIR\fast_vision.zig"
  Delete "$INSTDIR\fast_network.go"
  Delete "$INSTDIR\go.mod"
  Delete "$INSTDIR\build_hybrid.bat"
  Delete "$INSTDIR\RUN_HYBRID_ENGINE.bat"
  Delete "$INSTDIR\README.md"
  Delete "$INSTDIR\PROJECT_STATUS.md"
  Delete "$INSTDIR\TESTING_GUIDE.md"
  Delete "$INSTDIR\fast_vision.dll"
  Delete "$INSTDIR\fast_network.exe"
  Delete "$INSTDIR\Uninstall.exe"
  
  ; Remove directories
  RMDir /r "$INSTDIR\config"
  RMDir /r "$INSTDIR\examples"
  RMDir "$INSTDIR"
  
  ; Remove shortcuts
  Delete "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk"
  Delete "$SMPROGRAMS\${APPNAME}\Configure Settings.lnk"
  Delete "$SMPROGRAMS\${APPNAME}\User Guide.lnk"
  Delete "$SMPROGRAMS\${APPNAME}\Uninstall.lnk"
  RMDir "$SMPROGRAMS\${APPNAME}"
  Delete "$DESKTOP\VRChat Proximity Engine.lnk"
  
  ; Remove registry entries
  DeleteRegKey HKLM "${UNINSTALL_KEY}"
  DeleteRegKey HKLM "Software\${COMPANYNAME}\${APPNAME}"
  DeleteRegKey HKCR ".vrprox"
  DeleteRegKey HKCR "VRChatProximityConfig"
  
  ; Remove from PATH if added
  ${un.RemoveFromPath} "$INSTDIR"
  
SectionEnd

; Functions
Function .onInit
  ; Check if already installed
  ReadRegStr $R0 HKLM "${UNINSTALL_KEY}" "UninstallString"
  StrCmp $R0 "" done
  
  MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION \
    "${APPNAME} is already installed.$\n$\nClick OK to remove the previous version or Cancel to cancel this upgrade." \
    /SD IDOK IDOK uninst
  Abort
  
  uninst:
    ClearErrors
    ExecWait '$R0 /S'
    
    IfErrors no_remove_uninstaller done
    IfFileExists $INSTDIR no_remove_uninstaller done
    
    no_remove_uninstaller:
    
  done:
    
FunctionEnd

Function .onInstSuccess
  MessageBox MB_ICONINFORMATION "${APPNAME} has been installed successfully!$\n$\nFeatures:$\n• Ultra-fast Zig + Go + Python engine$\n• No OSC dependency$\n• Works with any VRChat world$\n• Real-time proximity detection$\n$\nClick OK to finish."
FunctionEnd
