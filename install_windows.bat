@echo off
echo ==========================================================
echo AI Monero Miner Ultra - Windows Installer
echo ==========================================================

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.10+ from python.org
    pause
    goto :eof
)

:: Create Virtual Environment
echo [1/3] Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create venv.
    pause
    goto :eof
)

:: Install Dependencies
echo [2/3] Installing Python dependencies...
call venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies. Note: C++ Build Tools are required for RandomX.
    pause
    goto :eof
)

:: Build Frontend
echo [3/3] Building React Frontend...
echo Note: This requires Node.js and npm to be installed.
cd frontend
call npm install
call npm run build
cd ..

echo ==========================================================
echo Installation Complete!
echo Use run_miner.bat to start the miner.
echo ==========================================================
pause
:eof