@echo off
setlocal
echo Starting AI Litecoin Miner Ultra...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)
python main.py --gui
pause
