@echo off
setlocal
echo ============================================================
echo AI LITECOIN MINER - LAUNCHER
echo ============================================================

if not exist venv\Scripts\activate.bat (
    echo [!] Virtual environment not found. Please run 'install_windows.bat' first.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo 1. Start Web GUI (Recommended)
echo 2. Start CLI Mode
echo 3. Exit
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo Starting Web GUI...
    python main.py --gui
) else if "%choice%"=="2" (
    set /p worker="Enter Worker Username: "
    echo Starting CLI Mode for %worker%...
    python main.py --user %worker%
) else if "%choice%"=="3" (
    exit /b 0
) else (
    echo Invalid choice.
    pause
    goto :eof
)

pause
