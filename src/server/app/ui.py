import sys
from pathlib import Path
from flask import Flask, render_template, request, Response

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

import server.send_commands.processcommands as processcommands
import server.gesture.gesture as gesture

TEMPLATE_DIR = ROOT / "server" / "templates"
STATIC_FOLDER = ROOT / "server" / "static"

app = Flask(__name__, template_folder=str(TEMPLATE_DIR), static_folder=str(STATIC_FOLDER))

@app.route('/')
def index():
    return render_template("index.html")

#verarbeite Button und Tasteneingaben
@app.route('/button-click', methods=['POST'])
def button_click():
    data = request.get_json()
    processcommands.ButtonClicked(f"{data['id']}")
    return '', 204
@app.route('/button-click-inside', methods=['POST'])
def button_click_inside():
    data = request.get_json()
    processcommands.ButtonClickedInside(f"{data['id']}")
    return '', 204
@app.route('/button-press', methods=['POST'])
def button_press():
    data = request.get_json()
    processcommands.ButtonPress(f"{data['id']}")
    return '', 204
@app.route('/button-release', methods=['POST'])
def button_release():
    data = request.get_json()
    processcommands.ButtonRelease(f"{data['id']}")
    return '', 204

@app.route('/key-down', methods=['POST'])
def key_down():
    data = request.get_json()
    processcommands.ButtonPress(f"{data['key']}")
    return '', 204
@app.route('/key-up', methods=['POST'])
def key_up():
    data = request.get_json()
    processcommands.ButtonRelease(f"{data['key']}")
    return '', 204
@app.route('/video_gesture', endpoint='video_gesture')
def video_feed():
    return Response(gesture.gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def start_ui():
    app.run(host='0.0.0.0', port=5000, debug=False)
