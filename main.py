import argparse
import sys
import signal
import os
from miner import MinerController
from gui import run_gui
from downloader import download_xmrig_windows

def main():
    parser = argparse.ArgumentParser(description="ULTIMATE AI MONERO MINER (XMRIG INTEGRATED)")
    parser.add_argument("--gui", action="store_true", help="Start the miner in Web GUI mode")
    parser.add_argument("--autotune", action="store_true", default=True, help="Enable auto-tuning")
    parser.add_argument("--no-autotune", dest="autotune", action="store_false", help="Disable auto-tuning")

    parser.add_argument("--host", default="pool.supportxmr.com", help="Pool host")
    parser.add_argument("--port", type=int, default=3333, help="Pool port")
    parser.add_argument("--user", help="Monero address")
    parser.add_argument("--pass", dest="password", default="x", help="Pool password")
    parser.add_argument("--threads", type=int, default=4, help="Number of mining threads")

    args = parser.parse_args()

    # Ensure XMRig is present
    if not os.path.exists("xmrig.exe"):
        print("XMRig binary not found. Attempting to download...")
        if not download_xmrig_windows():
            print("Failed to download XMRig. Please install manually.")
            sys.exit(1)

    if args.gui:
        run_gui()
        return

    if not args.user:
        parser.error("--user is required for CLI mode.")

    controller = MinerController(args.host, args.port, args.user, password=args.password)
    controller.threads = args.threads

    def signal_handler(sig, frame):
        print("\nExiting AI Monero Miner...")
        controller.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        controller.start(autotune=args.autotune)
    except Exception as e:
        print(f"Fatal error: {e}")
        controller.stop()
        sys.exit(1)

if __name__ == "__main__":
    main()
