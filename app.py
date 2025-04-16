from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import psutil
import json
from datetime import datetime
import sqlite3
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, async_mode='threading')

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('performance.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS performance_metrics
                 (timestamp DATETIME, cpu_usage REAL, memory_usage REAL, 
                  active_threads INTEGER, completed_tasks INTEGER)''')
    conn.commit()
    conn.close()

# Global variables for thread management
active_threads = 0
completed_tasks = 0
threads = []

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
def start_threads():
    global active_threads
    data = request.json
    num_threads = data.get('num_threads', 1)
    
    for _ in range(num_threads):
        thread = threading.Thread(target=worker_thread)
        thread.daemon = True
        thread.start()
        threads.append(thread)
        active_threads += 1
    
    return jsonify({'status': 'success', 'active_threads': active_threads})

@app.route('/api/stop_threads', methods=['POST'])
def stop_threads():
    global active_threads
    active_threads = 0
    threads.clear()
    return jsonify({'status': 'success', 'active_threads': active_threads})

@app.route('/api/performance')
def get_performance():
    cpu_usage = psutil.cpu_percent()
    memory_usage = psutil.virtual_memory().percent
    
    # Store metrics in database
    conn = sqlite3.connect('performance.db')
    c = conn.cursor()
    c.execute('INSERT INTO performance_metrics VALUES (?, ?, ?, ?, ?)',
              (datetime.now(), cpu_usage, memory_usage, active_threads, completed_tasks))
    conn.commit()
    conn.close()
    
    return jsonify({
        'cpu_usage': cpu_usage,
        'memory_usage': memory_usage,
        'active_threads': active_threads,
        'completed_tasks': completed_tasks
    })

def worker_thread():
    global completed_tasks
    while active_threads > 0:
        # Simulate some work
        time.sleep(1)
        completed_tasks += 1
        socketio.emit('task_completed', {'completed_tasks': completed_tasks})

def background_monitor():
    while True:
        socketio.emit('performance_update', {
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'active_threads': active_threads,
            'completed_tasks': completed_tasks
        })
        time.sleep(1)

if __name__ == '__main__':
    init_db()
    monitor_thread = threading.Thread(target=background_monitor)
    monitor_thread.daemon = True
    monitor_thread.start()
    socketio.run(app, debug=True) 