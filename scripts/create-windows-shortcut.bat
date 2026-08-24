@echo off
setlocal
set "SCRIPT_DIR=%~dp0.."
pushd "%SCRIPT_DIR%"
set "PROJECT_DIR=%CD%"
popd

set "TARGET_PATH=%PROJECT_DIR%\start.bat"
set "ICON_PATH=%PROJECT_DIR%\assets\app_icon.ico"

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$desktop = [Environment]::GetFolderPath('Desktop'); " ^
  "$shortcutPath = Join-Path $desktop 'Recruiter Outreach.lnk'; " ^
  "$ws = New-Object -ComObject WScript.Shell; " ^
  "$s = $ws.CreateShortcut($shortcutPath); " ^
  "$s.TargetPath = '%TARGET_PATH%'; " ^
  "$s.WorkingDirectory = '%PROJECT_DIR%'; " ^
  "$s.IconLocation = '%ICON_PATH%,0'; " ^
  "$s.Description = 'Recruiter Outreach Platform'; " ^
  "$s.Save(); " ^
  "if (Test-Path $shortcutPath) { Write-Host ('[OK] Created Windows Desktop shortcut with icon at: ' + $shortcutPath) }"
