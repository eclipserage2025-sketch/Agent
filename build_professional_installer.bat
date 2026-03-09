@echo off
echo Building Professional Windows Installer...
echo Ensure you have PyInstaller and Inno Setup (ISCC.exe in PATH) installed.

echo.
echo [1/3] Bundling Application with PyInstaller...
pyinstaller --clean miner.spec

echo.
echo [2/3] Compiling Installer with Inno Setup...
ISCC.exe setup_script.iss

echo.
echo [3/3] Done.
echo The final setup file is located in the 'dist' folder.
pause
