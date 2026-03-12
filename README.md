# AI Monero Miner Ultra

A Python-based AI CPU mining client designed for Monero (XMR) using the RandomX algorithm.

## Features
- **RandomX Hashing**: Integrated high-performance RandomX support via Python bindings.
- **AI Self-Learning**: Real-time thermal and system-load monitoring using a persistent MLP Neural Network to optimize efficiency.
- **Monero Stratum Protocol**: Dedicated support for Monero-specific Stratum pools (JSON-RPC 2.0).
- **Pro Miner Dashboard**: Modern React-based Web GUI with real-time hashrate and temperature charts.
- **Autonomous Throttling**: Automatic intensity adjustment at 80°C and safety shutdown at 90°C.

## Installation
### Windows
See the [Windows Installation Guide](WINDOWS_INSTALL.md) for automated setup scripts.

### Linux
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
