import psutil
import logging

class HealthMonitor:
    def __init__(self, throttle_temp=80, critical_temp=90):
        self.throttle_temp = throttle_temp
        self.critical_temp = critical_temp
        self.logger = logging.getLogger("miner.health")

    def get_cpu_temp(self):
        try:
            temps = psutil.sensors_temperatures()
            if not temps:
                return None

            max_t = 0
            # Look for CPU temps
            # Common keys are 'coretemp', 'cpu_thermal', 'pkg-temp-0'
            for name, entries in temps.items():
                for entry in entries:
                    if entry.current > max_t:
                        max_t = entry.current
            return max_t
        except Exception as e:
            self.logger.error(f"Error reading CPU temperature: {e}")
            return None

    def check_status(self):
        """
        Returns a status code:
        0 - OK
        1 - Throttling required (>= 80C)
        2 - Critical (>= 90C)
        """
        temp = self.get_cpu_temp()
        if temp is None:
            return 0, None

        if temp >= self.critical_temp:
            return 2, temp
        elif temp >= self.throttle_temp:
            return 1, temp
        else:
            return 0, temp

if __name__ == "__main__":
    monitor = HealthMonitor()
    status, temp = monitor.check_status()
    print(f"Status: {status}, Temp: {temp}")
