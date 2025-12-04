"""Thread-safe pub/sub helper so Whisper transcripts can be streamed to clients.

The module exposes three main helpers:
    - ``publish_transcript``: push a new transcript entry into the ring buffer.
    - ``subscribe``: register a listener and get a snapshot of the current backlog.
    - ``unsubscribe``: remove a listener when the SSE connection closes.

A transcript entry is a plain dictionary so it serialises nicely to JSON/SSE.
"""

from __future__ import annotations

import queue
import threading
import uuid
from collections import deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Deque, Dict, List, Tuple

MAX_BACKLOG = 250
KEEPALIVE_SECONDS = 15


@dataclass(slots=True)
class TranscriptEntry:
    text: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="milliseconds")
    )
    language: str | None = None
    command: str | None = None
    meta: Dict[str, Any] | None = None

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        # drop ``None`` fields for a cleaner payload
        return {key: value for key, value in payload.items() if value is not None}


_backlog: Deque[Dict[str, Any]] = deque(maxlen=MAX_BACKLOG)
_subscribers: set[queue.Queue] = set()
_lock = threading.Lock()


def publish_transcript(
    *,
    text: str,
    language: str | None = None,
    command: str | None = None,
    meta: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Insert a transcript entry into the ring buffer and notify listeners."""

    entry = TranscriptEntry(text=text, language=language, command=command, meta=meta)
    data = entry.to_dict()

    with _lock:
        _backlog.append(data)
        listeners = list(_subscribers)

    for subscriber in listeners:
        subscriber.put(data)

    return data


def subscribe(include_history: bool = True) -> Tuple[List[Dict[str, Any]], queue.Queue]:
    """Register a listener and optionally hand back the current backlog."""

    channel: queue.Queue = queue.Queue()
    with _lock:
        _subscribers.add(channel)
        history = list(_backlog) if include_history else []
    return history, channel


def unsubscribe(channel: queue.Queue) -> None:
    with _lock:
        _subscribers.discard(channel)


def snapshot(limit: int | None = None) -> List[Dict[str, Any]]:
    """Return a copy of the current backlog (most recent last)."""

    with _lock:
        data = list(_backlog)
    if limit is not None:
        return data[-limit:]
    return data
