# AI Monero Miner - CMake Build & Installation Guide

This guide explains how to build the native Rust-based AI Monero Miner using CMake.

## Prerequisites

Before building, ensure you have the following installed:

1.  **CMake 3.10+**: Available at [cmake.org](https://cmake.org/download/).
2.  **Rust & Cargo**: Install the Rust toolchain from [rustup.rs](https://rustup.rs/).
3.  **C++ Compiler**:
    -   **Windows**: Visual Studio 2022 with C++ Desktop Development workload.
    -   **Linux**: `gcc` or `clang`.
4.  **Linux Dependencies (egui)**:
    -   On Ubuntu/Debian: `sudo apt-get install libx11-dev libwayland-dev libasound2-dev libpango1.0-dev libatk1.0-dev libgtk-3-dev libegl1-mesa-dev`

## Building from Source

### 1. Configure the project

Create a build directory and run CMake configuration:

```bash
mkdir build
cd build
cmake ..
```

### 2. Build the miner

Run the build command:

```bash
cmake --build . --config Release
```

This will trigger Cargo to build the Rust components in release mode. The resulting binary will be located in:
-   **Windows**: `build/src-rust/target/release/ai_monero_miner.exe`
-   **Linux**: `build/src-rust/target/release/ai_monero_miner`

## Installation

To install the binary to a system directory (defaults to `/usr/local/bin` on Linux or `C:/Program Files` on Windows):

```bash
cmake --install .
```

## Running

1.  Ensure you have **XMRig** (`xmrig.exe`) in the same directory as the miner binary or in your system PATH.
2.  Launch the miner:

```bash
./ai_monero_miner
```

## Notes

-   **Cross-platform**: CMake manages the environment detection and passes the heavy lifting to Cargo.
-   **Performance**: Always use the `Release` configuration for mining to ensure the best GUI performance and lowest overhead.
