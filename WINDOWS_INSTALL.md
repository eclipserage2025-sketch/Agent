# AI Monero Miner Ultra - Windows Installation Guide
This guide will walk you through setting up the AI Monero Miner Ultra on a Windows machine.

## Prerequisites

1.  **Python 3.10+**: Download and install from [python.org](https://www.python.org/downloads/windows/).
    -  **Important**: During installation, check the box that says **Add Python to PATH**.
2.  **Node.js & npm**: Download and install from [nodejs.org](https://nodejs.org/).
3.  **C++ Build Tools**: Required for compiling the RandomX hashing library.
    -  Download the [Visual Studio Installer](https://visualstudio.microsoft.com/visual-cpp-build-tools/).
    -  Select "Desktop development with C++" and ensure the latest "MSVC v143" and "Windows 10/11 SDK" are checked.
4.  **Git (Optional)**: If you want to clone the repository directly.

## Automated Installation (Recommended)

1.  Open the miner directory in File Explorer.
2.  Double-click `install_windows.bat`.
3.  Follow the on-screen prompts. The script will:
    -  Create a Python virtual environment.
    -  Install all Python dependencies (`numpy`, `scikit-learn`, `flask`, `randomx`, `psutil`).
    -  Install frontend dependencies and build the React GUI.

## Running the Miner

1.  Double-click `run_miner.bat`.
2.  Select **Option 1** for the Web GUI mode.
3.  Open your browser and navigate to `http://127.0.0.1:5000`.
4.  Configure your wallet and pool in the dashboard and click **Start Mini\xe2\x9e

## Manual Installation

If you prefer to set up manually:

```powershell
# 1. Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# 2, Install dependencies
pip install -r requirements.txt

`# 3. Build the frontend
cd frontend
npm install
npm run build
cd ..

# 4. Start the miner
python main.py --gui
```J
## Troubleshooting

-   **RandomX Installation Fails**: Ensure the C++ Build Tools are correctly installed and that you are using a 64-bit version of Python.
-   **Node.js Not Found**: If the installer fails at the frontend build step, ensure Node.js is in your system PATH.
-   **Permission Errors**: Try running the command prompt or batch files as Administrator.