import socket
import threading
import time
import struct
from sv2_protocol import SV2Message, MSG_SETUP_CONNECTION, MSG_OPEN_STANDARD_MINING_CHANNEL, MSG_NEW_MINING_JOB
from sv2_noise import perform_sv2_handshake
from miner_logger import logger

class StratumV2Client:
    def __init__(self, host, port, username, pool_pubkey=None):
        self.host = host
        self.port = port
        self.username = username
        self.pool_pubkey = pool_pubkey
        self.sock = None
        self.noise = None
        self.is_connected = False
        self.on_new_job = None
        self.running = False
        self.message_id = 1

    def connect(self):
        try:
            self.sock = socket.create_connection((self.host, self.port), timeout=10)
            if self.pool_pubkey:
                self.noise = perform_sv2_handshake(self.sock, self.pool_pubkey)

            self.is_connected = True
            logger.info(f"Connected to SV2 Pool {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"SV2 Connection error: {e}")
            return False

    def setup_connection(self):
        payload = struct.pack("<HHI", 2, 2, 0) + b"\x00"
        msg = SV2Message(MSG_SETUP_CONNECTION, payload)
        self.send_message(msg)

    def open_channel(self, user):
        user_bytes = user.encode()
        payload = struct.pack("<B", len(user_bytes)) + user_bytes
        payload += struct.pack("<d", 0.0)
        payload += b"\x00" * 32

        msg = SV2Message(MSG_OPEN_STANDARD_MINING_CHANNEL, payload)
        self.send_message(msg)

    def send_message(self, msg):
        raw = msg.serialize()
        if self.noise:
            encrypted = self.noise.encrypt(raw)
            header = len(encrypted).to_bytes(3, 'little')
            self.sock.sendall(header + encrypted)
        else:
            self.sock.sendall(raw)

    def listen(self):
        while self.running:
            if not self.is_connected:
                time.sleep(5)
                if self.connect():
                    self.setup_connection()
                    time.sleep(1)
                    self.open_channel(self.username)
                continue

            try:
                header = self.sock.recv(5)
                if not header:
                    self.is_connected = False
                    continue

                msg_type = header[1]
                length = int.from_bytes(header[2:5], 'little')
                payload = self.sock.recv(length)

                if msg_type == MSG_NEW_MINING_JOB:
                    if self.on_new_job:
                        self.on_new_job(payload)
            except Exception as e:
                logger.error(f"SV2 Listen error: {e}")
                self.is_connected = False
                continue

    def start_listening(self): # Fixed method name to match MinerController expectation
        self.running = True
        thread = threading.Thread(target=self.listen, daemon=True)
        thread.start()

    def stop(self):
        self.running = False
        if self.sock:
            self.sock.close()
            self.is_connected = False
