import multiprocessing
import binascii
import time
from hashing import randomx_init, randomx_hash

def mining_worker(worker_id, blob_hex, target, seed_hash_hex, start_nonce, end_nonce, result_queue, stop_event, progress_counter):
    """
    Worker process to perform RandomX hashing for Monero.
    """
    try:
        blob = binascii.unhexlify(blob_hex)
        seed_hash = binascii.unhexlify(seed_hash_hex)

        # Initialize RandomX VM for this process
        randomx_init(seed_hash)

        local_count = 0
        # Monero nonces are typically 4 bytes at a specific offset in the blob.
        # However, Stratum often sends a blob where we just need to replace the nonce bytes.
        # The nonce offset is usually at byte 39 in the hashing blob for Monero.
        # But we will handle it by taking the blob and inserting the nonce.

        # Assuming standard Monero blob where nonce is at 39-42
        # (Actually, it's pool dependent, but most Stratum pools provide a blob with a placeholder)

        for nonce in range(start_nonce, end_nonce):
            if stop_event.is_set():
                break

            # Nonce is 4 bytes
            nonce_bytes = nonce.to_bytes(4, 'little')
            # Insert nonce into blob at offset 39
            current_blob = blob[:39] + nonce_bytes + blob[43:]

            hash_bytes = randomx_hash(current_blob)
            # RandomX hash is 32 bytes. Monero target comparison is usually against the reversed hash or just as a large int.
            # In Monero, hash_int < target
            hash_int = int.from_bytes(hash_bytes, 'little')

            local_count += 1
            if local_count >= 5: # Update shared counter (RandomX is slow, so frequent updates are fine)
                with progress_counter.get_lock():
                    progress_counter.value += local_count
                local_count = 0

            if hash_int < target:
                result_queue.put((nonce, binascii.hexlify(hash_bytes).decode()))

    except Exception as e:
        print(f"Worker {worker_id} error: {e}")

class MultiProcessMiner:
    def __init__(self, num_processes=None):
        self.num_processes = num_processes or multiprocessing.cpu_count()
        self.processes = []
        self.result_queue = multiprocessing.Queue()
        self.stop_event = multiprocessing.Event()
        self.progress_counter = multiprocessing.Value('Q', 0)

    def start_mining(self, blob_hex, target, seed_hash_hex, start_nonce, end_nonce):
        self.stop_event.clear()
        self.processes = []

        nonce_range = end_nonce - start_nonce
        chunk_size = max(1, nonce_range // self.num_processes)

        for i in range(self.num_processes):
            p_start = start_nonce + (i * chunk_size)
            p_end = p_start + chunk_size if i < self.num_processes - 1 else end_nonce
            if p_start >= end_nonce: break

            p = multiprocessing.Process(
                target=mining_worker,
                args=(i, blob_hex, target, seed_hash_hex, p_start, p_end, self.result_queue, self.stop_event, self.progress_counter)
            )
            p.start()
            self.processes.append(p)

    def stop_mining(self):
        self.stop_event.set()
        for p in self.processes:
            p.join(timeout=1)
            if p.is_alive():
                p.terminate()
        self.processes = []

    def get_results(self):
        results = []
        while not self.result_queue.empty():
            results.append(self.result_queue.get())
        return results

    def is_running(self):
        return any(p.is_alive() for p in self.processes)

if __name__ == "__main__":
    print("MultiProcessMiner for Monero defined.")
