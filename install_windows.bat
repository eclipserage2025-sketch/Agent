@echo off
echo Setting up AI Litecoin Miner Ultra Environment...
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
echo Setup Complete.
pause
