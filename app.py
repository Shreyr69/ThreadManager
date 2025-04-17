from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import psutil
import json
from datetime import datetime
import sqlite3
import threading
import time
from contextlib import contextmanager
import logging
from concurrent.futures import ThreadPoolExecutor
import atexit

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, async_mode='threading')

# Enable CORS
CORS(app)

# Configure rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@contextmanager
def get_db_connection():
    conn = sqlite3.connect('performance.db')
    try:
        yield conn
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        raise
    finally:
        conn.close()

def init_db():
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS performance_metrics
                     (timestamp DATETIME, cpu_usage REAL, memory_usage REAL, 
                      active_threads INTEGER, completed_tasks INTEGER)''')
            conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

# Thread management
thread_pool = ThreadPoolExecutor(max_workers=10)
thread_lock = threading.Lock()
active_threads = 0
completed_tasks = 0
total_tasks = 0
threads = []

def cleanup_threads():
    """Cleanup function to be called on application exit"""
    global active_threads
    with thread_lock:
        active_threads = 0
    thread_pool.shutdown(wait=True)
    logger.info("Thread pool shutdown completed")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/documentation')
def documentation():
    return render_template('documentation.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/api/start_threads', methods=['POST'])
@limiter.limit("10 per minute")
def start_threads():
    global active_threads, total_tasks
    try:
        data = request.json
        num_threads = data.get('num_threads', 1)
        
        if not isinstance(num_threads, int) or num_threads < 1:
            return jsonify({'error': 'Invalid number of threads'}), 400
        
        with thread_lock:
            for _ in range(num_threads):
                if active_threads >= 10:  # Max threads limit
                    break
                future = thread_pool.submit(worker_thread)
                threads.append(future)
                active_threads += 1
                total_tasks += 1  # Increment total tasks
        
        return jsonify({
            'status': 'success', 
            'active_threads': active_threads,
            'total_tasks': total_tasks
        })
    except Exception as e:
        logger.error(f"Error starting threads: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/stop_threads', methods=['POST'])
@limiter.limit("10 per minute")
def stop_threads():
    global active_threads, total_tasks
    try:
        with thread_lock:
            active_threads = 0
            threads.clear()
            total_tasks = 0  # Reset total tasks
        return jsonify({
            'status': 'success', 
            'active_threads': active_threads,
            'total_tasks': total_tasks
        })
    except Exception as e:
        logger.error(f"Error stopping threads: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/performance')
@limiter.limit("60 per minute")
def get_performance():
    try:
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('INSERT INTO performance_metrics VALUES (?, ?, ?, ?, ?)',
                    (datetime.now(), cpu_usage, memory_usage, active_threads, completed_tasks))
            conn.commit()
        
        return jsonify({
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage,
            'active_threads': active_threads,
            'completed_tasks': completed_tasks
        })
    except Exception as e:
        logger.error(f"Error in performance endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

def worker_thread():
    global completed_tasks
    try:
        while active_threads > 0:
            time.sleep(1)
            with thread_lock:
                completed_tasks += 1
            socketio.emit('task_completed', {'completed_tasks': completed_tasks})
    except Exception as e:
        logger.error(f"Error in worker thread: {e}")

def background_monitor():
    while True:
        socketio.emit('performance_update', {
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'active_threads': active_threads,
            'completed_tasks': completed_tasks,
            'total_tasks': total_tasks
        })
        time.sleep(1)

if __name__ == '__main__':
    init_db()
    atexit.register(cleanup_threads)
    monitor_thread = threading.Thread(target=background_monitor)
    monitor_thread.daemon = True
    monitor_thread.start()
    socketio.run(app, debug=True) 
