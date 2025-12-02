#starte den Flaskserver übern den das web UI läuft
from flask import Flask, render_template, request, Response
import sendcommands
import numpy as np
import threading
import gesture
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # server/src/
TEMPLATE_DIR = BASE_DIR / "ui" / "templates"
STATIC_FOLDER = BASE_DIR / "ui" / "static"

app = Flask(__name__, template_folder=str(TEMPLATE_DIR), static_folder=str(STATIC_FOLDER))

@app.route('/')
def index():
    return render_template("index.html")

#verarbeite Button und Tasteneingaben
@app.route('/button-click', methods=['POST'])
def button_click():
    data = request.get_json()
    sendcommands.ButtonClicked(f"{data['id']}")
    return '', 204
@app.route('/button-press', methods=['POST'])
def button_press():
    data = request.get_json()
    sendcommands.ButtonPress(f"{data['id']}")
    return '', 204
@app.route('/button-release', methods=['POST'])
def button_release():
    data = request.get_json()
    sendcommands.ButtonRelease(f"{data['id']}")
    return '', 204

@app.route('/key-down', methods=['POST'])
def key_down():
    data = request.get_json()
    sendcommands.ButtonPress(f"{data['key']}")
    return '', 204
@app.route('/key-up', methods=['POST'])
def key_up():
    data = request.get_json()
    sendcommands.ButtonRelease(f"{data['key']}")
    return '', 204

@app.route('/video_gesture', endpoint='video_gesture')
def video_feed():
    return Response(gesture.gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    t = threading.Thread(target=gesture.capture_loop, daemon=True)
    t.start()
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
