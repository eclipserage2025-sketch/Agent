import numpy as np
from sklearn.neural_network import MLPRegressor
import joblib
import os
import multiprocessing
import random

class AIMiner:
    def __init__(self, model_path="ai_model.pkl"):
        self.model_path = model_path
        # Input: [Load, Normalized_Temp, Thread_Count]
        # Output: [Efficiency_Score (Hashrate per Watt/Heat proxy)]
        self.model = MLPRegressor(
            hidden_layer_sizes=(16, 8),
            activation='relu',
            solver='adam',
            max_iter=1000,
            warm_start=True
        )
        self.training_data_x = []
        self.training_data_y = []
        self.is_trained = False
        self.total_samples = 0
        self.cpu_count = multiprocessing.cpu_count()

        self.load_model()

    def load_model(self):
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                self.is_trained = True
                print(f"[AI] Loaded persistent model from {self.model_path}")
            except Exception as e:
                print(f"[AI] Error loading model: {e}")

    def save_model(self):
        try:
            joblib.dump(self.model, self.model_path)
            # print(f"[AI] Saved persistent model to {self.model_path}")
        except Exception as e:
            print(f"[AI] Error saving model: {e}")

    def calculate_reward(self, hashrate, temp, load):
        # Efficiency Reward logic:
        # High hashrate is good.
        # High temperature (> 75) is very bad.
        # High system load (> 0.9) is bad.
        temp_penalty = 0
        if temp and temp > 75:
            temp_penalty = (temp - 75) * 10

        load_penalty = 0
        if load > 0.9:
            load_penalty = (load - 0.9) * 100

        reward = hashrate - temp_penalty - load_penalty
        return max(0, reward)

    def collect_experience(self, load, temp, threads, hashrate):
        temp_val = temp if temp else 50.0
        feature = [load, temp_val / 100.0, threads / self.cpu_count]
        reward = self.calculate_reward(hashrate, temp, load)

        self.training_data_x.append(feature)
        self.training_data_y.append(reward)
        self.total_samples += 1

        # Incremental learning every 10 samples
        if len(self.training_data_x) >= 10:
            X = np.array(self.training_data_x)
            y = np.array(self.training_data_y)
            try:
                self.model.fit(X, y)
                self.is_trained = True
                self.save_model()
                self.training_data_x = []
                self.training_data_y = []
            except Exception as e:
                print(f"[AI] Training error: {e}")

    def predict_optimal_threads(self, load, temp):
        """Self-learning decision: Evaluate all possible thread counts and pick the one with max predicted reward."""
        if not self.is_trained:
            return random.randint(1, self.cpu_count)

        temp_val = temp if temp else 50.0
        best_reward = -float('inf')
        best_threads = 1

        # Grid search over all possible thread counts
        features = []
        for t in range(1, self.cpu_count + 1):
            features.append([load, temp_val / 100.0, t / self.cpu_count])

        try:
            predictions = self.model.predict(features)
            best_threads = np.argmax(predictions) + 1
            return int(best_threads)
        except Exception:
            return random.randint(1, self.cpu_count)

if __name__ == "__main__":
    ai = AIMiner()
    print("AI Self-Learning Model with Reward logic and Persistence defined.")
