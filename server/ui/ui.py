#starte den Flaskserver übern den das web UI läuft
import json
import queue
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from flask import (
    Flask,
    Response,
    render_template,
    request,
    send_from_directory,
    stream_with_context,
)

import server.sendcommands
from server import transcript_stream

PROTOTYPE_DIR = BASE_DIR / "prototype_transcript"

app = Flask(__name__)


def _format_sse(payload: dict, event: str = "transcript") -> str:
    data = json.dumps(payload, ensure_ascii=False)
    return f"event: {event}\ndata: {data}\n\n"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/transcript-demo")
def transcript_demo():
    return send_from_directory(PROTOTYPE_DIR, "transcript.html")


#verarbeite Button und Tasteneingaben
@app.route("/button-click", methods=["POST"])
def button_click():
    data = request.get_json()
    server.sendcommands.ButtonClicked(f"{data['id']}")
    return "", 204


@app.route("/button-press", methods=["POST"])
def button_press():
    data = request.get_json()
    server.sendcommands.ButtonPress(f"{data['id']}")
    return "", 204


@app.route("/button-release", methods=["POST"])
def button_release():
    data = request.get_json()
    server.sendcommands.ButtonRelease(f"{data['id']}")
    return "", 204


@app.route("/key-down", methods=["POST"])
def key_down():
    data = request.get_json()
    server.sendcommands.ButtonPress(f"{data['key']}")
    return "", 204


@app.route("/key-up", methods=["POST"])
def key_up():
    data = request.get_json()
    server.sendcommands.ButtonRelease(f"{data['key']}")
    return "", 204


@app.route("/stream/transcripts")
def stream_transcripts():
    """Server-Sent Events endpoint consumed by the transcript UI."""

    def event_stream():
        history, inbox = transcript_stream.subscribe()
        try:
            for item in history:
                yield _format_sse(item)
            while True:
                try:
                    item = inbox.get(timeout=transcript_stream.KEEPALIVE_SECONDS)
                except queue.Empty:
                    yield ": keep-alive\n\n"
                    continue
                yield _format_sse(item)
        finally:
            transcript_stream.unsubscribe(inbox)

    headers = {
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
        "Connection": "keep-alive",
    }
    return Response(
        stream_with_context(event_stream()),
        mimetype="text/event-stream",
        headers=headers,
    )


@app.route("/transcripts", methods=["POST"])
def ingest_transcript():
    payload = request.get_json(silent=True) or {}
    text = payload.get("text")
    if not text:
        return {"error": "text is required"}, 400

    transcript_stream.publish_transcript(
        text=text,
        language=payload.get("language"),
        command=payload.get("command"),
        meta=payload.get("meta"),
    )
    return "", 204


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
