# Transcript UI prototype (minimal)

Fully self-contained HTML (inline CSS + JS) that attaches to the shared transcript stream and renders it inside a single auto-scrolling `<textarea>`. The markup is tiny so you can paste it straight into the production UI later.

## Files

| File | Purpose |
| --- | --- |
| `transcript.html` | Minimal demo page (inline EventSource client + styling). |
| `server.py` | Optional standalone Flask runner (still available if you want to serve the page separately). |
| `server/transcript_stream.py` | Process-wide pub/sub hub fed by `speechInput.py`. |

> The older `transcript.css` / `transcript.js` pair are kept only for reference; the new HTML file no longer depends on them.

## How data flows now

1. `speechInput.py` publishes every Whisper result via `transcript_stream.publish_transcript(...)`.
2. `transcript_stream` buffers the latest 250 entries and pushes new ones to all subscribers.
3. The main Flask UI (`server/ui/ui.py`) exposes `/stream/transcripts` on the same port as the rest of the app, plus a helper route `/transcript-demo` that just serves `transcript.html`.
4. The inline script inside `transcript.html` opens one `EventSource` to `/stream/transcripts`, appends each payload, and keeps the textarea scrolled to the bottom.

## Quick start (single server, no extra ports)

```powershell
# Terminal 1 – run Whisper capture so transcripts are produced
python server\speechInput.py --model tiny --language de

# Terminal 2 – start the existing Flask UI (now also hosts the transcript feed)
python server\ui\ui.py

# Browser – open the minimal viewer on the same server
http://localhost:5000/transcript-demo
```

When you're ready to integrate this into the "real" UI, copy the `<textarea>` and `<script>` block into your template and keep calling `/stream/transcripts`—no extra glue required.

## Integration tips

- Use the provided `/stream/transcripts` endpoint anywhere in your UI (SSE is standard, no frameworks needed).
- If you want fancier styling later, wrap the `<textarea>` inside your existing design system but leave the EventSource logic untouched.
- The optional `server/ui/prototype_transcript/server.py` runner is still there if you prefer to test the page in isolation, but it’s no longer required.
