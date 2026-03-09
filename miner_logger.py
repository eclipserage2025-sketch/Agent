import logging
from collections import deque

# Global log buffer for the GUI
log_buffer = deque(maxlen=100)

class BufferHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        log_buffer.append(log_entry)

def setup_logger():
    # File Logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler("miner.log"),
            logging.StreamHandler(),
            BufferHandler()
        ]
    )
    return logging.getLogger("miner")

def get_recent_logs():
    return list(log_buffer)

logger = setup_logger()
if __name__ == "__main__":
    logger.info("Miner logger initialized.")
    print(get_recent_logs())
