import unittest
from gui import app

class TestGUI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'AI Litecoin Miner Pro', response.data)

    def test_stats_initial(self):
        response = self.app.get('/stats')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['is_mining'], False)
        self.assertEqual(data['hash_rate'], 0.00)

    def test_stop_not_mining(self):
        response = self.app.post('/stop')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'Not mining')

if __name__ == "__main__":
    unittest.main()
