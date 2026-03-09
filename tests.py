import unittest
import binascii
import struct
import multiprocessing
import time
from hashing import scrypt_hash, double_sha256
from miner import build_merkle_root, MinerController
from ai_model import AIMiner
from worker import MultiProcessMiner

class TestUpgradedMiner(unittest.TestCase):

    def test_scrypt_hash(self):
        # 80-byte header
        header = b"0" * 80
        h = scrypt_hash(header)
        self.assertEqual(len(h), 32)

    def test_double_sha256(self):
        h = double_sha256(b"hello")
        self.assertEqual(len(h), 32)

    def test_merkle_root(self):
        # Test case for Merkle Root (simplified values)
        coinb1 = "0100000001"
        coinb2 = "ffffffff"
        extranonce1 = "00000001"
        extranonce2 = "00000002"
        merkle_branch = [
            "0000000000000000000000000000000000000000000000000000000000000001",
            "0000000000000000000000000000000000000000000000000000000000000002"
        ]

        # Should complete without error
        mr = build_merkle_root(coinb1, coinb2, extranonce1, extranonce2, merkle_branch)
        self.assertEqual(len(mr), 64)

    def test_serialize_header(self):
        def serialize_local(v, ph, mr, nt, nb, n):
            def reverse_hex(hex_str):
                return binascii.hexlify(binascii.unhexlify(hex_str)[::-1]).decode()
            header = (
                reverse_hex(v) +
                reverse_hex(ph) +
                reverse_hex(mr) +
                reverse_hex(nt) +
                reverse_hex(nb) +
                binascii.hexlify(struct.pack("<I", n)).decode()
            )
            return binascii.unhexlify(header)

        version = "00000001"
        prevhash = "0" * 64
        merkle_root = "0" * 64
        ntime = "50000000"
        nbits = "1d00ffff"
        nonce = 123456

        header = serialize_local(version, prevhash, merkle_root, ntime, nbits, nonce)
        self.assertEqual(len(header), 80)

    def test_ai_neural_network(self):
        ai = AIMiner()
        job_id = "test_job"
        ai.range_size = 5000
        for i in range(10):
            ai.collect_feedback(job_id, i * 1000, True)

        self.assertTrue(ai.is_trained)
        # Test default range_size
        start, end = ai.predict_nonce_range(job_id)
        self.assertEqual(end - start, 5000)

        # Test override range_size (the fix)
        start2, end2 = ai.predict_nonce_range(job_id, range_size=10000)
        self.assertEqual(end2 - start2, 10000)

    def test_multiprocess_miner(self):
        miner = MultiProcessMiner(num_processes=2)
        header_base = b"0" * 76
        target = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
        miner.start_mining(header_base, 0, 10, target)
        time.sleep(1)
        miner.stop_mining()
        results = miner.get_results()
        self.assertEqual(len(results), 10)

if __name__ == "__main__":
    unittest.main()
