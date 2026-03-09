# AI Litecoin Miner - Windows Professional Installation Guide

This guide explains how to build and install the AI Litecoin Miner on Windows as a professional application.

## 1. Quick Install (Script Mode)
If you have Python installed, simply run:
1. `install_windows.bat` - Sets up the environment and dependencies.
2. `run_miner.bat` - Launches the miner (GUI or CLI).

## 2. Professional Installer Build (.exe)
To create a standalone setup wizard (`AI_Litecoin_Miner_Setup.exe`):

### Prerequisites
- **Python 3.8+**
- **Inno Setup 6** (Download from [jrsoftware.org](https://jrsoftware.org/isdl.php))

### Build Steps
1. Open a terminal/command prompt in the project folder.
2. Run `build_professional_installer.bat`.
3. The script will:
   - Install `pyinstaller`.
   - Bundle the app into the `dist/` folder.
   - Use Inno Setup to create a professional installer.

## 3. Usage
Once installed, you will find "AI Litecoin Miner" in your **Start Menu** and on your **Desktop**.
- Launching from the shortcut will automatically start the **Web GUI**.
- The installer also includes a full uninstaller in the Control Panel.

## Features Included
- **Stratum V2 & V1 Support**
- **Auto-Tuning Engine** (Optimized for Windows CPU load)
- **Neural Network AI Optimization**
- **Multi-core Hashing**
