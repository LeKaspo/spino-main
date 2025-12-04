import sys
from pathlib import Path
from flask import Flask, render_template, request

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

import src.server.send_commands.sendcommands

index = ROOT / "server" / "templates" / "index.html"

app = Flask(__name__)
@app.route('/')
def index():
    return render_template(str(index))

#verarbeite Button und Tasteneingaben
@app.route('/button-click', methods=['POST'])
def button_click():
    data = request.get_json()
    src.server.send_commands.sendcommands.ButtonClicked(f"{data['id']}")
    return '', 204
@app.route('/button-click-inside', methods=['POST'])
def button_click_inside():
    data = request.get_json()
    src.server.send_commands.sendcommands.ButtonClickedInside(f"{data['id']}")
    return '', 204
@app.route('/button-press', methods=['POST'])
def button_press():
    data = request.get_json()
    src.server.send_commands.sendcommands.ButtonPress(f"{data['id']}")
    return '', 204
@app.route('/button-release', methods=['POST'])
def button_release():
    data = request.get_json()
    src.server.send_commands.sendcommands.ButtonRelease(f"{data['id']}")
    return '', 204

@app.route('/key-down', methods=['POST'])
def key_down():
    data = request.get_json()
    src.server.send_commands.sendcommands.ButtonPress(f"{data['key']}")
    return '', 204
@app.route('/key-up', methods=['POST'])
def key_up():
    data = request.get_json()
    src.server.send_commands.sendcommands.ButtonRelease(f"{data['key']}")
    return '', 204

def start_ui():
    app.run(host='0.0.0.0', port=5000, debug=False)
