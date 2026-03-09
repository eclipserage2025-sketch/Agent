import multiprocessing
import binascii
import time
from hashing import scrypt_hash

def mining_worker(worker_id, header_base, start_nonce, end_nonce, target, result_queue, stop_event, progress_counter):
    """
    Worker process to perform hashing.
    """
    local_count = 0
    for nonce in range(start_nonce, end_nonce):
        if stop_event.is_set():
            break

        nonce_bytes = nonce.to_bytes(4, 'little')
        header = header_base + nonce_bytes

        hash_bytes = scrypt_hash(header)
        hash_int = int.from_bytes(hash_bytes, 'little')

        local_count += 1
        if local_count >= 10: # Update shared counter periodically
            with progress_counter.get_lock():
                progress_counter.value += local_count
            local_count = 0

        if hash_int < target:
            result_queue.put((nonce, hash_bytes))

class MultiProcessMiner:
    def __init__(self, num_processes=None):
        self.num_processes = num_processes or multiprocessing.cpu_count()
        self.processes = []
        self.result_queue = multiprocessing.Queue()
        self.stop_event = multiprocessing.Event()
        self.progress_counter = multiprocessing.Value('Q', 0) # Unsigned long long

    def start_mining(self, header_base, start_nonce, end_nonce, target):
        self.stop_event.clear()
        self.processes = []
        # Reset progress counter for each new job/range
        # self.progress_counter.value = 0

        nonce_range = end_nonce - start_nonce
        chunk_size = max(1, nonce_range // self.num_processes)

        for i in range(self.num_processes):
            p_start = start_nonce + (i * chunk_size)
            p_end = p_start + chunk_size if i < self.num_processes - 1 else end_nonce
            if p_start >= end_nonce: break

            p = multiprocessing.Process(
                target=mining_worker,
                args=(i, header_base, p_start, p_end, target, self.result_queue, self.stop_event, self.progress_counter)
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
    miner = MultiProcessMiner(num_processes=2)
    header_base = b"0" * 76
    target = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
    miner.start_mining(header_base, 0, 100, target)
    time.sleep(2)
    print(f"Progress: {miner.progress_counter.value} hashes")
    miner.stop_mining()
    results = miner.get_results()
    print(f"Found {len(results)} hashes.")
