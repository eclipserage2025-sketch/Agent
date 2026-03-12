import struct
import binascii
import time
import threading
from stratum import MoneroStratumClient
from ai_model import AIMiner
from worker import MultiProcessMiner
from autotuner import AutoTuner
from health_check import HealthMonitor

class MinerController:
    def __init__(self, host, port, username, password="x"):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

        self.client = MoneroStratumClient(host, port, username, password)
        self.ai = AIMiner()
        self.mp_miner = MultiProcessMiner()
        self.autotuner = AutoTuner(self)
        self.health = HealthMonitor()

        self.is_mining = False
        self.current_job = None
        self.target = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

        # Stats
        self.shares_found = 0
        self.start_time = time.time()
        self.hash_rate = 0
        self.last_hashes_count = 0
        self.last_stats_time = time.time()

    def handle_new_job(self, job):
        self.current_job = job
        target_hex = job.get('target')
        if target_hex:
            if len(target_hex) == 8:
                self.target = int.from_bytes(binascii.unhexlify(target_hex), 'little')
            else:
                self.target = int(target_hex, 16)

        print(f"New Job received: {job.get('job_id')}, Target: {target_hex}")

        if self.is_mining:
            self.mp_miner.stop_mining()
            self.start_work()

    def start_work(self):
        if not self.current_job:
            return

        blob = self.current_job['blob']
        seed_hash = self.current_job['seed_hash']

        import random
        start_nonce = random.randint(0, 0x7FFFFFFF)
        end_nonce = start_nonce + 1000000

        self.mp_miner.start_mining(blob, self.target, seed_hash, start_nonce, end_nonce)

    def update_threads(self, num):
        if num == self.mp_miner.num_processes:
            return
        print(f"[MinerController] Updating thread count to {num}")
        self.mp_miner.num_processes = num
        if self.is_mining:
            self.mp_miner.stop_mining()
            self.start_work()

    def stats_dashboard(self):
        while self.is_mining:
            now = time.time()
            elapsed_total = now - self.start_time
            elapsed_delta = now - self.last_stats_time

            if elapsed_delta > 0:
                current_hashes = self.mp_miner.progress_counter.value
                delta_hashes = current_hashes - self.last_hashes_count
                self.hash_rate = delta_hashes / elapsed_delta
                self.ai.set_last_hashrate(self.hash_rate)

                self.last_hashes_count = current_hashes
                self.last_stats_time = now

            print("\n" + "="*50)
            print(f"AI MONERO MINER | Uptime: {int(elapsed_total)}s")
            print(f"Hashrate: {self.hash_rate:.2f} H/s")
            print(f"Shares Found: {self.shares_found}")
            print(f"Threads: {self.mp_miner.num_processes} | AI Trained: {self.ai.is_trained}")
            print("="*50)
            time.sleep(10)

    def monitor_health(self):
        """Monitors health every 30 seconds as requested."""
        while self.is_mining:
            status, temp = self.health.check_status()
            if status == 2: # Critical
                print(f"[CRITICAL] Temperature {temp}°C exceeded 90°C! Gracefully stopping miner.")
                # We stop the controller's mining status but keep the thread alive if needed
                # (though here we call stop which shuts everything down)
                self.stop()
                break
            elif status == 1: # Throttling
                print(f"[WARNING] Temperature {temp}°C exceeded 80°C. Throttling intensity.")
                # Intensity reduction is handled by AutoTuner/AI which we will update next

            time.sleep(30)

    def start(self, autotune=True):
        self.client.on_new_job = self.handle_new_job

        if not self.client.connect():
            return

        self.client.start_listening()
        self.client.login()

        self.is_mining = True
        self.last_stats_time = time.time()

        # Start stats thread
        stats_thread = threading.Thread(target=self.stats_dashboard, daemon=True)
        stats_thread.start()

        # Start health monitor thread
        health_thread = threading.Thread(target=self.monitor_health, daemon=True)
        health_thread.start()

        # Start autotuner
        if autotune:
            self.autotuner.start()

        # Main monitoring loop
        while self.is_mining:
            results = self.mp_miner.get_results()
            for nonce, hash_hex in results:
                print(f"\n[!] SHARE FOUND: {hash_hex}")
                self.shares_found += 1
                self.client.submit(self.current_job['job_id'], hex(nonce)[2:].zfill(8), hash_hex)

            if self.current_job and not self.mp_miner.is_running():
                self.start_work()

            time.sleep(1)

    def stop(self):
        self.is_mining = False
        self.mp_miner.stop_mining()
        self.client.stop()
        self.autotuner.stop()

if __name__ == "__main__":
    print("MinerController for Monero with health monitoring defined.")
