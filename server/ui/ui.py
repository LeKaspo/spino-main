#starte den Flaskserver übern den das web UI läuft
from flask import Flask, render_template, request, jsonify, Response
import server.sendcommands
import server.core.config as config
from server.logger import Logger

app = Flask(__name__)
logger = Logger.getInstance()

@app.route('/')
def index():
    return render_template("index.html")

#verarbeite Button und Tasteneingaben
@app.route('/button-click', methods=['POST'])
def button_click():
    data = request.get_json()
    server.sendcommands.ButtonClicked(f"{data['id']}")
    return '', 204
@app.route('/button-click-inside', methods=['POST'])
def button_click_inside():
    data = request.get_json()
    server.sendcommands.ButtonClickedInside(f"{data['id']}")
    return '', 204
@app.route('/button-press', methods=['POST'])
def button_press():
    data = request.get_json()
    server.sendcommands.ButtonPress(f"{data['id']}")
    return '', 204
@app.route('/button-release', methods=['POST'])
def button_release():
    data = request.get_json()
    server.sendcommands.ButtonRelease(f"{data['id']}")
    return '', 204
@app.route('/key-down', methods=['POST'])
def key_down():
    data = request.get_json()
    server.sendcommands.ButtonPress(f"{data['key']}")
    return '', 204
@app.route('/key-up', methods=['POST'])
def key_up():
    data = request.get_json()
    server.sendcommands.ButtonRelease(f"{data['key']}")
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
