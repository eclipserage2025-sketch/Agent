@echo off
setlocal
echo ============================================================
echo AI LITECOIN MINER - PROFESSIONAL INSTALLER BUILDER
echo ============================================================

:: 1. Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python is not installed.
    pause
    exit /b 1
)

:: 2. Install Build Tools
echo [1/4] Installing build dependencies...
pip install pyinstaller -r requirements.txt

:: 3. Build Executable with PyInstaller
echo [2/4] Building standalone executable with PyInstaller...
pyinstaller miner.spec --noconfirm

if %errorlevel% neq 0 (
    echo [!] PyInstaller build failed.
    pause
    exit /b 1
)

:: 4. Check for Inno Setup
echo [3/4] Checking for Inno Setup (ISCC.exe)...
set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist %ISCC% (
    echo [!] Inno Setup 6 not found at %ISCC%
    echo Please install Inno Setup 6 from https://jrsoftware.org/isdl.php
    echo After installation, you can run ISCC.exe on setup_script.iss manually.
    pause
    exit /b 0
)

:: 5. Compile Installer
echo [4/4] Compiling Windows Installer (.exe)...
%ISCC% setup_script.iss

if %errorlevel% neq 0 (
    echo [!] Inno Setup compilation failed.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo SUCCESS! Your professional installer is ready:
echo AI_Litecoin_Miner_Setup.exe
echo ============================================================
pause
