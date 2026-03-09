import struct
import binascii
import time
import hashlib
from hashing import scrypt_hash, double_sha256
from stratum import StratumClient
from ai_model import AIMiner

def reverse_hex(hex_str):
    """Reverses byte order of a hex string."""
    return binascii.hexlify(binascii.unhexlify(hex_str)[::-1]).decode()

def build_merkle_root(coinb1, coinb2, extranonce1, extranonce2, merkle_branch):
    """
    Builds the Merkle Root from coinbase parts and the merkle branch.
    All inputs are hex strings.
    """
    # 1. Construct the coinbase transaction
    coinbase = coinb1 + extranonce1 + extranonce2 + coinb2
    coinbase_bytes = binascii.unhexlify(coinbase)

    # 2. Hash the coinbase transaction (double SHA256)
    coinbase_hash = double_sha256(coinbase_bytes)

    # 3. Combine with merkle branch
    merkle_root = coinbase_hash
    for branch in merkle_branch:
        branch_bytes = binascii.unhexlify(branch)
        merkle_root = double_sha256(merkle_root + branch_bytes)

    return binascii.hexlify(merkle_root).decode()

class MinerController:
    def __init__(self, host, port, username, password="x"):
        self.client = StratumClient(host, port, username, password)
        self.ai = AIMiner()
        self.is_mining = False
        self.current_job = None
        self.target = 0x00000ffff0000000000000000000000000000000000000000000000000000000
        self.diff = 1

    def set_difficulty(self, diff):
        self.diff = diff
        target_max = 0x00000ffff0000000000000000000000000000000000000000000000000000000
        self.target = target_max // diff

    def handle_new_job(self, params):
        self.current_job = {
            'job_id': params[0],
            'prevhash': params[1],
            'coinb1': params[2],
            'coinb2': params[3],
            'merkle_branch': params[4],
            'version': params[5],
            'nbits': params[6],
            'ntime': params[7],
            'clean_jobs': params[8]
        }
        print(f"New job received: {self.current_job['job_id']}")

    def start(self):
        self.client.on_new_job = self.handle_new_job
        self.client.connect()
        self.client.start_listening()
        self.client.subscribe()
        time.sleep(1)
        self.client.authorize()
        self.is_mining = True
        self.mining_loop()

    def serialize_header(self, version, prevhash, merkle_root, ntime, nbits, nonce):
        """
        Serializes an 80-byte Litecoin block header (little-endian).
        All inputs are hex strings, nonce is integer.
        """
        header = (
            reverse_hex(version) +
            reverse_hex(prevhash) +
            reverse_hex(merkle_root) +
            reverse_hex(ntime) +
            reverse_hex(nbits) +
            binascii.hexlify(struct.pack("<I", nonce)).decode()
        )
        return binascii.unhexlify(header)

    def mining_loop(self):
        while self.is_mining:
            if self.current_job is None or self.client.extranonce1 is None:
                time.sleep(0.1)
                continue

            job = self.current_job
            extranonce1 = self.client.extranonce1
            # extranonce2 can be anything (incrementing)
            extranonce2 = "00000001"

            # 1. Build Merkle Root
            merkle_root = build_merkle_root(
                job['coinb1'], job['coinb2'], extranonce1, extranonce2, job['merkle_branch']
            )

            job_id = job['job_id']
            # AI predicts the nonce range
            start_nonce, end_nonce = self.ai.predict_nonce_range(job_id)
            print(f"Mining on job {job_id} using AI-predicted nonce range: {start_nonce} to {end_nonce}")

            for nonce in range(start_nonce, end_nonce):
                if self.current_job != job:
                    break

                # 2. Serialize header
                header_bytes = self.serialize_header(
                    job['version'], job['prevhash'], merkle_root, job['ntime'], job['nbits'], nonce
                )

                # 3. Hash header
                hash_bytes = scrypt_hash(header_bytes)
                hash_int = int.from_bytes(hash_bytes, 'little')

                # 4. Check against target
                if hash_int < self.target:
                    print(f"Found share! Nonce: {nonce}, Hash: {binascii.hexlify(hash_bytes).decode()}")
                    # 5. Submit share
                    self.client.submit(self.client.username, job_id, extranonce2, job['ntime'], hex(nonce)[2:].zfill(8))

                    # Provide feedback to AI
                    self.ai.collect_feedback(job_id, nonce, True)

            # Briefly yield
            time.sleep(0.01)

if __name__ == "__main__":
    print("MinerController and Merkle Root logic defined.")
