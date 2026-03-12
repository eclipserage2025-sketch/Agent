# AI Monero Miner Ultra

A high-performance AI-powered Monero (XMR) mining client utilizing RandomX.

## Features
- **XMRig Backend**: Industry-standard hashing engine for maximum efficiency.
- **AI Self-Learning**: Persistent MLP Neural Network optimizing thread allocation based on real-time hashrate, temperature, and load.
- **Dual Interface**:
  - **Native Rust GUI**: Performance-focused "Rust Pro Edition" dashboard built with `egui`.
  - **Web Dashboard**: Modern React-based SPA served via Flask.
- **Autonomous Throttling**: Real-time monitoring with automatic 80°C intensity reduction and 90°C safety shutdown.

## Installation & Setup

### 1. Build the Native Rust Version (Recommended)
The native Rust version offers the best performance and lowest overhead.
See the [CMake Installation Guide](INSTALL_CMAKE.md) for build instructions.

### 2. Standard Python/Web Installation
For the React-based Web GUI and Python controller:
- **Windows**: Follow the [Windows Installation Guide](WINDOWS_INSTALL.md).
- **Linux**:
  ```bash
  pip install -r requirements.txt
  cd frontend && npm install && npm run build && cd ..
  python3 main.py --gui
  ```

## Usage
### CLI Mode
```bash
python3 main.py --user <YOUR_XMR_ADDRESS> --host <POOL_HOST> --port <POOL_PORT>
```

### Web GUI Mode
```bash
python3 main.py --gui
```

## Build System
This project uses **CMake** to coordinate the native Rust builds. See `INSTALL_CMAKE.md` for details.
