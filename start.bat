@echo off
setlocal enabledelayedexpansion
title Recruiter Outreach Platform
cd /d "%~dp0"

echo ==========================================================
echo    🚀 Recruiter Outreach Platform — All-in-One Setup
echo ==========================================================

:: 1. Ensure Windows standard environment PATHs are included
set "PATH=%APPDATA%\npm;%ProgramFiles%\nodejs;%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Launcher;%ProgramFiles%\Python312;%PATH%"

:: 2. Check if Node.js is installed; if missing, auto-install silently
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [1/4] Node.js not detected. Auto-installing Node.js LTS...
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
      "$winget = Get-Command winget -ErrorAction SilentlyContinue; " ^
      "if ($winget) { " ^
      "  & winget install --id OpenJS.NodeJS.LTS -e --accept-package-agreements --accept-source-agreements --silent; " ^
      "} else { " ^
      "  $url = 'https://nodejs.org/dist/v22.14.0/node-v22.14.0-x64.msi'; " ^
      "  $msi = Join-Path $env:TEMP 'nodejs_install.msi'; " ^
      "  Invoke-WebRequest -Uri $url -OutFile $msi; " ^
      "  Start-Process msiexec.exe -ArgumentList '/i `\"' + $msi + '`\" /qn /norestart' -Wait; " ^
      "  Remove-Item $msi -ErrorAction SilentlyContinue; " ^
      "}"
    set "PATH=%ProgramFiles%\nodejs;%APPDATA%\npm;%PATH%"
)

:: 3. Check if Python is installed; if missing, auto-install silently
set "PYTHON_CMD=python"
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    where py >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set "PYTHON_CMD=py"
    ) else (
        echo [2/4] Python not detected. Auto-installing Python 3.12...
        powershell -NoProfile -ExecutionPolicy Bypass -Command ^
          "$winget = Get-Command winget -ErrorAction SilentlyContinue; " ^
          "if ($winget) { " ^
          "  & winget install --id Python.Python.3.12 -e --accept-package-agreements --accept-source-agreements --silent; " ^
          "} else { " ^
          "  $url = 'https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe'; " ^
          "  $exe = Join-Path $env:TEMP 'python_install.exe'; " ^
          "  Invoke-WebRequest -Uri $url -OutFile $exe; " ^
          "  Start-Process $exe -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -Wait; " ^
          "  Remove-Item $exe -ErrorAction SilentlyContinue; " ^
          "}"
        set "PATH=%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%ProgramFiles%\Python312;%PATH%"
        set "PYTHON_CMD=python"
    )
)

:: 4. Check if n8n is installed; if missing, auto-install globally via npm
where n8n >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [3/4] Installing n8n Automation Engine globally via npm...
    call npm install -g n8n
)

:: 5. Install required Python packages silently
%PYTHON_CMD% -c "import requests, PIL" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    %PYTHON_CMD% -m pip install requests pillow --quiet >nul 2>&1
)

:: 6. Ensure required directories exist
if not exist "files" mkdir files
if not exist "ui" mkdir ui
if not exist "%USERPROFILE%\.n8n" mkdir "%USERPROFILE%\.n8n"

:: 7. Create Windows Desktop Shortcut with custom icon if missing
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$desktop = [Environment]::GetFolderPath('Desktop'); " ^
  "$shortcutPath = Join-Path $desktop 'Recruiter Outreach.lnk'; " ^
  "if (-not (Test-Path $shortcutPath)) { " ^
  "  $ws = New-Object -ComObject WScript.Shell; " ^
  "  $s = $ws.CreateShortcut($shortcutPath); " ^
  "  $s.TargetPath = '%CD%\start.bat'; " ^
  "  $s.WorkingDirectory = '%CD%'; " ^
  "  $s.IconLocation = '%CD%\assets\app_icon.ico,0'; " ^
  "  $s.Description = 'Recruiter Outreach Platform'; " ^
  "  $s.Save(); " ^
  "}"

:: 8. Configure n8n environment variables
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

:: 9. Auto-configure n8n database and register webhook route
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

:: 10. Start n8n Automation Engine if not already running on port 5678
netstat -ano | findstr :5678 >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Starting n8n Automation Engine...
    start /b "" cmd /c "n8n start > n8n.log 2>&1"
)

:: 11. Start Outreach Studio Server if not already running on port 3000
netstat -ano | findstr :3000 >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Starting Outreach Studio Web Server...
    start /b "" cmd /c "%PYTHON_CMD% ui\server.py > ui.log 2>&1"
)

:: 12. Open default web browser directly to UI Studio
timeout /t 3 /nobreak >nul
start "" "http://localhost:3000"

echo ==========================================================
echo    🎉 Outreach Studio is LIVE at http://localhost:3000
echo ==========================================================
