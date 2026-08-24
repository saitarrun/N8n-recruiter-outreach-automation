@echo off
setlocal
cd /d "%~dp0"
echo ==========================================================
echo    Recruiter Outreach Platform — Windows 1-Click Launch   
echo ==========================================================
echo Starting n8n Automation Engine...
start "" /b n8n start
echo Starting Outreach Studio Web Server...
start "" /b python ui\server.py
timeout /t 3 >nul
start http://localhost:3000
echo Platform is online!
pause
