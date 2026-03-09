import argparse
import sys
import time
from miner import MinerController

def main():
    parser = argparse.ArgumentParser(description="AI Litecoin Crypto Miner")
    parser.add_argument("--host", default="litecoinpool.org", help="Pool host")
    parser.add_argument("--port", type=int, default=3333, help="Pool port")
    parser.add_argument("--user", required=True, help="Worker username (e.g., username.worker)")
    parser.add_argument("--pass", dest="password", default="x", help="Worker password")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    print("="*40)
    print("AI LITECOIN MINER")
    print(f"Pool: {args.host}:{args.port}")
    print(f"User: {args.user}")
    print("="*40)

    try:
        controller = MinerController(args.host, args.port, args.user, args.password)
        controller.start()
    except KeyboardInterrupt:
        print("\nMiner stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting miner: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
