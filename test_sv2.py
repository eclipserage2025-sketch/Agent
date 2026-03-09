import unittest
import binascii
from sv2_protocol import SV2Message, MSG_SETUP_CONNECTION

class TestSV2(unittest.TestCase):
    def test_sv2_serialize(self):
        msg = SV2Message(MSG_SETUP_CONNECTION, b"test")
        raw = msg.serialize()
        self.assertEqual(raw[0], 0x00) # flags
        self.assertEqual(raw[1], MSG_SETUP_CONNECTION) # type
        self.assertEqual(int.from_bytes(raw[2:5], 'little'), 4) # length
        self.assertEqual(raw[5:], b"test")

    def test_sv2_deserialize(self):
        raw = b"\x00\x00\x04\x00\x00test"
        msg, size = SV2Message.deserialize(raw)
        self.assertEqual(msg.msg_type, 0x00)
        self.assertEqual(msg.payload, b"test")
        self.assertEqual(size, 9)

if __name__ == "__main__":
    unittest.main()
