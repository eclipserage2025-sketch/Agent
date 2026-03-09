import argparse
import sys
import time
import signal
from miner import MinerController
from gui import run_gui

def main():
    parser = argparse.ArgumentParser(description="ULTIMATE AI LITECOIN MINER")
    parser.add_argument("--gui", action="store_true", help="Start the miner in Web GUI mode")
    parser.add_argument("--v2", action="store_true", help="Enable Stratum V2")
    parser.add_argument("--autotune", action="store_true", default=True, help="Enable auto-tuning (default: True)")
    parser.add_argument("--no-autotune", dest="autotune", action="store_false", help="Disable auto-tuning")

    parser.add_argument("--host", default="litecoinpool.org", help="Pool host")
    parser.add_argument("--port", type=int, default=3333, help="Pool port")
    parser.add_argument("--user", help="Worker username (e.g., username.worker)")
    parser.add_argument("--threads", type=int, default=None, help="Number of mining threads")

    args = parser.parse_args()

    if args.gui:
        run_gui()
        return

    if not args.user:
        parser.error("--user is required for CLI mode. Use --gui to start in web mode.")

    controller = MinerController(args.host, args.port, args.user, v2=args.v2)
    if args.threads:
        controller.mp_miner.num_processes = args.threads

    def signal_handler(sig, frame):
        print("\nExiting miner...")
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
