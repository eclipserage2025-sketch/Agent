import time
import random
import requests
from miner_logger import logger

class ProfitManager:
    def __init__(self):
        self.last_check = 0
        self.profits = {
            "LTC": 1.0, # Relative profit factor
            "DOGE": 0.8
        }
        self.best_coin = "LTC"

    def update_profitability(self):
        """
        In a real scenario, this would fetch from a mining pool or exchange API.
        For example: whattomine.com/api
        """
        now = time.time()
        if now - self.last_check > 300: # Check every 5 minutes
            try:
                # Simulate API call
                # response = requests.get("https://whattomine.com/coins.json")
                # data = response.json()

                # Mocking logic for demo
                self.profits["LTC"] = random.uniform(0.9, 1.1)
                self.profits["DOGE"] = random.uniform(0.7, 1.2)

                self.best_coin = "LTC" if self.profits["LTC"] >= self.profits["DOGE"] else "DOGE"
                logger.info(f"Profit update: LTC={self.profits['LTC']:.2f}, DOGE={self.profits['DOGE']:.2f}. Best: {self.best_coin}")
                self.last_check = now
            except Exception as e:
                logger.error(f"Profit check failed: {e}")

    def should_switch(self, current_coin):
        self.update_profitability()
        return self.best_coin != current_coin

if __name__ == "__main__":
    pm = ProfitManager()
    pm.update_profitability()
    print(f"Profit Switching - Best Coin: {pm.best_coin}")
