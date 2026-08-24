@echo off
title Recruiter Outreach Status
echo === Recruiter Outreach Platform Status (Windows) ===

netstat -ano | findstr :3000 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo * Outreach Studio UI:  ONLINE (Port 3000)
) else (
    echo * Outreach Studio UI:  OFFLINE
)

netstat -ano | findstr :5678 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo * n8n Automation:      ONLINE (Port 5678)
) else (
    echo * n8n Automation:      OFFLINE
)

python -c "
import sqlite3, os
db = 'ui/leads.db'
if os.path.exists(db):
    c = sqlite3.connect(db).cursor()
    c.execute('SELECT COUNT(*) FROM leads')
    tot = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM leads WHERE status=\"Sent\"')
    sent = c.fetchone()[0]
    print(f'* Leads in SQLite:      {tot} Total ({sent} Sent, {tot-sent} Unsent)')
" 2>nul

echo ===================================================
pause
