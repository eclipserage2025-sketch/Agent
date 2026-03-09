from noise.connection import NoiseConnection
import socket
import struct

# Stratum V2 Noise Handshake: Noise_NX_25519_ChaChaPoly_BLAKE2b
# Handshake: -> e, <- e, ee, s, es

def perform_sv2_handshake(sock, pool_pubkey):
    """
    Performs the Noise NX handshake for SV2.
    """
    noise = NoiseConnection.from_name(b'Noise_NX_25519_ChaChaPoly_BLAKE2b')
    noise.set_as_initiator()

    # 1. Initiator sends first message (empty payload)
    # This generates 'e'
    msg1 = noise.write_message()
    # SV2 Header for handshake (0x00 flag, 0x00 type, length 3 bytes)
    # Header: 5 bytes
    header = struct.pack("<BB", 0x00, 0x00) + len(msg1).to_bytes(3, 'little')
    sock.sendall(header + msg1)

    # 2. Receive response from pool
    # This includes 'e' and 'ee'
    resp_header = sock.recv(5)
    if not resp_header: return None
    resp_len = int.from_bytes(resp_header[2:5], 'little')
    resp_msg = sock.recv(resp_len)

    noise.read_message(resp_msg)

    # 3. Receive final message from pool (if any)
    # Noise NX requires the server to send its static key 's'
    # Actually, the handshake is 3 messages in NX?
    # -> e, <- e, ee, s, es
    # Wait, Noise NX is:
    #   -> e
    #   <- e, ee, s, es

    # After read_message, the handshake is complete
    return noise

if __name__ == "__main__":
    print("SV2 Noise Handshake logic defined.")
