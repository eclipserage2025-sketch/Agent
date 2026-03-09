import random
import time
from ai_model import AIMiner
from miner_logger import logger

def run_synthetic_training(miner_ai, count=1000):
    """
    Generates synthetic training data and trains the AI model.
    """
    logger.info(f"Starting synthetic training session ({count} samples)...")

    X_synthetic = []
    y_synthetic = []

    # Generate data where nonces have a weak correlation with job hashes
    # (Just for demonstration of learning)
    for _ in range(count):
        job_hash = random.randint(0, 1000)
        timestamp = time.time() % 1000

        # Simulated "winning" nonce based on some pseudo-rule
        nonce = (job_hash * 12345 + int(timestamp * 10)) % 0xFFFFFFFF

        X_synthetic.append([job_hash, timestamp])
        y_synthetic.append(nonce)

    miner_ai.bulk_train(X_synthetic, y_synthetic)
    logger.info("Synthetic training complete. Model updated.")
    return True

if __name__ == "__main__":
    ai = AIMiner()
    run_synthetic_training(ai, 500)
    print(f"Is Trained: {ai.is_trained}")
