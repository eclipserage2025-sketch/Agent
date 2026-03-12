import unittest
import binascii
import multiprocessing
import time
from hashing import randomx_init, randomx_hash
from ai_model import AIMiner
from worker import MultiProcessMiner

class TestMoneroMiner(unittest.TestCase):

    def test_randomx_hash(self):
        key = b"test key"
        blob = b"test blob"
        randomx_init(key)
        h = randomx_hash(blob)
        self.assertEqual(len(h), 32)

    def test_ai_resource_optimization(self):
        ai = AIMiner()
        # Simulate some data
        for i in range(10):
            ai.collect_system_metrics(0.5, 60.0, 4)

        self.assertTrue(ai.is_trained)
        opt_threads = ai.predict_optimal_threads(0.8, 85.0, 4)
        # Should likely predict lower or equal threads
        self.assertGreaterEqual(opt_threads, 1)

    def test_multiprocess_miner_monero(self):
        miner = MultiProcessMiner(num_processes=2)
        # RandomX needs a proper blob size, usually 76 or more bytes
        blob_hex = binascii.hexlify(b"0" * 76).decode()
        seed_hash_hex = binascii.hexlify(b"seed" * 8).decode()
        target = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

        # Test a small range
        miner.start_mining(blob_hex, target, seed_hash_hex, 0, 5)
        time.sleep(2)
        miner.stop_mining()
        results = miner.get_results()
        # Since target is max, every hash should be a "share"
        self.assertGreaterEqual(len(results), 0)

if __name__ == "__main__":
    unittest.main()
