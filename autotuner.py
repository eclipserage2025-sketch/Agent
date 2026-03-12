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
        self.is_throttled = False
        self.original_threads = multiprocessing.cpu_count()

    def get_max_temp(self):
        # Using miner's health monitor if available, otherwise fallback
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
            cpu_count = multiprocessing.cpu_count()
            return load1 / cpu_count
        except Exception:
            return 0.5

    def tune(self):
        while self.running:
            now = time.time()
            if now - self.last_tuning_time > 20:
                load = self.get_system_load()
                temp = self.get_max_temp()
                current_threads = self.miner.mp_miner.num_processes

                # Check for 80C threshold
                if temp and temp >= self.temp_threshold:
                    if not self.is_throttled:
                        self.is_throttled = True
                        # User requested a 20% decrease in intensity
                        new_threads = max(1, int(current_threads * 0.8))
                        print(f"[AutoTuning] Thermal alert ({temp}°C >= 80°C)! Throttling intensity by 20%: {current_threads} -> {new_threads}")
                        self.miner.update_threads(new_threads)
                    else:
                        # Already throttled, maybe AI wants to reduce further?
                        if self.miner.ai and self.miner.ai.is_trained:
                            opt_threads = self.miner.ai.predict_optimal_threads(load, temp, current_threads)
                            if opt_threads < current_threads:
                                print(f"[AutoTuning] AI suggesting further reduction to {opt_threads} due to heat.")
                                self.miner.update_threads(opt_threads)
                else:
                    # Auto Restore logic: Restore if temp is safely below threshold (e.g., < 75C)
                    if self.is_throttled and (not temp or temp < self.temp_threshold - 5):
                        self.is_throttled = False
                        # Let AI decide the best way to restore
                        if self.miner.ai and self.miner.ai.is_trained:
                            new_threads = self.miner.ai.predict_optimal_threads(load, temp, current_threads)
                        else:
                            new_threads = min(multiprocessing.cpu_count(), int(current_threads / 0.8))

                        print(f"[AutoTuning] Temperature stabilized ({temp if temp else 'N/A'}°C). Restoring intensity to {new_threads}.")
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
    print("AI-Controlled AutoTuner with thermal throttling and auto-restore defined.")
