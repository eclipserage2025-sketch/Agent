import argparse
import sys
import time
import signal
from miner import MinerController

def main():
    parser = argparse.ArgumentParser(description="UPGRADED AI LITECOIN MINER")
    parser.add_argument("--host", default="litecoinpool.org", help="Pool host")
    parser.add_argument("--port", type=int, default=3333, help="Pool port")
    parser.add_argument("--user", required=True, help="Worker username (e.g., username.worker)")
    parser.add_argument("--pass", dest="password", default="x", help="Worker password")
    parser.add_argument("--threads", type=int, default=None, help="Number of mining threads (processes)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    print("="*60)
    print("UPGRADED AI LITECOIN MINER (Neural Network + Multi-Processing)")
    print(f"Target: {args.host}:{args.port}")
    print(f"Worker: {args.user}")
    print("="*60)

    controller = MinerController(args.host, args.port, args.user, args.password)
    if args.threads:
        controller.mp_miner.num_processes = args.threads

    def signal_handler(sig, frame):
        print("\n\nExiting miner...")
        controller.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        controller.start()
    except Exception as e:
        print(f"Fatal error: {e}")
        controller.stop()
        sys.exit(1)

if __name__ == "__main__":
    main()
