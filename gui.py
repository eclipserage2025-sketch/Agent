from flask import Flask, render_template, request, jsonify
from waitress import serve
import threading
import time
from miner import MinerController
from config_manager import load_config, save_config
from miner_logger import logger, get_recent_logs
from train_ai import run_synthetic_training

app = Flask(__name__)
miner_instance = None
miner_thread = None
# Shared AI instance that exists even when not mining
from ai_model import AIMiner
global_ai = AIMiner()

@app.route('/')
def index():
    config = load_config()
    return render_template('index.html', config=config)

@app.route('/stats')
def get_stats():
    global miner_instance, global_ai
    active_ai = miner_instance.ai if miner_instance else global_ai

    if miner_instance:
        return jsonify({
            'is_mining': miner_instance.is_mining,
            'hash_rate': miner_instance.hash_rate,
            'total_hashes': miner_instance.mp_miner.progress_counter.value,
            'shares_found': miner_instance.shares_found,
            'ai_trained': active_ai.is_trained,
            'threads': miner_instance.mp_miner.num_processes,
            'v2': miner_instance.v2,
            'gpu_active': miner_instance.gpu_miner.is_available,
            'best_coin': miner_instance.profit_mgr.best_coin
        })
    return jsonify({
        'is_mining': False, 'hash_rate': 0.00, 'total_hashes': 0,
        'shares_found': 0, 'ai_trained': active_ai.is_trained, 'threads': 0,
        'v2': False, 'gpu_active': False, 'best_coin': 'LTC'
    })

@app.route('/logs')
def get_logs():
    return jsonify(get_recent_logs())

@app.route('/train', methods=['POST'])
def train_ai():
    global miner_instance, global_ai
    active_ai = miner_instance.ai if miner_instance else global_ai

    def background_train():
        run_synthetic_training(active_ai, count=2000)

    threading.Thread(target=background_train, daemon=True).start()
    return jsonify({'status': 'Training started in background'})

@app.route('/start', methods=['POST'])
def start_miner():
    global miner_instance, miner_thread, global_ai
    if miner_instance and miner_instance.is_mining:
        return jsonify({'status': 'Already mining'})

    host = request.form.get('host', 'litecoinpool.org')
    port = int(request.form.get('port', 3333))
    user = request.form.get('user')
    threads = int(request.form.get('threads', 4))
    v2 = request.form.get('v2') == 'on'
    autotune = request.form.get('autotune') == 'on'
    profit_switch = request.form.get('profit_switch') == 'on'

    if not user:
        return jsonify({'status': 'Error: Missing worker username'}), 400

    save_config({
        "host": host, "port": port, "user": user,
        "threads": threads, "v2": v2, "autotune": autotune,
        "profit_switch": profit_switch
    })

    return do_start(host, port, user, threads, v2, autotune, profit_switch)

def do_start(host, port, user, threads, v2, autotune, profit_switch):
    global miner_instance, miner_thread, global_ai
    miner_instance = MinerController(host, port, user, v2=v2)
    # Inherit global AI progress
    if global_ai.is_trained:
        miner_instance.ai = global_ai

    miner_instance.mp_miner.num_processes = threads

    def run_miner():
        try:
            miner_instance.start(autotune=autotune, profit_switch=profit_switch)
        except Exception as e:
            logger.error(f"Miner thread error: {e}")

    miner_thread = threading.Thread(target=run_miner, daemon=True)
    miner_thread.start()
    return jsonify({'status': 'Mining started'})

@app.route('/stop', methods=['POST'])
def stop_miner():
    global miner_instance
    if miner_instance:
        miner_instance.stop()
        return jsonify({'status': 'Mining stopped'})
    return jsonify({'status': 'Not mining'})

def run_gui(host='127.0.0.1', port=5000):
    logger.info(f"Starting Production Web Server at http://{host}:{port}")
    config = load_config()
    if config.get("autostart") and config.get("user"):
        logger.info("Auto-start enabled. Launching miner...")
        do_start(config['host'], config['port'], config['user'],
                 config['threads'], config['v2'], config['autotune'],
                 config.get('profit_switch', True))

    serve(app, host=host, port=port, _quiet=True)

if __name__ == '__main__':
    run_gui()
