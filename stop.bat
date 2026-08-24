@echo off
title Stop Recruiter Outreach Platform
echo Stopping Recruiter Outreach Platform on Windows...

:: Kill processes on port 3000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000') do (
    taskkill /f /pid %%a >nul 2>&1
)

:: Kill processes on port 5678
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5678') do (
    taskkill /f /pid %%a >nul 2>&1
)

echo [OK] All services stopped.
