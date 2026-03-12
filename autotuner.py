import multiprocessing
import time
import os
import psutil
import random

class AutoTuner:
    def __init__(self, miner_controller):
        self.miner = miner_controller
        self.running = False
        self.last_tuning_time = time.time()
        self.temp_threshold = 80
        self.cpu_count = multiprocessing.cpu_count()

        # Self-learning exploration params
        self.exploration_rate = 0.15 # 15% chance to try a random configuration
        self.exploration_interval = 60 # Check exploration every 60s

    def get_max_temp(self):
        if hasattr(self.miner, 'health'):
            return self.miner.health.get_cpu_temp()
        try:
            temps = psutil.sensors_temperatures()
            if not temps: return None
            max_t = 0
            for name, entries in temps.items():
                for entry in entries:
                    if entry.current > max_t: max_t = entry.current
            return max_t
        except Exception:
            return None

    def get_system_load(self):
        try:
            load1, _, _ = os.getloadavg()
            return load1 / self.cpu_count
        except Exception:
            return 0.5

    def tune(self):
        while self.running:
            now = time.time()
            load = self.get_system_load()
            temp = self.get_max_temp()
            current_threads = self.miner.mp_miner.num_processes
            hashrate = self.miner.hash_rate

            # 1. Update AI with latest experience
            if self.miner.ai:
                self.miner.ai.collect_experience(load, temp, current_threads, hashrate)

            # 2. Main Tuning Cycle (every 30s)
            if now - self.last_tuning_time > 30:
                # Critical safety check first (High Heat overrides AI)
                if temp and temp >= self.temp_threshold:
                    new_threads = max(1, int(current_threads * 0.8))
                    print(f"[AutoTuner] High Heat Alert! Throttling: {new_threads}")
                    self.miner.update_threads(new_threads)
                else:
                    # Self-Learning Decision: Explore vs Exploit
                    if random.random() < self.exploration_rate:
                        # Exploration: Try a random thread count to gather new data
                        new_threads = random.randint(1, self.cpu_count)
                        print(f"[AutoTuner] AI Exploring: Testing {new_threads} threads...")
                        self.miner.update_threads(new_threads)
                    else:
                        # Exploitation: Use AI to predict optimal configuration
                        if self.miner.ai and self.miner.ai.is_trained:
                            new_threads = self.miner.ai.predict_optimal_threads(load, temp)
                            if new_threads != current_threads:
                                print(f"[AutoTuner] AI Optimization: Predicted optimal threads = {new_threads}")
                                self.miner.update_threads(new_threads)

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
    print("AI Self-Learning AutoTuner with Exploration Loop defined.")
