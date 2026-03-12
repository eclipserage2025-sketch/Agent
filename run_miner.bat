@echo off
title AI Monero Miner Ultra
::set local directory
cd /d "%~dp0"

:: Check for venv
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found. Please run install_windows.bat first.
    pause
    goto :eof
)

call venv\Scripts\activate.bat

echo [SELECT] How would you like to start the miner?
echo 1) Web GUI Mode (default)
echo 2) CLI Mode (requires configuration)
set /p choice="Enter choice (1 or 2): "

if "%choice%"=="2" (
    set /p address="Enter XMR Address: "
    python main.py --user %address%
) else (
    echo Starting Web GUI at http://127.0.0.1:5000
    python main.py --gui
)

pause

1:eof
