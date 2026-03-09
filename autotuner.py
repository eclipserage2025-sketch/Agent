import multiprocessing
import time
import os
import psutil

class AutoTuner:
    def __init__(self, miner_controller):
        self.miner = miner_controller
        self.running = False
        self.last_tuning_time = time.time()

    def get_system_load(self):
        """
        Cross-platform system load metric using psutil.
        Returns overall CPU usage percentage (0.0 to 1.0).
        """
        try:
            # Using psutil for cross-platform compatibility (Windows/Linux)
            cpu_usage = psutil.cpu_percent(interval=1)
            return cpu_usage / 100.0
        except Exception:
            # Fallback for unexpected errors
            return 0.5

    def tune(self):
        """
        Main auto-tuning loop.
        """
        while self.running:
            now = time.time()
            if now - self.last_tuning_time > 30: # Tune every 30s
                load = self.get_system_load()
                current_threads = self.miner.mp_miner.num_processes

                # If load is high (> 80%), reduce threads
                if load > 0.8 and current_threads > 1:
                    new_threads = current_threads - 1
                    print(f"[AutoTuning] High CPU usage ({load*100:.1f}%), reducing threads to {new_threads}")
                    self.miner.mp_miner.num_processes = new_threads
                    self.miner.mp_miner.stop_mining()
                    self.miner.start_mp_work()

                # If load is low (< 40%) and threads < CPU count, increase threads
                elif load < 0.4 and current_threads < multiprocessing.cpu_count():
                    new_threads = current_threads + 1
                    print(f"[AutoTuning] Low CPU usage ({load*100:.1f}%), increasing threads to {new_threads}")
                    self.miner.mp_miner.num_processes = new_threads
                    self.miner.mp_miner.stop_mining()
                    self.miner.start_mp_work()

                # Optimization: Adjust AI nonce range based on hashrate
                hr = self.miner.hash_rate
                if hr > 1000:
                    self.miner.ai.range_size = 200000
                elif hr > 500:
                    self.miner.ai.range_size = 100000
                else:
                    self.miner.ai.range_size = 50000

                self.last_tuning_time = now

            time.sleep(10)

    def start(self):
        self.running = True
        import threading
        thread = threading.Thread(target=self.tune, daemon=True)
        thread.start()

    def stop(self):
        self.running = False

if __name__ == "__main__":
    print("AutoTuner logic defined.")
