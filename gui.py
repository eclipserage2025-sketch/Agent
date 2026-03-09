from flask import Flask, render_template, request, jsonify
import threading
import time
from miner import MinerController

app = Flask(__name__)
miner_instance = None
miner_thread = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stats')
def get_stats():
    global miner_instance
    if miner_instance:
        return jsonify({
            'is_mining': miner_instance.is_mining,
            'hash_rate': miner_instance.hash_rate,
            'total_hashes': miner_instance.mp_miner.progress_counter.value,
            'shares_found': miner_instance.shares_found,
            'ai_trained': miner_instance.ai.is_trained
        })
    return jsonify({
        'is_mining': False,
        'hash_rate': 0.00,
        'total_hashes': 0,
        'shares_found': 0,
        'ai_trained': False
    })

@app.route('/start', methods=['POST'])
def start_miner():
    global miner_instance, miner_thread
    if miner_instance and miner_instance.is_mining:
        return jsonify({'status': 'Already mining'})

    host = request.form.get('host', 'litecoinpool.org')
    port = int(request.form.get('port', 3333))
    user = request.form.get('user')
    threads = int(request.form.get('threads', 4))

    if not user:
        return jsonify({'status': 'Error: Missing worker username'}), 400

    miner_instance = MinerController(host, port, user)
    miner_instance.mp_miner.num_processes = threads

    def run_miner():
        try:
            miner_instance.start()
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
