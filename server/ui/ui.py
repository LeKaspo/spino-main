#starte den Flaskserver übern den das web UI läuft
from flask import Flask, render_template, request
import sendcommands

app = Flask(__name__)
@app.route('/')
def index():
    return render_template("index.html")

#verarbeite Button und Tasteneingaben
@app.route('/button-click', methods=['POST'])
def button_click():
    data = request.get_json()
    sendcommands.Buttonclicked({data['id']})
    return '', 204
@app.route('/button-press', methods=['POST'])
def button_press():
    data = request.get_json()
    sendcommands.Buttonclicked(f"button gedrückt: {data['id']}")
    return '', 204
@app.route('/button-release', methods=['POST'])
def button_release():
    data = request.get_json()
    sendcommands.Buttonclicked(f"button losgelassen: {data['id']}")
    return '', 204

@app.route('/key-down', methods=['POST'])
def key_down():
    data = request.get_json()
    print(f"Taste gedrückt: {data['key']}")
    return '', 204
@app.route('/key-up', methods=['POST'])
def key_up():
    data = request.get_json()
    print(f"Taste losgelassen: {data['key']}")
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)