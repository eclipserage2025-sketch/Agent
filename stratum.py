import socket
import json
import threading
import time
import errno

class StratumClient:
    def __init__(self, host, port, username, password="x"):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.sock = None
        self.sock_file = None
        self.message_id = 1
        self.subscription_details = None
        self.extranonce1 = None
        self.extranonce2_size = None
        self.authorized = False
        self.on_new_job = None
        self.on_difficulty_change = None
        self.running = False
        self.is_connected = False

    def connect(self):
        try:
            print(f"Connecting to {self.host}:{self.port}...")
            self.sock = socket.create_connection((self.host, self.port), timeout=10)
            self.sock_file = self.sock.makefile('r')
            self.is_connected = True
            print("Connected.")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            self.is_connected = False
            return False

    def send_request(self, method, params):
        if not self.is_connected:
            return False

        request = {
            "id": self.message_id,
            "method": method,
            "params": params
        }
        try:
            self.sock.sendall((json.dumps(request) + "\n").encode())
            self.message_id += 1
            return True
        except Exception as e:
            print(f"Error sending request: {e}")
            self.is_connected = False
            return False

    def subscribe(self):
        return self.send_request("mining.subscribe", [])

    def authorize(self):
        return self.send_request("mining.authorize", [self.username, self.password])

    def submit(self, worker_name, job_id, extranonce2, ntime, nonce):
        return self.send_request("mining.submit", [worker_name, job_id, extranonce2, ntime, nonce])

    def listen(self):
        while self.running:
            if not self.is_connected:
                time.sleep(5)
                if self.connect():
                    self.subscribe()
                    time.sleep(1)
                    self.authorize()
                continue

            try:
                line = self.sock_file.readline()
                if not line:
                    print("Disconnected from pool.")
                    self.is_connected = False
                    continue

                message = json.loads(line)
            except Exception as e:
                print(f"Error reading from socket: {e}")
                self.is_connected = False
                continue

            # Responses
            if 'id' in message and message['id'] is not None:
                if message['id'] == 1: # subscribe response
                    if message['result']:
                        self.subscription_details = message['result'][0]
                        self.extranonce1 = message['result'][1]
                        self.extranonce2_size = message['result'][2]
                        print(f"Subscribed: extranonce1={self.extranonce1}")
                elif message['id'] == 2: # authorize response
                    self.authorized = message['result']
                    print(f"Authorized: {self.authorized}")

            # Notifications
            else:
                method = message.get('method')
                if method == 'mining.notify':
                    if self.on_new_job:
                        self.on_new_job(message['params'])
                elif method == 'mining.set_difficulty':
                    if self.on_difficulty_change:
                        self.on_difficulty_change(message['params'][0])

    def start_listening(self):
        self.running = True
        thread = threading.Thread(target=self.listen, daemon=True)
        thread.start()

    def stop(self):
        self.running = False
        if self.sock:
            self.sock.close()
