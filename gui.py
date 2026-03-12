from flask import Flask, send_from_directory, request, jsonify
import threading
import os
from miner import MinerController

app = Flask(__name__, static_folder='frontend/dist', static_url_path='/')
miner_instance = None
miner_thread = None

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/stats')
def get_stats():
    global miner_instance
    if miner_instance:
        return jsonify({
            'is_mining': miner_instance.is_mining,
            'hash_rate': miner_instance.hash_rate,
            'total_hashes': miner_instance.mp_miner.progress_counter.value,
            'shares_found': miner_instance.shares_found,
            'ai_trained': miner_instance.ai.is_trained,
            'ai_samples': getattr(miner_instance.ai, 'total_samples', 0),
            'threads': miner_instance.mp_miner.num_processes,
            'cpu_temp': miner_instance.autotuner.get_max_temp()
        })
    return jsonify({
        'is_mining': False,
        'hash_rate': 0.00,
        'total_hashes': 0,
        'shares_found': 0,
        'ai_trained': False,
        'ai_samples': 0,
        'threads': 0,
        'cpu_temp': None
    })

@app.route('/start', methods=['POST'])
def start_miner():
    global miner_instance, miner_thread
    if miner_instance and miner_instance.is_mining:
        return jsonify({'status': 'Already mining'})

    # Handle both Form and JSON for new React frontend compatibility
    if request.is_json:
        data = request.json
        host = data.get('host', 'pool.supportxmr.com')
        port = int(data.get('port', 3333))
        user = data.get('user')
        password = data.get('pass', 'x')
        threads = int(data.get('threads', 4))
        autotune = data.get('autotune', True)
    else:
        host = request.form.get('host', 'pool.supportxmr.com')
        port = int(request.form.get('port', 3333))
        user = request.form.get('user')
        password = request.form.get('pass', 'x')
        threads = int(request.form.get('threads', 4))
        autotune = request.form.get('autotune') == 'on'

    if not user:
        return jsonify({'status': 'Error: Missing worker username/address'}), 400

    miner_instance = MinerController(host, port, user, password=password)
    miner_instance.mp_miner.num_processes = threads

    def run_miner():
        try:
            miner_instance.start(autotune=autotune)
        except Exception as e:
            print(f"Miner thread error: {e}")

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
    app.run(host=host, port=port, debug=False, use_reloader=False)

if __name__ == '__main__':
    run_gui()
