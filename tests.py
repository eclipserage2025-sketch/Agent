import unittest
import os
import numpy as np
from ai_model import AIMiner
from unittest.mock import MagicMock

class TestAISelfLearning(unittest.TestCase):
    def test_persistence(self):
        model_file = "test_ai.pkl"
        if os.path.exists(model_file): os.remove(model_file)

        ai = AIMiner(model_path=model_file)
        # Simulate training
        for i in range(15):
            ai.collect_experience(0.5, 60.0, 4, 100.0)

        self.assertTrue(ai.is_trained)
        self.assertTrue(os.path.exists(model_file))

        # Load again
        ai2 = AIMiner(model_path=model_file)
        self.assertTrue(ai2.is_trained)

        if os.path.exists(model_file): os.remove(model_file)

    def test_reward_calculation(self):
        ai = AIMiner()
        # Normal
        r1 = ai.calculate_reward(100.0, 60.0, 0.5)
        # Hot
        r2 = ai.calculate_reward(100.0, 85.0, 0.5)
        # Overloaded
        r3 = ai.calculate_reward(100.0, 60.0, 0.95)

        self.assertGreater(r1, r2)
        self.assertGreater(r1, r3)

    def test_optimal_thread_prediction(self):
        ai = AIMiner()
        # Mocking model training for specific outcome is complex,
        # but we check if it returns a valid integer
        threads = ai.predict_optimal_threads(0.5, 60.0)
        self.assertIsInstance(threads, int)
        self.assertGreaterEqual(threads, 1)

if __name__ == "__main__":
    unittest.main()
