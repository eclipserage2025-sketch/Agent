import struct
import binascii

# SV2 Message Header:
# 1 byte - flags (0x00 for standard)
# 1 byte - type
# 3 bytes - length (little-endian)
# total 5 bytes

class SV2Message:
    def __init__(self, msg_type, payload):
        self.msg_type = msg_type
        self.payload = payload

    def serialize(self):
        length = len(self.payload)
        # Type is 1 byte, Length is 3 bytes
        header = struct.pack("<BB", 0x00, self.msg_type)
        header += length.to_bytes(3, 'little')
        return header + self.payload

    @staticmethod
    def deserialize(data):
        if len(data) < 5:
            return None, 0

        flags = data[0]
        msg_type = data[1]
        length = int.from_bytes(data[2:5], 'little')

        if len(data) < 5 + length:
            return None, 0

        payload = data[5:5+length]
        return SV2Message(msg_type, payload), 5 + length

# SV2 Message Types (Mining Protocol)
MSG_SETUP_CONNECTION = 0x00
MSG_SETUP_CONNECTION_SUCCESS = 0x01
MSG_OPEN_STANDARD_MINING_CHANNEL = 0x10
MSG_OPEN_STANDARD_MINING_CHANNEL_SUCCESS = 0x11
MSG_NEW_MINING_JOB = 0x12
MSG_SUBMIT_SHARES_STANDARD = 0x15

if __name__ == "__main__":
    msg = SV2Message(MSG_SETUP_CONNECTION, b"test")
    raw = msg.serialize()
    print(f"Serialized: {binascii.hexlify(raw).decode()}")

    back, size = SV2Message.deserialize(raw)
    print(f"Deserialized Type: {back.msg_type}, Payload: {back.payload}")
