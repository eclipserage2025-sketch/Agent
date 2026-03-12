import multiprocessing
import time
import os
import psutil

class AutoTuner:
    def __init__(self, miner_controller):
        self.miner = miner_controller
        self.running = False
        self.last_tuning_time = time.time()
        self.temp_threshold = 80  # Celsius
        self.load_threshold = 0.8 # 80% per core

    def get_max_temp(self):
        try:
            temps = psutil.sensors_temperatures()
            if not temps:
                return None

            max_t = 0
            for name, entries in temps.items():
                for entry in entries:
                    if entry.current > max_t:
                        max_t = entry.current
            return max_t
        except Exception:
            return None

    def get_system_load(self):
        # returns 1-minute load average normalized by CPU count
        try:
            load1, _, _ = os.getloadavg()
            cpu_count = multiprocessing.cpu_count()
            return load1 / cpu_count
        except Exception:
            return 0.5

    def tune(self):
        """
        Main auto-tuning loop with thermal and load monitoring.
        """
        while self.running:
            now = time.time()
            if now - self.last_tuning_time > 20: # Tune every 20s
                load = self.get_system_load()
                temp = self.get_max_temp()
                current_threads = self.miner.mp_miner.num_processes

                print(f"[AutoTuning] Load: {load:.2f}, Temp: {temp if temp else 'N/A'}°C, Threads: {current_threads}")

                should_reduce = False
                reason = ""

                if load > self.load_threshold:
                    should_reduce = True
                    reason = "High Load"

                if temp and temp > self.temp_threshold:
                    should_reduce = True
                    reason = "High Temperature"

                if should_reduce and current_threads > 1:
                    new_threads = current_threads - 1
                    print(f"[AutoTuning] {reason}, reducing threads to {new_threads}")
                    self.miner.update_threads(new_threads)
                elif not should_reduce and load < 0.4 and (not temp or temp < self.temp_threshold - 10):
                    if current_threads < multiprocessing.cpu_count():
                        new_threads = current_threads + 1
                        print(f"[AutoTuning] Low usage, increasing threads to {new_threads}")
                        self.miner.update_threads(new_threads)

                # Collect feedback for AI optimization
                if self.miner.ai:
                    self.miner.ai.collect_system_metrics(load, temp, current_threads)

                self.last_tuning_time = now

            time.sleep(5)

    def start(self):
        self.running = True
        import threading
        thread = threading.Thread(target=self.tune, daemon=True)
        thread.start()

    def stop(self):
        self.running = False

if __name__ == "__main__":
    print("Enhanced AutoTuner with thermal monitoring defined.")
