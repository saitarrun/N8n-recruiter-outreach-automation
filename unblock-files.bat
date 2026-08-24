@echo off
title Unblock Files - Windows Defender / SmartScreen
cd /d "%~dp0"

echo ==========================================================
echo    🛡️ Unblocking Recruiter Outreach Files on Windows
echo ==========================================================
echo Removing Windows Mark-of-the-Web (Zone.Identifier) flags...

powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-ChildItem -Path '%~dp0' -Recurse | Unblock-File -ErrorAction SilentlyContinue"

echo.
echo [OK] All repository files have been unblocked!
echo You can now double-click start.bat without Windows SmartScreen blocking it.
echo.
pause
