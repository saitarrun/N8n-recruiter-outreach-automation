@echo off
setlocal
set "SCRIPT_DIR=%~dp0.."
pushd "%SCRIPT_DIR%"
set "PROJECT_DIR=%CD%"
popd

set "SHORTCUT_PATH=%USERPROFILE%\Desktop\Recruiter Outreach.lnk"
set "TARGET_PATH=%PROJECT_DIR%\start.bat"
set "ICON_PATH=%PROJECT_DIR%\assets\app_icon.ico"

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ws = New-Object -ComObject WScript.Shell; " ^
  "$s = $ws.CreateShortcut('%SHORTCUT_PATH%'); " ^
  "$s.TargetPath = '%TARGET_PATH%'; " ^
  "$s.WorkingDirectory = '%PROJECT_DIR%'; " ^
  "$s.IconLocation = '%ICON_PATH%,0'; " ^
  "$s.Description = 'Recruiter Outreach Platform'; " ^
  "$s.Save()"

if exist "%SHORTCUT_PATH%" (
    echo [OK] Created Windows Desktop shortcut with icon: %SHORTCUT_PATH%
)
