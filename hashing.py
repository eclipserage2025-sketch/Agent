import randomx
import binascii

class RandomXHasher:
    def __init__(self):
        self.flags = randomx.get_flags()
        self.vm = None
        self.cache = None
        self.current_key = None

    def init_vm(self, key_bytes):
        if self.current_key == key_bytes and self.vm:
            return

        # In Monero, the key for RandomX is the seed hash
        self.cache = randomx.Cache(self.flags)
        self.cache.init(key_bytes)
        self.vm = randomx.VM(self.flags, self.cache)
        self.current_key = key_bytes

    def hash(self, blob_bytes):
        if not self.vm:
            raise ValueError("RandomX VM not initialized. Call init_vm first.")
        # calculate_hash returns the hash bytes if output is NULL (default)
        return self.vm.calculate_hash(blob_bytes)

# Global hasher instance for ease of use in workers
_hasher = RandomXHasher()

def randomx_init(key_bytes):
    _hasher.init_vm(key_bytes)

def randomx_hash(blob_bytes):
    return _hasher.hash(blob_bytes)

if __name__ == "__main__":
    # Test RandomX
    key = b"test key"
    blob = b"test blob"
    randomx_init(key)
    h = randomx_hash(blob)
    print(f"RandomX Hash: {binascii.hexlify(h).decode()}")
