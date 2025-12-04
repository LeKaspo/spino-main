"""Minimal Flask app that serves the transcript prototype + SSE endpoint."""

from __future__ import annotations

import json
import queue
import sys
from pathlib import Path

from flask import Flask, Response, send_from_directory, stream_with_context
 
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:  # pragma: no cover - simple import shim
    from server import transcript_stream
except ImportError:  # pragma: no cover
    import transcript_stream


app = Flask(__name__, static_folder=None)


def _format_sse(payload: dict, event: str = "transcript") -> str:
    data = json.dumps(payload, ensure_ascii=False)
    return f"event: {event}\ndata: {data}\n\n"


@app.route("/")
def transcript_page():
    return send_from_directory(BASE_DIR, "transcript.html")


@app.route("/stream/transcripts")
def stream_transcripts():
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


if __name__ == "__main__":  # pragma: no cover - manual runner
    app.run(host="0.0.0.0", port=5050, debug=False)
