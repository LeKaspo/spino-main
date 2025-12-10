import json
import sys
from pathlib import Path
from flask import Flask, jsonify, render_template, request, Response, stream_with_context

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

import server.send_commands.processcommands as processcommands
import server.config.config as config
from server.send_commands.logger import Logger
import server.gesture.gesture as gesture

TEMPLATE_DIR = ROOT / "server" / "templates"
STATIC_FOLDER = ROOT / "server" / "static"

app = Flask(__name__, template_folder=str(TEMPLATE_DIR), static_folder=str(STATIC_FOLDER))
logger = Logger.getInstance()

@app.route('/')
def index():
    return render_template("index.html")

#verarbeite Button und Tasteneingaben
@app.route('/button-click', methods=['POST'])
def button_click():
    data = request.get_json()
    param = None
    if 'param' in data:
            param= f"{data['param']}"
    processcommands.ButtonClicked(f"{data['id']}", param)
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

# zugriff auf config
@app.get("/api/config")
def get_config():
    return  config.system_status
@app.post("/api/config")
def update_config():
    data = request.get_json()
    config.system_status = data
    return '', 204

# text logs
@app.get("/api/logs/<int:box>")
def get_logs_box(box: int):
    try:
        text = logger.read(box)
        return jsonify({"box": box, "text": text})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.get("/api/logs/stream")
def sse_stream():
    def sse_event(name, payload):
        return f'event: {name}\ndata: {json.dumps(payload)}\n\n'

    def event_stream():
        t1, v1 = logger.read_with_version(1)
        t2, v2 = logger.read_with_version(2)
        yield sse_event("box1", {"text": t1, "version": v1})
        yield sse_event("box2", {"text": t2, "version": v2})
        last_v1, last_v2 = v1, v2
        while True:
            with logger._cv:
                changed = logger._cv.wait(timeout=30)
                t1, v1 = logger.read_with_version(1)
                t2, v2 = logger.read_with_version(2)
                if v1 != last_v1:
                    last_v1 = v1
                    yield sse_event("box1", {"text": t1, "version": v1})
                if v2 != last_v2:
                    last_v2 = v2
                    yield sse_event("box2", {"text": t2, "version": v2})
                if not changed:
                    yield ': keep-alive\n\n'
    headers = {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
    }
    return Response(stream_with_context(event_stream()), headers=headers)

@app.route('/video_gesture', endpoint='video_gesture')
def video_feed():
    return Response(gesture.gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def start_ui():
    app.run(host='0.0.0.0', port=5000, debug=False)
