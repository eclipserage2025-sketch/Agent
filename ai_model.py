import numpy as np
from sklearn.neural_network import MLPRegressor
import time

class AIMiner:
    def __init__(self):
        # AI to predict optimal intensity/thread count
        # Inputs: [Current Load, Current Temp, Last Hashrate]
        # Output: [Optimal Threads]
        self.model = MLPRegressor(
            hidden_layer_sizes=(8, 4),
            activation='relu',
            solver='adam',
            max_iter=500,
            warm_start=True
        )
        self.training_data_x = []
        self.training_data_y = []
        self.is_trained = False
        self.last_hashrate = 0

    def collect_system_metrics(self, load, temp, threads):
        # Normalize inputs for better training
        temp_val = temp if temp else 50.0
        feature = [load, temp_val / 100.0, self.last_hashrate / 1000.0]

        # We target a thread count that keeps system usable and cool
        # For simplicity, we use the current 'successful' thread count as a label
        # In a more advanced version, we'd label based on 'hashrate per watt' or 'hashrate stability'
        self.training_data_x.append(feature)
        self.training_data_y.append(threads)

        if len(self.training_data_x) >= 10 and len(self.training_data_x) % 10 == 0:
            X = np.array(self.training_data_x)
            y = np.array(self.training_data_y)
            try:
                self.model.fit(X, y)
                self.is_trained = True
            except Exception as e:
                print(f"Error training AI: {e}")

    def predict_optimal_threads(self, load, temp, current_threads):
        if not self.is_trained:
            return current_threads

        temp_val = temp if temp else 50.0
        feature = [[load, temp_val / 100.0, self.last_hashrate / 1000.0]]
        try:
            predicted = self.model.predict(feature)[0]
            # Ensure predicted threads is within sensible bounds
            import multiprocessing
            cpu_count = multiprocessing.cpu_count()
            return int(np.clip(predicted, 1, cpu_count))
        except Exception:
            return current_threads

    def set_last_hashrate(self, hr):
        self.last_hashrate = hr

if __name__ == "__main__":
    ai = AIMiner()
    print("AI Model for Resource Optimization defined.")
