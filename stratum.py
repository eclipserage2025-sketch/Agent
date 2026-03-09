import socket
import json
import threading
import time

class StratumClient:
    def __init__(self, host, port, username, password="x"):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.sock = None
        self.message_id = 1
        self.subscription_details = None
        self.extranonce1 = None
        self.extranonce2_size = None
        self.authorized = False
        self.on_new_job = None

    def connect(self):
        self.sock = socket.create_connection((self.host, self.port))
        self.sock_file = self.sock.makefile('r')

    def send_request(self, method, params):
        request = {
            "id": self.message_id,
            "method": method,
            "params": params
        }
        self.sock.sendall((json.dumps(request) + "\n").encode())
        self.message_id += 1

    def subscribe(self):
        self.send_request("mining.subscribe", [])

    def authorize(self):
        self.send_request("mining.authorize", [self.username, self.password])

    def submit(self, worker_name, job_id, extranonce2, ntime, nonce):
        self.send_request("mining.submit", [worker_name, job_id, extranonce2, ntime, nonce])

    def listen(self):
        while True:
            line = self.sock_file.readline()
            if not line:
                break

            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                continue

            if 'id' in message and message['id'] is not None:
                # This is a response to our request
                if message['id'] == 1: # Response to subscribe
                    self.subscription_details = message['result'][0]
                    self.extranonce1 = message['result'][1]
                    self.extranonce2_size = message['result'][2]
                    print(f"Subscribed: extranonce1={self.extranonce1}, extranonce2_size={self.extranonce2_size}")
                elif message['id'] == 2: # Response to authorize
                    self.authorized = message['result']
                    print(f"Authorized: {self.authorized}")
            else:
                # This is a notification (e.g., new job)
                if message.get('method') == 'mining.notify':
                    if self.on_new_job:
                        self.on_new_job(message['params'])

    def start_listening(self):
        thread = threading.Thread(target=self.listen, daemon=True)
        thread.start()

if __name__ == "__main__":
    # Test with a known pool (e.g., litecoinpool.org - but we won't actually mine)
    client = StratumClient("litecoinpool.org", 3333, "username.worker")
    # try:
    #     client.connect()
    #     client.start_listening()
    #     client.subscribe()
    #     time.sleep(1)
    #     client.authorize()
    #     time.sleep(5)
    # except Exception as e:
    #     print(f"Error: {e}")
    print("StratumClient class defined.")
