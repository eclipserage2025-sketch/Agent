import multiprocessing
import time
import os

class AutoTuner:
    def __init__(self, miner_controller):
        self.miner = miner_controller
        self.running = False
        self.last_tuning_time = time.time()

    def get_system_load(self):
        # returns 1-minute load average normalized by CPU count
        load1, load5, load15 = os.getloadavg()
        cpu_count = multiprocessing.cpu_count()
        return load1 / cpu_count

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
                    print(f"[AutoTuning] High load ({load:.2f}), reducing threads to {new_threads}")
                    self.miner.mp_miner.num_processes = new_threads
                    self.miner.mp_miner.stop_mining()
                    self.miner.start_mp_work()

                # If load is low (< 40%) and threads < CPU count, increase threads
                elif load < 0.4 and current_threads < multiprocessing.cpu_count():
                    new_threads = current_threads + 1
                    print(f"[AutoTuning] Low load ({load:.2f}), increasing threads to {new_threads}")
                    self.miner.mp_miner.num_processes = new_threads
                    self.miner.mp_miner.stop_mining()
                    self.miner.start_mp_work()

                # Optimization: Adjust AI nonce range based on hashrate
                # If hashrate is high, we can cover more nonces
                hr = self.miner.hash_rate
                if hr > 1000:
                    new_range = 200000
                elif hr > 500:
                    new_range = 100000
                else:
                    new_range = 50000

                # We can store this in miner or AI
                # self.miner.ai.range_size = new_range

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
