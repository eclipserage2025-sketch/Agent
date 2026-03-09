import struct
import binascii
import time
import threading
from hashing import scrypt_hash, double_sha256
from stratum import StratumClient
from stratum_v2 import StratumV2Client
from ai_model import AIMiner
from worker import MultiProcessMiner
from autotuner import AutoTuner

def reverse_hex(hex_str):
    """Reverses byte order of a hex string."""
    return binascii.hexlify(binascii.unhexlify(hex_str)[::-1]).decode()

def build_merkle_root(coinb1, coinb2, extranonce1, extranonce2, merkle_branch):
    """
    Builds the Merkle Root from coinbase parts and the merkle branch.
    All inputs are hex strings.
    """
    coinbase = coinb1 + extranonce1 + extranonce2 + coinb2
    coinbase_bytes = binascii.unhexlify(coinbase)
    coinbase_hash = double_sha256(coinbase_bytes)

    merkle_root = coinbase_hash
    for branch in merkle_branch:
        branch_bytes = binascii.unhexlify(branch)
        merkle_root = double_sha256(merkle_root + branch_bytes)

    return binascii.hexlify(merkle_root).decode()

class MinerController:
    def __init__(self, host, port, username, password="x", v2=False, pool_pubkey=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.v2 = v2

        if v2:
            self.client = StratumV2Client(host, port, username, pool_pubkey)
        else:
            self.client = StratumClient(host, port, username, password)

        self.ai = AIMiner()
        self.mp_miner = MultiProcessMiner()
        self.autotuner = AutoTuner(self)
        self.is_mining = False
        self.current_job = None
        self.target = 0x00000ffff0000000000000000000000000000000000000000000000000000000
        self.diff = 1

        # Stats
        self.shares_found = 0
        self.start_time = time.time()
        self.hash_rate = 0
        self.last_hashes_count = 0
        self.last_stats_time = time.time()

    def set_difficulty(self, diff):
        self.diff = diff
        target_max = 0x00000ffff0000000000000000000000000000000000000000000000000000000
        self.target = target_max // diff
        print(f"Difficulty set to: {self.diff}")

    def handle_new_job(self, params):
        if self.v2:
            # Handle SV2 Job Payload...
            pass
        else:
            self.current_job = {
                'job_id': params[0],
                'prevhash': params[1],
                'coinb1': params[2],
                'coinb2': params[3],
                'merkle_branch': params[4],
                'version': params[5],
                'nbits': params[6],
                'ntime': params[7],
                'clean_jobs': params[8]
            }

        if self.is_mining:
            self.mp_miner.stop_mining()
            self.start_mp_work()

    def start_mp_work(self):
        if self.current_job is None:
            return

        # If V1, build header standard way
        if not self.v2:
            extranonce1 = getattr(self.client, 'extranonce1', None)
            if extranonce1 is None: return

            extranonce2 = "00000001"
            merkle_root = build_merkle_root(
                self.current_job['coinb1'], self.current_job['coinb2'],
                extranonce1, extranonce2, self.current_job['merkle_branch']
            )

            header_base = (
                reverse_hex(self.current_job['version']) +
                reverse_hex(self.current_job['prevhash']) +
                reverse_hex(merkle_root) +
                reverse_hex(self.current_job['ntime']) +
                reverse_hex(self.current_job['nbits'])
            )
            header_base_bytes = binascii.unhexlify(header_base)
            job_id = self.current_job['job_id']
        else:
            # Placeholder for SV2 job processing
            return

        start_nonce, end_nonce = self.ai.predict_nonce_range(job_id, range_size=100000)
        self.mp_miner.start_mining(header_base_bytes, start_nonce, end_nonce, self.target)

    def stats_dashboard(self):
        while self.is_mining:
            now = time.time()
            elapsed_total = now - self.start_time
            elapsed_delta = now - self.last_stats_time

            if elapsed_delta > 0:
                current_hashes = self.mp_miner.progress_counter.value
                delta_hashes = current_hashes - self.last_hashes_count
                self.hash_rate = delta_hashes / elapsed_delta

                self.last_hashes_count = current_hashes
                self.last_stats_time = now

            print("\n" + "="*50)
            print(f"AI MINER STATUS | V2: {self.v2} | Uptime: {int(elapsed_total)}s")
            print(f"Hashrate: {self.hash_rate:.2f} H/s")
            print(f"Total Hashes: {self.mp_miner.progress_counter.value}")
            print(f"Shares Found: {self.shares_found} | Diff: {self.diff}")
            print(f"Threads: {self.mp_miner.num_processes} (AutoTuned)")
            print(f"AI Trained: {self.ai.is_trained}")
            print("="*50)
            time.sleep(5)

    def start(self, autotune=True):
        self.client.on_new_job = self.handle_new_job
        if not self.v2:
            self.client.on_difficulty_change = self.set_difficulty

        if not self.client.connect():
            return

        self.client.start_listening()
        if self.v2:
            self.client.setup_connection()
            time.sleep(1)
            self.client.open_channel(self.username)
        else:
            self.client.subscribe()
            time.sleep(1)
            self.client.authorize()

        self.is_mining = True
        self.last_stats_time = time.time()

        # Start stats thread
        stats_thread = threading.Thread(target=self.stats_dashboard, daemon=True)
        stats_thread.start()

        # Start autotuner
        if autotune:
            self.autotuner.start()

        # Main monitoring loop
        while self.is_mining:
            results = self.mp_miner.get_results()
            for nonce, hash_bytes in results:
                print(f"\n[!] SHARE FOUND: {binascii.hexlify(hash_bytes).decode()}")
                self.shares_found += 1
                self.ai.collect_feedback(self.current_job['job_id'], nonce, True)

                if not self.v2:
                    extranonce2 = "00000001"
                    self.client.submit(self.client.username, self.current_job['job_id'], extranonce2, self.current_job['ntime'], hex(nonce)[2:].zfill(8))
                else:
                    # Submit SV2 share...
                    pass

            if self.current_job and not self.mp_miner.is_running():
                self.start_mp_work()

            time.sleep(0.5)

    def stop(self):
        self.is_mining = False
        self.mp_miner.stop_mining()
        self.client.stop()
        self.autotuner.stop()

if __name__ == "__main__":
    print("MinerController and Merkle Root logic defined.")
