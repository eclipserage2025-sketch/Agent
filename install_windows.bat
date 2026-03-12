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
echo [1/4] Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create venv.
    pause
    goto :eof
)

:: Install Dependencies
echo [2/4] Installing Python dependencies...
call venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    goto :eof
)

:: Download XMRig
echo [3/4] Downloading XMRig Binary...
python downloader.py
if %errorlevel% neq 0 (
    echo [ERROR] Failed to download XMRig.
    pause
    goto :eof
)

:: Install Frontend
echo [4/4] Building React Frontend...
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