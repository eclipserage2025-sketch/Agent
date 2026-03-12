import json
import os
import subprocess
import time
import threading
import requests
from ai_model import AIMiner
from autotuner import AutoTuner
from health_check import HealthMonitor

class MinerController:
    def __init__(self, host, port, username, password="x"):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

        self.ai = AIMiner()
        self.autotuner = AutoTuner(self)
        self.health = HealthMonitor()

        self.process = None
        self.is_mining = False
        self.hash_rate = 0
        self.shares_found = 0
        self.start_time = time.time()
        self.threads = 4
        self.api_port = 4048

        # Compat with old GUI code
        self.mp_miner = type('obj', (object,), {
            'progress_counter': type('obj', (object,), {'value': 0}),
            'num_processes': self.threads
        })

        # XMRig binary name
        self.xmrig_bin = "xmrig.exe"

    def generate_config(self):
        config = {
            "autosave": False,
            "cpu": {
                "enabled": True,
                "max-threads-hint": 100,
                "threads": self.threads,
            },
            "opencl": False,
            "cuda": False,
            "pools": [
                {
                    "url": f"{self.host}:{self.port}",
                    "user": self.username,
                    "pass": self.password,
                    "keepalive": True,
                    "tls": False
                }
            ],
            "http": {
                "enabled": True,
                "host": "127.0.0.1",
                "port": self.api_port,
                "access-token": None,
                "restricted": True
            }
        }
        with open("xmrig_config.json", "w") as f:
            json.dump(config, f, indent=4)
        return "xmrig_config.json"

    def fetch_metrics(self):
        while self.is_mining:
            try:
                resp = requests.get(f"http://127.0.0.1:{self.api_port}/1/summary", timeout=2)
                if resp.status_code == 200:
                    data = resp.json()
                    self.hash_rate = data.get("hashrate", {}).get("total", [0])[0]
                    self.shares_found = data.get("results", {}).get("shares_good", 0)
                    # Update compatibility fields
                    self.mp_miner.progress_counter.value = data.get("results", {}).get("hashes_total", 0)
            except Exception:
                pass
            time.sleep(5)

    def monitor_health(self):
        while self.is_mining:
            status, temp = self.health.check_status()
            if status == 2:
                print(f"[CRITICAL] Temperature {temp}°C exceeded 90°C! Shutting down XMRig.")
                self.stop()
                break
            time.sleep(30)

    def start(self, autotune=True):
        if not os.path.exists(self.xmrig_bin):
            print(f"[Miner] Error: {self.xmrig_bin} not found. Run downloader first.")
            return

        self.generate_config()
        print(f"[Miner] Starting XMRig with {self.threads} threads...")

        self.process = subprocess.Popen(
            [self.xmrig_bin, "-c", "xmrig_config.json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        self.is_mining = True
        self.start_time = time.time()

        threading.Thread(target=self.fetch_metrics, daemon=True).start()
        threading.Thread(target=self.monitor_health, daemon=True).start()

        if autotune:
            self.autotuner.start()

        while self.is_mining and self.process.poll() is None:
            time.sleep(1)

    def update_threads(self, num):
        if num == self.threads:
            return
        print(f"[Miner] Updating threads {self.threads} -> {num}. Restarting XMRig...")
        self.threads = num
        self.mp_miner.num_processes = num
        if self.is_mining:
            self.stop_subprocess()
            self.generate_config()
            self.process = subprocess.Popen(
                [self.xmrig_bin, "-c", "xmrig_config.json"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

    def stop_subprocess(self):
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None

    def stop(self):
        self.is_mining = False
        self.stop_subprocess()
        self.autotuner.stop()

if __name__ == "__main__":
    print("MinerController for XMRig defined.")
