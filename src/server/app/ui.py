import sys
from pathlib import Path
from flask import Flask, render_template, request

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

<<<<<<< HEAD
import src.server.send_commands.processcommands
=======
import server.send_commands.sendcommands as sendcommands
>>>>>>> 6641a894336efa293f67057b1f313ac4a7c9e2e7

index = ROOT / "server" / "templates" / "index.html"

app = Flask(__name__)
@app.route('/')
def index():
    return render_template(str(index))

#verarbeite Button und Tasteneingaben
@app.route('/button-click', methods=['POST'])
def button_click():
    data = request.get_json()
<<<<<<< HEAD
    src.server.send_commands.processcommands.ButtonClicked(f"{data['id']}")
=======
    sendcommands.ButtonClicked(f"{data['id']}")
>>>>>>> 6641a894336efa293f67057b1f313ac4a7c9e2e7
    return '', 204
@app.route('/button-click-inside', methods=['POST'])
def button_click_inside():
    data = request.get_json()
<<<<<<< HEAD
    src.server.send_commands.processcommands.ButtonClickedInside(f"{data['id']}")
=======
    sendcommands.ButtonClickedInside(f"{data['id']}")
>>>>>>> 6641a894336efa293f67057b1f313ac4a7c9e2e7
    return '', 204
@app.route('/button-press', methods=['POST'])
def button_press():
    data = request.get_json()
<<<<<<< HEAD
    src.server.send_commands.processcommands.ButtonPress(f"{data['id']}")
=======
    sendcommands.ButtonPress(f"{data['id']}")
>>>>>>> 6641a894336efa293f67057b1f313ac4a7c9e2e7
    return '', 204
@app.route('/button-release', methods=['POST'])
def button_release():
    data = request.get_json()
<<<<<<< HEAD
    src.server.send_commands.processcommands.ButtonRelease(f"{data['id']}")
=======
    sendcommands.ButtonRelease(f"{data['id']}")
>>>>>>> 6641a894336efa293f67057b1f313ac4a7c9e2e7
    return '', 204

@app.route('/key-down', methods=['POST'])
def key_down():
    data = request.get_json()
<<<<<<< HEAD
    src.server.send_commands.processcommands.ButtonPress(f"{data['key']}")
=======
    sendcommands.ButtonPress(f"{data['key']}")
>>>>>>> 6641a894336efa293f67057b1f313ac4a7c9e2e7
    return '', 204
@app.route('/key-up', methods=['POST'])
def key_up():
    data = request.get_json()
<<<<<<< HEAD
    src.server.send_commands.processcommands.ButtonRelease(f"{data['key']}")
=======
    sendcommands.ButtonRelease(f"{data['key']}")
>>>>>>> 6641a894336efa293f67057b1f313ac4a7c9e2e7
    return '', 204

def start_ui():
    app.run(host='0.0.0.0', port=5000, debug=False)
