@echo off
setlocal
echo ============================================================
echo AI LITECOIN MINER - WINDOWS INSTALLER
echo ============================================================

:: 1. Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

:: 2. Create Virtual Environment
echo [1/3] Creating virtual environment (venv)...
python -m venv venv
if %errorlevel% neq 0 (
    echo [!] Failed to create virtual environment.
    pause
    exit /b 1
)

:: 3. Install Dependencies
echo [2/3] Installing dependencies from requirements.txt...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [!] Failed to install dependencies.
    pause
    exit /b 1
)

:: 4. Finish
echo [3/3] Installation complete!
echo.
echo You can now use 'run_miner.bat' to start the miner.
echo ============================================================
pause
