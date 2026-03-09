import hashlib

def scrypt_hash(header):
    """
    Litecoin uses Scrypt with parameters N=1024, r=1, p=1.
    The header is a serialized 80-byte block header.
    The result is a 32-byte hash (little-endian).
    """
    # hashlib.scrypt(password, salt, n, r, p, maxmem=0, dklen=64)
    # For Litecoin, the salt is the same as the password.
    # However, some implementations treat it differently.
    # Standard Scrypt for LTC is scrypt(header, header, 1024, 1, 1, 32).
    return hashlib.scrypt(header, salt=header, n=1024, r=1, p=1, dklen=32)

def double_sha256(data):
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()

if __name__ == "__main__":
    # Test with 80-byte dummy header
    header = b"0" * 80
    h = scrypt_hash(header)
    print(f"Scrypt Hash: {h.hex()}")
