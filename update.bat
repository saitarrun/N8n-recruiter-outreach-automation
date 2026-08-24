@echo off
title Update Recruiter Outreach Platform
cd /d "%~dp0"

echo ==========================================================
echo    Updating Recruiter Outreach Platform from GitHub
echo ==========================================================

echo [1/2] Pulling latest code from GitHub...
git pull origin main

echo [2/2] Updating platform & launching browser...
call "%~dp0start.bat"
