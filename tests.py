import unittest
import binascii
import struct
from hashing import scrypt_hash, double_sha256
from miner import build_merkle_root, MinerController

class TestMiner(unittest.TestCase):

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
        controller = MinerController("localhost", 3333, "user")
        version = "00000001"
        prevhash = "0000000000000000000000000000000000000000000000000000000000000000"
        merkle_root = "0000000000000000000000000000000000000000000000000000000000000001"
        ntime = "50000000"
        nbits = "1d00ffff"
        nonce = 123456

        header = controller.serialize_header(version, prevhash, merkle_root, ntime, nbits, nonce)
        self.assertEqual(len(header), 80)
        # Check little-endian version (01000000 -> 00000001)
        self.assertEqual(header[0:4], b"\x01\x00\x00\x00")
        # Check nonce at the end (123456 -> 0x0001E240 -> 40E20100)
        self.assertEqual(header[76:80], struct.pack("<I", nonce))

if __name__ == "__main__":
    unittest.main()
