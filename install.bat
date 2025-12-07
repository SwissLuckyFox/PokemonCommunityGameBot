@echo off
REM Installation script for PokemonCommunityGameBot
REM This script installs all required Python packages

echo Installing Python dependencies for PokemonCommunityGameBot...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo Found Python version:
python --version
echo.

REM Check if pip is available
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not available!
    pause
    exit /b 1
)

echo Found pip version:
python -m pip --version
echo.

REM Upgrade pip to latest version
echo Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install requirements
echo Installing packages from requirements.txt...
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo Installation failed! Please check the errors above.
    pause
    exit /b 1
)

echo.
echo Installation completed successfully!
echo You can now run the bot using: python Start_Bots.py
echo.
pause
