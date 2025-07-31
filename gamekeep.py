#!/usr/bin/env python3

import sys, os, sqlite3, time, signal,subprocess
from threading import Thread, Event

# Try Flask import
try:
    from flask import Flask, request, jsonify
except ImportError:
    sys.exit("Flask is not installed. Please run: pip install flask")

# Configuration
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
DB_PATH       = os.path.join(BASE_DIR, 'time.db')
EMU_PROC_NAME = 'retroarch'
AUTH_USER     = 'clerk'
AUTH_PASS     = 'P@ssw0rd'

# Initialize DB
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('CREATE TABLE IF NOT EXISTS credits(sec INTEGER)')
    if conn.execute('SELECT COUNT(*) FROM credits').fetchone()[0] == 0:
        conn.execute('INSERT INTO credits VALUES(0)')
    conn.commit(); conn.close()

init_db()

# Time helpers
def get_secs():
    conn = sqlite3.connect(DB_PATH)
    try:
        row = conn.execute('SELECT sec FROM credits').fetchone()
        return row[0] if row else 0
    except sqlite3.OperationalError:
        init_db(); return 0
    finally: conn.close()

def set_secs(sec):
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute('UPDATE credits SET sec=?', (max(sec,0),))
        conn.commit()
    finally: conn.close()

# Flask app setup
app = Flask(__name__)
stop_event = Event()

@app.route('/add', methods=['POST'])
def add_time():
    auth = request.authorization
    if not auth or auth.username!=AUTH_USER or auth.password!=AUTH_PASS:
        return 'Unauthorized', 401
    try: minutes = int(request.args.get('m',0))
    except: return 'Invalid minutes', 400
    secs = get_secs() + minutes*60
    set_secs(secs)
    return jsonify(remaining=secs)

@app.route('/end', methods=['POST'])
def end_session():
    auth = request.authorization
    if not auth or auth.username!=AUTH_USER or auth.password!=AUTH_PASS:
        return 'Unauthorized', 401
    set_secs(0)
    # kill emulator
    for pid in os.popen(f"pgrep {EMU_PROC_NAME}").read().split():
        try: os.kill(int(pid), signal.SIGTERM)
        except: pass
    return jsonify(remaining=0)

@app.route('/status')
def status():
    return jsonify(remaining=get_secs())

@app.route('/')
def control_page():
    return '''<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Arcade Timekeeper Control</title>
  <style>
    body { margin:0; font-family:sans-serif; background:#ccc; }
    .container { width:80vw; height:80vh; margin:5vh auto; background:#999; border:4px solid #000; }
    .status-box { width:60%; height:20%; background:#666; border:4px solid #000; margin:20px auto; padding:10px; color:#fff; font-size:1.1rem; }
    .buttons { display:flex; justify-content:center; gap:20px; margin-top:40px; }
    .btn { border:4px solid #000; padding:20px 30px; font-size:1rem; cursor:pointer; }
    .btn-blue { background:#00bfff; color:#000; }
    .btn-red { background:#e60000; color:#000; }
  </style>
</head>
<body>
  <div class="container">
    <div class="status-box">
      <strong>Active Session Status:</strong>
      <div id="remaining">Loading...</div>
    </div>
    <div class="buttons">
      <button class="btn btn-blue" onclick="addTime(30)">30 Min</button>
      <button class="btn btn-blue" onclick="addTime(60)">1 Hour</button>
      <button class="btn btn-red" onclick="endSession()">End Session</button>
    </div>
  </div>
  <script>
    async function fetchStatus() {
      const res=await fetch('/status'), data=await res.json();
      const m=Math.floor(data.remaining/60), s=data.remaining%60;
      document.getElementById('remaining').innerText = m+' min '+s+' sec';
    }
    async function addTime(m) {
      const res=await fetch('/add?m='+m,{method:'POST', headers:{'Authorization':'Basic '+btoa('clerk:P@ssw0rd')}});
      res.ok?fetchStatus():alert('Error');
    }
    async function endSession() {
      const res=await fetch('/end',{method:'POST', headers:{'Authorization':'Basic '+btoa('clerk:P@ssw0rd')}});
      res.ok?fetchStatus():alert('Error');
    }
    fetchStatus(); setInterval(fetchStatus,1000);
  </script>
</body>
</html>'''

# Background countdown
def countdown():
    while not stop_event.is_set():
        secs=get_secs()
        if secs<=0:
            for pid in os.popen(f"pgrep {EMU_PROC_NAME}").read().split():
                try: os.kill(int(pid), signal.SIGTERM)
                except: pass
        else:
            mins = secs // 60
            sec_rem = secs % 60
            set_secs(secs-1)
        time.sleep(1)

if __name__=='__main__':
    Thread(target=countdown,daemon=True).start()
    app.run(host='0.0.0.0',port=5000)
    # stop_event.set()  # Ensure countdown stops on exit
    # sys.exit(0)