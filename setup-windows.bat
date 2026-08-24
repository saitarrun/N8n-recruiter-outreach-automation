@echo off
title Recruiter Outreach Platform - Automated Windows Setup
cd /d "%~dp0"

echo ==========================================================
echo    Recruiter Outreach Platform - Automated Windows Setup
echo ==========================================================
echo Provisioning Node.js LTS, Python 3, and n8n packages...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\setup-windows.ps1"

echo [OK] Setup finished. Launching platform...
call "%~dp0start.bat"
