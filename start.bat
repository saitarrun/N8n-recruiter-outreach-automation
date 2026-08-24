@echo off
setlocal enabledelayedexpansion
title Recruiter Outreach Platform
cd /d "%~dp0"

:: 1. Ensure Windows Node, Python, and npm PATHs are included
set "PATH=%APPDATA%\npm;%ProgramFiles%\nodejs;%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Launcher;%PATH%"

:: 2. Auto-detect Python executable command (python, py, or python3)
set "PYTHON_CMD=python"
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    where py >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set "PYTHON_CMD=py"
    ) else (
        where python3 >nul 2>&1
        if %ERRORLEVEL% EQU 0 (
            set "PYTHON_CMD=python3"
        )
    )
)

:: 3. Ensure required folders exist
if not exist "files" mkdir files
if not exist "ui" mkdir ui
if not exist "%USERPROFILE%\.n8n" mkdir "%USERPROFILE%\.n8n"

:: 4. Auto-create Windows Desktop shortcut with icon if missing
if exist "scripts\create-windows-shortcut.bat" (
    call "scripts\create-windows-shortcut.bat" >nul 2>&1
)

:: 5. Configure n8n environment variables
set N8N_PORT=5678
set N8N_PROTOCOL=http
set N8N_HOST=localhost
set WEBHOOK_URL=http://localhost:5678/
set N8N_DEFAULT_BINARY_DATA_MODE=default
set N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=false
set NODE_FUNCTION_ALLOW_BUILTIN=fs,path,os,crypto
set NODE_FUNCTION_ALLOW_EXTERNAL=*
set N8N_COMMUNITY_PACKAGES_ENABLED=true
set N8N_DIAGNOSTICS_ENABLED=false
set N8N_VERSION_NOTIFICATIONS_ENABLED=false
set N8N_HIRING_BANNER_ENABLED=false
set N8N_PERSONALIZATION_ENABLED=false
set N8N_LOG_LEVEL=info

:: 6. Auto-configure n8n workflow pipeline in SQLite database
%PYTHON_CMD% -c "
import sqlite3, json, os
db_path = os.path.expanduser('~/.n8n/database.sqlite')
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(\"SELECT id FROM workflow_entity WHERE id='T5xzFPEkCQ3vjclr'\")
    if not cur.fetchone():
        wf_file = os.path.join(os.getcwd(), 'workflows', 'direct_recruiter_outreach_batch_workflow.json')
        if os.path.exists(wf_file):
            with open(wf_file, 'r', encoding='utf-8') as f:
                wf = json.load(f)
            cur.execute(\"INSERT OR REPLACE INTO workflow_entity (id, name, active, nodes, connections) VALUES (?, ?, 1, ?, ?)\",
                        (wf['id'], wf['name'], json.dumps(wf['nodes']), json.dumps(wf['connections'])))
    else:
        cur.execute(\"UPDATE workflow_entity SET active=1 WHERE id='T5xzFPEkCQ3vjclr'\")
    
    cur.execute(\"INSERT OR REPLACE INTO webhook_entity (workflowId, webhookPath, method, node, webhookId, pathLength) VALUES ('T5xzFPEkCQ3vjclr', 'send-recruiter-outreach', 'POST', 'Webhook Trigger', NULL, NULL)\")
    conn.commit()
    conn.close()
" >nul 2>&1

:: 7. Start n8n Automation Engine if not already running on port 5678
netstat -ano | findstr :5678 >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    start /b "" cmd /c "n8n start > n8n.log 2>&1"
)

:: 8. Start Outreach Studio Server if not already running on port 3000
netstat -ano | findstr :3000 >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    start /b "" cmd /c "%PYTHON_CMD% ui\server.py > ui.log 2>&1"
)

:: 9. Wait for server and open default browser
timeout /t 3 /nobreak >nul
start "" "http://localhost:3000"

exit /b 0
