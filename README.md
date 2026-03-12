# AI Monero Miner Ultra

A Python-based AI CPU mining client designed for Monero (XMR) using the RandomX algorithm.

## Features
- **RandomX Hashing**: Integrated high-performance RandomX support via Python bindings.
- **AI-Throttling**: Real-time thermal and system-load monitoring using an AI Neural Network to adjust mining intensity (thread count) dynamically.
- **Monero Stratum Protocol**: Dedicated support for Monero-specific Stratum pools (JSON-RPC 2.0).
- **Agentic Architecture**: Modular design for easy extensibility and autonomous updates.
- **Web GUI**: Real-time dashboard with hashrate, CPU temperature, and AI status.

## Installation
```bash
pip install -r requirements.txt
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
