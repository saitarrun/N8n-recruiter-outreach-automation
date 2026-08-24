@echo off
title Launch Windows Sandbox Test Environment
cd /d "%~dp0.."
set "PROJECT_DIR=%CD%"
set "WSB_FILE=%PROJECT_DIR%\sandbox.wsb"

echo ==========================================================
echo    🧪 Generating Windows Sandbox Configuration (.wsb)
echo ==========================================================

(
echo ^<Configuration^>
echo   ^<MappedFolders^>
echo     ^<MappedFolder^>
echo       ^<HostFolder^>%PROJECT_DIR%^</HostFolder^>
echo       ^<SandboxFolder^>C:\n8n-outreach^</SandboxFolder^>
echo       ^<ReadOnly^>false^</ReadOnly^>
echo     ^</MappedFolder^>
echo   ^</MappedFolders^>
echo   ^<LogonCommand^>
echo     ^<Command^>cmd.exe /k "C:\n8n-outreach\start.bat"^</Command^>
echo   ^</LogonCommand^>
echo   ^<Networking^>Default^</Networking^>
echo   ^<MemoryInMB^>4096^</MemoryInMB^>
echo ^</Configuration^>
) > "%WSB_FILE%"

echo [OK] Generated: %WSB_FILE%
echo.
echo Launching Windows Sandbox...
start "" "%WSB_FILE%"
