import socket
import json
import threading
import time
import binascii

class MoneroStratumClient:
    def __init__(self, host, port, username, password="x"):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.sock = None
        self.message_id = 1
        self.running = False
        self.is_connected = False
        self.job = None
        self.on_new_job = None
        self.worker_id = None

    def connect(self):
        try:
            print(f"Connecting to {self.host}:{self.port} (Monero Stratum)...")
            self.sock = socket.create_connection((self.host, self.port), timeout=10)
            self.is_connected = True
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
            "jsonrpc": "2.0",
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

    def login(self):
        return self.send_request("login", {
            "login": self.username,
            "pass": self.password,
            "agent": "AI-Monero-Miner-Ultra/1.0"
        })

    def submit(self, job_id, nonce, result):
        return self.send_request("submit", {
            "id": self.worker_id,
            "job_id": job_id,
            "nonce": nonce,
            "result": result
        })

    def listen(self):
        while self.running:
            if not self.is_connected:
                time.sleep(5)
                if self.connect():
                    self.login()
                continue

            try:
                data = self.sock.recv(4096)
                if not data:
                    print("Disconnected from pool.")
                    self.is_connected = False
                    continue

                lines = data.decode().split('\n')
                for line in lines:
                    if not line.strip(): continue
                    message = json.loads(line)
                    self.handle_message(message)
            except Exception as e:
                print(f"Error reading from socket: {e}")
                self.is_connected = False
                continue

    def handle_message(self, message):
        # Handle login response
        if "id" in message and message["id"] == 1:
            if message.get("result"):
                res = message["result"]
                self.worker_id = res.get("id")
                job = res.get("job")
                if job and self.on_new_job:
                    self.on_new_job(job)
                print(f"Logged in. Worker ID: {self.worker_id}")
            elif message.get("error"):
                print(f"Login error: {message['error']}")

        # Handle job notification (Monero pools often send this as a notification or result of submit)
        method = message.get("method")
        if method == "job":
            if self.on_new_job:
                self.on_new_job(message["params"])
        elif "result" in message and message.get("id") != 1:
            # Could be a result of submission or periodic status
            pass

    def start_listening(self):
        self.running = True
        thread = threading.Thread(target=self.listen, daemon=True)
        thread.start()

    def stop(self):
        self.running = False
        if self.sock:
            self.sock.close()

if __name__ == "__main__":
    print("MoneroStratumClient defined.")
