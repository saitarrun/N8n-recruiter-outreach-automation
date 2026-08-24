@echo off
setlocal enabledelayedexpansion
title Recruiter Outreach Platform
cd /d "%~dp0"

echo ==========================================================
echo    Recruiter Outreach Platform - Windows Auto-Setup
echo ==========================================================

:: 1. Ensure required folders exist
if not exist "files" mkdir files
if not exist "ui" mkdir ui
if not exist "%USERPROFILE%\.n8n" mkdir "%USERPROFILE%\.n8n"

:: 2. Auto-create Windows Desktop shortcut with icon if missing
if exist "scripts\create-windows-shortcut.bat" (
    call "scripts\create-windows-shortcut.bat" >nul 2>&1
)

:: 3. Configure n8n environment variables
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
set N8N_LOG_LEVEL=info

:: 4. Auto-configure n8n workflow pipeline via Python
echo [1/3] Verifying n8n workflows and database...
python -c "
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

:: 5. Start n8n Automation Engine if not already running on port 5678
netstat -ano | findstr :5678 >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [2/3] Starting n8n Automation Engine...
    start /b "" n8n start > n8n.log 2>&1
) else (
    echo [2/3] n8n Engine is already running (http://localhost:5678)
)

:: 6. Start Outreach Studio Server if not already running on port 3000
netstat -ano | findstr :3000 >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [3/3] Starting Outreach Studio Web Server...
    start /b "" python ui\server.py > ui.log 2>&1
) else (
    echo [3/3] Outreach Studio is already running (http://localhost:3000)
)

:: 7. Wait and open browser
timeout /t 3 /nobreak >nul
start http://localhost:3000

echo ==========================================================
echo    Platform Ready - Outreach Studio is LIVE!
echo ==========================================================
echo   Outreach Studio UI: http://localhost:3000
echo   n8n Automation:     http://localhost:5678
echo ==========================================================
