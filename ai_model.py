import numpy as np
from sklearn.neural_network import MLPRegressor
import random
import time

class AIMiner:
    def __init__(self):
        self.model = MLPRegressor(
            hidden_layer_sizes=(10, 5),
            activation='relu',
            solver='adam',
            max_iter=1000,
            warm_start=True
        )
        self.training_data_x = []
        self.training_data_y = []
        self.is_trained = False
        self.range_size = 100000

    def collect_feedback(self, job_id, nonce, success):
        feature = [hash(job_id) % 1000, time.time() % 1000]
        self.training_data_x.append(feature)
        self.training_data_y.append(nonce)

        if len(self.training_data_x) >= 5 and len(self.training_data_x) % 5 == 0:
            self.train_on_data()

    def train_on_data(self):
        if len(self.training_data_x) < 2: return
        X = np.array(self.training_data_x)
        y = np.array(self.training_data_y)
        try:
            self.model.fit(X, y)
            self.is_trained = True
        except Exception:
            pass

    def bulk_train(self, X_bulk, y_bulk):
        """
        Trains the model on a large batch of data.
        X_bulk: list of [job_hash, timestamp]
        y_bulk: list of nonces
        """
        self.training_data_x.extend(X_bulk)
        self.training_data_y.extend(y_bulk)
        # Keep buffer size reasonable
        if len(self.training_data_x) > 10000:
            self.training_data_x = self.training_data_x[-10000:]
            self.training_data_y = self.training_data_y[-10000:]

        self.train_on_data()

    def predict_nonce_range(self, job_id, range_size=None):
        rs = range_size if range_size is not None else self.range_size
        if not self.is_trained:
            start = random.randint(0, 0xFFFFFFFF - rs)
            return start, start + rs

        feature = [[hash(job_id) % 1000, time.time() % 1000]]
        try:
            predicted_nonce = int(self.model.predict(feature)[0])
            start = max(0, min(0xFFFFFFFF - rs, predicted_nonce - (rs // 2)))
            return start, start + rs
        except Exception:
            start = random.randint(0, 0xFFFFFFFF - rs)
            return start, start + rs

if __name__ == "__main__":
    ai = AIMiner()
    ai.range_size = 50000
    start, end = ai.predict_nonce_range("test")
    print(f"Initial range: {start} to {end}")

    # Bulk train test
    X = [[random.randint(0, 1000), time.time() % 1000] for _ in range(100)]
    y = [random.randint(1000000, 2000000) for _ in range(100)]
    ai.bulk_train(X, y)

    start, end = ai.predict_nonce_range("test")
    print(f"After bulk train: {start} to {end}")
