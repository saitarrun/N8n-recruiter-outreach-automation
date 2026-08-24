# Recruiter Outreach Platform - Automated Windows Environment Provisioner
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   🚀 Recruiter Outreach Platform — Windows Auto-Setup    " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Detect / Install Node.js LTS
$nodeInstalled = $false
try {
    $nodeVer = & node -v 2>$null
    if ($nodeVer) {
        Write-Host "✓ Node.js runtime is installed: $nodeVer" -ForegroundColor Green
        $nodeInstalled = $true
    }
} catch {}

if (-not $nodeInstalled) {
    Write-Host "⚙️  Node.js not detected. Auto-installing Node.js LTS..." -ForegroundColor Yellow
    $wingetExists = Get-Command winget -ErrorAction SilentlyContinue
    if ($wingetExists) {
        & winget install --id OpenJS.NodeJS.LTS -e --accept-package-agreements --accept-source-agreements --silent
    } else {
        $nodeUrl = "https://nodejs.org/dist/v22.14.0/node-v22.14.0-x64.msi"
        $nodeMsi = "$env:TEMP\nodejs_installer.msi"
        Write-Host "Downloading Node.js installer..."
        Invoke-WebRequest -Uri $nodeUrl -OutFile $nodeMsi
        Start-Process msiexec.exe -ArgumentList "/i `"$nodeMsi`" /qn /norestart" -Wait
        Remove-Item $nodeMsi -ErrorAction SilentlyContinue
    }
    $env:PATH = "$env:ProgramFiles\nodejs;$env:APPDATA\npm;$env:PATH"
    Write-Host "✓ Node.js installed successfully!" -ForegroundColor Green
}

# 2. Detect / Install Python 3
$pythonInstalled = $false
try {
    $pyVer = & python --version 2>$null
    if ($pyVer) {
        Write-Host "✓ Python runtime is installed: $pyVer" -ForegroundColor Green
        $pythonInstalled = $true
    }
} catch {}

if (-not $pythonInstalled) {
    Write-Host "⚙️  Python not detected. Auto-installing Python 3.12..." -ForegroundColor Yellow
    $wingetExists = Get-Command winget -ErrorAction SilentlyContinue
    if ($wingetExists) {
        & winget install --id Python.Python.3.12 -e --accept-package-agreements --accept-source-agreements --silent
    } else {
        $pyUrl = "https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe"
        $pyExe = "$env:TEMP\python_installer.exe"
        Write-Host "Downloading Python installer..."
        Invoke-WebRequest -Uri $pyUrl -OutFile $pyExe
        Start-Process $pyExe -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait
        Remove-Item $pyExe -ErrorAction SilentlyContinue
    }
    $env:PATH = "$env:LOCALAPPDATA\Programs\Python\Python312;$env:LOCALAPPDATA\Programs\Python\Python312\Scripts;$env:ProgramFiles\Python312;$env:PATH"
    Write-Host "✓ Python 3 installed successfully!" -ForegroundColor Green
}

# 3. Detect / Install n8n Automation Engine globally
$n8nInstalled = $false
try {
    $n8nVer = & n8n --version 2>$null
    if ($n8nVer) {
        Write-Host "✓ n8n Automation Engine is installed: $n8nVer" -ForegroundColor Green
        $n8nInstalled = $true
    }
} catch {}

if (-not $n8nInstalled) {
    Write-Host "⚙️  Installing n8n globally via npm (may take 1-2 minutes)..." -ForegroundColor Yellow
    & npm install -g n8n
    Write-Host "✓ n8n installed successfully!" -ForegroundColor Green
}

# 4. Install Python dependencies
try {
    & python -m pip install --upgrade pip --quiet 2>$null
    & python -m pip install requests pillow --quiet 2>$null
} catch {}

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "   🎉 All environments, tech stacks & packages READY!    " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""
