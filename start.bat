@echo off
REM 🚀 Jarvis Quick-Start Script (Windows)
REM
REM This script starts both the Telegram bot and HTTP API bridge
REM in separate Command Prompt windows.
REM
REM Usage:
REM   start.bat
REM
REM Or run from PowerShell:
REM   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
REM   .\start.bat

setlocal enabledelayedexpansion

cls
echo ╔════════════════════════════════════════════════════════╗
echo ║          🚀 Jarvis Local Dev Environment             ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Check if .env exists
if not exist ".env" (
    echo ⚠️  .env file not found!
    echo Creating .env from template...
    copy .env.example .env >nul
    echo ✅ Created .env ^(please edit with your credentials^)
    echo.
)

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found!
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo Python: %PYTHON_VERSION%
echo.

REM Check and create virtual environment
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
)

REM Activate virtual environment
call venv\Scripts\activate.bat >nul
echo ✅ Virtual environment activated
echo.

REM Install dependencies
echo 📦 Installing dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies installed
echo.

REM Check Telegram token
for /f "tokens=2 delims==" %%i in ('findstr /R "^TELEGRAM_BOT_TOKEN" .env') do set TELEGRAM_TOKEN=%%i
set TELEGRAM_TOKEN=%TELEGRAM_TOKEN: =%

if "!TELEGRAM_TOKEN!"=="" (
    echo ⚠️  WARNING: TELEGRAM_BOT_TOKEN not set!
    echo Edit .env and add your bot token from @BotFather
    echo.
)

echo ╔════════════════════════════════════════════════════════╗
echo ║              🎯 Starting Services                      ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo Starting in 2 seconds... ^(Press Ctrl+C to cancel^)
echo.
timeout /t 2 /nobreak >nul

REM Create logs directory
if not exist "logs" mkdir logs

echo Starting: Telegram Bot + Background Tasks...
start "Jarvis - Telegram Bot" cmd /k "python -m jarvis.main"

REM Wait a bit for first process to start
timeout /t 2 /nobreak >nul

echo Starting: HTTP API Bridge...
start "Jarvis - API Bridge" cmd /k "python -m jarvis.api_bridge"

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║              ✨ All Services Running!                 ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo 🎯 Endpoints:
echo    API Health:    curl http://localhost:8000/api/health
echo    Send Command:  curl -X POST http://localhost:8000/api/command -H "Content-Type: application/json" -d "{\"command\": \"/status\"}"
echo.
echo 🌐 Web UI: Open your React frontend and ensure REACT_APP_JARVIS_API_URL=http://localhost:8000
echo.
echo 📋 Windows Terminal Tip:
echo    Right-click the title bar of each window and select "Split Pane" for side-by-side viewing
echo.
echo 🛑 To stop: Close both Command Prompt windows or press Ctrl+C in each
echo.
echo For detailed setup instructions, see SETUP.md
echo.
pause
