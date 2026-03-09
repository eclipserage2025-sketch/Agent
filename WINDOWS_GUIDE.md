# Windows Build Guide for AI Litecoin Miner Ultra

This guide explains how to generate the professional Windows installer for the miner.

## Prerequisites

1.  **Python 3.8+**: Ensure Python is installed and added to your `PATH`.
2.  **Inno Setup**: Download and install [Inno Setup](https://jrsoftware.org/isdl.php). Ensure `ISCC.exe` is in your `PATH`.
3.  **Visual C++ Build Tools**: Required for compiling `pyopencl`.

## One-Click Build Process

1.  **Install Dependencies**: Run `install_windows.bat` to set up the virtual environment and install all required Python packages.
2.  **Generate Installer**: Run `build_professional_installer.bat`. This will:
    -   Bundle the application using PyInstaller based on `miner.spec`.
    -   Compile the installer using Inno Setup and `setup_script.iss`.
3.  **Result**: The final installer (`AI-Litecoin-Miner-Ultra-Setup.exe`) will be in the `dist/` directory.

## Features Included in Windows Build

-   **Admin Privileges**: The executable is configured to request administrative rights.
-   **Auto-Startup**: Upon installation, the miner is added to the Windows Startup folder.
-   **GPU/CPU Mining**: Supports both GPU (via OpenCL) and CPU mining with automatic fallback.
-   **Web GUI**: Launches by default in Web GUI mode for ease of use.
-   **Shortcuts**: Adds icons to the Desktop and Start Menu.

## Troubleshooting

-   **GPU Not Detected**: Ensure you have the latest drivers for your NVIDIA, AMD, or Intel GPU.
-   **Admin Rights**: If the miner fails to start, try running it explicitly as an Administrator.
-   **Antivirus**: Some antivirus software may flag crypto miners. You may need to add an exclusion for the installation directory.
