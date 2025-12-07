# Installation script for PokemonCommunityGameBot
# This script installs Python (if needed) and all required Python packages

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "PokemonCommunityGameBot - Installation Script" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

# Required Python version (3.12.4 for discord.py-self compatibility)
$requiredPythonVersion = "3.12.0"
$pythonDownloadUrl = "https://www.python.org/ftp/python/3.12.4/python-3.12.4-amd64.exe"

# Function to find Python executable
function Find-Python {
    $pythonCommands = @("python3", "python", "py")
    
    foreach ($cmd in $pythonCommands) {
        try {
            $version = & $cmd --version 2>&1
            if ($version -match "Python \d+\.\d+") {
                return $cmd
            }
        } catch {
            continue
        }
    }
    return $null
}

# Function to compare versions
function Compare-Version {
    param (
        [string]$version1,
        [string]$version2
    )
    $v1 = [version]($version1 -replace "Python ", "")
    $v2 = [version]$version2
    return $v1 -ge $v2
}

# Function to download and install Python
function Install-Python {
    Write-Host "Python is not installed or not in PATH!" -ForegroundColor Yellow
    Write-Host ""
    
    $response = Read-Host "Would you like to download and install Python 3.12.4 automatically? (y/n)"
    
    if ($response -ne 'y' -and $response -ne 'Y') {
        Write-Host ""
        Write-Host "Installation cancelled." -ForegroundColor Yellow
        Write-Host "Please install Python 3.12.4 manually from https://www.python.org/downloads/" -ForegroundColor Cyan
        Write-Host "Make sure to check 'Add Python to PATH' during installation!" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Press any key to exit..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit 1
    }
    
    Write-Host ""
    Write-Host "Downloading Python 3.12.4..." -ForegroundColor Green
    
    $installerPath = "$env:TEMP\python-installer.exe"
    
    try {
        # Download Python installer
        Invoke-WebRequest -Uri $pythonDownloadUrl -OutFile $installerPath -UseBasicParsing
        Write-Host "Download completed!" -ForegroundColor Green
        Write-Host ""
        
        Write-Host "Installing Python..." -ForegroundColor Green
        Write-Host "Please wait, this may take a few minutes..." -ForegroundColor Cyan
        Write-Host ""
        
        # Install Python silently with PATH
        $installArgs = "/quiet InstallAllUsers=0 PrependPath=1 Include_test=0 Include_pip=1"
        Start-Process -FilePath $installerPath -ArgumentList $installArgs -Wait -NoNewWindow
        
        # Clean up installer
        Remove-Item $installerPath -Force
        
        Write-Host "Python installation completed!" -ForegroundColor Green
        Write-Host ""
        Write-Host "IMPORTANT: Please close and reopen this PowerShell window!" -ForegroundColor Yellow
        Write-Host "Then run this script again to install the packages." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Press any key to exit..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit 0
        
    } catch {
        Write-Host "ERROR: Failed to download or install Python!" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        Write-Host ""
        Write-Host "Please install Python manually from https://www.python.org/downloads/" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Press any key to exit..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit 1
    }
}

# Find Python installation
$pythonCmd = Find-Python

if ($null -eq $pythonCmd) {
    Install-Python
}

# Display Python version
$pythonVersion = & $pythonCmd --version 2>&1
Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
Write-Host "Using command: $pythonCmd" -ForegroundColor Cyan
Write-Host ""

# Check Python version
if (-not (Compare-Version -version1 $pythonVersion -version2 $requiredPythonVersion)) {
    Write-Host "WARNING: Python version is older than recommended ($requiredPythonVersion)" -ForegroundColor Yellow
    Write-Host "The bot may still work, but consider updating Python." -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne 'y' -and $continue -ne 'Y') {
        exit 1
    }
    Write-Host ""
}

# Check if pip is available
try {
    $pipVersion = & $pythonCmd -m pip --version 2>&1
    Write-Host "Found pip: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: pip is not available!" -ForegroundColor Red
    Write-Host "Please reinstall Python with pip enabled." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}
Write-Host ""

# Upgrade pip to latest version
Write-Host "Upgrading pip to latest version..." -ForegroundColor Yellow
& $pythonCmd -m pip install --upgrade pip
Write-Host ""

# Install requirements
Write-Host "Installing packages from requirements.txt..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Cyan
Write-Host ""
& $pythonCmd -m pip install -r requirements.txt

Write-Host ""
if ($LASTEXITCODE -eq 0) {
    Write-Host "=" * 70 -ForegroundColor Green
    Write-Host "Installation completed successfully!" -ForegroundColor Green
    Write-Host "=" * 70 -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now run the bot using:" -ForegroundColor Cyan
    Write-Host "  $pythonCmd Start_Bots.py" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "=" * 70 -ForegroundColor Red
    Write-Host "Installation failed! Please check the errors above." -ForegroundColor Red
    Write-Host "=" * 70 -ForegroundColor Red
    Write-Host ""
}

Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
